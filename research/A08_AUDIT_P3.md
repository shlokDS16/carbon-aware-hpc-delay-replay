VERDICT: PASS WITH ISSUES; 0 blocking issues (3 MAJOR threats to state or supplement in the paper, 7 MINOR)

# A08 research audit, Paper A (SUSCOM), P3/TEST gate (2026-11-11)

Scope: frozen PREREG, the TEST run (`results/sim_TEST`, `results/sim_TEST_nearlimit`) and the TEST analysis (`results/analysis_TEST_*.json`, `tables/ledger_TEST.csv`). Read only; `src/simulate.py` was not run. My own checks used only cheap numpy and pandas reads of cleaned inputs, forecast files and result files (scripts in the session scratchpad). All paths are relative to `paper_A`. Nothing below suggests re-scoring TEST under changed rules; anything added goes into PREREG section 9 as post hoc.

## 1. Table of checks

| # | Check | Result | Evidence |
|---|---|---|---|
| 1a | PREREG md5 equals frozen md5 | PASS | `md5sum research/PREREG.md` = cfe984017ef7c790d851bfa2f519fde3 = `research/PREREG.md5`; `simulate.check_prereg` (src/simulate.py:34-42) enforces it for TEST |
| 1b | Code md5 in PREREG status line | PASS (5 of 5 match) | simcore e1032a51..., simulate 1ede0089..., analyze 8178e63f..., forecast 3cc0e9ca..., prep_jobs 6a1fc5cb... all equal current files. mtimes: the three sim files 16:10:52, PREREG 16:12:24, TEST run finished 16:33; no code edited after the freeze |
| 1c | Input hashes in PREREG | PASS | ci_clean a77ee038..., jobs 95c96a33..., emission_factors 8c5c21e7..., ba_eligibility 8fe037d0... all recomputed and equal |
| 1d | Forecaster training, tuning, early stopping use TRAIN only | PASS | src/forecast.py:211-213 (targets < 2024-07-01, training targets < 2024-01-01, validation window 2024-01..06, purged); hyperparameters are command-line defaults, fixed; `skill_for_ba` (l.271-277) scores DEV only, TEST skill never computed in forecast.py |
| 1e | Forecast causality and time alignment with the simulator | PASS | `causal_input` (forecast.py:60-71); A05 future-perturbation test 0 of 150. My own check: for 300 random TEST arrivals in CISO, PJM, ERCO, persistence lead 1 equals ci[floor(a)-1] (97.7 to 100 %) and never ci[floor(a)]; snaive_day lead 1 equals ci[k-24]; so no look-ahead of the current hour, and `fc_window` (simulate.py:117-122) indexes the correct issue row |
| 1f | Historical profile uses TRAIN only | PASS | `hist_profile` (simulate.py:78-84) filters `utc` in TRAIN before the groupby; profile is then indexed by month and local hour only |
| 1g | Runtime predictor uses only the user's jobs that ended before submission | PASS | `history_predict` (src/prep_jobs.py:169-190, searchsorted on end < submit, states COMPLETED or TIMEOUT, two most recent, cap at R_req); naive recomputation assertion on 1,000 jobs per trace (l.193-209); the predictor is computed at trace time and does not depend on the random calendar placement |
| 1h | BA eligibility and cleaning thresholds free of outcome information | PASS with note | Rules are constants (clean_ci.py:31-39) set on data quality before any outcome. Note (MINOR M1): eligibility requires at least 90 % valid hours in TEST and data up to 2026-06-30 (clean_ci.py:161-168), so the 42 BAs are conditioned on TEST availability, not on TEST outcomes |
| 1i | Design choices (D = lgbm\|req, S = 12 h, k = 2 for pred2) fixed before TEST | PASS | D justified on DEV skill (38 of 42, 41 of 42; `tables/forecast_skill.csv`, recomputed: lgbm beats snaive_day 38, profile7 41, persistence 41, snaive_week 41 of 42); PREREG section 5; no TEST number enters any rule |
| 1j | Cleaning look-ahead | PASS with note | Outlier detection uses a centred 30-day window (clean_ci.py:73-76) so which hours are outliers depends on up to 15 later days; the forecaster inputs replace such hours by an earlier value (forecast.py:60-71), so only the flag, not a future value, leaks. Effect is negligible (MINOR M3) |
| 2a | Arms, slack set, deployable arm, job filter, seeds, reps, job count | PASS | RUN.txt: reps=3, n_jobs=20000, seed=20261111, states=COMPLETED, 42 BAs, all 3 traces; simulate.py:24-31, 229-231 (COMPLETED, r_act >= 1 min, 0 < r_req <= 72 h); rng key [seed, rep, crc(ba), crc(trace)] l.139 |
| 2b | Bootstrap mode, B, seeds, p-formula, Holm | PASS | analyze.py:159 seed 7+S; l.60-77 fixed-BA blocks of 7 days within BA, remainder kept; l.167-172 null-centred one-sided p = (1+#{T*-T >= T})/(B+1); l.96-104 Holm; l.149 Holm only over H1-H3; H4 two-sided and unadjusted; JSON: B=2000, boot=fixed, n_ba=42; two-stage files separate |
| 2c | Near-limit secondary applied | PASS | `sim_TEST_nearlimit` RUN.txt lacks the flag text but results differ (oracle\|act 6.36 vs 5.75 %, PM100 S12), counts per (BA, rep) identical because the 20,000 sample is drawn after the filter |
| 2d | Section 7 secondaries all done | PARTIAL (not blocking) | Item 6 "TIMEOUT jobs included" has no run (no `sim_TEST_*` with `--states COMPLETED,TIMEOUT`). `src/secondary.py` was written at 16:56, after the TEST run, and is not in PREREG's hash list; it is descriptive and covers section 7, so list it in progress.md as post-freeze code. Section 9 of PREREG is empty and needs no entry unless a rule changes |
| 3a | Planner and realised emissions | PASS | simcore.py:38-65 (cumulative-sum integral, candidates every 0.25 h, ties earliest, window clipped at 98), 68-70; selftest incl. brute force; 98 >= 1+24+72 = 97 so no clipping for any scored job; `assert r_act <= 72` (simulate.py:231). e_w = kW x g/kWh x h (l.168) |
| 3b | Random calendar alignment | PASS with note | simulate.py:87-105: weekday and clock time kept, standard-time offset from a January file (`tables/ba_utc_offset.csv`: 15 BAs at -5, 13 at -8, 8 at -7, 6 at -6, all 42 present). Arrival weeks run 2025-07-07 to 2026-06-14, so about 16 days of the TEST year never receive arrivals (MINOR M2). Trace wall-clock hours include the site's DST (prep_jobs.py:223-225) while placement uses BA standard time, a one-hour summer shift (MINOR M2) |
| 3c | Exclusion of jobs whose 98 h window touches unusable hours | PASS but vacuous in TEST | simulate.py:99-104 (cumulative count of unusable hours over [floor(a), floor(a)+98)); I measured: unusable-day share in TEST = 0.0, scored jobs = 840,000 of 840,000 per trace (rep 0, S12). TRAIN has 0.38 % unusable |
| 3d | Replicate alignment in analysis | PASS | analyze.py:36-45 adds replicates by calendar-day index; key matching `_S{S}__e_w` cannot confuse S2 with S12 |
| 3e | Ledger equals JSON | PASS | 40 randomly chosen keys of 4,221 (savings, CIs, tests, p, p_holm, shapley, per-BA counts, 9 JSON sources): 0 mismatches at 1e-9. A second ledger `ledger_TEST_secondary.csv` comes from secondary.py and was not spot-checked |
| 3f | Headline numbers internally consistent | PASS | PM100 weighted S12: oracle\|act 5.75, oracle\|req 3.33, lgbm\|act 4.08, lgbm\|req 1.90, lgbm\|pred 2.93, night 0.29 %; Shapley 2.30 runtime vs 1.56 forecast pp; H1 to H3 estimates 1.90, 2.18, 1.03 pp, p at the floor 1/2001 = 0.0005, Holm 0.0015 (report "p < 0.0005", not "p = 0.0005"); per-BA H2: 41 of 42 positive |
| 4a | CI definition matches sources | PASS with caveats | build_ci.py:49-60 (sum of clipped fuel generation x lifecycle factor / sum); six factors equal AR5 WGIII Annex III Table A.III.2 medians (coal 820, gas CC 490, nuclear 12, hydro 24, solar PV 48, wind 11); oil 650, other 230, unknown 700 are unverified judgement values (CSV `verified = no`; oil, other small; unknown share 0). Check against EIA's own CO2 file for one BA only (ERCO: hourly r 0.98, bias -0.9 g/kWh overall but TRAIN -3.2, DEV +4.0, TEST +7.8, i.e. drifts) |
| 4b | Battery storage and interchange | Caveat | EIA-930 2026 files carry "Battery Storage", "Other Energy Storage", "Unknown Energy Storage" columns (header check) that are not in `emission_factors.csv`, so discharge is outside both numerator and denominator; imports are ignored (production-based). Must be stated |
| 4c | Requested versus actual runtime semantics | PASS | A07: PM100 `time_limit` (min) vs `run_time`; F-DATA `elpl` vs `duration` (seconds; `elpl` unit inferred, not documented); KIT SWF requested vs run. PM100: 92.2 % of TIMEOUT jobs end within 2 % of the limit; KIT FH2: all 114,355 jobs carry status 1, so time-outs cannot be identified and 7.3 % of jobs sit within 2 % of the limit; F-DATA has no TIMEOUT state. Scored jobs are COMPLETED only, so scored r_act < r_req for all but 1 PM100 and about 0.001 % F-DATA jobs. The near-limit secondary addresses censoring. Median r_act/r_req 0.028 / 0.232 / 0.148, so the "requested walltime" arm is a very loose bound on PM100 |
| 4d | Power semantics | PASS with note | PM100 and F-DATA whole-job mean power, constant over run; KIT FH2 1 kW. The PREREG "unweighted variant (each job 1 kW)" does not match the code: `e_u` (simulate.py:169) is the mean intensity per job (job-count weighting), whereas 1 kW per job would be runtime weighting (MINOR M4) |

## 2. Reviewer threat list, ranked (not yet in PREREG or progress.md except where noted)

### MAJOR (must be stated; one needs an added analysis if time allows)

T1. Inference is conditional on one job sample and the bootstrap resamples only arrival-week blocks. PM100 is one machine, 477 users, 5 months of 2020 (COVID year); 20,000 jobs of 180,310 sampled and the same pool reused across all 42 BAs and 3 replicates; energy weighting makes a few long, high-power jobs dominate (PM100: jobs over 24 h are 14.1 % of energy). Intervals of plus or minus 0.1 pp and p at the floor are therefore precision about the placement and grid weeks, not about the workload. BAs are also resampled independently, ignoring same-week weather correlation (defensible because placements are independent). State: "intervals condition on the observed job sample"; add the three-trace agreement as the external check. Extra analysis (post hoc, section 9, primary unchanged): a user-cluster or job-level bootstrap, or 5 to 10 additional seeds of the same simulation, reporting how the S12 estimates move. This needs a re-run (job ids are not kept in the per-day sums), so label it a robustness replication, not a re-score.

T2. Data vintage and publication delay. The six-month EIA-930 files are revised and "Adjusted" series, and the forecasters (and the oracle) see them as if available at hour floor(a). Real-time feeds arrive with a delay of hours and are revised later. PREREG section 3 already states the availability assumption but not the revised-versus-real-time point. Must be a stated limitation, in the abstract-level caveats. Optional extra analysis: a delay-d sensitivity (forecast issued from data up to floor(a) - d, d = 3 and 6 h, for persistence, snaive_day and lgbm without refit); it affects short slack most. Persistence already loses (about -0.2 % at S12) so the headline is about lgbm and day-seasonal signals.

T3. Average (production-based, no imports or storage) versus marginal or consumption-based signals. The arm "saving" is a saving in the average signal's lifecycle intensity; the marginal effect of moving load may be smaller, larger or of another sign, and the interchange-aware consumption mix differs by BA. Also an hour-ending convention and lifecycle factors (three of nine unverified, ERCO-only validation, bias drift +7.8 g/kWh in TEST) apply. Must be stated; no extra analysis can fix it with the current data (a direct-factor sensitivity would need a full rebuild and forecast retrain; if done, report as post hoc).

T4. Cross-system pairing. Italian (PM100), Japanese (F-DATA) and German (KIT FH2) workloads from 2016 to 2023 are placed on 42 US grids in 2025-26 with the trace's local weekday and clock time; a US centre's submit behaviour, queue discipline and job mix differ. This is a "what-if the trace ran there" design. State plainly; the three-trace concordance (retained share, signs) is the support; Kestrel was not obtained, so there is no US trace.

### MODERATE (state in limitations)

T5. No queueing, capacity or backfilling interaction: jobs start at the planned time with free nodes, delay costs only start delay (reported in secondary item 8), delays shift load into low-carbon hours of all users at once (no feedback), no PUE or cooling, constant job power (no idle power, power phases or DVFS), no checkpoint and no interruptible jobs. All savings are bounds under free capacity.

T6. Pooled saving is emission-weighted, so dirtier BAs weigh more than clean ones; the estimand is "this fixed set of 42 BAs, the pooled sum" (PREREG section 5). Report per-BA and unweighted-over-BA means beside it (per-BA counts exist). Selection of BAs on coverage and TEST availability is a limitation of generality (US only, 42 of 70).

T7. The planner is a delay-to-lowest-integral heuristic; the oracle is the planner with perfect inputs on the same heuristic, not a global optimum. "Retained share" is relative to this oracle.

### MINOR

M1. BA eligibility conditions on TEST data completeness (>= 90 % valid in TEST, data through 2026-06-30).
M2. About 16 days of the TEST year (2025-07-01 to 07-06, 2026-06-15 to 06-30) receive no arrivals (weeks 0 to 48, p1 = period end minus 100 h); the BA standard-time placement versus the trace's DST wall-clock shifts summer starts by one hour.
M3. Realised outcomes use cleaned values: in TEST 0.04 % of hours interpolated (flag 1), 0.78 % outlier-replaced (flag 2) and 0.15 % copied from the previous week (flag 3); flag 3 copies favour week-lag forecasters at those hours. Negligible in magnitude (under 1 % of hours); state the counts. The outlier flag uses a centred window (clean_ci.py:73-76).
M4. "Unweighted" outcome is job-count weighted mean intensity, not 1 kW per job; fix the wording (do not recode).
M5. LightGBM is trained once on TRAIN and never refit, so TEST uses a model up to 2 years stale (conservative); at lead 1 persistence can be more accurate than lgbm (CISO MAE 12.9 vs 14.9 g/kWh on 300 TEST arrivals), which does not change the S >= 2 h arms materially.
M6. Secondary item 6 (TIMEOUT included) not run; `secondary.py` and its ledger are post-freeze code, unhashed; record in progress.md and in the paper's methods as descriptive.
M7. F-DATA power (`avgpcon`, documented as "average node power") is interpreted as whole-job power from the energy identity econ = avgpcon x duration / 3600; KIT FH2 has no power; `elpl` unit inferred. Secondary traces only.

## 3. Must be in the paper (limitations paragraph or methods)
T1, T2 (including revised data and publication delay), T3, T4, T5, T6, M1, M2, M3 counts, M4 wording, KIT FH2 status field limits, and that p-values sit at the bootstrap floor.

## 4. Optional extra analyses (all post hoc, section 9, primary result untouched)
1. Re-simulation of PM100 S12 with 5 to 10 other seeds or a user-cluster bootstrap (T1).
2. Information-delay sensitivity for 3 and 6 h (T2).
3. Per-BA and BA-unweighted summaries (T6) from existing results (no re-run).
4. TIMEOUT-included run (PREREG 7.6), which also bears on the censoring concern.

## 5. Reproducibility
Scripts, seeds, hashes and run settings are recorded (RUN.txt, PREREG hash lines, SHA-256 for raw EIA files, trace md5 in A07). Missing: package versions and the exact commands used for `analyze.py --boot twostage` and for the near-limit run (the near-limit RUN.txt does not record the flag); add them to progress.md.

VERDICT: PASS WITH ISSUES; 0 blocking issues
