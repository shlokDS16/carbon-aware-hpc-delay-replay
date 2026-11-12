"""S5 (post-freeze, exploratory): tuned forecasters (owner rule 12), exactly as research/P4_PLAN.md v2 SETTINGS.

Optuna TPE, 100 trials, sampler seed 20261112, objective = pooled mean MAE at leads 1-24 h on the frozen TRAIN validation
window (issues 2024-01-01 .. targets before 2024-07-01), no DEV or TEST data: every array handed to the tuning code is a
copy of the frozen series with all hours >= 2024-07-01 set to NaN (asserted), and every target index is < IDX_TRAIN_END.
Space: num_leaves 15-127, max_depth 3-10, learning_rate 0.01-0.15 (log), min_data_in_leaf 50-1000 (log), feature_fraction
0.6-1.0, bagging_fraction 0.6-1.0, lambda_l1 and lambda_l2 1e-4..10 (log), max_bin 63-255. Iteration count by early stopping
(patience 50, cap 1500 = frozen) on the frozen validation rows (random 12 of 96 leads per issue, as frozen); the trial
objective is evaluated on a separate set: leads 1-24 for every 6th issue hour of the window (~0.73 M rows), at the best
iteration. Refit with the selected settings and iteration count on full TRAIN (all training rows with target < 2024-07-01,
including the purged and validation rows), then TEST forecasts, lgbm arms, Shapley split beside the frozen values.
Rivals tuned on the same window: profile lookback L in {1, 3, 7, 14, 28} days; seasonal naive day vs week (no parameters).
Features, row sampling (seed 42, stride rule, 12 leads per issue), purge, base forecast and l1 objective are the frozen
ones (functions imported from src/forecast.py; make_rows is a copy of forecast.make_train that also returns the purged rows).
Usage: py src/sens_s5.py [--smoke --bas CISO,ERCO --trials 3 --n-jobs 2000 --reps 1] [--threads 20] [--stage hpo|all]
Outputs: results/_sens_s5/hpo.db (resumable), data/derived/forecasts_sens_s5/{lgbm,profile_tuned}/<BA>.npz, lgbm_model.txt,
 tables/sens_s5_*.csv, results/sim_TEST_sens_s5/, results/analysis_TEST_sens_s5_*.json, tables/ledger_TEST_sens_s5.csv
"""
import argparse
import gc
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sens_common as C  # noqa: E402
import forecast as F     # noqa: E402  (frozen)

SAMPLER_SEED = 20261112
N_TRIALS = 100
LOOKBACKS = (1, 3, 7, 14, 28)
OBJ_STRIDE = 6
SEED = 42            # frozen LightGBM / row-sampling seed
ARMS = ["runnow", "oracle|act", "oracle|req", "lgbm|act", "lgbm|req", "lgbm|pred", "ptuned|req", "snaive_tuned|req"]


# ---------------------------------------------------------------- TRAIN-only data
def truncate_to_train(data):
    """Copies of the series with every hour >= IDX_TRAIN_END set to NaN; rolling stats recomputed on the copy."""
    tr = {}
    for ba, rec in data.items():
        C_, Y_, S_ = rec["C"].copy(), rec["Y"].copy(), rec["S"].copy()
        C_[F.IDX_TRAIN_END:], Y_[F.IDX_TRAIN_END:], S_[F.IDX_TRAIN_END:] = np.nan, np.nan, np.nan
        tr[ba] = {"C": C_, "Y": Y_, "S": S_, "R": F.roll_stats(C_)}
    assert_train_only(tr)
    return tr


def assert_train_only(tr):
    for ba, rec in tr.items():
        for k in ("C", "Y", "S"):
            assert not np.isfinite(rec[k][F.IDX_TRAIN_END:]).any(), f"{ba} {k}: finite value at or after 2024-07-01"


def make_rows(ba_list, data, stride, rpi, rng):
    """Copy of forecast.make_train (same sampling order and masks) that also returns the purged rows (target >= 2024-01-01,
    issue < 2024-01-01), needed for the refit on full TRAIN. Returns {'tr','va','pu': (X, y_residual)}."""
    out = {k: ([], []) for k in ("tr", "va", "pu")}
    for code, ba in enumerate(ba_list):
        rec = data[ba]
        C_ = rec["C"]
        ts = np.arange(0, F.IDX_TRAIN_END)
        ts = ts[(ts % stride == 0) & np.isfinite(C_[ts])]
        if ts.size == 0:
            continue
        hs = np.argsort(rng.random((ts.size, F.H)), axis=1)[:, :rpi] + 1
        t = np.repeat(ts, rpi)
        h = hs.reshape(-1)
        tgt = t + h
        y = F.take(rec["Y"], tgt)
        ok = np.isfinite(y) & (tgt < F.IDX_TRAIN_END)
        assert t.max() < F.IDX_TRAIN_END
        is_val = ok & (t >= F.IDX_VAL_START)
        is_tr = ok & (tgt < F.IDX_VAL_START)
        is_pu = ok & ~is_val & ~is_tr
        for key, mask in (("tr", is_tr), ("va", is_val), ("pu", is_pu)):
            if mask.any():
                assert tgt[mask].max() < F.IDX_TRAIN_END
                X, base = F.build_X(code, rec, t[mask], h[mask])
                out[key][0].append(X)
                out[key][1].append((y[mask] - base).astype(np.float32))
    return {k: (np.concatenate(v[0]), np.concatenate(v[1])) for k, v in out.items()}


def profile_L(C_, t, h, L):
    """Mean of the L most recent same-hour-of-day values available at issue t (copy of forecast.baseline_feats, window L days)."""
    k0 = -(-h // 24)
    acc = np.zeros(t.shape, dtype=np.float32)
    cnt = np.zeros(t.shape, dtype=np.float32)
    for j in range(L):
        v = F.take(C_, t + h - 24 * (k0 + j))
        m = np.isfinite(v)
        acc[m] += v[m]
        cnt += m
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(cnt > 0, acc / cnt, np.nan).astype(np.float32)


def make_obj(ba_list, data):
    """Objective set: leads 1-24, issues in the validation window with t % 6 == 0, target < IDX_TRAIN_END.
    Also returns the rival forecasts (profile L in LOOKBACKS, snaive day, snaive week) on the same cells."""
    Xs, bases, ys, riv = [], [], [], []
    h24 = np.arange(1, 25)
    for code, ba in enumerate(ba_list):
        rec = data[ba]
        C_ = rec["C"]
        ts = np.arange(F.IDX_VAL_START, F.IDX_TRAIN_END)
        ts = ts[(ts % OBJ_STRIDE == 0) & np.isfinite(C_[ts])]
        t = np.repeat(ts, 24)
        h = np.tile(h24, ts.size)
        tgt = t + h
        y = F.take(rec["Y"], tgt)
        ok = np.isfinite(y) & (tgt < F.IDX_TRAIN_END)
        t, h, y = t[ok], h[ok], y[ok]
        assert (t + h).max() < F.IDX_TRAIN_END and t.min() >= F.IDX_VAL_START
        X, base = F.build_X(code, rec, t, h)
        k0 = -(-h // 24)
        r = np.stack([profile_L(C_, t, h, L) for L in LOOKBACKS] +
                     [F.take(C_, t + h - 24 * k0), F.take(C_, t + h - 168 * (-(-h // 168)))], axis=1)
        Xs.append(X)
        bases.append(base)
        ys.append(y.astype(np.float32))
        riv.append(r)
    return np.concatenate(Xs), np.concatenate(bases), np.concatenate(ys), np.concatenate(riv)


# ---------------------------------------------------------------- HPO
def run_hpo(ctx, args, rows, obj):
    import lightgbm as lgb
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    Xtr, ytr = rows["tr"]
    Xva, yva = rows["va"]
    Xo, base_o, y_o, _ = obj
    db = Path(ctx.res) / "_sens_s5" / "hpo.db"
    db.parent.mkdir(parents=True, exist_ok=True)
    study = optuna.create_study(study_name="s5_tpe", storage="sqlite:///" + db.as_posix(), load_if_exists=True,
                                direction="minimize", sampler=optuna.samplers.TPESampler(seed=SAMPLER_SEED))
    n_done = sum(t.state == optuna.trial.TrialState.COMPLETE for t in study.trials)
    ctx.log(f"HPO: {n_done} of {args.trials} trials already complete; sampler seed {SAMPLER_SEED} (resume re-seeds the sampler)")

    def objective(trial):
        p = dict(objective="l1", learning_rate=trial.suggest_float("learning_rate", 0.01, 0.15, log=True),
                 num_leaves=trial.suggest_int("num_leaves", 15, 127), max_depth=trial.suggest_int("max_depth", 3, 10),
                 min_data_in_leaf=trial.suggest_int("min_data_in_leaf", 50, 1000, log=True),
                 feature_fraction=trial.suggest_float("feature_fraction", 0.6, 1.0),
                 bagging_fraction=trial.suggest_float("bagging_fraction", 0.6, 1.0), bagging_freq=1,
                 lambda_l1=trial.suggest_float("lambda_l1", 1e-4, 10.0, log=True),
                 lambda_l2=trial.suggest_float("lambda_l2", 1e-4, 10.0, log=True),
                 max_bin=trial.suggest_int("max_bin", 63, 255),
                 seed=SEED, bagging_seed=SEED, feature_fraction_seed=SEED, data_random_seed=SEED,
                 deterministic=True, num_threads=args.threads, verbose=-1)
        t0 = time.time()
        dtr = lgb.Dataset(Xtr, ytr, feature_name=F.FEAT_NAMES, categorical_feature=["ba_code"], params=dict(p),
                          free_raw_data=False)
        dva = lgb.Dataset(Xva, yva, reference=dtr, free_raw_data=False)
        m = lgb.train(p, dtr, num_boost_round=args.rounds, valid_sets=[dva], valid_names=["val"],
                      callbacks=[lgb.early_stopping(50, verbose=False)])
        bi = int(m.best_iteration)
        pred = m.predict(Xo, num_iteration=bi, num_threads=args.threads)
        mae = float(np.mean(np.abs(np.maximum(base_o + pred, 0.0) - y_o)))
        trial.set_user_attr("best_iteration", bi)
        trial.set_user_attr("val_l1_resid_allleads", float(m.best_score["val"]["l1"]))
        trial.set_user_attr("seconds", time.time() - t0)
        ctx.log(f"trial {trial.number}: MAE(1-24h) {mae:.3f}  best_iter {bi}  {time.time()-t0:.0f} s  "
                + json.dumps({k: (round(v, 5) if isinstance(v, float) else v) for k, v in trial.params.items()}))
        del dtr, dva, m
        gc.collect()
        return mae

    if args.trials - n_done > 0:
        study.optimize(objective, n_trials=args.trials - n_done)
    best = study.best_trial
    ctx.log(f"HPO best trial {best.number}: MAE {best.value:.4f}, best_iteration {best.user_attrs['best_iteration']}, "
            + json.dumps(best.params))
    return best, study


# ---------------------------------------------------------------- forecasts and scoring
def profile_fc(C_, issues, L):
    """Profile forecast with lookback L for all issues x leads 1..96 (same shape and NaN rule as forecast.baseline_fc)."""
    t = np.repeat(issues, F.H)
    h = np.tile(np.arange(1, F.H + 1), issues.size)
    out = profile_L(C_, t, h, L).reshape(issues.size, F.H)
    out[~np.isfinite(C_[issues])] = np.nan
    return out


def score_test(data, ba_list, fdirs, issues, ctx):
    """TEST MAE by lead bucket for every model on the common valid cells (issue in TEST, target before 2026-07-01).
    Mirrors forecast.skill_for_ba (MAE part) for the TEST period; run only after all tuning is finished."""
    sel = (issues >= F.IDX_DEV_END) & (issues < F.IDX_ISSUE_END)
    t = issues[sel]
    rows = []
    for ba in ba_list:
        Y = F.take(data[ba]["Y"], (t[:, None] + np.arange(1, F.H + 1)[None, :]).ravel()).reshape(t.size, F.H)
        Y[(t[:, None] + np.arange(1, F.H + 1)[None, :]) >= F.IDX_ISSUE_END] = np.nan
        fcs = {m: np.load(os.path.join(ROOT_ABS, d, m_dir, f"{ba}.npz"))["fc"][sel] for m, (d, m_dir) in fdirs.items()}
        valid = np.isfinite(Y)
        for m in fcs:
            valid &= np.isfinite(fcs[m])
        for m, Fm in fcs.items():
            ae = np.where(valid, np.abs(Fm - Y), np.nan)
            for b, (lo, hi) in F.BUCKETS.items():
                sl = slice(lo - 1, hi)
                rows.append(dict(model=m, ba=ba, lead_bucket=b, n=int(valid[:, sl].sum()), sum_ae=float(np.nansum(ae[:, sl]))))
    df = pd.DataFrame(rows)
    df["MAE"] = df["sum_ae"] / df["n"]
    return df


ROOT_ABS = str(C.ROOT)
ROOTP = Path(C.ROOT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--bas", default="")
    ap.add_argument("--trials", type=int, default=N_TRIALS)
    ap.add_argument("--rounds", type=int, default=1500)
    ap.add_argument("--threads", type=int, default=20)
    ap.add_argument("--n-jobs", type=int, default=20000)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--seed", type=int, default=20261111)
    ap.add_argument("--traces", default="PM100,FDATA,KIT_FH2")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--stage", default="all", choices=["rows", "hpo", "all"])
    ap.add_argument("--verify", action="store_true", help="smoke: row equality with forecast.make_train and masked-vs-full data")
    args = ap.parse_args()
    ctx = C.Ctx("s5", args.smoke)
    C.verify_frozen()
    C.sim.check_prereg()
    F.model_threads[0] = args.threads
    ctx.header({"optuna_sampler_seed": SAMPLER_SEED, "trials": args.trials, "lgbm_seed": SEED, "sim_seed": args.seed,
                "analysis_seed": 7, "B": args.B},
               ["data/derived/ci_clean.parquet", "data/derived/ci_hourly.parquet", "data/derived/jobs.parquet"])
    bas = [b for b in args.bas.split(",") if b]
    ba_list, data = F.load_series(ROOTP / "data/derived/ci_clean.parquet", "", bas, ROOTP / "tables/ba_eligibility.csv",
                                  ROOTP / "data/derived/ci_hourly.parquet")
    ctx.log(f"loaded {len(ba_list)} BAs")
    for b in ba_list:
        data[b]["R"] = F.roll_stats(data[b]["C"])
    # ---- tuning data: TRAIN only
    tr = truncate_to_train(data)
    nvalid = sum(int(np.isfinite(tr[b]["C"][:F.IDX_TRAIN_END]).sum()) for b in ba_list)
    stride = max(7, math.ceil(nvalid * 12 / 2_800_000))
    ctx.log(f"TRAIN-only data asserted; valid TRAIN BA-hours {nvalid}; issue stride {stride}, 12 leads per issue (frozen rule)")
    rows = make_rows(ba_list, tr, stride, 12, np.random.default_rng(SEED))
    ctx.log("rows: train %d, validation %d, purged %d" % (len(rows["tr"][1]), len(rows["va"][1]), len(rows["pu"][1])))
    if args.verify:
        a = F.make_train(ba_list, tr, stride, 12, np.random.default_rng(SEED))
        b = F.make_train(ba_list, data, stride, 12, np.random.default_rng(SEED))
        same_frozen = all(np.array_equal(x, y, equal_nan=True) for x, y in zip(a, (rows["tr"][0], rows["tr"][1], rows["va"][0], rows["va"][1])))
        same_full = all(np.array_equal(x, y, equal_nan=True) for x, y in zip(a, b))
        ctx.log(f"VERIFY make_rows == forecast.make_train: {same_frozen}; masked-TRAIN rows == full-data rows: {same_full}")
        assert same_frozen and same_full
    obj = make_obj(ba_list, tr)
    ctx.log(f"objective set: {len(obj[2])} rows (leads 1-24, every {OBJ_STRIDE}th issue hour of the validation window)")
    # ---- rivals on the validation window (common valid cells)
    Xo, base_o, y_o, riv = obj
    common = np.isfinite(riv).all(axis=1)
    names = [f"profile_L{L}" for L in LOOKBACKS] + ["snaive_day", "snaive_week"]
    val_mae = {n: float(np.mean(np.abs(riv[common, i] - y_o[common]))) for i, n in enumerate(names)}
    ctx.log(f"validation MAE (1-24 h, {int(common.sum())} common cells): " + json.dumps({k: round(v, 3) for k, v in val_mae.items()}))
    L_best = LOOKBACKS[int(np.argmin([val_mae[f"profile_L{L}"] for L in LOOKBACKS]))]
    snaive_best = "snaive_day" if val_mae["snaive_day"] <= val_mae["snaive_week"] else "snaive_week"
    ctx.log(f"tuned profile lookback {L_best} d; seasonal naive choice {snaive_best}")
    if args.stage == "rows":
        ctx.log(f"stage rows done (memory probe, no tuning); rows+objective built for {len(ba_list)} BAs")
        ctx.footer()
        return
    # frozen lgbm on the same objective set (reference)
    import lightgbm as lgb
    fro = lgb.Booster(model_file=str(ROOTP / "data/derived/forecasts/lgbm_model.txt"))
    if len(ba_list) == 42:
        pf = fro.predict(Xo, num_iteration=fro.best_iteration or -1, num_threads=args.threads)
        val_mae["lgbm_frozen_on_obj"] = float(np.mean(np.abs(np.maximum(base_o + pf, 0.0) - y_o)))
        ctx.log(f"frozen LightGBM MAE on the objective set: {val_mae['lgbm_frozen_on_obj']:.3f}")
    # ---- HPO
    best, study = run_hpo(ctx, args, rows, obj)
    val_mae["lgbm_tuned_obj"] = float(best.value)
    n_it = int(best.user_attrs["best_iteration"])
    if args.stage == "hpo":
        ctx.footer()
        return
    # ---- refit on full TRAIN
    p = dict(objective="l1", bagging_freq=1, seed=SEED, bagging_seed=SEED, feature_fraction_seed=SEED, data_random_seed=SEED,
             deterministic=True, num_threads=args.threads, verbose=-1, **best.params)
    del obj
    gc.collect()
    n_all = sum(len(rows[k][1]) for k in ("tr", "va", "pu"))
    Xall = np.empty((n_all, rows["tr"][0].shape[1]), dtype=np.float32)    # fill piecewise to limit peak memory
    yall = np.empty(n_all, dtype=np.float32)
    pos = 0
    for k in ("tr", "va", "pu"):
        Xk, yk = rows.pop(k)
        Xall[pos:pos + len(yk)], yall[pos:pos + len(yk)] = Xk, yk
        pos += len(yk)
        del Xk, yk
    del rows
    gc.collect()
    ctx.log(f"refit on full TRAIN: {len(yall)} rows, {n_it} rounds")
    t0 = time.time()
    dall = lgb.Dataset(Xall, yall, feature_name=F.FEAT_NAMES, categorical_feature=["ba_code"], params=dict(p), free_raw_data=True)
    model = lgb.train(p, dall, num_boost_round=n_it)
    model.best_iteration = n_it
    ctx.log(f"refit done in {time.time()-t0:.0f} s")
    del Xall, yall, dall
    gc.collect()
    tag = ("_smoke" if args.smoke else "") + "_sens_s5"
    fdir = ROOTP / "data" / "derived" / f"forecasts{tag}"
    for m in ("lgbm", "profile_tuned"):
        (fdir / m).mkdir(parents=True, exist_ok=True)
    model.save_model(str(fdir / "lgbm_model.txt"), num_iteration=n_it)
    issues = np.arange(F.IDX_TRAIN_END, F.IDX_ISSUE_END)
    issue_ns = ((F.G0 + pd.to_timedelta(issues, unit="h")).to_numpy("datetime64[ns]")).astype(np.int64)
    for code, ba in enumerate(ba_list):
        Fc = F.lgbm_fc(model, code, data[ba], issues)
        np.savez_compressed(fdir / "lgbm" / f"{ba}.npz", issue_utc=issue_ns, fc=Fc.astype(np.float32))
        Pc = profile_fc(data[ba]["C"], issues, L_best)
        np.savez_compressed(fdir / "profile_tuned" / f"{ba}.npz", issue_utc=issue_ns, fc=Pc.astype(np.float32))
        if L_best == 7:
            assert np.array_equal(np.nan_to_num(Pc, nan=-1), np.nan_to_num(F.baseline_fc(data[ba]["C"], issues, "profile7"), nan=-1))
        ctx.log(f"forecasts written {ba} ({code+1}/{len(ba_list)})")
    del model
    # ---- TEST forecast accuracy, tuned vs frozen (after all tuning)
    fd = f"data/derived/forecasts{tag}"
    fz = "data/derived/forecasts"
    fdirs = {"lgbm_tuned": (fd, "lgbm"), "lgbm_frozen": (fz, "lgbm"), "profile_tuned": (fd, "profile_tuned"),
             "profile7_frozen": (fz, "profile7"), "snaive_day": (fz, "snaive_day"), "snaive_week": (fz, "snaive_week"),
             "persistence": (fz, "persistence")}
    sc_df = score_test(data, ba_list, fdirs, issues, ctx)
    sc_df.to_csv(Path(ctx.tab) / ("sens_s5_forecast_mae_TEST_by_ba.csv"), index=False)
    pooled = sc_df.groupby(["model", "lead_bucket"]).agg(n=("n", "sum"), sum_ae=("sum_ae", "sum")).reset_index()
    pooled["MAE"] = pooled["sum_ae"] / pooled["n"]
    pooled.to_csv(Path(ctx.tab) / "sens_s5_forecast_mae_TEST.csv", index=False)
    ctx.log("TEST pooled MAE 1-24 h: " + json.dumps({r.model: round(r.MAE, 3) for r in pooled[pooled.lead_bucket == "1-24"].itertuples()}))
    w = sc_df[sc_df.lead_bucket == "1-24"].pivot(index="ba", columns="model", values="MAE")
    n_better = int((w["lgbm_tuned"] < w["lgbm_frozen"]).sum())
    del data, tr
    gc.collect()
    # ---- simulation and analysis
    jobs = C.load_jobs("COMPLETED", args.traces.split(","))
    cfg = dict(tag="", arms=ARMS, slacks=C.SLACKS, ks=(0,), seed=args.seed, reps=args.reps, n_jobs=args.n_jobs,
               fc_src={"lgbm": (fd, "lgbm"), "ptuned": (fd, "profile_tuned"), "snaive_tuned": (fz, snaive_best)},
               outdir={0: ctx.simdir()})
    C.run_generic(ctx, cfg, jobs, ba_list, args.workers)
    del jobs
    out_rows = [(f"sens.s5.hpo.best_value_mae_1_24", float(best.value)), ("sens.s5.hpo.best_trial", best.number),
                ("sens.s5.hpo.best_iteration", n_it), ("sens.s5.hpo.n_trials", len(study.trials)),
                ("sens.s5.lookback_tuned_days", L_best), ("sens.s5.snaive_choice_is_week", int(snaive_best == "snaive_week")),
                ("sens.s5.test.n_ba_tuned_lgbm_better_1_24", n_better)]
    out_rows += [(f"sens.s5.hpo.param.{k}", v) for k, v in best.params.items()]
    out_rows += [(f"sens.s5.val_mae_1_24.{k}", v) for k, v in val_mae.items()]
    out_rows += [(f"sens.s5.test_mae.{r.model}.{r.lead_bucket}", float(r.MAE)) for r in pooled.itertuples()]
    for trace in args.traces.split(","):
        for wgt in ("w", "u"):
            res = C.analyse(ctx.simdir(), trace, wgt, B=args.B, seed=7)
            with open(ctx.analysis_path(trace, wgt), "w", encoding="utf-8") as f:
                json.dump(res, f, indent=1)
            out_rows += C.ledger_rows("s5", res)
            if wgt == "w":
                r = res["slacks"]["12"]
                ctx.log(f"S5 {trace} w S12: D(tuned) {100*r['savings']['lgbm|req']:.2f} %  H2 {100*r['tests']['H2_runtime_penalty']['est']:.2f} pp  "
                        f"H3 {100*r['tests']['H3_prediction_recovery']['est']:.2f} pp  ptuned|req {100*r['savings']['ptuned|req']:.2f} %")
    C.write_ledger(ctx, out_rows, "sens.s5.")
    ctx.log("ledger " + ctx.ledger_path())
    ctx.footer()
    if not args.smoke:
        open(ctx.done_path(), "w").write("done\n")


if __name__ == "__main__":
    main()
