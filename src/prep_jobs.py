"""A07: standardise HPC job traces into one job table (data/derived/jobs.parquet).

One loader function per trace; all loaders return a frame with the raw-but-renamed columns
    trace, job_id, user, state_raw, submit_utc, end_utc, r_req_h, r_act_h, nodes, power_w, energy_kwh
and `finalise()` adds state, local clock fields, the leakage-free history predictor r_pred_h and n_hist.

Run:  PYTHONIOENCODING=utf-8 python src/prep_jobs.py [pm100 fdata kit_fh2 kestrel]   (default: all available)
Never executes downloaded files; reads parquet/gz text only.
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.compute as pc
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "derived" / "jobs.parquet"
STATS = ROOT / "tables" / "jobs_trace_stats.json"

SITE_TZ = {
    "PM100": "Europe/Rome",
    "FDATA": "Asia/Tokyo",
    "KIT_FH2": "Europe/Berlin",
    "KESTREL": "America/Denver",
}
COLS = ["trace", "job_id", "user", "state", "submit_utc", "submit_local_hour", "submit_local_dow",
        "r_req_h", "r_act_h", "nodes", "power_w", "energy_kwh", "r_pred_h", "n_hist"]
RAW_COLS = ["trace", "job_id", "user", "state_raw", "submit_utc", "end_utc", "r_req_h", "r_act_h",
            "nodes", "power_w", "energy_kwh"]


# ----------------------------------------------------------------------------------------------
# loaders
# ----------------------------------------------------------------------------------------------
def _mean_of_lists(path: Path, column: str, batch_size: int = 4000) -> np.ndarray:
    """Per-row mean of a list<int> column, batch by batch (never holds all lists)."""
    f = pq.ParquetFile(path)
    out = []
    for b in f.iter_batches(batch_size=batch_size, columns=[column]):
        col = b.column(0)
        n = pc.list_value_length(col).fill_null(0).to_numpy(zero_copy_only=False).astype(np.int64)
        v = pc.list_flatten(col).to_numpy(zero_copy_only=False).astype(np.float64)
        off = np.concatenate([[0], np.cumsum(n)])
        cs = np.concatenate([[0.0], np.cumsum(v)])
        tot = cs[off[1:]] - cs[off[:-1]]
        out.append(np.where(n > 0, tot / np.maximum(n, 1), np.nan))
    return np.concatenate(out)


def load_pm100() -> pd.DataFrame:
    """PM100 (Marconi100, CINECA Bologna). Timestamps are tz-aware UTC in the parquet (Slurm epoch).
    node_power_consumption = whole-job power in W (sum over the job's nodes, ps0+ps1 input power, 20 s
    samples; see PM100-data/extract_data.py::extract_job_power), so power_w = mean of the series with
    NO multiplication by the node count."""
    p = RAW / "pm100" / "job_table.parquet"
    d = pq.read_table(p, columns=["job_id", "user_id", "job_state", "submit_time", "end_time", "run_time",
                                  "time_limit", "num_nodes_alloc", "num_nodes_req"]).to_pandas()
    d["power_w"] = _mean_of_lists(p, "node_power_consumption")
    nodes = d["num_nodes_alloc"].where(d["num_nodes_alloc"] > 0, d["num_nodes_req"])
    r_act = d["run_time"].astype(float) / 3600.0
    return pd.DataFrame({
        "trace": "PM100", "job_id": d["job_id"].astype(str), "user": d["user_id"].astype(str),
        "state_raw": d["job_state"].astype(str),
        "submit_utc": pd.to_datetime(d["submit_time"], utc=True),
        "end_utc": pd.to_datetime(d["end_time"], utc=True),
        "r_req_h": d["time_limit"].astype(float) / 60.0,      # minutes -> h
        "r_act_h": r_act, "nodes": nodes,
        "power_w": d["power_w"],
        "energy_kwh": d["power_w"] * r_act / 1000.0,           # derived (no measured energy field)
    })


def _fdata_month(path: Path) -> pd.DataFrame:
    cols = ["jid", "usr", "adt", "sdt", "edt", "duration", "elpl", "econ", "avgpcon", "nnuma", "nnumr",
            "exit state"]
    t = pq.read_table(path, columns=cols).to_pandas()
    sub = pd.to_datetime(t["adt"], utc=True, format="ISO8601")
    sdt = pd.to_datetime(t["sdt"], utc=True, format="ISO8601")
    edt = pd.to_datetime(t["edt"], utc=True, format="ISO8601")
    dur = t["duration"].astype(float)
    end = edt.where(edt.notna(), sdt + pd.to_timedelta(dur, unit="s"))
    nodes = t["nnuma"].where(t["nnuma"] > 0, t["nnumr"])
    return pd.DataFrame({
        "trace": "FDATA", "job_id": t["jid"].astype("string[pyarrow]"), "user": t["usr"].astype("string[pyarrow]"),
        "state_raw": t["exit state"].astype(str).str.upper().astype("string[pyarrow]"),
        "submit_utc": sub, "end_utc": end,
        "r_req_h": t["elpl"].astype(float) / 3600.0,          # s -> h
        "r_act_h": dur / 3600.0, "nodes": nodes,
        "power_w": t["avgpcon"].astype(float),                # whole-job average power, W (sum over nodes)
        "energy_kwh": t["econ"].astype(float) / 1000.0,       # econ is Wh (measured)
    })


def load_fdata() -> pd.DataFrame:
    files = sorted((RAW / "fdata").glob("2?_??.parquet"))
    d = pd.concat([_fdata_month(f) for f in files], ignore_index=True)
    # jid is shared by array/bulk sub-jobs (about 40 % of rows repeat a jid): keep every row, make ids unique
    k = d.groupby("job_id").cumcount()
    rep = d["job_id"].duplicated(keep=False)
    d["job_id"] = d["job_id"].where(~rep, d["job_id"] + "." + k.astype(str))
    return d


def load_kit_fh2() -> pd.DataFrame:
    """KIT ForHLR II, original SWF as received (no cleaned version exists in the archive).
    Fields: 2 submit (s since UnixStartTime), 3 wait, 4 run, 5 procs alloc, 8 procs req, 9 requested time,
    11 status, 12 user, 15 queue (1 normal 20 cores/node, 2 visu 48 cores/node)."""
    p = RAW / "kit_fh2" / "KIT-FH2-2016-1.swf.gz"
    start = None
    rows = []
    with gzip.open(p, "rt", encoding="latin-1") as fh:
        for line in fh:
            if line.startswith(";"):
                if "UnixStartTime" in line:
                    start = int(line.split(":")[1])
                continue
            s = line.split()
            if len(s) >= 15:
                rows.append(s[:18])
    assert start is not None
    a = np.array(rows, dtype=float)
    jid, sub, wait, run, pal, preq, rq, st, usr, qu = (a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4], a[:, 7],
                                                       a[:, 8], a[:, 10], a[:, 11], a[:, 14])
    procs = np.where(pal > 0, pal, preq)
    cpn = np.where(qu == 2, 48.0, 20.0)
    nodes = np.ceil(procs / cpn)
    submit = pd.to_datetime(start + sub, unit="s", utc=True)
    runs = np.where(run >= 0, run, np.nan)
    endt = pd.to_datetime(start + sub + np.where(wait >= 0, wait, np.nan) + runs, unit="s", utc=True)
    smap = {1: "COMPLETED", 0: "FAILED", 5: "CANCELLED"}
    return pd.DataFrame({
        "trace": "KIT_FH2", "job_id": pd.Series(jid.astype(np.int64)).astype(str),
        "user": pd.Series(usr.astype(np.int64)).astype(str),
        "state_raw": pd.Series(st.astype(int)).map(smap).fillna("OTHER"),
        "submit_utc": submit, "end_utc": endt,
        "r_req_h": np.where(rq > 0, rq, np.nan) / 3600.0, "r_act_h": runs / 3600.0,
        "nodes": nodes, "power_w": np.nan, "energy_kwh": np.nan,
    })


def load_kestrel() -> pd.DataFrame:
    """NLR Kestrel: only if downloaded to data/raw/kestrel (open licence, no click-through)."""
    d = RAW / "kestrel"
    files = list(d.rglob("*.parquet")) if d.exists() else []
    if not files:
        raise FileNotFoundError("Kestrel not downloaded")
    raise NotImplementedError("Kestrel loader is written only after the licence and schema are checked")


LOADERS = {"pm100": load_pm100, "fdata": load_fdata, "kit_fh2": load_kit_fh2, "kestrel": load_kestrel}


# ----------------------------------------------------------------------------------------------
# normalisation
# ----------------------------------------------------------------------------------------------
def norm_state(s: pd.Series) -> pd.Series:
    m = {"COMPLETED": "COMPLETED", "TIMEOUT": "TIMEOUT", "FAILED": "FAILED", "OUT_OF_MEMORY": "FAILED",
         "NODE_FAIL": "FAILED", "CANCELLED": "CANCELLED"}
    return s.map(m).fillna("OTHER")


def history_predict(df: pd.DataFrame, hist_states=("COMPLETED", "TIMEOUT")) -> tuple[np.ndarray, np.ndarray]:
    """Mean r_act_h of the user's two most recent (by END time) jobs with END strictly before this job's
    submit and state in hist_states. Returns (pred_h or NaN, n_prior_capped_at_2). Vectorised."""
    t0 = min(df["submit_utc"].min(), df["end_utc"].min())
    sub = ((df["submit_utc"] - t0).dt.total_seconds().to_numpy() * 1000).round().astype(np.int64)
    end = ((df["end_utc"] - t0).dt.total_seconds().to_numpy() * 1000)
    ucode = pd.factorize(df["user"])[0].astype(np.int64)
    SH = np.int64(1) << 42                                   # 4.4e12 ms = 139 years per user slot
    assert sub.max() < SH
    elig = df["state"].isin(hist_states).to_numpy() & np.isfinite(end) & np.isfinite(df["r_act_h"].to_numpy())
    ek = ucode[elig] * SH + np.nan_to_num(end[elig]).round().astype(np.int64)
    ra = df["r_act_h"].to_numpy()[elig]
    order = np.lexsort((np.arange(len(ek)), ek))             # by user, end, then original order (stable)
    ek, ra = ek[order], ra[order]
    q = ucode * SH + sub
    idx = np.searchsorted(ek, q, side="left")                # eligible jobs with key < q  (END < submit)
    ustart = np.searchsorted(ek, ucode * SH, side="left")
    n_prior = idx - ustart
    c1 = np.where(n_prior >= 1, ra[np.maximum(idx - 1, 0)], np.nan)
    c2 = np.where(n_prior >= 2, ra[np.maximum(idx - 2, 0)], np.nan)
    pred = np.where(n_prior >= 2, (c1 + c2) / 2.0, np.where(n_prior == 1, c1, np.nan))
    return pred, np.minimum(n_prior, 2)


def assert_leakage_free(df: pd.DataFrame, n: int = 1000, seed: int = 7) -> None:
    """Naive recomputation on a random sample; also checks every used job ended strictly before submit."""
    rng = np.random.default_rng(seed)
    pick = rng.choice(len(df), size=min(n, len(df)), replace=False)
    rows_of = df.groupby("user", sort=False).indices          # user -> row positions (ints only)
    for i in pick:
        row = df.iloc[i]
        g = df.iloc[rows_of[row["user"]]][["state", "end_utc", "r_act_h"]]
        g = g[g["state"].isin(["COMPLETED", "TIMEOUT"]) & (g["end_utc"] < row["submit_utc"])]
        assert (g["end_utc"] < row["submit_utc"]).all()
        g = g.assign(_o=g.index).sort_values(["end_utc", "_o"]).tail(2)
        if len(g) == 0:
            exp = row["r_req_h"]
        else:
            exp = min(g["r_act_h"].mean(), row["r_req_h"])
        assert int(row["n_hist"]) == min(len(g), 2), (row["trace"], row["job_id"])
        assert np.isclose(row["r_pred_h"], exp, rtol=1e-9, atol=1e-12), (row["trace"], row["job_id"])


def finalise(raw: pd.DataFrame, trace: str) -> tuple[pd.DataFrame, dict]:
    info = {"rows_in": int(len(raw))}
    df = raw.copy()
    df["state"] = norm_state(df["state_raw"])
    info["rows_by_state_in"] = {k: int(v) for k, v in df["state"].value_counts().items()}
    info["raw_states"] = {k: int(v) for k, v in df["state_raw"].value_counts().items()}
    ok = (df["submit_utc"].notna() & df["user"].notna() & np.isfinite(df["r_req_h"]) & (df["r_req_h"] > 0)
          & np.isfinite(df["r_act_h"]) & (df["r_act_h"] >= 0) & np.isfinite(df["nodes"]) & (df["nodes"] >= 1))
    info["dropped_invalid"] = int((~ok).sum())
    df = df[ok].reset_index(drop=True)
    df["nodes"] = df["nodes"].astype(np.int64)
    local = df["submit_utc"].dt.tz_convert(SITE_TZ[trace])
    df["submit_local_hour"] = (local.dt.hour + local.dt.minute / 60.0 + local.dt.second / 3600.0).astype(float)
    df["submit_local_dow"] = local.dt.dayofweek.astype(np.int64)
    # drop duplicate (trace, job_id) only if exact duplicates would break the table key; report count
    info["dup_job_id"] = int(df["job_id"].duplicated().sum())
    df = df.sort_values(["submit_utc", "job_id"], kind="stable").reset_index(drop=True)
    pred, nh = history_predict(df)
    df["r_pred_h"] = np.minimum(np.where(np.isnan(pred), df["r_req_h"], pred), df["r_req_h"])
    df["n_hist"] = nh.astype(np.int64)
    assert_leakage_free(df)
    info["leakage_assert"] = "passed (1000 random jobs recomputed naively)"
    info["rows_out"] = int(len(df))
    info["rows_by_state_out"] = {k: int(v) for k, v in df["state"].value_counts().items()}
    return df, info


# ----------------------------------------------------------------------------------------------
# statistics for the report
# ----------------------------------------------------------------------------------------------
Q = [0.05, 0.25, 0.5, 0.75, 0.95]


def _q(x) -> list:
    x = pd.Series(x).replace([np.inf, -np.inf], np.nan).dropna()
    return [float(v) for v in x.quantile(Q)] if len(x) else [float("nan")] * 5


def trace_stats(df: pd.DataFrame, info: dict) -> dict:
    s = dict(info)
    c = df[df["state"] == "COMPLETED"]
    s["completed_rows"] = int(len(c))
    s["frac_ract_gt_rreq_all"] = float((df["r_act_h"] > df["r_req_h"]).mean())
    s["frac_ract_gt_rreq_completed"] = float((c["r_act_h"] > c["r_req_h"]).mean()) if len(c) else float("nan")
    s["q_rreq_completed"] = _q(c["r_req_h"])
    s["q_ract_completed"] = _q(c["r_act_h"])
    s["q_ratio_completed"] = _q(c["r_act_h"] / c["r_req_h"])
    s["median_ratio_completed"] = s["q_ratio_completed"][2]
    t = df[df["state"] == "TIMEOUT"]
    s["n_timeout"] = int(len(t))
    s["timeout_within2pct"] = float((np.abs(t["r_act_h"] / t["r_req_h"] - 1) <= 0.02).mean()) if len(t) else None
    f = df[df["state"] == "FAILED"]
    s["failed_within2pct_of_req"] = float((np.abs(f["r_act_h"] / f["r_req_h"] - 1) <= 0.02).mean()) if len(f) else None
    pos = c[c["r_act_h"] > 0]
    s["q_rpred_over_ract_completed"] = _q(pos["r_pred_h"] / pos["r_act_h"])
    s["q_rpred_over_rreq_completed"] = _q(c["r_pred_h"] / c["r_req_h"])
    s["share_nhist0_all"] = float((df["n_hist"] == 0).mean())
    s["share_nhist0_completed"] = float((c["n_hist"] == 0).mean()) if len(c) else float("nan")
    s["q_power_w"] = _q(df["power_w"])
    s["power_nan_share"] = float(df["power_w"].isna().mean())
    if df["energy_kwh"].notna().any():
        tot = df["energy_kwh"].sum()
        s["total_energy_kwh"] = float(tot)
        s["energy_share_jobs_gt24h"] = float(df.loc[df["r_act_h"] > 24, "energy_kwh"].sum() / tot)
    else:
        s["total_energy_kwh"] = None
        s["energy_share_jobs_gt24h"] = None
    s["frac_within2pct_all"] = float((np.abs(df["r_act_h"] / df["r_req_h"] - 1) <= 0.02).mean())
    s["frac_r_act_zero"] = float((df["r_act_h"] == 0).mean())
    s["submit_min"] = str(df["submit_utc"].min())
    s["submit_max"] = str(df["submit_utc"].max())
    s["n_users"] = int(df["user"].nunique())
    s["submit_utc_hour_hist"] = [int(v) for v in df["submit_utc"].dt.hour.value_counts().sort_index().reindex(range(24), fill_value=0)]
    s["submit_local_hour_hist"] = [int(v) for v in np.floor(df["submit_local_hour"]).astype(int).value_counts().sort_index().reindex(range(24), fill_value=0)]
    return s


def main(which: list[str]) -> None:
    frames, allstats = [], {}
    if STATS.exists():
        allstats = json.loads(STATS.read_text(encoding="utf-8"))
    for name in which:
        try:
            raw = LOADERS[name]()
        except (FileNotFoundError, NotImplementedError) as e:
            print(f"[{name}] skipped: {e}")
            continue
        trace = raw["trace"].iloc[0]
        df, info = finalise(raw[RAW_COLS], trace)
        allstats[trace] = trace_stats(df, info)
        out = df[COLS]
        out.to_parquet(OUT.with_name(f"jobs_{trace}.parquet"), index=False)
        frames.append(out)
        print(f"[{name}] rows in {info['rows_in']}, out {info['rows_out']}, "
              f"median ratio completed {allstats[trace]['median_ratio_completed']:.4f}")
    STATS.parent.mkdir(exist_ok=True)
    STATS.write_text(json.dumps(allstats, indent=1), encoding="utf-8")
    # combine all per-trace files present
    parts = [pd.read_parquet(p) for p in sorted(OUT.parent.glob("jobs_*.parquet"))]
    jobs = pd.concat(parts, ignore_index=True)
    jobs = jobs.astype({"trace": "string", "job_id": "string", "user": "string", "state": "string"})
    jobs["submit_local_dow"] = jobs["submit_local_dow"].astype(np.int64)
    jobs["nodes"] = jobs["nodes"].astype(np.int64)
    jobs["n_hist"] = jobs["n_hist"].astype(np.int64)
    jobs[COLS].to_parquet(OUT, index=False)
    print("wrote", OUT, len(jobs), jobs.groupby("trace").size().to_dict())


if __name__ == "__main__":
    main(sys.argv[1:] or ["pm100", "fdata", "kit_fh2", "kestrel"])
