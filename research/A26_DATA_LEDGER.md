VERDICT: A26 done; 55 keys computed (all 38 pending keys covered, plus 17 check-only keys); 0 left pending; 5 differences from earlier documents (3 median ratios, ERCO r and bias) and 2 caveats (energy share population, S1 not run)

## Files
- `src/data_ledger.py` (run: `py src/data_ledger.py`, about 1 min) writes `tables/ledger_data.csv` (key,value,source). Asserts: eligible BA set equal in ci_clean, forecast_skill and ba_eligibility; hours_short = flag1+flag2 count and hours_week = flag3 count in ci_clean.parquet; unusable days from usable_day equal the cleaning_counts sum; MAX_REQ_H = 72; design constants equal results/sim_TEST/RUN.txt and analysis JSON B; S1 queue args equal sens_s1.py defaults.
- `logs/a26_forecast_leakcheck.txt`: fresh run of `src/forecast_leakcheck.py` (about 1 min, light; deterministic seed): future-perturbation 150 tests, 0 failed; flagged-input test 1,049 hours in 5 BAs, 0 failures. Matches A05.
- Templates edited (read-then-write, newline=""): `paper/sections/01_intro.tmpl.tex`, `03_data.tmpl.tex`, `04_method.tmpl.tex`, `paper/tables/T2_data.tex`. 50 placeholder occurrences lost the `PENDING:` prefix; the three intro keys were renamed `jobs.<trace>.median_ratio_completed` to `data.<trace>.median_ratio`. `grep PENDING:` over sections and tables now returns nothing.
- Ledger list: build_paper.py has no ledger list; the list is `LEDGER_FILES` in `src/paper/fill_ledger.py`. I added `"ledger_data.csv"` there (one token). `py -I src/paper/fill_ledger.py --check-only`: OK, 48 placeholders, 0 PENDING, 6 ledgers loaded, no key conflicts.

## Values (population in the source column of the CSV)
| key | PM100 | FDATA | KIT_FH2 |
|---|---|---|---|
| rows_in | 231,238 | 3,399,278 | 114,355 |
| completed_rows (before size filter) | 180,310 | 2,998,737 | 114,355 |
| users_filtered | 394 | 1,257 | 165 |
| median_ratio (main-filtered jobs) | 0.1426 | 0.3056 | 0.1783 |
Equal to jobs_trace_stats.json and to jobs.parquet: rows_in, completed_rows, n_timeout 8,689, timeout_within2pct 0.9223. users_filtered equal P4_PLAN (394, 1,257, 165).
Others: KIT_FH2.within2pct_share 0.0733 (all rows, as A07); PM100.energy_share_gt24h 0.1411; ci: n_candidate_ba 70, n_invalid 10,964, n_outlier 21,543, hours_short 21,046, hours_week 3,635, unusable_days 350, test flags 0.043, 0.779, 0.152 percent (stored as percent numbers, format .2f); fc: beat snaive 38, beat profile7 41 (of 42), leak 150 and 0; design: B 2000, reps 3, jobs_per_ba 20000, align_seed 20261111, perba_B 500, sync_weeks 50, s1_outer 30, s1_inner 200.

## Differences from earlier documents (d = 5)
1. median_ratio, all three traces: the frozen main filter removes many short or tiny jobs, so the ratio is larger than the unfiltered completed-row median in tables/jobs_trace_stats.json: PM100 0.1426 vs 0.0281; FDATA 0.3056 vs 0.2317; KIT FH2 0.1783 vs 0.1483. The ledger keeps both (`data.<t>.median_ratio_completed_unfiltered`). Sentences that cite the median ratio (intro, 03_data, T2) now say 14.3, 30.6 and 17.8 percent, not 2.8, 23.2 and 14.8. A07 and any prose that quotes 2.8 percent must be updated; the intro sentence "median completed job ran for X of its requested time" is true under either population, but the figure and tables must use the same one (fig:walltime: check which population it plots).
2. ERCO validation recomputed on the final ci_clean (flag-0 hours, 69,951 matched hours): r 0.9885, bias -2.0 g/kWh, against the v0 build values (A06: r 0.981, bias -0.9). Expected from the changed factors. Including repaired hours gives 0.9884 and -2.0 (key `_allflags`). Note A06/A08 per-period biases (-3.2, +4.0, +7.8) belong to v0 and are not recomputed; any text citing the TEST drift +7.8 g/kWh is stale.

## Caveats for the controller
- `data.PM100.energy_share_gt24h` = 0.1411 is over all rows and states (as prep_jobs.py defines it), the figure the sentence "jobs longer than 24 h supply X of the energy" needs if it speaks about the raw log. Over the main-filtered jobs the share is 0 (PM100 filtered jobs never exceed 24 h), key `..._filtered`. The sentence should say "in the raw PM100 log".
- design.s1_outer and design.s1_inner come from code (queue argument and sens_s1.py default); S1 has not run (no ledger_TEST_sens_s1.csv). If it completes fewer outer samples, replace the key with the number that ran.
- design.sync_weeks 50 (grid_days 351) is the written value in the posthoc JSON; design.B 2000 is the analysis JSON value.
- n_invalid uses n_row_missing + n_gen_le0 + n_ci_nan_other (R2 definition); for the eligible BAs it equals n_gen_le0 alone (A25's 10,964), so no change.
