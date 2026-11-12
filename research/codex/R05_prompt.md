Round R05 (Paper A). Multi-expert review of the post-freeze sensitivity plan. Read-only.

Play three roles in turn and label each answer: [METHODS] a carbon-aware computing referee; [STATS] a statistics and
reproducibility referee; [EDITOR] the SUSCOM handling editor.

Context since R04: the PREREG was frozen (research/PREREG.md) and TEST was scored once. TEST, PM100, energy-weighted,
S = 12 h (tables/ledger_TEST.csv): oracle|act 5.75 %, lgbm|req (D) 1.90 % [1.81, 1.99] fixed-BA bootstrap, [1.45, 2.39]
two-stage; H1 1.90, H2 2.18, H3 1.03 pp, all Holm p 0.0015; Shapley gap 3.86 = forecast 1.56 + runtime 2.30;
lgbm|pred 2.93 %. Same direction on F-DATA and KIT FH2. An internal audit (research/A08_AUDIT_P3.md) found three major
threats: (1) intervals hold the job sample and alignment fixed, so they are too tight; (2) EIA-930 data are revised
and published with a delay, and the average signal excludes imports and storage; (3) Italian, Japanese and German
traces are placed on US grids. Owner rule: research-grade HPO; the frozen LightGBM is one untuned configuration
(research/A05_FORECASTS.md). Topic-close SUSCOM papers (research/JOURNAL_PROFILE_A.md section 4) assume runtimes are
known and use noise-injected forecasts.

Read research/P4_PLAN.md (S1-S6), research/PREREG_DEVIATIONS.md, and src/simulate.py, src/analyze.py as needed.

Questions (at most 4 lines per role per question):
1. Is each of S1-S5 the right response to its threat? Give exact design changes (seeds, k values, trial budget,
   which arms, which traces). For S1, how should job-sample and alignment uncertainty be combined with the block
   bootstrap so a referee accepts the interval?
2. S3: LightGBM forecasts lifecycle intensity. Is an oracle-only run under direct factors enough, or must the
   forecaster be refit? What is the minimum credible version?
3. S5: is "Optuna TPE, 60 trials, TRAIN-only, same validation window as frozen" research-grade? What budget and search
   space? Should profile7 and snaive also get a tuned rival, for fairness?
4. What will a SUSCOM referee attack first in this paper as it stands, and which single extra analysis buys the most?
5. Anything in the plan that would look like post-hoc result shopping, and how to word it so it does not.
End with: VERDICT: RUN AS PLANNED | RUN WITH CHANGES (list) | RETHINK (reason); confidence 0-1.
