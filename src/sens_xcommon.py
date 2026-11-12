"""Shared engine for the P4 amendments (research/P4_PLAN_AMEND.md) and the exploratory items X1-X7 (research/P4_PLAN_X.md).

Frozen modules (simcore, simulate, analyze, forecast, prep_jobs) are IMPORTED, never edited; sens_common.py is reused unchanged.
Everything here is post-freeze and exploratory.  Contents:
  * extra runtime estimates per job: padded min(R_req, 1.5 x pred) and the user-history quantile estimate
    (90th percentile of the same user's past actual runtimes that ended STRICTLY before submission, at least 5 past jobs,
    capped at R_req, else R_req), with a naive leakage assertion in the pattern of prep_jobs.assert_leakage_free;
  * a forecast-free threshold start rule that reads only observations available at the decision time (asserted);
  * run_ba_x: arm engine with the RNG use of simulate.run_ba / sens_common.run_ba_generic (same jobs, same alignment for the
    same seed), extra arm types (runtime multipliers, log-normal noise, lead cap, injected noise, threshold), an optional
    clock shift of arrivals (placement check) and an optional job-level dump (X4-X6);
  * analyse_x: frozen block bootstrap (analyze.bootstrap) with free-form contrasts, no p-values (exploratory).
Arm names: 'runnow' | 'thresh' | '<signal>|<runtime>' with signal in oracle, lgbm, lgbm@L<lead cap>, noisy, noisy96 and
runtime in act, req, pred, pad, q, m<multiplier>, ln, lnmu.
"""
import json
import os
import sys
import time
import zlib

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sens_common as C  # noqa: E402

sc, sim, an = C.sc, C.sim, C.an
ROOT, SRC = C.ROOT, C.SRC
EXTRA = os.path.join(ROOT, "results", "_sens_arms")
JOBS = os.path.join(ROOT, "data", "derived", "jobs.parquet")
TRACES = ("PM100", "FDATA", "KIT_FH2")
TRACE_KEY = {"PM100": "pm100", "FDATA": "fdata", "KIT_FH2": "kit_fh2"}
Q_PCT, Q_MIN_N, PAD_FACTOR = 0.9, 5, 1.5
THRESH_WIN_H, THRESH_PCT = 168, 0.25


# ------------------------------------------------------------------------------------------ expanding quantile (numba)
try:
    import numba as nb
    _njit = nb.njit(cache=False)
except Exception:                                   # pragma: no cover - slow pure-python fallback
    def _njit(f):
        return f


@_njit
def _bit_kth(bit, m, k):
    """0-based rank index of the k-th smallest (k is 1-based) in a Fenwick tree of size m."""
    pos = 0
    pw = 1
    while pw * 2 <= m:
        pw *= 2
    while pw > 0:
        nxt = pos + pw
        if nxt <= m and bit[nxt] < k:
            pos = nxt
            k -= bit[nxt]
        pw //= 2
    return pos


@_njit
def _expanding(order, ev_user, ev_type, ev_job, rank_of_job, ustart, ucount, sorted_vals, n, minn, q):
    out_q = np.full(n, np.nan)
    out_n = np.zeros(n, np.int64)
    bit = np.zeros(int(ucount.max()) + 2, np.int64)
    cur = -1
    m = 0
    cnt = 0
    for e in order:
        u = ev_user[e]
        if u != cur:
            for i in range(m + 1):
                bit[i] = 0
            cur = u
            m = ucount[u]
            cnt = 0
        if ev_type[e] == 1:
            i = rank_of_job[ev_job[e]] + 1
            while i <= m:
                bit[i] += 1
                i += i & (-i)
            cnt += 1
        else:
            j = ev_job[e]
            out_n[j] = cnt
            if cnt >= minn:
                pos = q * (cnt - 1)
                lo = int(np.floor(pos))
                hi = min(lo + 1, cnt - 1)
                fr = pos - lo
                v_lo = sorted_vals[ustart[u] + _bit_kth(bit, m, lo + 1)]
                v_hi = sorted_vals[ustart[u] + _bit_kth(bit, m, hi + 1)]
                out_q[j] = v_lo + fr * (v_hi - v_lo)
    return out_q, out_n


def expanding_quantile(df, hist_states=("COMPLETED", "TIMEOUT"), q=Q_PCT, minn=Q_MIN_N):
    """For every job: (q-quantile of r_act_h over the same user's eligible jobs with END strictly before this job's SUBMIT,
    number of such jobs).  Same timeline convention as prep_jobs.history_predict (milliseconds, END < SUBMIT strictly)."""
    t0 = min(df["submit_utc"].min(), df["end_utc"].min())
    sub = ((df["submit_utc"] - t0).dt.total_seconds().to_numpy() * 1000).round().astype(np.int64)
    endf = (df["end_utc"] - t0).dt.total_seconds().to_numpy() * 1000
    ucode = pd.factorize(df["user"])[0].astype(np.int64)
    ra = df["r_act_h"].to_numpy("float64")
    elig = df["state"].isin(hist_states).to_numpy() & np.isfinite(endf) & np.isfinite(ra)
    n = len(df)
    ej = np.nonzero(elig)[0]
    endm = np.nan_to_num(endf).round().astype(np.int64)
    ev_user = np.concatenate([ucode[ej], ucode])
    ev_time = np.concatenate([endm[ej], sub])
    ev_type = np.concatenate([np.ones(len(ej), np.int64), np.zeros(n, np.int64)])     # query (0) sorts before insert (1) at ties
    ev_job = np.concatenate([ej, np.arange(n)])
    order = np.lexsort((ev_type, ev_time, ev_user))
    # rank of each eligible job within its user by actual runtime
    perm = np.lexsort((ej, ra[ej], ucode[ej]))
    sj = ej[perm]
    su = ucode[sj]
    ucount = np.bincount(ucode[ej], minlength=int(ucode.max()) + 1).astype(np.int64)
    ustart = np.concatenate([[0], np.cumsum(ucount)[:-1]]).astype(np.int64)
    rank_of_job = np.zeros(n, np.int64)
    rank_of_job[sj] = np.arange(len(sj)) - ustart[su]
    sorted_vals = ra[sj]
    return _expanding(order, ev_user, ev_type, ev_job, rank_of_job, ustart, ucount, sorted_vals, n, minn, q)


def assert_quantile_leakage_free(df, r_q, n_q, n=1000, seed=7):
    """Naive recomputation on a random sample (pattern of prep_jobs.assert_leakage_free): every used past job ended strictly
    before the submit time, the count and the quantile agree, and the estimate is capped at R_req / falls back to R_req."""
    rng = np.random.default_rng(seed)
    pick = rng.choice(len(df), size=min(n, len(df)), replace=False)
    rows_of = df.groupby("user", sort=False).indices
    for i in pick:
        row = df.iloc[i]
        g = df.iloc[rows_of[row["user"]]][["state", "end_utc", "r_act_h"]]
        g = g[g["state"].isin(["COMPLETED", "TIMEOUT"]) & (g["end_utc"] < row["submit_utc"])]
        assert (g["end_utc"] < row["submit_utc"]).all()
        assert int(n_q[i]) == len(g), ("count", row["trace"], row["job_id"], n_q[i], len(g))
        if len(g) >= Q_MIN_N:
            exp = float(np.quantile(g["r_act_h"].to_numpy(), Q_PCT))
            assert np.isclose(r_q[i], exp, rtol=1e-9, atol=1e-12), ("quantile", row["trace"], row["job_id"], r_q[i], exp)
        else:
            assert np.isnan(r_q[i])


def qest_path(trace):
    return os.path.join(EXTRA, f"qest_{trace}.parquet")


def compute_qest(trace, log=print):
    """Quantile runtime estimate for every row of jobs.parquet of one trace.  Re-runs the frozen loader and finalise()
    (which re-asserts the frozen leakage check) because jobs.parquet does not store the end time; the result is aligned to
    jobs.parquet by a hash of job_id and by equality of r_pred_h.  Cached in results/_sens_arms/qest_<trace>.parquet."""
    import prep_jobs as pj
    os.makedirs(EXTRA, exist_ok=True)
    t0 = time.time()
    raw = pj.LOADERS[TRACE_KEY[trace]]()
    df, _ = pj.finalise(raw[pj.RAW_COLS], trace)
    del raw
    log(f"{trace}: frozen loader + finalise reproduced {len(df)} rows in {time.time() - t0:.0f} s")
    chk = pd.util.hash_pandas_object(df["job_id"].astype(str), index=False).to_numpy()
    cur = pd.read_parquet(JOBS, columns=["trace", "job_id", "r_pred_h", "r_act_h"], filters=[("trace", "==", trace)])
    assert len(cur) == len(df), "row count differs from jobs.parquet"
    assert np.array_equal(pd.util.hash_pandas_object(cur["job_id"].astype(str), index=False).to_numpy(), chk), "job order differs"
    assert np.array_equal(cur["r_pred_h"].to_numpy(), df["r_pred_h"].to_numpy()), "r_pred_h differs from jobs.parquet"
    del cur
    t1 = time.time()
    qv, nq = expanding_quantile(df)
    log(f"{trace}: expanding 90th percentile computed in {time.time() - t1:.0f} s")
    r_req = df["r_req_h"].to_numpy("float64")
    r_q = np.where(nq >= Q_MIN_N, np.minimum(qv, r_req), r_req)
    assert_quantile_leakage_free(df, qv, nq)
    log(f"{trace}: leakage assertion passed (1000 random jobs recomputed naively; every used job ended before submit)")
    pd.DataFrame({"chk": chk, "q_raw": qv, "r_q": r_q, "n_q": nq.astype(np.int32)}).to_parquet(qest_path(trace), index=False)
    return len(df)


def load_jobs_x(states="COMPLETED", traces=TRACES, user=False, log=print):
    """Filtered job arrays (same filter and order as sens_common.load_jobs) plus r_pad (padded) and r_q (quantile) per job."""
    cols = ["trace", "job_id", "state", "r_act_h", "r_req_h", "r_pred_h", "power_w", "submit_local_dow", "submit_local_hour"]
    if user:
        cols.append("user")
    out = {}
    for t in traces:
        if not os.path.exists(qest_path(t)):
            log(f"quantile runtime estimate for {t} not cached: computing")
            compute_qest(t, log)
        df = pd.read_parquet(JOBS, columns=cols, filters=[("trace", "==", t)])
        q = pd.read_parquet(qest_path(t))
        assert len(q) == len(df), "qest cache misaligned (rows)"
        assert np.array_equal(pd.util.hash_pandas_object(df["job_id"].astype(str), index=False).to_numpy(), q["chk"].to_numpy()), \
            "qest cache misaligned (job ids)"
        df["r_q"] = q["r_q"].to_numpy()
        df["n_q"] = q["n_q"].to_numpy()
        df = df[df["state"].isin(states.split(","))]
        df = df[(df["r_act_h"] >= 1 / 60) & (df["r_req_h"] <= sim.MAX_REQ_H) & (df["r_req_h"] > 0)]
        assert df["r_act_h"].max() <= sim.MAX_REQ_H
        df = df.assign(power_kw=(df["power_w"] / 1000.0).fillna(1.0),
                       r_pad=np.minimum(df["r_req_h"], PAD_FACTOR * df["r_pred_h"]))
        assert (df["r_q"] <= df["r_req_h"] + 1e-12).all() and (df["r_pad"] <= df["r_req_h"] + 1e-12).all()
        keep = ["r_act_h", "r_req_h", "r_pred_h", "power_kw", "submit_local_dow", "submit_local_hour", "r_pad", "r_q", "n_q"]
        d = {c: df[c].to_numpy() for c in keep}
        if user:
            d["user"] = pd.factorize(df["user"])[0].astype(np.int64)
        out[t] = d
        del df, q
    return out


# ------------------------------------------------------------------------------------------ threshold rule
def trailing_q25(ci):
    """q[h] = 25th percentile of ci[h-168 .. h-1] (the 168 hourly values that ended before interval h started)."""
    s = pd.Series(ci).rolling(THRESH_WIN_H, min_periods=THRESH_WIN_H).quantile(THRESH_PCT).to_numpy()
    return np.concatenate([[np.nan], s[:-1]])


def threshold_starts(ci, q25b, a, S, return_maxidx=False):
    """Forecast-free rule: at each quarter-hour t = a + k x 0.25 (k = 0 .. S/0.25) the planner looks at the most recent
    COMPLETED hourly value, ci[floor(t) - 1] (the interval containing t is not yet complete), and at the trailing 7-day 25th
    percentile q25b[floor(t)] built from ci[floor(t)-168 .. floor(t)-1].  Start at the first t whose observed value is below
    that percentile, else at a + S.  Only indices < floor(t) are read (asserted)."""
    K = int(round(S / sc.STEP))
    t = a[:, None] + sc.STEP * np.arange(K + 1)[None, :]
    h = np.floor(t).astype(np.int64)
    assert h.min() >= THRESH_WIN_H + 1 and h.max() <= len(ci) - 1
    idx_obs = h - 1
    assert (idx_obs < h).all(), "threshold rule read an observation that is not yet complete"
    cond = ci[idx_obs] < q25b[h]
    first = np.where(cond.any(axis=1), cond.argmax(axis=1), K)
    s = a + sc.STEP * first
    return (s, idx_obs.max()) if return_maxidx else s


def threshold_causality_test(ci, a, S, n=40, seed=3):
    """No future intensity is read: for sampled jobs, overwrite every ci value at index >= floor(chosen start) with garbage
    and recompute that job's decision from the corrupted series; it must not change."""
    rng = np.random.default_rng(seed)
    s_all = threshold_starts(ci, trailing_q25(ci), a, S)
    for j in rng.choice(len(a), size=min(n, len(a)), replace=False):
        bad = ci.copy()
        k0 = int(np.floor(s_all[j]))
        bad[k0:] = rng.uniform(0, 1500, len(bad) - k0)
        s_j = threshold_starts(bad, trailing_q25(bad), a[j:j + 1], S)[0]
        assert s_j == s_all[j], ("threshold decision depends on future intensity", j, s_j, s_all[j])
    return True


# ------------------------------------------------------------------------------------------ DEV noise scale (X2)
def dev_noise_table(bas, log=print):
    """Per BA and lead 1..96: MAE of the frozen LightGBM forecast on DEV issue hours, and the Gaussian relative noise scale
    sigma_l with E|ci x eps| = MAE_l, i.e. sigma_l = MAE_l / (sqrt(2/pi) x mean ci over the same targets).  DEV only."""
    rows = []
    d0, d1 = (pd.Timestamp(x, tz="UTC") for x in sim.PERIODS["DEV"])
    for ba in bas:
        origin, ci, usable, _ = sim.load_ba(ba, "")
        first_k, fc = sim.load_fc("data/derived/forecasts", "lgbm", ba, origin)
        k0 = int(round((d0 - origin) / pd.Timedelta(hours=1)))
        k1 = int(round((d1 - origin) / pd.Timedelta(hours=1))) - 100
        ks = np.arange(max(k0, first_k), k1)
        badc = np.concatenate([[0], np.cumsum(~usable)])
        ok = (badc[ks + 96] - badc[ks]) == 0
        ks = ks[ok]
        tgt = ci[ks[:, None] + np.arange(96)[None, :]]
        f = fc[ks - first_k].astype("float64")
        mae = np.abs(f - tgt).mean(axis=0)
        mci = tgt.mean(axis=0)
        sig = mae / (np.sqrt(2.0 / np.pi) * mci)
        z = np.random.default_rng(11).standard_normal(tgt.shape)
        mae_chk = np.abs(np.maximum(tgt * (1 + sig[None, :] * z), 0) - tgt).mean(axis=0)     # realised MAE of the injected noise on DEV
        for l in range(96):
            rows.append((ba, l + 1, int(len(ks)), float(mae[l]), float(mci[l]), float(sig[l]), float(mae_chk[l])))
    return pd.DataFrame(rows, columns=["ba", "lead", "n_issue_hours", "mae_lgbm_dev", "mean_ci_dev", "sigma_rel", "mae_noise_check_dev"])


def sigma_vectors(tab_ba, variant):
    """Window-column noise scales (98 intervals = leads 1..98).  'noisy': matched at leads 1-24, sigma_24 held beyond;
    'noisy96': matched at every lead 1-96, sigma_96 held for leads 97-98 (as forecasts hold their lead-96 value)."""
    sg = tab_ba.sort_values("lead")["sigma_rel"].to_numpy()
    v = np.empty(sc.HP)
    if variant == "noisy":
        v[:24] = sg[:24]
        v[24:] = sg[23]
    else:
        v[:96] = sg
        v[96:] = sg[95]
    return v


# ------------------------------------------------------------------------------------------ engine
def window_ok(a, usable):
    hour_idx = np.floor(a).astype(np.int64)
    bad = np.concatenate([[0], np.cumsum(~usable)])
    lo = np.clip(hour_idx, 0, len(usable))
    hi = np.clip(hour_idx + sc.HP, 0, len(usable))
    return (hour_idx >= 0) & (hour_idx + sc.HP <= len(usable)) & (bad[hi] - bad[lo] == 0)


class Env:
    """Per (BA, trace, replicate) state; signals, runtimes and starts are built lazily and cached."""

    def __init__(self, cfg, ba, trace, rep, seed, ci, cum_ci, a, J, fcs, q25b, noise_sigma, ln):
        self.cfg, self.ba, self.trace, self.rep, self.seed = cfg, ba, trace, rep, seed
        self.ci, self.cum_ci, self.a, self.J, self.fcs, self.q25b = ci, cum_ci, a, J, fcs, q25b
        self.noise_sigma, self.ln = noise_sigma, ln
        self._sig, self._rt = {}, {}
        self.crc = [seed, rep, zlib.crc32(ba.encode()), zlib.crc32(trace.encode())]

    def signal(self, name):
        if name in self._sig:
            return self._sig[name]
        if name == "oracle":
            w = sc.window_signal_actual(self.ci, self.a)
        elif name.startswith("lgbm"):
            first_k, fc = self.fcs["lgbm"]
            w = C.fc_window_lat(first_k, fc, self.a, 0)
            if "@L" in name:
                L = int(name.split("@L")[1])
                assert 1 <= L <= 96
                w[:, L:] = w[:, L - 1:L]                 # beyond the cap the planner holds the lead-L value
        elif name in ("noisy", "noisy96"):
            base = self.signal("oracle")
            rng = np.random.default_rng(self.crc + [4242])
            eps = rng.standard_normal(base.shape) * self.noise_sigma[name][None, :]
            w = np.maximum(base * (1.0 + eps), 0.0)
        else:
            raise ValueError(name)
        self._sig[name] = w
        return w

    def runtime(self, rt):
        if rt in self._rt:
            return self._rt[rt]
        J = self.J
        if rt == "act":
            r = J["r_act_h"]
        elif rt == "req":
            r = J["r_req_h"]
        elif rt == "pred":
            r = J["r_pred_h"]
        elif rt == "pad":
            r = J["r_pad"]
        elif rt == "q":
            r = J["r_q"]
        elif rt.startswith("m"):
            r = J["r_act_h"] * float(rt[1:])
        elif rt in ("ln", "lnmu"):
            mu, sd = self.ln[self.trace]
            rng = np.random.default_rng(self.crc + [777])
            z = rng.standard_normal(len(J["r_act_h"]))
            r = J["r_act_h"] * np.exp((mu if rt == "lnmu" else 0.0) + sd * z)
        else:
            raise ValueError(rt)
        self._rt[rt] = r
        return r

    def starts(self, arm, slack):
        if arm == "runnow":
            return self.a
        if arm == "thresh":
            return threshold_starts(self.ci, self.q25b, self.a, float(slack[0]))
        sig, rt = arm.split("|")
        return sc.plan_start(self.signal(sig), self.a, self.runtime(rt), slack)


def run_ba_x(ba, cfg, jobs_by_trace, offsets):
    """cfg keys: tag, arms, fc_src {'lgbm': (dir, model)}, slacks, seed, reps, n_jobs, outdir (npz per BA, daily arrays),
    shift_h (clock shift of arrivals, default 0), dump_dir + dump_S (job-level dump), noise_table (csv path), ln {trace: (mu, sd)},
    shift_tag (npz sub-directory handled by the caller via outdir)."""
    origin, ci, usable, _ = sim.load_ba(ba, cfg["tag"])
    cum_ci = sc.cum_hours(ci)
    off = offsets[ba]
    arms = cfg["arms"]
    need_fc = any(x.split("|")[0].startswith("lgbm") for x in arms if "|" in x)
    fcs = {"lgbm": sim.load_fc(cfg["fc_src"]["lgbm"][0], cfg["fc_src"]["lgbm"][1], ba, origin)} if need_fc else {}
    q25b = trailing_q25(ci) if "thresh" in arms else None
    nsig = {}
    if any(x.split("|")[0].startswith("noisy") for x in arms if "|" in x):
        tab = pd.read_csv(cfg["noise_table"])
        tab = tab[tab["ba"] == ba]
        for v in ("noisy", "noisy96"):
            nsig[v] = sigma_vectors(tab, v)
    shift = float(cfg.get("shift_h", 0.0))
    for trace, jobs in jobs_by_trace.items():
        res = {}
        dump = {}
        for rep in range(cfg["reps"]):
            rng = np.random.default_rng([cfg["seed"], rep, zlib.crc32(ba.encode()), zlib.crc32(trace.encode())])
            nj = len(jobs["r_act_h"])
            idx = np.sort(rng.choice(nj, size=min(cfg["n_jobs"], nj), replace=False))
            J = {k: np.asarray(v[idx]) for k, v in jobs.items()}
            a, ok = sim.place_jobs(J, C.PERIOD, origin, off, rng, usable)
            J, a = {k: v[ok] for k, v in J.items()}, a[ok]
            if shift:
                a = a + shift                                       # local clock shift, weekday rolls with the clock
                ok2 = window_ok(a, usable)
                J, a = {k: v[ok2] for k, v in J.items()}, a[ok2]
            r_act = J["r_act_h"]
            p_kw = J["power_kw"]
            day = np.floor(a / 24.0).astype(np.int64)
            lcls = np.searchsorted(sim.LEN_EDGES, r_act, side="right") - 1
            env = Env(cfg, ba, trace, rep, cfg["seed"], ci, cum_ci, a, J, fcs, q25b, nsig, cfg.get("ln", {}))
            for S in cfg["slacks"]:
                slack = np.full(len(a), S)
                st = {x: env.starts(x, slack) for x in arms}
                e_w = np.stack([p_kw * sc.realised(cum_ci, ci, st[x], r_act) for x in arms])
                e_u = np.stack([sc.realised(cum_ci, ci, st[x], r_act) / r_act for x in arms])
                delay = np.stack([st[x] - a for x in arms])
                res[(rep, S)] = {"day": day, "lcls": lcls, "e_w": e_w.astype("float32"), "e_u": e_u.astype("float32"),
                                 "delay": delay.astype("float32"), "energy_kwh": (p_kw * r_act).astype("float32")}
                if cfg.get("dump_dir") and S == cfg["dump_S"]:
                    d = dump.setdefault("rep", []), dump.setdefault("a", []), dump.setdefault("e_w", []), dump.setdefault("delay", [])
                    d[0].append(np.full(len(a), rep, np.int8))
                    d[1].append(a)
                    d[2].append(e_w.astype("float32"))
                    d[3].append(delay.astype("float32"))
                    for k in ("r_act_h", "r_req_h", "r_pred_h", "power_kw", "submit_local_hour", "submit_local_dow", "user"):
                        if k in J:
                            dump.setdefault(k, []).append(np.asarray(J[k]))
            del env
        d = os.path.join(cfg["outdir"], trace)
        os.makedirs(d, exist_ok=True)
        flat = {}
        for kk, v in C.aggregate_arms(res, len(arms)).items():
            for k2, vv in v.items():
                flat[f"{kk}__{k2}"] = vv
        np.savez_compressed(os.path.join(d, f"{ba}.npz"), arms=np.array(arms), **flat)
        if dump:
            dd = os.path.join(cfg["dump_dir"], trace)
            os.makedirs(dd, exist_ok=True)
            out = {"arms": np.array(arms), "origin_ns": np.array([origin.value]), "offset_h": np.array([off])}
            for k, v in dump.items():
                out[k] = np.concatenate(v, axis=-1) if k in ("e_w", "delay") else np.concatenate(v)
            np.savez_compressed(os.path.join(dd, f"{ba}.npz"), **out)
        del res, dump
    return ba, C.peak_rss_mb()


def run_x(ctx, cfg, jobs_by_trace, bas, workers=3):
    """run_ba_x over BAs with at most 3 worker processes."""
    from joblib import Parallel, delayed
    workers = min(workers, 3)
    offsets = sim.ba_offsets()
    t0 = time.time()
    out = Parallel(n_jobs=workers, verbose=0)(delayed(run_ba_x)(ba, cfg, jobs_by_trace, offsets) for ba in bas)
    ctx.peak_workers_mb = max(ctx.peak_workers_mb, max(p for _, p in out))
    ctx.log(f"simulated {len(bas)} BAs x {len(jobs_by_trace)} traces x {cfg['reps']} reps, arms {len(cfg['arms'])}, in "
            f"{time.time() - t0:.0f} s; worker peak RSS {ctx.peak_workers_mb:.0f} MB")


# ------------------------------------------------------------------------------------------ analysis
def analyse_x(simdir, trace, weight, contrasts, B=2000, seed=7, S=12, per_ba_means=False):
    """Frozen block bootstrap (fixed BA set, seed seed+S) for every arm and for free-form contrasts
    {name: (plus_arms, minus_arms)} = sum(savings plus) - sum(savings minus).  No p-values (exploratory)."""
    arms, data = C.load_sim(simdir, trace, weight)
    idx, point, boot, per_b, W = an.bootstrap(arms, data, S, B, seed + S, "fixed")
    out = {"trace": trace, "weight": weight, "n_ba": len(data), "B": B, "S": S,
           "savings": {a: float(point[idx[a]]) for a in arms},
           "savings_ci95": {a: [float(np.quantile(boot[:, idx[a]], 0.025)), float(np.quantile(boot[:, idx[a]], 0.975))] for a in arms},
           "contrasts": {}}
    for name, spec in contrasts.items():
        pl, mi = spec[0], spec[1]
        sc_ = spec[2] if len(spec) > 2 else 1.0
        if not (set(pl) | set(mi)) <= set(arms):
            continue
        est = float(an.contrast(point, idx, pl, mi)) * sc_
        bc = an.contrast(boot, idx, pl, mi) * sc_
        out["contrasts"][name] = {"est": est, "ci95": [float(np.quantile(bc, 0.025)), float(np.quantile(bc, 0.975))]}
    if per_ba_means:
        pb = {}
        for pl_name, spec in contrasts.items():
            pl, mi = spec[0], spec[1]
            if (set(pl) | set(mi)) <= set(arms):
                v = np.array([float(an.contrast(per_b[b], idx, pl, mi)) for b in sorted(per_b)])
                pb[pl_name] = {"mean": float(v.mean()), "median": float(np.median(v)), "n": int(len(v))}
        out["per_ba"] = pb
    return out


def rows_x(sid, out, prefix=""):
    """Ledger rows: sens.<sid>.<trace>.<weight>.S<S>.<prefix>saving[_lo|_hi].<arm> and contrast.<name>.{est,lo,hi}."""
    k0 = f"sens.{sid}.{out['trace']}.{out['weight']}.S{out['S']}.{prefix}"
    rows = [(f"sens.{sid}.{out['trace']}.{out['weight']}.n_ba", out["n_ba"])]
    for a, v in out["savings"].items():
        lo, hi = out["savings_ci95"][a]
        rows += [(f"{k0}saving.{a}", v), (f"{k0}saving_lo.{a}", lo), (f"{k0}saving_hi.{a}", hi)]
    for n, c in out["contrasts"].items():
        rows += [(f"{k0}contrast.{n}.est", c["est"]), (f"{k0}contrast.{n}.lo", c["ci95"][0]), (f"{k0}contrast.{n}.hi", c["ci95"][1])]
    for n, c in out.get("per_ba", {}).items():
        rows += [(f"{k0}perba.{n}.mean", c["mean"]), (f"{k0}perba.{n}.median", c["median"])]
    return rows


def dump_item_header(ctx, seeds, extra_inputs=()):
    ctx.header(seeds, ["data/derived/jobs.parquet", "data/derived/ci_clean.parquet"] + list(extra_inputs))
    for f in ("P4_PLAN_AMEND", "P4_PLAN_X"):
        ctx.log(f"{f}.md md5: " + C.md5_file(os.path.join(ROOT, "research", f + ".md")))
    ctx.log("python/numpy/pandas: " + sys.version.split()[0] + " " + np.__version__ + " " + pd.__version__)


def verify_plans():
    for f in ("P4_PLAN_AMEND", "P4_PLAN_X", "PANEL_DECISIONS"):
        want = open(os.path.join(ROOT, "research", f + ".md5")).read().split()[0]
        if want != C.md5_file(os.path.join(ROOT, "research", f + ".md")):
            sys.exit(f"research/{f}.md changed after its md5 was written")
    return C.verify_frozen()


def mean_delay(simdir, trace, S):
    """Job-weighted mean start delay (hours) per arm over all BAs and replicates at slack S."""
    import glob
    tot, n, arms = None, 0.0, None
    for f in sorted(glob.glob(os.path.join(simdir, trace, "*.npz"))):
        z = np.load(f)
        arms = list(z["arms"])
        for k in z.files:
            if k.endswith(f"_S{S}__delay"):
                d = z[k].sum(axis=(1, 2))
                cnt = z[k[:-len("delay")] + "n"].sum()
                tot = d if tot is None else tot + d
                n += cnt
    return {a: float(v / n) for a, v in zip(arms, tot)} if tot is not None else {}


def runtime_stats(jobs_trace, rts):
    """Accuracy of runtime estimates on the filtered job pool: share under-estimated (R_hat < R_act), median and RMS of
    log(R_hat / R_act).  rts: names among req, pred, pad, q."""
    key = {"req": "r_req_h", "pred": "r_pred_h", "pad": "r_pad", "q": "r_q"}
    ra = jobs_trace["r_act_h"]
    out = {}
    for r in rts:
        rh = np.asarray(jobs_trace[key[r]])
        pos = rh > 0                                    # a zero estimate (user history of zero-length jobs) has no log
        lr = np.log(rh[pos] / ra[pos])
        out[r] = {"share_zero_estimate": float(1 - pos.mean()), "share_under": float(np.mean(rh < ra)), "median_log": float(np.median(lr)),
                  "rms_log": float(np.sqrt(np.mean(lr ** 2))), "sd_log": float(np.std(lr)), "mean_log": float(np.mean(lr))}
    return out


def std_parser(desc):
    import argparse
    ap = argparse.ArgumentParser(description=desc)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--bas", default="")
    ap.add_argument("--n-jobs", type=int, default=20000)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--seed", type=int, default=20261111)
    ap.add_argument("--traces", default="PM100,FDATA,KIT_FH2")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--B", type=int, default=2000)
    return ap


def run_standard(ctx, args, arms, contrasts, variants=None, jobs_user=False, slacks=(12.0,), cfg_extra=None,
                 weights=("w", "u"), jobs=None):
    """Simulate (per variant) and analyse; returns ledger rows and {(label, trace, w, S): analysis dict}."""
    bas = C.eligible_bas(args.bas.split(",") if args.bas else None)
    traces = args.traces.split(",")
    if jobs is None:
        jobs = load_jobs_x(user=jobs_user, traces=traces, log=ctx.log)
    rows, outs = [], {}
    for label, over in (variants or {"": {}}).items():
        cfg = dict(tag="", arms=arms, slacks=tuple(slacks), seed=args.seed, reps=args.reps, n_jobs=args.n_jobs,
                   fc_src={"lgbm": ("data/derived/forecasts", "lgbm")}, outdir=ctx.simdir(label) if label else ctx.simdir())
        cfg.update(cfg_extra or {})
        cfg.update(over)
        run_x(ctx, cfg, jobs, bas, args.workers)
        for trace in traces:
            for S in slacks:
                for w in weights:
                    out = analyse_x(cfg["outdir"], trace, w, contrasts, B=args.B, seed=7, S=int(S))
                    outs[(label, trace, w, int(S))] = out
                    rows += rows_x(ctx.sid, out, prefix=(label + "." if label else ""))
                    if w == "w":
                        md = mean_delay(cfg["outdir"], trace, int(S))
                        k0 = f"sens.{ctx.sid}.{trace}.w.S{int(S)}.{label + '.' if label else ''}"
                        rows += [(f"{k0}meandelay_h.{a}", v) for a, v in md.items()]
                        ctx.log(f"{ctx.sid} {label} {trace} w S{int(S)}: " +
                                "; ".join(f"{a} {100 * v:.2f} %" for a, v in out["savings"].items() if a != "runnow"))
    return rows, outs, jobs


def finish_item(ctx, rows, smoke):
    C.write_ledger(ctx, rows, f"sens.{ctx.sid}.")
    ctx.log("ledger " + ctx.ledger_path())
    ctx.footer()
    if not smoke:
        open(ctx.done_path(), "w").write("done\n")
