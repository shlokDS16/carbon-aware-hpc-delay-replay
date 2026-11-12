# P4 plan, Paper A (2026-11-12 01:30 IST): post-freeze exploratory sensitivities

All items are post-freeze and EXPLORATORY: confirmatory H1-H3 stay as frozen (tables/ledger_TEST.csv). Frozen files
(src/simcore.py, simulate.py, analyze.py, forecast.py, prep_jobs.py) are NOT edited; new code goes in new files
(src/sens_*.py) that import them. Every item gets a row in research/PREREG_DEVIATIONS.md (time, change, reason) and
writes its own ledger tables/ledger_TEST_sens_<item>.csv (key,value,source; keys prefixed `sens.<item>.`).
Result dirs use the `--tag _sens_<item>` pattern. Report each item beside the frozen value (PM100, energy-weighted,
S = 12 h first; then F-DATA, KIT FH2).

RESOURCE GATE: before each heavy run, at least 6 GB physical RAM free and commit below 85 % (2026-11-12 01:30: 2.5 GB
free, commit 96.3/97.6 GB, held mostly by two patent training runs PIDs 60460, 77520 and Paper B's queued HPO). Add a
row to _shared/GPU_SCHEDULE.md; one heavy job at a time across both papers. Never kill other projects' processes.

| id | A08 threat / rule | item | method | cost |
|---|---|---|---|---|
| S1 | intervals too tight (job sample fixed) | sampling-inclusive uncertainty | (a) spread of D, H2, H3 across the 3 alignment replicates (already in npz?); (b) rerun TEST with new job-sample and alignment seeds (5 extra seeds, lgbm/oracle x act/req/pred arms only), report the across-seed SD and a combined interval (bootstrap over seeds x blocks) | CPU, ~1-2 h, ~2 GB |
| S2 | EIA publication delay | data-latency sensitivity | planner sees only data up to floor(a) - k for k in {1, 3, 6} h: use the LightGBM forecast issued at floor(a) - k with leads shifted by k (forecast table already holds those issues); oracle unchanged | CPU, light |
| S3 | average signal, factors | emission-factor sensitivity | rebuild intensity with direct (combustion) factors and with the oil factor 1116 vs 650 g/kWh; rerun oracle and lgbm arms (lgbm forecasts are of lifecycle intensity: forecast must be refit or the run limited to oracle arms; decide in code review) | CPU, medium |
| S4 | PREREG secondary 6 not run (deviation 2) | TIMEOUT-included jobs | `--states COMPLETED,TIMEOUT`, PM100 only, all arms | CPU, ~30 min |
| S5 | owner rule 12 (research-grade HPO) | tuned forecaster | Optuna TPE on TRAIN only (time-split validation = last 6 months of TRAIN, as frozen), fixed trial budget (e.g. 60 trials), objective 1-24 h MAE; refit; regenerate TEST forecasts; rerun lgbm arms; report D, H2, H3, Shapley split and MAE beside frozen | CPU 24 threads, ~1-2 h, ~2-3 GB |
| S6 | foreign traces on US grids | limitation text only | state plainly; note PM100/F-DATA/KIT arrivals placed in BA local time; results by trace already reported | none |

Order: S4, S2 (light) when RAM allows; then S1, S5; S3 last. Codex round R05 (single thread) on the S1-S5 design
before running; panel review (SUSCOM editor, domain referee, statistics referee persona agents) after the journal
PDFs are analysed.

Owner-rule items to carry into P5-P8 (D0012): AI use only in the AI-declaration section; writers' room; blue DOI
links; private GitHub (owner gives link); manual Zenodo guide; position against SUSCOM A1-A5
(_shared/PAYWALLED_SUSCOM_LANE_A.md); Elsevier template exactly; author placeholders.


## v2 SETTINGS, FIXED BEFORE ANY RUN (Codex R05: RUN WITH CHANGES, 0.91; adopted 2026-11-12 02:45 IST, D0013)
These settings are fixed now; the md5 of this file is written to research/P4_PLAN.md5 before the first S-run, and
every setting below is reported whatever it shows. All items are post-freeze exploratory sensitivities; the frozen
TEST estimates, H1-H3, D and the abstract headline are not changed by them, and no sensitivity is promoted.

- Arms common to S1-S5 unless stated: lgbm|req, lgbm|act, lgbm|pred, oracle|act, oracle|req (D, H2, H3, Shapley).
  S = 12 h primary; energy-weighted; the frozen fixed-BA estimand (BAs are not resampled).
- S1 user-cluster uncertainty: outer bootstrap over users (clusters) with replacement per trace (users after the frozen main
  filter, counted 2026-11-12 from data/derived/jobs.parquet: PM100 394, F-DATA 1,257, KIT FH2 165; Codex's 477 was
  not from our data), then 20,000 eligible jobs per BA drawn from the
  resampled pool, then the frozen 7-day block bootstrap within BA on that sample (B = 200 inner per outer sample).
  30 outer samples, seeds 20261112-20261141, one alignment replicate per outer sample (cost; stated). Report per
  trace: the combined percentile interval of D, H2, H3 and the Shapley terms over all outer x inner draws, and the
  outer-only spread separately. If 30 outer samples do not fit the machine, report the completed number and label the
  result Monte Carlo sensitivity, not a corrected interval.
- S2 data latency: the planner sees data up to floor(a) - k, k in {1, 3, 6} h (forecast issued at floor(a) - k, leads
  shifted by k; the forecast table holds those issues). Arms lgbm|req, lgbm|pred, snaive_day|req; oracle unchanged and
  labelled an upper bound. All three traces; every k reported.
- S3 accounting signal: (a) direct (combustion) factors for coal, gas, oil from the source cited in
  src/emission_factors.csv (if no direct-factor source is in hand, the IPCC 2006 stationary-combustion defaults, cited);
  (b) lifecycle factors with oil 1116 instead of 650 g/kWh. For each: rebuild CI with src/build_ci.py logic, refit the
  frozen LightGBM pipeline with UNCHANGED hyperparameters, splits and seeds, regenerate TEST forecasts, rerun
  lgbm|req and oracle|act (plus lgbm|act, lgbm|pred for Shapley) on all traces. Imports and storage stay excluded and
  this is stated. Both factor sets reported.
- S4 TIMEOUT included: PM100 only, states COMPLETED,TIMEOUT, all frozen arms, frozen seeds; descriptive only (timeout
  runtimes are limit-censored).
- S5 tuned forecasters: Optuna TPE, 100 trials, sampler seed 20261112, objective mean MAE at leads 1-24 h on the frozen
  TRAIN validation window (issues 2024-01-01 to targets before 2024-07-01), no DEV or TEST data. Space: num_leaves
  15-127, max_depth 3-10, learning_rate 0.01-0.15 (log), min_data_in_leaf 50-1000 (log), feature_fraction 0.6-1.0,
  bagging_fraction 0.6-1.0, lambda_l1 and lambda_l2 1e-4 to 10 (log), max_bin 63-255. Iteration count by early stopping
  on the same window; then refit with the selected settings and iteration count on full TRAIN. Rivals tuned on the same
  window: profile7 lookback in {1, 3, 7, 14, 28} days; snaive day vs week compared (no parameters). Report the TEST
  MAE of tuned and frozen forecasters and D, H2, H3, Shapley under the tuned LightGBM, all traces, beside the frozen
  values.
- S6 limitation text only (foreign traces on US grids; counterfactual replay, no queue capacity; revised EIA data;
  imports and storage excluded). The abstract and title must not overstate real-world reductions (EDITOR R05 q4).
- Every run: command, seed, code md5, input md5 and a PREREG_DEVIATIONS.md row; outputs tables/ledger_TEST_sens_<id>.csv.
- Cost order: S4, S2 (light); S5 HPO (CPU, about 2-3 GB); S3 (refit x2); S1 last (largest). Time one S1 outer sample
  first and extrapolate before committing to 30.
