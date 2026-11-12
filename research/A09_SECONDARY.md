VERDICT: A09 done; all six secondary items computed on TEST (42 BAs x 3 traces x S 2/6/12/24); check saving(lgbm|req) S12 PM100 w = 0.018961 matches 0.0190 in analysis_TEST_PM100_w.json.

Script: src/secondary.py (reads results/sim_TEST and sim_TEST_nearlimit only, no re-simulation; 20 s run; results/_secondary_cache.pkl is a local aggregate written by the script itself). Tables: tables/secondary_*.csv (retained_share, delay, all_arms, best_vs_D, nearlimit, spearman_character, per_ba_S12, ba_character_TEST, forecast_mae, forecast_mae_summary, forecast_gap_spearman). Ledger: tables/ledger_TEST_secondary.csv (2024 rows, key,value,source).
Aggregation: plain sums over BAs, days, classes and the 3 replicates (day alignment only matters for the bootstrap, not for point savings). Numbers below are energy-weighted (w) unless stated; u is in the csvs.

## Check
saving(lgbm|req), TEST PM100 w S12 recomputed = 0.018961, rounds to 0.0190. Matches results/analysis_TEST_PM100_w.json (0.018961).

## 1. Retained share (secondary_retained_share.csv; pooled, per BA, per class, w and u)
Pooled, retained = saving(lgbm|req) / saving(oracle|act); in brackets lgbm|pred / oracle|act.
- PM100: S2 0.251 (0.402); S6 0.264 (0.439); S12 0.330 (0.509); S24 0.311 (0.494).
- FDATA S12 0.528 (0.602). KIT_FH2 S12 0.376 (0.463).
PM100 S12 by class (lgbm|req share; pred share; oracle|act saving; jobs over 3 reps x 42 BAs):
- <1 h: 0.383; 0.653; 0.106; 1,755,206 jobs
- 1-4 h: 0.357; 0.623; 0.094; 407,893
- 4-12 h: 0.394; 0.551; 0.090; 155,695
- >=12 h: 0.267; 0.406; 0.039; 201,206
Pattern: the longest jobs retain least and have the smallest oracle saving (0.039 vs 0.106 for <1 h at S12). On FDATA the 1-4 h class retains most (0.644). On KIT_FH2 the 1-4 h class retains least (0.188 at S12, 254,946 jobs) while 4-12 h retains 0.447.
Per BA, PM100 S12: 41 of 42 BAs have a defined share (median 0.329, IQR 0.255-0.382, min 0.068, max 0.485). SPA has oracle saving exactly 0 (constant intensity) in all three traces, so its share is undefined (NaN). No BA has a negative lgbm|req saving at S12.
Job counts per trace are the same for every S: 2,520,000 per trace (42 BAs x 3 reps x 20,000). Class counts (<1, 1-4, 4-12, >=12 h): FDATA 1.35M / 0.68M / 0.23M / 0.26M; KIT_FH2 1.59M / 0.25M / 0.35M / 0.32M. Per-BA per-class cells are small (a BA has about 60,000 jobs in total), so per-BA class rows are noisy.

## 2. Spearman across the 42 BAs, S12, w (secondary_spearman_character.csv)
Caveat: tables/ba_coverage.csv spans 2018-07 to 2026-07, not TEST only. I also recomputed the four characters on TEST hours (2025-07-01 to 2026-06-30): daily range from ci_clean flag 0-3 on UTC days with at least 20 usable hours, median over days; shares are generation-weighted means from ci_hourly, fossil = coal + gas + oil (secondary_ba_character_TEST.csv). I did not check whether ba_coverage defines the shares the same way. Both versions are in the csv (column character_source) and agree in sign and size.
TEST-hours values, PM100:
- saving(oracle|act): daily range rho 0.82 (p 4e-11); solar 0.76 (p 8e-9); wind 0.66 (p 2e-6); fossil -0.45 (p 0.0025).
- runtime penalty saving(lgbm|act) - saving(lgbm|req): daily range 0.70 (p 3e-7); solar 0.87 (p 9e-14); wind 0.17 (p 0.28); fossil -0.29 (p 0.064).
Coverage-period version, PM100: oracle saving vs range 0.87, solar 0.75, wind 0.64, fossil -0.27 (p 0.083); penalty vs range 0.63, solar 0.85, wind 0.18, fossil -0.19. FDATA and KIT_FH2 are very similar (oracle saving vs range 0.81 and 0.80; penalty vs solar 0.83 and 0.86, TEST hours). The fossil association with oracle saving is weaker under the coverage-period characters (p 0.05-0.08). Solar and wind shares are zero for many BAs (median 0.02 and 0), so those rank correlations rest on many ties. Descriptive, unadjusted for multiple comparisons.

## 3. Delay cost (secondary_delay.csv; mean start delay h = sum delay / sum n)
PM100 S12: night 4.42; oracle|act 5.38; oracle|req 5.60; lgbm|act 5.23; lgbm|req 5.50; snaive_day|req 4.84. lgbm|req at S2 0.86, S6 2.62, S24 12.32. FDATA S12 lgbm|req 5.84; KIT_FH2 5.36. Delay is about 0.46 S at S12 and 0.51 S at S24. The deployable arm waits about as long as the oracle. The night rule delays 4.4 h at S12 for 0.003 saving.

## 4. All arms (secondary_all_arms.csv; best vs D in secondary_best_vs_D.csv)
PM100 w S12, saving: oracle|act 0.0575, oracle|req 0.0333, oracle|pred 0.0418; lgbm act/req/pred/pred2 0.0408 / 0.0190 / 0.0293 / 0.0237; profile7|req 0.0111; snaive_week|req 0.0116; snaive_day|req 0.0096; histprofile|req 0.0073; night 0.0029; persistence|req -0.0020 (persistence is negative under every runtime estimate at S12, -0.0036 to -0.0020).
D = lgbm|req beats every other non-oracle-signal arm that uses the requested runtime, in every trace and slack. The best other deployable arm (no oracle signal, no oracle runtime) is lgbm|pred in every trace, weight and slack: PM100 S12 +0.0103 over D (0.0293 vs 0.0190); FDATA S12 +0.0053; KIT_FH2 S12 +0.0035. Across all slacks and traces the margin is +0.0002 to +0.0158 (w). Counting lgbm|act (oracle runtime, not deployable) the margin is +0.0218 (PM100 S12 w). The csv has both sets (column set: deployable, any_nonoracle_signal).

## 5. Forecast skill on TEST (secondary_forecast_mae*.csv)
Target for fc[i,h-1] is ci_clean at grid index t+h (per src/forecast.py and simcore: interval k carries ci[k]), flags 0-3 only, TEST issues. Median over BAs of MAE (g/kWh) for leads 1-6 / 7-24 / 25-48 / 49-96:
- lgbm 18.6 / 22.8 / 26.8 / 30.6
- profile7 27.8 / 27.9 / 30.6 / 33.3
- snaive_day 24.0 / 24.0 / 30.5 / 35.4
- snaive_week 39.3 / 39.4 / 39.4 / 39.5
- persistence 27.5 / 46.6 / 50.2 / 53.4
LightGBM 1-24 h MAE is lower than snaive_day in 37 of 42 BAs, than profile7 in 41, persistence in 40, snaive_week in 41 (PREREG cites 38 and 41 for DEV).
Spearman across BAs of lgbm 1-24 h MAE vs the forecast term saving(oracle|req) - saving(lgbm|req): PM100 S2/S6/S12/S24 rho 0.62 / 0.69 / 0.78 / 0.82; MAE relative to the BA TEST mean intensity 0.76 / 0.89 / 0.93 / 0.95 (all p < 0.001). FDATA S12 0.69 (relative 0.83); KIT_FH2 S12 0.75 (0.91). Caveat: the gap is large where the oracle saving is large (volatile, solar-heavy BAs), and those BAs also have large MAE, so the correlation is confounded by headroom and does not isolate forecast quality. Within-window rank skill (PREREG item 7) was not computed; the brief asked for MAE by lead only.

## 6. Near-limit sensitivity (secondary_nearlimit.csv; w)
PM100 S12, main vs near-limit-excluded: oracle|act 0.0575 vs 0.0636; oracle|req 0.0333 vs 0.0345; lgbm|act 0.0408 vs 0.0462; lgbm|req 0.0190 vs 0.0210; lgbm|pred 0.0293 vs 0.0333; lgbm|pred2 0.0237 vs 0.0269. Excluding jobs with R_act >= 0.98 R_req raises every saving slightly; lgbm|req rises by 0.0001 to 0.0035 across the 12 trace x slack cells (mean 0.0018). In all 24 trace x slack x variant cells the ordering oracle|act > oracle|req, lgbm|pred > lgbm|req, lgbm|act > lgbm|req holds. The runtime penalty lgbm|act - lgbm|req at PM100 S12 rises from 0.0218 to 0.0252. n_jobs is identical in both runs (2,520,000 per trace) because the near-limit run removed those jobs before sampling.

## Caveats and oddities
- SPA: oracle saving exactly 0 (constant intensity) in all traces; retained share undefined there, per-BA shares use 41 BAs.
- Per-BA class cells are small; pooled shares are stable.
- ba_coverage.csv is 2018-2026; TEST-hours recomputation reported alongside.
- Point estimates only; no intervals computed. Spearman p-values unadjusted.
- Forecast-gap association is confounded by headroom (item 5).
- src/analyze.py, src/simulate.py and PREREG.md untouched; TEST not re-run.
