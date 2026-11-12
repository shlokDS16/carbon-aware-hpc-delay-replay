VERDICT: A03 done; top candidate C7 restricted ("C7-lite", forecast x runtime-estimate x accounting x slack; fallback C2+C6) (novelty 4/5 as an integration, 3/5 for each part); data check: ok for EIA-930, Parallel Workloads Archive (needs browser User-Agent), Azure LLM traces, Alibaba GPU 2020, Google 2019 (BigQuery only, login); BLOCKED: Electricity Maps (login, academic approval, no redistribution)

# Novelty scan for Paper A candidates C1-C7 (expert E4, task A03, 2026-11-11)

Method: OpenAlex search (2019+) for each candidate, abstracts read through the OpenAlex API, Exa for HPC and runtime-error papers, HTTP HEAD checks for data. Only abstracts were read, not full texts, so statements about what a paper did NOT do are "not seen in the abstract", and are marked as such. Scratch: `agents\scratch_A03\` (oa.sh, abs.py, eia_files.txt).

## 0. Position, alternatives, confidence (hypotheses, not facts)

Position: the single-signal studies are mostly taken. The defensible gap is the joint, honest-evaluation gap: savings reported under oracle forecasts, known durations and one accounting convention, versus savings under past-only forecasts, real user runtime estimates and the accounting that a grid regulator would accept. I recommend C7 restricted to what is computable from public data in two days. I hold this at about 60 % confidence.

Strongest alternative rejected: C2 alone (most feasible, free EIA data, SUSCOM fit). Rejected as the lead because LiteCast (arXiv 2511.06187), the EuroSys 2024 "Limitations" study and HotCarbon 2024 already inject or compute forecast error, so a hostile referee writes "incremental". What would change my mind: if a full read of LiteCast shows it already uses held-out years across dozens of US balancing authorities with real past-only forecasters, C2 drops to 2/5 and C7 must rest on C6 and C3 content.

Second alternative rejected: C1 (average vs marginal). Directly pre-empted by e-Energy 2024 (65 regions). Marginal factors also cannot be observed, which a referee will use (SIGMETRICS PER 2025 statement paper). Kept only as a sensitivity arm inside C7.

What a hostile SUSCOM referee says about C7: "a simulation of an obvious claim (forecast and duration errors reduce savings) with a synthetic link between 1990s to 2011 HPC logs and 2019-2025 grid data". Mitigation: state the pairing as random alignment (COAST did the same), use the 2024-2026 job traces where available (Azure LLM 2023 is a short trace only; Alibaba 2020), give the error decomposition with intervals, and pre-register the held-out year.

## 1. Specific checks (a) to (e)

(a) Marginal vs average scoring of temporal shifting: DONE in part. Hanafy et al., e-Energy 2024, "On the Implications of Choosing Average versus Marginal Carbon Intensity Signals on Carbon-aware Optimizations", 65 regions, finds the signals have very low correlation and optimising one can raise the other's emissions (doi:10.1145/3632775.3661953). Also a 2026 ERIS study scores LLM training pause/migrate with WattTime marginal rates (MOER) in 43 US subregions for 2025 (doi:10.1088/2634-4505/aebbef), and Radovanovic et al. use grid-level signals (doi:10.1109/tpwrs.2022.3173250). Not seen: scoring with job traces plus real past-only forecasts. Marginal factors need WattTime (login/paid for full data) or own estimation.

(b) Effect of job runtime estimate error on carbon-aware savings: NOT found with real estimates. LACS (arXiv 2404.15211, SIGMETRICS-line work) models job-length error synthetically (symmetric bounded error) for scaling jobs and reports 1.2 % from perfect-length baseline. COAST (arXiv 2609.05443, GreenCom 2026) uses CEA-Curie HPC trace but assumes known runtimes, actual (not forecast) carbon, and lists forecast error and queueing as future work. No paper seen uses the requested-versus-actual runtime fields of the Parallel Workloads Archive for carbon. Novelty here is real but thin: referee says "a sensitivity analysis".

(c) Savings retained under real past-only forecasts across many regions: PARTLY. CarbonCast (doi:10.1145/3563357.3564079) is a forecaster (about 10 % error, 3-day horizon) not a savings study. EuroSys 2024 Limitations (doi:10.1145/3627703.3650079) covers 123 regions and includes prediction error as a question, using Electricity Maps data (login-gated). HotCarbon 2024 algorithm selection injects 0 to 20 % synthetic forecast error. LiteCast (doi:10.48550/arxiv.2511.06187) states accuracy gains do not give proportional savings gains. Not seen: a held-out final year, about 60 US balancing authorities, retention as a function of grid mix and slack with real past-only forecasters on public EIA data.

(d) Consumption-based vs production-based intensity in carbon-aware computing: PARTLY. Green Mirage (doi:10.1145/3632775.3639587) and Untangling (doi:10.1145/3632775.3662164) treat location-based vs market-based (PPA) accounting. ElectricityEmissions.jl (doi:10.1145/3679240.3734597) compares signals for load shifting and accounting; I did not verify whether it includes flow-traced consumption intensity. Flow tracing exists for Europe (Quantification of carbon intensity of electricity produced and used in Europe, doi:10.1016/j.apenergy.2021.117901) and for US data reconciliation (doi:10.1016/j.apenergy.2021.117761). Not seen: flow-traced US BA intensity used to score temporal or spatial shifting with job traces. Gap exists, but reviewers outside the grid field may see it as accounting detail.

(e) Integrated error budget C7: NOT found. No paper seen decomposes the oracle-to-realised gap into forecast, runtime and accounting terms. Risk: scope, and each term has a precedent.

## 2. Candidates

### C1 Average vs marginal. Novelty 2/5
Closest:
1. Hanafy et al., On the Implications of Choosing Average versus Marginal Carbon Intensity Signals..., e-Energy 2024, doi:10.1145/3632775.3661953. 65 regions, signal comparison.
2. Carbon-aware scheduling of LLM training across US power grid operators: a marginal emissions analysis, ERIS 2026, doi:10.1088/2634-4505/aebbef. WattTime MOER 2025, 43 subregions, CAISO/ERCOT/MISO/PJM.
3. Can Carbon-Aware Electric Load Shifting Reduce Emissions? Equilibrium analysis, e-Energy 2026, doi:10.1145/3744255.3798127. Theory plus IEEE RTS-GMLC, shows average signal limits.
4. Moving Beyond Marginal Carbon Intensity, SIGMETRICS PER 2025, doi:10.1145/3764944.3764969. Argues MCI unobservable.
5. Spatio-temporal load shifting for truly clean computing, Adv. Appl. Energy 2024, doi:10.1016/j.adapen.2024.100202.
6. Radovanovic et al., Carbon-Aware Computing for Datacenters, IEEE TPWRS 2022, doi:10.1109/tpwrs.2022.3173250 (Google; load shifting with average intensity).
Open: scoring on job traces with self-estimated MEF from public EIA-930. Objection ("already done by Hanafy et al."): strong. Data: EIA ok, but WattTime marginal data is login-gated, so own regression only, which a referee calls unverifiable.

### C2 Past-only forecasts, oracle retention. Novelty 3/5
Closest:
1. LiteCast, arXiv 2025, doi:10.48550/arxiv.2511.06187 (accuracy vs savings).
2. On the Limitations of Carbon-Aware Temporal and Spatial Workload Shifting in the Cloud, EuroSys 2024, doi:10.1145/3627703.3650079 (123 regions, 3 years, includes prediction error).
3. Let's Wait Awhile, Middleware 2021, doi:10.1145/3464298.3493399 (4 regions, forecast error variants).
4. CarbonCast, BuildSys 2022, doi:10.1145/3563357.3564079 and EnsembleCI, e-Energy 2025, doi:10.1145/3679240.3734630 (forecasters).
5. Signal-Aware Workload Shifting with Uncertainty-Quantified Predictors, e-Energy 2026, doi:10.1145/3744255.3798123 (online algorithm with UQ forecasts).
6. Data-driven Algorithm Selection for Carbon-Aware Scheduling, HotCarbon 2024 (https://hotcarbon.org/assets/2024/pdf/hotcarbon24-final23.pdf; synthetic 0 to 20 % error).
Open: about 60 US BAs, real past-only forecasters, held-out year, retention vs mix and slack, on public data. Objection: "LiteCast and EuroSys 2024 already show forecast error costs little". Data: EIA ok.

### C3 Consumption-based intensity. Novelty 3/5 (computing side), 2/5 (grid side)
Closest:
1. Green Mirage, e-Energy 2024, doi:10.1145/3632775.3639587 (location vs market).
2. Untangling carbon-free energy attribution, e-Energy 2024, doi:10.1145/3632775.3662164.
3. ElectricityEmissions.jl, e-Energy 2025, doi:10.1145/3679240.3734597 (signal comparison; flow-tracing content unverified).
4. Quantification of carbon intensity of electricity produced and used in Europe, Appl. Energy 2021, doi:10.1016/j.apenergy.2021.117901.
5. Physics-informed data reconciliation for real-time electricity and emissions tracking, Appl. Energy 2021, doi:10.1016/j.apenergy.2021.117761 (US data).
6. Carbon Emission Flow Tracing: Fast Algorithm and California Grid Study, arXiv 2025, doi:10.48550/arxiv.2507.18077.
Open: effect of imports on which hour or region a scheduler picks, with EIA-930 interchange. Objection: "accounting detail; flow tracing known". Feasibility: EIA-930 BALANCE and INTERCHANGE files present, but hourly matrix inversion and data-quality repair (negative, missing, reporting gaps) is work.

### C4 Idle GPU energy, Alibaba 2020. Novelty 2/5
Closest: The Energy Cost of Execution-Idle in GPU Clusters, arXiv 2026, doi:10.48550/arxiv.2604.04745 (10.7 % of energy, per-second telemetry, academic cluster; this pre-empts the idea with measured power); Characterization and prediction of deep learning workloads in large-scale GPU datacenters (SenseTime, SC 2021, doi:10.1145/3458817.3476223); Deep Learning Workload Scheduling in GPU Datacenters survey (CSUR 2023, doi:10.1145/3638757); Design and Operation of Shared ML Clusters on Campus (ASPLOS 2025, doi:10.1145/3669940.3707266); SmartCap (ICS 2026, doi:10.1145/3797905.3800526). Alibaba 2020 has utilisation but no power, so energy would be modelled from a laptop-GPU curve, a weak transfer. Objection: modelled power, 2020 data. Not recommended.

### C5 LLM serving energy on consumer GPU. Novelty 1-2/5
Closest: DynamoLLM (HPCA 2025, doi:10.1109/hpca61900.2025.00102), throttLL'eM (HPCA 2025, doi:10.1109/hpca61900.2025.00103), Characterization of Request and Token Energy Costs (IISWC 2026, doi:10.1109/iiswc71020.2026.00027), Towards Greener LLMs (arXiv 2403.20306), TAPAS (ASPLOS 2025, doi:10.1145/3676641.3716025), The Illusion of Power Capping in LLM Decode (arXiv 2605.11999). Saturated; owner's LLM routing work also adjacent. Objection: "another measurement study of known knobs on a laptop GPU". Not recommended.

### C6 Runtime uncertainty, real estimates. Novelty 3.5/5
Closest:
1. LACS, arXiv 2404.15211 (synthetic job-length error; within 1.2 % of perfect-length baseline).
2. COAST, arXiv 2609.05443 / GreenCom 2026 (CEA-Curie, known runtimes, actual carbon, 15.4 % saving; forecast error and queueing future work).
3. CarbonScaler, SIGMETRICS 2024, doi:10.1145/3626788 (assumes known job length).
4. Quantifying the Carbon Reduction of DAG Workloads, doi:10.1145/3802973.3804454.
5. Anticipatory Resource Allocation for ML Training (SoCC 2023, doi:10.1145/3620678.3624669; duration prediction error in schedulers, not carbon).
6. Machine Learning-Based Runtime Prediction and Energy Optimization for HPC Job Scheduling, NREL Eagle, Informatica 2026, doi:10.31449/inf.v50i15.15344 (runtime prediction, energy; not seen carbon-forecast coupling).
Open: using real requested vs actual runtimes, deadline violations, interaction with backfilling. Objection: "logs are 1990s to 2011, pairing with modern grids is artificial; COAST did the same". Data: PWA ok with UA.

### C7 Integrated error budget. Novelty 4/5 (integration), parts 2 to 3/5
Nothing seen that combines the four terms. Closest are C2 items 1, 2 and C6 items 1, 2, plus Radovanovic. Open: a factorial design with attribution (Shapley or ANOVA) of the oracle-to-realised gap, across many BAs and a held-out year, with intervals. Objection: breadth versus depth; "each part known"; synthetic job-grid pairing. Mitigation: restrict to temporal shifting, three accounting arms (production average, consumption average, MEF as sensitivity), two job sources, one held-out year, pre-registered.

## 3. Data availability (checked 2026-11-11 from this machine)

| Source | Result | Licence and notes |
|---|---|---|
| EIA-930 six-month CSV | Directory listing returns 403 to curl, but direct files return HTTP 200: BALANCE 2019_Jan_Jun (43.4 MB), 2019_Jul_Dec (44.1 MB), 2024_Jul_Dec (47.9 MB), 2025_Jan_Jun (47.6 MB), 2025_Jul_Dec (48.3 MB), 2026_Jan_Jun (47.1 MB); INTERCHANGE 2024_Jul_Dec (102.6 MB). Pattern: `https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_<year>_<Jan_Jun|Jul_Dec>.csv`. OK, no login | Licence text not re-read today; EIA data is normally public domain (verify and cite EIA) |
| Parallel Workloads Archive | Server returns an error page to default curl; with a browser User-Agent logs.html (76 KB) and CEA-Curie-2011-2.1-cln.swf.gz (3.6 MB) return 200. OK with UA | Free for research, ask to cite Feitelson et al. (exact licence text not read) |
| Alibaba clusterdata GPU 2020 | README 200; OSS files pai_*.tar.gz return 200 (pai_sensor_table 406 MB; instance table about 663 MB per README). OK, no login | No LICENSE file found on master (404) and GitHub API was rate-limited, so licence UNCONFIRMED; note. Newer traces exist (gpu-v2023, v2025, v2026 six-month ASI). |
| Azure LLM inference traces | AzureLLMInferenceTrace_conv.csv 200 (719 KB); code trace listed. OK | CC-BY 4.0 (read in the repo's md); cite Splitwise, ISCA 2024 |
| Google cluster trace 2019 | Repo 200; data only through BigQuery (about 2.4 TiB) which needs a Google Cloud account/login. BLOCKED for plain download; the 2011 trace is separate (not checked) | CC-BY 4.0 |
| Electricity Maps data portal | `www.electricitymaps.com/data-portal` redirects to `app.electricitymaps.com/datasets`, 403 to scripts. Help Center (Mar 2026): general datasets product sunset; CSVs only for approved academic users (verified academic email) and Scope 2 requests; non-commercial; no redistribution; attribution required. BLOCKED without login | ToS, non-commercial, no redistribution. Earlier ODbL claims in a 2022 repo are outdated. |

USER STEPS NEEDED (only if Electricity Maps data is wanted; recommended to avoid): sign up at https://portal.electricitymaps.com with a VIT email, activate the academic licence, then download hourly carbon intensity CSVs per zone. Without it we lose a second independent signal for validating the EIA-derived intensities; not essential because EIA-930 gives generation by fuel and interchange at public-domain terms.

## 4. Ranking by novelty x feasibility x SUSCOM fit (each 1-5)

| Rank | Cand | N | F | S | Product | Comment |
|---|---|---|---|---|---|---|
| 1 | C7-lite | 4 | 3.5 | 5 | 70 | Umbrella; modular, so a failed arm degrades to C2+C6 |
| 2 | C2 | 3 | 5 | 5 | 75 | Highest raw product but thinly novel (LiteCast, EuroSys 2024); best used as the backbone of C7 |
| 3 | C6 | 3.5 | 4 | 5 | 70 | Real runtime estimates are the only genuinely unexplored input |
| 4 | C3 | 3 | 3 | 4 | 36 | Interesting arm; flow tracing on EIA-930 is the hard cleaning job |
| 5 | C1 | 2 | 3 | 5 | 30 | Pre-empted by Hanafy 2024 |
| 6 | C4 | 2 | 3 | 4 | 24 | Execution-idle paper pre-empts; modelled power |
| 7 | C5 | 1.5 | 4 | 3 | 18 | Saturated |

Note on method: C2 scores above C7 on the raw product. I still recommend C7-lite because a SUSCOM referee (5 % acceptance) rewards a distinct, decision-relevant result over a feasible incremental one, and C2 is its backbone anyway, so the downside is bounded.

## 5. Recommendation (confidence about 60 %)

Build C7-lite: temporal shifting only, about 60 US balancing authorities from EIA-930 (2019 to 2025 train/validate, 2026 H1 or final full year held out, pre-registered), factors: (1) forecast (oracle, persistence, seasonal naive, gradient boosting past-only), (2) runtime knowledge (exact, user estimate from PWA, predicted), (3) accounting (production average, flow-traced consumption average; MEF regression as a clearly labelled sensitivity), (4) slack and interruptibility. Report savings retained versus oracle, deadline violations and a Shapley or ANOVA attribution of the gap. Report trivial baselines (run now, fixed night window). State the pairing of old job logs with grid years as random alignment and test its sensitivity; add the Azure LLM 2023 or Alibaba 2020 trace as a modern job source.

Evidence that would change this: (i) full-text read of LiteCast and EuroSys 2024 showing a many-BA real-forecast study (then reframe around C6 and C3); (ii) EIA interchange data too noisy for flow tracing (drop C3 arm); (iii) PWA log pairing judged too artificial in a pilot (then lean on Azure/Alibaba).

Not verified: full texts (only abstracts), licence wording for EIA and PWA, whether ElectricityEmissions.jl includes flow tracing, Google 2011 trace access.
