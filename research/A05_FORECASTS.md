# A05 Final run (supersedes the _v0 results below)

VERDICT: A05 final done; 42 BAs; DEV MAE lgbm vs snaive_day 24.5 vs 29.6 g/kWh (pooled 1-24 h)

Command: `python src/forecast.py --input data/derived/ci_clean.parquet --tag "" --shares data/derived/ci_hourly.parquet` (log `logs/a05_forecast_final.log`, run time 478 s). Outputs: `data/derived/forecasts/<model>/<BA>.npz` (42 BAs x 5 models; `fc` float32 [17520, 96], no NaN in lgbm), `data/derived/forecasts/lgbm_model.txt`, `tables/forecast_skill.csv` (DEV only, 1050 rows), `tables/forecast_skill_summary.csv` (pooled MAE). The `_v0` files are kept.

Changes versus the _v0 run
1. Input: `ci_clean.parquet` and `ba_eligibility.csv` (42 eligible BAs); fuel shares from `ci_hourly.parquet`.
2. Causal model input (closes the caveat). Every model input (lags, rolling stats, persistence, snaive_day, snaive_week, profile7, lgbm features) is built from a series in which hours with flag 1 or 2 are replaced by the last earlier unflagged value (forward fill, at most 6 h, else NaN). Flag 3 (same hour previous week, taken from an earlier time) is causal and kept. Flag 4 stays NaN (no forecast when C at the issue hour is NaN; none occurred in the stored lgbm output at lead 1). Targets (lgbm fitting, early stopping, DEV skill) stay `ci_clean` as is. Function `causal_input` in `src/forecast.py`.
3. Same hyperparameters and seed. Stride 10 (2,418,567 training rows, 217,931 validation rows), best iteration 777, validation residual MAE 31.80; fit 34 s.

Leakage checks on the final run (`src/forecast_leakcheck.py`, 5 BAs: CISO, PJM, ERCO, AECI, DUK)
- Future perturbation: 6 random DEV+TEST issue hours per BA x 5 models = 150 tests, with every value after the issue hour replaced by noise; 0 failed.
- Flagged-value test: the stored values at all 1049 flag 1/2 hours were replaced by random numbers; the model input series was bit-identical (0 failures), and each replaced hour equals an earlier unflagged value within 6 h or NaN.
- TRAIN-only fitting, purged validation window, DEV-only scoring with targets before 2025-07-01, and identical cell sets across models: unchanged (209,940 cells per BA at 1-24 h). No TEST skill computed.
- Remaining note: skill targets include A06-flagged hours (interpolated or outlier-replaced values) as they stand in ci_clean, as instructed. `usable_day` was not applied to scoring.

DEV MAE (g/kWh), 42 BAs. Pooled (cell-weighted):

| model | 1-6 | 7-24 | 1-24 | 25-48 | 49-96 |
|---|---|---|---|---|---|
| lgbm | 19.1 | 26.3 | 24.5 | 30.4 | 33.4 |
| profile7 | 31.1 | 31.1 | 31.1 | 33.4 | 35.7 |
| snaive_day | 29.6 | 29.6 | 29.6 | 35.4 | 39.1 |
| snaive_week | 43.2 | 43.2 | 43.2 | 43.2 | 43.2 |
| persistence | 28.4 | 46.2 | 41.8 | 48.9 | 52.4 |

Median over BAs:

| model | 1-6 | 7-24 | 1-24 | 25-48 | 49-96 |
|---|---|---|---|---|---|
| lgbm | 16.8 | 20.7 | 19.7 | 23.8 | 28.1 |
| profile7 | 24.3 | 24.4 | 24.4 | 27.3 | 30.5 |
| snaive_day | 23.1 | 23.1 | 23.1 | 27.9 | 30.7 |
| snaive_week | 36.0 | 36.0 | 36.0 | 36.0 | 36.1 |
| persistence | 26.0 | 40.9 | 36.9 | 43.4 | 45.4 |

Median MAPE (1-24 h): lgbm 0.073, snaive_day 0.086, profile7 0.087, persistence 0.121, snaive_week 0.123. Mean rank skill (windows 1-24, 25-48, 49-96): lgbm 0.598, 0.564, 0.552; profile7 0.570, 0.560, 0.551; snaive_day 0.511, 0.480, 0.466; snaive_week 0.468; persistence 0 by definition.
Per BA (1-24 h MAE): lgbm beats snaive_day in 38 of 42 BAs and profile7 in 41 of 42. Gain over snaive_day at 1-24 h pooled: 17 %; at 49-96 h lgbm and profile7 are close in rank skill (0.552 vs 0.551), so lgbm adds little ranking information at long leads.

---
# Earlier _v0 run (37 BAs, uncorrected flag-1/2 inputs; kept for the record)

# A05 Past-only carbon-intensity forecasters

VERDICT (superseded by the Final run section below, which is the file set to use): A05 done; 37 BAs; DEV MAE lgbm vs snaive_day 25.7 vs 31.3 g/kWh (pooled 1-24 h)

Code: `src/forecast.py` (run: `python src/forecast.py --input data/derived/ci_clean_v0.parquet --tag _v0 --models persistence,snaive_day,snaive_week,profile7,lgbm`), leakage test `src/forecast_leakcheck.py`. Log: `logs/a05_forecast_v0.log`.
Outputs: `data/derived/forecasts_v0/<model>/<BA>.npz` (37 BAs x 5 models, 224 MB; arrays `issue_utc` int64 ns, `fc` float32 [17520, 96]; issue hours 2024-07-01 00:00 to 2026-06-30 23:00 UTC), `data/derived/forecasts_v0/lgbm_model.txt`, `tables/forecast_skill_v0.csv` (model, ba, period=DEV, lead_bucket, MAE, RMSE, MAPE, rank_skill, n), `tables/forecast_skill_summary_v0.csv` (pooled MAE).
Note: the forecast folder is `forecasts_v0` (the tag is appended), not `forecasts`. Rename or point `simulate.py` at it when the final run is frozen.

## Input
`ci_clean_v0.parquet` (A06; 37 eligible BAs per `ba_eligibility_v0.csv`). Shares come from `ci_hourly_v0.parquet` (forward-filled, causal). Development was first done on CISO, PJM, ERCO from `ci_hourly_v0.parquet` with forward fill; those test files were deleted.

## Method
- Hour index grid from 2018-07-01 00:00 UTC. Forecast for issue hour t, lead h targets the hour labelled t+h (the series value at t is known at issue).
- persistence: C(t). snaive_day: C(t+h-24*ceil(h/24)). snaive_week: C(t+h-168*ceil(h/168)).
- profile7: mean of the 7 most recent same-hour-of-day values at or before t, i.e. C(t+h-24*(k+j)), k=ceil(h/24), j=0..6. (Reading of "7 days before the issue hour" that keeps all leads past-only.)
- lgbm: one global LightGBM (objective L1, target = actual minus a base, base = profile7 with fallback to snaive_day then C(t), prediction clipped at 0). Features (34): lead h; CI at lags 0,1,2,3,6,12,24,48,72,168 h; rolling 24 h and 168 h mean and std (trailing, min 12 and 84 obs); target-hour hour-of-day, day-of-week, month (UTC); issue-hour hour-of-day and day-of-week; snaive_day, snaive_week and profile7 values for the target hour; 9 fuel shares at the issue hour; BA as categorical code.
- Training set: TRAIN issues with stride 9 h (stride chosen so rows stay below 3 M), 12 random leads per issue (seed 42): 2,369,216 training rows, 213,276 validation rows. Early stopping (patience 50) on the last 6 months of TRAIN (issues from 2024-01-01, targets before 2024-07-01). Best iteration 506 (max 1500), validation residual MAE 33.06.
- Hyperparameters (logged): learning_rate 0.08, num_leaves 63, min_data_in_leaf 200, feature_fraction 0.8, bagging_fraction 0.7 (freq 1), lambda_l2 1, max_bin 255, seed 42 (all seeds), deterministic, 20 threads. No tuning beyond this single configuration. No refit on the full TRAIN after early stopping.
- Top gain features: s168 (0.48), s24, ba_code, lag0, m168, profile7, h.
- Inference one BA at a time, float32, chunks of 1200 issues; peak RAM well under 3 GB. Rows with NaN C(t) (BA has no data yet) get NaN forecasts; none for lgbm in the 37 BAs.

## Leakage checks (each stated)
1. Future-perturbation test (`forecast_leakcheck.py`): for 3 BAs x 5 random issue hours in DEV+TEST x all 5 models, every CI and share value after the issue hour was replaced by random noise; forecasts at that issue hour were identical (tolerance 1e-4). 0 of 75 failures. This covers lags, rolling windows, snaive/profile, shares and the model inference path.
2. lgbm fitted on TRAIN only: training-target hour < 2024-01-01 (purged so no training target falls in the validation window), validation rows have issue >= 2024-01-01 and target < 2024-07-01. Code asserts target < TRAIN_END; DEV and TEST values never enter fitting, scaling (no scaling is used), feature selection or early stopping.
3. No normalisation or statistics are computed over the whole series; rolling statistics are trailing.
4. Calendar features of the target hour are known at issue time (deterministic), not leakage.
5. Skill scored on DEV only: issues in 2024-07-01..2025-06-30 and target hours before 2025-07-01 (leads that would reach into TEST are excluded). No TEST skill was computed or looked at. Stored forecasts cover TEST issue hours but they were not scored.
6. All models are scored on the identical cell set (a cell counts only if actual and all five forecasts are finite): 209,940 cells per BA for 1-24 h.
Caveat: the A06 clean series for DEV/TEST uses flag 3 (previous-week fill) and interpolation; both are past-only for the fill value, but interpolated short gaps (flag 1) use the next observation. Features at issue hour use whatever the clean series holds at times <= t, so a flag-1 value at t or earlier may contain information from up to 3 h later. This is a property of A06 cleaning, affects <1 % of hours, and is not fixed here; the controller should know it.

## Run time
Whole run 295 s (data 5 s, LightGBM fit 28 s on 20 threads, inference plus skill about 7.5 s per BA). Reproducible with fixed seed.

## DEV MAE (g/kWh), lead buckets, 37 BAs
Pooled (cell-weighted over BAs):

| model | 1-6 | 7-24 | 1-24 | 25-48 | 49-96 |
|---|---|---|---|---|---|
| lgbm | 19.9 | 27.6 | 25.7 | 32.0 | 35.2 |
| profile7 | 32.8 | 32.8 | 32.8 | 35.2 | 37.6 |
| snaive_day | 31.3 | 31.3 | 31.3 | 37.4 | 41.2 |
| snaive_week | 45.4 | 45.4 | 45.4 | 45.4 | 45.4 |
| persistence | 28.9 | 47.0 | 42.5 | 50.0 | 53.6 |

Median over BAs:

| model | 1-6 | 7-24 | 1-24 | 25-48 | 49-96 |
|---|---|---|---|---|---|
| lgbm | 17.3 | 22.7 | 21.7 | 26.1 | 29.6 |
| profile7 | 28.3 | 28.3 | 28.3 | 30.0 | 32.4 |
| snaive_day | 23.8 | 23.8 | 23.8 | 29.9 | 35.7 |
| snaive_week | 37.8 | 37.8 | 37.8 | 37.9 | 37.8 |
| persistence | 26.8 | 39.1 | 35.5 | 44.6 | 47.0 |

Median MAPE (1-24 h): lgbm 0.074, profile7 0.095, snaive_day 0.089, persistence 0.129, snaive_week 0.135. RMSE and MAPE per BA and bucket are in the table.
Mean within-window rank skill (Spearman over each 24 h window; windows 1-24, 25-48, 49-96 = mean of 49-72 and 73-96): lgbm 0.593, 0.555, 0.543; profile7 0.561, 0.551, 0.542; snaive_day 0.502, 0.470, 0.455; snaive_week 0.458 throughout; persistence defined as 0 (constant window). Rank skill is NaN for buckets 1-6 and 7-24 (shorter than a window).
Per BA (1-24 h MAE): lgbm beats snaive_day in 32 of 37 BAs and profile7 in 36 of 37.

Honest reading: lgbm gains over the best simple baseline (snaive_day) are 18 % at 1-24 h pooled, mostly from leads 1-6 (36 %) where it uses current state; at 49-96 h the gain over profile7 is only 6 %, and rank skill of lgbm and profile7 is nearly equal there (0.543 vs 0.542). Persistence is poor beyond 6 h, as expected.

## Items for the controller
- Skill table has extra bucket "1-24" and column `n` (cells) so pooled values can be rebuilt as sum(MAE*n)/sum(n).
- If A06 re-issues `ci_clean`/eligibility, rerun the same command (about 5 minutes).
- Dev-mode run on `ci_hourly_v0` should not be used for results.
