"""P4 amendment arms (research/P4_PLAN_AMEND.md section D), exploratory, post-freeze.  --item arms | shift

arms  (id 'arms'): forecast-free threshold rule (start at the first quarter-hour whose most recent COMPLETED hourly intensity is
      below the trailing 7-day 25th percentile, else a + S; only data known at decision time, asserted and tested), padded runtime
      estimate min(R_req, 1.5 x pred), quantile runtime estimate (user's 90th percentile of past actual runtimes that ended before
      submission, >= 5 past jobs, capped at R_req, else R_req).  Signals oracle and lgbm, S = 12 h, all three traces, w and u.
      Also reported: runtime-estimate accuracy of req / pred / pad / q, mean delays.
shift (id 'shift'): placement check, PM100, arrivals shifted by -3, 0, +3 h of local clock, arms lgbm|req, lgbm|pred (+ runnow,
      lgbm|act, oracle|act), all slacks.  z0 (no shift) reproduces the frozen numbers.
Usage: py src/sens_arms.py --item arms|shift [--smoke --bas CISO,ERCO --n-jobs 2000 --reps 1 --B 50]
Outputs: results/sim_TEST_sens_<id>/..., tables/ledger_TEST_sens_<id>.csv, logs/sens_<id>.log
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sens_xcommon as X  # noqa: E402
C = X.C

ARMS = ["runnow", "thresh", "oracle|act", "oracle|req", "oracle|pred", "oracle|pad", "oracle|q",
        "lgbm|act", "lgbm|req", "lgbm|pred", "lgbm|pad", "lgbm|q"]
CONTRASTS = {
    "thresh_minus_lgbm_req": (["thresh"], ["lgbm|req"]),
    "thresh_minus_lgbm_pred": (["thresh"], ["lgbm|pred"]),
    "lgbm_pad_minus_req": (["lgbm|pad"], ["lgbm|req"]),
    "lgbm_q_minus_req": (["lgbm|q"], ["lgbm|req"]),
    "lgbm_pad_minus_pred": (["lgbm|pad"], ["lgbm|pred"]),
    "lgbm_q_minus_pred": (["lgbm|q"], ["lgbm|pred"]),
    "lgbm_act_minus_pad": (["lgbm|act"], ["lgbm|pad"]),
    "lgbm_act_minus_q": (["lgbm|act"], ["lgbm|q"]),
    "oracle_pad_minus_req": (["oracle|pad"], ["oracle|req"]),
    "oracle_q_minus_req": (["oracle|q"], ["oracle|req"]),
    "oracle_act_minus_lgbm_req": (["oracle|act"], ["lgbm|req"]),
}
SHIFT_ARMS = ["runnow", "oracle|act", "lgbm|act", "lgbm|req", "lgbm|pred"]
SHIFT_CONTRASTS = {"H2_penalty": (["lgbm|act"], ["lgbm|req"]), "H3_recovery": (["lgbm|pred"], ["lgbm|req"])}


def causality_check(ctx, ba, jobs):
    """Threshold decisions must not depend on any intensity at or after the chosen start (see xcommon.threshold_causality_test)."""
    offsets = C.sim.ba_offsets()
    origin, ci, usable, _ = C.sim.load_ba(ba, "")
    t = next(iter(jobs))
    rng = np.random.default_rng(5)
    nj = len(jobs[t]["r_act_h"])
    idx = np.sort(rng.choice(nj, size=min(3000, nj), replace=False))
    J = {k: np.asarray(v[idx]) for k, v in jobs[t].items()}
    a, ok = C.sim.place_jobs(J, C.PERIOD, origin, offsets[ba], rng, usable)
    a = a[ok]
    X.threshold_causality_test(ci, a, 12.0)
    s, mx = X.threshold_starts(ci, X.trailing_q25(ci), a, 12.0, return_maxidx=True)
    ctx.log(f"threshold causality test passed ({ba}, {t}, {len(a)} jobs; 40 decisions recomputed after overwriting every "
            f"intensity at or after the chosen start with garbage); mean delay {np.mean(s - a):.2f} h; "
            f"share started at a + S {np.mean(s - a >= 12 - 1e-9):.3f}")


def main():
    ap = X.std_parser(__doc__)
    ap.add_argument("--item", required=True, choices=["arms", "shift"])
    args = ap.parse_args()
    sid = args.item
    ctx = C.Ctx(sid, args.smoke)
    X.verify_plans()
    C.sim.check_prereg()
    X.dump_item_header(ctx, {"sim_seed": args.seed, "analysis_seed": 7, "B": args.B, "reps": args.reps, "n_jobs": args.n_jobs})
    if sid == "arms":
        jobs = X.load_jobs_x(traces=args.traces.split(","), log=ctx.log)
        bas = C.eligible_bas(args.bas.split(",") if args.bas else None)
        causality_check(ctx, bas[0], jobs)
        rows, outs, _ = X.run_standard(ctx, args, ARMS, CONTRASTS, jobs=jobs)
        rows.append(("sens.arms.threshold_causality_test_passed", 1))
        for t in args.traces.split(","):
            st = X.runtime_stats(jobs[t], ["req", "pred", "pad", "q"])
            for r, d in st.items():
                rows += [(f"sens.arms.{t}.rt_{r}.{k}", v) for k, v in d.items()]
            rows.append((f"sens.arms.{t}.share_jobs_with_5_past", float(np.mean(jobs[t]["n_q"] >= X.Q_MIN_N))))
            rows.append((f"sens.arms.{t}.n_filtered_jobs", len(jobs[t]["r_act_h"])))
            ctx.log(f"runtime accuracy {t}: " + json_short(st))
    else:
        args.traces = "PM100"
        variants = {"m3": {"shift_h": -3.0}, "z0": {"shift_h": 0.0}, "p3": {"shift_h": 3.0}}
        rows, outs, _ = X.run_standard(ctx, args, SHIFT_ARMS, SHIFT_CONTRASTS, variants=variants, slacks=C.SLACKS)
        for S in C.SLACKS:
            for w in ("w", "u"):
                for lab in ("m3", "p3"):
                    for arm in ("lgbm|req", "lgbm|pred"):
                        d = outs[(lab, "PM100", w, int(S))]["savings"][arm] - outs[("z0", "PM100", w, int(S))]["savings"][arm]
                        rows.append((f"sens.shift.PM100.{w}.S{int(S)}.diff_vs_z0.{lab}.{arm}", d))
    X.finish_item(ctx, rows, args.smoke)


def json_short(st):
    return "; ".join(f"{r}: under {100 * d['share_under']:.1f} %, rms log {d['rms_log']:.2f}" for r, d in st.items())


if __name__ == "__main__":
    main()
