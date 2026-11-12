"""Savings, contrasts, two-stage block bootstrap and Holm correction from results/sim_<period><tag>/.

saving(arm) = 1 - sum E_arm / sum E_runnow, pooled over BAs, days, length classes and alignment replicates.
Primary bootstrap ("fixed"): the 42 BAs are a fixed set; within each BA, resample 7-day blocks of arrival days with
replacement (blocks are consecutive from the BA's first arrival day; the remainder days, fewer than 7, form a short
block that is kept unchanged in every replicate).
Sensitivity ("twostage"): resample BAs with replacement first, then blocks within each drawn BA.
p-values are null-centred: one-sided p = (1 + #{T* - T >= T}) / (B + 1); two-sided uses |T* - T| >= |T|.
Holm over the confirmatory H1-H3; H4 (interaction) is secondary and reported without adjustment.
Usage: python src/analyze.py --period DEV [--tag _v0] [--trace PM100] [--weight w|u] [--B 2000]
Writes results/analysis_<period><tag>_<trace>_<weight>.json and appends ledger rows to tables/ledger_<period><tag>.csv.
"""
import argparse
import glob
import json
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLACKS = (2, 6, 12, 24)


def load(period, tag, trace, weight):
    files = sorted(glob.glob(os.path.join(ROOT, "results", f"sim_{period}{tag}", trace, "*.npz")))
    data = {}
    arms = None
    for f in files:
        z = np.load(f)
        arms = list(z["arms"])
        ba = os.path.basename(f)[:-4]
        per_s = {}
        for S in SLACKS:
            mats = []
            for k in z.files:
                if k.endswith(f"_S{S}__e_{weight}"):
                    pre = k[: -len(f"__e_{weight}")]
                    mats.append((int(z[pre + "__day0"]), z[k].sum(axis=2)))   # (first day, [arms, days])
            d_min = min(d0 for d0, _ in mats)
            d_max = max(d0 + m.shape[1] for d0, m in mats)
            acc = np.zeros((mats[0][1].shape[0], d_max - d_min))
            for d0, m in mats:                                 # align replicates on the calendar day index
                acc[:, d0 - d_min: d0 - d_min + m.shape[1]] += m
            per_s[S] = acc
        data[ba] = per_s
    return arms, data


def weekly(m):
    """[arms, days] -> ([arms, full 7-day blocks], [arms] remainder of fewer than 7 days, kept fixed)."""
    nf = m.shape[1] // 7
    return m[:, :nf * 7].reshape(m.shape[0], nf, 7).sum(axis=2), m[:, nf * 7:].sum(axis=1)


def savings_from(tot, idx):
    return 1.0 - tot / tot[idx["runnow"]]


def bootstrap(arms, data, S, B, seed, mode="fixed"):
    idx = {a: i for i, a in enumerate(arms)}
    bas = sorted(data)
    W = [weekly(data[b][S]) for b in bas]                     # list of [arms, weeks]
    point = savings_from(sum(w.sum(axis=1) + r for w, r in W), idx)
    rng = np.random.default_rng(seed)
    boot = np.empty((B, len(arms)))
    for b in range(B):
        pick = rng.integers(0, len(bas), len(bas)) if mode == "twostage" else range(len(bas))
        tot = np.zeros(len(arms))
        for p in pick:
            w, r = W[p]
            tot += w[:, rng.integers(0, w.shape[1], w.shape[1])].sum(axis=1) + r
        boot[b] = savings_from(tot, idx)
    per_ba = {}
    for b, (w, r) in zip(bas, W):
        per_ba[b] = savings_from(w.sum(axis=1) + r, idx)
    return idx, point, boot, per_ba, W


def per_ba_boot(W_ba, idx, B, seed):
    w, r = W_ba
    rng = np.random.default_rng(seed)
    nw = w.shape[1]
    out = np.empty((B, w.shape[0]))
    for b in range(B):
        out[b] = savings_from(w[:, rng.integers(0, nw, nw)].sum(axis=1) + r, idx)
    return out


def contrast(vec, idx, plus, minus):
    """Linear contrast of savings: sum(plus) - sum(minus); vec may be [arms] or [B, arms]."""
    c = sum(vec[..., idx[a]] for a in plus) - sum(vec[..., idx[a]] for a in minus)
    return c


def holm(pvals):
    order = np.argsort(pvals)
    m = len(pvals)
    adj = np.empty(m)
    run = 0.0
    for r, i in enumerate(order):
        run = max(run, (m - r) * pvals[i])
        adj[i] = min(1.0, run)
    return adj


def write_ledger(out, args):
    """One row per number: key, value, source. Rows of this period/tag/trace/weight are replaced on re-run."""
    pre = f"{args.period}{args.tag}.{args.trace}.{args.weight}" + ("" if args.boot == "fixed" else f".{args.boot}")
    src = (f"results/analysis_{args.period}{args.tag}_{args.trace}_{args.weight}"
           + ("" if args.boot == "fixed" else f"_{args.boot}") + ".json")
    rows = [(f"{pre}.n_ba", out["n_ba"])]
    for S, r in out["slacks"].items():
        k0 = f"{pre}.S{S}"
        for a, v in r["savings"].items():
            lo, hi = r["savings_ci95"][a]
            rows += [(f"{k0}.saving.{a}", v), (f"{k0}.saving_lo.{a}", lo), (f"{k0}.saving_hi.{a}", hi)]
        for n, t in r["tests"].items():
            rows += [(f"{k0}.{n}.est", t["est"]), (f"{k0}.{n}.lo", t["ci95"][0]), (f"{k0}.{n}.hi", t["ci95"][1]),
                     (f"{k0}.{n}.p", t["p"])]
            if t["p_holm"] is not None:
                rows.append((f"{k0}.{n}.p_holm", t["p_holm"]))
        for k, v in r["shapley"].items():
            rows.append((f"{k0}.shapley.{k}", v))
        for k, v in r["per_ba_H2_counts"].items():
            rows.append((f"{k0}.perba_H2.{k}", v))
    new = pd.DataFrame(rows, columns=["key", "value"]).assign(source=src)
    fn = os.path.join(ROOT, "tables", f"ledger_{args.period}{args.tag}.csv")
    if os.path.exists(fn):
        old = pd.read_csv(fn)
        new = pd.concat([old[~old["key"].str.startswith(pre + ".")], new], ignore_index=True)
    new.to_csv(fn, index=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", required=True)
    ap.add_argument("--tag", default="")
    ap.add_argument("--trace", default="PM100")
    ap.add_argument("--weight", default="w", choices=["w", "u"])
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--fc", default="lgbm")
    ap.add_argument("--primary-slack", type=int, default=12)
    ap.add_argument("--boot", default="fixed", choices=["fixed", "twostage"])
    args = ap.parse_args()
    arms, data = load(args.period, args.tag, args.trace, args.weight)
    F = args.fc
    confirm = ("H1_deployable_saving", "H2_runtime_penalty", "H3_prediction_recovery")
    tests = {   # name: (plus arms, minus arms, sidedness)
        "H1_deployable_saving": ([f"{F}|req"], ["runnow"], "greater"),
        "H2_runtime_penalty": ([f"{F}|act"], [f"{F}|req"], "greater"),
        "H3_prediction_recovery": ([f"{F}|pred"], [f"{F}|req"], "greater"),
        "H4_interaction": (["oracle|act", f"{F}|req"], ["oracle|req", f"{F}|act"], "two"),
    }
    out = {"period": args.period, "trace": args.trace, "weight": args.weight, "n_ba": len(data), "B": args.B, "boot": args.boot,
           "slacks": {}}
    for S in SLACKS:
        idx, point, boot, per_ba, W = bootstrap(arms, data, S, args.B, args.seed + S, args.boot)
        rs = {"savings": {a: float(point[idx[a]]) for a in arms},
              "savings_ci95": {a: [float(np.quantile(boot[:, idx[a]], 0.025)), float(np.quantile(boot[:, idx[a]], 0.975))]
                               for a in arms}}
        tres = {}
        for name, (pl, mi, side) in tests.items():
            est = float(contrast(point, idx, pl, mi))
            bc = contrast(boot, idx, pl, mi)
            dev = bc - est                                            # null-centred bootstrap statistic
            if side == "greater":
                p = (1 + np.sum(dev >= est)) / (1 + len(bc))
            else:
                p = (1 + np.sum(np.abs(dev) >= abs(est))) / (1 + len(bc))
            tres[name] = {"est": est, "ci95": [float(np.quantile(bc, 0.025)), float(np.quantile(bc, 0.975))], "p": float(p)}
        adj = holm(np.array([tres[n]["p"] for n in confirm]))
        for n in tests:
            tres[n]["p_holm"] = None
        for n, a in zip(confirm, adj):
            tres[n]["p_holm"] = float(a)
        # Shapley 2x2 of the gap oracle|act -> F|req
        o_a, o_r, f_a, f_r = (point[idx[k]] for k in ("oracle|act", "oracle|req", f"{F}|act", f"{F}|req"))
        gap = o_a - f_r
        phi_fc = 0.5 * ((o_a - f_a) + (o_r - f_r))
        phi_rt = 0.5 * ((o_a - o_r) + (f_a - f_r))
        rs["shapley"] = {"gap": float(gap), "forecast": float(phi_fc), "runtime": float(phi_rt),
                         "interaction": float((o_a - o_r) - (f_a - f_r)),
                         "retained_share": float(f_r / o_a) if o_a else None}
        rs["tests"] = tres
        # per-BA H2 with within-BA bootstrap
        cnt = {"n": 0, "pos": 0, "sig": 0}
        per = {}
        for j, (b, w) in enumerate(zip(sorted(data), W)):
            bb = per_ba_boot(w, idx, 500, args.seed + 100 + j)
            d = contrast(bb, idx, [f"{F}|act"], [f"{F}|req"])
            e = float(contrast(per_ba[b], idx, [f"{F}|act"], [f"{F}|req"]))
            per[b] = {"saving_" + k.replace("|", "_"): float(per_ba[b][idx[k]]) for k in
                      ("oracle|act", "oracle|req", f"{F}|act", f"{F}|req", f"{F}|pred", f"{F}|pred2", "night", "histprofile|req")}
            per[b]["H2_est"] = e
            per[b]["H2_lo"] = float(np.quantile(d, 0.025))
            cnt["n"] += 1
            cnt["pos"] += int(e > 0)
            cnt["sig"] += int(np.quantile(d, 0.025) > 0)
        rs["per_ba_H2_counts"] = cnt
        rs["per_ba"] = per
        out["slacks"][str(S)] = rs
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    fn = os.path.join(ROOT, "results", f"analysis_{args.period}{args.tag}_{args.trace}_{args.weight}"
                      + ("" if args.boot == "fixed" else f"_{args.boot}") + ".json")
    with open(fn, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    write_ledger(out, args)
    S = str(args.primary_slack)
    r = out["slacks"][S]
    print(f"{args.trace} {args.weight} S={S}h n_ba={out['n_ba']}")
    for a in ["night", "histprofile|req", "oracle|act", "oracle|req", "oracle|pred", f"{F}|act", f"{F}|req", f"{F}|pred", f"{F}|pred2",
              "snaive_day|req", "profile7|req", "persistence|req"]:
        lo, hi = r["savings_ci95"][a]
        print(f"  saving {a:18s} {100*r['savings'][a]:6.2f} %  [{100*lo:5.2f}, {100*hi:5.2f}]")
    for n, t in r["tests"].items():
        ph = "-" if t["p_holm"] is None else f"{t['p_holm']:.4f}"
        print(f"  {n:24s} est {100*t['est']:6.2f} pp  CI [{100*t['ci95'][0]:5.2f}, {100*t['ci95'][1]:5.2f}]  p {t['p']:.4f}  holm {ph}")
    print("  shapley", {k: (round(100 * v, 2) if isinstance(v, float) and k != "retained_share" else v) for k, v in r["shapley"].items()})
    print("  per-BA H2", r["per_ba_H2_counts"])
    for S2 in SLACKS:
        rr = out["slacks"][str(S2)]
        print(f"  S={S2:2d}h oracle|act {100*rr['savings']['oracle|act']:5.2f}  {F}|act {100*rr['savings'][f'{F}|act']:5.2f}  "
              f"{F}|req {100*rr['savings'][f'{F}|req']:5.2f}  {F}|pred {100*rr['savings'][f'{F}|pred']:5.2f}  night {100*rr['savings']['night']:5.2f}")


if __name__ == "__main__":
    main()
