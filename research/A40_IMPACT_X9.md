VERDICT: A40 done; B1-B4 done (B4 supported by the saved per-BA daily arrays, so run); X9 smoke pass; queue ready (not started)

## Files
- `src/posthoc_impact.py` -> `tables/ledger_TEST_posthoc_impact.csv` (531 rows, keys `posthoc.B<n>.<trace>.<weight>.S<S>.<name>`), `results/analysis_TEST_posthoc_impact.json`. Run time 18 s, peak RSS 279 MB.
- `src/sens_x9.py`, `src/run_x9_queue.ps1` (new, not started). Deviations row 7 appended to `research/PREREG_DEVIATIONS.md`.
- Frozen md5 unchanged (simcore e1032a51..., simulate 1ede0089..., analyze 8178e63f..., forecast 3cc0e9ca..., prep_jobs 6a1fc5cb...); `research/P4_PLAN_X9.md` md5 6451f781... unchanged.

## Choices not fixed by the plan (all in deviations row 7)
- B2 quartile: top ceil(42/4) = 11 BAs by TRAIN (2018-07-01..2024-06-30) median daily (max-min) of ci_clean, same day rule as secondary.test_character (flag <= 3, >= 20 h/day). Threshold 126.8 g/kWh. Groups resampled independently (fixed BA set), group difference from index-paired draws. Weights w and u.
- B3/B4: S = 12 and 24. B3 energy-weighted only (grams need energy). Sign: H2 = saving(lgbm|act) - saving(lgbm|req) in grams (checked equal to the PH4 arm difference, 54.257 g/job PM100 S12). B4 BA-week = one calendar week of one BA, replicates pooled; weeks with zero run-now energy skipped.
- B1 reads the PH4 rows (energy-weighted) x 8.76.

## Headline numbers (energy-weighted unless stated; intervals = frozen bootstrap B = 2000, seed 7 + S)
B1 (key `posthoc.B1.<trace>.w.S12.<D|lgbm|pred|oracle|act>.{g_per_kwh,t_per_MW_year}.{est,lo,hi}`), S = 12:
| trace | D g/kWh (t/MW-yr) | lgbm|pred | oracle|act |
|---|---|---|---|
| PM100 | 6.64 [6.32,6.97] (58.1) | 10.25 (89.8) | 20.14 (176.5) |
| FDATA | 13.20 [12.09,14.27] (115.7) | 15.06 (131.9) | 25.03 (219.3) |
| KIT_FH2 | 5.27 [5.14,5.41] (46.2) | 6.50 (56.9) | 14.02 (122.8) |
S = 24: D 9.37 / 19.65 / 7.68 g/kWh (82.1 / 172.1 / 67.3 t/MW-yr); oracle|act 30.17 / 38.33 / 21.72.

B3 (key `posthoc.B3.<trace>.w.S<S>.<H2|H3>.<g_per_job|g_per_kwh>.{est,lo,hi}`), S = 12:
- H2 PM100 54.26 g/job [52.30,56.22], 7.64 g/kWh [7.38,7.91]; FDATA 49.91 [43.56,56.75], 5.21 [4.56,5.90]; KIT_FH2 23.85 [23.27,24.39], 4.58 [4.47,4.68].
- H3 PM100 25.66 g/job [23.85,27.48], 3.62 g/kWh [3.37,3.87]; FDATA 17.75 [11.61,24.49], 1.85 [1.21,2.54]; KIT_FH2 6.39 [6.00,6.79], 1.23 [1.15,1.30].
- S = 24: H2 72.3 / 73.6 / 32.8 g/job; H3 39.4 / 30.4 / 13.6 g/job (PM100 / FDATA / KIT_FH2).

B2 (key `posthoc.B2.<trace>.<w|u>.S12.<top|rest|diff_top_minus_rest>.<saving_D|saving_pred|saving_oracle_act|share_D|share_pred>.{est,lo,hi}`), 11 top BAs vs 31 rest, w:
| trace | D saving top / rest | D share of oracle|act top / rest | pred share top / rest |
|---|---|---|---|
| PM100 | 3.45 % / 1.39 % | 0.325 / 0.333 (diff -0.007 [-0.034,0.018]) | 0.548 / 0.477 |
| FDATA | 7.22 % / 2.71 % | 0.551 / 0.509 (diff 0.041 [-0.021,0.099]) | 0.663 / 0.553 |
| KIT_FH2 | 2.86 % / 1.07 % | 0.387 / 0.366 (diff 0.021 [0.008,0.034]) | 0.493 / 0.439 |
Reading: high-range BAs carry about 2.5x the D saving in absolute terms; the retained share of the oracle is about the same (energy-weighted PM100 and FDATA differences include zero; unweighted shares differ by 0.02-0.08 and exclude zero).

B4 (key `posthoc.B4.<trace>.<w|u>.S<S>.D_positive_share_ba_weeks`; 2100 BA-weeks per trace), S = 12: w 0.856 / 0.852 / 0.909, u 0.933 / 0.949 / 0.923 (PM100 / FDATA / KIT_FH2); median over BAs 0.88-0.96 (w); the minimum over BAs is 0.000 (at least one BA never shows a positive D week).

## X9
- Smoke (CISO, ERCO; 2,000 jobs, 1 rep, B 50; also 20,000 jobs x 3 reps x all three traces): pass. Checks built in and passed: rank-1 candidate equals `simcore.plan_start` for every arm; cap = inf reproduces the uncapped plan, cap = 0 runs every job now; hourly start energy of jobs that found room never exceeds the cap (assert on every replicate); frozen md5 and plan md5 verified at start.
- Smoke (2 BAs, 3 reps, 20,000 jobs) is a preview only, not a result: PM100 w S12 D 4.04 % uncapped vs 2.82 % capped; displaced job share 0.7 % but displaced energy share 20 %; 0.36 % of jobs (32 % of energy) are larger than the cap alone and run now (F-DATA 67 % of energy, KIT_FH2 none). Extra counters written for this reading: oversize job and energy share, fallback share, run-now hours at the cap.
- Run time of the smoke is seconds per trace; full run expected well under the 45 min rule (the engine matches X1/X3 cost; no timing of the full 42 BAs yet). Peak RSS: workers 0.27 to 0.57 GB; main process peaked at 2.4 GB when loading the F-DATA job table (under 3 GB; at most 2 workers enforced in code).
- Ledger rows per trace: `sens.x9.<trace>.<w|u>.S12.saving[_lo|_hi].<arm>`, `.contrast.cap_cost_<arm>.{est,lo,hi}`, `.retained_share_of_uncapped.cap:<arm>`, `.meandelay_h.<arm>`, `sens.x9.<trace>.S12.cap:<arm>.{displaced_job_share, fallback_run_now_job_share, displaced_energy_share, displaced_job_share_median_ba, displaced_job_share_max_ba}`, cap level, oversize shares.

## Start command (queue waits until run_p4_queue.ps1 and run_p4x_queue.ps1 are no longer running; both currently running)
```
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\Shlok\Downloads\Sustainable Computing papers\paper_A\src\run_x9_queue.ps1" -AllowPaperB -IgnoreTrainPy -Workers 2 -Threads 10
```
Order PM100, FDATA, KIT_FH2; next trace only if the previous finished in under 45 min (`-MaxTraceMinutes`); a trace is skipped when its rows already exist in `tables/ledger_TEST_sens_x9.csv`; logs `logs/x9_queue.log`, `logs/sens_x9.log`. Dry run tested (`-DryRun`); the dry run shows both P4 queues running.
Manual alternative per trace: `py src\sens_x9.py --traces PM100 --workers 2`.
