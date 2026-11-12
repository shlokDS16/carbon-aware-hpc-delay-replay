VERDICT: A13 done; overlap C1..C5 = C1 SUBSTANTIAL (A3, concept only; wind not grid carbon), C2 NONE, C3 NONE, C4 NONE, C5 PARTIAL (A1); risk: do not claim "first oracle-vs-forecast gap" and do not claim "first multi-grid real-trace study", only the walltime/2x2/held-out-year combination is unmatched.

# A13 novelty and overlap audit of Paper A against five SUSCOM papers (2026-11-12)

Pointers: "md:Lnnn" = line in `research\sources\suscom_pdfs\md\1-s2.0-<stem>-main.md` (PDF text, read as data). "PREREG s." = `research\PREREG.md`. Full texts of all five were read in the parts listed; unread parts are said so. Wiesner, Sukprasert and Radovanovic come only from `research\EXEMPLARS.md` rows 7-9 (arXiv preprints read by agent A02, not re-read by me); cells I could not source are marked "not extracted".

## 0. Paper A in one line (PREREG s.1, s.4-7)
Non-interruptible batch jobs, delay start within slack S in {2,6,12,24} h (primary 12 h) on 42 US balancing authorities; arms = (oracle | past-only LightGBM carbon forecast) x (actual runtime | requested walltime) plus history-predicted runtime; Shapley split of the gap oracle|act minus lgbm|req (PREREG s.7.1); PM100 confirmatory (energy-weighted), F-DATA and KIT FH2 secondary; frozen held-out TEST year; Holm over H1-H3 with block bootstrap (PREREG s.6).

## 1. Per-paper extraction

### A1 Attenni, Moawad, Bartolini, Thamsen, 10.1016/j.suscom.2026.101498 (SUSCOM 52, 2026; stem S2210537926002088)
- Problem and decision variable: where (region) and when (start time) to run a job to minimise a weighted carbon, water and land-use footprint; spatial, temporal and spatio-temporal shifting (md:L755-790, Eq. 9-12). Temporal rule is the Let's Wait Awhile argmin over [arrival, deadline] (md:L810-823).
- Workload: Scenario 1 = Azure Functions 2019, 100,000 synthetic requests per day with runtimes sampled from published percentiles, no deadlines, only spatial shift (md:L915-935). Scenario 2 = AWS Spark traces (Scout), 50k requests over a week, arrival times and origin synthetic, 50 % periodic jobs; runtime "as reported in the traces" (md:L1021-1050). Deadline = periodicity or a tunable delay tolerance dt in {4,12,24,48} h (md:L1056-1060, L1405-1406). Interruptible: not stated; jobs are placed once. Not HPC.
- Carbon signal: average (not marginal) carbon intensity from the grid mix with IPCC lifecycle medians; grids in Table 5 include ERCOT, MISO, PJM, CAISO plus European grids; one mid-season week (15th-22nd) per season, season varied (md:L1168-1262). Hourly.
- Forecasting: none trained. "Predictions" are the true mix with synthetic noise, MAE 0.05, 0.1, 0.15, 0.2, error split by source (solar 45 %, wind 30 %, ...) (md:L1135-1160, L1253-1256). Authors state that an operational forecaster remains future work (md:L3030-3036).
- Oracle: no perfect-information benchmark; baseline is the Local (run where and when requested) schedule (md:L805-806). The gap to perfect information is not analysed.
- Runtime uncertainty or requested walltime: not tested. Threats to validity: "it is assumed that the application runtimes are available to the schedulers" (md:L3043-3047; one quote); they add low-error estimates "could be available from previous runs or profiling".
- Baselines: Local; carbon-only temporal (WaitAwhile-style), GreenCourier-inspired spatial, WaterWise-inspired spatial (md:L810-855).
- Scale: one week per season, 4 seasons, 4 (Scenario 1) or 5 (Scenario 2) regions; the temporal results use a single winter week at MAE 0.1 (md:L1399-1406).
- Statistics: six seeds (0-5) per simulation, means and standard deviations; no intervals or tests (md:L1253-1255).
- Headline: temporal shifting gives 6 % to 12 % even at dt = 48 h (md:L1414-1417); spatial 20 % to 85 % depending on scenario and objective (md:L3096-3102).
- Admitted limitations: simulation only, resources assumed available, synthetic noise in place of a forecaster, runtimes known, arrival synthetic, embodied impacts excluded (md:L2966-3060).
- Code and data: released (GitHub GlasgowC3lab/CaWaLand, md:L175).

### A2 Zhai et al., 10.1016/j.suscom.2025.101216 (SUSCOM 48, 2025; stem S2210537925001374)
- Problem: two-stage geo-distributed scheduling of delay-tolerant workload across 3 data centres powered by wind plus grid; decision variables are binary assignment of workload to (DC, slot), offline stage then real-time correction (md:L283-308, L644-735, L1396-1650).
- Workload: aggregate workload arrivals per slot from the Alibaba 2018 cluster trace; CPU treated as elastic and non-binding; deferral within delay bounds; no per-job runtime or walltime (md:L1919-1936, L2108-2112 "before/after" feasible slot sets). Interruptible: not stated.
- Signal: wind power (Vestas V90 model, open database, normalised) at Ningxia, Guizhou, Gansu; grid emission factors per DC as parameters (md:L745, L1921-1932). 96 hourly slots. It is not grid carbon intensity.
- Forecasting: what is forecast = workload arrivals and wind power; EMD-VMD plus LSTM/xLSTM; five-fold expanding rolling CV (70 % initial) (md:L2068-2078); horizon via look-back windows (Fig. 9).
- Oracle or perfect benchmark: no scheduler oracle. A sensitivity sweep injects WP forecast error MAE 0 to 0.12 (Fig. 11), with zero error as one point; utilisation rises 16.10 % from MAE 0 to 0.03 because stage 2 is not triggered at zero error (md:L2745-2760 text, Fig. 11 caption md:L2900-2902). This is injected error, not a past-only forecast.
- Runtime uncertainty or walltime: none beyond a parameter "execution time of workload" (Table 1 notation, md:L735).
- Baselines: greedy, round-robin, real-time-only ablation, 10-DC scale-up (md:L2040-2064).
- Scale: 3 DCs (10 in scale-up), 96 h.
- Statistics: "5-fold CV mean" (Table 7 caption); no intervals, no tests.
- Headline: WP utilisation +17.73 to 40.40 % and 8.55 to 16.27 t CO2 avoided against the baselines (md:L2900-2906, abstract md:L28-36).
- Limitations: capacity and contention not modelled "left to future work" (md:L1931-1933); future work lists better preprocessing and RL (md:L2905-2910).
- Code and data: not released ("plan to release them upon the completion of the related work", md:L3044-3047).

### A3 Zhai et al., ReBase, 10.1016/j.suscom.2026.101470 (SUSCOM 52, 2026; stem S2210537926001800)
- Problem: prediction-driven two-stage scheduling of delay-tolerant unit workloads across 3 geo-distributed DCs; offline MILP baseline from forecasts, then RL residual correction (md:L405-470, L592-660). Decision variables: integer counts of unit workloads from arrival slot to execution slot and DC (md:L264-300).
- Workload: normalised unit tasks with identical energy, intra-DC constraints abstracted away (md:L238-248); traces from Google (Reiss et al.) and an Alibaba microservice study; scheduling experiments use WL-WG only (md:L711-725); maximum delay 6 slots (md:L801-805). No runtimes at all.
- Signal: wind power (Renewables.ninja) at NX, GS, GZ; grid emission factor as a parameter (md:L879); not grid carbon intensity.
- Forecasting: multi-step wind power and workload forecasts by decomposition (EMD, EWT, CEEMDAN, VMD) plus LSTM, chronological 0.8/0.2 split, scalers fitted on training only, five-run rolling evaluation, horizons 6, 12, 24 (md:L711-740, L801-805).
- Oracle: yes. "A perfect-information benchmark" solving the same MILP with realised WP and workload (md:L841-845). Gap analysed by horizon: wind-utilisation gap 1.03 % at H = 6 widening to 7.38 % and 11.33 %; carbon overhead 3.09 %, 13.71 %, 21.88 % (md:L1195-1210; Table 8 md:L1119-1153). A conditional bound says the ReBase-to-Oracle gap is bounded by the baseline-to-Oracle gap (md:L694-706). The gap is attributed to forecast quality only; no second information factor.
- Runtime uncertainty or walltime: none.
- Baselines: Pred-RR, Pred-Off (MILP baseline without correction), OnlyRL, E2E-RL, ablations (md:L810-860).
- Scale: three DCs, three horizons; five seeds for RL methods, deterministic baselines run once (md:L800-806).
- Statistics: mean and standard deviation over five RL seeds (Table 8: 90.54 plus or minus 0.11 WU); no tests.
- Headline: ReBase approaches the Oracle with a "wind utilization gap as low as 1.03%" (abstract md:L63-66).
- Limitations: Oracle gap widens with horizon; restricted online decision space; abstracted intra-DC constraints (md:L1232-1248).
- Code and data: not released ("may be open-sourced after completion", md:L1252-1256).

### A4 Liow et al., CARA, 10.1016/j.suscom.2026.101407 (SUSCOM 51, 2026; stem S2210537926001174)
- Problem: pick (region, start time) in a window to minimise carbon for one task with duration d and deadline T_max; search over S = {(r,t)} (md:L423-470).
- Workload: simulated tasks; primary a 3 h model-training profile; sensitivity adds 1 h and 6 h profiles; 12 h MaxLatency; estimated duration in the Task object, compute emulated (md:L545-600). No trace. Interruptible: not stated.
- Signal: marginal emissions rate forecasts from the ElectricityMap API for 4 AWS regions (Malaysia, Melbourne, California, Frankfurt) (md:L580-595).
- Forecasting: forecasts are fetched, not built or scored; the paper says forecast error is a limitation and defers controlled error levels 5, 10, 20 % to future work (md:L870-880).
- Oracle: none. Baseline is Local-Immediate in Malaysia (md:L675-681).
- Runtime uncertainty or walltime: none; duration is given.
- Baselines: Local-Immediate; a relative comparison against CarbonFlex "[6]" (md:L855-862).
- Scale: effectively one decision per profile, n = 3 archetypes (md:L901-912).
- Statistics: mean, SD and a 95 % CI over n = 3 profiles, [70.6 %, 90.0 %], then "we reject the null hypothesis" (md:L903-914).
- Headline: "a 75.7% reduction in carbon footprint" (abstract), mostly spatial arbitrage (single case, 2009 against 488 gCO2eq, Table 2).
- Limitations: forecast dependence, cloud costs, emulated not native deployment (md:L870-890, L960-975).
- Code and data: "Data will be made available on request" (md:L981).

### A5 Chen, Ma, Wang, Yao, 10.1016/j.suscom.2023.100950 (SUSCOM 41, 2024; stem S2210537923001051)
- Problem: ESTS two-stage spatio-temporal scheduling of online and offline computing load across data centres to raise renewable consumption, cut carbon and cost (md:L620-715). Offline load can be delayed within deadline and server limits (md:L1050-1060).
- Workload: Alibaba cluster_trace_v2018 offline requests, 7 days, converted to a number of servers; max 2000 servers, 80 % utilisation, 3000 W (md:L787-805). No per-job runtimes or walltime. Not HPC.
- Signal: China 2019 regional baseline emission factors plus wind and solar average intensities (static, not time-varying grid intensity); four data centres (Guizhou, Ningxia, Inner Mongolia, Gansu) (md:L806-815).
- Forecasting: none; scheduling is offline with known load and supply. No oracle versus forecast comparison.
- Runtime uncertainty or walltime: none.
- Baselines: Wuhan grid-supplied data centre; CSS4 (cost-oriented suspension scheme); ESTS1 single DC (md:L747-775, L967-973).
- Scale: four seasons x 7 typical days; 1 to 4 DCs.
- Statistics: none (descriptive comparisons of fluctuation by season).
- Headline: abstract reports "carbon emissions by 70% and operating costs by 40%".
- Limitations: future work on storage and demand response only (md:L1076-1085); no limitation paragraph.
- Code and data: "I have explained the source of various data in the article." (md:L1104); no code.

### Exemplars (from EXEMPLARS.md rows 7-9 only)
- Wiesner et al. 2021 (arXiv:2110.13234): carbon intensity for 4 regions, 2020; nightly-job and ML-project scenarios (3,387 jobs); delay tolerance assumed; baseline issue-time start; optimal versus 5 % error forecasts, 10 repeats averaged; no intervals or tests; code public. Runtime treatment: not extracted.
- Sukprasert et al. 2024 (arXiv:2306.06502): 123 regions, 2020-2022 hourly; synthetic job classes (length, deadline, interruptibility); "ideal upper bounds" and simple versus sophisticated policies; has a prediction-error scenario; averages with intervals over 8,760 start times; Zenodo and GitHub released. Real traces: cited but results use configured workloads.
- Radovanovic et al. 2023 (arXiv:2106.11750 preprint): production Google fleet, day-ahead carbon forecasts, measured not simulated; 95 % bands on hourly means; no code.

## 2. Overlap verdicts

Levels: NONE = element absent; PARTIAL = element present in a different form (different signal, workload or only injected error); SUBSTANTIAL = the same measurement in a comparable setting.

| Paper | C1 realised saving past-only forecast vs oracle | C2 cost of requested walltime vs actual runtime | C3 2x2 decomposition of the gap | C4 history-based runtime prediction | C5 real HPC traces, many grids, held-out year |
|---|---|---|---|---|---|
| A1 | PARTIAL: noise-injected "forecast", no oracle arm (md:L1135-1160) | NONE: runtimes "assumed available" (md:L3043) | NONE | NONE: only cites profiling literature (md:L3046) | PARTIAL: real Azure and Spark traces with synthetic arrivals, 4 US BAs among 9 regions, 1 week per season; not HPC, no held-out year |
| A2 | PARTIAL: injected wind error incl. MAE 0 (Fig. 11); forecaster scored separately, no oracle arm | NONE | NONE | NONE | NONE: Alibaba 2018 aggregate load, 3 Chinese DCs, 96 h |
| A3 | SUBSTANTIAL for the concept: trained chronological forecaster vs MILP Oracle on realised data, gap by horizon (md:L841-845, L1195-1210); but wind power, unit tasks, 3 DCs, carbon from a fixed factor | NONE: unit tasks, no runtime (md:L238-248) | NONE: gap vs Oracle only by horizon; a bound, not a split (md:L694-706) | NONE | NONE |
| A4 | NONE: live MER forecasts, no scoring, no oracle (md:L870-880) | NONE: duration given | NONE | NONE | NONE: n = 3 simulated profiles |
| A5 | NONE: offline, no forecast | NONE | NONE | NONE | NONE: Alibaba trace, static emission factors |
| Max | SUBSTANTIAL (A3, concept only) | NONE | NONE | NONE | PARTIAL (A1) |

Outside the five (not re-audited here): `research\NOVELTY_SCAN.md` s.(b) and `research\A04_TRACES_AND_OVERLAP.md` record LACS (synthetic job-length error), COAST (CEA-Curie HPC trace, known runtimes, actual carbon) and LiteCast (real forecast on the KIT-FH2 log, ideal job lengths); the final related-work text must cover them, since they, not the five SUSCOM papers, bound C2 and C5. Exemplars: Wiesner and Sukprasert have oracle or "ideal" versus error scenarios (C1 PARTIAL to SUBSTANTIAL with synthetic error), no walltime in the extracted cells.

Adversarial points on what a referee will say
1. "Forecast gap to oracle is known": true. A3 reports it (1.03 % to 21.88 % by horizon), Wiesner and Sukprasert report error scenarios. C1 is a replication at scale with a real past-only forecaster, not a novelty. Its value is the realised-saving number on 42 grids with real jobs.
2. "Real traces over many grids": A1 has real traces and 4 of Paper A's US grids; it differs by synthetic arrivals, one week, spatial focus, noise forecast, no oracle and no walltime.
3. Statistics: A4 reports a 95 % CI over n = 3 profiles and calls it significant; Paper A must say its inference uses block bootstrap over 7-day blocks with Holm control (PREREG s.6) and that the unit is the fixed BA set, not a sample.
4. Where no paper reads the user's requested walltime, "none of the five" is a statement about these five only; do not extend it to the field without the LACS, COAST and LiteCast check.

## 3. Contribution wording Paper A can defend
1. "We measure how much of the perfect-information saving a deployable scheduler realises on real HPC batch jobs, using a past-only forecaster on 42 US grids and a pre-registered held-out year with block-bootstrap intervals." (C1 as a measurement at scale, C5.)
2. "We quantify the saving lost when the scheduler plans with the user-requested walltime instead of the actual runtime, and the saving a history-based runtime prediction recovers." (C2, C4: no one of the five tests either; A1 states runtimes are assumed known.)
3. "We split the gap between perfect information and the deployable scheduler into a forecast part and a runtime part with a 2x2 design and a Shapley allocation of the interaction." (C3: none of the five has a second information factor; A3's gap analysis is by horizon only.)
4. "We report the result against non-forecast baselines (run-now, night rule) and several forecasters under every runtime estimate, with negative findings stated." (PREREG s.7.5, s.8.)

Wording to avoid
- "first to compare forecast-based with perfect-information carbon-aware scheduling" or "first to show forecast error erodes saving" (A3, Wiesner, Sukprasert).
- "first study on real traces and many grids" (A1, LiteCast).
- "no prior work treats runtime uncertainty" without LACS (synthetic) named (NOVELTY_SCAN s.b).
- Any claim about water, land use, spatial shifting or wind (A1, A2, A3, A5 own that ground).
- "significant" for H1-H3 unless it is the Holm-adjusted bootstrap result; do not equate the 42-BA set with a sample of grids (PREREG s.5).
- A numeric comparison to the headline figures of A1 to A5 (20 to 85 %, 70 %, 75.7 %): different objectives, signals and baselines.

## 4. Comparison-table draft (cells only from what was read)

| Paper | Decision | Workload | Carbon or RES signal | Forecast | Oracle | Runtime uncertainty | Evaluation scale | Statistics | Code |
|---|---|---|---|---|---|---|---|---|---|
| A1 Attenni 2026 | where and when | Azure Functions 2019 and Spark traces, arrivals synthetic, delay tolerance 4-48 h | average intensity from grid mix; ERCOT, MISO, PJM, CAISO and EU grids | true mix plus synthetic noise, MAE 0.05-0.2 | none | assumed known | 4 or 5 regions, one week per season | 6 seeds, mean and SD | yes (GitHub) |
| A2 Zhai 2025 | DC and slot | Alibaba 2018 aggregate load | wind power, 3 Chinese sites | EMD-VMD-LSTM, rolling CV | none; error sweep incl. MAE 0 | none | 3 DCs, 96 h | CV mean | no |
| A3 Zhai 2026 | DC and slot, MILP plus RL | unit tasks from Google and Alibaba traces, delay up to 6 slots | wind power; fixed grid factor | decomposition-LSTM, H = 6, 12, 24 | MILP with realised data | none | 3 DCs, 3 horizons | mean and SD over 5 seeds | no |
| A4 Liow 2026 | region and start | 3 simulated profiles (1, 3, 6 h), 12 h latency | ElectricityMap MER, 4 AWS regions | fetched, not scored | none | duration given | n = 3 | CI over 3 profiles | on request |
| A5 Chen 2024 | DC and slot, offline | Alibaba 2018 offline load, 7 days | static regional factors, wind, solar | none | none | none | 4 seasons x 7 days, 1-4 DCs | none | no |
| Wiesner 2021 | start within window | nightly and ML-project jobs, delay assumed | 4 regions, 2020 | 5 % injected error | optimal | not extracted | 4 regions, 1 year | 10 repeats, no intervals | yes |
| Sukprasert 2024 | time and place | synthetic classes by length, deadline, interruptibility | 123 regions, 2020-2022 | prediction-error scenario | ideal bounds | not extracted | 123 regions, 8,760 starts | averages and intervals | yes |
| Radovanovic 2023 | cluster load shaping | Google fleet | day-ahead carbon forecast | production | no | not extracted | measured in deployment | 95 % bands | no |
| Paper A | start within slack | PM100, F-DATA, KIT FH2 real jobs, non-interruptible | hourly intensity, 42 US BAs | past-only LightGBM, leads 1-96 | perfect information arm | requested walltime and history prediction | 42 BAs, held-out year | block bootstrap, Holm | to release |

## 5. Related-work positioning (2-4 sentences each, factual, for citation)
- A1: Attenni et al. [A1] simulate spatial, temporal and spatio-temporal shifting of cloud workloads over carbon, water and land use, using Azure Functions and Spark traces with synthetic arrival patterns and a noise-perturbed grid mix as the forecast. Temporal shifting alone reduced the footprint by 6 % to 12 % at delay tolerances up to 48 h in their AWS scenario. They state that job runtimes are assumed known to the scheduler and that a trained operational forecaster remains future work, which are the two inputs the present study measures.
- A2: Zhai et al. [A2] schedule delay-tolerant aggregate workload over three wind-powered data centres, forecasting workload and wind power with decomposition-LSTM models and correcting errors in a second stage. They vary injected wind-forecast error and report wind utilisation and avoided emissions against greedy and round-robin baselines. The workload is aggregate load without per-job runtimes, and the signal is wind generation rather than grid carbon intensity.
- A3: Zhai et al. [A3] compare a forecast-driven MILP baseline with RL residual correction against an Oracle that uses realised wind and workload, and report the gap by forecast horizon (wind-utilisation gap 1.03 % to 11.33 %). Workloads are unit tasks with identical energy, so no job runtime enters the problem. The Oracle gap is attributed to forecast error alone.
- A4: Liow et al. [A4] present an architecture that selects a region and start time from ElectricityMap marginal-emissions forecasts for emulated tasks of 1, 3 and 6 h under a 12 h latency bound. The 75.7 % reduction is a single-case comparison against an immediate local start, and the confidence interval is over three task profiles. Forecast error is named as a limitation and left for future work.
- A5: Chen et al. [A5] schedule offline computing load of the Alibaba 2018 trace over one to four Chinese data centres with renewable supply and regional emission factors, reporting carbon reductions above 70 % in the four-site case against a grid-supplied data centre. The scheduling is offline with known load and supply, without forecasts or runtime estimates.

## 6. What Paper A should adopt or answer in Discussion
Adopt
1. A3: report the oracle gap as a function of horizon. Paper A has lead 1-96 forecasts; add the gap or retained share by slack (already in PREREG s.7.2) and, if cheap, by planning-window length, to connect with A3's 1.03 % to 11.33 % pattern.
2. A3 and Wiesner: a "perfect forecast" arm with a fixed runtime estimate already exists as oracle|req (2x2 cell); state in the text that this is the walltime-only cost, parallel to A3's forecast-only gap.
3. A2 Fig. 11: an injected-error sweep (MAE 0 to 0.12) as a secondary check that the LightGBM result is not specific to its error level. This is a candidate secondary analysis only if added to the deviations table; it is not in PREREG s.7 and cannot be confirmatory.
4. A1: a simple-policy ladder around the planner. Paper A already has run-now and night rule (PREREG s.4); keep them in the table beside the deployable arm.
5. A1 Discussion statement that runtimes could be "estimated from previous runs": cite as the position Paper A tests (history predictor, PREREG s.4 pred).

Answer in Discussion
1. A1 and A3 report their numbers against different baselines; the paper must say why 12 h slack on batch HPC jobs gives smaller savings than 70 % to 85 % figures in spatial or wind-driven studies (spatial freedom and wind supply versus a fixed grid).
2. A4 style single-case headline numbers: state that Paper A's saving is pooled over 42 BAs and jobs with block-bootstrap intervals, not a single case.
3. The zero-error finding in A2 (more error-free is not always better for a two-stage method): Paper A's planner is one-stage, so no analogue; state it so a reader does not expect it.
4. Data and code: A2, A3, A4 and A5 do not release code; A1 does. Paper A releasing code, derived data and the frozen PREREG md5 is a differentiator to mention once.
5. Marginal versus average intensity: A4 uses marginal emissions rates, A1 uses average. Paper A's accounting convention must be stated in the methods and flagged as a limitation of the conclusion.

## 7. Checks and gaps
- Not read in full: A1 sections 2.1-2.2.2 and Figs. 3-12 numerics beyond what is cited; A2 sections 3.2-3.3, 4.2-4.4 (forecasting and optimisation formulae); A3 sections 4.2-4.4 (RL design, proofs); A4 sections 2, 3.1; A5 section 3 (system model equations) and Table 3 values. None of these affect the verdicts because the extraction fields (workload, signal, forecast, oracle, runtime, statistics, availability) were read in the sections that define them.
- Line numbers refer to the md text renders and will differ in the PDFs.
- The A3 verdict C1 = SUBSTANTIAL is a deliberate adversarial reading; the defensible reading is PARTIAL because the signal (wind), workload (unit tasks) and objective (wind utilisation plus a fixed-factor carbon) differ.
