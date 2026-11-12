"""A06: check for a level shift in CI and in generation coverage at the 2024-07-01 EIA-930 schema change.
Window test: mean over the 14 days before vs the 14 days after Jul 1 (hour-start UTC) in 2019..2024, per BA;
the 2024 difference is compared with the mean and sd of the 2019-2023 differences.
Coverage test: sum of the mapped fuel columns / reported Net Generation (Adjusted), same windows.
Outputs tables/schema_break_windows[_v0].csv"""
import os, sys
import numpy as np, pandas as pd, pyarrow.dataset as ds
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG = "" if "--final" in sys.argv else "_v0"
el = pd.read_csv(os.path.join(ROOT, "tables", f"ba_eligibility{TAG}.csv"))
bas = el.loc[el["eligible"], "ba"].tolist()
d = ds.dataset(os.path.join(ROOT, "data", "derived", f"ci_hourly{TAG}.parquet")).to_table(
    columns=["ba", "utc", "ci", "gen_total_mw"], filter=ds.field("ba").isin(bas)).to_pandas()
d["utc"] = pd.to_datetime(d["utc"], utc=True) - pd.Timedelta(hours=1)
# coverage: raw net generation (adjusted)
parts = []
for f in ["2023_Jan_Jun", "2023_Jul_Dec", "2024_Jan_Jun", "2024_Jul_Dec", "2022_Jan_Jun", "2022_Jul_Dec"]:
    r = pd.read_csv(os.path.join(ROOT, "data", "raw", "eia930", f"EIA930_BALANCE_{f}.csv"),
                    usecols=["Balancing Authority", "UTC Time at End of Hour", "Net Generation (MW) (Adjusted)"],
                    thousands=",")
    r["utc"] = pd.to_datetime(r["UTC Time at End of Hour"], format="%m/%d/%Y %I:%M:%S %p", utc=True) - pd.Timedelta(hours=1)
    parts.append(r.rename(columns={"Balancing Authority": "ba", "Net Generation (MW) (Adjusted)": "net_gen"})[["ba", "utc", "net_gen"]])
r = pd.concat(parts)
d = d.merge(r, on=["ba", "utc"], how="left")
rows = []
for ba, g in d.groupby("ba"):
    g = g.set_index("utc").sort_index()
    row = {"ba": ba}
    for y in range(2019, 2025):
        a = g.loc[f"{y}-06-17":f"{y}-06-30"]; b = g.loc[f"{y}-07-01":f"{y}-07-14"]
        row[f"dci_{y}"] = b["ci"].mean() - a["ci"].mean()
        if y >= 2022:
            ca = (a["gen_total_mw"].sum() / a["net_gen"].sum()) if a["net_gen"].sum() > 0 else np.nan
            cb = (b["gen_total_mw"].sum() / b["net_gen"].sum()) if b["net_gen"].sum() > 0 else np.nan
            row[f"cov_before_{y}"], row[f"cov_after_{y}"] = ca, cb
    prev = np.array([row[f"dci_{y}"] for y in range(2019, 2024)])
    row["dci_prev_mean"], row["dci_prev_sd"] = np.nanmean(prev), np.nanstd(prev, ddof=1)
    row["excess_2024"] = row["dci_2024"] - row["dci_prev_mean"]
    row["z_2024"] = row["excess_2024"] / row["dci_prev_sd"] if row["dci_prev_sd"] > 0 else np.nan
    row["flag_jump"] = bool(abs(row["z_2024"]) > 3 and abs(row["excess_2024"]) > 15)
    row["cov_shift_2024"] = row["cov_after_2024"] - row["cov_before_2024"]
    row["cov_shift_2023"] = row["cov_after_2023"] - row["cov_before_2023"]
    rows.append(row)
out = pd.DataFrame(rows)
out.to_csv(os.path.join(ROOT, "tables", f"schema_break_windows{TAG}.csv"), index=False)
pd.set_option("display.width", 250)
print(out[["ba", "dci_2023", "dci_2024", "dci_prev_mean", "dci_prev_sd", "excess_2024", "z_2024", "flag_jump",
           "cov_before_2024", "cov_after_2024", "cov_shift_2023", "cov_shift_2024"]].round(3).to_string())
print("flagged", int(out["flag_jump"].sum()), "of", len(out))
