"""S2b (post-freeze, exploratory; research/P4_PLAN_AMEND2.md): data latency at publication scale, k = 24 and 48 h.

The planner uses the LightGBM forecast issued at floor(a) - k with leads shifted by k; leads beyond 96 hold the lead-96 value
(sens_common.fc_window_lat, the S2 logic unchanged).  Arms lgbm|req, lgbm|pred, snaive_day|req (+ runnow, lgbm|act, oracle|act,
oracle|req for the baseline, H2 and Shapley).  Oracle is an UPPER BOUND and does not depend on k.  All three traces, S = 12 h,
energy-weighted (w) and unweighted (u).  k = 0 reproduces the frozen numbers (S2 equality test).
Revisions (first release vs revised EIA-930 values) cannot be tested; stated as a limitation.
Usage: py src/sens_s2b.py [--smoke --bas CISO,ERCO --n-jobs 2000 --reps 1 --ks 24,48 --B 100]
Outputs: results/sim_TEST_sens_s2b/k<k>/<trace>/<BA>.npz, results/analysis_TEST_sens_s2b_k<k>_<trace>_<w|u>.json,
         tables/ledger_TEST_sens_s2b.csv (keys sens.s2b.<trace>.<w|u>.S12.k<k>.<name>), logs/sens_s2b.log
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sens_common as C  # noqa: E402

ARMS = ["runnow", "oracle|act", "oracle|req", "lgbm|act", "lgbm|req", "lgbm|pred", "snaive_day|req"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--bas", default="")
    ap.add_argument("--n-jobs", type=int, default=20000)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--seed", type=int, default=20261111)
    ap.add_argument("--ks", default="24,48")
    ap.add_argument("--traces", default="PM100,FDATA,KIT_FH2")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--B", type=int, default=2000)
    args = ap.parse_args()
    ctx = C.Ctx("s2b", args.smoke)
    C.verify_frozen()
    C.sim.check_prereg()
    for f in ("P4_PLAN_AMEND2",):
        want = open(os.path.join(C.ROOT, "research", f + ".md5")).read().split()[0]
        if want != C.md5_file(os.path.join(C.ROOT, "research", f + ".md")):
            sys.exit(f + ".md changed after its md5 was written")
    ks = [int(k) for k in args.ks.split(",")]
    traces = args.traces.split(",")
    ctx.header({"sim_seed": args.seed, "analysis_seed": 7, "B": args.B, "ks": ks, "reps": args.reps, "n_jobs": args.n_jobs, "S": 12},
               ["data/derived/jobs.parquet", "data/derived/ci_clean.parquet"])
    ctx.log("P4_PLAN_AMEND2.md md5: " + C.md5_file(os.path.join(C.ROOT, "research", "P4_PLAN_AMEND2.md")))
    bas = C.eligible_bas(args.bas.split(",") if args.bas else None)
    jobs = C.load_jobs("COMPLETED", traces)
    cfg = dict(tag="", arms=ARMS, slacks=(12.0,), ks=tuple(ks), seed=args.seed, reps=args.reps, n_jobs=args.n_jobs,
               fc_src={"lgbm": ("data/derived/forecasts", "lgbm"), "snaive_day": ("data/derived/forecasts", "snaive_day")},
               outdir={k: ctx.simdir(f"k{k}") for k in ks})
    C.run_generic(ctx, cfg, jobs, bas, args.workers)
    del jobs
    rows = []
    for k in ks:
        for trace in traces:
            for w in ("w", "u"):
                out = C.analyse(ctx.simdir(f"k{k}"), trace, w, B=args.B, seed=7, slacks=(12,))
                with open(ctx.analysis_path(trace, w, f"_k{k}"), "w", encoding="utf-8") as f:
                    json.dump(out, f, indent=1)
                rows += C.ledger_rows("s2b", out, name_prefix=f"k{k}.")
                if w == "w":
                    r = out["slacks"]["12"]
                    ctx.log(f"S2b k={k} {trace} w S12: D {100*r['savings']['lgbm|req']:.2f} %  pred {100*r['savings']['lgbm|pred']:.2f} %  "
                            f"snaive_day|req {100*r['savings']['snaive_day|req']:.2f} %  oracle|act {100*r['savings']['oracle|act']:.2f} % (upper bound)")
    C.write_ledger(ctx, rows, "sens.s2b.")
    ctx.log("ledger " + ctx.ledger_path())
    ctx.footer()
    if not args.smoke:
        open(ctx.done_path(), "w").write("done\n")


if __name__ == "__main__":
    main()
