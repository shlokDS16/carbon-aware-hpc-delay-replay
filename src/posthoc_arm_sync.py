"""Post-hoc PH1 extension (A31): synchronised-week 95 % interval for the saving of EVERY arm (PH1 stored it only for the
contrasts D, H1-H4, gap, Shapley terms). Same draws as src/posthoc_inference.py sync_boot (same week indices for all BAs,
seed 7 + S, B = 2000); reads only results/sim_TEST/<trace>/*.npz; frozen files untouched; POST-HOC, descriptive.

Usage: py src/posthoc_arm_sync.py [--traces PM100,FDATA,KIT_FH2] [--B 2000]
Writes tables/ledger_TEST_posthoc_armsync.csv with keys posthoc.PH1arm.<trace>.w.S<S>.<arm>.{est,sync_lo,sync_hi}
(energy-weighted only). The point estimate is checked against tables/ledger_TEST.csv.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze as A  # noqa: E402
import posthoc_inference as P  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--traces", default="PM100,FDATA,KIT_FH2")
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    led = pd.read_csv(os.path.join(A.ROOT, "tables", "ledger_TEST.csv")).set_index("key")["value"]
    rows = []
    for trace in a.traces.split(","):
        arms, data = P.load_ext(trace, "w")
        bas = sorted(data)
        na = len(arms)
        idx = {x: i for i, x in enumerate(arms)}
        for S in A.SLACKS:
            tot_pt, tot_b, nf, Dg = P.sync_boot([data[b][S] for b in bas], a.B, a.seed + S)
            sv = A.savings_from(tot_pt[:na], idx)
            sb = np.stack([A.savings_from(tot_b[i, :na], idx) for i in range(a.B)])
            for arm in arms:
                if arm == "runnow":
                    continue
                k = f"posthoc.PH1arm.{trace}.w.S{int(S)}.{arm}"
                lo, hi = np.quantile(sb[:, idx[arm]], [0.025, 0.975])
                key = f"TEST.{trace}.w.S{int(S)}.saving.{arm}"
                if key in led.index:
                    assert abs(led[key] - sv[idx[arm]]) < 1e-9, key
                rows += [(k + ".est", float(sv[idx[arm]])), (k + ".sync_lo", float(lo)), (k + ".sync_hi", float(hi))]
        print(trace, "done", flush=True)
    df = pd.DataFrame(rows, columns=["key", "value"])
    df["source"] = "src/posthoc_arm_sync.py from results/sim_TEST (synchronised-week bootstrap, B=%d, seed 7+S)" % a.B
    df.to_csv(os.path.join(A.ROOT, "tables", "ledger_TEST_posthoc_armsync.csv"), index=False)


if __name__ == "__main__":
    main()
