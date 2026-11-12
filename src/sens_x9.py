"""Exploratory item X9: capacity-capped replay (research/P4_PLAN_X9.md C1, binding; md5 in research/P4_PLAN_X9.md5), post-freeze.

Rule (fixed by the plan, details of the greedy order stated here):
  per BA, trace and replicate (the replicate's own job sample), the cap is 1.0 x the 99th percentile of the hourly START energy
  of the RUN-NOW arm (hourly sum of p_kW x R_act of the jobs whose run-now start falls in the hour; every hour from the first to
  the last arrival counts, empty hours as zero).  Jobs are processed in arrival order.  A capped arm ranks each job's candidate
  starts (the 0.25 h grid inside [a, a + S]) by the arm's own plan cost (planner signal x the arm's runtime estimate; the first
  rank is exactly the uncapped plan_start choice, asserted) and takes the best-ranked candidate whose start hour still has room
  (load + job energy <= cap); a job for which no candidate has room runs now.  A job larger than the cap runs now.  The load of
  a job is its actual energy (physical capacity), whatever runtime estimate the planner used.
Arms: runnow, lgbm|req, lgbm|pred, oracle|act (uncapped, same sample) and cap:lgbm|req, cap:lgbm|pred, cap:oracle|act.
Outputs: results/sim_TEST_sens_x9/<trace>/<BA>.npz (daily arrays + x9_* counters), results/analysis_TEST_sens_x9_<trace>_<w>.json,
tables/ledger_TEST_sens_x9.csv (rows replaced per trace), logs/sens_x9.log.  Share of jobs displaced = final start differs from
the uncapped choice of the same arm; 'fb' = no candidate had room (ran now).
Usage: py src/sens_x9.py --traces PM100 [--smoke --bas CISO,ERCO --n-jobs 2000 --reps 1 --B 50] [--workers 2]
"""
import glob
import os
import sys
import time
import zlib

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sens_xcommon as X  # noqa: E402
C = X.C
sc, sim = C.sc, C.sim

ARMS = ["runnow", "lgbm|req", "lgbm|pred", "oracle|act", "cap:lgbm|req", "cap:lgbm|pred", "cap:oracle|act"]
CAPPED = ["cap:lgbm|req", "cap:lgbm|pred", "cap:oracle|act"]
CAP_PCT = 99.0
CAP_MULT = 1.0
SLACK = 12.0
X9_MD5 = "6451f7813c6a38ac07ba01cf11835f3b"


def plan_cost(signal, a, r_hat, slack):
    """Copy of simcore.plan_start up to the cost matrix: returns cost [n, K] (inf where infeasible) and offs [K]."""
    n = len(a)
    W = signal.shape[1]
    cumf = np.zeros((n, W + 1))
    np.cumsum(signal, axis=1, out=cumf[:, 1:])
    k_max = int(np.ceil(np.max(slack) / sc.STEP)) if n else 0
    offs = np.arange(k_max + 1) * sc.STEP
    x0 = (a - np.floor(a))[:, None] + offs[None, :]
    x1 = np.minimum(x0 + r_hat[:, None], float(W))
    x0c = np.minimum(x0, float(W))

    def eval_cum(x):
        k = np.clip(np.floor(x).astype(np.int64), 0, W - 1)
        rows = np.arange(n)[:, None]
        return cumf[rows, k] + (x - k) * signal[rows, k]

    cost = eval_cum(x1) - eval_cum(x0c)
    cost = np.where(offs[None, :] <= slack[:, None] + 1e-9, cost, np.inf)
    return cost, offs


@X._njit
def _greedy(order, hmat, e, load, cap):
    """order [n, K] candidate indices by rank (arrival-sorted jobs), hmat [n, K] hour index of each candidate start, e [n] job
    energy, load [H] running hourly start energy.  Returns chosen candidate index and status (0 normal, 1 no room -> run now)."""
    n, K = order.shape
    chosen = np.zeros(n, np.int64)
    status = np.zeros(n, np.int64)
    for i in range(n):
        pick = -1
        for r in range(K):
            k = order[i, r]
            if load[hmat[i, k]] + e[i] <= cap + 1e-9:
                pick = k
                break
        if pick < 0:
            pick = 0
            status[i] = 1
        chosen[i] = pick
        load[hmat[i, pick]] += e[i]
    return chosen, status


def capped_starts(signal, a, r_hat, e_kwh, cap, slack, s_uncapped):
    """Capped start times for one arm.  Returns s, displaced flag, fallback flag.  Asserts that rank 1 equals plan_start."""
    cost, offs = plan_cost(signal, a, r_hat, slack)
    perm = np.argsort(a, kind="stable")                        # arrival order
    order = np.argsort(cost, axis=1, kind="stable")            # rank candidates; ties -> earlier start (as plan_start's argmin)
    assert np.array_equal(a + offs[order[:, 0]], s_uncapped), "rank-1 candidate differs from plan_start"
    hmat = np.floor(a[:, None] + offs[None, :]).astype(np.int64)
    hmat -= hmat.min()
    load = np.zeros(int(hmat.max()) + 2)
    ch, stt = _greedy(np.ascontiguousarray(order[perm]), np.ascontiguousarray(hmat[perm]), np.ascontiguousarray(e_kwh[perm]),
                      load, float(cap))
    k = np.empty(len(a), np.int64)
    k[perm] = ch
    fb = np.zeros(len(a), bool)
    fb[perm] = stt == 1
    s = a + offs[k]
    # capacity check: hours holding only jobs that found room never exceed the cap
    hs = np.floor(s).astype(np.int64)
    hs -= hs.min()
    ld = np.bincount(hs[~fb], weights=e_kwh[~fb], minlength=int(hs.max()) + 1)
    assert ld.max() <= cap + 1e-6, ("hourly start energy above the cap", ld.max(), cap)
    return s, k != order[:, 0], fb


def run_cap_cfg_selftest():
    """Tiny synthetic checks: cap = inf reproduces the uncapped plan; cap = 0 runs every job now."""
    rng = np.random.default_rng(1)
    t = np.arange(24 * 40)
    ci = 300 + 100 * np.sin(2 * np.pi * (t % 24) / 24) + rng.normal(0, 5, len(t))
    n = 3000
    a = rng.uniform(24, 24 * 30, n)
    r = rng.uniform(0.5, 10, n)
    e = rng.uniform(1, 20, n)
    S = np.full(n, 12.0)
    sig = sc.window_signal_actual(ci, a)
    s0 = sc.plan_start(sig, a, r, S)
    s_inf, d, fb = capped_starts(sig, a, r, e, np.inf, S, s0)
    assert np.array_equal(s_inf, s0) and not d.any() and not fb.any()
    s_z, d, fb = capped_starts(sig, a, r, e, 0.0, S, s0)
    assert np.array_equal(s_z, a) and fb.all()
    h = np.floor(a).astype(np.int64)
    run_now_load = np.bincount(h - h.min(), weights=e)
    cap = np.percentile(run_now_load, 99)
    s_c, d, fb = capped_starts(sig, a, r, e, cap, S, s0)
    assert d.any() and (s_c >= a - 1e-9).all() and (s_c <= a + 12 + 1e-9).all()
    return True


def run_ba_x9(ba, cfg, jobs_by_trace, offsets):
    origin, ci, usable, _ = sim.load_ba(ba, cfg["tag"])
    cum_ci = sc.cum_hours(ci)
    off = offsets[ba]
    fcs = {"lgbm": sim.load_fc(cfg["fc_src"]["lgbm"][0], cfg["fc_src"]["lgbm"][1], ba, origin)}
    n_arms = len(ARMS)
    for trace, jobs in jobs_by_trace.items():
        res = {}
        ex = {k: [] for k in ("disp", "fb", "dispE", "n", "E", "cap", "nbind_hours", "over", "overE")}
        for rep in range(cfg["reps"]):
            rng = np.random.default_rng([cfg["seed"], rep, zlib.crc32(ba.encode()), zlib.crc32(trace.encode())])
            nj = len(jobs["r_act_h"])
            idx = np.sort(rng.choice(nj, size=min(cfg["n_jobs"], nj), replace=False))
            J = {k: np.asarray(v[idx]) for k, v in jobs.items()}
            a, ok = sim.place_jobs(J, C.PERIOD, origin, off, rng, usable)
            J, a = {k: v[ok] for k, v in J.items()}, a[ok]
            r_act = J["r_act_h"]
            p_kw = J["power_kw"]
            e_kwh = (p_kw * r_act).astype("float64")
            day = np.floor(a / 24.0).astype(np.int64)
            lcls = np.searchsorted(sim.LEN_EDGES, r_act, side="right") - 1
            env = X.Env(cfg, ba, trace, rep, cfg["seed"], ci, cum_ci, a, J, fcs, None, {}, {})
            h0 = np.floor(a).astype(np.int64)
            hourly = np.bincount(h0 - h0.min(), weights=e_kwh)           # every hour from first to last arrival (zeros included)
            cap = CAP_MULT * float(np.percentile(hourly, CAP_PCT))
            slack = np.full(len(a), SLACK)
            st, disp, fbk = {}, {}, {}
            for x in ARMS:
                if x.startswith("cap:"):
                    base = x[4:]
                    sig, rt = base.split("|")
                    st[x], disp[x], fbk[x] = capped_starts(env.signal(sig), a, env.runtime(rt), e_kwh, cap, slack, st[base])
                else:
                    st[x] = env.starts(x, slack)
            e_w = np.stack([p_kw * sc.realised(cum_ci, ci, st[x], r_act) for x in ARMS])
            e_u = np.stack([sc.realised(cum_ci, ci, st[x], r_act) / r_act for x in ARMS])
            delay = np.stack([st[x] - a for x in ARMS])
            res[(rep, int(SLACK))] = {"day": day, "lcls": lcls, "e_w": e_w.astype("float32"), "e_u": e_u.astype("float32"),
                                      "delay": delay.astype("float32"), "energy_kwh": e_kwh.astype("float32")}
            dsp, fbs, dsE = np.zeros(n_arms), np.zeros(n_arms), np.zeros(n_arms)
            for i, x in enumerate(ARMS):
                if x in disp:
                    dsp[i], fbs[i], dsE[i] = disp[x].sum(), fbk[x].sum(), e_kwh[disp[x]].sum()
            ex["disp"].append(dsp)
            ex["fb"].append(fbs)
            ex["dispE"].append(dsE)
            ex["n"].append(len(a))
            ex["E"].append(float(e_kwh.sum()))
            ex["cap"].append(cap)
            ex["over"].append(int((e_kwh > cap + 1e-9).sum()))
            ex["overE"].append(float(e_kwh[e_kwh > cap + 1e-9].sum()))
            ex["nbind_hours"].append(int((hourly >= cap - 1e-9).sum()))
            del env
        d = os.path.join(cfg["outdir"], trace)
        os.makedirs(d, exist_ok=True)
        flat = {}
        for kk, v in C.aggregate_arms(res, n_arms).items():
            for k2, vv in v.items():
                flat[f"{kk}__{k2}"] = vv
        np.savez_compressed(os.path.join(d, f"{ba}.npz"), arms=np.array(ARMS), x9_disp=np.array(ex["disp"]), x9_fb=np.array(ex["fb"]),
                            x9_dispE=np.array(ex["dispE"]), x9_n=np.array(ex["n"]), x9_E=np.array(ex["E"]), x9_cap=np.array(ex["cap"]),
                            x9_runnow_hours_at_cap=np.array(ex["nbind_hours"]), x9_over=np.array(ex["over"]), x9_overE=np.array(ex["overE"]), **flat)
        del res
    return ba, C.peak_rss_mb()


def run_x9(ctx, cfg, jobs, bas, workers):
    from joblib import Parallel, delayed
    workers = min(workers, 2)
    offsets = sim.ba_offsets()
    t0 = time.time()
    out = Parallel(n_jobs=workers, verbose=0)(delayed(run_ba_x9)(ba, cfg, jobs, offsets) for ba in bas)
    ctx.peak_workers_mb = max(ctx.peak_workers_mb, max(p for _, p in out))
    ctx.log(f"simulated {len(bas)} BAs x {len(jobs)} traces x {cfg['reps']} reps, {len(ARMS)} arms, in {time.time() - t0:.0f} s; "
            f"worker peak RSS {ctx.peak_workers_mb:.0f} MB")


def disp_rows(sid, simdir, trace):
    """Pooled displaced / fallback shares per capped arm, per-BA median share, cap level and run-now hours at the cap."""
    files = sorted(glob.glob(os.path.join(simdir, trace, "*.npz")))
    tot = None
    per_ba, caps, atcap = [], [], []
    for f in files:
        z = np.load(f)
        d = {k: z[k].sum(axis=0) if z[k].ndim > 1 else z[k].sum() for k in ("x9_disp", "x9_fb", "x9_dispE", "x9_n", "x9_E", "x9_over", "x9_overE")}
        tot = d if tot is None else {k: tot[k] + d[k] for k in d}
        per_ba.append(d["x9_disp"] / d["x9_n"])
        caps.append(float(z["x9_cap"].mean()))
        atcap.append(float(z["x9_runnow_hours_at_cap"].mean()))
    arms = ARMS
    rows = []
    for i, x in enumerate(arms):
        if x not in CAPPED:
            continue
        k0 = f"sens.{sid}.{trace}.S12.{x}"
        rows += [(f"{k0}.displaced_job_share", float(tot["x9_disp"][i] / tot["x9_n"])),
                 (f"{k0}.fallback_run_now_job_share", float(tot["x9_fb"][i] / tot["x9_n"])),
                 (f"{k0}.displaced_energy_share", float(tot["x9_dispE"][i] / tot["x9_E"])),
                 (f"{k0}.displaced_job_share_median_ba", float(np.median([p[i] for p in per_ba]))),
                 (f"{k0}.displaced_job_share_max_ba", float(np.max([p[i] for p in per_ba])))]
    rows += [(f"sens.{sid}.{trace}.S12.cap_kwh_per_hour_median_ba", float(np.median(caps))),
             (f"sens.{sid}.{trace}.S12.runnow_hours_at_cap_mean_ba", float(np.mean(atcap))),
             (f"sens.{sid}.{trace}.S12.oversize_job_share", float(tot["x9_over"] / tot["x9_n"])),
             (f"sens.{sid}.{trace}.S12.oversize_energy_share", float(tot["x9_overE"] / tot["x9_E"])),
             (f"sens.{sid}.{trace}.S12.n_jobs_total", float(tot["x9_n"]))]
    return rows


def main():
    ap = X.std_parser(__doc__)
    args = ap.parse_args()
    ctx = C.Ctx("x9", args.smoke)
    X.verify_plans()
    C.sim.check_prereg()
    if C.md5_file(os.path.join(C.ROOT, "research", "P4_PLAN_X9.md")) != X9_MD5:
        sys.exit("research/P4_PLAN_X9.md changed after its md5 was written")
    X.dump_item_header(ctx, {"sim_seed": args.seed, "analysis_seed": 7, "B": args.B, "reps": args.reps, "n_jobs": args.n_jobs,
                             "cap": f"{CAP_MULT} x p{CAP_PCT} of run-now hourly start energy"})
    ctx.log("P4_PLAN_X9.md md5: " + X9_MD5)
    run_cap_cfg_selftest()
    ctx.log("selftest passed (cap = inf reproduces the uncapped plan, cap = 0 runs every job now, cap respected)")
    bas = C.eligible_bas(args.bas.split(",") if args.bas else None)
    contrasts = {f"cap_cost_{x[4:]}": ([x], [x[4:]]) for x in CAPPED}
    for trace in args.traces.split(","):
        t0 = time.time()
        jobs = X.load_jobs_x(traces=[trace], log=ctx.log)
        cfg = dict(tag="", arms=ARMS, slacks=(SLACK,), seed=args.seed, reps=args.reps, n_jobs=args.n_jobs,
                   fc_src={"lgbm": ("data/derived/forecasts", "lgbm")}, outdir=ctx.simdir())
        run_x9(ctx, cfg, jobs, bas, args.workers)
        rows = []
        for w in ("w", "u"):
            out = X.analyse_x(cfg["outdir"], trace, w, contrasts, B=args.B, seed=7, S=int(SLACK))
            rows += X.rows_x(ctx.sid, out)
            sv = out["savings"]
            for x in CAPPED:                           # retained share of the uncapped saving (point estimate, no interval)
                if sv[x[4:]] != 0:
                    rows.append((f"sens.x9.{trace}.{w}.S12.retained_share_of_uncapped.{x}", sv[x] / sv[x[4:]]))
            if w == "w":
                md = X.mean_delay(cfg["outdir"], trace, int(SLACK))
                rows += [(f"sens.x9.{trace}.w.S12.meandelay_h.{a}", v) for a, v in md.items()]
                ctx.log(f"x9 {trace} w S12: " + "; ".join(f"{a} {100 * v:.2f} %" for a, v in sv.items() if a != "runnow"))
            import json
            with open(ctx.analysis_path(trace, w), "w", encoding="utf-8") as fh:
                json.dump(out, fh, indent=1)
        rows += disp_rows(ctx.sid, cfg["outdir"], trace)
        C.write_ledger(ctx, rows, f"sens.x9.{trace}.")
        ctx.log(f"x9 {trace} finished in {(time.time() - t0) / 60:.1f} min; ledger {ctx.ledger_path()}")
        del jobs
    ctx.footer()
    if not args.smoke:
        open(ctx.done_path(), "w").write("done\n")


if __name__ == "__main__":
    main()
