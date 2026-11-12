## 1. E1 desk view

**Borderline yes, if the paper is framed as a trace-grounded study of runtime information in carbon-aware scheduling.** The gap is plausible and the data are public; the main desk risk is that “real runtimes” are not necessarily runtimes the scheduler could have known or predicted. With older job logs randomly aligned to newer grid traces, this is a replay study under an explicit synthetic calendar, not a contemporaneous production evaluation. State that plainly.

## 2. E6: strongest attack

The central attack is that the runtime effect may measure **trace semantics and scheduler construction**, rather than the value of runtime information. Requested walltime may be a kill limit, a conservative cap, or a user-set value; actual runtime may include failed or retried jobs. If jobs end early, a planner that reserves their full requested duration can appear badly misinformed even though the real system would release capacity and admit another job. Conversely, using final observed runtime in the oracle gives the oracle information unavailable at submission.

Before analysis, verify the exact SWF schema and status codes, and report how many records are successful, killed, failed, or otherwise excluded. Check whether job arrays or repeated workloads let you construct a legitimate history-based prediction without leakage. If not, the claim that a two-run user-history mean recovers most runtime loss is especially vulnerable: “user” may not identify a stable workload, and two prior completions may be too few or too selective.

The **2–5× overestimation** claim needs trace-specific evidence, not HPC folklore. Report the requested/actual ratio distribution for eligible successful jobs, including medians, tails, and shares at or near the requested limit. If many jobs terminate at the limit, or if the effect vanishes after excluding questionable records, the result is an artefact. If job lengths are systematically overestimated but the chosen start is unchanged because carbon intensity is flat within the slack window, the runtime term may also be practically trivial.

Randomly aligning historical jobs to modern grid years is a major external-validity limitation. It can support a controlled replay, but cannot show what actual operators would have saved. Pre-register the alignment and repeat over multiple offsets; don’t select one that produces a large effect.

## 3. E3: estimands and scheduler

Define jobs as eligible, successful, non-interruptible jobs with a valid arrival and requested walltime. The decision is a start time within a fixed **slack window** after arrival; define whether slack means latest allowable start or latest allowable completion. I recommend latest allowable start, with the same deadline constraint in every arm.

At each arrival, the planner sees only the carbon forecast available then and either requested walltime or a runtime prediction trained only on prior records. It chooses the feasible start minimizing forecasted emissions over the **predicted execution interval**. Evaluation uses realized start, actual runtime, and held-out production-based carbon intensity integrated over actual execution. Keep job energy constant per unit time in the main design; otherwise runtime and energy uncertainty are confounded. Specify whether the workload’s power is constant or estimated from trace data.

Estimands:

1. **Realized savings:** percent emissions reduction versus run-now, per eligible workload replay.
2. **Runtime-information penalty:** change in realized emissions when using requested walltime rather than a leakage-free runtime prediction, holding forecast and constraints fixed.
3. **Forecast penalty:** change when replacing the oracle signal with a past-only forecast, holding runtime information fixed.
4. **Interaction:** whether the combined loss differs from the sum of the two single-information losses.

Confirmatory hypotheses (one-sided only if preregistered):

- Forecast-aware scheduling reduces emissions versus run-now.
- Runtime prediction reduces emissions versus requested walltime.
- Forecast and runtime information have a nonzero interaction.
- Runtime-information benefit is larger for short jobs or larger slack (choose one primary interaction; treat the other as exploratory).

Use paired replays. Bootstrap contiguous day blocks within balancing authorities, then aggregate at the BA level; do not treat every job-hour as independent. Apply Holm to the confirmatory family. Report per-BA effects and uncertainty, alongside pooled estimates.

At hourly resolution for 1–48 h ahead, the minimum credible forecast set is **persistence**, **seasonal naive** (same hour of prior day/week where available), and **one past-only learned model** such as gradient boosting. Compare against the oracle and non-forecast policies as bounds/baselines, not forecasters. Fit and tune without held-out data. Report forecast performance by lead time; overall MAE alone may hide wrong within-window rankings.

## 4. Attribution

The 2×2 Shapley decomposition is defensible as an **accounting attribution**, not causal identification. It allocates the interaction symmetrically between forecast and runtime information, but that convention is not uniquely “correct.” Show all four cells and the interaction directly; label Shapley shares as a summary convention. Use the same job set and paired replays in every cell.

## 5. Four-day cuts and recommendation

Cut capacity-constrained replay, MAE-versus-ranking analysis, marginal factors, and extra power modeling. Keep the prespecified runtime predictor only if trace history supports it; otherwise compare requested runtime with oracle actual runtime and present the latter strictly as an upper bound. Limit the headline to one primary runtime contrast and one held-out grid year.

**Recommendation: proceed with C8 only after the trace audit. Confidence it is the best choice: 0.68.** The novelty case is stronger than C2’s, given the supplied scout findings, but the runtime result depends on semantics and censoring checks that could invalidate the headline. If those checks fail, C8 should be reframed as an upper-bound sensitivity study rather than a claim that history-based prediction recovers savings.