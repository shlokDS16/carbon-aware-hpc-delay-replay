"""Secondary analyses A09 (PREREG section 7 items 2, 4, 5, 7, 8, 11) on TEST. Descriptive; reads results/sim_TEST*.
Writes tables/secondary_*.csv and tables/ledger_TEST_secondary.csv. Does not re-run the simulation."""
import glob
import os
import pickle

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAB = os.path.join(ROOT, "tables")
TRACES = ["PM100", "FDATA", "KIT_FH2"]
SLACKS = (2, 6, 12, 24)
CLSK = ["lt1", "1-4", "4-12", "ge12"]
CACHE = os.path.join(ROOT, "results", "_secondary_cache.pkl")
G0 = pd.Timestamp("2018-07-01", tz="UTC")
LED = []   # (key, value, source)


def led(key, val, src):
    LED.append((key, float(val), src))


def aggregate():
    if os.path.exists(CACHE):
        with open(CACHE, "rb") as fh:
            return pickle.load(fh)
    out = {}
    for var, d in (("main", "sim_TEST"), ("nl", "sim_TEST_nearlimit")):
        for tr in TRACES:
            for f in sorted(glob.glob(os.path.join(ROOT, "results", d, tr, "*.npz"))):
                ba = os.path.basename(f)[:-4]
                z = np.load(f)
                out["arms"] = list(z["arms"])
                for S in SLACKS:
                    acc = {}
                    for k in z.files:
                        if k.startswith("r") and k.endswith(f"_S{S}__n"):
                            pre = k[:-3]
                            for name in ("e_w", "e_u", "delay"):
                                acc[name] = acc.get(name, 0) + z[pre + "__" + name].sum(axis=1)   # [arms, classes]
                            acc["n"] = acc.get("n", 0) + z[k].sum(axis=0)                        # [classes]
                    out[(var, tr, ba, S)] = acc
    with open(CACHE, "wb") as fh:
        pickle.dump(out, fh)
    return out


def tot(A, var, tr, bl, S, name):
    return sum(A[(var, tr, b, S)][name] for b in bl)


def main():
    A = aggregate()
    arms = A["arms"]
    ix = {a: i for i, a in enumerate(arms)}
    bas = {tr: sorted({k[2] for k in A if k != "arms" and k[0] == "main" and k[1] == tr}) for tr in TRACES}

    def sav(E, a, cls=slice(None)):
        return 1 - E[ix[a], cls].sum() / E[ix["runnow"], cls].sum()

    src = "src/secondary.py from results/sim_TEST"
    E = tot(A, "main", "PM100", bas["PM100"], 12, "e_w")
    chk = sav(E, "lgbm|req")
    print("check lgbm|req S12 PM100 w =", chk, "n_ba", {t: len(v) for t, v in bas.items()})
    led("TEST.PM100.w.S12.check.saving.lgbm_req", chk, src)

    # item 1: retained share
    rows = []
    for tr in TRACES:
        for wt in ("w", "u"):
            for S in SLACKS:
                units = [("pooled", bas[tr])] + [(b, [b]) for b in bas[tr]]
                for unit, bl in units:
                    E = tot(A, "main", tr, bl, S, "e_" + wt)
                    N = tot(A, "main", tr, bl, S, "n")
                    for ci, c in [("all", slice(None))] + list(zip(CLSK, range(4))):
                        so = sav(E, "oracle|act", c)
                        r = {"trace": tr, "weight": wt, "S": S, "unit": unit, "class": ci,
                             "n_jobs": float(N.sum() if ci == "all" else N[c]), "saving_oracle_act": so}
                        for a in ("oracle|req", "lgbm|act", "lgbm|req", "lgbm|pred", "lgbm|pred2"):
                            r["saving_" + a.replace("|", "_")] = sav(E, a, c)
                        r["retained_lgbm_req"] = r["saving_lgbm_req"] / so if so > 0 else np.nan
                        r["retained_lgbm_pred"] = r["saving_lgbm_pred"] / so if so > 0 else np.nan
                        rows.append(r)
                        if unit == "pooled":
                            k = f"TEST.{tr}.{wt}.S{S}"
                            suf = "" if ci == "all" else f".class_{ci}"
                            led(f"{k}.retained.lgbm_req{suf}", r["retained_lgbm_req"], src)
                            led(f"{k}.retained.lgbm_pred{suf}", r["retained_lgbm_pred"], src)
                            led(f"{k}.saving.oracle_act{suf}", so, src)
                            led(f"{k}.njobs{suf}", r["n_jobs"], src)
    pd.DataFrame(rows).to_csv(os.path.join(TAB, "secondary_retained_share.csv"), index=False)

    # item 3: delay
    rows = []
    for tr in TRACES:
        for S in SLACKS:
            D = tot(A, "main", tr, bas[tr], S, "delay")
            N = tot(A, "main", tr, bas[tr], S, "n").sum()
            for a in arms:
                v = D[ix[a]].sum() / N
                rows.append({"trace": tr, "S": S, "arm": a, "mean_delay_h": v})
                led(f"TEST.{tr}.S{S}.delay_h.{a.replace('|', '_')}", v, src)
    pd.DataFrame(rows).to_csv(os.path.join(TAB, "secondary_delay.csv"), index=False)

    # item 4: all arms
    rows = []
    for tr in TRACES:
        for wt in ("w", "u"):
            for S in SLACKS:
                E = tot(A, "main", tr, bas[tr], S, "e_" + wt)
                for a in arms:
                    s = sav(E, a)
                    rows.append({"trace": tr, "weight": wt, "S": S, "arm": a, "saving": s})
                    led(f"TEST.{tr}.{wt}.S{S}.saving.{a.replace('|', '_')}", s, src)
    R4 = pd.DataFrame(rows)
    R4.to_csv(os.path.join(TAB, "secondary_all_arms.csv"), index=False)
    rows = []
    for (tr, wt, S), g in R4.groupby(["trace", "weight", "S"]):
        D = g[g.arm == "lgbm|req"].saving.iloc[0]
        base = g[~g.arm.str.startswith("oracle") & (g.arm != "runnow") & (g.arm != "lgbm|req")]
        dep = base[~base.arm.str.endswith("|act")]            # deployable: no oracle signal, no oracle runtime
        for lab, gg in (("deployable", dep), ("any_nonoracle_signal", base)):
            best = gg.loc[gg.saving.idxmax()]
            rows.append({"trace": tr, "weight": wt, "S": S, "set": lab, "D_lgbm_req": D, "best_other_arm": best.arm,
                         "best_other_saving": best.saving, "best_minus_D": best.saving - D})
            led(f"TEST.{tr}.{wt}.S{S}.best_{lab}_minus_D", best.saving - D, src)
        led(f"TEST.{tr}.{wt}.S{S}.best_deployable_arm_is_" + dep.loc[dep.saving.idxmax()].arm.replace("|", "_"), 1, src)
    pd.DataFrame(rows).to_csv(os.path.join(TAB, "secondary_best_vs_D.csv"), index=False)

    # item 6: near-limit
    rows = []
    cells = ["oracle|act", "oracle|req", "lgbm|act", "lgbm|req", "lgbm|pred", "lgbm|pred2"]
    for tr in TRACES:
        for wt in ("w", "u"):
            for S in SLACKS:
                for var in ("main", "nl"):
                    E = tot(A, var, tr, bas[tr], S, "e_" + wt)
                    N = tot(A, var, tr, bas[tr], S, "n").sum()
                    r = {"trace": tr, "weight": wt, "S": S, "variant": var, "n_jobs": N}
                    for a in cells:
                        r[a.replace("|", "_")] = sav(E, a)
                        if wt == "w":
                            led(f"TEST.{tr}.w.S{S}.nearlimit.{var}.{a.replace('|', '_')}", r[a.replace('|', '_')], src)
                    if wt == "w":
                        led(f"TEST.{tr}.w.S{S}.nearlimit.{var}.njobs", N, src)
                    rows.append(r)
    pd.DataFrame(rows).to_csv(os.path.join(TAB, "secondary_nearlimit.csv"), index=False)

    # item 2: Spearman with BA character
    ch = test_character()
    ch.to_csv(os.path.join(TAB, "secondary_ba_character_TEST.csv"))
    cov = pd.read_csv(os.path.join(TAB, "ba_coverage.csv")).set_index("ba")[
        ["median_daily_range", "share_solar", "share_wind", "share_fossil"]]
    rows, per = [], []
    for tr in TRACES:
        S, wt = 12, "w"
        pb = {}
        for b in bas[tr]:
            E = A[("main", tr, b, S)]["e_" + wt]
            pb[b] = (sav(E, "oracle|act"), sav(E, "lgbm|act") - sav(E, "lgbm|req"))
            per.append({"ba": b, "trace": tr, "oracle_act_saving_S12": pb[b][0], "runtime_penalty_S12": pb[b][1]})
        for sname, C in (("coverage_2018_2026", cov), ("TEST_hours", ch)):
            for si, stat in enumerate(["oracle_act_saving", "runtime_penalty"]):
                for c in C.columns:
                    x = np.array([C.loc[b, c] if b in C.index else np.nan for b in bas[tr]], dtype=float)
                    y = np.array([pb[b][si] for b in bas[tr]])
                    m = ~(np.isnan(x) | np.isnan(y))
                    rho, p = spearmanr(x[m], y[m])
                    rows.append({"trace": tr, "S": S, "weight": wt, "character_source": sname, "stat": stat,
                                 "character": c, "rho": rho, "p": p, "n_ba": int(m.sum())})
                    led(f"TEST.{tr}.{wt}.S{S}.spearman.{sname}.{stat}.{c}.rho", rho, src)
                    led(f"TEST.{tr}.{wt}.S{S}.spearman.{sname}.{stat}.{c}.p", p, src)
    pd.DataFrame(rows).to_csv(os.path.join(TAB, "secondary_spearman_character.csv"), index=False)
    pd.DataFrame(per).to_csv(os.path.join(TAB, "secondary_per_ba_S12.csv"), index=False)

    forecast_skill(A, bas, sav)
    pd.DataFrame(LED, columns=["key", "value", "source"]).to_csv(os.path.join(TAB, "ledger_TEST_secondary.csv"), index=False)
    print("ledger rows", len(LED))


def test_character():
    hr = pd.read_parquet(os.path.join(ROOT, "data", "derived", "ci_hourly.parquet"))
    cc = pd.read_parquet(os.path.join(ROOT, "data", "derived", "ci_clean.parquet"))
    lo, hi = pd.Timestamp("2025-07-01", tz="UTC"), pd.Timestamp("2026-07-01", tz="UTC")
    hr = hr[(hr.utc >= lo) & (hr.utc < hi)]
    cc = cc[(cc.utc >= lo) & (cc.utc < hi) & (cc.flag <= 3)].dropna(subset=["ci_clean"])
    rows = {}
    for b, g in cc.groupby("ba"):
        d = g.groupby(g.utc.dt.floor("D")).ci_clean.agg(["max", "min", "count"])
        d = d[d["count"] >= 20]
        rows[b] = {"median_daily_range": float((d["max"] - d["min"]).median())}
    for b, g in hr.groupby("ba"):
        w = g.gen_total_mw.clip(lower=0).fillna(0)
        tw = w.sum()
        if tw <= 0:
            continue
        sh = lambda c: float((g[c].fillna(0) * w).sum() / tw)
        r = rows.setdefault(b, {})
        r["share_solar"] = sh("share_solar")
        r["share_wind"] = sh("share_wind")
        r["share_fossil"] = sh("share_coal") + sh("share_natural_gas") + sh("share_oil")
    return pd.DataFrame(rows).T


def forecast_skill(A, bas, sav):
    cc = pd.read_parquet(os.path.join(ROOT, "data", "derived", "ci_clean.parquet"))
    models = ["persistence", "snaive_day", "snaive_week", "profile7", "lgbm"]
    buckets = [(1, 6), (7, 24), (25, 48), (49, 96), (1, 24)]
    lo, hi = pd.Timestamp("2025-07-01", tz="UTC"), pd.Timestamp("2026-07-01", tz="UTC")
    allbas = bas["PM100"]
    nh = int((pd.Timestamp("2026-07-02", tz="UTC") - G0) / pd.Timedelta(hours=1)) + 200
    rows, mu = [], {}
    for b in allbas:
        g = cc[(cc.ba == b) & (cc.flag <= 3)].dropna(subset=["ci_clean"])
        Y = np.full(nh, np.nan)
        Y[((g.utc - G0) / pd.Timedelta(hours=1)).astype(int).to_numpy()] = g.ci_clean.to_numpy()
        gt = g[(g.utc >= lo) & (g.utc < hi)]
        mu[b] = gt.ci_clean.mean()
        for m in models:
            z = np.load(os.path.join(ROOT, "data", "derived", "forecasts", m, f"{b}.npz"))
            ti = (z["issue_utc"] // 3_600_000_000_000 - int(G0.value // 3_600_000_000_000)).astype(int)  # grid index t
            t0 = int((lo - G0) / pd.Timedelta(hours=1))
            t1 = int((hi - G0) / pd.Timedelta(hours=1))
            sel = (ti >= t0) & (ti < t1)
            ti, fc = ti[sel], z["fc"][sel].astype(float)
            for h0, h1 in buckets:
                errs = []
                for h in range(h0, h1 + 1):
                    tgt = Y[ti + h]                      # fc[:, h-1] forecasts grid index t+h (simcore: interval k carries ci[k])
                    e = np.abs(fc[:, h - 1] - tgt)
                    errs.append(e[~np.isnan(e)])
                e = np.concatenate(errs)
                rows.append({"ba": b, "model": m, "bucket": f"{h0}-{h1}", "mae": float(e.mean()), "n": len(e)})
    F = pd.DataFrame(rows)
    F["mean_ci_test"] = F.ba.map(mu)
    F["mae_rel"] = F.mae / F.mean_ci_test
    F.to_csv(os.path.join(TAB, "secondary_forecast_mae.csv"), index=False)
    src = "src/secondary.py from data/derived/forecasts and ci_clean (flag 0-3)"
    piv = F.groupby(["model", "bucket"]).agg(mae_mean=("mae", "mean"), mae_median=("mae", "median"),
                                             mae_rel_median=("mae_rel", "median")).reset_index()
    piv.to_csv(os.path.join(TAB, "secondary_forecast_mae_summary.csv"), index=False)
    for _, r in piv.iterrows():
        led(f"TEST.forecast.{r.model}.lead{r.bucket}.mae_mean_over_ba", r.mae_mean, src)
        led(f"TEST.forecast.{r.model}.lead{r.bucket}.mae_median_over_ba", r.mae_median, src)
        led(f"TEST.forecast.{r.model}.lead{r.bucket}.mae_rel_median_over_ba", r.mae_rel_median, src)
    # lgbm vs snaive_day / profile7 win counts at 1-24
    p = F[F.bucket == "1-24"].pivot(index="ba", columns="model", values="mae")
    for o in ("snaive_day", "profile7", "persistence", "snaive_week"):
        led(f"TEST.forecast.lgbm_beats_{o}.lead1-24.n_ba", int((p["lgbm"] < p[o]).sum()), src)
    l24 = F[(F.model == "lgbm") & (F.bucket == "1-24")].set_index("ba")
    rows = []
    for tr in TRACES:
        for S in SLACKS:
            y = np.array([sav(A[("main", tr, b, S)]["e_w"], "oracle|req") - sav(A[("main", tr, b, S)]["e_w"], "lgbm|req")
                          for b in bas[tr]])
            for nm, x in (("mae_1_24", l24.mae), ("mae_rel_1_24", l24.mae_rel)):
                xx = np.array([x[b] for b in bas[tr]])
                rho, pv = spearmanr(xx, y)
                rows.append({"trace": tr, "S": S, "weight": "w", "metric": nm, "rho": rho, "p": pv, "n_ba": len(y)})
                led(f"TEST.{tr}.w.S{S}.spearman.forecastgap.{nm}.rho", rho, src)
                led(f"TEST.{tr}.w.S{S}.spearman.forecastgap.{nm}.p", pv, src)
    pd.DataFrame(rows).to_csv(os.path.join(TAB, "secondary_forecast_gap_spearman.csv"), index=False)


if __name__ == "__main__":
    main()
