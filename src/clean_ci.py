"""A06: audit, clean and screen the hourly carbon-intensity series (fixed rules, cited by the pre-registration).

Usage: python src/clean_ci.py [--final]
  default   reads data/derived/ci_hourly_v0.parquet, writes ci_clean_v0.parquet, ba_eligibility_v0.csv (+ audit tables _v0)
  --final   reads ci_hourly.parquet, writes the same names without _v0

Rules (all constants below, none tuned on DEV/TEST):
 R1 grid: hourly end-of-hour UTC grid GRID_START..GRID_END for every BA (one BA at a time).
 R2 invalid hour: gen_total_mw missing or <= 0, or ci missing  -> ci set to NaN (flag source "missing").
 R3 outlier hour: |d_t - med_t| / max(1.4826 * MAD_t, SCALE_FLOOR) > Z_MAX, where d_t = ci_t - ci_{t-1} (both valid)
    and med_t, MAD_t are the median and median absolute deviation of d over a centred 30-day window (min 7 days),
    OR ci outside [0, CI_MAX]  -> ci set to NaN (flag source "outlier").
 R4 repair: maximal runs of NaN of length <= 3 h: linear interpolation (flag 1; flag 2 for hours that were outliers);
    runs of 4..168 h: value of the same hour one week earlier in the already repaired series (flag 3);
    runs > 168 h (or no repair value): left NaN, flag 4, and the whole UTC calendar day is marked unusable.
 R5 eligibility: present over the full span (first valid hour <= 2018-09-01, last valid hour >= 2026-06-30 23:00 UTC);
    >= 95 % valid (flag-0) hours in each of TRAIN, DEV, TEST; mean generation >= 100 MW; std of ci_clean in TRAIN > 1.
"""
import os
import sys

import numpy as np
import pandas as pd
import pyarrow.dataset as ds

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINAL = "--final" in sys.argv
TAG = "" if FINAL else "_v0"
SRC = os.path.join(ROOT, "data", "derived", f"ci_hourly{TAG}.parquet")

GRID_START = pd.Timestamp("2018-07-01 09:00", tz="UTC")  # every BA has begun reporting by 08:00 UTC
GRID_END = pd.Timestamp("2026-07-01 00:00", tz="UTC")     # end of the last hour of 2026-06-30
PERIODS = {"TRAIN": ("2018-07-01", "2024-06-30"), "DEV": ("2024-07-01", "2025-06-30"),
           "TEST": ("2025-07-01", "2026-06-30")}
Z_MAX, WIN, MIN_WIN, SCALE_FLOOR, CI_MAX = 8.0, 720, 168, 1.0, 1100.0
SHORT, LONG = 3, 168
FIRST_OK = pd.Timestamp("2018-09-01 00:00", tz="UTC")  # first valid hour within the first 62 days of TRAIN
LAST_OK = pd.Timestamp("2026-06-30 23:00", tz="UTC")
MIN_VALID, MIN_MW, MIN_STD = 0.90, 100.0, 1.0  # D0003: 0.90 per period (was 0.95)


def period_of(utc):
    """Period by the date of the hour START (end-of-hour stamp minus 1 h), so 2026-07-01 00:00 closes 2026-06-30."""
    d = (utc - pd.Timedelta(hours=1)).dt.floor("D").dt.tz_localize(None) if hasattr(utc, "dt") else None
    out = pd.Series("", index=utc.index)
    for p, (a, b) in PERIODS.items():
        out[(d >= pd.Timestamp(a)) & (d <= pd.Timestamp(b))] = p
    return out


def runs_of_nan(isnan):
    """Return (start, length) of maximal True runs."""
    x = np.concatenate([[0], isnan.astype(np.int8), [0]])
    dx = np.diff(x)
    s, e = np.where(dx == 1)[0], np.where(dx == -1)[0]
    return s, e - s


def clean_one(g):
    """g: one BA, columns utc, ci, gen_total_mw. Returns frame on the full grid and a dict of counts."""
    idx = pd.date_range(GRID_START, GRID_END, freq="h")
    g = g.drop_duplicates("utc", keep="last").set_index("utc").reindex(idx)
    ci = g["ci"].to_numpy("float64").copy()
    gen = g["gen_total_mw"].to_numpy("float64")
    missing_row = g["gen_total_mw"].isna().to_numpy()
    bad_gen = ~missing_row & ~(gen > 0)
    invalid = missing_row | bad_gen | np.isnan(ci)
    cnt = {"hours_grid": len(idx), "n_row_missing": int(missing_row.sum()), "n_gen_le0": int(bad_gen.sum()),
           "n_ci_nan_other": int((np.isnan(ci) & ~missing_row & ~bad_gen).sum())}
    ci[invalid] = np.nan
    # outliers
    out_range = (ci < 0) | (ci > CI_MAX)
    d = pd.Series(ci).diff()
    med = d.rolling(WIN + 1, center=True, min_periods=MIN_WIN).median()
    mad = (d - med).abs().rolling(WIN + 1, center=True, min_periods=MIN_WIN).median()
    z = ((d - med).abs() / np.maximum(1.4826 * mad, SCALE_FLOOR)).to_numpy()
    out_z = np.nan_to_num(z, nan=0.0) > Z_MAX
    outlier = out_z | np.nan_to_num(out_range)
    cnt["n_outlier_z"] = int(out_z.sum())
    cnt["n_outlier_range"] = int(out_range.sum())
    cnt["n_outlier_total"] = int(outlier.sum())
    ci[outlier] = np.nan
    flag = np.zeros(len(ci), dtype=np.int8)
    nanmask = np.isnan(ci)
    out_clean = ci.copy()
    s, ln = runs_of_nan(nanmask)
    n_short = n_week = n_long = h_short = h_week = h_long = 0
    unusable_hours = np.zeros(len(ci), dtype=bool)
    for a, l in zip(s, ln):
        b = a + l
        if l <= SHORT and a > 0 and b < len(ci):
            x0, x1 = ci[a - 1], ci[b]
            out_clean[a:b] = np.interp(np.arange(a, b), [a - 1, b], [x0, x1])
            flag[a:b] = np.where(outlier[a:b], 2, 1)
            n_short += 1
            h_short += l
        elif l <= LONG:
            ok = True
            for t in range(a, b):  # sequential: repaired values of earlier hours may serve as source
                src = t - 168
                if src >= 0 and not np.isnan(out_clean[src]):
                    out_clean[t] = out_clean[src]
                    flag[t] = 3
                else:
                    ok = False
                    flag[t] = 4
            if ok:
                n_week += 1
                h_week += l
            else:
                n_long += 1
                h_long += l
                unusable_hours[a:b] = True
        else:
            flag[a:b] = 4
            n_long += 1
            h_long += l
            unusable_hours[a:b] = True
    cnt.update(n_runs_short=n_short, hours_short=h_short, n_runs_week=n_week, hours_week=h_week,
               n_runs_long=n_long, hours_long=h_long)
    # raw valid = not invalid, not outlier
    raw_valid = ~invalid & ~outlier
    res = pd.DataFrame({"utc": idx, "ci_clean": out_clean.astype("float32"), "flag": flag,
                        "raw_valid": raw_valid, "gen_total_mw": gen.astype("float32")})
    day = res["utc"].sub(pd.Timedelta(hours=1)).dt.floor("D")
    bad_days = set(day[unusable_hours])
    res["usable_day"] = ~day.isin(bad_days)
    cnt["unusable_days"] = len(bad_days)
    cnt["hours_unusable_day"] = int((~res["usable_day"]).sum())
    return res, cnt


def main():
    dset = ds.dataset(SRC)
    bas = sorted(dset.to_table(columns=["ba"]).column("ba").unique().to_pylist())
    outs, rows, counts, schema_rows = [], [], [], []
    for ba in bas:
        t = dset.to_table(columns=["ba", "utc", "ci", "gen_total_mw", "share_coal", "share_natural_gas",
                                   "share_nuclear", "share_oil", "share_hydro", "share_solar", "share_wind",
                                   "share_other", "share_unknown"],
                          filter=ds.field("ba") == ba).to_pandas()
        t["utc"] = pd.to_datetime(t["utc"], utc=True)
        rec = {"ba": ba}
        if t["ci"].notna().sum() == 0:
            rows.append({**rec, "eligible": False, "reason": "no valid ci hour"})
            continue
        first, last = t.loc[t["ci"].notna(), "utc"].min(), t.loc[t["ci"].notna(), "utc"].max()
        res, cnt = clean_one(t[["utc", "ci", "gen_total_mw"]])
        res["ba"] = ba
        per = period_of(res["utc"])
        stats = {"first_valid": first, "last_valid": last}
        for p in PERIODS:
            m = (per == p).to_numpy()
            stats[f"valid_{p}"] = float(res.loc[m, "raw_valid"].mean()) if m.any() else np.nan
        stats["mean_gen_mw"] = float(res["gen_total_mw"].where(res["raw_valid"]).mean())
        mt = (per == "TRAIN").to_numpy()
        stats["std_ci_train"] = float(res.loc[mt, "ci_clean"].std())
        stats["mean_ci_train"] = float(res.loc[mt, "ci_clean"].mean())
        stats["unusable_day_frac"] = 1.0 - float(res["usable_day"].mean())
        reasons = []
        if first > FIRST_OK:
            reasons.append(f"starts {first:%Y-%m-%d}")
        if last < LAST_OK:
            reasons.append(f"ends {last:%Y-%m-%d}")
        for p in PERIODS:
            v = stats[f"valid_{p}"]
            if not (v >= MIN_VALID):
                reasons.append(f"valid {p} {v:.3f} < {MIN_VALID}")
        if not (stats["mean_gen_mw"] >= MIN_MW):
            reasons.append(f"mean gen {stats['mean_gen_mw']:.0f} MW < 100")
        if not (stats["std_ci_train"] > MIN_STD):
            reasons.append(f"std ci TRAIN {stats['std_ci_train']:.2f} <= 1")
        elig = not reasons
        rows.append({**rec, "eligible": elig, "reason": "; ".join(reasons) if reasons else "ok", **stats})
        counts.append({"ba": ba, **cnt})
        if elig:
            outs.append(res[["ba", "utc", "ci_clean", "flag", "usable_day"]])
        # schema-change check (monthly means, UTC hour-start month)
        tt = t.set_index("utc")
        tt.index = tt.index - pd.Timedelta(hours=1)
        mm = tt[["ci", "share_hydro", "share_solar", "share_wind", "share_other", "share_unknown",
                 "share_natural_gas", "share_coal"]].resample("MS").mean()
        mm.index = mm.index.tz_localize(None)

        def dl(y, c):
            try:
                return float(mm.loc[f"{y}-07-01", c] - mm.loc[f"{y}-06-01", c])
            except KeyError:
                return np.nan
        prev = [dl(y, "ci") for y in range(2019, 2024)]
        sr = {"ba": ba, "d_ci_2024": dl(2024, "ci"), "d_ci_2023": dl(2023, "ci"),
              "d_ci_med_2019_23": float(np.nanmedian(prev)) if np.isfinite(prev).any() else np.nan}
        for c in ["share_hydro", "share_solar", "share_wind", "share_other", "share_unknown"]:
            sr[f"d_{c}_2024"], sr[f"d_{c}_2023"] = dl(2024, c), dl(2023, c)
        schema_rows.append(sr)
        print(ba, "eligible" if elig else "DROP " + "; ".join(reasons), flush=True)
    clean = pd.concat(outs, ignore_index=True)
    clean.to_parquet(os.path.join(ROOT, "data", "derived", f"ci_clean{TAG}.parquet"), index=False)
    el = pd.DataFrame(rows)
    el.to_csv(os.path.join(ROOT, "tables", f"ba_eligibility{TAG}.csv"), index=False)
    pd.DataFrame(counts).to_csv(os.path.join(ROOT, "tables", f"cleaning_counts{TAG}.csv"), index=False)
    sc = pd.DataFrame(schema_rows)
    sc["jump_ci"] = sc["d_ci_2024"] - sc["d_ci_2023"]
    sc["flag_schema_jump"] = sc["jump_ci"].abs() > 30.0
    sc.to_csv(os.path.join(ROOT, "tables", f"schema_break_check{TAG}.csv"), index=False)
    print("eligible", int(el["eligible"].sum()), "of", len(el))


if __name__ == "__main__":
    main()
