# Best-paper bar for Paper A (from research/EXEMPLARS.md, agent A02, and Codex R01-R02; 2026-11-11)

Bar set by: Sukprasert et al. EuroSys 2024 (123 regions, 3 years, CIs, Zenodo artifact), Wiesner et al. Middleware 2021
(4 regions, 10 runs, GitHub), Radovanovic et al. TPWRS (Google fleet, 95 % bands), CarbonCast BuildSys 2022, SUSCOM
#1 Desislavov et al. 2023. SUSCOM lane-A sample reports no uncertainty and mostly simulated workloads.

Each item is a checklist item in progress.md P4-P8.
| # | They do | We must do | Status |
|---|---|---|---|
| B1 | 123 regions, 3 years hourly (Electricity Maps, login-gated) | All EIA-930 BAs with usable fuel data (about 50-65) over 7+ years, plus an open non-US set if obtainable (GB regional Carbon Intensity API, which also publishes real operational forecasts); state why not 100+ (open-data limit) | open |
| B2 | Code and data released | Zenodo archive with reproduce-all script, derived data, ledger, PREREG | open |
| B3 | CIs or 10 runs | Block bootstrap over days within BA, BA-level aggregation, paired tests, Holm | open |
| B4 | Carbon-agnostic baseline, simple policies, oracle | Run-now, fixed night window, historical clean-hour profile, persistence, seasonal naive, GBM forecast, oracle | open |
| B5 | Simple policies capture most gain | Test every method against the best simple policy; report plainly | open |
| B6 | Synthetic or scenario forecast error | Real past-only forecasters; real operator forecasts where published (GB) | open |
| B7 | Configured job classes or proprietary data | Real public job traces with requested and actual runtimes (A04 audit) | open |
| B8 | What-if scenarios | Cleaner-grid scenario (by BA mix strata and over years) ; capacity case cut per Codex R02 unless time (state as limitation) | open |
| B9 | One gap sentence + contribution list | Gap sentence + related-work comparison table (us vs Wiesner, Sukprasert, Radovanovic, CarbonCast, LACS, COAST) | open |
| B10 | Relative gains only | Absolute (gCO2 per job-hour, kgCO2) and relative effects with CIs | open |
| B11 | 11-13 figures, 1-6 tables, 9-13.5k words | 13-14 figures (owner rule), 4-6 tables, 9-11k words | open |
| B12 | Descriptive titles, mean 13.4 words | Finding-led title (owner rule) under about 18 words naming the object | open |
| B13 | Abstract 180-308 words, 25 w/sentence, a third passive, "we" | 220-250 words with numbers and CIs; "we" allowed (exemplars use it); one English variant | open |
| B14 | Simulator metaheuristics | Real data, pre-registered held-out year, leakage audit | open |
| B15 | (Codex R02) trace semantics | Audit status codes, kill-at-limit share, requested/actual ratio before analysis | open |
