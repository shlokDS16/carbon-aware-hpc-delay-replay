"""Shared helpers for the post-freeze exploratory sensitivities S1-S5 (research/P4_PLAN.md, v2 SETTINGS).

Frozen modules are IMPORTED, never edited: simcore, simulate, analyze, forecast, prep_jobs (md5 checked against
research/PREREG.md line 4 before every run).  Functions copied with minimal changes carry a comment naming the source.

Context: `Ctx(smoke=True)` redirects every output to results/_smoke_sens/ and logs/smoke_*.log, so a smoke test can
never create a ledger that the queue runner would treat as a finished item.
"""
import ctypes
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import zlib

import numpy as np
import pandas as pd

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
if SRC not in sys.path:
    sys.path.insert(0, SRC)
os.environ["PYTHONPATH"] = SRC + os.pathsep + os.environ.get("PYTHONPATH", "")   # joblib/loky workers import this module

import simcore as sc          # noqa: E402  (frozen)
import simulate as sim        # noqa: E402  (frozen)
import analyze as an          # noqa: E402  (frozen)

FROZEN = ("simcore", "simulate", "analyze", "forecast", "prep_jobs")
PERIOD = "TEST"
MARGIN = sim.MARGIN_H
SLACKS = sim.SLACKS
HP = sc.HP


# ---------------------------------------------------------------- housekeeping
def md5_file(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def frozen_md5():
    return {m: md5_file(os.path.join(SRC, m + ".py")) for m in FROZEN}


def verify_frozen():
    """Frozen code md5 must equal the values in research/PREREG.md line 4; the P4 plan md5 must match its file."""
    line = open(os.path.join(ROOT, "research", "PREREG.md"), encoding="utf-8").read().splitlines()[3]
    want = dict(re.findall(r"`src/(\w+)\.py` ([0-9a-f]{32})", line))
    got = frozen_md5()
    bad = {m: (want.get(m), got[m]) for m in FROZEN if want.get(m) != got[m]}
    if bad:
        sys.exit(f"frozen code changed: {bad}")
    plan = open(os.path.join(ROOT, "research", "P4_PLAN.md5")).read().split()[0]
    if plan != md5_file(os.path.join(ROOT, "research", "P4_PLAN.md")):
        sys.exit("research/P4_PLAN.md changed after its md5 was written")
    return got


def peak_rss_mb():
    """Peak working set of this process (Windows), MB."""
    class PMC(ctypes.Structure):
        _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
                    ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
    try:
        k32, ps = ctypes.windll.kernel32, ctypes.windll.psapi
        k32.GetCurrentProcess.restype = ctypes.c_void_p
        ps.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(PMC), ctypes.c_ulong]
        c = PMC()
        c.cb = ctypes.sizeof(c)
        ps.GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(c), c.cb)
        return c.PeakWorkingSetSize / 1e6
    except Exception:
        import psutil
        return psutil.Process().memory_info().rss / 1e6


class Ctx:
    """Output locations for one sensitivity item; smoke=True redirects everything under results/_smoke_sens."""

    def __init__(self, sid, smoke=False):
        self.sid, self.smoke = sid, smoke
        self.res = os.path.join(ROOT, "results", "_smoke_sens") if smoke else os.path.join(ROOT, "results")
        self.tab = self.res if smoke else os.path.join(ROOT, "tables")
        self.logf = os.path.join(ROOT, "logs", ("smoke_" if smoke else "sens_") + sid + ".log")
        os.makedirs(self.res, exist_ok=True)
        os.makedirs(os.path.join(ROOT, "logs"), exist_ok=True)
        self.peak_workers_mb = 0.0
        self.t0 = time.time()

    def simdir(self, *parts):
        return os.path.join(self.res, f"sim_TEST_sens_{self.sid}", *parts)

    def analysis_path(self, trace, weight, extra=""):
        return os.path.join(self.res, f"analysis_TEST_sens_{self.sid}{extra}_{trace}_{weight}.json")

    def ledger_path(self):
        return os.path.join(self.tab, f"ledger_TEST_sens_{self.sid}.csv")

    def done_path(self):
        return os.path.join(ROOT, "logs", f"sens_{self.sid}{'_smoke' if self.smoke else ''}.done")

    def log(self, msg):
        line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
        print(line, flush=True)
        with open(self.logf, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def header(self, seeds, inputs):
        """Command, seeds, code md5s, input md5s, start time."""
        self.log("START " + self.sid + " smoke=" + str(self.smoke))
        self.log("command: " + " ".join([sys.executable] + sys.argv))
        self.log("seeds: " + str(seeds))
        self.log("code md5 (frozen): " + json.dumps(frozen_md5()))
        new = {os.path.basename(p): md5_file(p) for p in glob.glob(os.path.join(SRC, "sens_*.py"))}
        self.log("code md5 (sens): " + json.dumps(new))
        self.log("input md5: " + json.dumps({p: md5_file(os.path.join(ROOT, p)) for p in inputs}))
        self.log("P4_PLAN.md md5: " + md5_file(os.path.join(ROOT, "research", "P4_PLAN.md")))

    def footer(self):
        mine = peak_rss_mb()
        self.log(f"END {self.sid} elapsed {time.time() - self.t0:.0f} s; peak RSS main {mine:.0f} MB; "
                 f"peak RSS worker (max) {self.peak_workers_mb:.0f} MB")
        return mine, self.peak_workers_mb


def write_ledger(ctx, rows, replace_prefix):
    """rows: list of (key, value). Rows whose key starts with replace_prefix are replaced; others kept."""
    fn = ctx.ledger_path()
    new = pd.DataFrame(rows, columns=["key", "value"])
    new["source"] = new["key"].map(lambda k: f"results/analysis_TEST_sens_{ctx.sid}*.json" if ".saving." in k or ".H" in k
                                   else f"results/sim_TEST_sens_{ctx.sid}")
    if os.path.exists(fn):
        old = pd.read_csv(fn)
        new = pd.concat([old[~old["key"].str.startswith(replace_prefix)], new], ignore_index=True)
    new.to_csv(fn, index=False)


# ---------------------------------------------------------------- jobs
def load_jobs(states="COMPLETED", traces=None, jobs="data/derived/jobs.parquet", user=False):
    """Copy of the filter block in simulate.main (same filters and columns). Returns {trace: {col: array}}.
    user=True adds integer-coded `user` per trace (for the S1 cluster bootstrap)."""
    cols = ["trace", "state", "r_act_h", "r_req_h", "r_pred_h", "power_w", "submit_local_dow", "submit_local_hour"]
    if user:
        cols.append("user")
    flt = [("state", "in", states.split(","))]
    if traces:
        flt.append(("trace", "in", list(traces)))
    df = pd.read_parquet(os.path.join(ROOT, jobs), columns=cols, filters=flt)
    df = df[(df["r_act_h"] >= 1 / 60) & (df["r_req_h"] <= sim.MAX_REQ_H) & (df["r_req_h"] > 0)]
    assert df["r_act_h"].max() <= sim.MAX_REQ_H, "actual runtime beyond 72 h would leave the 98 h checked window"
    df = df.assign(power_kw=(df["power_w"] / 1000.0).fillna(1.0))
    tr = sorted(df["trace"].unique()) if not traces else list(traces)
    keep = ["r_act_h", "r_req_h", "r_pred_h", "power_kw", "submit_local_dow", "submit_local_hour"]
    out = {}
    for t in tr:
        m = (df["trace"] == t).to_numpy()
        d = {c: df.loc[m, c].to_numpy() for c in keep}
        if user:
            d["user"] = pd.factorize(df.loc[m, "user"])[0].astype(np.int64)
        out[t] = d
    return out


# ---------------------------------------------------------------- generic simulation (copy of simulate.run_ba)
def fc_window_lat(first_k, fc_arr, a, k):
    """Planner window of a forecast issued k hours before floor(a) (data latency k): row floor(a)-k, leads shifted by k
    (leads k+1..96 give intervals 0..95-k; the remaining intervals hold the lead-96 value, as in simulate.fc_window).
    k = 0 reproduces simulate.fc_window exactly."""
    rows = np.floor(a).astype(np.int64) - k - first_k
    assert rows.min() >= 0 and rows.max() < len(fc_arr), "arrival outside forecast span"
    w = fc_arr[rows][:, k:].astype("float64")
    pad = np.repeat(w[:, -1:], sc.HP - w.shape[1], axis=1)
    return np.concatenate([w, pad], axis=1)


def aggregate_arms(res, n_arms):
    """Copy of simulate.aggregate with the arm count as a parameter."""
    agg = {}
    for (rep, S), r in res.items():
        d0 = r["day"].min()
        nd = r["day"].max() - d0 + 1
        nc = len(sim.LEN_EDGES) - 1
        flat = (r["day"] - d0) * nc + r["lcls"]
        ew, eu, dl = (np.zeros((n_arms, nd * nc)) for _ in range(3))
        for i in range(n_arms):
            ew[i] = np.bincount(flat, weights=r["e_w"][i], minlength=nd * nc)
            eu[i] = np.bincount(flat, weights=r["e_u"][i], minlength=nd * nc)
            dl[i] = np.bincount(flat, weights=r["delay"][i], minlength=nd * nc)
        cnt = np.bincount(flat, minlength=nd * nc)
        en = np.bincount(flat, weights=r["energy_kwh"], minlength=nd * nc)
        agg[f"r{rep}_S{int(S)}"] = dict(day0=d0, e_w=ew.reshape(n_arms, nd, nc), e_u=eu.reshape(n_arms, nd, nc),
                                       delay=dl.reshape(n_arms, nd, nc), n=cnt.reshape(nd, nc),
                                       energy=en.reshape(nd, nc))
    return agg


def run_ba_generic(ba, cfg, jobs_by_trace, offsets):
    """Arm-subset version of simulate.run_ba. cfg keys:
      tag        CI tag (ci_clean<tag>.parquet)         arms     list of 'runnow' | '<signal>|<runtime>'
      fc_src     {signal: (fc_dir, model_name)}          slacks   tuple of slack hours
      ks         data latencies in hours (default (0,))  outdir   {k: directory} for the npz files
      seed, reps, n_jobs                                 cum      optional {trace: cumulative job multiplicity} (S1)
      seed_by_trace optional {trace: seed}
    RNG consumption is identical to simulate.run_ba (choice, then place_jobs), so with ks=(0,) and the frozen seed the
    jobs and alignment equal the frozen run. Returns (ba, peak RSS MB of this process)."""
    origin, ci, usable, utc = sim.load_ba(ba, cfg["tag"])
    cum_ci = sc.cum_hours(ci)
    off = offsets[ba]
    arms = cfg["arms"]
    ks = cfg.get("ks", (0,))
    fc_sigs = sorted({a.split("|")[0] for a in arms if "|" in a} - {"oracle"})
    fcs = {s: sim.load_fc(cfg["fc_src"][s][0], cfg["fc_src"][s][1], ba, origin) for s in fc_sigs}
    for trace, jobs in jobs_by_trace.items():
        res = {k: {} for k in ks}
        for rep in range(cfg["reps"]):
            seed = cfg.get("seed_by_trace", {}).get(trace, cfg["seed"])
            rng = np.random.default_rng([seed, rep, zlib.crc32(ba.encode()), zlib.crc32(trace.encode())])
            nj = len(jobs["r_act_h"])
            if cfg.get("cum") is not None:     # S1: jobs drawn from the user-resampled pool
                cm = cfg["cum"][trace]
                tot = int(cm[-1])
                pos = rng.choice(tot, size=min(cfg["n_jobs"], tot), replace=False)
                idx = np.sort(np.searchsorted(cm, pos, side="right"))
            else:
                idx = np.sort(rng.choice(nj, size=min(cfg["n_jobs"], nj), replace=False))
            J = {k: np.asarray(v[idx]) for k, v in jobs.items() if k != "user"}
            a, ok = sim.place_jobs(J, PERIOD, origin, off, rng, usable)
            J, a = {k: v[ok] for k, v in J.items()}, a[ok]
            r_act = J["r_act_h"]
            r_est = {"act": r_act, "req": J["r_req_h"], "pred": J["r_pred_h"]}
            p_kw = J["power_kw"]
            day = np.floor(a / 24.0).astype(np.int64)
            lcls = np.searchsorted(sim.LEN_EDGES, r_act, side="right") - 1
            sig_or = sc.window_signal_actual(ci, a)
            for S in cfg["slacks"]:
                slack = np.full(len(a), S)
                base = {"runnow": a}
                for arm in arms:
                    if arm.startswith("oracle|"):
                        base[arm] = sc.plan_start(sig_or, a, r_est[arm.split("|")[1]], slack)
                for k in ks:
                    starts = dict(base)
                    for s in fc_sigs:
                        sg = fc_window_lat(*fcs[s], a, k)
                        for arm in arms:
                            if arm.startswith(s + "|"):
                                starts[arm] = sc.plan_start(sg, a, r_est[arm.split("|")[1]], slack)
                        del sg
                    e_w = np.stack([p_kw * sc.realised(cum_ci, ci, starts[x], r_act) for x in arms])
                    e_u = np.stack([sc.realised(cum_ci, ci, starts[x], r_act) / r_act for x in arms])
                    delay = np.stack([starts[x] - a for x in arms])
                    res[k][(rep, S)] = {"day": day, "lcls": lcls, "e_w": e_w.astype("float32"),
                                        "e_u": e_u.astype("float32"), "delay": delay.astype("float32"),
                                        "energy_kwh": (p_kw * r_act).astype("float32")}
        for k in ks:
            d = os.path.join(cfg["outdir"][k], trace)
            os.makedirs(d, exist_ok=True)
            flat = {}
            for kk, v in aggregate_arms(res[k], len(arms)).items():
                for k2, vv in v.items():
                    flat[f"{kk}__{k2}"] = vv
            np.savez_compressed(os.path.join(d, f"{ba}.npz"), arms=np.array(arms), **flat)
        del res
    return ba, peak_rss_mb()


def run_generic(ctx, cfg, jobs_by_trace, bas, workers=3):
    """Run run_ba_generic over BAs with at most `workers` processes (never more than 3)."""
    from joblib import Parallel, delayed
    workers = min(workers, 3)
    offsets = sim.ba_offsets()
    t0 = time.time()
    out = Parallel(n_jobs=workers, verbose=0)(delayed(run_ba_generic)(ba, cfg, jobs_by_trace, offsets) for ba in bas)
    ctx.peak_workers_mb = max(ctx.peak_workers_mb, max(p for _, p in out))
    ctx.log(f"simulated {len(bas)} BAs x {len(jobs_by_trace)} traces in {time.time() - t0:.0f} s; "
            f"worker peak RSS {ctx.peak_workers_mb:.0f} MB")


def eligible_bas(smoke_bas=None):
    el = pd.read_csv(os.path.join(ROOT, "tables", "ba_eligibility.csv"))
    bas = sorted(el[el["eligible"]]["ba"])
    return smoke_bas if smoke_bas else bas


# ---------------------------------------------------------------- analysis (mirror of analyze.main)
def load_sim(simdir, trace, weight):
    """Copy of analyze.load with the directory as parameter."""
    files = sorted(glob.glob(os.path.join(simdir, trace, "*.npz")))
    data, arms = {}, None
    for f in files:
        z = np.load(f)
        arms = list(z["arms"])
        per_s = {}
        for S in an.SLACKS:
            mats = []
            for k in z.files:
                if k.endswith(f"_S{S}__e_{weight}"):
                    pre = k[: -len(f"__e_{weight}")]
                    mats.append((int(z[pre + "__day0"]), z[k].sum(axis=2)))
            if not mats:
                continue
            d_min = min(d0 for d0, _ in mats)
            d_max = max(d0 + m.shape[1] for d0, m in mats)
            acc = np.zeros((mats[0][1].shape[0], d_max - d_min))
            for d0, m in mats:
                acc[:, d0 - d_min: d0 - d_min + m.shape[1]] += m
            per_s[S] = acc
        data[os.path.basename(f)[:-4]] = per_s
    return arms, data


def analyse(simdir, trace, weight, B=2000, seed=7, F="lgbm", slacks=an.SLACKS, per_ba=True):
    """Mirror of analyze.main for one trace/weight (same bootstrap, null-centred p, Holm, Shapley, per-BA H2), tolerant of
    arm subsets: a test or Shapley term is computed only if all its arms are present."""
    arms, data = load_sim(simdir, trace, weight)
    have = set(arms)
    confirm = ("H1_deployable_saving", "H2_runtime_penalty", "H3_prediction_recovery")
    tests = {"H1_deployable_saving": ([f"{F}|req"], ["runnow"], "greater"),
             "H2_runtime_penalty": ([f"{F}|act"], [f"{F}|req"], "greater"),
             "H3_prediction_recovery": ([f"{F}|pred"], [f"{F}|req"], "greater"),
             "H4_interaction": (["oracle|act", f"{F}|req"], ["oracle|req", f"{F}|act"], "two")}
    tests = {n: v for n, v in tests.items() if set(v[0]) | set(v[1]) <= have}
    conf = [n for n in confirm if n in tests]
    out = {"period": PERIOD, "trace": trace, "weight": weight, "n_ba": len(data), "B": B, "boot": "fixed", "slacks": {}}
    for S in slacks:
        if any(S not in data[b] for b in data):
            continue
        idx, point, boot, per_b, W = an.bootstrap(arms, data, S, B, seed + S, "fixed")
        rs = {"savings": {a: float(point[idx[a]]) for a in arms},
              "savings_ci95": {a: [float(np.quantile(boot[:, idx[a]], 0.025)),
                                   float(np.quantile(boot[:, idx[a]], 0.975))] for a in arms}}
        tres = {}
        for name, (pl, mi, side) in tests.items():
            est = float(an.contrast(point, idx, pl, mi))
            bc = an.contrast(boot, idx, pl, mi)
            dev = bc - est
            p = (1 + np.sum(dev >= est)) / (1 + len(bc)) if side == "greater" else \
                (1 + np.sum(np.abs(dev) >= abs(est))) / (1 + len(bc))
            tres[name] = {"est": est, "ci95": [float(np.quantile(bc, 0.025)), float(np.quantile(bc, 0.975))],
                          "p": float(p), "p_holm": None}
        if conf:
            adj = an.holm(np.array([tres[n]["p"] for n in conf]))
            for n, a in zip(conf, adj):
                tres[n]["p_holm"] = float(a)
        rs["tests"] = tres
        if {"oracle|act", "oracle|req", f"{F}|act", f"{F}|req"} <= have:
            o_a, o_r, f_a, f_r = (point[idx[k]] for k in ("oracle|act", "oracle|req", f"{F}|act", f"{F}|req"))
            rs["shapley"] = {"gap": float(o_a - f_r), "forecast": float(0.5 * ((o_a - f_a) + (o_r - f_r))),
                             "runtime": float(0.5 * ((o_a - o_r) + (f_a - f_r))),
                             "interaction": float((o_a - o_r) - (f_a - f_r)),
                             "retained_share": float(f_r / o_a) if o_a else None}
        else:
            rs["shapley"] = {}
        cnt = {"n": 0, "pos": 0, "sig": 0}
        if per_ba and {f"{F}|act", f"{F}|req"} <= have:
            for j, (b, w) in enumerate(zip(sorted(data), W)):
                bb = an.per_ba_boot(w, idx, 500, seed + 100 + j)
                d = an.contrast(bb, idx, [f"{F}|act"], [f"{F}|req"])
                e = float(an.contrast(per_b[b], idx, [f"{F}|act"], [f"{F}|req"]))
                cnt["n"] += 1
                cnt["pos"] += int(e > 0)
                cnt["sig"] += int(np.quantile(d, 0.025) > 0)
        rs["per_ba_H2_counts"] = cnt
        out["slacks"][str(S)] = rs
    return out


def ledger_rows(sid, out, name_prefix=""):
    """Rows (key, value) with key sens.<sid>.<trace>.<weight>.S<S>.<name_prefix><name>."""
    rows = [(f"sens.{sid}.{out['trace']}.{out['weight']}.n_ba", out["n_ba"])]
    for S, r in out["slacks"].items():
        k0 = f"sens.{sid}.{out['trace']}.{out['weight']}.S{S}.{name_prefix}"
        for a, v in r["savings"].items():
            lo, hi = r["savings_ci95"][a]
            rows += [(f"{k0}saving.{a}", v), (f"{k0}saving_lo.{a}", lo), (f"{k0}saving_hi.{a}", hi)]
        for n, t in r["tests"].items():
            rows += [(f"{k0}{n}.est", t["est"]), (f"{k0}{n}.lo", t["ci95"][0]), (f"{k0}{n}.hi", t["ci95"][1]),
                     (f"{k0}{n}.p", t["p"])]
            if t["p_holm"] is not None:
                rows.append((f"{k0}{n}.p_holm", t["p_holm"]))
        for k, v in r["shapley"].items():
            rows.append((f"{k0}shapley.{k}", v))
        for k, v in r["per_ba_H2_counts"].items():
            rows.append((f"{k0}perba_H2.{k}", v))
    return rows


def run_polled(args, cwd=ROOT, stdout_path=None):
    """Run a (frozen) script unchanged as a subprocess and poll psutil for the peak working set of the process tree.
    Returns (returncode, peak_single_process_MB, peak_tree_total_MB)."""
    import psutil
    cmd = [sys.executable] + list(args)
    out = open(stdout_path, "a", encoding="utf-8") if stdout_path else subprocess.DEVNULL
    p = subprocess.Popen(cmd, cwd=cwd, stdout=out, stderr=subprocess.STDOUT)
    pk_one = pk_tree = 0.0
    root = psutil.Process(p.pid)
    while p.poll() is None:
        try:
            procs = [root] + root.children(recursive=True)
            rss = []
            for q in procs:
                try:
                    rss.append(q.memory_info().rss / 1e6)
                except psutil.Error:
                    pass
            if rss:
                pk_one, pk_tree = max(pk_one, max(rss)), max(pk_tree, sum(rss))
        except psutil.Error:
            pass
        time.sleep(1.0)
    if stdout_path:
        out.close()
    return p.returncode, pk_one, pk_tree
