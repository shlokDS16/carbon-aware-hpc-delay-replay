VERDICT: A20 done; 5 of 5 full texts read (Tsafrir via author PDF; Mu'alem via ResearchGate full text, its Table 2 cells not extractable); licence unknown (no licence text, only an acknowledgement and citation request); EIA delay found; 2 user steps

# A20 literature and licence check for Paper A (2026-11-12)

Method: arXiv PDFs downloaded and converted with pdftotext. Tsafrir PDF from https://dants.github.io/papers/Pred07TPDS.pdf (author copy; preprint pagination, not the TPDS page numbers). Mu'alem text from the ResearchGate full-text page (journal pagination visible). DOIs checked: Crossref for LACS, Tsafrir, Mu'alem and Feitelson 2014; DataCite for the three arXiv DOIs (arXiv DOIs are not in Crossref). No Crossref retraction or update notice was found for the Crossref-registered items. Quotes are short and marked.

## 1. Papers

### 1.1 LiteCast
- Citation: Joseph, M.; Savadi, T.; Souza, A. "LiteCast: A Lightweight Forecaster for Carbon Optimizations", arXiv:2511.06187 v2, 24 Nov 2025 (v1 9 Nov 2025). DOI 10.48550/arxiv.2511.06187 (DataCite verified). The arXiv page shows no journal reference; treat as a preprint.
- What they do: a lightweight SARIMAX-type energy-mix forecaster (plus a heuristic extension) for carbon intensity. The scheduler delays jobs within a slack. Compared with persistence, CarbonCast and an oracle ("Actual").
- Data: 2023 hourly EIA and ENTSO-E energy mix, weather and demand data for 50 regions in the USA and Europe. Synthetic jobs with lengths and slacks; KIT FH2 replay from the Parallel Workloads Archive (Sect. 6.3: slack assigned "according to the waiting time recorded in the trace").
- Requested walltime or runtime prediction: neither. Job length is treated as known; requested time is not mentioned.
- Forecast versus oracle: yes, the core of the paper. Abstract: 97 % of the maximum attainable average savings; about 20 % higher savings than state-of-the-art forecasters. KIT replay: average saving 3.4 %, "approximately 2% lower than the oracle"; the heuristic beats CarbonCast in 93 % of the 50 regions. The authors note that the short-job mix of KIT limits the savings.
- Not past-only: uses third-party weather and demand forecasts as inputs. No preregistered held-out year.
- Numbers Paper A may cite: 3.4 % (KIT, 50 regions, 2023), about 2 points below the oracle; 97 % of oracle savings for synthetic loads.
- Row in A13 format:

| Paper | Decision | Workload | Carbon or RES signal | Forecast | Oracle | Runtime uncertainty | Evaluation scale | Statistics | Code |
|---|---|---|---|---|---|---|---|---|---|
| LiteCast, Joseph 2025 | start within slack (continuous and interruptible) | synthetic lengths and slacks 1-168 h; KIT FH2 replay, slack = recorded wait | hourly mix from EIA and ENTSO-E, 50 regions, 2023 | SARIMAX with weather and demand inputs; persistence; CarbonCast | yes (actual intensity) | none: lengths known | 50 regions, one year | averages; no intervals found | not checked |

- Verdict on C1-C5 (C1 realised saving of a past-only forecast versus oracle; C2 cost of requested walltime versus actual; C3 2x2 gap decomposition; C4 history-based runtime prediction; C5 real HPC traces, many grids, held-out year):
  - C1 SUBSTANTIAL. Abstract and Sect. 6.3. Paper A differs by a past-only forecaster without third-party weather input, 42 US BAs, a frozen held-out year and an energy-weighted outcome.
  - C2 NONE.
  - C3 NONE (one information factor only).
  - C4 NONE.
  - C5 PARTIAL. Real KIT trace and 50 regions, but one year, no held-out evaluation year, job lengths known.

### 1.2 COAST
- Citation: Feng, W.; Dasgupta, A.; Tekler, Z. D.; Ahuja, S.; Zheng, J.; Jiang, X. "COAST: Congestion-Aware Start-Time Recommendations for Carbon-Aware HPC Jobs", arXiv:2609.05443, submitted 29 Jul 2026. DOI 10.48550/arxiv.2609.05443 (DataCite verified). NOVELTY_SCAN says "GreenCom 2026"; I could not confirm a venue on the arXiv page or in the text, so cite it as an arXiv preprint.
- What they do: start-time recommendation for HPC jobs as a congestion game that trades carbon, waiting and peak load; rolling 48 h horizon, 30 min slots.
- Data: CEA-Curie 2011 log (Parallel Workloads Archive), 165,887 jobs in 224 day-long windows; UK Carbon Intensity API, 1 Jan 2025 to 1 Jan 2026; windows paired with a random start index ("not a calendar replay"); 67 training windows and 157 held-out windows, configuration frozen. Energy from a linear 10 W/core model; deadlines and delay bounds synthesised from runtime (up to 4x runtime, capped at 24 h).
- Requested walltime or prediction: none; actual runtime from the trace.
- Forecast versus oracle: none. Recommendations are scored at the actual intensity of the execution window. The discussion leaves queueing, forecast error and scheduler enforcement to future work.
- Numbers: 15.4 % lower carbon than no shifting; 23.8 % lower peak load than carbon-greedy; 93 % of the achievable carbon saving; +1.5 h mean start delay (A04 summary of the abstract; the 93 % and 23.8 % are visible in the PDF text).
- Row in A13 format:

| Paper | Decision | Workload | Carbon or RES signal | Forecast | Oracle | Runtime uncertainty | Evaluation scale | Statistics | Code |
|---|---|---|---|---|---|---|---|---|---|
| COAST, Feng 2026 | start time under a congestion game | CEA-Curie 2011 (PWA), 165,887 jobs, random alignment | UK half-hourly intensity, 2025 | none (actual intensity used) | no oracle arm; carbon-greedy and an achievable bound | none: actual runtime | 1 grid, 224 windows (67 train, 157 held out) | paired tests, variance decomposition | not checked |

- Verdict: C1 NONE (no forecast); C2 NONE; C3 NONE (a variance decomposition of outcomes by carbon alignment exists, not a gap split); C4 NONE; C5 PARTIAL (real HPC trace with frozen held-out windows, but one non-matching grid and windows rather than a held-out year).

### 1.3 LACS
- Citation: Bostandoost, R.; Lechowicz, A.; Hanafy, W. A.; Bashir, N.; Shenoy, P.; Hajiesmaili, M. "LACS: Learning-Augmented Algorithms for Carbon-Aware Resource Scaling with Uncertain Demand", The 15th ACM International Conference on Future and Sustainable Energy Systems (E-Energy '24), 4-7 June 2024, Singapore, pp. 27-45. DOI 10.1145/3632775.3661942 (Crossref verified). arXiv:2404.15211.
- What they do: online carbon-aware resource scaling for elastic jobs of unknown length; a learning-augmented algorithm combines minimum and maximum length bounds with an ML length prediction.
- Data: Electricity Maps CAISO hourly 2020-2023; synthetic job lengths; carbon forecasts simulated by adding uniform random error; job-length prediction error modelled (up to 60 %, Sect. 5.4). No workload trace.
- Requested walltime: no. Runtime prediction: simulated error only.
- Forecast versus oracle: the offline baseline needs accurate job length and carbon forecasts; the online baseline needs the true length. Abstract: within 1.2 % of the online baseline with perfect job length; within 16 % of the offline baseline; 32 % less carbon than the deadline-aware carbon-agnostic run.
- Row in A13 format:

| Paper | Decision | Workload | Carbon or RES signal | Forecast | Oracle | Runtime uncertainty | Evaluation scale | Statistics | Code |
|---|---|---|---|---|---|---|---|---|---|
| LACS, Bostandoost 2024 | resource scaling per slot (elastic) | synthetic jobs, length in [min, max] | Electricity Maps CAISO 2020-2023 | actual plus uniform synthetic error | online (known length) and offline (known length and intensity) baselines | synthetic prediction error 0-60 % | 1 grid | CDFs, competitive ratios | not checked |

- Verdict: C1 PARTIAL (synthetic forecast error, offline baseline); C2 PARTIAL (job-length uncertainty modelled, synthetic, no user estimates); C3 PARTIAL (length error and forecast error swept separately in Sect. 5.4 and 5.5 and compared with two baselines, but no 2x2 grid and no Shapley split); C4 PARTIAL (a length predictor is part of the algorithm, simulated error only); C5 NONE.

### 1.4 Tsafrir, Etsion and Feitelson 2007
- Citation: Tsafrir, D.; Etsion, Y.; Feitelson, D. G. "Backfilling Using System-Generated Predictions Rather than User Runtime Estimates", IEEE Transactions on Parallel and Distributed Systems 18(6), 789-803, June 2007. DOI 10.1109/TPDS.2007.70606 (Crossref verified). Full text: https://dants.github.io/papers/Pred07TPDS.pdf (author copy).
- What they do: EASY+ and EASY++. User estimates are kept only as kill times; scheduling uses system predictions (mean runtime of the user's last two jobs); predictions that prove too short are corrected.
- Data: SDSC, CTC, KTH and BLUE logs (Parallel Workloads Archive).
- Walltime versus prediction: both; the paper replaces requested time with a history prediction. No carbon, no forecast versus oracle comparison.
- Figures Paper A may cite (author PDF; accuracy = runtime / estimate, averaged over jobs, 1 for a perfect estimate):
  - Table 2 (Sect. 3.2, PDF page 11): average accuracy under EASY with user estimates is 32 % (SDSC), 39 % (CTC), 47 % (KTH), 31 % (BLUE). With the last-two-jobs predictor (EASY+) it is 60, 62, 60 and 61 %; the text says "stabilized at 60-62%" across the four traces. Row order was read from the text layer and cross-checked with the SDSC wait figure (363 min) in the later table; confirm visually before print.
  - Sect. 1, Fig. 2: for successfully terminated jobs the accuracy histogram is "rather uniform-like"; users pick round values so that 90 % of jobs use the same 20 estimates (Sect. 1, attributed there to its reference [35]).
  - Fig. 6: 7.7 % (SDSC), 9.3 % (CTC), 1.7 % (KTH) and 9.9 % (BLUE) of jobs have runtimes larger than their estimate (the caption says up to 10 %).
- Fit with Paper A: supports the gap between requested and actual runtime and the last-jobs history predictor as the third arm. The accuracy here is a mean ratio, not a median multiplier. The 7x to 300x median overstatement in A04 comes from A04's own trace computation and must be cited as such, not to this paper.

### 1.5 Mu'alem and Feitelson 2001
- Citation: Mu'alem, A. W.; Feitelson, D. G. "Utilization, predictability, workloads, and user runtime estimates in scheduling the IBM SP2 with backfilling", IEEE Transactions on Parallel and Distributed Systems 12(6), 529-543, June 2001. DOI 10.1109/71.932708 (Crossref verified). Full text read at https://www.researchgate.net/publication/3300562 (journal pagination visible).
- What they do: compare EASY and conservative backfilling on the CTC, KTH and SDSC SP2 logs and on models; study how user estimate quality affects backfilling.
- Walltime versus prediction: real user estimates analysed (Sect. 4); estimates from historical averages tested (Sect. 4.4: 45,159 of 62,630 CTC jobs, 72.1 %, had history; 12,001 jobs, 19.2 %, would have been underestimated). No carbon.
- Figures Paper A may cite:
  - Sect. 4.1 (pp. 535-536), Fig. 8 and Table 2: for jobs that ran 90 s or more and ended normally, the histogram of used share of requested time is "quite flat"; the authors conclude user estimates are "rather poor" but a good upper bound, since only a small fraction were killed. The text I could read gives no single mean accuracy; the exact bin values are in Table 2, whose cells did not extract (user step 2).
  - Footnote 2 (p. 537): 3,215 KTH jobs form the 100 % peak (killed at their estimate); 793 of the killed jobs had requested 4 h, the daytime limit.
  - Sect. 4.2: estimates drawn uniformly from [r, f x r] improve backfilling for moderate f, so inaccuracy is not necessarily harmful to a backfilling scheduler. Paper A should word the requested-walltime arm as a planning input loss, not as a scheduler defect.
- No median ratio is stated by the paper; none is given here.

## 2. KIT FH2 licence (Parallel Workloads Archive)
Sources (fetched 2026-11-12): https://www.cs.huji.ac.il/labs/parallel/workload/l_kit_fh2/index.html and https://www.cs.huji.ac.il/labs/parallel/workload/
- Log: KIT ForHLR II, Jun 2016 to Jan 2018, 114,355 jobs; file KIT-FH2-2016-1.swf (1.2 MB gz), "original log in SWF format as received". The page notes the log does not include the full workload of the machine.
- Acknowledgement: the log "was graciously provided by Mehmet Soysal" and the page asks users to "use a similar acknowledgment". Suggested text: "The KIT ForHLR II workload log was graciously provided by Mehmet Soysal."
- Archive citation request (main page): refer to the archive page as the source, and cite Feitelson, D. G.; Tsafrir, D.; Krakov, D. "Experience with using the Parallel Workloads Archive", Journal of Parallel and Distributed Computing 74(10), 2967-2982, Oct 2014, DOI 10.1016/j.jpdc.2014.06.013 (Crossref verified). The archive describes its aim as making the information "freely available" to researchers.
- Licence: neither page has licence text, terms of use or any statement on redistribution of the log or of derived data. Status: unknown (not restricted, not explicitly open). Safe practice: do not re-host the raw SWF; ship scripts that fetch it from the archive URL plus derived aggregate tables, with the acknowledgement and both citations. If the replication package will include job-level derived data from KIT FH2, ask the maintainer (contact on the main page) in writing first.
- The log page lists one paper that used it, key "soysal19". I did not resolve that key. A likely candidate is Soysal, Berghoff, Streit, "Analysis of Job Metadata for Enhanced Wall Time Prediction", JSSPP 2018, LNCS, DOI 10.1007/978-3-030-10632-4_1 (Crossref-registered, pages 1-14, 2019), which studies walltime prediction and would be relevant to Paper A, but the mapping to the archive key is not confirmed; check the archive bibliography page before citing.

## 3. EIA-930 publication delay and revisions
- EIA, "About the EIA-930 data", https://www.eia.gov/electricity/930-content/about.html. Schedule: demand for today is typically available one hour after the end of the operating hour; net generation, net generation by energy source and total interchange for each hour of yesterday are typically available by 11:00 a.m. Eastern time today; interchange with directly connected BAs for the day before yesterday by 11:00 a.m. Eastern; total CO2 emissions by energy source for yesterday by 4:00 p.m. Eastern; demand by subregion on a lag of 1-30 days.
- Revisions, same page ("Data quality"): demand is collected twice (hourly after the operating hour, and again at 7:00 a.m. the next day for the previous day) and the "reported values may or not be the same"; individual-BA hourly data are published as received; data are best values at the time of reporting.
- EIA, form instructions, https://www.eia.gov/survey/form/eia_930/instructions.pdf ("Response due date", "Data quality"): same-day files within 60 minutes of the end of the operating hour; daily files by 7:00 a.m. Eastern; expected revisions are resubmitted "within 3 days or as soon as the actual data is available"; unexpected errors above 10 MWh in any hour are corrected within 30 days.
- Consequence for Paper A: generation by source (the input to fuel-based carbon intensity) is available with roughly a one-day lag, so a deployable forecaster at hour t sees fuel data only up to about the previous day, and routine revisions run up to 3 days (30 days for errors). Paper A should either enforce a lag of at least 24 h on the generation-by-source inputs, or state that the "past-only" forecaster runs on final archived data and note the vintage caveat.

## 4. User steps
1. Optional (needed only if the release contains job-level KIT FH2 derived data): ask the Parallel Workloads Archive maintainer whether derived job-level data may be shared; address on https://www.cs.huji.ac.il/labs/parallel/workload/. Reply "done: sent" or paste the answer.
2. Optional: Mu'alem and Feitelson 2001, Table 2 (exact histogram components, p. 541) did not extract. Download via the VIT e-gateway from https://doi.org/10.1109/71.932708 into C:\Users\Shlok\Downloads and reply "done: <path>". Without it, Paper A cites only the qualitative result (flat histogram, Sect. 4.1) from this paper and the Tsafrir Table 2 figures for numbers.
