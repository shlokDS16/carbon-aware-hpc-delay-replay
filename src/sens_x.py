"""Exploratory items X1-X7 (research/P4_PLAN_X.md, binding), post-freeze, new code only.  --item x1 ... x7   (X8 is NOT run)

x1  runtime-estimate sweep: R_hat = R_act x m, m in {0.25, 0.5, 1 (= act), 2, 4, 8}; log-normal noise variants with the SD of
    log(R_req / R_act) of the filtered job pool (ln: zero-mean; lnmu: also the pool's mean log ratio); signals oracle and lgbm,
    S = 12 h, three traces; req and pred marked.  (The DEV and TEST replays draw the identical 20,000 jobs per BA, so the pool
    SD uses no TEST-period information.)
x2  injected noise vs real forecast: signal = actual x (1 + eps), eps ~ N(0, sigma_l), sigma_l per BA and lead fitted on DEV so
    that the MAE equals the LightGBM MAE.  'noisy' = matched at leads 1-24 (sigma_24 held beyond; the plan's literal rule),
    'noisy96' = matched at every lead 1-96 (addition, stated).  Arms noisy|act, noisy|req (and noisy96).
x3  forecast-lead cap L in {6, 12, 24, 48, 96}: the planner sees leads <= L and holds the lead-L value beyond; lgbm|req, lgbm|act.
x4  load-concentration proxy from a start dump (arms runnow, oracle|act, lgbm|act, lgbm|req, lgbm|pred; S = 12 h): hourly job
    power per BA, peak-to-mean, 99th percentile and exceedance per arm relative to run-now.  NOT a queue simulation.
x5  concentration of the runtime penalty (H2) by decile of R_act/R_req, by R_act decile, by top users; per-BA mean and median
    beside the pooled estimate.  Uses the x4 dump (job-level).
x6  when the saving accrues: by local arrival hour, weekday and month (x4 dump; BA-bootstrap descriptive intervals).
x7  marginal-like proxy: fossil-only intensity (lifecycle-weighted fossil generation per kWh of fossil generation); the same
    pipeline as S3 (clean_ci rules, frozen forecast.py refit unchanged) so lgbm arms are included when the refit works;
    otherwise oracle arms only (stated in the log).  Labelled 'proxy, not a marginal estimate'.
Usage: py src/sens_x.py --item x1 [--smoke --bas CISO,ERCO --n-jobs 2000 --reps 1 --B 50]
Outputs: results/sim_TEST_sens_<id>/, tables/ledger_TEST_sens_<id>.csv, logs/sens_<id>.log
"""
import glob
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sens_xcommon as X  # noqa: E402
C = X.C

MULTS = [0.25, 0.5, 2, 4, 8]
LS = [6, 12, 24, 48]
DUMP_ARMS = ["runnow", "oracle|act", "lgbm|act", "lgbm|req", "lgbm|pred"]
H2 = (["lgbm|act"], ["lgbm|req"])


# ------------------------------------------------------------------------------------------------------ x1
def item_x1(ctx, args):
    traces = args.traces.split(",")
    jobs = X.load_jobs_x(traces=traces, log=ctx.log)
    ln = {}
    for t in traces:
        lr = np.log(jobs[t]["r_req_h"] / jobs[t]["r_act_h"])
        ln[t] = (float(lr.mean()), float(lr.std()))
        ctx.log(f"x1 {t}: log(R_req/R_act) mean {ln[t][0]:.3f} sd {ln[t][1]:.3f} (pool of {len(lr)} filtered jobs)")
    arms = ["runnow", "oracle|act", "oracle|req", "oracle|pred", "lgbm|act", "lgbm|req", "lgbm|pred"]
    for sig in ("oracle", "lgbm"):
        arms += [f"{sig}|m{m}" for m in MULTS] + [f"{sig}|ln", f"{sig}|lnmu"]
    contrasts = {}
    for sig in ("oracle", "lgbm"):
        contrasts[f"{sig}_ln_minus_act"] = ([f"{sig}|ln"], [f"{sig}|act"])
        contrasts[f"{sig}_req_minus_ln"] = ([f"{sig}|req"], [f"{sig}|ln"])
        contrasts[f"{sig}_pred_minus_ln"] = ([f"{sig}|pred"], [f"{sig}|ln"])
    rows, outs, _ = X.run_standard(ctx, args, arms, contrasts, cfg_extra={"ln": ln}, jobs=jobs)
    tab = []
    for t in traces:
        st = X.runtime_stats(jobs[t], ["req", "pred"])
        err = {"act": (0.0, 0.0)}
        for m in MULTS:
            err[f"m{m}"] = (float(np.log(m)), abs(float(np.log(m))))
        err["ln"] = (0.0, ln[t][1])
        err["lnmu"] = (ln[t][0], float(np.hypot(*ln[t])))
        err["req"] = (st["req"]["median_log"], st["req"]["rms_log"])
        err["pred"] = (st["pred"]["median_log"], st["pred"]["rms_log"])
        for rt, (med, rms) in err.items():
            rows += [(f"sens.x1.{t}.logerr_median.{rt}", med), (f"sens.x1.{t}.logerr_rms.{rt}", rms)]
            for sig in ("oracle", "lgbm"):
                o = outs[("", t, "w", 12)]
                arm = f"{sig}|{rt}"
                if arm in o["savings"]:
                    lo, hi = o["savings_ci95"][arm]
                    tab.append((t, sig, rt, med, rms, o["savings"][arm], lo, hi))
    df = pd.DataFrame(tab, columns=["trace", "signal", "runtime", "median_log_err", "rms_log_err", "saving_w", "lo", "hi"])
    out_csv = os.path.join(ctx.tab, "x1_runtime_sweep.csv" if not args.smoke else "x1_runtime_sweep_smoke.csv")
    df.to_csv(out_csv, index=False)
    ctx.log("table " + out_csv)
    try:
        stem = os.path.join(C.ROOT, "figures", "sens_x1_runtime_sweep") if not args.smoke else \
            os.path.join(C.ROOT, "results", "_smoke_sens", "sens_x1_runtime_sweep")
        plot_x1(df, stem)
    except Exception as e:                       # the figure is a convenience; the ledger is the record
        ctx.log("plot skipped: " + repr(e))
    return rows


def plot_x1(df, stem):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ok = {"oracle": "#0072B2", "lgbm": "#D55E00"}
    traces = list(df["trace"].unique())
    fig, axs = plt.subplots(1, len(traces), figsize=(3.2 * len(traces), 3.0))
    axs = np.atleast_1d(axs)
    for ax, t in zip(axs, traces):
        d = df[df["trace"] == t]
        for sig, col in ok.items():
            c = d[(d["signal"] == sig) & d["runtime"].str.match(r"^(act|m[0-9.]+)$")].sort_values("median_log_err")
            x = c["median_log_err"] / np.log(2)
            ax.plot(x, 100 * c["saving_w"], "-o", color=col, ms=3, label=f"{sig} signal, m x R_act")
            ax.fill_between(x, 100 * c["lo"], 100 * c["hi"], color=col, alpha=0.15, lw=0)
            for rt, mk in (("req", "s"), ("pred", "^")):
                p = d[(d["signal"] == sig) & (d["runtime"] == rt)]
                if len(p):
                    ax.plot(p["median_log_err"] / np.log(2), 100 * p["saving_w"], mk, color=col, mfc="white", ms=6)
        ax.set_title(t, fontsize=9)
        ax.set_xlabel("median log2(R_hat / R_act)", fontsize=8)
        ax.tick_params(labelsize=7)
    axs[0].set_ylabel("saving vs run-now (%)", fontsize=8)
    axs[0].legend(fontsize=6, frameon=False)
    fig.tight_layout()
    fig.savefig(stem + ".png", dpi=300)
    fig.savefig(stem + ".pdf")


# ------------------------------------------------------------------------------------------------------ x2
def item_x2(ctx, args):
    bas = C.eligible_bas(args.bas.split(",") if args.bas else None)
    tab = X.dev_noise_table(bas, ctx.log)
    path = os.path.join(ctx.tab, "x2_noise_scale_DEV.csv" if not args.smoke else "x2_noise_scale_DEV_smoke.csv")
    tab.to_csv(path, index=False)
    ctx.log(f"DEV noise-scale table {path} ({len(tab)} rows, DEV issue hours only)")
    rel = (tab["mae_noise_check_dev"] / tab["mae_lgbm_dev"] - 1).abs()
    arms = ["runnow", "oracle|act", "oracle|req", "lgbm|act", "lgbm|req", "noisy|act", "noisy|req", "noisy96|act", "noisy96|req"]
    contrasts = {"H2_lgbm": H2, "H2_noisy": (["noisy|act"], ["noisy|req"]), "H2_noisy96": (["noisy96|act"], ["noisy96|req"]),
                 "noisy_minus_lgbm_act": (["noisy|act"], ["lgbm|act"]), "noisy_minus_lgbm_req": (["noisy|req"], ["lgbm|req"]),
                 "noisy96_minus_lgbm_act": (["noisy96|act"], ["lgbm|act"]), "noisy96_minus_lgbm_req": (["noisy96|req"], ["lgbm|req"])}
    rows, outs, _ = X.run_standard(ctx, args, arms, contrasts, cfg_extra={"noise_table": path})
    rows += [("sens.x2.noise_check.max_rel_dev_mae", float(rel.max())), ("sens.x2.noise_check.mean_rel_dev_mae", float(rel.mean())),
             ("sens.x2.sigma_rel.mean_lead1", float(tab[tab.lead == 1]["sigma_rel"].mean())),
             ("sens.x2.sigma_rel.mean_lead24", float(tab[tab.lead == 24]["sigma_rel"].mean())),
             ("sens.x2.sigma_rel.mean_lead96", float(tab[tab.lead == 96]["sigma_rel"].mean()))]
    ctx.log(f"x2 injected-noise MAE vs LightGBM MAE on DEV: mean |rel dev| {rel.mean():.4f}, max {rel.max():.4f}")
    return rows


# ------------------------------------------------------------------------------------------------------ x3
def item_x3(ctx, args):
    arms = ["runnow", "oracle|act", "oracle|req", "lgbm|act", "lgbm|req"]
    contrasts = {"H2_L96": H2}
    for L in LS:
        arms += [f"lgbm@L{L}|act", f"lgbm@L{L}|req"]
        contrasts[f"H2_L{L}"] = ([f"lgbm@L{L}|act"], [f"lgbm@L{L}|req"])
        contrasts[f"req_L{L}_minus_L96"] = ([f"lgbm@L{L}|req"], ["lgbm|req"])
        contrasts[f"act_L{L}_minus_L96"] = ([f"lgbm@L{L}|act"], ["lgbm|act"])
    rows, _, _ = X.run_standard(ctx, args, arms, contrasts)
    return rows


# ------------------------------------------------------------------------------------------------------ dump (x4-x6)
def ensure_dump(ctx, args):
    c4 = C.Ctx("x4", args.smoke)
    ddir = c4.simdir("dump")
    marker = os.path.join(ddir, "DONE.txt")
    if not os.path.exists(marker):
        ctx.log("start dump not found: running the dump simulation (arms " + ", ".join(DUMP_ARMS) + ", S = 12 h)")
        traces = args.traces.split(",")
        jobs = X.load_jobs_x(user=True, traces=traces, log=ctx.log)
        bas = C.eligible_bas(args.bas.split(",") if args.bas else None)
        cfg = dict(tag="", arms=DUMP_ARMS, slacks=(12.0,), seed=args.seed, reps=args.reps, n_jobs=args.n_jobs,
                   fc_src={"lgbm": ("data/derived/forecasts", "lgbm")}, outdir=c4.simdir("daily"), dump_dir=ddir, dump_S=12.0)
        X.run_x(ctx, cfg, jobs, bas, args.workers)
        with open(marker, "w") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} reps={args.reps} n_jobs={args.n_jobs}\n")
    return ddir


def load_dump(ddir, trace):
    out = []
    for f in sorted(glob.glob(os.path.join(ddir, trace, "*.npz"))):
        z = np.load(f)
        out.append((os.path.basename(f)[:-4], {k: z[k] for k in z.files}))
    return out


def hourly_load(s, e, p, grid):
    """Mean job power (kW) in each hour [grid[i], grid[i+1]) of jobs running over [s, e] with power p (exact, piecewise linear)."""
    def cum(t_ev):
        o = np.argsort(t_ev)
        ts = t_ev[o]
        pc = np.concatenate([[0.0], np.cumsum(p[o])])
        pt = np.concatenate([[0.0], np.cumsum((p * t_ev)[o])])
        i = np.searchsorted(ts, grid, side="right")
        return pc[i] * grid - pt[i]
    return np.diff(cum(s) - cum(e))


def item_x4(ctx, args):
    ddir = ensure_dump(ctx, args)
    rows, tab = [], []
    for t in args.traces.split(","):
        per = {}
        for ba, z in load_dump(ddir, t):
            arms = list(z["arms"])
            for rep in np.unique(z["rep"]):
                m = z["rep"] == rep
                a, ra, p = z["a"][m], z["r_act_h"][m], z["power_kw"][m]
                grid = np.arange(np.floor(a.min()), np.ceil(a.max()) + 1.0)
                met = {}
                for i, arm in enumerate(arms):
                    s = a + z["delay"][i][m]
                    L = hourly_load(s, s + ra, p, grid)
                    mu = L.mean()
                    met[arm] = {"ptm": L.max() / mu, "p99m": np.quantile(L, 0.99) / mu, "frac_gt2": float(np.mean(L > 2 * mu)),
                                "max": L.max(), "p99": np.quantile(L, 0.99), "mean": mu}
                for arm in arms:
                    d = per.setdefault(arm, {})
                    for k in ("ptm", "p99m", "frac_gt2"):
                        d.setdefault(k, []).append(met[arm][k])
                    d.setdefault("max_rel", []).append(met[arm]["max"] / met["runnow"]["max"])
                    d.setdefault("p99_rel", []).append(met[arm]["p99"] / met["runnow"]["p99"])
                    d.setdefault("ptm_rel", []).append(met[arm]["ptm"] / met["runnow"]["ptm"])
                    d.setdefault("mean_rel", []).append(met[arm]["mean"] / met["runnow"]["mean"])
        for arm, d in per.items():
            for k, v in d.items():
                v = np.array(v)
                rows += [(f"sens.x4.{t}.{arm}.{k}.{st}", float(f)) for st, f in
                         (("mean", v.mean()), ("median", np.median(v)), ("p05", np.quantile(v, 0.05)), ("p95", np.quantile(v, 0.95)))]
                tab.append((t, arm, k, float(v.mean()), float(np.median(v)), float(np.quantile(v, 0.05)), float(np.quantile(v, 0.95)), len(v)))
        r = per["lgbm|req"]
        ctx.log(f"x4 {t}: lgbm|req vs run-now hourly load: peak-to-mean x{np.mean(r['ptm_rel']):.3f}, p99 x{np.mean(r['p99_rel']):.3f}, "
                f"max x{np.mean(r['max_rel']):.3f} (mean over {len(r['ptm_rel'])} BA-replicates); oracle|act p99 x{np.mean(per['oracle|act']['p99_rel']):.3f}")
    pd.DataFrame(tab, columns=["trace", "arm", "metric", "mean", "median", "p05", "p95", "n_units"]).to_csv(
        os.path.join(ctx.tab, "x4_load_concentration.csv" if not args.smoke else "x4_load_concentration_smoke.csv"), index=False)
    return rows


def gini(x):
    x = np.sort(np.asarray(x, float))
    n = len(x)
    return float((2 * np.arange(1, n + 1) - n - 1) @ x / (n * x.sum())) if x.sum() > 0 else float("nan")


def item_x5(ctx, args):
    ddir = ensure_dump(ctx, args)
    rows = []
    for t in args.traces.split(","):
        parts = load_dump(ddir, t)
        arms = list(parts[0][1]["arms"])
        i_run, i_act, i_req = arms.index("runnow"), arms.index("lgbm|act"), arms.index("lgbm|req")
        pen, ra, rq, user, erun, ba_h2 = [], [], [], [], [], []
        for ba, z in parts:
            ew = z["e_w"]
            pen.append(ew[i_req] - ew[i_act])
            erun.append(ew[i_run])
            ra.append(z["r_act_h"])
            rq.append(z["r_req_h"])
            user.append(z["user"])
            ba_h2.append((ew[i_req].sum() - ew[i_act].sum()) / ew[i_run].sum())
        pen, erun, ra, rq, user = (np.concatenate(v) for v in (pen, erun, ra, rq, user))
        P, E = pen.sum(), erun.sum()
        h2 = P / E
        k0 = f"sens.x5.{t}."
        rows += [(k0 + "h2_pooled", float(h2)), (k0 + "h2_perba_mean", float(np.mean(ba_h2))), (k0 + "h2_perba_median", float(np.median(ba_h2))),
                 (k0 + "n_jobs", len(pen)), (k0 + "n_users", int(len(np.unique(user)))),
                 (k0 + "share_jobs_penalty_positive", float(np.mean(pen > 0))),
                 (k0 + "share_penalty_from_positive_jobs", float(pen[pen > 0].sum() / P))]
        for name, v in (("ratio", ra / rq), ("ract", ra)):
            edges = np.quantile(v, np.linspace(0, 1, 11))
            b = np.clip(np.searchsorted(edges, v, side="right") - 1, 0, 9)
            for d in range(10):
                m = b == d
                rows += [(f"{k0}{name}_decile{d + 1}.penalty_share", float(pen[m].sum() / P)),
                         (f"{k0}{name}_decile{d + 1}.energy_share", float(erun[m].sum() / E)),
                         (f"{k0}{name}_decile{d + 1}.h2_within_pp", float(100 * pen[m].sum() / erun[m].sum())),
                         (f"{k0}{name}_decile{d + 1}.edge_lo", float(edges[d]))]
        pu = np.bincount(user, weights=pen)
        order = np.argsort(-pu)
        cs = np.cumsum(pu[order]) / P
        for k in (1, 5, 10, 20):
            sh = float(cs[min(k, len(cs)) - 1])
            rows += [(f"{k0}top{k}_users.penalty_share", sh), (f"{k0}top{k}_users.recovered_pp", float(100 * h2 * sh))]
        half = int(np.searchsorted(cs, 0.5) + 1)
        rows += [(k0 + "users_for_half_penalty", half), (k0 + "user_penalty_gini", gini(np.maximum(pu, 0)))]
        ctx.log(f"x5 {t}: H2 pooled {100 * h2:.2f} pp, per-BA mean {100 * np.mean(ba_h2):.2f}, median {100 * np.median(ba_h2):.2f}; "
                f"top-5 users carry {100 * cs[min(5, len(cs)) - 1]:.1f} % of the penalty; {half} users carry half")
    return rows


def item_x6(ctx, args):
    ddir = ensure_dump(ctx, args)
    rows = []
    rng = np.random.default_rng(6)
    sel = ["oracle|act", "lgbm|act", "lgbm|req", "lgbm|pred"]
    strata = {"hour": 24, "dow": 7, "month": 12}
    for t in args.traces.split(","):
        parts = load_dump(ddir, t)
        arms = list(parts[0][1]["arms"])
        names = sel + ["runnow"]
        ia = {x: arms.index(x) for x in names}
        acc = {k: np.zeros((len(parts), n, len(names))) for k, n in strata.items()}
        for j, (ba, z) in enumerate(parts):
            origin_h = z["origin_ns"][0] / 3.6e12
            lh = z["a"] + origin_h + float(z["offset_h"][0])
            hour = (np.floor(lh) % 24).astype(int)
            day = pd.to_datetime(np.floor(lh / 24).astype("int64"), unit="D")
            lab = {"hour": hour, "dow": np.asarray(day.dayofweek), "month": np.asarray(day.month) - 1}
            assert np.mean(hour == np.floor(z["submit_local_hour"] + 1e-6).astype(int)) > 0.999, "arrival clock hour mismatch"
            for k, n in strata.items():
                for q, name in enumerate(names):
                    acc[k][j, :, q] = np.bincount(lab[k], weights=z["e_w"][ia[name]], minlength=n)
        ir = names.index("runnow")
        isel = [names.index(s) for s in sel]
        for k, n in strata.items():
            A = acc[k]
            tot = A.sum(axis=0)
            tot_save = {s: tot[:, ir].sum() - tot[:, names.index(s)].sum() for s in sel}
            boots = np.empty((500, n, len(sel)))
            for b in range(500):
                T = A[rng.integers(0, len(parts), len(parts))].sum(axis=0)
                boots[b] = 1 - T[:, isel] / T[:, [ir]]
            for si in range(n):
                lab_i = si + 1 if k == "month" else si
                for q, s in enumerate(sel):
                    sav = 1 - tot[si, names.index(s)] / tot[si, ir]
                    lo, hi = np.quantile(boots[:, si, q], [0.025, 0.975])
                    key = f"sens.x6.{t}.{k}{lab_i}.{s}"
                    rows += [(key + ".saving", float(sav)), (key + ".lo", float(lo)), (key + ".hi", float(hi)),
                             (key + ".share_of_total_saving", float((tot[si, ir] - tot[si, names.index(s)]) / tot_save[s]))]
                oa = 1 - tot[si, names.index("oracle|act")] / tot[si, ir]
                lr = 1 - tot[si, names.index("lgbm|req")] / tot[si, ir]
                rows += [(f"sens.x6.{t}.{k}{lab_i}.retained_share", float(lr / oa) if oa else float("nan")),
                         (f"sens.x6.{t}.{k}{lab_i}.energy_share", float(tot[si, ir] / tot[:, ir].sum()))]
            if k == "month":
                sv = [1 - tot[si, names.index("lgbm|req")] / tot[si, ir] for si in range(n)]
                ctx.log(f"x6 {t}: lgbm|req saving by month (Jan..Dec, %): " + " ".join(f"{100 * v:.1f}" for v in sv) +
                        f"; months with negative saving: {sum(v < 0 for v in sv)}")
    return rows


# ------------------------------------------------------------------------------------------------------ x7
def item_x7(ctx, args):
    import sens_s3 as S3
    cc = S3.cc
    bas = C.eligible_bas(args.bas.split(",") if args.bas else None)
    tag = ("_smoke" if args.smoke else "") + "_sens_x7"
    clean_p = os.path.join(C.ROOT, "data", "derived", f"ci_clean{tag}.parquet")
    if not os.path.exists(clean_p):
        h = pd.read_parquet(os.path.join(C.ROOT, "data", "derived", "ci_hourly.parquet"),
                            columns=["ba", "utc", "ci", "gen_total_mw"] + ["share_" + f for f in S3.FUELS], filters=[("ba", "in", bas)])
        h["utc"] = pd.to_datetime(h["utc"], utc=True)
        life = S3.factors("life")
        fos = ["coal", "natural_gas", "oil"]
        sh = h[["share_" + f for f in fos]].fillna(0.0).to_numpy("float64")
        den = sh.sum(axis=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            ci_f = np.where(den > 0, sh @ np.array([life[f] for f in fos]) / den, np.nan)
        ctx.log("x7 fossil-only intensity: lifecycle factors " + ", ".join(f"{f} {life[f]:.0f}" for f in fos) +
                f"; hours with no fossil generation (undefined, missing under the A06 repair rules): {np.mean(den <= 0):.4f} of BA-hours")
        h["ci"] = ci_f.astype("float32")
        parts = []
        for ba, g in h.groupby("ba"):
            res, _ = cc.clean_one(g[["utc", "ci", "gen_total_mw"]])
            res["ba"] = ba
            parts.append(res[["ba", "utc", "ci_clean", "flag", "usable_day"]])
        clean = pd.concat(parts, ignore_index=True)
        clean.to_parquet(clean_p, index=False)
        base = pd.read_parquet(os.path.join(C.ROOT, "data", "derived", "ci_clean.parquet"), columns=["ba", "usable_day"])
        base = base[base["ba"].isin(bas)]
        ctx.log(f"x7 usable-day share: fossil proxy {clean['usable_day'].mean():.4f} vs frozen CI {base['usable_day'].mean():.4f}; "
                f"mean fossil proxy {clean['ci_clean'].mean():.1f} g/kWh")
    ctx.log("x7 ci_clean md5 " + C.md5_file(clean_p))
    fdir = os.path.join(C.ROOT, "data", "derived", f"forecasts{tag}")
    have = os.path.isdir(os.path.join(fdir, "lgbm")) and len(os.listdir(os.path.join(fdir, "lgbm"))) >= len(bas)
    lgbm_ok = have
    if not have:
        cmd = [os.path.join(C.SRC, "forecast.py"), "--input", f"data/derived/ci_clean{tag}.parquet", "--tag", tag,
               "--shares", "data/derived/ci_hourly.parquet", "--eligibility", "tables/ba_eligibility.csv", "--models", "lgbm",
               "--threads", str(args.threads)] + (["--bas", args.bas] if args.bas else [])
        ctx.log("frozen forecast.py refit, hyperparameters unchanged: " + " ".join(cmd[1:]))
        rc, pk1, pkt = C.run_polled(cmd, stdout_path=ctx.logf)
        ctx.peak_workers_mb = max(ctx.peak_workers_mb, pk1)
        ctx.log(f"forecast.py rc={rc}; peak RSS single process {pk1:.0f} MB, tree total {pkt:.0f} MB")
        lgbm_ok = rc == 0 and os.path.isdir(os.path.join(fdir, "lgbm")) and len(os.listdir(os.path.join(fdir, "lgbm"))) >= len(bas)
    # A42: a BA with no usable day under the fossil-only signal (no fossil generation at all, e.g. a hydro-only BA) has no job
    # window; it is excluded from X7 only (and recorded), every other item keeps its 42 BAs.
    cl = pd.read_parquet(clean_p, columns=["ba", "usable_day"])
    ud = cl.groupby("ba")["usable_day"].sum()
    excl = sorted(b for b in bas if float(ud.get(b, 0)) <= 0)
    if excl:
        bas = [b for b in bas if b not in excl]
        args.bas = ",".join(bas)
        ctx.log(f"x7 EXCLUDED BAs (fossil-only signal undefined for every hour, no usable day, no job window): {', '.join(excl)}; "
                f"n_bas = {len(bas)}")
    arms = ["runnow", "oracle|act", "oracle|req", "oracle|pred"]
    if lgbm_ok:
        arms += ["lgbm|act", "lgbm|req", "lgbm|pred"]
        ctx.log("x7: the fossil-only signal could be forecast with the frozen pipeline unchanged: lgbm arms included")
    else:
        ctx.log("x7: forecast refit failed or incomplete: ORACLE ARMS ONLY (stated)")
    o_a, o_r, f_a, f_r = ["oracle|act"], ["oracle|req"], ["lgbm|act"], ["lgbm|req"]
    contrasts = {"H2_runtime_penalty": (f_a, f_r), "H3_prediction_recovery": (["lgbm|pred"], f_r),
                 "oracle_runtime_term": (o_a, o_r), "shapley_gap": (o_a, f_r),
                 "shapley_forecast": (o_a + o_r, f_a + f_r, 0.5), "shapley_runtime": (o_a + f_a, o_r + f_r, 0.5),
                 "shapley_interaction": (o_a + f_r, o_r + f_a)}
    rows, _, _ = X.run_standard(ctx, args, arms, contrasts,
                                cfg_extra={"tag": tag, "fc_src": {"lgbm": (f"data/derived/forecasts{tag}", "lgbm")}})
    rows.append(("sens.x7.lgbm_arms_included", int(lgbm_ok)))
    rows.append(("sens.x7.meta.n_bas", len(bas)))
    rows.append(("sens.x7.meta.excluded_bas", ",".join(excl) if excl else "none"))
    rows.append(("sens.x7.meta.excluded_n", len(excl)))
    ctx.log("x7 excluded_bas: " + (",".join(excl) if excl else "none"))
    ctx.log("x7 label: proxy, not a marginal estimate")
    return rows


ITEMS = {"x1": item_x1, "x2": item_x2, "x3": item_x3, "x4": item_x4, "x5": item_x5, "x6": item_x6, "x7": item_x7}


def main():
    ap = X.std_parser(__doc__)
    ap.add_argument("--item", required=True, choices=sorted(ITEMS))
    ap.add_argument("--threads", type=int, default=10)
    args = ap.parse_args()
    ctx = C.Ctx(args.item, args.smoke)
    X.verify_plans()
    C.sim.check_prereg()
    X.dump_item_header(ctx, {"sim_seed": args.seed, "analysis_seed": 7, "B": args.B, "reps": args.reps, "n_jobs": args.n_jobs,
                             "x6_bootstrap_seed": 6})
    rows = ITEMS[args.item](ctx, args)
    X.finish_item(ctx, rows, args.smoke)


if __name__ == "__main__":
    main()
