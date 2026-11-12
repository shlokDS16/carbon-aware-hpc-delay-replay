# P4 amendment 2, fixed before any run of it (2026-11-12 01:25 IST, D0017)

Reason: research/journal/A20_LIT_LICENCE.md (EIA documentation): EIA-930 generation by source is available about one
day late and revised for up to 3 days (30 days for errors). The S2 lags (1, 3, 6 h) are kept as fixed in P4_PLAN v2
and reported; S2b adds realistic publication delays.

- S2b data latency at publication scale: k in {24, 48} h, the planner uses the LightGBM forecast issued at
  floor(a) - k with leads shifted by k; leads beyond 96 hold the lead-96 value (same rule as the frozen design for
  intervals 96-97). Arms lgbm|req, lgbm|pred, snaive_day|req; oracle unchanged and labelled an upper bound. All three
  traces, S = 12 h, energy-weighted. Every k reported.
- Revisions (first-release vs revised values) cannot be tested: first-release EIA-930 values are not archived in the
  project data; stated as a limitation.
