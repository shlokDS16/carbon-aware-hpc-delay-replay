"""A26: data ledger for Paper A. Computes every data-section and design number from source files.

Output: tables/ledger_data.csv (key,value,source). No value is typed by hand; each is computed from a file in the project.
Usage: py src/data_ledger.py            (reads parquet columns only; peak memory well under 1.5 GB)
Sources: data/derived/jobs_<trace>.parquet, jobs.parquet (cross-check), ci_clean.parquet, tables/cleaning_counts.csv,
         tables/ba_eligibility.csv, tables/forecast_skill.csv, logs/a26_forecast_leakcheck.txt (output of src/forecast_leakcheck.py),
         data/raw/eia930_emissions/ERCO_co2_hourly.csv, argparse defaults and constants parsed from src/*.py, results/*.json.
"""
import ast
import csv
import json
import os
import re

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
rows = []          # (key, value, source)
notes = []         # cross-check messages printed at the end


def add(key, value, source):
    rows.append((key, repr(float(value)) if isinstance(value, (float, np.floating)) else str(int(value)) if isinstance(value, (int, np.integer)) else str(value), source))


# ------------------------------------------------------------------ jobs
MAX_REQ_H = 72.0   # PREREG s2; cross-checked against simcore/simulate below
sim_src = open(P("src", "simulate.py"), encoding="utf-8").read()
m = re.search(r"^MAX_REQ_H\s*=\s*([0-9.]+)", sim_src, re.M)
if m is None:
    m = re.search(r"MAX_REQ_H\s*=\s*([0-9.]+)", open(P("src", "simcore.py"), encoding="utf-8").read())
assert m and float(m.group(1)) == MAX_REQ_H, "MAX_REQ_H in code differs from PREREG s2 (72 h)"

stats = json.load(open(P("tables", "jobs_trace_stats.json"), encoding="utf-8"))
FILT = "filter: state COMPLETED, r_act >= 1 min, 0 < r_req <= 72 h (PREREG s2, as simulate.py)"
for t in ["PM100", "FDATA", "KIT_FH2"]:
    f = P("data", "derived", f"jobs_{t}.parquet")
    d = pq.read_table(f, columns=["state", "user", "r_act_h", "r_req_h", "energy_kwh"]).to_pandas()
    src_f = f"data/derived/jobs_{t}.parquet"
    add(f"data.{t}.rows_in", len(d), f"{src_f} row count (all states, before the main filter)")
    comp = d[d["state"] == "COMPLETED"]
    add(f"data.{t}.completed_rows", len(comp), f"{src_f} rows with state COMPLETED, before the size filter")
    flt = comp[(comp["r_act_h"] >= 1 / 60) & (comp["r_req_h"] <= MAX_REQ_H) & (comp["r_req_h"] > 0)]
    add(f"data.{t}.users_filtered", flt["user"].nunique(), f"{src_f} distinct user after the main filter ({FILT})")
    add(f"data.{t}.n_filtered_jobs", len(flt), f"{src_f} rows after the main filter")
    mr = float((flt["r_act_h"] / flt["r_req_h"]).median())
    add(f"data.{t}.median_ratio", mr, f"{src_f} median r_act/r_req over the main-filtered jobs ({FILT})")
    mr_c = float((comp["r_act_h"] / comp["r_req_h"]).median())
    add(f"data.{t}.median_ratio_completed_unfiltered", mr_c,
        f"{src_f} median r_act/r_req over all COMPLETED rows (population of tables/jobs_trace_stats.json)")
    js = stats[t]["median_ratio_completed"]
    notes.append(f"{t}: median ratio filtered {mr:.6f}; completed unfiltered {mr_c:.6f}; jobs_trace_stats.json {js:.6f}; "
                 f"rows_in {len(d)} vs json {stats[t]['rows_in']}; completed {len(comp)} vs json {stats[t]['completed_rows']}")
    near = (np.abs(d["r_act_h"] / d["r_req_h"] - 1) <= 0.02)
    if t == "PM100":
        to = d[d["state"] == "TIMEOUT"]
        add("data.PM100.n_timeout", len(to), f"{src_f} rows with state TIMEOUT (all rows)")
        add("data.PM100.timeout_within2pct", float((np.abs(to["r_act_h"] / to["r_req_h"] - 1) <= 0.02).mean()),
            f"{src_f} share of TIMEOUT rows with |r_act/r_req - 1| <= 0.02 (definition of src/prep_jobs.py)")
        e = d["energy_kwh"]
        add("data.PM100.energy_share_gt24h", float(e[d["r_act_h"] > 24].sum() / e.sum()),
            f"{src_f} energy of rows with r_act > 24 h over total energy, all states (definition of src/prep_jobs.py)")
        ef = flt["energy_kwh"]
        add("data.PM100.energy_share_gt24h_filtered", float(ef[flt["r_act_h"] > 24].sum() / ef.sum()),
            f"{src_f} same share over main-filtered jobs (check only)")
        notes.append(f"PM100 timeout {len(to)} vs json {stats[t]['n_timeout']}; within2pct json {stats[t]['timeout_within2pct']:.6f}; "
                     f"energy share json {stats[t]['energy_share_jobs_gt24h']:.6f}")
    if t == "KIT_FH2":
        add("data.KIT_FH2.within2pct_share", float(near.mean()),
            f"{src_f} share of all rows with |r_act/r_req - 1| <= 0.02 (all KIT FH2 rows are COMPLETED)")
        add("data.KIT_FH2.within2pct_share_filtered", float(((np.abs(flt['r_act_h'] / flt['r_req_h'] - 1) <= 0.02)).mean()),
            f"{src_f} same share over main-filtered jobs (check only)")
    del d, comp, flt

# cross-check: combined jobs.parquet row counts and filtered counts per trace
pf = pq.ParquetFile(P("data", "derived", "jobs.parquet"))
jt = pf.read(columns=["trace", "state"]).to_pandas()
for t in ["PM100", "FDATA", "KIT_FH2"]:
    n_all = int((jt["trace"] == t).sum())
    n_c = int(((jt["trace"] == t) & (jt["state"] == "COMPLETED")).sum())
    notes.append(f"jobs.parquet {t}: rows {n_all}, completed {n_c}")
del jt

# ------------------------------------------------------------------ CI cleaning
cc = pd.read_csv(P("tables", "cleaning_counts.csv"))
el = pd.read_csv(P("tables", "ba_eligibility.csv"))
elig = set(el.loc[el["eligible"], "ba"])
add("data.ci.n_candidate_ba", len(el), "tables/ba_eligibility.csv row count (candidate BAs of the final build)")
add("data.ci.n_eligible_ba", len(elig), "tables/ba_eligibility.csv rows with eligible == True (check only)")
c = cc[cc["ba"].isin(elig)]
ci = pd.read_parquet(P("data", "derived", "ci_clean.parquet"), columns=["ba", "utc", "flag", "usable_day"])
assert set(ci["ba"].unique()) == elig, "ci_clean.parquet BAs differ from the eligible set"
n_inv = int(c["n_row_missing"].sum() + c["n_gen_le0"].sum() + c["n_ci_nan_other"].sum())
add("data.ci.n_invalid", n_inv, "tables/cleaning_counts.csv, eligible BAs: n_row_missing + n_gen_le0 + n_ci_nan_other (R2: generation missing or not positive, or CI missing)")
add("data.ci.n_invalid_gen_le0_only", int(c["n_gen_le0"].sum()), "tables/cleaning_counts.csv, eligible BAs: n_gen_le0 only (A25 figure; check only)")
add("data.ci.n_outlier", int(c["n_outlier_total"].sum()), "tables/cleaning_counts.csv, eligible BAs: n_outlier_total (R3)")
fl = ci["flag"].value_counts()
hs_cnt, hw_cnt = int(c["hours_short"].sum()), int(c["hours_week"].sum())
add("data.ci.hours_short", hs_cnt, "tables/cleaning_counts.csv, eligible BAs: hours_short (R4, runs <= 3 h)")
add("data.ci.hours_week", hw_cnt, "tables/cleaning_counts.csv, eligible BAs: hours_week (R4, runs 4 to 168 h)")
assert hs_cnt == int(fl.get(1, 0) + fl.get(2, 0)), "hours_short differs from flag 1 + flag 2 count in ci_clean.parquet"
assert hw_cnt == int(fl.get(3, 0)), "hours_week differs from flag 3 count in ci_clean.parquet"
day = (ci["utc"] - pd.Timedelta(hours=1)).dt.floor("D")
n_unus = int(ci.loc[~ci["usable_day"], ["ba"]].assign(d=day[~ci["usable_day"]]).drop_duplicates().shape[0])
assert n_unus == int(c["unusable_days"].sum()), f"unusable days differ: parquet {n_unus} vs counts {int(c['unusable_days'].sum())}"
add("data.ci.unusable_days", n_unus, "data/derived/ci_clean.parquet distinct (BA, UTC hour-start day) with usable_day False; equals the sum in tables/cleaning_counts.csv (eligible BAs)")
# TEST-year flag shares, percent of eligible-BA hours whose hour start lies in 2025-07-01..2026-06-30
d0 = pd.Timestamp("2025-07-01"); d1 = pd.Timestamp("2026-07-01")
ds_ = (ci["utc"] - pd.Timedelta(hours=1)).dt.tz_localize(None)
tm = (ds_ >= d0) & (ds_ < d1)
nt = int(tm.sum())
for k in (1, 2, 3):
    add(f"data.ci.test_flag{k}_pct", 100.0 * float(((ci["flag"] == k) & tm).sum()) / nt,
        f"data/derived/ci_clean.parquet: percent of the {nt} eligible-BA hours in the TEST year (hour start 2025-07-01 to 2026-06-30) with flag {k}")
add("data.ci.test_flag4_pct", 100.0 * float(((ci["flag"] == 4) & tm).sum()) / nt, "same, flag 4 (check only)")
del ci, day, ds_, tm

# ERCO validation against EIA's published CO2 intensity, final cleaned CI (flag 0 hours: unmodified valid hours)
LB2G = 453.592   # as in src/validate_eia_ci.py
assert "LB2G = 453.592" in open(P("src", "validate_eia_ci.py"), encoding="utf-8").read()
e = pd.read_csv(P("data", "raw", "eia930_emissions", "ERCO_co2_hourly.csv"))
e["utc"] = pd.to_datetime(e["UTC time"], utc=True)
e["eia"] = e["CO2 Emissions Intensity for Generated Electricity"] * LB2G
e = e[["utc", "eia"]].dropna()
x = pd.read_parquet(P("data", "derived", "ci_clean.parquet"), filters=[("ba", "==", "ERCO")], columns=["utc", "ci_clean", "flag"])
x["utc"] = pd.to_datetime(x["utc"], utc=True)
for lab, sub in (("", x[(x["flag"] == 0) & x["ci_clean"].notna()]), ("_allflags", x[x["ci_clean"].notna()])):
    mm = sub.merge(e, on="utc", how="inner")
    r = float(np.corrcoef(mm["ci_clean"], mm["eia"])[0, 1]); b = float((mm["ci_clean"] - mm["eia"]).mean())
    kind = "flag-0 hours (unmodified valid hours)" if lab == "" else "all non-NaN hours incl. repaired (check only)"
    add(f"data.ci.erco_r{lab}", r, f"data/derived/ci_clean.parquet (ERCO, {kind}) vs EIA CO2 intensity x {LB2G} g/lb, n={len(mm)} matched hours; logic of src/validate_eia_ci.py")
    add(f"data.ci.erco_bias{lab}", b, f"same sample, mean of (ci_clean - EIA) in g/kWh")
    if lab == "":
        add("data.ci.erco_n", len(mm), "matched hours of the ERCO validation sample")

# ------------------------------------------------------------------ forecasts
fs = pd.read_csv(P("tables", "forecast_skill.csv"))
w = fs[(fs["period"] == "DEV") & (fs["lead_bucket"] == "1-24")].pivot(index="ba", columns="model", values="MAE")
assert len(w) == len(elig) and set(w.index) == elig, "forecast_skill.csv BAs differ from the eligible set"
add("data.fc.dev_beat_snaive", int((w["lgbm"] < w["snaive_day"]).sum()), "tables/forecast_skill.csv: BAs (DEV, lead bucket 1-24) with lgbm MAE < snaive_day MAE")
add("data.fc.dev_beat_profile7", int((w["lgbm"] < w["profile7"]).sum()), "tables/forecast_skill.csv: BAs (DEV, lead bucket 1-24) with lgbm MAE < profile7 MAE")
add("data.fc.n_ba", len(w), "tables/forecast_skill.csv BAs in the DEV 1-24 h comparison")
lc = P("logs", "a26_forecast_leakcheck.txt")
lt = open(lc, encoding="utf-8").read()
mfp = re.search(r"future-perturbation: (\d+) tests, (\d+) failed", lt)
mfi = re.search(r"flagged-input test: (\d+) flagged hours in (\d+) BAs, (\d+) failures", lt)
assert mfp and mfi, "leak-check output not parseable"
add("data.fc.leak_tests", int(mfp.group(1)), "logs/a26_forecast_leakcheck.txt (output of src/forecast_leakcheck.py, final run): future-perturbation tests")
add("data.fc.leak_failed", int(mfp.group(2)), "logs/a26_forecast_leakcheck.txt: future-perturbation tests failed")
add("data.fc.leak_flag_failed", int(mfi.group(3)), "logs/a26_forecast_leakcheck.txt: flagged-input test failures (check only)")

# ------------------------------------------------------------------ design constants parsed from code
def arg_default(path, flag):
    tree = ast.parse(open(P("src", path), encoding="utf-8").read())
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "add_argument" and n.args and \
                isinstance(n.args[0], ast.Constant) and n.args[0].value == flag:
            for kw in n.keywords:
                if kw.arg == "default":
                    return ast.literal_eval(kw.value)
    raise KeyError((path, flag))


def run_txt(k):
    t = open(P("results", "sim_TEST", "RUN.txt"), encoding="utf-8").read()
    return int(re.search(rf"\b{k}=(\d+)", t).group(1))


aB = arg_default("analyze.py", "--B")
add("design.B", aB, "src/analyze.py --B default (argparse, parsed); results/analysis_TEST_PM100_w.json field B agrees")
jB = json.load(open(P("results", "analysis_TEST_PM100_w.json"), encoding="utf-8"))["B"]
assert jB == aB == arg_default("posthoc_inference.py", "--B")
for k, key, flag in (("reps", "design.reps", "--reps"), ("n_jobs", "design.jobs_per_ba", "--n-jobs"), ("seed", "design.align_seed", "--seed")):
    v = arg_default("simulate.py", flag)
    assert v == run_txt(k), f"simulate.py default {flag} differs from results/sim_TEST/RUN.txt"
    add(key, v, f"src/simulate.py {flag} default (argparse, parsed); equals results/sim_TEST/RUN.txt {k}")
pb = set(int(x) for x in re.findall(r"per_ba_boot\(w, idx, (\d+),", open(P("src", "analyze.py"), encoding="utf-8").read() + open(P("src", "posthoc_inference.py"), encoding="utf-8").read()))
assert len(pb) == 1, pb
add("design.perba_B", pb.pop(), "src/analyze.py and src/posthoc_inference.py: draws argument of A.per_ba_boot (regex on the call)")
sw = set()
for t in ("PM100", "FDATA", "KIT_FH2"):
    j = json.load(open(P("results", f"analysis_TEST_posthoc_{t}.json"), encoding="utf-8"))
    for wt in j["weights"].values():
        for s in wt.values():
            sw.add(s["sync_weeks"])
assert len(sw) == 1, sw
add("design.sync_weeks", sw.pop(), "results/analysis_TEST_posthoc_<trace>.json sync_weeks (identical in all traces, weights and slacks; written by src/posthoc_inference.py)")
q = open(P("src", "run_p4_queue.ps1"), encoding="utf-8").read()
mo = re.search(r"script = 'sens_s1\.py'; extra = @\('--n-outer', '(\d+)'", q)
add("design.s1_outer", int(mo.group(1)) if mo else arg_default("sens_s1.py", "--n-outer"),
    "src/run_p4_queue.ps1 S1 entry '--n-outer' (S1 has not run yet; equals the sens_s1.py --n-outer default)")
assert (int(mo.group(1)) if mo else None) == arg_default("sens_s1.py", "--n-outer")
add("design.s1_inner", arg_default("sens_s1.py", "--B"), "src/sens_s1.py --B default (argparse, parsed); S1 has not run yet")

# ------------------------------------------------------------------ write
os.makedirs(P("tables"), exist_ok=True)
with open(P("tables", "ledger_data.csv"), "w", encoding="utf-8", newline="") as fh:
    wr = csv.writer(fh)
    wr.writerow(["key", "value", "source"])
    wr.writerows(rows)
print(f"{len(rows)} rows written to tables/ledger_data.csv")
for n in notes:
    print("CHECK", n)
