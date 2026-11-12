"""S4 (post-freeze, exploratory): TIMEOUT jobs included, PM100 only, all frozen arms, frozen seeds.

Runs the FROZEN simulate.py unchanged with --states COMPLETED,TIMEOUT --traces PM100 and a different output suffix, then
analyses with the mirror of analyze.py (sens_common.analyse). TIMEOUT runtimes are limit-censored: descriptive only.
Usage: py src/sens_s4.py [--smoke --bas CISO,ERCO --n-jobs 2000 --reps 1 --states COMPLETED,TIMEOUT] [--B 2000]
Outputs: results/sim_TEST_sens_s4/PM100/*.npz, results/analysis_TEST_sens_s4_PM100_{w,u}.json,
         tables/ledger_TEST_sens_s4.csv (keys sens.s4.PM100.<w|u>.S<S>.<name>), logs/sens_s4.log
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sens_common as C  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--bas", default="")
    ap.add_argument("--n-jobs", type=int, default=20000)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--seed", type=int, default=20261111)       # frozen simulation seed
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--states", default="COMPLETED,TIMEOUT")
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--sim-only", action="store_true")
    args = ap.parse_args()
    ctx = C.Ctx("s4", args.smoke)
    C.verify_frozen()
    C.sim.check_prereg()
    ctx.header({"sim_seed": args.seed, "analysis_seed": 7, "B": args.B},
               ["data/derived/jobs.parquet", "data/derived/ci_clean.parquet", "src/emission_factors.csv"])
    suffix = "/../_smoke_sens/sim_TEST_sens_s4" if args.smoke else "_sens_s4"
    cmd = [os.path.join(C.SRC, "simulate.py"), "--period", "TEST", "--traces", "PM100", "--states", args.states,
           "--out-suffix", suffix, "--workers", str(min(args.workers, 3)), "--reps", str(args.reps),
           "--n-jobs", str(args.n_jobs), "--seed", str(args.seed)]
    if args.bas:
        cmd += ["--bas", args.bas]
    ctx.log("frozen simulate.py: " + " ".join(cmd[1:]))
    rc, pk1, pkt = C.run_polled(cmd, stdout_path=ctx.logf)
    ctx.peak_workers_mb = pk1
    ctx.log(f"simulate.py rc={rc}; peak RSS single process {pk1:.0f} MB, process tree total {pkt:.0f} MB")
    if rc != 0:
        sys.exit("simulate.py failed")
    if args.sim_only:
        return
    rows = []
    for w in ("w", "u"):
        out = C.analyse(ctx.simdir(), "PM100", w, B=args.B, seed=7)
        with open(ctx.analysis_path("PM100", w), "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)
        rows += C.ledger_rows("s4", out)
        r = out["slacks"]["12"]
        ctx.log(f"S4 PM100 {w} S12: D {100*r['savings']['lgbm|req']:.2f} %, H2 {100*r['tests']['H2_runtime_penalty']['est']:.2f} pp, "
                f"H3 {100*r['tests']['H3_prediction_recovery']['est']:.2f} pp")
    C.write_ledger(ctx, rows, "sens.s4.")
    ctx.log("ledger " + ctx.ledger_path())
    ctx.footer()
    if not args.smoke:
        open(ctx.done_path(), "w").write("done\n")


if __name__ == "__main__":
    main()
