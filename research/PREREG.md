# Pre-registration, Paper A (SUSCOM): realised carbon saving of carbon-aware batch scheduling

Status: FROZEN 2026-11-11 IST after Codex R03 (do not freeze, fixes) and R04 (freeze after fixes, all applied). Freezing wrote `research/PREREG.md5`;
`src/simulate.py` refuses the TEST period unless that md5 matches this file. Code at freeze: `src/simcore.py` e1032a51dfa070b9787b490936050ef4, `src/simulate.py` 1ede008932d484fff6753ce5f9345bbb, `src/analyze.py` 8178e63f4d6d09023836c4c3bee2efdc, `src/forecast.py` 3cc0e9ca068eaa35077c2be89acaba6b, `src/prep_jobs.py` 6a1fc5cb5d05649ce2f8acc99c28357d.
Any change after the freeze goes into the deviations table (section 9), with reason and time.

## 1. Question
For non-interruptible batch jobs that a scheduler may delay within a slack window to lower-carbon hours, how much of
the perfect-information carbon saving is realised when the scheduler uses (a) a past-only forecast of grid carbon
intensity and (b) the user's requested walltime, or a history-based runtime prediction, instead of the actual runtime?

## 2. Data
- Grid: EIA-930 six-month BALANCE files 2018 H2 to 2026 H1 (public domain), SHA-256 in
  `data/raw/eia930/SHA256SUMS.txt`. Hourly production-based average intensity per balancing authority (BA) with the
  lifecycle factors in `src/emission_factors.csv` (IPCC AR5 WGIII Annex III Table A.III.2 medians; oil, other and
  unknown are documented judgement values, generation share small). Built by `src/build_ci.py`, cleaned by
  `src/clean_ci.py --final` (rules in `research/A06_DATA_AUDIT.md`). Eligible BAs: the 42 in
  `tables/ba_eligibility.csv` (md5 8fe037d0b2f50778057e6668ec040927). Frozen rule: first valid hour on or before
  2018-09-01 and last valid hour on or after 2026-06-30 23:00 UTC; at least 90 % valid hours in each of TRAIN, DEV and
  TEST (D0003; the v0 audit used 95 %); mean generation over valid hours >= 100 MW; TRAIN standard deviation of the
  cleaned intensity > 1 g/kWh. Input hashes: `data/derived/ci_clean.parquet` a77ee0385f8a5d251ae4dd19a334afa1,
  `data/derived/jobs.parquet` 95c96a3353eae71b2190ebc2c1aa7bae, `src/emission_factors.csv`
  8c5c21e790f966d6f3b9af95c11c8eff.
- Jobs: PM100 (Marconi100, CC-BY-4.0, doi 10.5281/zenodo.10127767), primary; F-DATA (Fugaku, CC-BY-4.0, months
  2021-04, 2023-01, 2023-04, 2023-07, 2023-10) and KIT FH2 (Parallel Workloads Archive), secondary. KIT FH2 has no
  power data, so its jobs carry 1 kW each (energy weight proportional to runtime). Trace audit:
  `research/A07_JOBS.md`. Standardised by `src/prep_jobs.py`
  (`data/derived/jobs.parquet`). NLR Kestrel enters as a secondary trace only if obtained and licence-checked before the
  freeze.
- Job power: PM100 and F-DATA give a whole-job mean power (PM100: mean of the sampled job power series; F-DATA:
  avgpcon), used as constant power over the run; never multiplied by node count.
- Job filter (main): state COMPLETED; actual runtime >= 1 min; requested walltime <= 72 h and > 0.

## 3. Periods and leakage rules
- TRAIN 2018-07-01 to 2024-06-30: forecaster fitting, tuning, early stopping, historical profile.
- DEV 2024-07-01 to 2025-06-30: all design choices and pilots.
- TEST 2025-07-01 to 2026-06-30: scored once, after the freeze.
- Forecasts at arrival time a use only data up to the hour ending floor(a) (causal inputs; future-perturbation test
  in `research/A05_FORECASTS.md`). Runtime prediction for a job uses only the same user's jobs that ended before its
  submission (assertion in `src/prep_jobs.py`).
- Assumption stated as a limitation: grid data for the hour ending floor(a) is available at time a (EIA-930 publishes
  with a delay of hours in practice).

## 4. Scheduler and arms (`src/simcore.py`, `src/simulate.py`)
- Job: arrival a, requested walltime R_req, actual runtime R_act, mean power P. Slack S in {2, 6, 12, 24} h: the start
  s may be any of a, a + 0.25 h, ..., a + S. The planner minimises the integral of its signal over [s, s + R_hat],
  seeing the 98 hourly intervals from floor(a) (same width for every signal; it covers frac(a) + 24 + 72 < 98 h).
  Forecasts have leads 1-96 (intervals 0-95); intervals 96-97 hold the lead-96 value. Ties go to the earliest start.
  Jobs whose 98 h window touches an unusable grid hour are excluded.
  Realised emissions = P x integral of the actual intensity over [s, s + R_act].
- Signals: oracle (actual intensity), persistence, seasonal naive day, seasonal naive week, profile7, LightGBM (global,
  horizon as feature), historical profile (TRAIN mean by month and local hour).
- Runtime estimates: act (R_act, oracle), req (R_req), pred (mean actual runtime of the user's two most recent jobs
  that ended before this job's submission with state COMPLETED or TIMEOUT, capped at R_req; R_req if no history); pred2 = min(R_req, 2 x pred),
  secondary (k = 2 fixed before any TEST result, not tuned).
- Non-forecast baselines: run-now (s = a); night rule (earliest start in local hours 00:00-03:59 within slack, else
  now).
- Random calendar alignment: each sampled job is placed in a random week of the period with its own local weekday and
  clock time, in the BA's standard local time. 3 alignment replicates x 20,000 jobs per BA per trace (or all jobs if
  fewer), fixed seed 20261111.

## 5. Outcomes and estimands
- saving(arm) = 1 - sum E_arm / sum E_runnow, pooled over BAs, days and replicates; E energy-weighted with the
  trace's whole-job mean power (PM100). Unweighted variant (each job 1 kW) secondary.
- Deployable arm D = lgbm|req, selected on DEV because the final LightGBM had lower 1-24 h MAE than seasonal naive day
  in 38 of 42 BAs and lower than profile7 in 41 of 42 (`tables/forecast_skill.csv`); no TEST skill or outcome informed
  this choice.
- Primary slack S = 12 h; others secondary.
- Inference target: this fixed set of 42 eligible BAs (selected on coverage, not sampled), over the TEST year. BA
  heterogeneity is reported descriptively.

## 6. Confirmatory hypotheses (TEST, PM100, energy-weighted, S = 12 h, the fixed set of 42 BAs)
- H1: saving(lgbm|req) > 0.
- H2 (runtime penalty): saving(lgbm|act) - saving(lgbm|req) > 0.
- H3 (prediction recovery): saving(lgbm|pred) - saving(lgbm|req) > 0.
Test (`src/analyze.py --boot fixed`): stratified block bootstrap with all 42 BAs kept in every replicate; within each
BA, 7-day blocks of arrival days are resampled with replacement (blocks are consecutive from the BA's first arrival day
after replicate days are aligned and summed; the remainder of fewer than 7 days is a short block kept unchanged in
every replicate). The two-stage bootstrap (secondary 12) targets a different, hypothetical BA population and is shown
beside each confirmatory estimate, not as a second confirmation. B = 2000, seed 7 + S. One-sided
null-centred p = (1 + #{T* - T >= T}) / (B + 1), where T is the estimate and T* a bootstrap replicate; Holm over H1-H3
at alpha = 0.05. A hypothesis is supported when its Holm-adjusted p < 0.05; the 95 % percentile interval is reported
for every estimate. The DEV pilot p-values computed before R03 (uncentred) are void.

## 7. Secondary analyses (descriptive, no confirmatory claim)
1. Shapley decomposition of the gap saving(oracle|act) - saving(lgbm|req) into forecast and runtime terms (2x2,
   symmetric allocation of the interaction; all four cells reported).
2. Retained share saving(lgbm|req) / saving(oracle|act) and the same for pred, by BA, slack and job-length class
   (< 1 h, 1-4 h, 4-12 h, >= 12 h).
3. Per-BA H2 counts: estimate > 0, and 95 % within-BA interval above 0.
4. Cross-BA association of the oracle saving and of the runtime penalty with BA character (median daily intensity
   range, solar share, wind share, fossil share): Spearman correlations.
5. Every forecaster and the non-forecast baselines under each runtime estimate; best simple policy vs D.
6. Secondary traces (F-DATA, KIT FH2; Kestrel if present), unweighted outcome, slacks 2, 6, 24 h, and TIMEOUT jobs
   included.
7. Forecast skill on TEST (MAE by lead, within-window rank skill) and its association with realised saving across BAs.
8. Delay cost: mean start delay per arm.
9. Interaction (demoted from confirmatory on Codex R03 advice, before TEST): [saving(oracle|act) -
   saving(oracle|req)] - [saving(lgbm|act) - saving(lgbm|req)], estimate and 95 % interval, two-sided null-centred p
   unadjusted and descriptive.
10. pred2 = min(R_req, 2 x pred) under every signal.
11. Censoring sensitivity: jobs with R_act >= 0.98 R_req excluded (`--exclude-near-limit`), all arms.
12. Inference sensitivity: two-stage bootstrap (BAs with replacement, then blocks within BA), read as uncertainty over
    a hypothetical population of eligible BAs.
Scope note: the planner is the delay-to-lowest-integral policy used in prior temporal-shifting studies (Wiesner et al.
2021; Sukprasert et al. 2024); no other published scheduler is reimplemented.

## 8. What counts as a negative result
- If H1 fails, deployable carbon-aware delay scheduling gives no significant saving on these grids at 12 h slack; this
  is reported as the main finding.
- If H2 fails, requested walltime costs no significant saving; the paper reports the size bound.
- If H3 fails, the history predictor does not recover saving; reported plainly.
- Results that hold on DEV but not on TEST are reported as not confirmed.

## 9. Deviations after freeze
| # | time | change | reason |
|---|---|---|---|
