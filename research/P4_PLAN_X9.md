# X9 capacity-capped replay and post-hoc impact items, fixed before running (2026-11-12 09:30 IST, D0025)

## B. Light post-hoc computations (one script src/posthoc_impact.py, ledger tables/ledger_TEST_posthoc_impact.csv,
## labelled post-hoc, one deviations row; settings fixed here before running)
B1 Scale table: g CO2e per kWh and t CO2e per MW-year for D, lgbm|pred, oracle|act, S12 and S24, all traces (PH4 keys
   x 8.76).
B2 Top-quartile BAs by TRAIN median daily intensity range (quartile fixed on TRAIN data only): pooled saving of D and
   lgbm|pred and their share of oracle|act in those BAs vs the rest, S12, all traces, with the frozen calendar
   bootstrap restricted to those BAs (seed 7 + S).
B3 Absolute contrasts: H2 and H3 in g CO2e per job and per kWh with intervals (frozen bootstrap).
B4 Share of BA-weeks with positive D saving (only if the saved per-BA weekly arrays support it; else skip and say so).


## C. One more exploratory run (fixed before running; research/P4_PLAN_X9.md with md5)
C1 X9 capacity-capped replay (E_VALIDITY F2): per BA and trace, at most the run-now peak hourly job-energy of the
   arm's own sample may start in any hour (cap = 1.0 x the run-now 99th percentile hourly start energy); jobs that
   would exceed it take the next candidate start in their slack, else run now. Arms lgbm|req, lgbm|pred, oracle|act,
   S12, PM100 first, then F-DATA and KIT FH2 if time allows. Reports savings and the share of jobs displaced.

