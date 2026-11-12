"""Replay of carbon-aware delay scheduling for every eligible BA (see research/PIPELINE_SPEC.md).

Usage:
  python src/simulate.py --period DEV  [--tag _v0] [--fc-dir data/derived/forecasts_v0] [--reps 3] [--n-jobs 20000]
  python src/simulate.py --period TEST ...   (refused unless research/PREREG.md matches research/PREREG.md5)
Output: results/sim_<period><tag>/<trace>/<BA>.npz with per-day sums for every arm, slack, replicate and length class.
"""
import argparse
import hashlib
import os
import sys
import time
import zlib

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import simcore as sc  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERIODS = {"DEV": ("2024-07-01", "2025-07-01"), "TEST": ("2025-07-01", "2026-07-01")}
TRAIN = ("2018-07-01", "2024-07-01")
SLACKS = (2.0, 6.0, 12.0, 24.0)
FC_MODELS = ("persistence", "snaive_day", "snaive_week", "profile7", "lgbm")
SIGNALS = ("oracle",) + FC_MODELS + ("histprofile",)
RUNTIMES = ("act", "req", "pred", "pred2")   # pred2 = min(req, 2 x pred), secondary
ARMS = ["runnow", "night"] + [f"{s}|{r}" for s in SIGNALS for r in RUNTIMES]
LEN_EDGES = np.array([0.0, 1.0, 4.0, 12.0, np.inf])      # length classes on actual runtime (h)
MAX_REQ_H = 72.0
MARGIN_H = 100.0


def check_prereg():
    p = os.path.join(ROOT, "research", "PREREG.md")
    m = os.path.join(ROOT, "research", "PREREG.md5")
    if not (os.path.exists(p) and os.path.exists(m)):
        sys.exit("TEST refused: PREREG.md and PREREG.md5 must exist (freeze first)")
    want = open(m, encoding="utf-8").read().split()[0]
    got = hashlib.md5(open(p, "rb").read()).hexdigest()
    if want != got:
        sys.exit("TEST refused: PREREG.md changed after freeze")


def ba_offsets():
    """Standard-time UTC offset (hours) per BA, from EIA's local and UTC columns in a January file."""
    out = os.path.join(ROOT, "tables", "ba_utc_offset.csv")
    if os.path.exists(out):
        return pd.read_csv(out).set_index("ba")["offset_h"].to_dict()
    f = os.path.join(ROOT, "data", "raw", "eia930", "EIA930_BALANCE_2025_Jan_Jun.csv")
    d = pd.read_csv(f, usecols=["Balancing Authority", "Local Time at End of Hour", "UTC Time at End of Hour"],
                    nrows=None)
    d = d.iloc[::24]
    loc = pd.to_datetime(d["Local Time at End of Hour"], format="%m/%d/%Y %I:%M:%S %p")
    utc = pd.to_datetime(d["UTC Time at End of Hour"], format="%m/%d/%Y %I:%M:%S %p")
    d = d.assign(off=((loc - utc).dt.total_seconds() / 3600).round())
    jan = d[utc.dt.month == 1]
    res = jan.groupby("Balancing Authority")["off"].agg(lambda x: x.mode().iloc[0]).rename("offset_h")
    res.index.name = "ba"
    res.reset_index().to_csv(out, index=False)
    return res.to_dict()


def load_ba(ba, tag):
    d = pd.read_parquet(os.path.join(ROOT, "data", "derived", f"ci_clean{tag}.parquet"),
                        filters=[("ba", "==", ba)], columns=["utc", "ci_clean", "usable_day"])
    d = d.sort_values("utc").reset_index(drop=True)
    # interval k covers [utc_k - 1h, utc_k); origin = start of the first interval
    origin = d["utc"].iloc[0] - pd.Timedelta(hours=1)
    ci = d["ci_clean"].to_numpy(dtype="float64")
    usable = d["usable_day"].to_numpy(dtype=bool) & np.isfinite(ci)
    # NaN (long gaps) only on unusable hours; jobs whose 96 h window touches one are excluded in place_jobs,
    # so the fill below is never read by a scored job (it only keeps the arithmetic finite)
    ci = pd.Series(ci).ffill().bfill().to_numpy()
    return origin, ci, usable, d["utc"]


def hist_profile(ci, utc, offset):
    """TRAIN mean CI by (month, local hour); returned as a function of interval indices."""
    loc = utc + pd.Timedelta(hours=offset) - pd.Timedelta(hours=1)   # local start of interval
    tr = (utc >= pd.Timestamp(TRAIN[0], tz="UTC")) & (utc < pd.Timestamp(TRAIN[1], tz="UTC"))
    tab = pd.DataFrame({"m": loc.dt.month, "h": loc.dt.hour, "ci": ci})[tr.to_numpy()].groupby(["m", "h"])["ci"].mean()
    prof = tab.reindex(pd.MultiIndex.from_product([range(1, 13), range(24)])).to_numpy().reshape(12, 24)
    return prof[loc.dt.month.to_numpy() - 1, loc.dt.hour.to_numpy()]   # value per interval


def place_jobs(jobs, period, origin, offset, rng, usable):
    """Random alignment: each job gets a random week of the period, keeping its local weekday and clock time."""
    p0 = pd.Timestamp(PERIODS[period][0], tz="UTC")
    p1 = pd.Timestamp(PERIODS[period][1], tz="UTC") - pd.Timedelta(hours=MARGIN_H)
    # Monday 00:00 local of the first full week
    first_local = (p0 + pd.Timedelta(hours=offset)).normalize()
    first_monday = first_local + pd.Timedelta(days=(7 - first_local.weekday()) % 7)
    n_weeks = int(((p1 + pd.Timedelta(hours=offset)) - first_monday) / pd.Timedelta(days=7)) - 1
    w = rng.integers(0, n_weeks, len(jobs["r_act_h"]))
    local = first_monday + pd.to_timedelta(w * 7 + jobs["submit_local_dow"], unit="D") \
        + pd.to_timedelta(jobs["submit_local_hour"], unit="h")
    a = ((local - pd.Timedelta(hours=offset)) - origin) / pd.Timedelta(hours=1)
    a = np.asarray(a, dtype="float64")
    hour_idx = np.floor(a).astype(np.int64)
    bad = np.concatenate([[0], np.cumsum(~usable)])          # unusable hours before index k
    lo = np.clip(hour_idx, 0, len(usable))
    hi = np.clip(hour_idx + sc.HP, 0, len(usable))
    ok = (hour_idx >= 0) & (hour_idx + sc.HP <= len(usable)) & (bad[hi] - bad[lo] == 0)
    return a, ok


def load_fc(fc_dir, model, ba, origin):
    z = np.load(os.path.join(ROOT, fc_dir, model, f"{ba}.npz"))
    issue = pd.to_datetime(z["issue_utc"], utc=True)
    first_k = int(round((issue[0] - origin) / pd.Timedelta(hours=1)))   # issue at origin + first_k hours
    step = np.diff(z["issue_utc"].astype("int64"))
    assert (step == 3_600_000_000_000).all(), "forecast issues must be hourly"
    return first_k, z["fc"]


def fc_window(first_k, fc, a):
    rows = np.floor(a).astype(np.int64) - first_k
    assert rows.min() >= 0 and rows.max() < len(fc), "arrival outside forecast span"
    w = fc[rows].astype("float64")                          # leads 1..96 = intervals 0..95
    pad = np.repeat(w[:, -1:], sc.HP - w.shape[1], axis=1)  # intervals 96-97: hold the lead-96 value
    return np.concatenate([w, pad], axis=1)


def run_ba(ba, args, jobs_by_trace, offsets, outdir):
    """Simulate one BA for every trace; aggregate and write results/<...>/<trace>/<BA>.npz inside the worker."""
    origin, ci, usable, utc = load_ba(ba, args.tag)
    cum = sc.cum_hours(ci)
    off = offsets[ba]
    prof = hist_profile(ci, utc, off)
    fcs = {m: load_fc(args.fc_dir, m, ba, origin) for m in FC_MODELS}
    # local clock hour of every interval start, for the night-window rule
    loc_hour = ((utc + pd.Timedelta(hours=off) - pd.Timedelta(hours=1)).dt.hour).to_numpy()
    # usable flag is per hour row; convert to per-interval day usability
    out = {}
    for trace, jobs in jobs_by_trace.items():
        res = {}
        for rep in range(args.reps):
            rng = np.random.default_rng([args.seed, rep, zlib.crc32(ba.encode()), zlib.crc32(trace.encode())])
            nj = len(jobs["r_act_h"])
            idx = np.sort(rng.choice(nj, size=min(args.n_jobs, nj), replace=False))
            J = {k: np.asarray(v[idx]) for k, v in jobs.items()}
            a, ok = place_jobs(J, args.period, origin, off, rng, usable)
            J, a = {k: v[ok] for k, v in J.items()}, a[ok]
            r_act = J["r_act_h"]
            r_est = {"act": r_act, "req": J["r_req_h"], "pred": J["r_pred_h"],
                     "pred2": np.minimum(J["r_req_h"], 2.0 * J["r_pred_h"])}
            p_kw = J["power_kw"]
            day = np.floor(a / 24.0).astype(np.int64)
            lcls = np.searchsorted(LEN_EDGES, r_act, side="right") - 1
            sig = {"oracle": sc.window_signal_actual(ci, a),
                   "histprofile": sc.window_signal_actual(prof, a)}
            for m in FC_MODELS:
                sig[m] = fc_window(*fcs[m], a)
            for S in SLACKS:
                slack = np.full(len(a), S)
                starts = {"runnow": a}
                # night rule: earliest candidate start whose local hour is 0-3, else now
                offs = np.arange(int(S / sc.STEP) + 1) * sc.STEP
                cand = a[:, None] + offs[None, :]
                hrs = loc_hour[np.clip(np.floor(cand).astype(np.int64), 0, len(loc_hour) - 1)]
                night = hrs < 4
                first = np.where(night.any(axis=1), night.argmax(axis=1), 0)
                starts["night"] = a + offs[first]
                for s_name, sg in sig.items():
                    for r_name, rh in r_est.items():
                        starts[f"{s_name}|{r_name}"] = sc.plan_start(sg, a, rh, slack)
                e_w = np.stack([p_kw * sc.realised(cum, ci, starts[k], r_act) for k in ARMS])   # g CO2
                e_u = np.stack([sc.realised(cum, ci, starts[k], r_act) / r_act for k in ARMS])  # g/kWh per job
                delay = np.stack([starts[k] - a for k in ARMS])
                key = (rep, S)
                res[key] = {"day": day, "lcls": lcls, "e_w": e_w.astype("float32"), "e_u": e_u.astype("float32"),
                            "delay": delay.astype("float32"), "energy_kwh": (p_kw * r_act).astype("float32")}
        os.makedirs(os.path.join(outdir, trace), exist_ok=True)
        flat = {}
        for k, v in aggregate(res).items():
            for kk, vv in v.items():
                flat[f"{k}__{kk}"] = vv
        np.savez_compressed(os.path.join(outdir, trace, f"{ba}.npz"), arms=np.array(ARMS), **flat)
        del res
    return ba


def aggregate(res):
    """Per (rep, S): per-day sums by length class -> arrays [n_arms, n_days, n_classes]."""
    agg = {}
    for (rep, S), r in res.items():
        d0 = r["day"].min()
        nd = r["day"].max() - d0 + 1
        nc = len(LEN_EDGES) - 1
        flat = (r["day"] - d0) * nc + r["lcls"]
        ew = np.zeros((len(ARMS), nd * nc))
        eu = np.zeros((len(ARMS), nd * nc))
        dl = np.zeros((len(ARMS), nd * nc))
        for i in range(len(ARMS)):
            ew[i] = np.bincount(flat, weights=r["e_w"][i], minlength=nd * nc)
            eu[i] = np.bincount(flat, weights=r["e_u"][i], minlength=nd * nc)
            dl[i] = np.bincount(flat, weights=r["delay"][i], minlength=nd * nc)
        cnt = np.bincount(flat, minlength=nd * nc)
        en = np.bincount(flat, weights=r["energy_kwh"], minlength=nd * nc)
        agg[f"r{rep}_S{int(S)}"] = dict(day0=d0, e_w=ew.reshape(len(ARMS), nd, nc), e_u=eu.reshape(len(ARMS), nd, nc),
                                       delay=dl.reshape(len(ARMS), nd, nc), n=cnt.reshape(nd, nc),
                                       energy=en.reshape(nd, nc))
    return agg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", required=True, choices=list(PERIODS))
    ap.add_argument("--tag", default="")
    ap.add_argument("--fc-dir", default="data/derived/forecasts")
    ap.add_argument("--traces", default="")
    ap.add_argument("--bas", default="")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--n-jobs", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=20261111)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--states", default="COMPLETED")
    ap.add_argument("--jobs", default="data/derived/jobs.parquet")
    ap.add_argument("--out-suffix", default="")
    ap.add_argument("--exclude-near-limit", action="store_true")
    args = ap.parse_args()
    if args.period == "TEST":
        check_prereg()
    el = pd.read_csv(os.path.join(ROOT, "tables", f"ba_eligibility{args.tag}.csv"))
    bas = sorted(el[el["eligible"]]["ba"]) if not args.bas else args.bas.split(",")
    offsets = ba_offsets()
    jobs = pd.read_parquet(os.path.join(ROOT, args.jobs))
    jobs = jobs[jobs["state"].isin(args.states.split(","))]
    jobs = jobs[(jobs["r_act_h"] >= 1 / 60) & (jobs["r_req_h"] <= MAX_REQ_H) & (jobs["r_req_h"] > 0)]
    assert jobs["r_act_h"].max() <= MAX_REQ_H, "actual runtime beyond 72 h would leave the 98 h checked window"
    if args.exclude_near_limit:   # sensitivity: drop jobs that ran to within 2 % of the request
        jobs = jobs[jobs["r_act_h"] < 0.98 * jobs["r_req_h"]]
    jobs = jobs.assign(power_kw=(jobs["power_w"] / 1000.0).fillna(1.0))   # traces without power: 1 kW per job
    traces = args.traces.split(",") if args.traces else sorted(jobs["trace"].unique())
    cols = ["r_act_h", "r_req_h", "r_pred_h", "power_kw", "submit_local_dow", "submit_local_hour"]
    jobs_by_trace = {t: {c: jobs.loc[jobs["trace"] == t, c].to_numpy() for c in cols} for t in traces}  # numpy: memmapped
    del jobs
    outdir = os.path.join(ROOT, "results", f"sim_{args.period}{args.tag}{args.out_suffix}")
    t0 = time.time()
    from joblib import Parallel, delayed
    Parallel(n_jobs=args.workers, verbose=5)(
        delayed(run_ba)(ba, args, jobs_by_trace, offsets, outdir) for ba in bas)
    with open(os.path.join(outdir, "RUN.txt"), "w", encoding="utf-8") as f:
        f.write(f"period={args.period} tag={args.tag} fc_dir={args.fc_dir} reps={args.reps} n_jobs={args.n_jobs} "
                f"seed={args.seed} states={args.states} traces={traces} bas={len(bas)} seconds={time.time()-t0:.0f}\n")
    print("done", outdir, f"{time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
