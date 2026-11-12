VERDICT: A19 done; wrapper reproduces frozen ledger (max diff 0 against the stored analysis JSONs for all 3 traces x w,u x 4 slacks, 191 values per cell; 9.9e-17 against tables/ledger_TEST.csv, 480 keys); PH1-PH7 done; PM100 S12 synchronised/calendar width ratios H1 1.71, H2 1.74, H3 1.40 (F-DATA 0.93, 0.97, 0.99; KIT FH2 2.28, 2.10, 1.53), all three H intervals still exclude zero on all traces; (runtime term - forecast term) excludes zero on PM100 [0.62, 0.88] pp and KIT FH2 [0.38, 0.53] pp under both intervals but NOT on F-DATA ([-0.31, 0.10] pp, both intervals)

# A19 post-hoc inference PH1-PH7 (panel D0016, D0018), 2026-11-12

All results below are POST-HOC and descriptive (no hypothesis test, no p-values). Frozen code md5 unchanged before and after (simcore e1032a51, simulate 1ede0089, analyze 8178e63f, forecast 3cc0e9ca, prep_jobs 6a1fc5cb; PREREG md5 cfe98401 unchanged). Names: "calendar interval" = frozen block bootstrap (each BA resampled independently; B = 2000, seed 7 + S); "synchronised-week interval" = PH1 (the same 50 week indices for all 42 BAs in a draw; weeks are 7-day blocks of the common day grid starting at the earliest first arrival day, the 1 to 2 remaining days are a fixed remainder; B = 2000, seed 7 + S). Intervals are 2.5 and 97.5 percentiles. pp = percentage points of saving relative to run-now. Point estimates are identical under both (checked, max diff below 1e-12).

## Files
- src/posthoc_inference.py (new; imports frozen analyze.py), src/rebuild_ledgers.py (new)
- tables/ledger_TEST_posthoc.csv (keys posthoc.<PH>.<trace>.<weight>.S<S>.<name>.<stat>; PH1 = D, H1-H4, gap, retained share; PH2 = forecast, runtime, interaction, runtime minus forecast, runtime share; PH3 per-BA H2 est/lo/hi and summary; PH4 absolute effects; PH6 D minus profile7; PH7 saving per delay hour). Weights w and u and slacks 2, 6, 12, 24 are all stored; the tables here show S = 12 h, w.
- results/analysis_TEST_posthoc_{PM100,FDATA,KIT_FH2}.json
- research/ENVIRONMENT.txt, research/RESULTS_MD5.txt, research/RUN_COMMANDS.md, research/PREREG_DEVIATIONS.md row 5
- Memory: peak RSS about 100 MB per run (one trace at a time, saved aggregated npz only); runtime about 30 s for everything. No MemoryError.

## Wrapper proof (first check)
With the frozen bootstrap (analyze.bootstrap, mode fixed, seed 7 + S, B = 2000) and the frozen per_ba_boot (seed 7 + 100 + j, B = 500) called from the new script, every stored value is reproduced exactly: savings, savings_ci95 for all 30 arms, H1-H4 est and interval, Shapley gap/forecast/runtime/interaction/retained share, per-BA H2_est and H2_lo: max abs difference 0 (191 values per trace x weight x slack cell; 24 cells). Against tables/ledger_TEST.csv (D = saving lgbm|req and its limits, H1-H4, Shapley terms; 480 keys) the max abs difference is 9.9e-17 (csv round-off). The PH4 energy-extended bootstrap reproduces the frozen draws exactly (assertion in the script).

## Reading
1. D and H1 are the same quantity (saving(lgbm|req) minus run-now, which is 0); both rows are given.
2. Synchronising the weeks widens the interval on PM100 and KIT FH2 (H1 1.7 and 2.3 times, H2 1.7 and 2.1, H3 1.4 and 1.5, Shapley gap 2.05 on PM100) and leaves F-DATA unchanged (0.93 to 0.99). No H1-H3 conclusion changes (all intervals exclude zero on all traces, S = 12, w).
3. Runtime term versus forecast term (S = 12, w): excludes zero on PM100 (runtime larger by 0.75 pp) and KIT FH2 (0.45 pp); on F-DATA the interval includes zero ([-0.292, 0.085] calendar, [-0.309, 0.101] synchronised), so the F-DATA wording must be "comparable", not "forecast term larger". Across the 24 trace x weight x slack cells the status changes from calendar to synchronised only for PM100 w S24 and KIT FH2 w S24 (exclude zero under calendar, include zero under synchronised); full table below.
4. PH6: the learned forecaster beats the 7-day profile (profile7|req) on all three traces at S = 12 (0.79, 0.47, 0.53 pp); the interval excludes zero under both bootstraps; also at S = 24 on all three.
5. PH3 (descriptive, 500 draws, 50 blocks): per-BA H2 lower bound above zero in 41 of 42 BAs (PM100), 33 (F-DATA), 40 (KIT FH2); the smallest lower bound is -6.98 pp on F-DATA. The PM100 count 41 equals the frozen count (stored H2_lo reproduced).
6. Absolute effects: run-now mean realised intensity about 350 g CO2/kWh on each trace. The deployable arm saves 47 g per job (PM100) and 6.6 g per kWh; see tables.

## Per-trace tables: calendar interval (frozen) vs synchronised-week interval, and absolute effects

### PM100: S = 12 h, energy-weighted; percentage points of saving unless stated

| quantity | estimate | calendar interval (frozen) | synchronised-week interval (PH1) | width ratio | excludes 0 (calendar / sync) |
|---|---|---|---|---|---|
| D = saving of lgbm\|req (= H1 estimate) | 1.896 | [1.805, 1.989] | [1.734, 2.047] | 1.71 | yes / yes |
| H1 deployable saving | 1.896 | [1.805, 1.989] | [1.734, 2.047] | 1.71 | yes / yes |
| H2 runtime penalty | 2.184 | [2.106, 2.259] | [2.048, 2.316] | 1.74 | yes / yes |
| H3 prediction recovery | 1.033 | [0.960, 1.104] | [0.934, 1.134] | 1.40 | yes / yes |
| H4 interaction | 0.239 | [0.179, 0.299] | [0.159, 0.317] | 1.32 | yes / yes |
| PH6: saving(lgbm\|req) - saving(profile7\|req) | 0.788 | [0.713, 0.866] | [0.664, 0.902] | 1.55 | yes / yes |
| Shapley gap oracle\|act - lgbm\|req | 3.858 | [3.775, 3.943] | [3.693, 4.036] | 2.05 | yes / yes |
| Shapley forecast term | 1.555 | [1.499, 1.612] | [1.456, 1.658] | 1.78 | yes / yes |
| Shapley runtime term | 2.303 | [2.244, 2.371] | [2.185, 2.424] | 1.89 | yes / yes |
| runtime term - forecast term | 0.748 | [0.667, 0.829] | [0.618, 0.878] | 1.61 | yes / yes |
| interaction (Shapley, = H4) | 0.239 | [0.179, 0.299] | [0.159, 0.317] | 1.32 | yes / yes |
| runtime share of gap (fraction x 100) | 59.691 | [58.647, 60.756] | [58.051, 61.341] | 1.56 | yes / yes |
| retained share lgbm\|req / oracle\|act (fraction x 100) | 32.951 | [31.728, 34.219] | [31.065, 34.640] | 1.44 | yes / yes |

### FDATA: S = 12 h, energy-weighted; percentage points of saving unless stated

| quantity | estimate | calendar interval (frozen) | synchronised-week interval (PH1) | width ratio | excludes 0 (calendar / sync) |
|---|---|---|---|---|---|
| D = saving of lgbm\|req (= H1 estimate) | 3.810 | [3.482, 4.117] | [3.513, 4.106] | 0.93 | yes / yes |
| H1 deployable saving | 3.810 | [3.482, 4.117] | [3.513, 4.106] | 0.93 | yes / yes |
| H2 runtime penalty | 1.503 | [1.313, 1.701] | [1.316, 1.692] | 0.97 | yes / yes |
| H3 prediction recovery | 0.535 | [0.351, 0.734] | [0.353, 0.731] | 0.99 | yes / yes |
| H4 interaction | 0.294 | [0.148, 0.436] | [0.145, 0.446] | 1.05 | yes / yes |
| PH6: saving(lgbm\|req) - saving(profile7\|req) | 0.473 | [0.331, 0.622] | [0.327, 0.629] | 1.04 | yes / yes |
| Shapley gap oracle\|act - lgbm\|req | 3.412 | [3.241, 3.605] | [3.181, 3.643] | 1.27 | yes / yes |
| Shapley forecast term | 1.761 | [1.656, 1.870] | [1.605, 1.912] | 1.44 | yes / yes |
| Shapley runtime term | 1.650 | [1.513, 1.815] | [1.502, 1.824] | 1.07 | yes / yes |
| runtime term - forecast term | -0.111 | [-0.292, 0.085] | [-0.309, 0.101] | 1.09 | no / no |
| interaction (Shapley, = H4) | 0.294 | [0.148, 0.436] | [0.145, 0.446] | 1.05 | yes / yes |
| runtime share of gap (fraction x 100) | 48.374 | [45.683, 51.215] | [45.433, 51.509] | 1.10 | yes / yes |
| retained share lgbm\|req / oracle\|act (fraction x 100) | 52.755 | [49.673, 55.511] | [50.000, 55.245] | 0.90 | yes / yes |

### KIT_FH2: S = 12 h, energy-weighted; percentage points of saving unless stated

| quantity | estimate | calendar interval (frozen) | synchronised-week interval (PH1) | width ratio | excludes 0 (calendar / sync) |
|---|---|---|---|---|---|
| D = saving of lgbm\|req (= H1 estimate) | 1.509 | [1.469, 1.550] | [1.415, 1.598] | 2.28 | yes / yes |
| H1 deployable saving | 1.509 | [1.469, 1.550] | [1.415, 1.598] | 2.28 | yes / yes |
| H2 runtime penalty | 1.311 | [1.278, 1.342] | [1.245, 1.379] | 2.10 | yes / yes |
| H3 prediction recovery | 0.352 | [0.329, 0.374] | [0.317, 0.385] | 1.53 | yes / yes |
| H4 interaction | 0.337 | [0.316, 0.358] | [0.302, 0.374] | 1.73 | yes / yes |
| PH6: saving(lgbm\|req) - saving(profile7\|req) | 0.527 | [0.497, 0.556] | [0.467, 0.587] | 2.03 | yes / yes |
| Shapley gap oracle\|act - lgbm\|req | 2.507 | [2.463, 2.549] | [2.398, 2.621] | 2.62 | yes / yes |
| Shapley forecast term | 1.027 | [0.998, 1.056] | [0.958, 1.094] | 2.37 | yes / yes |
| Shapley runtime term | 1.480 | [1.451, 1.507] | [1.410, 1.549] | 2.47 | yes / yes |
| runtime term - forecast term | 0.453 | [0.416, 0.490] | [0.376, 0.526] | 2.02 | yes / yes |
| interaction (Shapley, = H4) | 0.337 | [0.316, 0.358] | [0.302, 0.374] | 1.73 | yes / yes |
| runtime share of gap (fraction x 100) | 59.026 | [58.265, 59.805] | [57.405, 60.587] | 2.07 | yes / yes |
| retained share lgbm\|req / oracle\|act (fraction x 100) | 37.568 | [36.919, 38.229] | [36.304, 38.727] | 1.85 | yes / yes |

### Widening factor (synchronised width / calendar width) by trace, weighting and slack

| trace | weight | S | H1 | H2 | H3 | H4 | forecast term | runtime term | runtime - forecast |
|---|---|---|---|---|---|---|---|---|---|
| PM100 | w | 2 | 1.45 | 1.35 | 1.15 | 1.21 | 1.53 | 1.62 | 1.36 |
| PM100 | w | 6 | 1.41 | 1.60 | 1.27 | 1.25 | 1.87 | 1.77 | 1.51 |
| PM100 | w | 12 | 1.71 | 1.74 | 1.40 | 1.32 | 1.78 | 1.89 | 1.61 |
| PM100 | w | 24 | 1.81 | 1.73 | 1.37 | 1.13 | 2.09 | 1.92 | 1.77 |
| PM100 | u | 2 | 1.52 | 1.53 | 1.48 | 2.03 | 2.09 | 2.25 | 1.56 |
| PM100 | u | 6 | 1.52 | 1.83 | 1.79 | 2.03 | 2.01 | 2.29 | 1.72 |
| PM100 | u | 12 | 1.91 | 2.11 | 2.06 | 1.95 | 2.02 | 2.28 | 1.88 |
| PM100 | u | 24 | 2.18 | 1.76 | 1.67 | 1.63 | 2.36 | 2.08 | 1.72 |
| FDATA | w | 2 | 0.89 | 1.05 | 1.06 | 1.22 | 1.27 | 1.05 | 1.11 |
| FDATA | w | 6 | 0.94 | 1.09 | 1.13 | 1.03 | 1.20 | 1.07 | 1.06 |
| FDATA | w | 12 | 0.93 | 0.97 | 0.99 | 1.05 | 1.44 | 1.07 | 1.09 |
| FDATA | w | 24 | 1.03 | 0.96 | 1.02 | 0.92 | 1.35 | 1.08 | 1.09 |
| FDATA | u | 2 | 1.98 | 1.34 | 1.36 | 2.25 | 2.16 | 1.89 | 1.91 |
| FDATA | u | 6 | 2.06 | 1.54 | 1.26 | 2.19 | 2.11 | 2.04 | 1.77 |
| FDATA | u | 12 | 2.45 | 1.87 | 1.69 | 1.97 | 2.22 | 2.13 | 1.88 |
| FDATA | u | 24 | 2.33 | 1.87 | 1.65 | 1.60 | 2.41 | 2.18 | 1.84 |
| KIT_FH2 | w | 2 | 1.96 | 1.81 | 1.65 | 2.09 | 2.24 | 2.25 | 1.86 |
| KIT_FH2 | w | 6 | 2.17 | 2.05 | 1.59 | 1.89 | 2.32 | 2.37 | 1.97 |
| KIT_FH2 | w | 12 | 2.28 | 2.10 | 1.53 | 1.73 | 2.37 | 2.47 | 2.02 |
| KIT_FH2 | w | 24 | 2.31 | 2.28 | 1.44 | 1.80 | 2.58 | 2.50 | 2.18 |
| KIT_FH2 | u | 2 | 1.24 | 1.45 | 1.16 | 2.14 | 2.02 | 2.27 | 1.41 |
| KIT_FH2 | u | 6 | 1.46 | 1.68 | 1.46 | 2.14 | 1.82 | 2.26 | 1.52 |
| KIT_FH2 | u | 12 | 1.79 | 1.72 | 1.63 | 1.97 | 2.09 | 2.13 | 1.82 |
| KIT_FH2 | u | 24 | 2.04 | 1.74 | 1.53 | 1.83 | 2.37 | 2.08 | 1.73 |

### Does the (runtime term - forecast term) interval exclude zero? All traces, weightings, slacks

| trace | weight | S | estimate (pp) | calendar | synchronised | excludes 0 (cal / sync) |
|---|---|---|---|---|---|---|
| PM100 | w | 2 | 0.217 | [0.199, 0.234] | [0.192, 0.241] | yes / yes |
| PM100 | w | 6 | 0.574 | [0.527, 0.619] | [0.505, 0.644] | yes / yes |
| PM100 | w | 12 | 0.748 | [0.667, 0.829] | [0.618, 0.878] | yes / yes |
| PM100 | w | 24 | 0.141 | [0.023, 0.252] | [-0.072, 0.334] | yes / no |
| PM100 | u | 2 | 0.077 | [0.057, 0.097] | [0.045, 0.109] | yes / yes |
| PM100 | u | 6 | 0.607 | [0.552, 0.654] | [0.517, 0.691] | yes / yes |
| PM100 | u | 12 | 1.542 | [1.451, 1.635] | [1.362, 1.708] | yes / yes |
| PM100 | u | 24 | 1.073 | [0.955, 1.192] | [0.863, 1.269] | yes / yes |
| FDATA | w | 2 | 0.002 | [-0.073, 0.101] | [-0.090, 0.103] | no / no |
| FDATA | w | 6 | 0.139 | [-0.036, 0.365] | [-0.053, 0.373] | no / no |
| FDATA | w | 12 | -0.111 | [-0.292, 0.085] | [-0.309, 0.101] | no / no |
| FDATA | w | 24 | -0.690 | [-0.926, -0.441] | [-0.948, -0.418] | yes / yes |
| FDATA | u | 2 | -0.221 | [-0.238, -0.205] | [-0.253, -0.189] | yes / yes |
| FDATA | u | 6 | -0.155 | [-0.198, -0.114] | [-0.229, -0.081] | yes / yes |
| FDATA | u | 12 | 0.200 | [0.127, 0.276] | [0.057, 0.336] | yes / yes |
| FDATA | u | 24 | -0.450 | [-0.549, -0.350] | [-0.639, -0.272] | yes / yes |
| KIT_FH2 | w | 2 | 0.127 | [0.120, 0.134] | [0.114, 0.139] | yes / yes |
| KIT_FH2 | w | 6 | 0.341 | [0.321, 0.360] | [0.300, 0.378] | yes / yes |
| KIT_FH2 | w | 12 | 0.453 | [0.416, 0.490] | [0.376, 0.526] | yes / yes |
| KIT_FH2 | w | 24 | 0.096 | [0.040, 0.150] | [-0.030, 0.209] | yes / no |
| KIT_FH2 | u | 2 | -0.054 | [-0.072, -0.034] | [-0.080, -0.027] | yes / yes |
| KIT_FH2 | u | 6 | 0.286 | [0.236, 0.330] | [0.213, 0.356] | yes / yes |
| KIT_FH2 | u | 12 | 0.753 | [0.674, 0.836] | [0.601, 0.896] | yes / yes |
| KIT_FH2 | u | 24 | 0.003 | [-0.102, 0.104] | [-0.175, 0.180] | no / no |

### PH3 per-BA H2 (S = 12 h, w): within-BA 95 % interval, frozen function and seeds (500 draws, 50 weekly blocks); descriptive

| trace | BAs | H2 est > 0 | lower bound > 0 | median per-BA H2 (pp) | smallest lower bound (pp) | largest upper bound (pp) |
|---|---|---|---|---|---|---|
| PM100 | 42 | 41 | 41 | 1.355 | 0.000 | 11.437 |
| FDATA | 42 | 40 | 33 | 1.136 | -6.984 | 9.326 |
| KIT_FH2 | 42 | 41 | 40 | 0.823 | -0.009 | 6.755 |

### PH4 absolute effects (S = 12 h, w; calendar interval from the frozen bootstrap; pooled over 42 BAs and 3 replicates)

| trace | run-now mean realised intensity (g CO2/kWh) | jobs | energy (kWh) |
|---|---|---|---|
| PM100 | 350.08 [347.48, 352.90] | 2,520,000 | 17,886,609 |
| FDATA | 346.60 [341.67, 351.58] | 2,520,000 | 24,136,356 |
| KIT_FH2 | 349.23 [347.00, 351.66] | 2,520,000 | 13,123,883 |

Saving of D = lgbm\|req (deployable) relative to run-now, S = 12 h:

| trace | g CO2 per job | g CO2 per kWh | relative saving (pp) |
|---|---|---|---|
| PM100 | 47.115 [44.864, 49.388] | 6.638 [6.323, 6.966] | 1.896 |
| FDATA | 126.472 [115.839, 137.043] | 13.204 [12.088, 14.275] | 3.810 |
| KIT_FH2 | 27.437 [26.721, 28.153] | 5.268 [5.135, 5.407] | 1.509 |

Saving of lgbm\|act relative to run-now, S = 12 h:

| trace | g CO2 per job | g CO2 per kWh | relative saving (pp) |
|---|---|---|---|
| PM100 | 101.372 [98.691, 103.952] | 14.282 [13.911, 14.639] | 4.080 |
| FDATA | 176.383 [166.414, 186.022] | 18.416 [17.419, 19.367] | 5.313 |
| KIT_FH2 | 51.286 [50.305, 52.288] | 9.848 [9.659, 10.039] | 2.820 |

Saving of lgbm\|pred relative to run-now, S = 12 h:

| trace | g CO2 per job | g CO2 per kWh | relative saving (pp) |
|---|---|---|---|
| PM100 | 72.774 [70.452, 75.083] | 10.253 [9.923, 10.576] | 2.929 |
| FDATA | 144.225 [134.643, 153.323] | 15.058 [14.088, 15.998] | 4.345 |
| KIT_FH2 | 33.831 [33.068, 34.579] | 6.496 [6.351, 6.641] | 1.860 |

Saving of oracle\|act relative to run-now, S = 12 h:

| trace | g CO2 per job | g CO2 per kWh | relative saving (pp) |
|---|---|---|---|
| PM100 | 142.983 [140.270, 146.013] | 20.145 [19.778, 20.527] | 5.754 |
| FDATA | 239.732 [229.635, 249.790] | 25.030 [24.058, 26.001] | 7.222 |
| KIT_FH2 | 73.033 [71.979, 74.119] | 14.024 [13.823, 14.234] | 4.016 |

Saving of oracle\|req relative to run-now, S = 12 h:

| trace | g CO2 per job | g CO2 per kWh | relative saving (pp) |
|---|---|---|---|
| PM100 | 82.792 [80.438, 85.349] | 11.664 [11.336, 12.011] | 3.332 |
| FDATA | 180.067 [169.424, 190.261] | 18.800 [17.697, 19.844] | 5.424 |
| KIT_FH2 | 43.055 [42.293, 43.856] | 8.267 [8.119, 8.419] | 2.367 |

### PH7 saving per hour of added mean start delay (S = 12 h, w; descriptive ratio, no interval; cells: mean delay h / saving in pp per hour; delay is the job-count mean)

| arm | PM100 | FDATA | KIT_FH2 |
|---|---|---|---|
| night | 4.42 / 0.065 | 3.79 / -0.064 | 4.75 / 0.044 |
| profile7\|req | 4.83 / 0.230 | 5.06 / 0.660 | 4.28 / 0.230 |
| lgbm\|req | 5.50 / 0.345 | 5.84 / 0.652 | 5.36 / 0.281 |
| lgbm\|act | 5.23 / 0.780 | 5.62 / 0.946 | 5.01 / 0.563 |
| lgbm\|pred | 5.22 / 0.561 | 5.67 / 0.766 | 4.99 / 0.373 |
| oracle\|req | 5.60 / 0.595 | 5.89 / 0.920 | 5.50 / 0.430 |
| oracle\|act | 5.38 / 1.070 | 5.74 / 1.258 | 5.20 / 0.773 |


## Notes
- Widening factors for the u weighting and all slacks are in the table above and in the ledger (keys ending .widen).
- PH4: energy-weighted (w) only, since grams and kWh need the energy weighting. Per job = pooled over 42 BAs x 3 replicates x 20,000 jobs (2.52 million jobs per trace). Intervals are calendar intervals (frozen bootstrap with the energy and job-count rows resampled by the same week indices).
- PH7 uses the job-count mean delay of tables/secondary_delay.csv and the energy-weighted saving of the frozen analysis; the ratio mixes the two weightings and is descriptive only. Night on F-DATA has a negative saving, hence a negative ratio.
- Caveat for text (P3 section 1b): the synchronised interval still conditions on the observed job sample and resamples calendar weeks only; it is not the workload-sample interval (S1).
- PH5: src/rebuild_ledgers.py rebuilt ledger_TEST.csv (4221 rows) and ledger_TEST_nearlimit.csv (1407 rows) from results with the frozen analyze.py into a temp folder: all rows exactly equal, max abs diff 0, source strings equal: PASS (68 s; nothing in results/ or tables/ written). The exact commands of the simulation and analysis runs were not recorded verbatim; research/RUN_COMMANDS.md marks them "reconstructed" with the evidence used.
