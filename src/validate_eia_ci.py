"""A06: compare our CI with EIA's published CO2 intensity of generated electricity (per-BA Excel file)."""
import os, sys
import numpy as np, pandas as pd, pyarrow.dataset as ds
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ba = sys.argv[1] if len(sys.argv) > 1 else "ERCO"
LB2G = 453.592
e = pd.read_csv(os.path.join(ROOT, "data", "raw", "eia930_emissions", f"{ba}_co2_hourly.csv"))
e["utc"] = pd.to_datetime(e["UTC time"], utc=True)
e["eia"] = e["CO2 Emissions Intensity for Generated Electricity"] * LB2G
e = e[["utc", "eia"]].dropna()
d = ds.dataset(os.path.join(ROOT, "data", "derived", "ci_hourly_v0.parquet")).to_table(
    filter=ds.field("ba") == ba).to_pandas()
d["utc"] = pd.to_datetime(d["utc"], utc=True)
# direct-emission version of our CI (IPCC AR5 direct medians for coal/gas, EIA US 2023 petroleum, 0 for the rest, unknown 575)
dirf = {"coal": 760, "natural_gas": 370, "nuclear": 0, "oil": 1116, "hydro": 0, "solar": 0, "wind": 0, "other": 0, "unknown": 575}
d["ci_direct"] = sum(d["share_" + k].fillna(0) * v for k, v in dirf.items())
dirf_eia = {"coal": 1048, "natural_gas": 435, "oil": 1116}  # EIA FAQ 74 (2023 US average), other fuels 0
d["ci_direct_eia"] = sum(d["share_" + k].fillna(0) * v for k, v in dirf_eia.items())
m = d.merge(e, on="utc", how="inner")
m = m[(m["ci"].notna()) & (m["gen_total_mw"] > 0)]
rows = []
def stat(x, label):
    r = {"ba": ba, "subset": label, "n": len(x)}
    for c in ["ci", "ci_direct", "ci_direct_eia"]:
        r[f"r_hourly_{c}"] = float(np.corrcoef(x[c], x["eia"])[0, 1])
        r[f"bias_{c}"] = float((x[c] - x["eia"]).mean())
        r[f"mae_{c}"] = float((x[c] - x["eia"]).abs().mean())
    dd = x.set_index("utc")[["ci", "ci_direct", "ci_direct_eia", "eia"]].resample("D").mean().dropna()
    for c in ["ci", "ci_direct", "ci_direct_eia"]:
        r[f"r_daily_{c}"] = float(np.corrcoef(dd[c], dd["eia"])[0, 1])
    r["eia_mean"] = float(x["eia"].mean())
    return r
rows.append(stat(m, "all 2018-07..2026-06"))
yr = m["utc"].dt.tz_convert(None)
for lab, a, b in [("TRAIN", "2018-07-01", "2024-06-30"), ("DEV", "2024-07-01", "2025-06-30"), ("TEST", "2025-07-01", "2026-06-30")]:
    s = m[(yr >= a) & (yr < pd.Timestamp(b) + pd.Timedelta(days=1))]
    if len(s): rows.append(stat(s, lab))
out = pd.DataFrame(rows)
out.to_csv(os.path.join(ROOT, "tables", f"eia_co2_validation_{ba}_v0.csv"), index=False)
pd.set_option("display.width", 250)
print(out.round(3).T.to_string())
