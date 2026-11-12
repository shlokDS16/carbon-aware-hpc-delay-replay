# Panel decisions, Paper A (2026-11-12 01:30 IST, D0016). Binding for SPEC v1, drafting and new analyses.

Sources: research/panel/P1_EDITOR.md (send out after changes), P2_DOMAIN.md (major as planned), P3_STATS.md (minor as
planned), research/codex/R06_resp.md (draft after changes, 0.90).

## A. Story and claims
1. Lead with the bounded replay finding: the deployable arm (lgbm|req) gives a positive modelled saving at 12 h slack
   on all three trace replays and keeps part of the same planner's perfect-information saving; the history-based
   runtime prediction raises the saving on all three. Numbers only from ledger keys. Finding inside the first 150
   abstract words.
2. Absolute effect beside relative (run-now mean intensity per trace; g CO2 saved per job and per kWh) before the
   retained share.
3. Shapley terms are descriptive allocations, not causal; ordering is trace-specific. "Forecast term > runtime term"
   (or the reverse) is stated only where the interval of the difference excludes zero (post-hoc analysis below).
   Never "runtime matters more" in general. No "jointly determine" title.
4. Operational advice is a hypothesis ("the replay suggests"), not "operators should".
5. Framing: counterfactual replay of non-US traces on US balancing-authority signals; production-average intensity,
   not avoided marginal emissions; the oracle is the same heuristic with perfect inputs, not a global optimum;
   no queue capacity (bound under free capacity).
6. p-values only for H1-H3, written "p < 0.0005 (Holm-adjusted < 0.0015)"; none for exploratory items.
7. H1-H3 confirmatory on PM100 only; F-DATA and KIT FH2 are secondary replications.

## B. Counts (owner rules override the panel where they conflict; reason: explicit owner instructions D0012 and
## the kickoff rules in CLAUDE.md section 9)
- Figures: 13 in the main text (owner rule 13-14; panel wanted 9-12). Each must answer a distinct question; merge
  FIGURE_PLAN 11 and 12 (cross-BA) and make room for one robustness figure and one runtime-accuracy (X1) figure.
- Algorithms: 3 boxes (owner rule: several small algorithms building to one final; editor: 3-4): (1) planner with the
  runtime estimate (merge Plan and RuntimeEstimate), (2) calendar alignment and simulation of one arm, (3) the full
  evaluation pipeline with bootstrap (final algorithm).
- References: about 60, every one tied to a claim (owner: high, well-used count; panel 45-55).
- Length: about 10,500 words of body text.

## C. New post-hoc inference (POSTHOC; light, runs now on saved results; labelled post-hoc, own ledger
## tables/ledger_TEST_posthoc.csv, a PREREG_DEVIATIONS row, new script src/posthoc_inference.py, frozen code imported)
- PH1 synchronised-week bootstrap: the same 7-day block indices for all 42 BAs in each replicate (blocks aligned on
  calendar weeks of the TEST arrival span), B = 2000, seed 7 + S; D, H1-H3, H4, Shapley terms; all three traces.
- PH2 Shapley-term intervals and the interval of (forecast term - runtime term), under the frozen bootstrap (same
  function, same seed) and under PH1.
- PH3 per-BA H2 full 95 % within-BA intervals (lower and upper), frozen per_ba_boot function and seed.
- PH4 absolute effects: run-now mean realised intensity (g/kWh) per trace, and saving in g CO2 per job and per kWh
  for each arm, with intervals from the frozen bootstrap.
- PH5 reproducibility: environment lock (py -m pip freeze to research/ENVIRONMENT.txt, Python and numpy versions),
  md5 of every results file and forecast file (research/RESULTS_MD5.txt), the exact commands of every TEST run
  (main, twostage, near-limit) in research/RUN_COMMANDS.md, and src/rebuild_ledgers.py that rebuilds every ledger
  from results and checks equality.
- Interval names in all text: "calendar interval" (frozen block bootstrap), "synchronised-week interval" (PH1),
  "workload-sample interval" (S1).

## D. P4 amendments (before any S1 run; recorded in research/P4_PLAN_AMEND.md with md5)
- S1: add an original-users control (same 30 seeds, users not resampled, one alignment replicate each); the total
  interval is a normal approximation around the frozen estimate with variance = calendar variance + between-outer
  variance (law of total variance), reported beside the percentile version.
- New exploratory arms (P2): forecast-free threshold rule (start at the first quarter-hour whose current observed
  intensity, known at decision time, is below the trailing 7-day 25th percentile, else at a + S); padded runtime
  estimate min(R_req, 1.5 x pred); quantile runtime estimate (user's 90th percentile of past actual runtimes, at
  least 5 past jobs, capped at R_req; else R_req). PM100, F-DATA, KIT FH2; lgbm and oracle signals; S = 12 h. X1
  sweep stays as in P4_PLAN_X.
- X7 extended to lgbm arms only if the fossil-only signal can be forecast with the frozen pipeline unchanged (refit,
  same hyperparameters); else oracle arms only, stated.
- Placement shift check (P2): arrivals shifted by +/- 3 h local clock, lgbm|req and lgbm|pred, PM100.

## E. Before final prose (pre-submission blockers, R06 and P1)
- KIT FH2 licence (Parallel Workloads Archive terms), EIA-930 publication-delay source, and full reads of LACS,
  COAST, LiteCast, Tsafrir et al. 2007 and Mu'alem and Feitelson 2001 (numbers on walltime inaccuracy).
- Figures 6 and 7 rebuilt (FIGURE_FIXES); Shapley intervals in Figure 7.
- Main-text robustness table: S1-S4, PH1; S5 and X2, X3, X5-X7 in the supplement; X1 and X4 compact in the main text.
- Supplement: an all-cells table (every arm x trace x slack x weighting) and an analysis registry (every analysis,
  status confirmatory / secondary / post-hoc / exploratory, file, ledger).
