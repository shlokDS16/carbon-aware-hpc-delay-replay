VERDICT: A21 done; 11 items implemented (S1 amendment, arms, shift, S2b, X1-X7); 11 of 11 item smoke tests pass plus 3 equality tests; queue ready

Frozen md5 (simcore, simulate, analyze, forecast, prep_jobs), PREREG.md, P4_PLAN.md, P4_PLAN_AMEND.md, P4_PLAN_AMEND2.md, P4_PLAN_X.md, PANEL_DECISIONS.md checked unchanged at 01:31 IST. src/run_p4_queue.ps1 not touched. sens_common.py and sens_s2.py not touched. src/sens_s1.py WAS edited: logs/p4_queue.log at 01:26 still showed "waiting for s4", so S1 had not started; it was smoke-tested after the edit. No real ledger was created (smoke outputs only in results/_smoke_sens, logs/smoke_*.log); smoke data in data/derived and tables (x7 smoke) deleted.

## Files
- src/sens_xcommon.py: engine (run_ba_x, same RNG use as simulate.run_ba), runtime estimates, threshold rule, DEV noise table, analysis (analyse_x: frozen block bootstrap, free contrasts, no p-values), helpers.
- src/sens_arms.py --item arms | shift (ids arms, shift).
- src/sens_x.py --item x1 ... x7.
- src/sens_s2b.py (id s2b), src/sens_s1.py (amended), src/sens_x_tests.py (equality tests), src/run_p4x_queue.ps1.
- Per item: tables/ledger_TEST_sens_<id>.csv, results/sim_TEST_sens_<id>/, logs/sens_<id>.log (command, seeds, md5 of frozen and sens code, input md5, plan md5s, elapsed, peak RSS main and workers).
- Cache: results/_sens_arms/qest_<trace>.parquet (quantile runtime estimate for every job row; built once, aligned to jobs.parquet by job-id hash).

## Tests (all PASS)
- T frozen: run_ba_x (shift 0, 2 BAs, 20,000 jobs x 3 reps, PM100, S = 12, arms runnow, oracle|act/req/pred, lgbm|act/req/pred) equals results/sim_TEST/PM100 npz, max abs difference 0.0.
- T shift: +3 h changes the saving (4.28 to 5.23 % on the tiny config), job count kept.
- T qest: r_q <= r_req, r_pad <= r_req, r_q == r_req where fewer than 5 past jobs, all three traces.
- Quantile estimate leakage: expanding 90th percentile (numba Fenwick tree) re-run on the frozen loader + finalise output (prep_jobs.finalise, which re-asserts the frozen leakage check; r_pred_h equality with jobs.parquet asserted); naive recomputation on 1,000 random jobs per trace: every used job ended strictly before submit, count and quantile agree. Passed for PM100, KIT_FH2, FDATA. Share of jobs with at least 5 past jobs: 0.984 / 0.992 / 0.981 (PM100 / KIT / FDATA).
- Threshold causality: 40 decisions recomputed after overwriting every intensity at or after the chosen start with random values; unchanged. Index read is floor(t) - 1 < floor(t) (asserted in code).
- Dump totals equal daily-array totals (X4 dump vs its own daily npz).

## Per item (smoke = CISO + ERCO, 2,000 jobs, 1 rep, B 50; timing probe = same 2 BAs, 20,000 jobs x 3 reps, B 2000)
Memory: main process 1.9-2.4 GB (loads the FDATA job pool; under 3 GB), workers 0.3-0.7 GB (2 workers default; at most 3 allowed). Times below are extrapolated from the probe (42 BAs / 2 workers) plus analysis; not measured at full size.
- S1 amendment (src/sens_s1.py): original-users control (same 30 seeds, users not resampled, one alignment replicate; keys sens.s1ctl.*, runs after the main 30 samples within the same time budget; --no-control skips) and total interval = normal approximation around the frozen estimate, variance = frozen calendar variance (analyze.bootstrap on results/sim_TEST, S = 12, seed 7 + 12, B-cal 2000) + between-outer variance (keys tot_se, tot_lo, tot_hi); alternative with the mean inner variance of the outer samples (totin_*); percentile versions kept. Smoke PASS. Extra time about +0.5-1 h (control) + 2-3 min (frozen bootstrap). Peak RSS main 1.9 GB.
- S2b (src/sens_s2b.py): k = 24, 48 h, S = 12 only, arms as S2 (lgbm|req, lgbm|pred, snaive_day|req, oracle bound, plus runnow, lgbm|act, oracle|act, oracle|req), w and u. Smoke PASS (k = 48 forecast row floor(a) - 48 within the forecast span). Est. 5-10 min; RSS main 1.6 GB, worker 0.25 GB at smoke.
- arms (src/sens_arms.py --item arms): arms thresh, oracle and lgbm with act, req, pred, pad, q (+ runnow); contrasts thresh vs lgbm|req/pred, pad and q vs req and pred; runtime-estimate accuracy (share under-estimated, log error) for req, pred, pad, q; mean delay. Smoke PASS. Probe: 12 s for 2 BAs full-size; est. 12-15 min total; RSS main 2.0 GB, worker 0.52 GB.
- shift (--item shift): PM100, shifts -3, 0, +3 h of local clock (weekday rolls with the clock; window usability re-checked after the shift), arms runnow, oracle|act, lgbm|act, lgbm|req, lgbm|pred, all four slacks, w and u; difference to the z0 (frozen-equivalent) run as ledger rows. Smoke PASS. Est. 5-8 min.
- X1: multipliers 0.25, 0.5, 2, 4, 8 (1 = act arm), ln and lnmu, oracle and lgbm, S = 12; table tables/x1_runtime_sweep.csv; figure figures/sens_x1_runtime_sweep.png/.pdf (saving against median log2 error, req and pred marked). Smoke PASS (figure produced). Probe 22 s sim for 2 BAs full-size (21 arms); est. 15-20 min; worker 0.54 GB.
- X3: L in {6, 12, 24, 48} plus the frozen 96; lgbm|req and lgbm|act (+ oracle references); contrasts per L. Smoke PASS. Est. 12-15 min.
- X2: tables/x2_noise_scale_DEV.csv (BA x lead: DEV MAE of LightGBM, mean ci, sigma, realised noise MAE check; check max relative deviation 2 % on the smoke BAs); arms noisy|act, noisy|req (+ noisy96); contrasts vs lgbm. Smoke PASS. Est. 12-15 min.
- X4: ensure_dump() runs the dump simulation (arms runnow, oracle|act, lgbm|act, lgbm|req, lgbm|pred, S = 12; job-level arrays per BA) once, then hourly power load per BA-replicate with exact piecewise-linear integration: peak-to-mean, p99/mean, share of hours above 2 x mean, and each relative to run-now; tables/x4_load_concentration.csv. Smoke PASS. Est. 10 min.
- X5 and X6 read the same dump (rebuilt if absent); X5: penalty share by deciles of R_act/R_req and R_act, by top 1/5/10/20 users, users needed for half the penalty, Gini, per-BA mean and median beside the pooled H2; X6: saving, BA-bootstrap interval (B 500, descriptive), share of total saving and retained share by local hour, weekday, month. Smoke PASS. Each under 2 min.
- X7: fossil-only intensity (coal 820, gas 490, oil 650 lifecycle, as the frozen CI; hours with no fossil generation are missing under the A06 repair rules, 0.07 % of BA-hours on the smoke BAs), cleaned with clean_ci.clean_one, frozen forecast.py refit unchanged (--models lgbm, defaults, seed 42; --threads from the queue), arms runnow, oracle|act/req/pred, lgbm|act/req/pred; Shapley terms and H2/H3 as contrasts with intervals, no p-values; label "proxy, not a marginal estimate". Smoke PASS: refit worked, so lgbm arms are included; if the refit fails the script runs oracle arms only and logs it. Est. 25-30 min (forecast.py 8-12 min, RSS 2-3 GB as S3, not measured at full size).

Total estimate: about 2-2.5 h after the gate opens.

## Deviations or interpretations (none touches a binding setting; reasons given)
1. Threshold rule: "current observed intensity" is read as the most recent COMPLETED hourly value, ci[floor(t) - 1] at quarter-hour t (the interval containing t is not complete), with the trailing 7-day percentile from the 168 values before that interval. Same information set as the frozen forecasts (issued at floor(a) with data up to floor(a) - 1). Publication delay is covered by S2/S2b. The trailing window uses the forward-filled CI series (the usability rule is applied to the job windows only, as in the frozen code).
2. X1: the log-normal SD is taken from the filtered job pool per trace. DEV and TEST replays draw the identical 20,000 jobs per BA (same seed), so no TEST-period information is used. Added variant lnmu (also matches the mean log ratio).
3. X2: the plan says MAE matched at leads 1 to 24. Arm noisy follows this literally (sigma_24 held for leads 25-98); noisy96 (matched at every lead 1-96) is an addition to avoid understating long-lead error. Noise is independent across leads and clipped at 0.
4. X4/X5/X6 share one dump with five arms (plan: two arms for X4 and X5, daily arrays for X6): the superset is needed for H2 (lgbm|act), the local arrival hour and users, none of which the daily arrays hold. Same seed, jobs and alignment as the frozen run (equality tested).
5. X4 metrics are descriptive on the 20,000-job sample per BA and replicate (not a queue simulation, stated). X5 and X6 have no frozen-style bootstrap; X6 intervals are BA-bootstrap, descriptive. X5: because the replay has no capacity coupling, giving exact estimates to a set of users removes exactly their penalty share (reported as recovered pp).
6. X7 hours without fossil generation are left to the A06 repair rules rather than imputed by a new rule.
7. S1 total interval: calendar variance is the frozen block-bootstrap variance recomputed from results/sim_TEST (B 2000); the alternative with the outer samples' mean inner variance is reported beside it.
8. No p-values anywhere (panel rule 6); all analyses are w and u where an item is a standard arm run, S = 12 unless stated.
9. Queue defaults follow the restarted P4 queue (gate free >= 5 GB, commit < 90 %, stable 5 min); Workers 2 and Threads 10 default.

## Queue
src/run_p4x_queue.ps1 (PowerShell 5.1, -DryRun tested). Order: s2b, x1, x3, arms, shift, x2, x4, x5, x6, x7. Waits until run_p4_queue.ps1 has finished (no powershell process runs it and logs/p4_queue.log has at least one " RUN " line), then the same memory gate before every item; resumable by ledger; appends IN USE / DONE / FAILED rows to ../_shared/GPU_SCHEDULE.md and logs/p4x_queue.log; never kills processes; lock logs/p4x_queue.lock. NOT started.

Start command:
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\Shlok\Downloads\Sustainable Computing papers\paper_A\src\run_p4x_queue.ps1" -AllowPaperB -IgnoreTrainPy -Workers 2 -Threads 10

Remaining for the controller: add a PREREG_DEVIATIONS row per item when it completes; X8 not run.
