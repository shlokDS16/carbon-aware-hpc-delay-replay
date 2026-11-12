"""S3 (post-freeze, exploratory): emission-factor sensitivity of the accounting signal.

Variant a: direct (combustion) factors from src/emission_factors.csv column direct_g_per_kwh (coal 760, gas 370, oil 1116, ...).
Variant b: lifecycle factors as frozen, but oil 1116 g/kWh instead of 650.
Imports and storage stay excluded (production-based signal), as in the frozen CI.
Pipeline (all frozen code unchanged; only inputs differ):
  1. CI_t = sum_f share_f,t * EF_f  from data/derived/ci_hourly.parquet (the shares are gen_f / total, so this equals the
     src/build_ci.py formula; reproduction of the frozen lifecycle CI is verified to 0.05 g/kWh before use)
  2. clean with clean_ci.clean_one (same A06 rules, same 42 BAs)  -> data/derived/ci_clean_sens_s3<v>.parquet
  3. src/forecast.py UNCHANGED (hyperparameters, splits, seeds), --models lgbm, new CI as input -> forecasts_sens_s3<v>
  4. arms runnow, oracle|act, oracle|req, lgbm|act, lgbm|req, lgbm|pred on all traces (3 reps x 20,000 jobs, frozen seed)
  5. analysis as frozen (B = 2000, seed 7); ledger tables/ledger_TEST_sens_s3<v>.csv (keys sens.s3<v>.<trace>.<w|u>.S<S>.<name>)
Usage: py src/sens_s3.py --variant a|b [--smoke --bas CISO,ERCO --n-jobs 2000 --reps 1] [--force]
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sens_common as C  # noqa: E402
import clean_ci as cc  # noqa: E402  (A06 cleaning rules; module has no side effects on import)

FUELS = ["coal", "natural_gas", "nuclear", "oil", "hydro", "solar", "wind", "other", "unknown"]
ARMS = ["runnow", "oracle|act", "oracle|req", "lgbm|act", "lgbm|req", "lgbm|pred"]


def factors(variant):
    ef = pd.read_csv(os.path.join(C.ROOT, "src", "emission_factors.csv")).set_index("fuel")
    life = ef["lifecycle_g_per_kwh"].astype(float)
    if variant == "life":
        return life.to_dict()
    if variant == "a":
        return ef["direct_g_per_kwh"].astype(float).to_dict()
    if variant == "b":
        d = life.to_dict()
        d["oil"] = float(ef.loc["oil", "direct_g_per_kwh"])      # 1116 g/kWh (EIA FAQ 74), per research/S3_FACTORS.md
        return d
    raise ValueError(variant)


def build_clean(variant, tag, bas, log):
    """Steps 1-2. Returns path of the cleaned parquet."""
    out = os.path.join(C.ROOT, "data", "derived", f"ci_clean{tag}.parquet")
    cols = ["ba", "utc", "ci", "gen_total_mw"] + ["share_" + f for f in FUELS]
    h = pd.read_parquet(os.path.join(C.ROOT, "data", "derived", "ci_hourly.parquet"), columns=cols,
                        filters=[("ba", "in", bas)])
    h["utc"] = pd.to_datetime(h["utc"], utc=True)
    S = h[["share_" + f for f in FUELS]].to_numpy("float64")
    life = factors("life")
    ci_life = S @ np.array([life[f] for f in FUELS])          # NaN where total <= 0 (shares NaN), as ci
    both = h["ci"].notna().to_numpy()
    err = np.nanmax(np.abs(ci_life[both] - h["ci"].to_numpy("float64")[both]))
    assert np.array_equal(both, np.isfinite(ci_life)), "validity of rebuilt CI differs from the frozen CI"
    assert err < 0.05, f"rebuilt lifecycle CI differs from frozen ci by {err}"
    log(f"rebuilt lifecycle CI reproduces ci_hourly.ci: max abs diff {err:.5f} g/kWh over {both.sum()} valid hours")
    ef = factors(variant)
    h["ci"] = (S @ np.array([ef[f] for f in FUELS])).astype("float32")
    log("variant " + variant + " factors: " + json.dumps(ef))
    parts = []
    for ba, g in h.groupby("ba"):
        res, _ = cc.clean_one(g[["utc", "ci", "gen_total_mw"]])
        res["ba"] = ba
        parts.append(res[["ba", "utc", "ci_clean", "flag", "usable_day"]])
    clean = pd.concat(parts, ignore_index=True)
    clean.to_parquet(out, index=False)
    log(f"wrote {out}: {len(clean)} rows, {clean['ba'].nunique()} BAs, mean ci_clean {clean['ci_clean'].mean():.1f} g/kWh")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", required=True, choices=["a", "b"])
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--bas", default="")
    ap.add_argument("--n-jobs", type=int, default=20000)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--seed", type=int, default=20261111)
    ap.add_argument("--traces", default="PM100,FDATA,KIT_FH2")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    v = args.variant
    sid = "s3" + v
    ctx = C.Ctx(sid, args.smoke)
    C.verify_frozen()
    C.sim.check_prereg()
    tag = ("_smoke" if args.smoke else "") + f"_sens_{sid}"
    ctx.header({"sim_seed": args.seed, "analysis_seed": 7, "B": args.B, "forecast": "frozen defaults (seed 42)"},
               ["data/derived/jobs.parquet", "data/derived/ci_hourly.parquet", "data/derived/ci_clean.parquet",
                "src/emission_factors.csv"])
    bas = C.eligible_bas(args.bas.split(",") if args.bas else None)
    traces = args.traces.split(",")
    clean_p = os.path.join(C.ROOT, "data", "derived", f"ci_clean{tag}.parquet")
    if args.force or not os.path.exists(clean_p):
        build_clean(v, tag, bas, ctx.log)
    ctx.log("ci_clean md5 " + C.md5_file(clean_p))
    fdir = os.path.join(C.ROOT, "data", "derived", f"forecasts{tag}")
    have = os.path.isdir(os.path.join(fdir, "lgbm")) and len(os.listdir(os.path.join(fdir, "lgbm"))) >= len(bas)
    if args.force or not have:
        cmd = [os.path.join(C.SRC, "forecast.py"), "--input", f"data/derived/ci_clean{tag}.parquet", "--tag", tag,
               "--shares", "data/derived/ci_hourly.parquet", "--eligibility", "tables/ba_eligibility.csv",
               "--models", "lgbm"] + (["--bas", args.bas] if args.bas else [])
        ctx.log("frozen forecast.py (unchanged hyperparameters): " + " ".join(cmd[1:]))
        rc, pk1, pkt = C.run_polled(cmd, stdout_path=ctx.logf)
        ctx.peak_workers_mb = max(ctx.peak_workers_mb, pk1)
        ctx.log(f"forecast.py rc={rc}; peak RSS single process {pk1:.0f} MB, tree total {pkt:.0f} MB")
        if rc:
            sys.exit("forecast.py failed")
    sk = pd.read_csv(os.path.join(C.ROOT, "tables", f"forecast_skill{tag}.csv"))
    s1 = sk[(sk["model"] == "lgbm") & (sk["lead_bucket"] == "1-24")]
    dev_mae = float((s1["MAE"] * s1["n"]).sum() / s1["n"].sum())
    ctx.log(f"DEV pooled MAE lgbm 1-24 h under these factors: {dev_mae:.2f} g/kWh")
    jobs = C.load_jobs("COMPLETED", traces)
    cfg = dict(tag=tag, arms=ARMS, slacks=C.SLACKS, ks=(0,), seed=args.seed, reps=args.reps, n_jobs=args.n_jobs,
               fc_src={"lgbm": (f"data/derived/forecasts{tag}", "lgbm")}, outdir={0: ctx.simdir()})
    C.run_generic(ctx, cfg, jobs, bas, args.workers)
    del jobs
    rows = [(f"sens.{sid}.dev_mae_lgbm_1_24", dev_mae)]
    ci = pd.read_parquet(clean_p, columns=["ba", "utc", "ci_clean"])
    rows.append((f"sens.{sid}.mean_ci_clean_all_hours", float(ci["ci_clean"].mean())))
    for trace in traces:
        for w in ("w", "u"):
            out = C.analyse(ctx.simdir(), trace, w, B=args.B, seed=7)
            with open(ctx.analysis_path(trace, w), "w", encoding="utf-8") as f:
                json.dump(out, f, indent=1)
            rows += C.ledger_rows(sid, out)
            if w == "w":
                r = out["slacks"]["12"]
                ctx.log(f"S3{v} {trace} w S12: oracle|act {100*r['savings']['oracle|act']:.2f} %  D {100*r['savings']['lgbm|req']:.2f} %  "
                        f"H2 {100*r['tests']['H2_runtime_penalty']['est']:.2f} pp  H3 {100*r['tests']['H3_prediction_recovery']['est']:.2f} pp")
    C.write_ledger(ctx, rows, f"sens.{sid}.")
    ctx.log("ledger " + ctx.ledger_path())
    ctx.footer()
    if not args.smoke:
        open(ctx.done_path(), "w").write("done\n")


if __name__ == "__main__":
    main()
