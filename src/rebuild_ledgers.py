"""Rebuild tables/ledger_TEST.csv and tables/ledger_TEST_nearlimit.csv from the saved simulation results with the FROZEN
src/analyze.py, writing into a temporary folder, and check equality with the stored files (PH5 of research/PANEL_DECISIONS.md).

The frozen analyze.py reads results/sim_<period><tag>/ and writes under its ROOT; here its ROOT is pointed at a temp folder
and glob is redirected so the saved simulation files are read from the real folder. Nothing in results/ or tables/ is written.
Usage: py src/rebuild_ledgers.py [--B 2000] [--keep]
Prints PASS or the differences (key sets, max abs difference of values, source strings).
"""
import argparse
import glob as _glob
import os
import shutil
import sys
import tempfile
import time

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze as A  # noqa: E402  (frozen)

REAL = A.ROOT
RUNS = [  # (tag, trace, weight, boot) in the order the TEST analyses were run
    *[("", t, w, "fixed") for t in ("PM100", "FDATA", "KIT_FH2") for w in ("w", "u")],
    *[("", t, "w", "twostage") for t in ("PM100", "FDATA", "KIT_FH2")],
    *[("_nearlimit", t, "w", "fixed") for t in ("PM100", "FDATA", "KIT_FH2")],
]


def compare(stored, rebuilt, name):
    a = pd.read_csv(stored)
    b = pd.read_csv(rebuilt)
    ok = True
    ka, kb = set(a.key), set(b.key)
    if ka != kb:
        ok = False
        print(f"  {name}: key sets differ; only stored {len(ka - kb)}, only rebuilt {len(kb - ka)}")
    m = a.merge(b, on="key", suffixes=("_s", "_r"))
    d = (m["value_s"] - m["value_r"]).abs()
    src_diff = int((m["source_s"] != m["source_r"]).sum())
    exact = int((d == 0).sum())
    print(f"  {name}: stored {len(a)} rows, rebuilt {len(b)} rows, common {len(m)}; exactly equal {exact}; "
          f"max abs diff {d.max():.3g}; source strings differing {src_diff}")
    if d.max() > 1e-12 or src_diff:
        ok = False
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="rebuild_ledgers_")
    os.makedirs(os.path.join(tmp, "results"))
    os.makedirs(os.path.join(tmp, "tables"))
    A.ROOT = tmp
    real_glob = _glob.glob
    A.glob.glob = lambda pat, *a, **k: real_glob(pat.replace(tmp, REAL), *a, **k)   # read sim files from the real folder
    t0 = time.time()
    for tag, trace, weight, boot in RUNS:
        sys.argv = ["analyze.py", "--period", "TEST", "--tag", tag, "--trace", trace, "--weight", weight, "--B", str(args.B),
                    "--boot", boot]
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            A.main()
        print(f"rebuilt TEST{tag} {trace} {weight} {boot} ({time.time() - t0:.0f}s)", flush=True)
    A.glob.glob = real_glob
    ok = True
    for name in ("ledger_TEST.csv", "ledger_TEST_nearlimit.csv"):
        ok &= compare(os.path.join(REAL, "tables", name), os.path.join(tmp, "tables", name), name)
    print("PASS" if ok else "DIFFERENCES FOUND")
    if not args.keep:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
