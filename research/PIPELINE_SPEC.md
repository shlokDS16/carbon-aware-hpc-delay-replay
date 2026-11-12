# Paper A pipeline spec (contract for all agents; v1 2026-11-11)

Study (C8): realised carbon saving of carbon-aware delay scheduling of batch jobs under past-only carbon forecasts and
real user runtime estimates. Grid: EIA-930 hourly production-based intensity per US balancing authority (BA).

## Periods (UTC, end-of-hour timestamps as in EIA-930)
- TRAIN: 2018-07-01 to 2024-06-30 (forecaster fitting and tuning only).
- DEV: 2024-07-01 to 2025-06-30 (design choices, pilots, forecaster selection; may be looked at).
- TEST (held out, scored once after PREREG freeze): 2025-07-01 to 2026-06-30.
- Forecasts used in DEV/TEST are issued from information up to and including the issue hour only.

## Files
- `data/derived/ci_hourly[_v0].parquet`: ba, region, utc, ci (g/kWh), gen_total_mw, share_<fuel>, demand_mw.
- `data/derived/ci_clean[_v0].parquet` (A06): ba, utc (complete hourly grid per eligible BA), ci_clean, flag
  (0 ok, 1 interpolated short gap <= 3 h, 2 outlier replaced, 3 long gap filled by same-hour-previous-week).
- `tables/ba_eligibility[_v0].csv` (A06): ba, eligible (bool), reason, stats.
- `data/derived/forecasts/<model>/<BA>.npz` (A05): arrays `issue_utc` (int64 ns, hourly, DEV+TEST span),
  `fc` float32 [n_issue, 96] where fc[i, h-1] is the forecast of the hour ending at issue_utc[i] + h hours,
  h = 1..96. Models: `persistence`, `snaive_day`, `snaive_week`, `profile7` (mean of same hour over the previous 7
  days), `lgbm` (global LightGBM, horizon as feature, trained on TRAIN, early stopping on the last 6 months of TRAIN
  only), `oracle` is NOT stored (the simulator reads actuals).
- `tables/forecast_skill[_v0].csv` (A05): model, ba, period, lead_bucket, MAE, RMSE, MAPE, and within-window rank
  skill (Spearman between forecast and actual over each 24 h window).

## Simulator (controller writes `src/simulate.py`)
- Job: arrival a, requested walltime R_req, actual runtime R_act, nodes n, power P (W per node, trace or constant).
- Slack S in {2, 6, 12, 24} h = latest allowed start a + S. Candidate starts every 15 min.
- Planner sees at time a: signal (oracle actual CI, or forecast issued at floor_hour(a)) and runtime estimate
  (R_act oracle, R_req, or R_pred from user history before a). Chooses start minimising the integral of the signal over
  [s, s + R_hat]. Realised emissions = n * P * integral of actual CI over [s, s + R_act]. Saving vs run-now (s = a).
- Arms: signal {oracle, persistence, snaive_day, profile7, lgbm} x runtime {actual, requested, predicted}.
- Non-forecast baselines: run-now, fixed night window (start at the next 00:00-04:00 local slot within slack else now),
  historical clean-hour profile (TRAIN mean by hour of day and month).
