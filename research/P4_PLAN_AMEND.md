# P4 amendments, fixed before any S1, X or new-arm run (D0016, 2026-11-12 01:35 IST)

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

