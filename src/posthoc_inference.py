"""Post-hoc inference PH1-PH4 (panel decision D0016, research/PANEL_DECISIONS.md section C).

Reads only the saved aggregated results (results/sim_TEST/<trace>/*.npz); imports the frozen functions of src/analyze.py
(weekly, bootstrap, per_ba_boot, savings_from, contrast, load constants) and does not change any frozen file.
Everything here is POST-HOC and descriptive: no hypothesis test, no change of the frozen ledger.

  calendar interval            = frozen block bootstrap (analyze.bootstrap, mode fixed, seed 7 + S, B = 2000)
  synchronised-week interval   = PH1: the same 7-day block indices for all 42 BAs in each replicate, blocks aligned on the
                                 calendar weeks of the common day grid, same seed 7 + S and B = 2000

Usage: py src/posthoc_inference.py [--traces PM100,FDATA,KIT_FH2] [--weights w,u] [--B 2000]
Writes results/analysis_TEST_posthoc_<trace>.json and tables/ledger_TEST_posthoc.csv (rows of the run traces replaced).
One trace at a time is held in memory.
"""
import argparse
import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze as A  # noqa: E402  (frozen)

ROOT = A.ROOT
SLACKS = A.SLACKS
F = "lgbm"
PERIOD, TAG = "TEST", ""
QS = ("0.025", "0.975")


def rss_mb():
    try:
        import psutil
        return psutil.Process().memory_info().rss / 1e6
    except Exception:
        import ctypes
        from ctypes import wintypes

        class PMC(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD), ("PeakWorkingSetSize", ctypes.c_size_t),
                        ("WorkingSetSize", ctypes.c_size_t), ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPagedPoolUsage", ctypes.c_size_t), ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaNonPagedPoolUsage", ctypes.c_size_t), ("PagefileUsage", ctypes.c_size_t),
                        ("PeakPagefileUsage", ctypes.c_size_t)]
        pmc = PMC()
        pmc.cb = ctypes.sizeof(PMC)
        ctypes.windll.kernel32.K32GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb)
        return pmc.PeakWorkingSetSize / 1e6


def load_ext(trace, weight):
    """Same alignment as analyze.load (replicates added on the calendar day index) plus two rows: energy (kWh), jobs (n).
    Returns arms, {ba: {S: (d_min, acc[arms + 2, days])}}."""
    files = sorted(glob.glob(os.path.join(ROOT, "results", f"sim_{PERIOD}{TAG}", trace, "*.npz")))
    data, arms = {}, None
    for f in files:
        z = np.load(f)
        arms = [str(a) for a in z["arms"]]
        ba = os.path.basename(f)[:-4]
        per_s = {}
        for S in SLACKS:
            mats = []
            for k in z.files:
                if k.endswith(f"_S{S}__e_{weight}"):
                    pre = k[: -len(f"__e_{weight}")]
                    e = z[k].sum(axis=2)
                    en = z[pre + "__energy"].sum(axis=1)[None, :]
                    nn = z[pre + "__n"].sum(axis=1)[None, :].astype(float)
                    mats.append((int(z[pre + "__day0"]), np.vstack([e, en, nn])))
            d_min = min(d0 for d0, _ in mats)
            d_max = max(d0 + m.shape[1] for d0, m in mats)
            acc = np.zeros((mats[0][1].shape[0], d_max - d_min))
            for d0, m in mats:
                acc[:, d0 - d_min: d0 - d_min + m.shape[1]] += m
            per_s[S] = (d_min, acc)
        data[ba] = per_s
    return arms, data


def boot_raw(W, B, seed):
    """Mirror of analyze.bootstrap (mode fixed) returning raw per-draw totals [B, rows]; identical rng call order."""
    rng = np.random.default_rng(seed)
    rows = W[0][0].shape[0]
    out = np.empty((B, rows))
    for b in range(B):
        tot = np.zeros(rows)
        for w, r in W:
            tot += w[:, rng.integers(0, w.shape[1], w.shape[1])].sum(axis=1) + r
        out[b] = tot
    return out


def sync_boot(accs, B, seed):
    """PH1. accs: list of (d_min, acc[rows, days]) per BA. Same week indices for all BAs in each draw.
    Returns point totals [rows] and draws [B, rows]; weeks are 7-day blocks of the common global day grid; the days beyond
    the last full week are a fixed remainder (as in the frozen design)."""
    D0 = min(d for d, _ in accs)
    Dg = max(d + a.shape[1] for d, a in accs) - D0
    rows = accs[0][1].shape[0]
    G = np.zeros((rows, Dg))
    for d, a in accs:
        G[:, d - D0: d - D0 + a.shape[1]] += a            # pooled over BAs: indices are shared, so pooling first is exact
    nf = Dg // 7
    Wk = G[:, : nf * 7].reshape(rows, nf, 7).sum(axis=2)
    R = G[:, nf * 7:].sum(axis=1)
    rng = np.random.default_rng(seed)
    out = np.empty((B, rows))
    for b in range(B):
        out[b] = Wk[:, rng.integers(0, nf, nf)].sum(axis=1) + R
    return Wk.sum(axis=1) + R, out, nf, Dg


def terms(sv, idx):
    """sv: [..., arms] savings -> dict of the PH1/PH2 quantities (vectorised over the leading axis)."""
    g = lambda a: sv[..., idx[a]]  # noqa: E731
    o_a, o_r, f_a, f_r, f_p = g("oracle|act"), g("oracle|req"), g(f"{F}|act"), g(f"{F}|req"), g(f"{F}|pred")
    gap = o_a - f_r
    fc = 0.5 * ((o_a - f_a) + (o_r - f_r))
    rt = 0.5 * ((o_a - o_r) + (f_a - f_r))
    return {"D": f_r, "H1": f_r - g("runnow"), "H2": f_a - f_r, "H3": f_p - f_r,
            "H4": (o_a - o_r) - (f_a - f_r), "D_minus_profile7": f_r - g("profile7|req"), "gap": gap, "forecast": fc, "runtime": rt,
            "runtime_minus_forecast": rt - fc, "interaction": (o_a - o_r) - (f_a - f_r),
            "runtime_share": rt / gap, "retained_share": f_r / o_a}


def ci(x):
    return [float(np.quantile(x, 0.025)), float(np.quantile(x, 0.975))]


def run_trace(trace, weights, B, seed0):
    t0 = time.time()
    res = {"trace": trace, "B": B, "seed_rule": "7 + S (frozen); per-BA 7 + 100 + j (frozen)", "weights": {}}
    repro = []
    for weight in weights:
        arms, data = load_ext(trace, weight)
        bas = sorted(data)
        na = len(arms)
        idx = {a: i for i, a in enumerate(arms)}
        wres = {}
        for S in SLACKS:
            data30 = {b: {S: data[b][S][1][:na]} for b in bas}
            # frozen function and seed: reproduces the stored calendar interval exactly
            _, point, boot, per_ba, W30 = A.bootstrap(arms, data30, S, B, seed0 + S, "fixed")
            tf_pt, tf_bt = terms(point, idx), terms(boot, idx)
            # PH1 synchronised-week bootstrap
            tot_pt, tot_b, nf, Dg = sync_boot([data[b][S] for b in bas], B, seed0 + S)
            sv_pt = A.savings_from(tot_pt[:na], idx)
            sv_b = np.stack([A.savings_from(tot_b[i, :na], idx) for i in range(B)])
            assert np.abs(sv_pt - point).max() < 1e-12, "sync point estimate differs from frozen point"
            ts_bt = terms(sv_b, idx)
            q = {}
            for name in tf_pt:
                est = float(tf_pt[name])
                cal, syn = ci(tf_bt[name]), ci(ts_bt[name])
                q[name] = {"est": est, "cal_lo": cal[0], "cal_hi": cal[1], "sync_lo": syn[0], "sync_hi": syn[1],
                           "widen": (syn[1] - syn[0]) / (cal[1] - cal[0]),
                           "sync_excludes_zero": bool(syn[0] > 0 or syn[1] < 0),
                           "cal_excludes_zero": bool(cal[0] > 0 or cal[1] < 0)}
            sres = {"terms": q, "sync_weeks": int(nf), "grid_days": int(Dg)}
            # PH3 per-BA H2 intervals (frozen function and seeds); check the stored H2_lo
            per = {}
            for j, (b, w) in enumerate(zip(bas, W30)):
                bb = A.per_ba_boot(w, idx, 500, seed0 + 100 + j)
                d = A.contrast(bb, idx, [f"{F}|act"], [f"{F}|req"])
                est = float(A.contrast(per_ba[b], idx, [f"{F}|act"], [f"{F}|req"]))
                per[b] = {"est": est, "lo": float(np.quantile(d, 0.025)), "hi": float(np.quantile(d, 0.975))}
            sres["per_ba_H2"] = per
            sres["per_ba_H2_summary"] = {"n": len(per), "pos": int(sum(v["est"] > 0 for v in per.values())),
                                         "lo_gt0": int(sum(v["lo"] > 0 for v in per.values())),
                                         "min_lo": float(min(v["lo"] for v in per.values())),
                                         "max_hi": float(max(v["hi"] for v in per.values())),
                                         "median_est": float(np.median([v["est"] for v in per.values()]))}
            # PH4 absolute effects (energy-weighted only: grams and kWh)
            if weight == "w":
                W32 = [A.weekly(data[b][S][1]) for b in bas]
                raw = boot_raw(W32, B, seed0 + S)
                assert np.abs(np.stack([A.savings_from(raw[i, :na], idx) for i in range(B)]) - boot).max() == 0.0 or \
                    np.abs(np.stack([A.savings_from(raw[i, :na], idx) for i in range(B)]) - boot).max() < 1e-15
                tot_pt32 = sum(w_.sum(axis=1) + r_ for w_, r_ in W32)
                E, en, nn = tot_pt32[:na], tot_pt32[na], tot_pt32[na + 1]
                Eb, enb, nnb = raw[:, :na], raw[:, na], raw[:, na + 1]
                rn = idx["runnow"]
                ab = {"runnow_mean_intensity_g_per_kwh": {"est": float(E[rn] / en), "lo": ci(Eb[:, rn] / enb)[0],
                                                          "hi": ci(Eb[:, rn] / enb)[1]},
                      "total_energy_kwh": float(en), "n_jobs": float(nn), "arms": {}}
                for a in arms:
                    i = idx[a]
                    sj, sk = (E[rn] - E[i]) / nn, (E[rn] - E[i]) / en
                    bj, bk = (Eb[:, rn] - Eb[:, i]) / nnb, (Eb[:, rn] - Eb[:, i]) / enb
                    ab["arms"][a] = {"g_per_job": {"est": float(sj), "lo": ci(bj)[0], "hi": ci(bj)[1]},
                                     "g_per_kwh": {"est": float(sk), "lo": ci(bk)[0], "hi": ci(bk)[1]}}
                sres["absolute"] = ab
            # reproduction against the stored analysis JSON (calendar interval, point, per-BA H2_lo)
            fj = os.path.join(ROOT, "results", f"analysis_{PERIOD}{TAG}_{trace}_{weight}.json")
            with open(fj, encoding="utf-8") as fh:
                st = json.load(fh)["slacks"][str(S)]
            diffs = [abs(st["savings"][a] - float(point[idx[a]])) for a in arms]
            diffs += [abs(st["savings_ci95"][a][k] - ci(boot[:, idx[a]])[k]) for a in arms for k in (0, 1)]
            nm = {"H1_deployable_saving": "H1", "H2_runtime_penalty": "H2", "H3_prediction_recovery": "H3",
                  "H4_interaction": "H4"}
            for n, k in nm.items():
                diffs += [abs(st["tests"][n]["est"] - q[k]["est"]), abs(st["tests"][n]["ci95"][0] - q[k]["cal_lo"]),
                          abs(st["tests"][n]["ci95"][1] - q[k]["cal_hi"])]
            for k in ("gap", "forecast", "runtime", "interaction", "retained_share"):
                diffs.append(abs(st["shapley"][k] - q[k]["est"]))
            diffs += [abs(st["per_ba"][b]["H2_lo"] - per[b]["lo"]) for b in bas]
            diffs += [abs(st["per_ba"][b]["H2_est"] - per[b]["est"]) for b in bas]
            repro.append({"weight": weight, "S": S, "max_abs_diff": float(max(diffs)), "n_compared": len(diffs)})
            wres[f"S{S}"] = sres
            print(f"  {trace} {weight} S{S}: repro max diff {max(diffs):.3g} ({len(diffs)} values); "
                  f"H2 widen {q['H2']['widen']:.2f}; RSS peak {rss_mb():.0f} MB; {time.time() - t0:.0f}s", flush=True)
        res["weights"][weight] = wres
        del data
    res["reproduction"] = repro
    return res


def ledger_rows(res):
    trace = res["trace"]
    src = f"results/analysis_TEST_posthoc_{trace}.json"
    rows = []
    for weight, wres in res["weights"].items():
        for sk, sres in wres.items():
            pre = f"{trace}.{weight}.{sk}"
            for name, q in sres["terms"].items():
                ph = "PH6" if name == "D_minus_profile7" else "PH1" if name in ("D", "H1", "H2", "H3", "H4", "gap", "retained_share") else "PH2"
                rows += [(f"posthoc.{ph}.{pre}.{name}.est", q["est"], src),
                         (f"posthoc.{ph}.{pre}.{name}.cal_lo", q["cal_lo"], src),
                         (f"posthoc.{ph}.{pre}.{name}.cal_hi", q["cal_hi"], src),
                         (f"posthoc.{ph}.{pre}.{name}.sync_lo", q["sync_lo"], src),
                         (f"posthoc.{ph}.{pre}.{name}.sync_hi", q["sync_hi"], src),
                         (f"posthoc.{ph}.{pre}.{name}.widen", q["widen"], src)]
            for b, v in sres["per_ba_H2"].items():
                rows += [(f"posthoc.PH3.{pre}.{b}.H2_est", v["est"], src), (f"posthoc.PH3.{pre}.{b}.H2_lo", v["lo"], src),
                         (f"posthoc.PH3.{pre}.{b}.H2_hi", v["hi"], src)]
            for k, v in sres["per_ba_H2_summary"].items():
                rows.append((f"posthoc.PH3.{pre}.summary.{k}", v, src))
            if "absolute" in sres:
                ab = sres["absolute"]
                rows += [(f"posthoc.PH4.{pre}.runnow_g_per_kwh.{k}", ab["runnow_mean_intensity_g_per_kwh"][k], src)
                         for k in ("est", "lo", "hi")]
                rows += [(f"posthoc.PH4.{pre}.total_energy_kwh", ab["total_energy_kwh"], src),
                         (f"posthoc.PH4.{pre}.n_jobs", ab["n_jobs"], src)]
                for a, v in ab["arms"].items():
                    for m in ("g_per_job", "g_per_kwh"):
                        rows += [(f"posthoc.PH4.{pre}.{a}.{m}.{k}", v[m][k], src) for k in ("est", "lo", "hi")]
    return rows


def ph7_rows(trace):
    """PH7: saving per hour of added mean start delay (descriptive ratio, no interval), S = 12 h, from the stored analysis
    JSON (point savings) and tables/secondary_delay.csv (mean delay in hours, job-count mean). Run-now has zero delay: skipped."""
    d = pd.read_csv(os.path.join(ROOT, "tables", "secondary_delay.csv"))
    d = d[(d["trace"] == trace) & (d["S"] == 12)].set_index("arm")["mean_delay_h"]
    out = []
    for w in ("w", "u"):
        with open(os.path.join(ROOT, "results", f"analysis_TEST_{trace}_{w}.json"), encoding="utf-8") as fh:
            sv = json.load(fh)["slacks"]["12"]["savings"]
        for a, delay in d.items():
            if a == "runnow" or not delay > 0:
                continue
            out += [(f"posthoc.PH7.{trace}.{w}.S12.{a}.mean_delay_h", float(delay), "tables/secondary_delay.csv"),
                    (f"posthoc.PH7.{trace}.{w}.S12.{a}.saving_per_delay_hour", float(sv[a] / delay),
                     f"results/analysis_TEST_{trace}_{w}.json / tables/secondary_delay.csv")]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--traces", default="PM100,FDATA,KIT_FH2")
    ap.add_argument("--weights", default="w,u")
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    fn = os.path.join(ROOT, "tables", "ledger_TEST_posthoc.csv")
    for trace in args.traces.split(","):
        res = run_trace(trace, args.weights.split(","), args.B, args.seed)
        res["peak_rss_mb"] = rss_mb()
        with open(os.path.join(ROOT, "results", f"analysis_TEST_posthoc_{trace}.json"), "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1)
        new = pd.DataFrame(ledger_rows(res) + ph7_rows(trace), columns=["key", "value", "source"])
        if os.path.exists(fn):
            old = pd.read_csv(fn)
            old = old[~old["key"].str.contains(rf"\.{trace}\.", regex=True)]
            new = pd.concat([old, new], ignore_index=True)
        new.to_csv(fn, index=False)
        print(f"{trace} done; peak RSS {res['peak_rss_mb']:.0f} MB; max repro diff "
              f"{max(r['max_abs_diff'] for r in res['reproduction']):.3g}", flush=True)


if __name__ == "__main__":
    main()
