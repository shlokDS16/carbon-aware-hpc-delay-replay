"""Sanity tests of the S1-S5 wrappers against the frozen code path (outputs under results/_smoke_sens only).
Usage: py src/sens_smoke_tests.py [s4|s2k0|frozen|mirror|all]
T s4     S4 wrapper (states COMPLETED) == direct frozen simulate.py call on the same tiny configuration (exact)
T s2k0   S2 generic runner at k = 0 == frozen simulate.py npz for the shared arms on the same tiny configuration (exact)
T frozen S4 wrapper (COMPLETED, 2 BAs, full 20,000 jobs x 3 reps) == results/sim_TEST/PM100 npz (exact)
T mirror sens_common.analyse == frozen analysis JSON results/analysis_TEST_PM100_w.json (B = 2000, seed 7)
"""
import json
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sens_common as C  # noqa: E402

SM = os.path.join(C.ROOT, "results", "_smoke_sens")
BAS = "CISO,ERCO"


def run(args):
    p = subprocess.run([sys.executable] + args, cwd=C.ROOT, capture_output=True, text=True)
    if p.returncode:
        print(p.stdout[-2000:], p.stderr[-2000:])
        sys.exit("subprocess failed: " + " ".join(args))


def compare(dir_a, dir_b, trace, bas, arms_common=None):
    worst = 0.0
    for ba in bas.split(","):
        za, zb = np.load(os.path.join(dir_a, trace, ba + ".npz")), np.load(os.path.join(dir_b, trace, ba + ".npz"))
        aa, ab = list(za["arms"]), list(zb["arms"])
        common = arms_common or [x for x in aa if x in ab]
        assert common, "no common arms"
        for key in za.files:
            if key == "arms":
                continue
            if "__e_" in key or "__delay" in key:
                A, B = za[key], zb[key]
                for arm in common:
                    d = np.abs(A[aa.index(arm)] - B[ab.index(arm)]).max()
                    worst = max(worst, float(d))
            else:
                assert np.array_equal(za[key], zb[key]), f"{ba} {key} differs"
    return worst


def t_s4():
    run([os.path.join(C.SRC, "simulate.py"), "--period", "TEST", "--traces", "PM100", "--states", "COMPLETED",
         "--out-suffix", "/../_smoke_sens/sim_direct_s4", "--workers", "2", "--reps", "1", "--n-jobs", "2000", "--bas", BAS])
    run([os.path.join(C.SRC, "sens_s4.py"), "--smoke", "--states", "COMPLETED", "--bas", BAS, "--n-jobs", "2000",
         "--reps", "1", "--B", "100", "--workers", "2", "--sim-only"])
    w = compare(os.path.join(SM, "sim_direct_s4"), os.path.join(SM, "sim_TEST_sens_s4"), "PM100", BAS)
    print("T s4: max abs difference", w, "PASS" if w == 0 else "FAIL")
    return w == 0


def t_s2k0():
    run([os.path.join(C.SRC, "simulate.py"), "--period", "TEST", "--traces", "PM100", "--states", "COMPLETED",
         "--out-suffix", "/../_smoke_sens/sim_direct_s4", "--workers", "2", "--reps", "1", "--n-jobs", "2000", "--bas", BAS])
    run([os.path.join(C.SRC, "sens_s2.py"), "--smoke", "--bas", BAS, "--n-jobs", "2000", "--reps", "1", "--ks", "0",
         "--traces", "PM100", "--B", "100", "--workers", "2"])
    w = compare(os.path.join(SM, "sim_direct_s4"), os.path.join(SM, "sim_TEST_sens_s2", "k0"), "PM100", BAS)
    print("T s2k0: max abs difference", w, "PASS" if w == 0 else "FAIL")
    return w == 0


def t_frozen():
    run([os.path.join(C.SRC, "sens_s4.py"), "--smoke", "--states", "COMPLETED", "--bas", BAS, "--workers", "2", "--sim-only"])
    w = compare(os.path.join(C.ROOT, "results", "sim_TEST"), os.path.join(SM, "sim_TEST_sens_s4"), "PM100", BAS)
    print("T frozen: max abs difference vs results/sim_TEST", w, "PASS" if w == 0 else "FAIL")
    return w == 0


def t_s3clean():
    """Cleaning the CI rebuilt from shares with the frozen lifecycle factors reproduces data/derived/ci_clean.parquet."""
    import pandas as pd
    import sens_s3 as S3
    tag = "_smoke_life"
    path = S3.build_clean("life", tag, ["CISO", "ERCO"], print)
    new = pd.read_parquet(path).sort_values(["ba", "utc"]).reset_index(drop=True)
    old = pd.read_parquet(os.path.join(C.ROOT, "data", "derived", "ci_clean.parquet"))
    old = old[old["ba"].isin(["CISO", "ERCO"])].sort_values(["ba", "utc"]).reset_index(drop=True)
    ok = len(new) == len(old) and (new["utc"] == old["utc"]).all() and (new["flag"] == old["flag"]).all()         and (new["usable_day"] == old["usable_day"]).all()         and np.allclose(new["ci_clean"], old["ci_clean"], atol=1e-3, equal_nan=True)
    d = float(np.nanmax(np.abs(new["ci_clean"] - old["ci_clean"]))) if len(new) == len(old) else -1
    os.remove(path)
    print("T s3clean: rows", len(new), len(old), "max abs ci diff", d, "PASS" if ok else "FAIL")
    return ok


def t_mirror():
    fz = json.load(open(os.path.join(C.ROOT, "results", "analysis_TEST_PM100_w.json")))
    out = C.analyse(os.path.join(C.ROOT, "results", "sim_TEST"), "PM100", "w", B=2000, seed=7)
    worst = 0.0
    for S, r in fz["slacks"].items():
        for a, v in r["savings"].items():
            worst = max(worst, abs(v - out["slacks"][S]["savings"][a]),
                        abs(r["savings_ci95"][a][0] - out["slacks"][S]["savings_ci95"][a][0]))
        for n, t in r["tests"].items():
            o = out["slacks"][S]["tests"][n]
            worst = max(worst, abs(t["est"] - o["est"]), abs(t["p"] - o["p"]), abs(t["ci95"][0] - o["ci95"][0]))
        for k, v in r["shapley"].items():
            if v is not None:
                worst = max(worst, abs(v - out["slacks"][S]["shapley"][k]))
        assert r["per_ba_H2_counts"] == out["slacks"][S]["per_ba_H2_counts"]
    print("T mirror: max abs difference vs frozen analysis JSON", worst, "PASS" if worst < 1e-12 else "FAIL")
    return worst < 1e-12


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    fns = {"s4": t_s4, "s2k0": t_s2k0, "frozen": t_frozen, "s3clean": t_s3clean, "mirror": t_mirror}
    ok = True
    for name, fn in fns.items():
        if which in ("all", name):
            ok &= bool(fn())
    print("ALL PASS" if ok else "SOME FAIL")
