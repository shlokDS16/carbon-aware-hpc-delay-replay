"""S1 (post-freeze, exploratory): sampling-inclusive uncertainty, user-cluster outer bootstrap x frozen block bootstrap.

Per outer sample m (seed 20261112 + m): within each trace, users (clusters, counted after the frozen main filter) are resampled
with replacement; per BA, 20,000 eligible jobs are drawn (without replacement) from the resampled pool; one alignment
replicate; the frozen 7-day block bootstrap within BA (fixed BA set, analyze.bootstrap) is then run on that sample with B = 200.
S = 12 h only (primary slack), energy-weighted, arms lgbm|act, lgbm|req, lgbm|pred, oracle|act, oracle|req, runnow.
Report per trace: the combined percentile interval over all outer x inner draws, and the outer-only spread (the 30 point
estimates). Job-level history-based runtime predictions (r_pred_h) are those of the frozen prep (computed before resampling).
Amendment (research/P4_PLAN_AMEND.md D): original-users control (users not resampled, same 30 seeds, one alignment replicate each,
keys sens.s1ctl.*) and a total interval = normal approximation around the frozen estimate with variance = frozen calendar variance +
between-outer variance (keys ...tot_lo/hi; ...totin_* uses the mean inner variance instead), beside the percentile intervals.
If fewer than 30 outer samples fit the time budget the result is labelled Monte Carlo sensitivity, not a corrected interval.
Usage: py src/sens_s1.py [--n-outer 30] [--budget-hours 8] [--smoke --bas CISO,ERCO --n-jobs 2000 --B 50 --n-outer 2]
Outputs: results/sim_TEST_sens_s1/m<NN>/<trace>/<BA>.npz, results/analysis_TEST_sens_s1_m<NN>_<trace>_w.json,
         results/analysis_TEST_sens_s1_summary_<trace>_w.json, tables/ledger_TEST_sens_s1.csv, logs/sens_s1.log
"""
import argparse
import json
import math
import os
import sys
import time
import zlib

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sens_common as C  # noqa: E402

ARMS = ["runnow", "oracle|act", "oracle|req", "lgbm|act", "lgbm|req", "lgbm|pred"]
FIRST_SEED = 20261112
EXPECTED_USERS = {"PM100": 394, "FDATA": 1257, "KIT_FH2": 165}      # counted 2026-11-12 (P4_PLAN v2)
STATS = ("D_saving_lgbm_req", "oracle_act_saving", "H2_runtime_penalty", "H3_prediction_recovery", "shapley_gap",
         "shapley_forecast", "shapley_runtime", "shapley_interaction", "retained_share")


def stat_arrays(vec, idx):
    """vec: [..., arms] savings -> dict of the reported statistics (same definitions as analyze.main)."""
    g = lambda a: vec[..., idx[a]]
    o_a, o_r, f_a, f_r, f_p = g("oracle|act"), g("oracle|req"), g("lgbm|act"), g("lgbm|req"), g("lgbm|pred")
    return {"D_saving_lgbm_req": f_r, "oracle_act_saving": o_a, "H2_runtime_penalty": f_a - f_r,
            "H3_prediction_recovery": f_p - f_r, "shapley_gap": o_a - f_r,
            "shapley_forecast": 0.5 * ((o_a - f_a) + (o_r - f_r)), "shapley_runtime": 0.5 * ((o_a - o_r) + (f_a - f_r)),
            "shapley_interaction": (o_a - o_r) - (f_a - f_r), "retained_share": f_r / o_a}


def one_outer(ctx, args, m, jobs, bas, traces, control=False):
    """control=True (P4_PLAN_AMEND D): original-users control, same seed, users NOT resampled (every user once)."""
    seed = FIRST_SEED + m
    pre = "c" if control else "m"
    t0 = time.time()
    cum, nusers = {}, {}
    for t in traces:
        u = jobs[t]["user"]
        n_u = int(u.max()) + 1
        if control:
            mult = np.ones(n_u, dtype=np.int64)
        else:
            rng = np.random.default_rng([seed, zlib.crc32(t.encode()), 1])
            mult = np.bincount(rng.integers(0, n_u, n_u), minlength=n_u)
        cum[t] = np.cumsum(mult[u]).astype(np.int64)
        nusers[t] = n_u
    cfg = dict(tag="", arms=ARMS, slacks=(12.0,), ks=(0,), seed=seed, reps=1, n_jobs=args.n_jobs, cum=cum,
               fc_src={"lgbm": ("data/derived/forecasts", "lgbm")},
               outdir={0: ctx.simdir(f"{pre}{m:02d}")})
    C.run_generic(ctx, cfg, jobs, bas, args.workers)
    for t in traces:
        arms, data = C.load_sim(ctx.simdir(f"{pre}{m:02d}"), t, "w")
        idx, point, boot, per_ba, W = C.an.bootstrap(arms, data, 12, args.B, seed, "fixed")
        rec = {"seed": seed, "n_users": nusers[t], "B": args.B, "point": {k: float(v) for k, v in stat_arrays(point, idx).items()},
               "boot": {k: v.tolist() for k, v in stat_arrays(boot, idx).items()}}
        with open(os.path.join(ctx.res, f"analysis_TEST_sens_s1_{pre}{m:02d}_{t}_w.json"), "w", encoding="utf-8") as f:
            json.dump(rec, f)
    dt = time.time() - t0
    with open(os.path.join(ctx.simdir(f"{pre}{m:02d}"), "DONE.txt"), "w") as f:
        f.write(f"{dt:.1f}\n")
    ctx.log(f"{"control" if control else "outer"} sample {m} (seed {seed}) done in {dt:.0f} s; users resampled " + json.dumps(nusers))
    return dt


def frozen_calendar(ctx, traces, bas, B):
    """Frozen estimate and calendar (block-bootstrap) variance per statistic from the frozen TEST run, S = 12 h, energy-weighted:
    analyze.bootstrap on results/sim_TEST with the frozen seed (7 + S) and B (2000 by default)."""
    out = {}
    for t in traces:
        arms, data = C.load_sim(os.path.join(C.ROOT, "results", "sim_TEST"), t, "w")
        if bas:
            data = {b: v for b, v in data.items() if b in bas}
        idx, point, boot, _, _ = C.an.bootstrap(arms, data, 12, B, 7 + 12, "fixed")
        pt, bt = stat_arrays(point, idx), stat_arrays(boot, idx)
        out[t] = {s: {"est": float(pt[s]), "var_cal": float(np.var(bt[s], ddof=1)), "cal_lo": float(np.quantile(bt[s], 0.025)),
                      "cal_hi": float(np.quantile(bt[s], 0.975))} for s in STATS}
        ctx.log(f"frozen calendar bootstrap {t}: B={B}, n_ba={len(data)}")
    return out


def summarise(ctx, traces, ms, pre="m", frozen=None):
    rows = []
    sid = "s1" if pre == "m" else "s1ctl"
    for t in traces:
        recs = [json.load(open(os.path.join(ctx.res, f"analysis_TEST_sens_s1_{pre}{m:02d}_{t}_w.json"))) for m in ms]
        k0 = f"sens.{sid}.{t}.w.S12."
        rows.append((f"sens.{sid}.{t}.w.n_outer", len(recs)))
        summ = {}
        for s in STATS:
            pts = np.array([r["point"][s] for r in recs])
            allb = np.concatenate([np.array(r["boot"][s]) for r in recs])
            inner_sd = float(np.mean([np.std(r["boot"][s], ddof=1) for r in recs]))
            inner_var = float(np.mean([np.var(r["boot"][s], ddof=1) for r in recs]))
            d = {"outer_mean": float(pts.mean()), "outer_sd": float(pts.std(ddof=1)) if len(pts) > 1 else float("nan"),
                 "outer_lo": float(np.quantile(pts, 0.025)), "outer_hi": float(np.quantile(pts, 0.975)),
                 "outer_min": float(pts.min()), "outer_max": float(pts.max()),
                 "comb_mean": float(allb.mean()), "comb_lo": float(np.quantile(allb, 0.025)),
                 "comb_hi": float(np.quantile(allb, 0.975)), "inner_sd_mean": inner_sd, "n_draws": int(len(allb))}
            if frozen is not None and len(pts) > 1:
                # P4_PLAN_AMEND D: law of total variance, normal approximation around the FROZEN estimate:
                # var = calendar variance (frozen block bootstrap) + between-outer variance (variance of the outer point estimates);
                # alternative: calendar variance replaced by the mean inner variance of the outer samples.
                f = frozen[t][s]
                var_b = float(pts.var(ddof=1))
                for tag, vc in (("tot", f["var_cal"]), ("totin", inner_var)):
                    se = float(np.sqrt(vc + var_b))
                    d[f"{tag}_se"] = se
                    d[f"{tag}_lo"] = f["est"] - 1.96 * se
                    d[f"{tag}_hi"] = f["est"] + 1.96 * se
                d.update({"frozen_est": f["est"], "frozen_cal_lo": f["cal_lo"], "frozen_cal_hi": f["cal_hi"],
                          "frozen_cal_sd": float(np.sqrt(f["var_cal"])), "between_outer_sd": float(np.sqrt(var_b))})
            summ[s] = d
            rows += [(f"{k0}{s}.{k}", v) for k, v in d.items()]
        rows.append((f"{k0}n_users_mean", float(np.mean([r["n_users"] for r in recs]))))
        json.dump(summ, open(os.path.join(ctx.res, f"analysis_TEST_sens_{sid}_summary_{t}_w.json"), "w"), indent=1)
        s = summ["H2_runtime_penalty"]
        ctx.log(f"{sid} {t} S12 n_outer={len(recs)}: D {100*summ['D_saving_lgbm_req']['outer_mean']:.2f} % "
                f"[comb {100*summ['D_saving_lgbm_req']['comb_lo']:.2f}, {100*summ['D_saving_lgbm_req']['comb_hi']:.2f}; "
                f"outer {100*summ['D_saving_lgbm_req']['outer_lo']:.2f}, {100*summ['D_saving_lgbm_req']['outer_hi']:.2f}]; "
                f"H2 {100*s['outer_mean']:.2f} pp [comb {100*s['comb_lo']:.2f}, {100*s['comb_hi']:.2f}; outer SD {100*s['outer_sd']:.2f}]")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--bas", default="")
    ap.add_argument("--n-outer", type=int, default=30)
    ap.add_argument("--budget-hours", type=float, default=8.0)
    ap.add_argument("--n-jobs", type=int, default=20000)
    ap.add_argument("--B", type=int, default=200)
    ap.add_argument("--traces", default="PM100,FDATA,KIT_FH2")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--no-summary", action="store_true", help="run samples only (timing call)")
    ap.add_argument("--no-control", action="store_true", help="skip the original-users control (P4_PLAN_AMEND D)")
    ap.add_argument("--B-cal", type=int, default=2000, help="B of the frozen calendar bootstrap used for the total interval")
    args = ap.parse_args()
    ctx = C.Ctx("s1", args.smoke)
    C.verify_frozen()
    C.sim.check_prereg()
    traces = args.traces.split(",")
    ctx.header({"outer_seeds": f"{FIRST_SEED}..{FIRST_SEED + args.n_outer - 1}", "inner_B": args.B, "n_outer": args.n_outer,
                "n_jobs": args.n_jobs, "alignment_reps_per_outer": 1}, ["data/derived/jobs.parquet", "data/derived/ci_clean.parquet"])
    bas = C.eligible_bas(args.bas.split(",") if args.bas else None)
    jobs = C.load_jobs("COMPLETED", traces, user=True)
    for t in traces:
        n_u = int(jobs[t]["user"].max()) + 1
        ctx.log(f"{t}: {len(jobs[t]['r_act_h'])} filtered jobs, {n_u} users (expected {EXPECTED_USERS.get(t)})")
    times, todo = [], []
    for m in range(args.n_outer):
        d = os.path.join(ctx.simdir(f"m{m:02d}"), "DONE.txt")
        if os.path.exists(d):
            times.append(float(open(d).read()))
        else:
            todo.append(m)
    n_target = args.n_outer
    t_start = time.time()
    first_in_run = True
    for m in todo:
        times.append(one_outer(ctx, args, m, jobs, bas, traces))
        if first_in_run:
            first_in_run = False
            proj_h = np.mean(times) * args.n_outer / 3600.0
            ctx.log(f"first outer sample of this run took {times[-1]:.0f} s; projected total for {args.n_outer} samples "
                    f"{proj_h:.2f} h (budget {args.budget_hours} h)")
            if proj_h > args.budget_hours:
                n_target = max(1, int(args.budget_hours * 3600.0 / np.mean(times)))
                ctx.log(f"projected total exceeds the budget: stopping after {n_target} outer samples; the result is a "
                        f"Monte Carlo sensitivity, not a corrected interval")
        if len(times) >= n_target or args.no_summary:
            break
    done = [m for m in range(args.n_outer) if os.path.exists(os.path.join(ctx.simdir(f"m{m:02d}"), "DONE.txt"))]
    ctx.log(f"{len(done)} of {args.n_outer} outer samples complete; elapsed this run {time.time() - t_start:.0f} s")
    if args.no_summary or not done:
        ctx.footer()
        return
    # original-users control (P4_PLAN_AMEND D): same seeds and sample count, users not resampled, one alignment replicate each
    ctl_done, ctl_times = [], []
    if not args.no_control:
        t_c = time.time()
        budget_s = args.budget_hours * 3600.0
        for m in done:
            d = os.path.join(ctx.simdir(f"c{m:02d}"), "DONE.txt")
            if os.path.exists(d):
                ctl_times.append(float(open(d).read()))
            else:
                if ctl_times and time.time() - t_c + np.mean(ctl_times) > budget_s:
                    ctx.log("control: time budget reached; stopping with " + str(len(ctl_times)) + " control samples")
                    break
                ctl_times.append(one_outer(ctx, args, m, jobs, bas, traces, control=True))
        ctl_done = [m for m in done if os.path.exists(os.path.join(ctx.simdir(f"c{m:02d}"), "DONE.txt"))]
        ctx.log(f"{len(ctl_done)} control samples complete (users not resampled)")
    frozen = frozen_calendar(ctx, traces, set(bas) if args.bas else None, args.B_cal)
    rows = summarise(ctx, traces, done, "m", frozen)
    if ctl_done:
        rows += summarise(ctx, traces, ctl_done, "c", None)
        rows.append(("sens.s1ctl.n_outer_completed", len(ctl_done)))
    rows.append(("sens.s1.B_cal", args.B_cal))
    rows.append(("sens.s1.n_outer_completed", len(done)))
    rows.append(("sens.s1.n_outer_planned", args.n_outer))
    rows.append(("sens.s1.mean_seconds_per_outer", float(np.mean(times))))
    C.write_ledger(ctx, rows, "sens.s1.")
    ctx.log("ledger " + ctx.ledger_path())
    ctx.footer()
    if not args.smoke and (len(done) >= n_target):
        open(ctx.done_path(), "w").write(f"done {len(done)} of {args.n_outer}\n")


if __name__ == "__main__":
    main()
