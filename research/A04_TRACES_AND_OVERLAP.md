# A04 traces and overlap (Paper A, candidate C8)

VERDICT: A04 done; best trace PM100 (231,238 rows, Marconi100 May-Oct 2020, power yes) for the power-weighted analysis, with F-DATA (about 24M jobs, 2021-2024, power yes) as the large recent companion and NLR Kestrel/Eagle (listed, over 500 MB) as the energy traces whose years match EIA-930; overlap: LiteCast already does real-forecast carbon-aware scheduling on the KIT-FH2 PWA log (3.4 % saving, actual runtimes, one grid year); none of the four decomposes the oracle-to-realised gap into forecast, runtime-estimate and interaction terms, and none uses real user-requested walltime as the length signal.

Notes: the Zenodo search API returned 403 once (rate limit), the per-record API worked afterwards; DataCite was used to find DOIs. No login was needed anywhere. Free disk before downloads: about 102 GB.

## Part 1. Job traces

### Summary

| Trace | Jobs | Years | Requested time | Actual runtime | Job power or energy | Size | Status |
|---|---|---|---|---|---|---|---|
| PM100 (Marconi100) | 231,238 rows | May-Oct 2020 | yes (`time_limit`, minutes) | yes (`run_time`, s) | yes, sampled series (node, CPU, memory) | 287 MB | downloaded, md5 verified |
| F-DATA (Fugaku) | about 24M | Mar 2021-Apr 2024 | yes (`elpl`, s) | yes (`duration`, s) | yes (`econ`, `avgpcon`, `minpcon`, `maxpcon`) | 38 monthly files, 27.2 GB total | month 21_04 downloaded |
| NLR Kestrel | about 11M | Aug 2023-Dec 2025 | yes (`wallclock_req`) | yes (`wallclock_used`) | yes (`consumed_energy_raw_joules`, measured) | 697 MB | listed only |
| NLR Eagle | about 13.8M | Nov 2018-Jun 2024 | yes (`wallclock_req`) | yes (`wallclock_used`) | yes (iLO node energy, GPU energy; null if unmonitored) | 870 MB (1.3 GB with energy metrics) | listed only |
| LANL Mustang | 2,113,175 | Oct 2011-Nov 2016 | yes (`wallclock_limit`) | from start/end | no | 17.5 MB gz | schema checked |
| LANL Trinity | 25,237 jobs per FAQ | 2016, 3 months | yes | yes | no | 1.2 MB gz | schema checked |
| PWA logs (KIT FH2 etc.) | see (d) | 2010-2018 | yes | yes | no | 1 to 4 MB each | verified |

### (a) PM100
- Landing page https://zenodo.org/records/10127767 (v3, 2023-11-24). DOI 10.5281/zenodo.10127767 (earlier versions 10.5281/zenodo.8129257 and 8129258). Paper: Antici et al., DOI 10.1145/3624062.3624263 (Crossref).
- Licence CC-BY-4.0, open, no login. One file `job_table.parquet`, 287,154,521 bytes, md5 cf85f171a5ed5ff1d951d93f9bcbc6ef (equals the Zenodo md5, checked locally).
- Local: `C:\Users\Shlok\Downloads\Sustainable Computing papers\paper_A\data\raw\pm100\job_table.parquet`.
- Rows in the file: 231,238 (Zenodo text says 231,116; the 122-row difference is unexplained). Submit times 2020-05-05 to 2020-10-13 UTC. 477 users. States: COMPLETED 180,310, FAILED 29,840, CANCELLED 11,218, TIMEOUT 8,689, OUT_OF_MEMORY 1,011, NODE_FAIL 170.
- Exact fields: submit `submit_time`; also `eligible_time`; start `start_time`; end `end_time`; runtime `run_time` (s, int64); requested walltime `time_limit` (minutes, int64, 1 to 1440, median 540, no zeros); nodes `num_nodes_req`, `num_nodes_alloc`; cores `num_cores_req`, `num_cores_alloc`; GPUs `num_gpus_req`, `num_gpus_alloc`; user `user_id`; `group_id`; state `job_state`; exit `derived_ec`; `partition`, `qos`; power `node_power_consumption`, `cpu_power_consumption`, `mem_power_consumption` (list<int32>, one value per sample). List length is about run_time/20, so a 20 s cadence is inferred, not verified; a 16-node job shows about 7,970 W, so values look like whole-job sums in W.
- Observed: median run_time/time_limit = 0.028; 3.7 % of jobs exceed their limit. Field documentation: https://github.com/francescoantici/PM100-data/blob/main/documentation/job_features.md
- Schema (35 columns) printed from parquet metadata; 3 rows read (columns subset).
- Caveats: only jobs that ran exclusively on their nodes (per Zenodo description); five months of 2020, so random calendar alignment to the EIA years is needed.

### (b) F-DATA
- Landing page https://zenodo.org/records/11467483 (v1.0, 2024-06-05). DOI 10.5281/zenodo.11467483 (concept 10.5281/zenodo.11467482). Antici, Bartolini, Domke, Kiziltan, Yamamoto. CC-BY-4.0, open, no login.
- Files: 38 monthly `YY_MM.parquet` (21_03 to 24_04; the Zenodo listing shows 38 parquet files plus `feature_list.csv` 2,209 B), total 27.2 GB. Sizes 151 MB (21_04) to 1.33 GB (23_06). Only seven are under 500 MB: 21_03 (458 MB), 21_04 (151), 21_05 (433), 21_07 (283), 21_08 (336), 21_09 (331), 23_09 (456). All others are listed, not downloaded.
- Local: `...\paper_A\data\raw\fdata\21_04.parquet` (150,514,262 B, complete) and `feature_list.csv`.
- 21_04: 116,977 jobs submitted 2021-04-01 to 2021-04-30 (JST), 392 users, completed 103,315, failed 13,662.
- Exact fields: submit `adt` (also `qdt`, `schedsdt`); start `sdt`; end `edt`; runtime `duration` (s); requested limit `elpl` (s; none zero in 21_04; median 21,600; max 259,200); nodes `nnumr` (requested), `nnuma`, `nnumu`; cores `cnumr`, `cnumat`, `cnumut`; user `usr`; state `exit state` (completed or failed) and `ec`; power `avgpcon`, `minpcon`, `maxpcon`; energy `econ` (unit not stated in feature_list.csv; check the F-DATA paper); plus counters and a text embedding.
- Observed in 21_04: median duration/elpl = 0.139; power and energy fields non-null for all rows. Power is a scalar per job, not a series.
- Schema and 3 rows printed from parquet metadata (columns subset).

### (c) LANL Atlas
- https://ftp.pdl.cmu.edu/pub/datasets/ATLAS/ ("v1.0beta", repository still under development). No login. Licence text not found on the page. Cite Amvrosiadis et al., USENIX ;login: 43(4), Winter 2018 and USENIX ATC 2018, as the page requests.
- Mustang: `mustang/mustang_release_v1.0beta.csv.gz`, 17,542,790 B; 2,113,175 rows, 565 users, 2011-10-27 to 2016-11-08. Fields `user_ID`, `group_ID`, `submit_time`, `start_time`, `end_time`, `wallclock_limit`, `job_status` (COMPLETED 1,825,151; TIMEOUT 152,284; CANCELLED 135,740), `node_count`, `tasks_requested`. No power. Median runtime/limit 0.167.
- Trinity: `trinity/trinity_release_v1.0beta.csv.gz` 1,217,056 B (event log, about 33.8k rows; FAQ says 25,237 jobs, 88 users, 3 months of 2016); formatted version 284,486 B. Fields include `submission_time`, `start_date`, `end_date`, `wallclock_limit`, `nodes_requested`, `user_name`. No power.
- Verdict: 2011-2016 and no power; only useful as a large requested-versus-actual runtime robustness check. Copies in scratch only.

### (d) Parallel Workloads Archive, 2010 onward
Source https://www.cs.huji.ac.il/labs/parallel/workload/logs.html (browser User-Agent, HTTP 200). SWF format https://www.cs.huji.ac.il/labs/parallel/workload/swf.html: field 4 run time, field 9 requested time, field 12 user (I used the standard column positions). Page says "use original" for these logs, except CURIE which has a `-cln` file.

| Log | Jobs (page) | Period | gz size | What I checked |
|---|---|---|---|---|
| RICC (RICC-2010-2) | 447,794 | May-Sep 2010 | 3.7 MB | requested time > 0: 447,792; run > 0: 447,784; 176 users; median run/requested 0.017 |
| CEA CURIE cleaned (CEA-Curie-2011-2.1-cln) | 312,826 | Feb 2011-Oct 2012 | 3.6 MB | requested > 0: 312,823; run > 0: 295,540; 582 users; median 0.021 |
| PIK IPLEX (2009-1) | 742,965 | Apr 2009-Jul 2012 | 10.6 MB | not parsed |
| Intel NetBatch A to D 2012 | 9.1M to 13.4M each | Oct-Dec 2012 | not measured | not parsed |
| UniLu Gaia (2014-2) | 51,987 | May-Aug 2014 | 0.86 MB | requested > 0: all; run > 0: 51,859; 84 users; median 0.003 |
| MetaCentrum2 | 5,731,100 | Jan 2013-Apr 2015 | 57.7 MB (part 3) | not parsed |
| CIEMAT Euler | 9,263,012 | Nov 2008-Dec 2017 | 90.7 MB | not parsed |
| KIT FH2 (ForHLR II) | 114,355 | Jun 2016-Jan 2018 | 1.2 MB | requested > 0 and run > 0 for all rows; 166 users; median 0.148 |

None has power. Median run/requested of 0.003 to 0.15 shows how loose user estimates are. Needs random calendar alignment to grid years.

### (e) Other public traces (requested plus actual runtime plus power or energy)
1. NLR HPC Kestrel Jobs Data, DOI 10.7799/3023270, https://data.nlr.gov/submissions/302. About 11M Slurm jobs, Aug 2023-Dec 2025, `esif.hpc.kestrel.job-anon.zip` 697.3 MB (md5 8f1d3be1cbe6345ef45e658a783c2aa0), parquet. Fields `submit_time`, `start_time`, `end_time`, `wallclock_req`, `wallclock_used`, `nodes_req/used`, `processors_req/used`, `state_simple`, `consumed_energy_raw_joules`, `consumed_energy_raw_watt_hours`, `cpu_energy_tdp_estimated_*`. Licence behind "View License" not read. Over 500 MB: listed, not downloaded.
2. NLR HPC Eagle Jobs Data and Additional Energy Metrics, DOI 10.7799/3023273, https://data.nlr.gov/submissions/295. About 13.8M jobs, Nov 2018-Jun 2024; core zip 870.1 MB (md5 a06527de28cbf207d1e743822978b9b4), energy-metrics zip 1.3 GB. Fields `submit_time_tz`, `start_time_tz`, `end_time_tz`, `wallclock_req`, `wallclock_used`, `state_simple` (incl. TIMEOUT), `node_energy_total_watt_hours`, `gpu0/1_energy_total_watt_hours`. Licence not read. Over 500 MB: listed only.
3. NREL Eagle three-month sample, DOI 10.7799/1722950, https://data.nlr.gov/submissions/152: json.bz2 for 2019-12, 2020-04, 2020-08 (4 to 5 MB each) with `wallclock_req`, `wallclock_used`, `avg_power`, `std_power`. Small and usable now; not downloaded because the brief named only PM100 and F-DATA.
4. Adastra (GENCI/CINES) MI250/Genoa, 90 days with 20 s power telemetry, https://zenodo.org/records/21834931 (2026-08-07, CC-BY-4.0, 1.7 GB, PM100-like columns incl. `time_limit`). Over 500 MB; single depositor, no paper.
5. BR-HPC-Log (Petrobras), DOI 10.5281/zenodo.23173614: 7,787,294 Slurm records 2021-2024, 8.13 GB uncompressed, Apache-2.0; no power field in the abstract.
6. Not a trace but relevant: "Timed-out HPC jobs are 45% of a cluster's job energy and are predictable before they start", Zenodo DOI 10.5281/zenodo.21911812 (2026-08-13, single author, not peer reviewed), built on Eagle and Kestrel.
7. Possible near-duplicate on data only: "Quantifying job-level carbon efficiency in HPC: an empirical study based on the PM100 dataset", DOI 10.1186/s42162-025-00586-6 (2025-11-12). Per its abstract it predicts per-job emissions with an MLP and scores efficiency; no shifting. Full text not read.

### Recommendation for C8 data
- Primary: PM100 (real power series, real limit versus runtime, 231k jobs) and F-DATA 2021-2024 (per-job average power over three years). Both CC-BY-4.0, no login.
- Same-country, same-years option: Kestrel (2023-2025) and Eagle (2019-2024) next to EIA-930. Needs the user's go-ahead for 697 MB and 870 MB (see USER STEPS).
- KIT FH2 should be included, since LiteCast used it; that gives a direct comparison.
- Requested walltime alone overstates length by about 7x to 300x at the median across these traces, so a history-based predictor is a needed third length arm.

## Part 2. Overlap read

Read from arXiv HTML converted to text (`agents\scratch_A04\t_*.txt`); method and evaluation sections only.

### LiteCast (arXiv 2511.06187, https://arxiv.org/abs/2511.06187)
- Regions and years: 50 regions in the USA and Europe; jobs scheduled through all days of 2023; CarbonCast trained on 2022 (Sect. 5, Emission Calculations).
- CI source: EIA and ENTSO-E hourly energy mix with per-source emission factors; weather from a public portal.
- Forecasts: real models (SARIMAX with weather and demand exogenous inputs, persistence, CarbonCast). It consumes third-party weather and demand forecasts, so it is not strictly past-only.
- Job lengths: known. Synthetic lengths and slacks of 1 to 168 h; the KIT replay (Sect. 6.3) uses recorded runtimes with slack set to the recorded wait time. No requested versus actual distinction found.
- Real user runtime estimates: no. Decomposition of the gap: no (compares predictors with the oracle and uses a concordance index). Held-out: no preregistered holdout; temporal split only for the CarbonCast baseline.
- Headline: 97 % of the maximum attainable average savings and about 20 % higher savings than state-of-the-art forecasters (abstract); KIT trace average saving 3.4 %, about 2 points below the oracle (Sect. 6.3, Fig. 9).

### Sukprasert et al., EuroSys 2024 (doi 10.1145/3627703.3650079; arXiv 2306.06502)
The lass.cs.umass.edu PDF URL returned 404, so I read the arXiv version (OpenAlex lists arXiv 2306.06502 as a location of this DOI). I did not diff it against the ACM version.
- Regions and years: 123 regions, 2020-2022.
- CI source: Electricity Maps hourly average intensity.
- Forecasts: main analysis assumes perfect future knowledge of intensity and job length (Sect. 5). Sect. 6.2 adds uniform random forecast error. No real forecaster.
- Job lengths: known and idealised (1 h to 168 h, distributions drawn from cited Google and Azure traces). No HPC trace, no requested walltime.
- Real user estimates: no. Decomposition: by job length, slack, interruptibility and migration, not by information source. Held-out: no.
- Headline (Sect. 5.2): temporal shifting with 24 h slack saves 8.4 % of the global average emissions, 34 % with one-year slack; a 50 % forecast error adds 10 to 12 % emissions (Sect. 6.2), about 3 % at CarbonCast's reported 14 % MAPE.

### COAST (arXiv 2609.05443, v1 29 Jul 2026, https://arxiv.org/abs/2609.05443)
- Region and years: UK carbon intensity, 1 Jan 2025-1 Jan 2026, paired with the 2011 CEA-Curie workload under random alignments (Sect. IV-A). The authors say the HPC was not in the UK.
- Forecasts: none. Candidates are scored with actual intensity ("rather than forecasts", Sect. V); forecast error left for future work.
- Job lengths: actual runtime from the trace. Energy from a linear core-count model (trace has no power). Deadlines and maximum delay synthesised (up to 4x runtime, capped at 24 h).
- Real user estimates: no. Gap decomposition: no, but it reports a variance decomposition of outcomes (carbon alignment explains 83 % of the variance of the carbon outcome). Held-out: yes, 67 training and 157 held-out windows, parameters frozen on the training windows.
- Headline: 15.4 % lower carbon than no shifting, 23.8 % lower peak load than carbon-greedy, 93 % of achievable carbon saving, +1.5 h mean start delay (abstract); an upper bound under idealised realisation.
- Relevance: same random-calendar-alignment device as C8; cite it for the method.

### LACS (arXiv 2404.15211; E-Energy 2024, doi 10.1145/3632775.3661942)
- Region and years: CAISO only, Electricity Maps hourly 2020-2023; 1,314 arrival slots (Sect. 5.1).
- Forecasts: synthetic uniform percentage error on actual intensity.
- Job lengths: unknown to the algorithm; ML length predictions simulated with synthetic error of 0 to 60 % (Sect. 5.4). No trace. Elastic (resource-scaling) jobs, not rigid delay-only.
- Real user estimates: no. Decomposition: no, though Sect. 5.4 and 5.5 vary length error and forecast error separately (nearest thing to a 2x2). Held-out: no.
- Headline: within 1.2 % of the online baseline with perfect job length and within 16 % of the offline baseline with accurate forecasts; 32 % less carbon than the deadline-aware carbon-agnostic run (abstract).

### Verdict against C8
Already done by others:
- Real past-and-weather forecasts against an oracle for delay-only jobs across about 50 US and EU regions for one year, plus a replay of the KIT FH2 trace: LiteCast.
- Perfect-information upper bounds by slack, length and region: Sukprasert et al.
- Synthetic forecast error and synthetic length-prediction error as separate sweeps: Sukprasert (forecast), LACS (both, elastic jobs, one region).
- Random calendar alignment and held-out workload windows: COAST (but perfect intensity).
Still open against these four:
- Real user-requested walltime as the job-length signal compared with actual runtime and a history predictor, and the saving it loses.
- The 2x2 design (forecast oracle or past-only, length actual or estimated) with the oracle-to-realised gap split into forecast, runtime and interaction terms (Shapley).
- Energy-weighted outcome with measured job power (PM100, F-DATA, Kestrel, Eagle).
- Preregistered final-12-month holdout across about 50-60 US balancing authorities with fixed fuel factors.
- A model of the retained share against grid mix, slack and job length.
Limit: reading was targeted at these four papers; novelty beyond them rests on A03's scan (`NOVELTY_SCAN.md`).

Hostile referee sentence: "LiteCast already shows that rank-preserving real forecasts recover about 97 % of oracle savings on real cluster trace replays, and Sukprasert and LACS already study forecast and job-length error separately, so this paper only relabels that finding with a Shapley table over a 2x2 grid and a request-time baseline that everyone knows is loose."
Defence to prepare: user-requested walltime is not the actual-length oracle LiteCast used; the interaction term is a new quantity; the energy-weighted outcome with measured power is new.

## USER STEPS NEEDED
1. Decide whether to allow the NLR Kestrel download (697.3 MB, https://data.nlr.gov/submissions/302, DOI 10.7799/3023270) and the Eagle core file (870.1 MB, https://data.nlr.gov/submissions/295). Reason: they are the only measured-energy Slurm traces whose years match EIA-930. Without them C8 uses PM100 and F-DATA with random alignment. The licence text behind "View License" on both pages was not read; confirm before reuse.
2. Confirm the F-DATA `econ` unit from the F-DATA paper before any energy arithmetic.

## Files
- Downloaded: `C:\Users\Shlok\Downloads\Sustainable Computing papers\paper_A\data\raw\pm100\job_table.parquet`; `...\data\raw\fdata\21_04.parquet` and `feature_list.csv`.
- Scratch: `C:\Users\Shlok\Downloads\Sustainable Computing papers\paper_A\research\agents\scratch_A04\` (PWA samples in `pwa\`, Atlas in `atlas\`, paper texts `t_*.txt`, `swfstat.py`).
