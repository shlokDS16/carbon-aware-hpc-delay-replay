## 1. Strongest objection by role

- **[EDITOR]** “The manuscript is in scope, but it is not submission-ready: the abstract/front matter and multiple results still contain placeholders, so I cannot judge the complete contribution or reproducibility.”
- **[IMPACT]** “A saving of roughly 1–4% may be statistically detectable yet operationally negligible; the paper does not show the system-scale emissions or operational cost that would make this matter.”
- **[OVERLAP]** “Forecast-versus-oracle savings are established by ReBase and LiteCast, while runtime error is studied by LACS; this looks like combining known components without enough new insight.”
- **[VALIDITY]** “Foreign job calendars replayed on U.S. average grid intensity, with free capacity and revised delayed data, cannot support claims about real avoided emissions or feasible scheduling.”
- **[AUTHOR]** “Our main risk is framing a careful counterfactual measurement as an operational result: it is neither U.S.-workload evidence nor a queue-feasible estimate of marginal emissions.”

## 2. [AUTHOR] Best answers and post-hoc work, ranked by value per hour

1. **Impact:** Lead with absolute effects already in `ledger_TEST_posthoc.csv`: D removes 6.6379/13.204/5.2683 g CO₂e per kWh and 47.115/126.47/27.437 g per job on PM100/F-DATA/KIT (`posthoc.PH4.*.lgbm|req.g_per_kwh.est`; `posthoc.PH4.*.lgbm|req.g_per_job.est`). Show the 24 h slack results already in `ledger_TEST.csv`: 2.6764%, 5.6689%, 2.1997% (`TEST.*.w.S24.saving.lgbm|req`); this is a different operating allowance, not evidence of a free improvement. A facility-wide annual tCO₂e estimate needs a defensible annual energy denominator and workload representativeness; otherwise it risks false precision.
2. **Validity:** The existing latency sensitivity preserves positive modeled savings at 24–48 h, but it delays revised data rather than recovering first-release vintages (`sens.s2b.PM100.w.S12.k24.saving.lgbm|req`, `...k48...`; corresponding F-DATA and KIT keys). Direct-factor and oil-factor sensitivities also remain positive (`sens.s3a.*.saving.lgbm|req`; `sens.s3b.*.saving.lgbm|req`). Best quick addition: a predeclared top-quartile-by-TRAIN daily-range summary and lgbm|pred versus oracle|act distance in those BAs; **needs a light post-hoc computation from saved per-BA replay results and TRAIN grid series**. It illustrates where the opportunity is, not generalizes to U.S. sites.
3. **Overlap:** ReBase isolates forecast error for wind/unit tasks; LiteCast evaluates forecasts with known job lengths; COAST uses actual runtime and intensity without a carbon forecast or requested walltime; LACS uses synthetic errors. The distinctive claim is the measured two-input gap on real HPC traces, not a first oracle comparison. No extra analysis required; tighten the related-work claim to this exact combination.
4. **Editor:** Replace “deployable” as the default arm label with “forecast-and-request” (retain the conditional definition), fill all pending boxes and front-matter/DOI/repository placeholders, and ensure tables, figures, supplement, and ledger agree before submission.

## 3. Reframing

**Contribution:** “Across three real HPC traces replayed on 42 U.S. grids, a delay planner using a past-only carbon forecast and requested walltime retains positive modeled average-intensity savings; a two-factor replay measures how forecast and runtime information contribute to the remaining gap.”

**Title:** *Past-Only Carbon Forecasts and Requested Walltimes Preserve Modeled Savings in HPC Batch Scheduling*

It is true across the three traces without implying deployment or avoided marginal emissions.

## 4. Other acceptance risk

The current paper says the historical data and latency analyses support a past-only decision while acknowledging that first-release EIA values are unavailable and revisions remain unmeasured. Keep this limitation adjacent to the latency result, and do not describe D as operationally validated. Also ensure the KIT FH2 citation-request terms, non-redistribution, archive DOI, and code-access statement are resolved before submission.

**VERDICT: ACCEPTABLE AFTER (complete pending runs and front matter; narrow “deployable” language; keep counterfactual, average-intensity and free-capacity limits prominent; make the overlap claim explicitly about the two-input measurement); confidence 0.86.**