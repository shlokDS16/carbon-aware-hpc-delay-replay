VERDICT: A15 done; 60 verified references recommended; 10 SUSCOM

# A15: Related work and references for Paper A

Sources: the six PDFs' text in `research\sources\suscom_pdfs\md\` (file stem in brackets), Crossref API (queried 2026-11-12). A13's five papers (101498, 101216, 101470, 101407, 100950) are not analysed here; they are only cited.

## 1. Paper-by-paper notes (what Paper A can say)

**101429, Cam and Polat, "Carbon-conscious energy management of PV-BESS data centers" (SUSCOM 51, 2026) [S2210537926001393]**
- Builds an energy-management model for a PV plus battery data centre with three flexibility classes: short deferrable (Mode A), long continuous (Mode B), long interruptible (Mode C) (abstract; Sect. 3).
- Mode B is the closest model to Paper A: a non-interruptible block is shifted as a single unit, keeping its duration and power profile (Sect. 3.2); Mode A uses a 3 h deferral window (Sect. 3.1).
- Reported: daily cost 658 to 492 USD, CUE 0.455 to 0.349 kgCO2/kWh_IT, avoided emissions 2574 to 3325 kgCO2 under Turkiye grid parameters (abstract). Inputs are a stylised 24 h IT load profile with assumed parameters (Fig. 5; renewable share assumed 0.44, Sect. 5), not job traces.
- Placement: Related work, subsection "Shifting rigid (non-interruptible) workloads". Contrast: stylised load, known duration, no carbon forecast, no real trace; Paper A uses real traces and a past-only forecast.

**100592, Sharma and Rao, "Scheduling computing loads for improved utilization of solar energy" (SUSCOM 32, 2021) [S2210537921000810]**
- A "ren-aware" scheduler places jobs in the hours of predicted green (solar) energy; jobs carry a start time and a deadline or wait-time bound (Sect. 2). The prediction module uses hourly irradiance and per-minute CPU load (Sect. 2.1).
- Reported: +51 percent green-energy use against a randomised scheduler; -25 percent total energy by sleeping idle data centres; 4.5 times more idle energy saved (abstract).
- The reference list names a Kaggle server-cluster CPU-load set and NREL MIDC irradiance data ([24], [35]) and cites Feitelson et al. on parallel job scheduling ([13]).
- Placement: Related work, "Renewable-aware batch scheduling" (solar signal, cloud load; not HPC walltime, not grid carbon intensity).

**101398, Al-Shammaa and Al-Hadrawi, "Carbon-aware federated orchestration in edge-cloud systems" (SUSCOM 51, 2026) [S2210537926001083]**
- Simulation of 3969 workloads over 7 days on 3 cloud data centres and 9 edge nodes; reports -10.2 percent carbon, -15.7 percent cost, 60 percent relative fewer SLA violations, +14.0 percent carbon efficiency (abstract).
- Algorithm 1 scores each node and each start time inside the deadline window using mean carbon over [start, start+duration]; the workload tuple carries `duration` (Sect. 4, Alg. 1; text near lines 599 and 1244-1254). Duration is therefore an input known at decision time (our reading; the paper does not discuss runtime error).
- Uses average carbon intensity and says so: marginal signals are described as more accurate for demand response but need dispatch data; cites Sukprasert et al. (section "Marginal vs. Average carbon intensity", about line 752). The prediction layer can accept forecasts, but the evaluation uses real-time pricing for simplicity (about line 720). Carbon values are quoted in a 200 to 450 gCO2/kWh range (about line 1625).
- Placement: Related work "Start-time search inside a deadline window", and Methods/Discussion for the average-intensity choice. Contrast: oracle duration, no forecast evaluated, synthetic workload.

**101106, Da Costa, "Hardware and application aware performance, power and energy models for modern HPC servers with DVFS" (SUSCOM 46, 2025) [S2210537925000265]**
- Models performance, power and energy of applications under DVFS; validated on 18 clusters and 9 benchmarks (abstract). Uses a few hardware counters and RAPL.
- Reports that a per-server model reduces power error and that a fluid model cuts duration MAPE from above 14 percent to about 2 percent (Sect. 5, about lines 594-625); energy prediction accuracy about 94 percent (about line 168).
- Placement: Related work "HPC energy and power modelling", or Data/Methods when stating that per-job energy is taken from measured power (PM100) rather than modelled. Not about carbon or scheduling; do not overstate.

**101333, Aguirre-Usandizaga et al., forecasting perception layer for LLM serving on HPC clusters (SUSCOM 50, 2026) [S2210537926000430]**
- Four months of telemetry from four NVIDIA H100 nodes (KATEA HPC environment); compares RNN, SNN, Transformer and state-space forecasters of GPU load and energy at 30 s and 1 min windows (Sect. 5.1; abstract). Says HPC energy management has centred on batch scheduling and that LLM serving is the gap (Introduction).
- Placement: optional, Related work "Forecasting inside HPC energy management" (load forecasting, not carbon-intensity forecasting). Low priority.

**100989, Lin et al., "A systematic review of green-aware management techniques for sustainable data center" (SUSCOM 42, 2024) [S2210537924000349]**
- Reviews five areas: workload management, virtual resource management, energy management, thermal management, waste-heat recovery; also collects real-world datasets (workload traces, renewable data, electricity-price traces) (abstract; Sect. 4.1 lists the Alibaba cluster trace and the Parallel Workloads Archive, about lines 1376-1392). Its tables list batch and delay-tolerant scheduling works (Sect. 3.1).
- Cited by 101216 and 101407 (reference lists).
- Placement: Introduction or Related work (broad review positioning; the claim that no prior review treats walltime error for HPC delay scheduling must be checked against NOVELTY_SCAN.md before use). Data: pointer to the Parallel Workloads Archive.

## 2. Task 4 flag: runtime estimate inaccuracy

- None of the 16 papers in `md\` reports user runtime or walltime estimates being inaccurate. A grep for walltime, wall-time, user estimate, requested time, runtime prediction and overestimate found no relevant hit (only Q-value overestimation in 100992 and a Q-value remark in 101106 line ~634, both unrelated). Paper A's H2 literature must come from outside the 16 papers.
- Verified in Crossref and recommended for H2 (existence and metadata checked; the inaccuracy figures were not read by this agent and must not be quoted until the paper is read): Tsafrir, Etsion, Feitelson 2007; Mu'alem and Feitelson 2001; Gaussier et al. 2015; Fan and Lan 2017 (underestimation trade-off); Klusacek and Chlumsky 2024 (HPC trace with refined runtime estimates).
- Peer contrast: 101398 (Alg. 1) and 101429 (Mode B) treat duration as known, which is the oracle-runtime assumption Paper A tests.

## 3. Reference harvest summary

- 16 reference lists searched with keyword sweeps (carbon, emission, shifting, runtime, walltime, HPC, marginal, intensity, trace). 100949 (Abu-Hashem et al., task scheduling) has no isolable reference list (table-mangled), so its full text was searched; it holds nothing on the topics. The 101470 reference section was sliced from line 1438 of a garbled two-column file; 100989's list is also whitespace-mangled.
- Most cited carbon-aware works across the 16: Wiesner et al. 2021 (3 papers), Radovanovic et al. 2023 (3), Asadov et al. 2025 (3), CASPER (2), Lin and Chien (2), Greening geographical load balancing (2). Counts are in `cited_by_n_of_16` (pattern match on reference lists; may undercount where text is mangled).
- Crossref check: each recommended item was fetched by DOI or title query with title similarity at or above 0.85, or confirmed by hand where Crossref stores a short title (Wiesner "Let's wait awhile"; CarbonCast). `retraction_checked` = Crossref `filter=updates:<DOI>` queried for each DOI. Two items have notices, both corrections rather than retractions: SciPy 1.0 (Author Correction, 10.1038/s41592-020-0772-5) and Freitag et al. 2021 (notice 10.1016/j.patter.2022.100576 with the same title; read it before citing). Retraction Watch was not queried separately.

## 4. Recommended references (60; target 50 to 60)

Mix: domain 25, SUSCOM 10, methods and statistics 13, data/rules/software 7, broader context 5. Full records in `A15_REFERENCES.csv`.

### Domain: carbon-aware scheduling, shifting, forecasting, average vs marginal

| key | citation | section | why / claim | n/16 |
|---|---|---|---|---|
| wiesner2021 | Wiesner, P. et al. (2021). Let's wait awhile (full title in the 16 papers: ... how temporal workload shifting can red. Proceedings of the 22nd International Middlew. doi:10.1145/3464298.3493399 | Introduction; Related work: temporal shifting | Temporal shifting of delay-tolerant jobs within a slack window cuts emissions; Paper A tests this for non-interruptible HPC jobs | 3 |
| radovanovic2023 | Radovanović, A et al. (2023). Carbon-Aware Computing for Datacenters. IEEE Transactions on Power Systems. doi:10.1109/tpwrs.2022.3173250 | Related work: temporal shifting | Operational carbon-aware load shaping exists at hyperscale but for flexible cloud load, not HPC batch jobs | 3 |
| sukprasert2024limits | Sukprasert, T et al. (2024). On the Limitations of Carbon-Aware Temporal and Spatial Workload Shifting in the Cloud. Proceedings of the Nineteenth European Confer. doi:10.1145/3627703.3650079 | Introduction; Discussion | Achievable savings are bounded by grid carbon-intensity variability and slack | 1 |
| sukprasert2024avgmarg | Sukprasert, T et al. (2024). On the Implications of Choosing Average versus Marginal Carbon Intensity Signals on Carbon. The 15th ACM International Conference on Futu. doi:10.1145/3632775.3661953 | Methods; Limitations | Paper A uses average (not marginal) intensity; savings are on the average-accounting basis | 1 |
| hanafy2024green | Hanafy, W et al. (2024). Going Green for Less Green: Optimizing the Cost of Reducing Cloud Carbon Emissions. Proceedings of the 29th ACM International Con. doi:10.1145/3620666.3651374 | Related work: cost of carbon-aware scheduling | Carbon savings carry a delay or cost price; Paper A reports slack-vs-saving curve | 1 |
| hanafy2023carbonscaler | Hanafy, W et al. (2023). CarbonScaler: Leveraging Cloud Workload Elasticity for Optimizing Carbon-Efficiency. Proceedings of the ACM on Measurement and Ana. doi:10.1145/3626788 | Related work: elastic and interruptible workloads | Elastic workloads exploit carbon variation by scaling; rigid HPC jobs can only be delayed | 1 |
| souza2023casper | Souza, A et al. (2023). CASPER: Carbon-Aware Scheduling and Provisioning for Distributed Web Services. Proceedings of the 14th International Green a. doi:10.1145/3634769.3634812 | Related work: spatial shifting | Service workloads differ from batch HPC; Paper A is single-site temporal | 2 |
| linchien2023 | Lin, L et al. (2023). Adapting Datacenter Capacity for Greener Datacenters and Grid. Proceedings of the 14th ACM International Con. doi:10.1145/3575813.3595197 | Related work: datacentre flexibility | Capacity modulation offers an alternative to job delay | 2 |
| lindberg2022 | Lindberg, J et al. (2022). Using geographic load shifting to reduce carbon emissions. Electric Power Systems Research. doi:10.1016/j.epsr.2022.108586 | Related work: geographic shifting | Spatial shifting benefits depend on grid mix; Paper A restricts to temporal shifting | 1 |
| lindberg2021 | Lindberg, J et al. (2021). A Guide to Reducing Carbon Emissions through Data Center Geographical Load Shifting. Proceedings of the Twelfth ACM International . doi:10.1145/3447555.3466582 | Related work: geographic shifting | Marginal vs average signal matters for load shifting | 1 |
| maji2022carboncast | Maji, D. et al. (2022). CarbonCast (full title: CarbonCast: multi-day forecasting of grid carbon intensity). Proceedings of the 9th ACM International Conf. doi:10.1145/3563357.3564079 | Methods: carbon forecast; Related work: forecasting | Forecast-based scheduling needs carbon-intensity forecasts; Paper A uses a past-only LightGBM forecast | 0 |
| lechowicz2025 | Lechowicz, A et al. (2025). Carbon- and Precedence-Aware Scheduling for Data Processing Clusters. Proceedings of the ACM SIGCOMM 2025 Conferenc. doi:10.1145/3718958.3750478 | Related work: carbon-aware batch scheduling | Batch-job carbon-aware schedulers exist for data clusters | 1 |
| hall2025 | Hall, S et al. (2025). Carbon-Aware Computing for Data Centers with Probabilistic Performance Guarantees. IEEE Transactions on Power Systems. doi:10.1109/tpwrs.2025.3630499 | Related work: uncertainty in carbon-aware control | Forecast error needs explicit treatment, as in Paper A's oracle-vs-forecast gap | 1 |
| asadov2025 | Asadov, N et al. (2025). Carbon-Aware Spatio-Temporal Workload Shifting in Edge–Cloud Environments: A Review and No. Sustainability. doi:10.3390/su17146433 | Related work: reviews | Review of spatio-temporal shifting | 3 |
| dodge2022 | Dodge, J et al. (2022). Measuring the Carbon Intensity of AI in Cloud Instances. 2022 ACM Conference on Fairness Accountabilit. doi:10.1145/3531146.3533234 | Introduction | Same job emits differently by hour and region | 0 |
| acun2023 | Acun, B et al. (2023). Carbon Explorer: A Holistic Framework for Designing Carbon Aware Datacenters. Proceedings of the 28th ACM International Con. doi:10.1145/3575693.3575754 | Related work: datacentre design | Scheduling is one lever among supply options | 0 |
| koebrich2025 | Koebrich, S et al. (2025). Towards objective evaluation of the accuracy of marginal emissions factors. Renewable and Sustainable Energy Reviews. doi:10.1016/j.rser.2025.115508 | Discussion: average vs marginal | Marginal factors are uncertain, supporting an average-intensity primary analysis | 1 |
| siler2012 | Siler-Evans, K et al. (2012). Marginal Emissions Factors for the U.S. Electricity System. Environmental Science & Technology. doi:10.1021/es300145v | Methods: accounting basis | Average vs marginal emissions differ in the US | 0 |
| hawkes2010 | Hawkes, A et al. (2010). Estimating marginal CO2 emissions rates for national electricity systems. Energy Policy. doi:10.1016/j.enpol.2010.05.053 | Discussion: average vs marginal | Marginal rate differs from average | 0 |
| callaway2018 | Callaway, D et al. (2018). Location, Location, Location: The Variable Value of Renewable Energy and Demand-Side Effic. Journal of the Association of Environmental a. doi:10.1086/694179 | Discussion: average vs marginal | Marginal emissions vary by region and hour | 0 |
| cucumber2022 | Wiesner, P. et al. (2022). Cucumber: Renewable-Aware Admission Control for Delay-Tolerant Cloud and Edge Workloads. Euro-Par 2022: Parallel Processing. doi:10.1007/978-3-031-12597-3_14 | Related work: delay-tolerant admission control | Delay-tolerant jobs can be held for low-carbon periods | 1 |
| tranberg2019 | Tranberg, B et al. (2019). Real-time carbon accounting method for the European electricity markets. Energy Strategy Reviews. doi:10.1016/j.esr.2019.100367 | Data: carbon accounting | Average intensity with import-export tracing | 0 |
| leerbeck2020 | Leerbeck, K et al. (2020). Short-term forecasting of CO2 emission intensity in power grids by machine learning. Applied Energy. doi:10.1016/j.apenergy.2020.115527 | Methods: carbon forecast | ML carbon-intensity forecasts reach useful accuracy | 0 |
| li2023sc | Li, B et al. (2023). Toward Sustainable HPC: Carbon Footprint Estimation and Environmental Implications of HPC . Proceedings of the International Conference f. doi:10.1145/3581784.3607035 | Introduction: HPC carbon | HPC carbon footprint is significant | 0 |
| lannelongue2021 | Lannelongue, L et al. (2021). Green Algorithms: Quantifying the Carbon Footprint of Computation. Advanced Science. doi:10.1002/advs.202100707 | Methods: energy-to-carbon | Carbon of a job = energy x intensity | 0 |

### SUSCOM peers (cite and position against)

| key | citation | section | why / claim | n/16 |
|---|---|---|---|---|
| suscom_100989 | Lin, W et al. (2024). A systematic review of green-aware management techniques for sustainable data center. Sustainable Computing: Informatics and System. doi:10.1016/j.suscom.2024.100989 | Related work: reviews | SUSCOM review | 2 |
| suscom_100950 | Chen, D et al. (2024). Spatio-temporal management of renewable energy consumption, carbon emissions, and cost in . Sustainable Computing: Informatics and System. doi:10.1016/j.suscom.2023.100950 | Related work: spatio-temporal management | SUSCOM peer | 2 |
| suscom_101216 | Zhai, X et al. (2025). F2S-WSS: A forecast-driven two-stage workload scheduling scheme for carbon-aware geo-distr. Sustainable Computing: Informatics and System. doi:10.1016/j.suscom.2025.101216 | Related work: forecast-driven scheduling | SUSCOM peer | 1 |
| suscom_101407 | Liow, K et al. (2026). CARA: Adaptive scheduling for carbon-efficient workload orchestration in distributed cloud. Sustainable Computing: Informatics and System. doi:10.1016/j.suscom.2026.101407 | Related work: carbon-aware orchestration | SUSCOM peer | 0 |
| suscom_101398 | Al-Shammaa, A et al. (2026). Carbon-aware federated orchestration in edge-cloud systems: A multi-objective optimization. Sustainable Computing: Informatics and System. doi:10.1016/j.suscom.2026.101398 | Related work; Discussion: average intensity | SUSCOM peer | 0 |
| suscom_101498 | Attenni, G et al. (2026). Spatio-temporal shifting to reduce carbon, water, and land use footprints of cloud workloa. Sustainable Computing: Informatics and System. doi:10.1016/j.suscom.2026.101498 | Related work: shifting | SUSCOM peer | 0 |
| suscom_101470 | Zhai, X et al. (2026). ReBase: Prediction-driven scheduling with baseline-guided online correction for renewable-. Sustainable Computing: Informatics and System. doi:10.1016/j.suscom.2026.101470 | Related work: prediction-driven | SUSCOM peer | 0 |
| suscom_101429 | Çam, N et al. (2026). Carbon-conscious energy management of PV–BESS data centers: Integrated workload flexibilit. Sustainable Computing: Informatics and System. doi:10.1016/j.suscom.2026.101429 | Related work: non-interruptible block shifting | SUSCOM peer | 0 |
| suscom_101106 | Da Costa, G et al. (2025). Hardware and application aware performance, power and energy models for modern HPC servers. Sustainable Computing: Informatics and System. doi:10.1016/j.suscom.2025.101106 | Related work: HPC energy | SUSCOM peer | 0 |
| suscom_100592 | Sharma, D et al. (2021). Scheduling computing loads for improved utilization of solar energy. Sustainable Computing: Informatics and System. doi:10.1016/j.suscom.2021.100592 | Related work: renewable-aware scheduling | SUSCOM peer | 0 |

### Methods and statistics

| key | citation | section | why / claim | n/16 |
|---|---|---|---|---|
| tsafrir2007 | Tsafrir, D et al. (2007). Backfilling Using System-Generated Predictions Rather than User Runtime Estimates. IEEE Transactions on Parallel and Distributed. doi:10.1109/tpds.2007.70606 | Methods: runtime predictor; Discussion | User walltime estimates are poor; history-based predictors improve scheduling | 0 |
| mualem2001 | Mu'alem, A et al. (2001). Utilization, predictability, workloads, and user runtime estimates in scheduling the IBM S. IEEE Transactions on Parallel and Distributed. doi:10.1109/71.932708 | Related work: runtime estimates | User estimates are inaccurate yet scheduling still works | 0 |
| gaussier2015 | Gaussier, E et al. (2015). Improving backfilling by using machine learning to predict running times. Proceedings of the International Conference f. doi:10.1145/2807591.2807646 | Related work: runtime prediction | History-based ML predictors beat user estimates | 0 |
| fan2017 | Fan, Y et al. (2017). Trade-Off Between Prediction Accuracy and Underestimation Rate in Job Runtime Estimates. 2017 IEEE International Conference on Cluster. doi:10.1109/cluster.2017.11 | Methods: runtime predictor | Underestimates kill jobs; predictor must be conservative | 0 |
| klusacek2024 | Klusáček, D. et al. (2024). Real-Life HPC Workload Trace Featuring Refined Job Runtime Estimates. Job Scheduling Strategies for Parallel Proces. doi:10.1007/978-3-031-74430-3_1 | Methods: runtime estimates; Data | Refined runtime estimates are available for a real HPC trace; user estimates alone are not the ground truth | 0 |
| politis1994 | Politis, D et al. (1994). The Stationary Bootstrap. Journal of the American Statistical Associati. doi:10.1080/01621459.1994.10476870 | Methods: statistics | Block bootstrap for autocorrelated daily savings | 0 |
| efron1979 | Efron, B et al. (1979). Bootstrap Methods: Another Look at the Jackknife. The Annals of Statistics. doi:10.1214/aos/1176344552 | Methods: statistics | Bootstrap confidence intervals | 0 |
| lundberg2020 | Lundberg, S et al. (2020). From local explanations to global understanding with explainable AI for trees. Nature Machine Intelligence. doi:10.1038/s42256-019-0138-9 | Methods: Shapley decomposition | Shapley attribution of forecast features | 0 |
| owen2014 | Owen, A et al. (2014). Sobol' Indices and Shapley Value. SIAM/ASA Journal on Uncertainty Quantificatio. doi:10.1137/130936233 | Methods: Shapley decomposition | Shapley decomposition of savings gap | 0 |
| nosek2018 | Nosek, B et al. (2018). The preregistration revolution. Proceedings of the National Academy of Scienc. doi:10.1073/pnas.1708274114 | Methods: preregistration | Pre-registered held-out year | 0 |
| cerqueira2020 | Cerqueira, V et al. (2020). Evaluating time series forecasting models: an empirical study on performance estimation me. Machine Learning. doi:10.1007/s10994-020-05910-7 | Methods: held-out evaluation | Held-out year beats random CV for time series | 0 |
| hyndman2006 | Hyndman, R et al. (2006). Another look at measures of forecast accuracy. International Journal of Forecasting. doi:10.1016/j.ijforecast.2006.03.001 | Methods: forecast metrics | MASE-type metrics for carbon forecast | 0 |
| feitelson2004 | Feitelson, D et al. (2005). Parallel Job Scheduling — A Status Report. Lecture Notes in Computer Science. doi:10.1007/11407522_1 | Related work: HPC scheduling | Backfill and runtime-estimate background | 1 |

### Data, rules and software

| key | citation | section | why / claim | n/16 |
|---|---|---|---|---|
| miller2020 | Miller, G et al. (2023). Evaluating the hourly emissions intensity of the US electricity system. Environmental Research Letters. doi:10.1088/1748-9326/acc119 | Data: EIA-930 emissions | Hourly average carbon intensity can be built from EIA hourly generation by fuel | 0 |
| feitelson2014pwa | Feitelson, D et al. (2014). Experience with using the Parallel Workloads Archive. Journal of Parallel and Distributed Computing. doi:10.1016/j.jpdc.2014.06.013 | Data: KIT FH2 and PWA | Trace-use cautions apply to KIT FH2 | 0 |
| antici2023pm100 | Antici, F et al. (2023). PM100: A Job Power Consumption Dataset of a Large-scale Production HPC System. Proceedings of the SC '23 Workshops of the In. doi:10.1145/3624062.3624263 | Data: PM100 | PM100 provides per-job power for Marconi100 | 0 |
| antici2024fdata | Antici, F et al. (2025). F-DATA: A Fugaku Workload Dataset for Job-centric Predictive Modelling in HPC Systems. Scientific Data. doi:10.1038/s41597-025-05633-1 | Data: F-DATA | F-DATA provides Fugaku job records | 0 |
| schlomer2014 |  et al. (2015). Technology-specific Cost and Performance Parameters. Climate Change 2014: Mitigation of Climate Ch. doi:10.1017/cbo9781107415416.025 | Methods: emission factors | Fuel emission factors | 1 |
| harris2020 | Harris, C et al. (2020). Array programming with NumPy. Nature. doi:10.1038/s41586-020-2649-2 | Software | Software | 0 |
| virtanen2020 | Virtanen, P et al. (2020). SciPy 1.0: fundamental algorithms for scientific computing in Python. Nature Methods. doi:10.1038/s41592-019-0686-2 | Software | Software | 0 |

### Broader context

| key | citation | section | why / claim | n/16 |
|---|---|---|---|---|
| masanet2020 | Masanet, E et al. (2020). Recalibrating global data center energy-use estimates. Science. doi:10.1126/science.aba3758 | Introduction | Data-centre energy growth was far slower than workload growth to 2018 | 1 |
| freitag2021 | Freitag, C et al. (2021). The real climate and transformative impact of ICT: A critique of estimates, trends, and re. Patterns. doi:10.1016/j.patter.2021.100340 | Introduction | ICT emissions estimates are uncertain | 1 |
| gupta2021 | Gupta, U et al. (2021). Chasing Carbon: The Elusive Environmental Footprint of Computing. 2021 IEEE International Symposium on High-Per. doi:10.1109/hpca51647.2021.00076 | Introduction | Operational carbon is only part of computing footprint | 0 |
| belkhir2018 | Belkhir, L et al. (2018). Assessing ICT global emissions footprint: Trends to 2040 & recommendations. Journal of Cleaner Production. doi:10.1016/j.jclepro.2017.12.239 | Introduction | ICT share of emissions projected to grow | 1 |
| malmodin2018 | Malmodin, J et al. (2018). The Energy and Carbon Footprint of the Global ICT and E&M Sectors 2010–2015. Sustainability. doi:10.3390/su10093027 | Introduction | ICT carbon footprint estimate | 1 |

## 5. Reserve (verified in Crossref, not counted in the recommended set)

gao2012 (doi:10.1145/2342356.2342398); liu2015 (doi:10.1109/tnet.2014.2308295); zheng2020 (doi:10.1016/j.joule.2020.08.001); maji2023multicloud (doi:10.1145/3604930.3605711); kunsch1989 (doi:10.1214/aos/1176347265); dm1995 (doi:10.1080/07350015.1995.10524599); friedman2001 (doi:10.1214/aos/1013203451); benjamini1995 (doi:10.1111/j.2517-6161.1995.tb02031.x); smith1999 (doi:10.1007/3-540-47954-6_11); matsunaga2010 (doi:10.1109/ccgrid.2010.98); lublin2003 (doi:10.1016/s0743-7315(03)00108-4); patterson2022 (doi:10.1109/mc.2022.3148714); jones2018 (doi:10.1038/d41586-018-06610-y); mytton2020 (doi:10.1038/s41558-020-0837-6); dacosta2017 (doi:10.1016/j.suscom.2017.05.003); suscom_101333 (doi:10.1016/j.suscom.2026.101333); suscom_100649 (doi:10.1016/j.suscom.2021.100649).

Use the reserve if a section needs another anchor (Liu 2015 and Gao 2012 for geographic-balancing history, Lublin and Feitelson 2003 for rigid-job workloads, Kunsch 1989 for the moving-block bootstrap, Benjamini-Hochberg for multiple testing, 101333 and LECC as extra SUSCOM items).

## 6. Unverified or not recommended (kept out of the list)

- LightGBM (Ke et al., NeurIPS 2017): not found in Crossref; cite from the NeurIPS proceedings record and check the entry before use.
- Holm 1979 (Scand. J. Stat.): the Crossref title query returned a different paper (Biometrics 1987), so it was not accepted.
- CarbonFlex (Hanafy et al., arXiv 2505.18357): printed in 101407's reference list [6]; arXiv preprint, not checked in Crossref.
- "COAST: congestion-aware start-time recommendations for carbon-aware HPC jobs" (SSRN 10.2139/ssrn.7345605, 2026): present in Crossref but a preprint; not read; check NOVELTY_SCAN.md for overlap before citing.
- No paper exists to cite for EIA-930, Electricity Maps, WattTime or GHG Protocol Scope 2 (controller adds these as data/standard sources). IEA "Energy and AI" and the 2024 LBNL data-centre report (printed in 101407) were not checked in Crossref.
- KIT FH2: no dedicated paper found; cite the Parallel Workloads Archive and Feitelson et al. 2014 (both recommended above).
- Note: Miller et al. (EIA hourly emissions intensity) is ERL 2023 in Crossref, not 2020 as often assumed.
