VERDICT: P3 stats: minor as planned; add a synchronised-week (cross-BA) bootstrap and a registry plus all-cells supplement before any sensitivity number enters the text

Referee P3, statistics and reproducibility (persona: JOURNAL_EXPERT_BRIEF s5c, S1-S9). Date 2026-11-12. Plan-stage review; nothing in paper/ was edited.
Check I ran myself (scratch script, not in the project): with `analyze.load/bootstrap` (numpy 2.4.2) the frozen TEST PM100 S12 bootstrap reproduces the ledger exactly: H1 interval [0.018054, 0.019886], H2 [0.021055, 0.022591] (ledger keys TEST.PM100.w.S12.H1_deployable_saving.lo/.hi and H2_runtime_penalty.lo/.hi). The frozen code plus seed 7+S is deterministic here, so post-hoc recomputation on the same stream is possible.

## 1. Estimands and inference

1a. Fixed-BA block bootstrap vs estimand. Right for the stated target (PREREG s5 "this fixed set of 42 BAs ... over the TEST year"; s6; analyze.py:68 `pick = range(len(bas))`; blocks analyze.py:72). It measures calendar-week sampling uncertainty (50 blocks per BA; I confirmed 50 for all 42) given the observed job pool. It does not measure job-sample uncertainty (A08 T1; SPEC 4.7, W24). Say exactly that: "calendar interval, conditional on the observed job sample".

1b. Three things the plan does not yet say that a referee will find.
 (i) Cross-BA independence. analyze.py:72 draws a separate `rng.integers` per BA, so the same calendar week is not resampled across BAs. A08 T1 waves this away ("placements are independent"), but the grid-side week effect (heat wave, wind lull) is shared by neighbouring BAs and enters every contrast. I tested a synchronised version (same 50 week indices for all 42 BAs, 2000 draws, my own seed): H1 [0.01733, 0.02051] vs frozen [0.01805, 0.01989] (about 1.7x wider); H2 [0.02048, 0.02328] vs [0.02106, 0.02259] (about 2.0x wider). Both still exclude zero, so no claim changes, but the frozen interval is too narrow as a calendar interval. Report the synchronised interval as a labelled post-hoc sensitivity beside the frozen one (a few lines on `W`, seconds of CPU).
 (ii) Pooled estimand. saving = 1 - sum E_arm / sum E_runnow pooled over BAs (PREREG s5; analyze.py:56-57). Every BA gets the same 20,000 jobs, so BA weight is proportional to its carbon intensity and high-carbon grids dominate. The headline is a carbon-weighted pooled saving, not the average BA's saving. State it in the estimand sentence and show the per-BA median and IQR beside it (per-BA values are already in the JSON `per_ba`; A08 T6).
 (iii) The same 20,000-job pool is reused in all 42 BAs and 3 replicates (A08 T1), so BAs are not independent draws of workload either. This is the S1 issue.

1c. Null-centred p and Holm as coded. Correct. analyze.py:167-171: dev = T* - T, one-sided p = (1 + #{dev >= est}) / (1 + B), the standard shift-null bootstrap test (R03 blocker fixed); H4 two-sided via |dev| >= |est|. Holm (analyze.py:96-104) is the correct step-down with running maximum, applied only to H1-H3 (analyze.py:173-177). The ledger shows p_holm = 3 x p at the floor (0.0004998 to 0.0014993). Two reporting defects, not code defects:
 - analyze.py runs Holm for every slack and every file, so ledger rows for S2/S6/S24, F-DATA, KIT FH2, `_u`, `_twostage`, `_nearlimit` and DEV also carry p and p_holm. Only TEST.PM100.w.S12 is confirmatory (PREREG s6). Any other p must be dropped from the paper or labelled descriptive.
 - H4 is two-sided, unadjusted and descriptive (PREREG s7 item 9); keep it out of any "significant" sentence.
 - The per-BA counts (41 of 42 positive, 41 with lower bound > 0; analyze.py:198-200) use 500 draws and an unadjusted 2.5 % bound for 42 BAs. Call them descriptive counts, not 41 significant tests.

1d. Floor p-values. Smallest attainable p is 1/(B+1) = 0.0004998; Holm floor 3/2001 = 0.0014993. Report "bootstrap p < 0.0005 (Holm-adjusted p < 0.0015; B = 2000, the smallest attainable value)" for H1-H3, never "p = 0.0005" (A08 3f, W23). Add the one number the floor hides: effect over bootstrap SE. My value for H1: SE 0.000474, z about 40; label it post-hoc descriptive and state in the same sentence that it reflects calendar-week resampling only (hence S1). Do not raise B to chase a smaller p (a post-freeze change with no inferential gain). Make the decision rule the interval plus the Holm p, and avoid "significant" for anything else.

1e. H2 (0.021835, ledger H2.est) and the Shapley runtime term (0.023029) are two different "runtime penalties" (H2 conditions on lgbm; Shapley averages over both signals). Define both once, next to each other, or readers will think the numbers disagree.

## 2. The job-sample issue (P4 S1)

2a. Will S1 give a defensible interval? Partly. The design (user-cluster outer x frozen blocks inner; P4_PLAN v2 S1; src/sens_s1.py) is the right one and was requested by Codex R05. Fix these before running:
 - 30 outer draws estimate the outer SD with about 13 % relative error; the 2.5/97.5 percentiles of 30 points are essentially min/max. Do not publish percentiles of outer estimates. Report outer SD (with its own interval), mean inner SD, and a normal-approximation total interval: est_frozen +/- 1.96 sqrt(s_outer^2 + mean s_inner^2). The pooled percentile over 30 x 200 draws (P4_PLAN v2) treats 6,000 draws as independent; it is a mixture over only 30 user resamples.
 - Centring. The pooled percentile is centred on the mean of resampled estimates, not the frozen estimate (computed from the original pool). Report the bias (mean outer minus frozen) and centre the interval on the frozen estimate.
 - Estimator mismatch. Frozen uses 3 alignment replicates; S1 uses 1 per outer sample (P4_PLAN v2). Part of the outer spread is extra alignment noise that the frozen estimator averages out. Add a control: 30 draws with the ORIGINAL user set, new alignment seeds, one replicate. Outer SD (resampled users) minus control SD isolates the user-sampling part. This also covers the earlier "5 extra seeds" idea.
 - Heavy users. PM100 jobs over 24 h carry 14.1 % of energy (A08 T1) and there are 394 users after the main filter. Call the user bootstrap approximate and give the energy share of the top 10 users.
 - Scope. S1 covers sampling of users within one trace period (PM100 = 5 months of 2020). It does not cover sampling of machines or years. Three traces are three observations of systems, not an interval; do not pool them. The what-if wording (Italian, Japanese and German workloads on US grids; R05) stays in the caveats.
 - Predictions. S1 keeps the frozen history predictions (computed before resampling; sens_s1.py header). State it: H3's interval is slightly narrower than a full re-run would give.

2b. Presenting frozen beside S1. One naming rule everywhere (text, Fig 6, tables):
 - "Calendar interval" (frozen; blocks within BA, job sample fixed) and "workload-sample interval" (S1; user clusters x blocks). Never an unqualified "confidence interval".
 - Fig 6: frozen interval as the thick bar (FIGURE_FIXES 1); S1 as a visibly different mark (second row or open caps, different colour). Move the two-stage whisker to the supplement or legend: three interval types in one panel confuse readers, and the two-stage reading is a different estimand (PREREG s6).
 - Table columns: estimate | calendar interval (frozen) | workload-sample interval (S1, exploratory) | sign agrees in n of 30 outer draws. The last column is the readable robust claim.
 - Text rule: headline and abstract state estimates and name which interval they quote. If S1 completes, quote the wider total once ("widens to ... when users are resampled"). If fewer than 30 outer samples finish, label it Monte Carlo sensitivity (as P4_PLAN v2 says).
 - Hierarchy: frozen H1-H3 stay confirmatory; S1 is neither a corrected CI nor a second test.

## 3. Shapley decomposition intervals (FIGURE_FIXES items 2 and 3)

3a. Terms. Legitimate. They are linear in the four cell savings (analyze.py:178-186; E11, E12), so phi_forecast and phi_runtime per draw come exactly from `boot[:, idx[...]]` of the frozen bootstrap. My reproduction at S12, PM100: forecast [0.01499, 0.01612]; runtime [0.02244, 0.02371]; runtime minus forecast [0.00667, 0.00829]; runtime share [0.586, 0.608] (point 0.60). These are post-hoc intervals of secondary quantities from the frozen function `analyze.bootstrap` and frozen seed 7+S; because the stored H1/H2 limits reproduce to the last digit, this is an exact recomputation, not a new random draw.

3b. Per-BA upper bounds (item 3). `per_ba_boot` seed is args.seed + 100 + j with j the index in `sorted(data)` (analyze.py:191), B = 500. Recomputing with the same call must reproduce the stored `H2_lo`; make that the first check. The upper quantile is then a legitimate by-product. The within-BA interval rests on 50 week blocks and 500 draws (coarse tails) and is descriptive.

3c. Labelling (binding). Figure and caption: "post-hoc recomputation from the frozen bootstrap (same code, same seed; not in the frozen ledger); descriptive, no hypothesis test." Write values to a new ledger (for example tables/ledger_TEST_posthoc_shapley.csv, keys `posthoc.shapley.*`, with the script md5) and add a PREREG_DEVIATIONS row (rows exist only for items 1-4 now). Never edit analyze.py (frozen md5 8178e63f...); use a new file that imports it.

3d. Claim discipline. FIGURE_FIXES item 2 wants a note that F-DATA forecast term 1.76 > runtime term 1.65 (52/48). That compares two uncertain terms: compute the interval of (runtime - forecast) for F-DATA and KIT FH2 from the same draws and write "forecast term larger" only if it excludes zero; otherwise "comparable". Give the share with its interval. Because the interaction is not zero (H4 est 0.002388, ledger), say the 2x2 split depends on the symmetric Shapley allocation (PREREG s7 item 1) and print all four cells (already planned).

## 4. Multiplicity and garden of forks

Forks as planned: 3 confirmatory tests (H1-H3; one slack, one trace) + H4 + 12 PREREG secondaries (slacks, 3 traces, weighted/unweighted, near-limit, TIMEOUT, two-stage) + P4 S1-S5 (each over 3 traces; S2 x 3 lags; S3 x 2 factor sets; S5 tuned vs frozen) + X1-X7 (each over 3 traces) + 42 per-BA intervals. Only the first is a hypothesis family; the rest is a sensitivity grid. Reporting rule (put in Method 4.7 and the supplement):
 1. Registry table in the supplement, one row per analysis: id, status (confirmatory / prespecified secondary / post-freeze exploratory), setting grid, plan md5, code md5, seed, ledger file, shown in main text yes/no. P4_PLAN.md5 and P4_PLAN_X.md5 exist; list them with their timestamps relative to the first run. Include analyses started and abandoned (for example `results/_smoke_sens`, stated as smoke tests only).
 2. Complete-results table for every cell of every sensitivity (all traces, lags, factor sets, tuned and frozen forecasters), generated by script from the ledgers, no hand selection. Any sensitivity quoted in the main text carries "k of n cells agree in sign and ordering" (A09 s6 already has 24 of 24 for the secondary grid).
 3. p-values only for H1-H3 (TEST, PM100, S12). Everything else: estimate and interval, no p, no stars. Strip the p/p_holm rows of other files from anything quotable (1c).
 4. Frozen value first, sensitivity beside it, never instead; nothing promoted to the abstract (P4_PLAN v2).
 5. Adverse results get the same prominence as favourable ones (R05 "post-hoc shopping"); settings fixed and md5-written before the first run.
 6. "Three traces agree" is descriptive replication of the ordering, because PREREG makes PM100 primary.
 7. The 42 per-BA results are shown as a distribution (Fig 9), not a significance tally.

## 5. Reproducibility

Present now: PREREG md5 (cfe98401...) enforced in code (simulate.py:34-42; A08 1a); code md5s at freeze (PREREG status line); input md5s (ci_clean, jobs, emission_factors, ba_eligibility); RUN.txt per simulation; EIA SHA-256 list; seeds (20261111 alignment; 7+S bootstrap; 20261112+m for S1); ledger with source file per key; void DEV pilot files flagged `preR03_v0`.
Missing or weak (items 1-2 are already SPEC open item 26 and A08 s5):
 1. Package versions and interpreter (Python, numpy 2.4.2 in my run, pandas, pyarrow, lightgbm, scikit-learn, optuna) plus a lock file. NumPy `Generator` streams are not guaranteed identical across versions, so the numpy version is part of the seed.
 2. Exact commands in one script: the `analyze.py --boot twostage` and near-limit commands (near-limit RUN.txt lacks the flag, A08 2c), and the S1-S5/X commands with seed lists (ship src/run_p4_queue.ps1).
 3. md5 of every result file feeding a ledger (results/analysis_*.json, sim npz or a manifest) in a CHECKSUMS file, and a `verify.py` that rebuilds the ledger from the saved per-day npz sums with analyze.py and prints PASS or the difference. The statistics step needs no GPU, so a referee can rerun it even without retraining LightGBM.
 4. LightGBM determinism: multi-thread training can differ in the last bits. Ship the TEST forecast tables and frozen parameters with md5; state whether deterministic and seed options were set and that retraining may differ at about 1e-6.
 5. Licences: PM100 and F-DATA CC-BY-4.0 (A07 md5s); KIT FH2 licence still "to check" (SPEC s8). Do not redistribute it until checked; give download URL plus md5.
 6. Deviations ledger: add rows for the post-hoc Shapley and synchronised-bootstrap recomputation, S1-S5, X1-X7, and the md5 of src/secondary.py and src/sens_*.py at time of use (deviation 3 promises this). Keep PREREG.md byte-identical (it is).
 7. Zenodo contents: code with md5 table; PREREG.md, .md5, DEVIATIONS, both P4 plans with md5; derived inputs with md5 (ci_clean.parquet, jobs.parquet, ba_eligibility.csv, forecasts); per-day result npz or manifest; all ledgers; figure scripts; lock file; README with one command and expected values of the headline ledger keys; hardware and run-time note.
 8. Methods (4.7 and 6.5) must say: freeze md5 and date; TEST scored once; seeds; B; block definition including the fixed remainder; leakage rules; entry-point command; software versions; ledger location; the p-floor sentence; the pooled carbon-weighted estimand.
 9. The data-timing assumption (EIA revised data, available at floor(a); A08 T2, R05) sits in the same subsection; S2 is its sensitivity.

## 6. Recommendation

Minor revision of the plan. The confirmatory machinery is correct as coded and reproduces, the estimand is stated, deviations are logged. A statistics referee will still attack the narrowness of the interval (calendar-only, BAs independent, job pool fixed) and the sprawl of exploratory analyses. Five changes, ranked:
 1. Add the synchronised-week bootstrap (same weeks across all BAs) as a labelled post-hoc sensitivity for H1-H3, Shapley and Fig 6; word the frozen interval "calendar interval, BAs resampled independently" (my check: H1 about 1.7x wider, H2 about 2.0x, signs unchanged).
 2. Redesign the S1 readout: original-users control with new seeds; outer SD, inner SD, bias, normal-approximation total interval around the frozen estimate instead of percentiles of 30 points; sign-agreement n/30; fixed names "calendar interval" and "workload-sample interval" in text, figure and tables.
 3. Registry plus all-cells supplement with the seven-point rule (section 4); p-values only for H1-H3 at TEST/PM100/S12; remove the other p/p_holm rows from anything quotable.
 4. Post-hoc Shapley and per-BA recomputation as a new script importing the frozen functions and seed; first verify it reproduces stored `H2_lo` and the ledger H1/H2 limits; intervals for each term, runtime minus forecast, and share; label per 3c; deviations row and own ledger; no "forecast term > runtime term" claim without an interval that excludes zero.
 5. Reproducibility pack: lock file with numpy version, one-command script including the missing twostage and near-limit commands, md5 manifest of results and forecasts, `verify.py` rebuilding the ledger from saved sums, p-floor and block-definition sentences in Methods.
Cheap addition to the estimand sentence: the pooled saving is carbon-weighted; per-BA median and IQR go beside it.
