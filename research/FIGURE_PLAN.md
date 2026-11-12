# Figure plan, Paper A (draft 2026-11-11 20:15 IST; numbers only from ledgers)

Style: matplotlib + seaborn, Okabe-Ito, 300 dpi PNG + vector PDF, text >= 7 pt at final size (single column 90 mm,
double 190 mm), no overlaps, even spacing. Arms colour-coded consistently: oracle|act, oracle|req, lgbm|act, lgbm|req
(D), lgbm|pred, lgbm|pred2, baselines grey. All TEST unless stated.

| # | content | source |
|---|---|---|
| 1 | Schematic: job arrival, slack window, planner over a forecast, realised over actual; the 2x2 information design (signal x runtime estimate) | diagram |
| 2 | The 42 BAs: median daily intensity range vs mean intensity, point size = generation, colour = solar share | tables/secondary_* (TEST-hour characters), ba_coverage.csv |
| 3 | Job traces: ECDF of r_act/r_req per trace; inset share of jobs by length class | data/derived/jobs.parquet (filtered as in PREREG) |
| 4 | Example: one BA, one week, actual intensity and LightGBM forecast issued at an arrival; start chosen under act vs req and realised intervals | ci_clean, forecasts/lgbm |
| 5 | Forecast skill on TEST: MAE by lead bucket per model (median and IQR over BAs) | tables/secondary_* (item 5) |
| 6 | Main result: savings vs run-now for all arms at S = 12 h, three traces, with 95 % intervals (fixed and two-stage) | ledger_TEST.csv |
| 7 | Shapley decomposition of the gap oracle|act -> lgbm|req: forecast, runtime, interaction, per trace | ledger_TEST.csv |
| 8 | Saving vs slack (2, 6, 12, 24 h) for the four 2x2 cells plus pred, PM100 (panels for F-DATA, KIT) | ledger_TEST.csv |
| 9 | Per-BA forest: H2 runtime penalty with within-BA interval, sorted; marker for oracle saving | analysis_TEST_PM100_w.json per_ba |
| 10 | Retained share by job-length class and trace | tables/secondary_* (item 1) |
| 11 | Cross-BA: oracle saving vs daily range, colour = solar share, Spearman in panel | secondary_* (item 2) |
| 12 | Cross-BA: runtime penalty vs solar share | secondary_* (item 2) |
| 13 | Delay cost vs saving per arm (mean start delay, h) | secondary_* (item 3) |
| 14 | Robustness: D and H2 under near-limit exclusion, unweighted, two-stage bootstrap, DEV vs TEST, and post-freeze sensitivities (labelled exploratory) | ledgers |

Tables (4-6): T1 related work (information assumptions per paper); T2 data (BAs, traces, periods); T3 arms and
estimands; T4 confirmatory results H1-H3 (+H4 secondary); T5 secondaries summary; T6 sensitivity grid.
