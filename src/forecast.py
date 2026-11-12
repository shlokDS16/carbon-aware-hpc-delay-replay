#!/usr/bin/env python
"""A05: past-only hourly carbon-intensity forecasters for every BA (Paper A).

Models: persistence, snaive_day, snaive_week, profile7, lgbm (global LightGBM, horizon as a feature).
Outputs (see research/PIPELINE_SPEC.md):
  data/derived/forecasts<tag>/<model>/<BA>.npz  with issue_utc (int64 ns) and fc float32 [n_issue, 96]
  tables/forecast_skill<tag>.csv                DEV only (TEST is never scored here)
Leakage design: every feature for issue hour t uses C[<= t] only; LightGBM is fitted on TRAIN targets only
(target hour < 2024-07-01), early-stopped on the last 6 months of TRAIN (issues from 2024-01-01, targets
< 2024-07-01), and training rows are purged so that no training target falls inside the validation window.

Usage: python src/forecast.py --input data/derived/ci_clean_v0.parquet --tag _v0 --models persistence,snaive_day,...
"""
import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
H = 96
G0 = pd.Timestamp("2018-07-01 00:00:00")          # grid origin, hour index 0 (naive UTC)
G1 = pd.Timestamp("2026-07-06 00:00:00")          # grid end (exclusive)
NG = int((G1 - G0) / pd.Timedelta(hours=1))
TRAIN_END = pd.Timestamp("2024-07-01")            # first DEV hour
VAL_START = pd.Timestamp("2024-01-01")            # start of early-stopping window (last 6 months of TRAIN)
DEV_END = pd.Timestamp("2025-07-01")              # first TEST hour
ISSUE_END = pd.Timestamp("2026-07-01")            # exclusive; issue hours cover DEV + TEST
IDX_TRAIN_END = int((TRAIN_END - G0) / pd.Timedelta(hours=1))
IDX_VAL_START = int((VAL_START - G0) / pd.Timedelta(hours=1))
IDX_DEV_END = int((DEV_END - G0) / pd.Timedelta(hours=1))
IDX_ISSUE_END = int((ISSUE_END - G0) / pd.Timedelta(hours=1))
LAGS = [0, 1, 2, 3, 6, 12, 24, 48, 72, 168]
FUELS = ["coal", "natural_gas", "nuclear", "oil", "hydro", "solar", "wind", "other", "unknown"]
ALL_MODELS = ["persistence", "snaive_day", "snaive_week", "profile7", "lgbm"]
BUCKETS = {"1-6": (1, 6), "7-24": (7, 24), "25-48": (25, 48), "49-96": (49, 96), "1-24": (1, 24)}

_DOW0 = 6  # 2018-07-01 is a Sunday; Monday = 0
_MONTH = np.asarray(pd.date_range(G0, periods=NG + H + 200, freq="h").month, dtype=np.int8)


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def take(a, idx):
    """a[idx] with NaN for out-of-range indices."""
    ok = (idx >= 0) & (idx < a.shape[0])
    out = np.full(idx.shape, np.nan, dtype=np.float32)
    out[ok] = a[idx[ok]]
    return out


# ---------------------------------------------------------------- data
def causal_input(Y, flag, limit=6):
    """Model-input series: hours with flag 1 (interpolated) or 2 (outlier replaced) hold values that may use later
    observations, so they are replaced by the last earlier valid value (forward fill, at most `limit` hours; NaN if none).
    Flag 3 (same hour previous week) is causal and kept; flag 4 (unfilled) stays NaN."""
    C = Y.copy()
    bad = (flag == 1) | (flag == 2)
    if bad.any():
        m = Y.copy()
        m[bad] = np.nan
        ff = pd.Series(m).ffill(limit=limit).to_numpy(np.float32)
        C[bad] = ff[bad]
    return C


def load_series(input_path, tag, bas, elig_path, shares_path):
    df = pd.read_parquet(input_path)
    col = "ci_clean" if "ci_clean" in df.columns else "ci"
    has_flag = "flag" in df.columns
    df = df[["ba", "utc", col] + (["flag"] if has_flag else [])].rename(columns={col: "c"})
    df["utc"] = pd.to_datetime(df["utc"], utc=True).dt.tz_convert(None)
    use_ffill = col == "ci"
    if elig_path is not None and Path(elig_path).exists():
        el = pd.read_csv(elig_path)
        el_bas = set(el.loc[el["eligible"].astype(str).str.lower().isin(["true", "1"]), "ba"])
        df = df[df["ba"].isin(el_bas)]
        log(f"eligibility file {elig_path}: {len(el_bas)} eligible BAs")
    if bas:
        df = df[df["ba"].isin(bas)]
    ba_list = sorted(df["ba"].unique())
    sh = None
    if shares_path and Path(shares_path).exists():
        cols = ["ba", "utc"] + ["share_" + f for f in FUELS]
        sh = pd.read_parquet(shares_path, columns=cols)
        sh["utc"] = pd.to_datetime(sh["utc"], utc=True).dt.tz_convert(None)
        sh = sh[sh["ba"].isin(ba_list)]
    data = {}
    for ba in ba_list:
        d = df[df["ba"] == ba].drop_duplicates("utc").set_index("utc")["c"].sort_index()
        d = d[(d.index >= G0) & (d.index < G1)]
        full = pd.Series(np.nan, index=pd.date_range(G0, G1 - pd.Timedelta(hours=1), freq="h"), dtype="float32")
        full.loc[d.index] = d.values.astype("float32")
        if use_ffill and len(d):
            lo, hi = d.index.min(), d.index.max()
            full.loc[lo:hi] = full.loc[lo:hi].ffill()   # causal forward fill inside the observed span
        C = full.to_numpy(dtype=np.float32)
        S = np.full((NG, len(FUELS)), np.nan, dtype=np.float32)
        if sh is not None:
            s = sh[sh["ba"] == ba].drop_duplicates("utc").set_index("utc").sort_index()
            s = s[(s.index >= G0) & (s.index < G1)]
            if len(s):
                sf = s[["share_" + f for f in FUELS]].reindex(full.index).ffill()   # causal
                S = sf.to_numpy(dtype=np.float32)
        Y = C.copy()                                   # targets (training, DEV skill): ci_clean as is
        if has_flag:
            fl = np.full(NG, -1, dtype=np.int8)
            f = df.loc[df["ba"] == ba].drop_duplicates("utc").set_index("utc")["flag"]
            f = f[(f.index >= G0) & (f.index < G1)]
            fl[((f.index - G0) / pd.Timedelta(hours=1)).astype(int)] = f.to_numpy(np.int8)
            C = causal_input(Y, fl)
        data[ba] = {"C": C, "Y": Y, "S": S}
    return ba_list, data


# ---------------------------------------------------------------- baselines (vectorised over issue x lead)
def baseline_feats(C, t, h):
    k0 = -(-h // 24)                       # ceil(h/24)
    snd = take(C, t + h - 24 * k0)
    snw = take(C, t + h - 168 * (-(-h // 168)))
    acc = np.zeros(t.shape, dtype=np.float32)
    cnt = np.zeros(t.shape, dtype=np.float32)
    for j in range(7):
        v = take(C, t + h - 24 * (k0 + j))
        m = np.isfinite(v)
        acc[m] += v[m]
        cnt += m
    with np.errstate(invalid="ignore", divide="ignore"):
        p7 = np.where(cnt > 0, acc / cnt, np.nan).astype(np.float32)
    return snd, snw, p7


def baseline_fc(C, issues, model):
    t = np.repeat(issues, H)
    h = np.tile(np.arange(1, H + 1), issues.size)
    if model == "persistence":
        out = take(C, t)
    else:
        snd, snw, p7 = baseline_feats(C, t, h)
        out = {"snaive_day": snd, "snaive_week": snw, "profile7": p7}[model]
    out = out.reshape(issues.size, H).astype(np.float32)
    out[~np.isfinite(C[issues])] = np.nan    # no forecast before the BA has data
    return out


# ---------------------------------------------------------------- LightGBM features
def roll_stats(C):
    s = pd.Series(C.astype(np.float64))
    r24, r168 = s.rolling(24, min_periods=12), s.rolling(168, min_periods=84)
    return (r24.mean().to_numpy(np.float32), r24.std().to_numpy(np.float32),
            r168.mean().to_numpy(np.float32), r168.std().to_numpy(np.float32))


FEAT_NAMES = (["h"] + [f"lag{l}" for l in LAGS] + ["m24", "s24", "m168", "s168",
              "tgt_hod", "tgt_dow", "iss_hod", "iss_dow", "tgt_month", "snaive_day", "snaive_week", "profile7"]
              + ["share_" + f for f in FUELS] + ["ba_code"])


def build_X(ba_code, rec, t, h):
    """Feature matrix for rows (issue index t, lead h) of one BA. Only data at index <= t is used for CI/share
    features; calendar features of the target hour are known in advance."""
    C, S, R = rec["C"], rec["S"], rec["R"]
    n = t.size
    X = np.empty((n, len(FEAT_NAMES)), dtype=np.float32)
    X[:, 0] = h
    c = 1
    for l in LAGS:
        X[:, c] = take(C, t - l)
        c += 1
    for r in R:
        X[:, c] = take(r, t)
        c += 1
    tt = t + h
    X[:, c] = tt % 24
    X[:, c + 1] = ((tt // 24) + _DOW0) % 7
    X[:, c + 2] = t % 24
    X[:, c + 3] = ((t // 24) + _DOW0) % 7
    X[:, c + 4] = _MONTH[tt]
    c += 5
    snd, snw, p7 = baseline_feats(C, t, h)
    X[:, c], X[:, c + 1], X[:, c + 2] = snd, snw, p7
    c += 3
    Sv = S[t]
    X[:, c:c + len(FUELS)] = Sv
    X[:, -1] = ba_code
    base = np.where(np.isfinite(p7), p7, np.where(np.isfinite(snd), snd, take(C, t))).astype(np.float32)
    return X, base


def make_train(ba_list, data, stride, rows_per_issue, rng):
    Xtr, ytr, Xva, yva = [], [], [], []
    for code, ba in enumerate(ba_list):
        rec = data[ba]
        C = rec["C"]
        ts = np.arange(0, IDX_TRAIN_END)
        ts = ts[(ts % stride == 0) & np.isfinite(C[ts])]
        if ts.size == 0:
            continue
        hs = np.argsort(rng.random((ts.size, H)), axis=1)[:, :rows_per_issue] + 1
        t = np.repeat(ts, rows_per_issue)
        h = hs.reshape(-1)
        tgt = t + h
        y = take(rec["Y"], tgt)
        ok = np.isfinite(y) & (tgt < IDX_TRAIN_END)
        is_val = ok & (t >= IDX_VAL_START)
        is_tr = ok & (tgt < IDX_VAL_START)               # purge: training targets end before the validation window
        for mask, Xl, yl in ((is_tr, Xtr, ytr), (is_val, Xva, yva)):
            if mask.any():
                X, base = build_X(code, rec, t[mask], h[mask])
                Xl.append(X)
                yl.append((y[mask] - base).astype(np.float32))
                if Xl is Xtr:
                    pass
    return (np.concatenate(Xtr), np.concatenate(ytr), np.concatenate(Xva), np.concatenate(yva))


def fit_lgbm(ba_list, data, args, out_dir):
    import lightgbm as lgb
    rng = np.random.default_rng(args.seed)
    nvalid = sum(int(np.isfinite(data[b]["C"][:IDX_TRAIN_END]).sum()) for b in ba_list)
    stride = max(args.min_stride, math.ceil(nvalid * args.rows_per_issue / args.max_rows))
    log(f"lgbm: {nvalid} valid TRAIN BA-hours; issue stride {stride}, {args.rows_per_issue} leads per issue")
    Xtr, ytr, Xva, yva = make_train(ba_list, data, stride, args.rows_per_issue, rng)
    log(f"lgbm: train rows {len(ytr)}, validation rows {len(yva)}")
    assert len(ytr) < 3_000_000
    params = dict(objective="l1", learning_rate=args.lr, num_leaves=args.num_leaves, min_data_in_leaf=200,
                  feature_fraction=0.8, bagging_fraction=0.7, bagging_freq=1, lambda_l2=1.0, max_bin=255,
                  seed=args.seed, bagging_seed=args.seed, feature_fraction_seed=args.seed, data_random_seed=args.seed,
                  deterministic=True, num_threads=args.threads, verbose=-1)
    log("lgbm hyperparameters: " + json.dumps({**params, "num_boost_round": args.rounds,
                                               "early_stopping_rounds": args.patience, "stride": stride,
                                               "rows_per_issue": args.rows_per_issue}))
    dtr = lgb.Dataset(Xtr, ytr, feature_name=FEAT_NAMES, categorical_feature=["ba_code"], free_raw_data=True)
    dva = lgb.Dataset(Xva, yva, reference=dtr, free_raw_data=True)
    t0 = time.time()
    model = lgb.train(params, dtr, num_boost_round=args.rounds, valid_sets=[dva], valid_names=["val"],
                      callbacks=[lgb.early_stopping(args.patience, verbose=True), lgb.log_evaluation(50)])
    log(f"lgbm: fitted in {time.time()-t0:.0f} s, best iteration {model.best_iteration}, "
        f"val MAE (residual) {model.best_score['val']['l1']:.3f}")
    model.save_model(str(out_dir / "lgbm_model.txt"), num_iteration=model.best_iteration)
    imp = pd.Series(model.feature_importance("gain"), index=FEAT_NAMES).sort_values(ascending=False)
    log("lgbm top gain features: " + ", ".join(f"{k}:{v/imp.sum():.3f}" for k, v in imp.head(10).items()))
    del Xtr, ytr, Xva, yva, dtr, dva
    return model


def lgbm_fc(model, ba_code, rec, issues, chunk=1200):
    out = np.empty((issues.size, H), dtype=np.float32)
    hh = np.tile(np.arange(1, H + 1), chunk)
    for a in range(0, issues.size, chunk):
        ts = issues[a:a + chunk]
        t = np.repeat(ts, H)
        X, base = build_X(ba_code, rec, t, hh[:t.size])
        pred = model.predict(X, num_iteration=model.best_iteration, num_threads=model_threads[0]).astype(np.float32)
        out[a:a + chunk] = np.maximum(base + pred, 0).reshape(ts.size, H)
    out[~np.isfinite(rec["C"][issues])] = np.nan
    return out


model_threads = [20]


# ---------------------------------------------------------------- skill (DEV only)
def skill_for_ba(ba, C, issues, fcs):   # C here is the TARGET series (ci_clean)
    """fcs: dict model -> [n_issue,H]. Scored on DEV: issue in DEV and target hour < 2025-07-01 (no TEST data)."""
    from scipy.stats import rankdata
    sel = (issues >= IDX_TRAIN_END) & (issues < IDX_DEV_END)
    t = issues[sel]
    Y = take(C, (t[:, None] + np.arange(1, H + 1)[None, :]).ravel()).reshape(t.size, H)
    Y[(t[:, None] + np.arange(1, H + 1)[None, :]) >= IDX_DEV_END] = np.nan
    valid = np.isfinite(Y)
    for m in fcs:
        valid &= np.isfinite(fcs[m][sel])
    rows = []
    for m, F in fcs.items():
        F = F[sel]
        err = np.where(valid, F - Y, np.nan)
        ae, se = np.abs(err), err ** 2
        ape = np.where(valid & (Y > 1.0), ae / np.where(Y > 1.0, Y, 1.0), np.nan)
        for b, (lo, hi) in BUCKETS.items():
            sl = slice(lo - 1, hi)
            n = int(valid[:, sl].sum())
            r = dict(model=m, ba=ba, period="DEV", lead_bucket=b, n=n,
                     MAE=float(np.nansum(ae[:, sl]) / n) if n else np.nan,
                     RMSE=float(np.sqrt(np.nansum(se[:, sl]) / n)) if n else np.nan,
                     MAPE=float(np.nanmean(ape[:, sl])) if n else np.nan,
                     sum_ae=float(np.nansum(ae[:, sl])), rank_skill=np.nan)
            wins = {"1-24": [(0, 24)], "25-48": [(24, 48)], "49-96": [(48, 72), (72, 96)]}.get(b)
            if wins:
                cs = []
                for a0, a1 in wins:
                    w = valid[:, a0:a1].all(axis=1)
                    if w.sum() == 0:
                        continue
                    fw, yw = F[w, a0:a1], Y[w, a0:a1]
                    if m == "persistence":
                        cs.append(np.zeros(fw.shape[0]))
                        continue
                    rf, ry = rankdata(fw, axis=1), rankdata(yw, axis=1)
                    rf -= rf.mean(1, keepdims=True)
                    ry -= ry.mean(1, keepdims=True)
                    den = np.sqrt((rf ** 2).sum(1) * (ry ** 2).sum(1))
                    c = np.where(den > 0, (rf * ry).sum(1) / np.where(den > 0, den, 1), 0.0)   # constant window -> 0
                    cs.append(c)
                if cs:
                    r["rank_skill"] = float(np.concatenate(cs).mean())
            rows.append(r)
    return rows


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--tag", default="")
    ap.add_argument("--models", default=",".join(ALL_MODELS))
    ap.add_argument("--bas", default="", help="comma list to restrict BAs (dev runs)")
    ap.add_argument("--eligibility", default="")
    ap.add_argument("--shares", default="")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--max-rows", type=int, default=2_800_000)
    ap.add_argument("--rows-per-issue", type=int, default=12)
    ap.add_argument("--min-stride", type=int, default=7)
    ap.add_argument("--lr", type=float, default=0.08)
    ap.add_argument("--num-leaves", type=int, default=63)
    ap.add_argument("--rounds", type=int, default=1500)
    ap.add_argument("--patience", type=int, default=50)
    ap.add_argument("--threads", type=int, default=20)
    args = ap.parse_args()
    t_start = time.time()
    model_threads[0] = args.threads
    inp = Path(args.input)
    if not inp.is_absolute():
        inp = ROOT / inp
    models = [m for m in args.models.split(",") if m]
    assert all(m in ALL_MODELS for m in models), models
    elig = args.eligibility or str(ROOT / "tables" / f"ba_eligibility{args.tag}.csv")
    shares = args.shares or next((str(p) for p in [ROOT / "data/derived" / f"ci_hourly{args.tag}.parquet",
                                                    ROOT / "data/derived/ci_hourly_v0.parquet"] if p.exists()), "")
    free_gb = __import__("shutil").disk_usage(str(ROOT)).free / 1e9
    if free_gb < 10:
        sys.exit(f"free disk {free_gb:.1f} GB < 10 GB, stopping")
    bas = [b for b in args.bas.split(",") if b]
    ba_list, data = load_series(inp, args.tag, bas, elig, shares)
    log(f"input {inp.name}: {len(ba_list)} BAs; models {models}; free disk {free_gb:.0f} GB")
    for ba in ba_list:
        data[ba]["R"] = roll_stats(data[ba]["C"])
    issues = np.arange(IDX_TRAIN_END, IDX_ISSUE_END)
    issue_ns = ((G0 + pd.to_timedelta(issues, unit="h")).to_numpy("datetime64[ns]")).astype(np.int64)
    fdir = ROOT / "data" / "derived" / f"forecasts{args.tag}"
    for m in models:
        (fdir / m).mkdir(parents=True, exist_ok=True)
    model = fit_lgbm(ba_list, data, args, fdir) if "lgbm" in models else None
    for code, ba in enumerate(ba_list):
        C = data[ba]["C"]
        fcs = {}
        for m in models:
            F = lgbm_fc(model, code, data[ba], issues) if m == "lgbm" else baseline_fc(C, issues, m)
            np.savez_compressed(fdir / m / f"{ba}.npz", issue_utc=issue_ns, fc=F.astype(np.float32))
            fcs[m] = F
        rows = skill_for_ba(ba, data[ba]["Y"], issues, fcs)
        pd.DataFrame(rows).to_csv(fdir / f"_skill_{ba}.csv", index=False)
        log(f"{ba} done ({code+1}/{len(ba_list)})")
        del fcs
    # collect skill
    sk = pd.concat([pd.read_csv(fdir / f"_skill_{ba}.csv") for ba in ba_list], ignore_index=True)
    sk = sk[["model", "ba", "period", "lead_bucket", "MAE", "RMSE", "MAPE", "rank_skill", "n"]]
    out = ROOT / "tables" / f"forecast_skill{args.tag}.csv"
    sk.to_csv(out, index=False)
    for ba in ba_list:
        (fdir / f"_skill_{ba}.csv").unlink()
    log(f"wrote {out}; total run time {time.time()-t_start:.0f} s")


if __name__ == "__main__":
    main()
