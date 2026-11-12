"""Hourly production-based carbon intensity per US balancing authority from EIA-930 BALANCE files.

CI_t = sum_f max(g_f,t, 0) * EF_f / sum_f max(g_f,t, 0)   (g/kWh), using the (Adjusted) net generation by fuel.

Usage: python -I src/build_ci.py [--pilot]
  --pilot  fills TO_VERIFY factors with provisional values and tags outputs _v0 (never used for final results).
Outputs: data/derived/ci_hourly[_v0].parquet, tables/ba_coverage[_v0].csv
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "eia930")
PILOT = "--pilot" in sys.argv
TAG = "_v0" if PILOT else ""
PROVISIONAL = {"oil": 650.0, "other": 700.0, "unknown": 700.0}  # legacy pilot fallback; unused now that the CSV has values

ef = pd.read_csv(os.path.join(ROOT, "src", "emission_factors.csv"))
factors = {}
for _, r in ef.iterrows():
    v = r["lifecycle_g_per_kwh"]
    if str(v) == "TO_VERIFY":
        if not PILOT:
            sys.exit(f"factor for {r['fuel']} not verified; run with --pilot for a provisional build")
        v = PROVISIONAL[r["fuel"]]
    factors[r["fuel"]] = (r["eia_columns"].split("|"), float(v))

base_cols = ["Balancing Authority", "UTC Time at End of Hour", "Region",
             "Demand (MW) (Adjusted)", "Net Generation (MW) (Adjusted)"]
schema_log = []

parts = []
for path in sorted(glob.glob(os.path.join(RAW, "EIA930_BALANCE_*.csv"))):
    header = pd.read_csv(path, nrows=0).columns.tolist()
    fuel_cols = {f: [c for c in cols if c in header] for f, (cols, _) in factors.items()}
    for f, cols in fuel_cols.items():
        if not cols:
            sys.exit(f"{os.path.basename(path)}: no column for fuel {f}")
    schema_log.append({"file": os.path.basename(path), **{f: "|".join(c) for f, c in fuel_cols.items()}})
    usecols = base_cols + sorted({c for cols in fuel_cols.values() for c in cols})
    d = pd.read_csv(path, usecols=usecols, thousands=",", low_memory=False)
    d["utc"] = pd.to_datetime(d["UTC Time at End of Hour"], format="%m/%d/%Y %I:%M:%S %p", utc=True)
    out = pd.DataFrame({"ba": d["Balancing Authority"].astype("category"),
                        "region": d["Region"].astype("category"), "utc": d["utc"]})
    gen = np.zeros((len(d), len(factors)), dtype="float64")
    for j, fuel in enumerate(factors):
        block = d[fuel_cols[fuel]].apply(pd.to_numeric, errors="coerce")
        present = block.notna().any(axis=1).to_numpy()
        g = block.sum(axis=1, min_count=1).to_numpy(dtype="float64")  # sum sub-columns before clipping
        out["n_" + fuel] = present
        gen[:, j] = np.clip(np.nan_to_num(g, nan=0.0), 0.0, None)
    any_fuel = np.column_stack([out["n_" + f].to_numpy() for f in factors]).any(axis=1)
    total = gen.sum(axis=1)
    efv = np.array([v for _, v in factors.values()])
    with np.errstate(invalid="ignore", divide="ignore"):
        ci = np.where(any_fuel & (total > 0), gen @ efv / total, np.nan)
    out = out[["ba", "region", "utc"]].copy()
    out["ci"] = ci.astype("float32")
    out["gen_total_mw"] = total.astype("float32")
    for j, fuel in enumerate(factors):
        with np.errstate(invalid="ignore", divide="ignore"):
            out["share_" + fuel] = np.where(total > 0, gen[:, j] / total, np.nan).astype("float32")
    out["demand_mw"] = pd.to_numeric(d["Demand (MW) (Adjusted)"], errors="coerce").astype("float32")
    parts.append(out)
    print(os.path.basename(path), len(out), flush=True)

pd.DataFrame(schema_log).to_csv(os.path.join(ROOT, "tables", f"eia930_schema_map{TAG}.csv"), index=False)
df = pd.concat(parts, ignore_index=True)
df["ba"] = df["ba"].astype(str)
df["region"] = df["region"].astype(str)
df = df.drop_duplicates(["ba", "utc"], keep="last").sort_values(["ba", "utc"]).reset_index(drop=True)
os.makedirs(os.path.join(ROOT, "data", "derived"), exist_ok=True)
df.to_parquet(os.path.join(ROOT, "data", "derived", f"ci_hourly{TAG}.parquet"), index=False)

# coverage and character per BA
rows = []
for ba, g in df.groupby("ba"):
    span = pd.date_range(g["utc"].min(), g["utc"].max(), freq="h")
    valid = g["ci"].notna()
    gd = g[valid].set_index("utc")["ci"]
    daily_range = (gd.resample("D").max() - gd.resample("D").min()).median() if len(gd) else np.nan
    rows.append({"ba": ba, "region": g["region"].iloc[-1], "first": g["utc"].min(), "last": g["utc"].max(),
                 "hours_span": len(span), "hours_valid": int(valid.sum()),
                 "frac_valid": valid.sum() / len(span), "mean_ci": float(gd.mean()) if len(gd) else np.nan,
                 "std_ci": float(gd.std()) if len(gd) else np.nan, "median_daily_range": daily_range,
                 "mean_gen_mw": float(g["gen_total_mw"].mean()),
                 "share_fossil": float((g["share_coal"] + g["share_natural_gas"] + g["share_oil"]).mean()),
                 "share_solar": float(g["share_solar"].mean()), "share_wind": float(g["share_wind"].mean())})
cov = pd.DataFrame(rows).sort_values("mean_gen_mw", ascending=False)
os.makedirs(os.path.join(ROOT, "tables"), exist_ok=True)
cov.to_csv(os.path.join(ROOT, "tables", f"ba_coverage{TAG}.csv"), index=False)
print("rows", len(df), "BAs", df["ba"].nunique())
print(cov.head(60).to_string(index=False, float_format=lambda x: f"{x:.3g}"))
