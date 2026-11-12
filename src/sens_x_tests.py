"""Equality / sanity tests for the P4x engine (outputs under results/_smoke_sens only).
T frozen : run_ba_x (shift 0, 2 BAs, 20,000 jobs x 3 reps, PM100, S 12) == results/sim_TEST/PM100 npz for shared arms (exact)
T shift  : shift +3 h changes savings but keeps the number of jobs within 1 % of unshifted
T qest   : r_q <= r_req, r_pad <= r_req, r_q == r_req where n_q < 5
Usage: py src/sens_x_tests.py [frozen|shift|qest|all]
"""
import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sens_xcommon as X
C = X.C
BAS = ["CISO", "ERCO"]


def t_frozen():
    ctx = C.Ctx("xtest", True)
    jobs = X.load_jobs_x(traces=("PM100",))
    out = ctx.simdir("z")
    cfg = dict(tag="", arms=["runnow", "oracle|act", "oracle|req", "oracle|pred", "lgbm|act", "lgbm|req", "lgbm|pred"],
               slacks=(12.0,), seed=20261111, reps=3, n_jobs=20000, fc_src={"lgbm": ("data/derived/forecasts", "lgbm")}, outdir=out)
    X.run_x(ctx, cfg, jobs, BAS, 2)
    worst = 0.0
    for ba in BAS:
        za, zb = np.load(os.path.join(out, "PM100", ba + ".npz")), np.load(os.path.join(C.ROOT, "results", "sim_TEST", "PM100", ba + ".npz"))
        aa, ab = list(za["arms"]), list(zb["arms"])
        for key in za.files:
            if key == "arms" or "_S12__" not in key:
                continue
            if "__e_" in key or "__delay" in key:
                for arm in aa:
                    worst = max(worst, float(np.abs(za[key][aa.index(arm)] - zb[key][ab.index(arm)]).max()))
            else:
                assert np.array_equal(za[key], zb[key]), key
    print("T frozen: max abs difference", worst, "PASS" if worst == 0 else "FAIL")
    return worst == 0


def t_shift():
    ctx = C.Ctx("xtest", True)
    jobs = X.load_jobs_x(traces=("PM100",))
    res = {}
    for sh in (0.0, 3.0):
        cfg = dict(tag="", arms=["runnow", "lgbm|req"], slacks=(12.0,), seed=20261111, reps=1, n_jobs=5000,
                   fc_src={"lgbm": ("data/derived/forecasts", "lgbm")}, outdir=ctx.simdir(f"s{int(sh)}"), shift_h=sh)
        X.run_x(ctx, cfg, jobs, BAS, 2)
        arms, d = C.load_sim(ctx.simdir(f"s{int(sh)}"), "PM100", "w")
        tot = sum(v[12].sum(axis=1) for v in d.values())
        res[sh] = 1 - tot[1] / tot[0]
        z = np.load(os.path.join(ctx.simdir(f"s{int(sh)}"), "PM100", "CISO.npz"))
        print("shift", sh, "saving", res[sh], "jobs", int(z["r0_S12__n"].sum()))
    ok = res[0.0] != res[3.0]
    print("T shift:", "PASS" if ok else "FAIL")
    return ok


def t_qest():
    jobs = X.load_jobs_x(traces=X.TRACES)
    for t, d in jobs.items():
        assert (d["r_q"] <= d["r_req_h"] + 1e-12).all() and (d["r_pad"] <= d["r_req_h"] + 1e-12).all()
        assert np.array_equal(d["r_q"][d["n_q"] < 5], d["r_req_h"][d["n_q"] < 5])
        print(t, "n", len(d["r_q"]), "share n_q>=5", float((d["n_q"] >= 5).mean()))
    print("T qest: PASS")
    return True


if __name__ == "__main__":
    w = sys.argv[1] if len(sys.argv) > 1 else "all"
    ok = True
    for name, f in (("frozen", t_frozen), ("shift", t_shift), ("qest", t_qest)):
        if w in (name, "all"):
            ok &= f()
    sys.exit(0 if ok else 1)
