Round R03 (Paper A, SUSCOM). Role: E1 methods reviewer and E6 adversarial referee. Read-only.

We are about to freeze the pre-registration and then score the held-out TEST year (2025-07 to 2026-06) once.
Files in the current folder (read them; do not edit):
- research/PREREG.md (the draft to freeze)
- src/simcore.py, src/simulate.py (scheduler and arms), src/analyze.py (bootstrap, Holm, Shapley, ledger)
- research/A07_JOBS.md (trace audit: state counts, r_act/r_req, TIMEOUT share, power semantics)
- research/A06_DATA_AUDIT.md, research/A05_FORECASTS.md (grid cleaning, forecasters, leakage tests)

DEV pilot (2024-07 to 2025-06, 42 BAs, 3 alignment replicates x 20,000 jobs, energy-weighted, S = 12 h), savings vs run-now:
- PM100: oracle|act 5.23 %, oracle|req 3.02, lgbm|act 3.68, lgbm|req 1.73 [1.33, 2.19], lgbm|pred 2.69, night 0.27,
  histprofile|req 0.76, profile7|req 1.05, persistence|req -0.16. H2 1.95 pp [1.34, 2.66]; H3 0.96 pp; H4 0.26 pp
  [0.08, 0.45]. Shapley of gap 3.50 pp: forecast 1.42, runtime 2.08, interaction 0.26; retained share 0.33. Per-BA H2:
  41 of 42 positive, 39 with 95 % interval above 0.
- F-DATA: oracle|act 6.54, lgbm|req 3.56, lgbm|pred 3.87, profile7|req 3.13, histprofile|req 2.39; H3 0.31 pp
  [0.07, 0.59]; retained share 0.54.
- KIT FH2 (no power, 1 kW per job): oracle|act 3.63, lgbm|req 1.38, lgbm|pred 1.69; retained share 0.38.
- Slack trend PM100 lgbm|req: 0.24 (2 h), 0.71 (6 h), 1.73 (12 h).

Questions. Answer each in at most 4 lines:
1. Is anything in PREREG.md ambiguous enough that a referee could say the analysis was chosen after seeing TEST?
   Give the exact wording fix.
2. Any bug or bias you can find in simcore/simulate/analyze that would change these numbers (planning window, ties,
   alignment, exclusion of jobs near unusable hours, replicate alignment, bootstrap, Holm, p-value floor)?
3. Is the two-stage bootstrap (BAs, then weekly blocks within BA) the right unit for a claim about "these 42 US
   grids"? Should H1-H4 be claimed for the population of BAs or for this fixed set?
4. H4 (interaction) is significant on DEV on all traces. Keep it confirmatory, or demote to secondary?
5. Missing baselines or secondary analyses a SUSCOM referee would demand (for example a padded or quantile runtime
   estimate, a "req capped at k x pred" heuristic, or a carbon-aware scheduler from prior work)? Name at most 3 and say
   whether each belongs before the freeze.
6. Anything that should block the freeze.

End with one line: VERDICT: FREEZE | FREEZE AFTER FIXES (list) | DO NOT FREEZE (reason); confidence 0-1.
