"""Post-hoc impact items B1-B4 (research/P4_PLAN_X9.md, section B, binding; deviations row 7).

Reads only saved TEST results (results/sim_TEST/<trace>/*.npz, tables/ledger_TEST_posthoc.csv) and the TRAIN part of
data/derived/ci_clean.parquet (B2 quartile).  Imports the frozen src/analyze.py and the helpers of src/posthoc_inference.py;
changes no frozen file.  Everything is POST-HOC and descriptive: no hypothesis test.

B1  scale table: g CO2e per kWh and t CO2e per MW-year (= g/kWh x 8.76, one MW drawn all year) for D = lgbm|req, lgbm|pred,
    oracle|act, S = 12 and 24 h, all traces, energy-weighted.  From the PH4 rows of ledger_TEST_posthoc.csv.
B2  top-quartile BAs by TRAIN median daily intensity range (same day rule as secondary.test_character: flag <= 3, at least 20
    hours per UTC day; TRAIN = 2018-07-01 .. 2024-06-30; the top ceil(n/4) BAs by that statistic, ties impossible in practice).
    Pooled saving of D and of lgbm|pred and their share of the oracle|act saving, top group vs the rest, S = 12 h, weights w
    and u, frozen calendar bootstrap (analyze.bootstrap, mode fixed, seed 7 + S, B = 2000) restricted to each group.  The two
    groups are resampled independently (fixed BA set, weeks resampled within each BA), so a group difference is formed from the
    two draw vectors paired by draw index.
B3  H2 (runtime penalty, lgbm|act minus lgbm|req) and H3 (lgbm|pred minus lgbm|req) as absolute differences in g CO2e per job
    and per kWh, S = 12 and 24 h, energy-weighted, frozen bootstrap draws (posthoc_inference.boot_raw, seed 7 + S).
B4  share of BA-weeks with a positive D saving (BA-week = one calendar week of one BA, replicates pooled; weeks with zero run-now
    energy skipped), S = 12 and 24 h, both weights; also the median over BAs of the per-BA share.  The saved daily per-BA arrays
    support it, so it is run.
Usage: py src/posthoc_impact.py [--traces PM100,FDATA,KIT_FH2] [--B 2000]
Writes tables/ledger_TEST_posthoc_impact.csv (keys posthoc.B<n>.<trace>.<weight>.S<S>.<name>) and
results/analysis_TEST_posthoc_impact.json.  One trace at a time in memory.
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze as A  # noqa: E402  (frozen)
import posthoc_inference as P  # noqa: E402  (post-hoc helpers: load_ext, boot_raw, ci, rss_mb)

ROOT = A.ROOT
TRACES = ("PM100", "FDATA", "KIT_FH2")
F = "lgbm"
T_PER_MW_YEAR = 8.76          # g/kWh x 8760 h x 1000 kW = g/kWh x 8.76e6 g = 8.76 t per MW-year
TRAIN = ("2018-07-01", "2024-07-01")


def train_range_table():
    """Median daily (max - min) of ci_clean per BA on TRAIN, same rule as secondary.test_character."""
    cc = pd.read_parquet(os.path.join(ROOT, "data", "derived", "ci_clean.parquet"), columns=["ba", "utc", "ci_clean", "flag"])
    lo, hi = (pd.Timestamp(x, tz="UTC") for x in TRAIN)
    cc = cc[(cc.utc >= lo) & (cc.utc < hi) & (cc.flag <= 3)].dropna(subset=["ci_clean"])
    out = {}
    for b, g in cc.groupby("ba"):
        d = g.groupby(g.utc.dt.floor("D")).ci_clean.agg(["max", "min", "count"])
        d = d[d["count"] >= 20]
        out[b] = float((d["max"] - d["min"]).median())
    return pd.Series(out, name="train_median_daily_range").sort_index()


# ---------------------------------------------------------------------------------------------------------------- B1
def b1_rows(ledger):
    rows = []
    names = {"D": "lgbm|req", "lgbm|pred": "lgbm|pred", "oracle|act": "oracle|act"}
    for trace in TRACES:
        for S in (12, 24):
            for nm, arm in names.items():
                for q in ("est", "lo", "hi"):
                    key = f"posthoc.PH4.{trace}.w.S{S}.{arm}.g_per_kwh.{q}"
                    v = float(ledger[key])
                    pre = f"posthoc.B1.{trace}.w.S{S}.{nm}"
                    rows += [(f"{pre}.g_per_kwh.{q}", v, f"ledger_TEST_posthoc.csv:{key}"),
                             (f"{pre}.t_per_MW_year.{q}", v * T_PER_MW_YEAR, f"ledger_TEST_posthoc.csv:{key} x 8.76")]
            k0 = f"posthoc.PH4.{trace}.w.S{S}.runnow_g_per_kwh.est"
            rows.append((f"posthoc.B1.{trace}.w.S{S}.runnow_mean_intensity_g_per_kwh", float(ledger[k0]), f"ledger_TEST_posthoc.csv:{k0}"))
    return rows


# ---------------------------------------------------------------------------------------------------------------- B2
def b2_trace(trace, weights, B, rng_tab, top_bas):
    rows, info = [], {}
    S = 12
    for weight in weights:
        arms, data = A.load("TEST", "", trace, weight)
        idx = {a: i for i, a in enumerate(arms)}
        bas = sorted(data)
        top = [b for b in bas if b in top_bas]
        rest = [b for b in bas if b not in top_bas]
        res = {}
        for gname, grp in (("top", top), ("rest", rest)):
            sub = {b: {S: data[b][S]} for b in grp}
            _, point, boot, _, _ = A.bootstrap(arms, sub, S, B, 7 + S, "fixed")
            res[gname] = (point, boot)
        pre = f"posthoc.B2.{trace}.{weight}.S{S}"
        meas = {"saving_D": lambda v: v[..., idx[f"{F}|req"]], "saving_pred": lambda v: v[..., idx[f"{F}|pred"]],
                "saving_oracle_act": lambda v: v[..., idx["oracle|act"]],
                "share_D": lambda v: v[..., idx[f"{F}|req"]] / v[..., idx["oracle|act"]],
                "share_pred": lambda v: v[..., idx[f"{F}|pred"]] / v[..., idx["oracle|act"]]}
        for gname in ("top", "rest"):
            point, boot = res[gname]
            rows.append((f"{pre}.{gname}.n_ba", len(top) if gname == "top" else len(rest), "TRAIN quartile"))
            for m, fn in meas.items():
                lo, hi = P.ci(fn(boot))
                rows += [(f"{pre}.{gname}.{m}.est", float(fn(point)), "frozen bootstrap restricted"),
                         (f"{pre}.{gname}.{m}.lo", lo, "frozen bootstrap restricted"),
                         (f"{pre}.{gname}.{m}.hi", hi, "frozen bootstrap restricted")]
        for m, fn in meas.items():
            d_est = float(fn(res["top"][0]) - fn(res["rest"][0]))
            d_b = fn(res["top"][1]) - fn(res["rest"][1])
            lo, hi = P.ci(d_b)
            rows += [(f"{pre}.diff_top_minus_rest.{m}.est", d_est, "independent group draws, paired by index"),
                     (f"{pre}.diff_top_minus_rest.{m}.lo", lo, "independent group draws, paired by index"),
                     (f"{pre}.diff_top_minus_rest.{m}.hi", hi, "independent group draws, paired by index")]
        info[weight] = {"top": top, "rest": rest}
        del data
    return rows, info


# ---------------------------------------------------------------------------------------------------------------- B3 + B4
def b3_b4_trace(trace, B):
    rows = []
    for weight in ("w", "u"):
        arms, data = P.load_ext(trace, weight)
        bas = sorted(data)
        na = len(arms)
        idx = {a: i for i, a in enumerate(arms)}
        rn, fr, fa, fp = idx["runnow"], idx[f"{F}|req"], idx[f"{F}|act"], idx[f"{F}|pred"]
        for S in (12, 24):
            pre = f"posthoc.B{{}}.{trace}.{weight}.S{S}"
            W = [A.weekly(data[b][S][1]) for b in bas]           # [arms + energy + n, weeks], remainder
            if weight == "w":                                    # B3: grams need the energy-weighted rows
                raw = P.boot_raw(W, B, 7 + S)
                tot = sum(w_.sum(axis=1) + r_ for w_, r_ in W)
                en, nn = tot[na], tot[na + 1]
                Eb, enb, nnb = raw[:, :na], raw[:, na], raw[:, na + 1]
                for name, alt in (("H2", fa), ("H3", fp)):
                    # saving(alt) - saving(req) in grams = (E[req] - E[alt]) / denominator
                    for unit, den, denb in (("g_per_job", nn, nnb), ("g_per_kwh", en, enb)):
                        est = (tot[fr] - tot[alt]) / den
                        draws = (Eb[:, fr] - Eb[:, alt]) / denb
                        lo, hi = P.ci(draws)
                        rows += [(f"{pre.format(3)}.{name}.{unit}.est", float(est), "frozen bootstrap draws"),
                                 (f"{pre.format(3)}.{name}.{unit}.lo", lo, "frozen bootstrap draws"),
                                 (f"{pre.format(3)}.{name}.{unit}.hi", hi, "frozen bootstrap draws")]
                rows += [(f"{pre.format(3)}.total_energy_kwh", float(en), "saved arrays"), (f"{pre.format(3)}.n_jobs", float(nn), "saved arrays")]
                del raw
            # B4: share of BA-weeks with positive D saving
            pos, tot_w, per_ba = 0, 0, []
            for (w_, _) in W:
                ok = w_[rn] > 0
                s = 1.0 - w_[fr][ok] / w_[rn][ok]
                pos += int((s > 0).sum())
                tot_w += int(ok.sum())
                per_ba.append(float((s > 0).mean()) if ok.any() else float("nan"))
            rows += [(f"{pre.format(4)}.D_positive_share_ba_weeks", pos / tot_w, "saved per-BA weekly arrays"),
                     (f"{pre.format(4)}.n_ba_weeks", float(tot_w), "saved per-BA weekly arrays"),
                     (f"{pre.format(4)}.D_positive_share_median_over_ba", float(np.nanmedian(per_ba)), "saved per-BA weekly arrays"),
                     (f"{pre.format(4)}.D_positive_share_min_over_ba", float(np.nanmin(per_ba)), "saved per-BA weekly arrays")]
        del data
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--traces", default=",".join(TRACES))
    ap.add_argument("--B", type=int, default=2000)
    args = ap.parse_args()
    t0 = time.time()
    led = pd.read_csv(os.path.join(ROOT, "tables", "ledger_TEST_posthoc.csv")).set_index("key")["value"]
    rng_tab = train_range_table()
    elig = pd.read_csv(os.path.join(ROOT, "tables", "ba_eligibility.csv"))
    elig = sorted(elig[elig["eligible"]]["ba"])
    rng_tab = rng_tab.loc[elig]
    n_top = math.ceil(len(rng_tab) / 4)
    top_bas = set(rng_tab.sort_values(ascending=False).index[:n_top])
    print(f"TRAIN range table: {len(rng_tab)} BAs; top quartile n = {n_top}; threshold {rng_tab[list(top_bas)].min():.1f} g/kWh", flush=True)
    rows = [("posthoc.B2.train_quartile.n_top", float(n_top), "TRAIN ci_clean"),
            ("posthoc.B2.train_quartile.min_range_in_top", float(rng_tab[list(top_bas)].min()), "TRAIN ci_clean"),
            ("posthoc.B2.train_quartile.median_range_all", float(rng_tab.median()), "TRAIN ci_clean")]
    rows += b1_rows(led)
    info = {"top_bas": sorted(top_bas), "train_range": rng_tab.to_dict(), "traces": {}}
    for trace in args.traces.split(","):
        r2, inf = b2_trace(trace, ("w", "u"), args.B, rng_tab, top_bas)
        r34 = b3_b4_trace(trace, args.B)
        rows += r2 + r34
        info["traces"][trace] = inf
        print(f"{trace} done; RSS peak {P.rss_mb():.0f} MB; {time.time() - t0:.0f} s", flush=True)
    fn = os.path.join(ROOT, "tables", "ledger_TEST_posthoc_impact.csv")
    new = pd.DataFrame(rows, columns=["key", "value", "source"])
    if os.path.exists(fn) and args.traces != ",".join(TRACES):           # partial rerun: keep rows of other traces
        old = pd.read_csv(fn)
        keep = ~old["key"].apply(lambda k: any(f".{t}." in k for t in args.traces.split(",")))
        new = pd.concat([old[keep], new], ignore_index=True).drop_duplicates("key", keep="last")
    new.to_csv(fn, index=False)
    info["peak_rss_mb"] = P.rss_mb()
    with open(os.path.join(ROOT, "results", "analysis_TEST_posthoc_impact.json"), "w", encoding="utf-8") as fh:
        json.dump(info, fh, indent=1)
    print(f"ledger {fn}: {len(new)} rows; peak RSS {info['peak_rss_mb']:.0f} MB; {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
