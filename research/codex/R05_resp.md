[ METHODS]

1. **S1–S5 responses**
- **S1:** Current five seed reruns estimate simulation variation, but don’t establish user/job-sample uncertainty. For PM100, run at least **30 user-cluster resamples** (477 users sampled with replacement; then sample 20,000 eligible jobs per BA/trace) with distinct recorded seeds `20261112–20261141`; rerun the six arms needed for D/H2/H3/Shapley (`lgbm|req, act, pred`; `oracle|act, req`) on all three traces.
- **S2:** Use fixed lags **k=1, 3, 6 h**; evaluate `lgbm|req` and `lgbm|pred` (plus `snaive_day|req` as a simple policy) on all three traces. Keep current-data oracle as an upper bound, clearly labeled.
- **S3:** Do not compare lifecycle-trained forecasts against direct-factor outcomes as the deployable result; refit as below. **S4:** PM100 only, `COMPLETED,TIMEOUT`, all arms, same seeds/settings; label descriptive because timeout runtimes are limit-censored. **S6:** limitation text is right.

2. **S3 direct factors**
- An oracle-only run answers only how the *oracle policy* changes under direct factors; it does not test the deployable forecast policy. Minimum credible version: rebuild direct-factor CI, retrain the same LightGBM pipeline with **unchanged hyperparameters/splits/seeds**, regenerate forecasts, and rerun `lgbm|req` plus `oracle|act` for all traces.
- Prespecify direct coal/gas/oil factors and the oil-factor alternative as separate sensitivities; don’t select whichever preserves the headline. State imports/storage remain excluded.

3. **S5 HPO**
- “60 TPE trials, TRAIN-only” is a reasonable exploratory start, but the plan needs a search space, seed, and selection/refit rule; repeated tuning on the same six-month validation window risks overfitting that window.
- Use **100 trials**, fixed Optuna seed, MAE at 1–24 h, and a bounded space: leaves 15–127, depth 3–10, learning rate 0.01–0.15 log, min leaf 50–1000 log, feature/bagging fractions 0.6–1, L1/L2 1e-4–10 log, max-bin 63–255. Select iteration count on the same TRAIN validation, then refit with selected settings on full TRAIN.
- Give `profile7` a tuned window-length rival (1, 3, 7, 14, 28 days) and compare day/week seasonal-naive variants on that same validation. Keep all tuned results exploratory; frozen D stays the headline.

4. **First attack / highest-value analysis**
- First attack: external validity—the workload traces are Italian, Japanese, and German, placed on US grids; the evaluation is a counterfactual replay, not a measured US deployment. Revised EIA data and excluded imports/storage further limit the operational carbon claim.
- The highest-value extra analysis is S1 with **user-cluster sampling uncertainty combined with calendar-block uncertainty**; it directly tests whether the narrow headline intervals survive workload variation. S2 is the strongest operational sensitivity, but cannot resolve data revision or cross-system pairing.

5. **Post-hoc shopping**
- S2–S5 are post-freeze sensitivities: report **all prespecified settings and traces**, alongside the frozen TEST estimates, without changing H1–H3, D, or the abstract headline. Don’t tune choices or omit unfavorable factor/lag/trace results.
- State that HPO is a post-hoc robustness check—not a corrected confirmatory model—and disclose every new seed, code hash, deviation, and run command.

[STATS]

1. **S1–S5 responses**
- **S1:** Across-seed SD alone is not a confidence interval. For a referee-defensible combined interval, bootstrap the **477 PM100 users** as clusters, draw 20,000 jobs from each resulting sample, then resample aligned 7-day arrival blocks within each BA; repeat **at least 30 outer samples**, seeds `20261112–20261141`, and carry all stages through the same paired contrasts.
- Use the six arms `lgbm|req, act, pred; oracle|act, req` for D/H2/H3/Shapley, all three traces; keep traces’ intervals separate. If 30 outer runs exceed budget, report seed spread as sensitivity, not as a corrected CI.
- **S2:** fixed lags **1/3/6 h**, all three traces, `lgbm|req/pred` and `snaive_day|req`; report each lag. **S3:** retrain direct-target forecaster. **S4:** PM100 `COMPLETED,TIMEOUT`, all arms, descriptive only.

2. **S3 direct factors**
- Oracle-only is inadequate for the deployable-policy question; a lifecycle-targeted LightGBM forecast is not calibrated to direct-factor CI. Minimum: rebuild direct CI and refit the unchanged frozen model pipeline on TRAIN, score on held-out TEST, and rerun both `lgbm|req` and `oracle|act`.
- Keep fuel-factor alternatives separate and report all; no selecting the factor set with the best saving.

3. **S5 HPO**
- TPE 60 is not inherently research-grade; a fixed budget is reproducible, but one six-month validation window can be overfit by 60 adaptive trials. Use **100 trials**, fixed seed, bounded space as METHODS specifies, with the same objective and no TEST use.
- Give profile7 a tuned lookback rival; day/week naive have no tunable parameters. Compare tuned LightGBM against both frozen and tuned-simple baselines, label the whole exercise exploratory.

4. **First attack / highest-value analysis**
- First attack: the reported intervals condition on one observed job sample and one alignment design, so they understate uncertainty for workload populations; p-values at the bootstrap floor reinforce that impression.
- Highest value: user-cluster outer bootstrap crossed with calendar blocks. Fixed BA is appropriate for the chosen estimand; do not bootstrap BAs as if randomly sampled.

5. **Post-hoc shopping**
- Prespecify and disclose all S2 lags, S3 factor sets, S4 state filters, S5 search space/trials and all seeds before running; publish unfavorable cases and identify results as exploratory.
- Keep the frozen TEST headline and confirmatory p-values untouched; do not call the sensitivity interval a replacement primary interval unless its method was specified before observing TEST.

[EDITOR]

1. **S1–S5 responses**
- **S1:** Yes to addressing uncertainty, but five extra seeds and an “across-seed SD” are not enough to claim job-population uncertainty; target **30 user-cluster resamples** with calendar blocks nested, or call the result Monte Carlo sensitivity only.
- **S2:** Use predeclared **1/3/6 h** delays and show all; include `lgbm|req`, `lgbm|pred`, and seasonal-naive day, all traces. **S3:** refit; **S4:** include timeouts as descriptive; **S5:** HPO and comparator details need freezing in the plan before execution. **S6:** explicit limitation is necessary.

2. **S3 direct factors**
- Oracle-only is not enough to support a claim about deployable carbon-aware scheduling. Minimum is the same forecaster pipeline trained on direct intensity with unchanged TRAIN/DEV rules and fixed hyperparameters, then TEST scoring for deployable and oracle arms.
- Frame it as an accounting-signal sensitivity, not proof of marginal avoided emissions; keep all specified factor choices visible.

3. **S5 HPO**
- Sixty trials could be acceptable for a small exploratory tuning run, but absent a search space and refit rule it is not auditable. Prefer **100 fixed-seed trials** with a compact documented space and TRAIN-only validation.
- Tune a profile7 window rival and show both frozen simple baselines and tuned rivals, so the tuning comparison doesn’t privilege LightGBM.

4. **First attack / highest-value analysis**
- First desk concern: title/abstract may overstate real-world carbon reduction when this is a synthetic placement of non-US workloads on revised historical average US grid signals, without queue capacity or imports/storage.
- The most valuable addition is S1 if it widens uncertainty materially; if time only permits one operational check, S2 at 3 and 6 hours is the clearest test of whether the forecast result survives realistic information delay.

5. **Post-hoc shopping**
- Call these “post-freeze exploratory sensitivities”; state the frozen result first, enumerate every attempted setting, and don’t promote the best sensitivity to the headline or suppress a negative one.
- Add each run’s code/input hash, command, seed, and deviation record; no new confirmatory claims from these analyses.

**VERDICT: RUN WITH CHANGES (S1 must separate user-sample uncertainty from seed spread; S3 refit the forecaster; define complete S2/S4/S5 settings and retain all outcomes as exploratory); confidence 0.91.**