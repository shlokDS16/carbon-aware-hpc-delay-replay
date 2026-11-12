1. **PREREG ambiguity / exact wording fix**

- The “deployable arm” justification cites an obsolete v0 result (32/37 BAs), while the frozen design uses the final 42-BA forecast run. Replace it with: **“Deployable arm D = lgbm|req, selected on DEV because final-run LightGBM had lower 1–24 h MAE than seasonal-naive day in 38/42 BAs and lower MAE than profile7 in 41/42; no TEST skill or outcomes informed this choice.”**
- Also reconcile the prereg’s **≥90%** BA validity threshold with A06’s final **≥95%** rule. State the exact frozen eligibility rule and identify the exact 42-BAs table/version.

2. **Code or bias issues that could change results**

- **Inference blocker:** `analyze.py` computes p-values from the uncentered bootstrap distribution’s fraction above/below zero. That distribution is centered near the observed effect, not the null; plus-one and Holm do not fix this. Use a null-centered bootstrap test (or prespecify interval-based decisions instead of p-values), then rerun DEV before freeze.
- At S=24, a 72 h planning interval starting at a fractional hour can extend to nearly 97 h, but `plan_start` truncates costs at H=96; `place_jobs` checks unusable hours only through 96 h. This can alter secondary results. Extend/check the horizon or exclude affected jobs, and state that the primary S=12 horizon is unaffected for requested runtime ≤72 h.
- Tie handling is correctly earliest-start. Replicate day totals are summed before bootstrap; `weekly()` then drops leftover days and forms arbitrary consecutive 7-day blocks, not calendar weeks. Clarify the block definition and handle the remainder explicitly. **Do not treat the pilot p-values as valid** until the p-value issue is corrected.

3. **Inference target and resampling unit**

- The BA bootstrap implies inference to a population of BAs, but these 42 are selected by coverage and generation criteria, not randomly sampled. The defensible primary claim is about **this fixed eligible set of 42**, with paired weekly-block resampling for temporal uncertainty; report BA heterogeneity descriptively.
- If retaining BA resampling, label it a sensitivity analysis over a hypothetical population of eligible BAs, not the primary basis for a claim about all US grids.

4. **H4**

- **Demote H4 to secondary.** Its interaction was examined on DEV and is significant across the pilot traces, so promoting it into the confirmatory family at freeze invites a post-selection critique. Report the four cells and interaction estimate/interval descriptively; no confirmatory p-value.

5. **Baselines / analyses**

- **Requested walltime capped at \(k \times\) history prediction** (or a prespecified padded prediction): important operational comparator given the very large request/actual gap. Add before freeze only if \(k\) is fixed without TEST input; otherwise label exploratory.
- **One established carbon-aware scheduler/policy baseline:** useful for SUSCOM novelty, but add before freeze only if a faithful implementation is already feasible and its information assumptions can be matched; otherwise explain the simpler policies’ scope.
- **Completed-job sensitivity excluding runtimes near the request limit:** add before freeze. PM100’s 92.2% of TIMEOUT jobs are within 2% of requested walltime, and KIT has no TIMEOUT label, so this checks whether apparent runtime overestimation reflects censoring/status semantics.

6. **Freeze blockers**

- Fix the null p-value calculation and rerun DEV; resolve the eligibility-threshold/version mismatch; specify the actual weekly-block and remainder handling. Also remove “measured job power” for PM100: A07 says PM100 power is sampled/averaged and energy is derived, not directly measured.

**VERDICT: DO NOT FREEZE (fix inference, eligibility/version, block handling, and PM100 power wording first); confidence 0.94.**