# A07 job table (Paper A)

VERDICT: A07 done; traces PM100 (180,310 completed jobs of 231,238), F-DATA/Fugaku (2,998,737 completed of 3,399,278; months 21_04, 23_01, 23_04, 23_07, 23_10), KIT FH2 (114,355 completed of 114,355; every SWF status is 1, so no TIMEOUT can be identified); median r_act/r_req 0.028 (PM100), 0.232 (F-DATA), 0.148 (KIT FH2); NLR Kestrel NOT obtained (HTTP 503 at 13:48 IST and again at 15:04 IST); see USER STEPS NEEDED.

Output: `data/derived/jobs.parquet` (3,744,871 rows, exactly the 14 requested columns; dtypes string, timestamp[ns, UTC], double, int64). Intermediate per-trace files `data/derived/jobs_<TRACE>.parquet` are kept (the script merges them). Code: `src/prep_jobs.py` (one loader per trace: `load_pm100`, `load_fdata`, `load_kit_fh2`, `load_kestrel`; `finalise()` shared). Numbers below come from `tables/jobs_trace_stats.json`, written by the script. Run: `PYTHONIOENCODING=utf-8 python src/prep_jobs.py` (takes about 1.5 minutes). Free disk before work 115 GB, after 80 GB (limit 15 GB).

## Definitions applied (all three traces)
- `r_req_h`, `r_act_h` in hours; `nodes` = allocated nodes (falls back to requested if allocated is 0).
- `state` mapping: COMPLETED, TIMEOUT, CANCELLED, FAILED stay; PM100 OUT_OF_MEMORY (1,011) and NODE_FAIL (170) are mapped to FAILED; anything else OTHER (none occurred). SWF status 1 = COMPLETED, 0 = FAILED, 5 = CANCELLED, other = OTHER. F-DATA `exit state`: completed / failed only.
- `submit_local_hour` = local clock hour + minutes/60 + seconds/3600 at the site (zoneinfo, so DST is handled); `submit_local_dow` 0 = Monday.
- `r_pred_h` and `n_hist` exactly as specified: the user's jobs with END strictly before this job's submit and state COMPLETED or TIMEOUT; mean `r_act_h` of the two most recent by end time (one job: that job's value); none: `r_req_h`; then capped at `r_req_h`. `n_hist` = min(number of such jobs, 2). Implemented with sorted keys and `searchsorted` (vectorised). Ties in end time break by row order (rows sorted by submit time).
- Leakage check: for every trace, 1,000 random jobs were recomputed naively (pandas filter on user, `end < submit`, state, last two by end) and compared with the vectorised result; the assertion on `n_hist`, `r_pred_h` and on end < submit passed for all three traces (it runs inside `finalise()`, so any rerun re-asserts).
- No row was dropped: validity filter (submit present, `r_req_h` > 0, `r_act_h` >= 0 and finite, nodes >= 1) removed 0 rows in each trace. Jobs with `r_act_h` = 0 are kept (PM100 0.03 %, others none); the simulator should filter them if it needs a positive length.

## 1. PM100 (Marconi100, CINECA Bologna, Europe/Rome)
Source `data/raw/pm100/job_table.parquet`, md5 cf85f171a5ed5ff1d951d93f9bcbc6ef (equals the Zenodo md5, https://zenodo.org/records/10127767), sha256 6be954098d9bd6bfdef6881c6d8a3260170b00d16839509700e1b6976da3a7eb.

Timestamps: UTC. Evidence: (1) the parquet columns are `timestamp[us, tz=UTC]`, produced from Slurm epoch times; (2) the weekday submit profile converted with Europe/Rome has the shape of an Italian working day: ramp 2.0 % (07h) to 3.4 % (08h) to 6.2 % (09h), a lunch dip at 14h (5.0 % against 6.0 % at 13h and 7.1 % at 15h) and a dinner dip at 20h (2.8 %); read as already-local it would put the dinner dip at 18h and the ramp at 07h. UTC hour histogram of all jobs (hours 0 to 23): 4920, 4028, 3923, 3901, 4739, 4933, 7522, 13454, 15391, 14624, 13490, 13463, 10879, 15931, 17075, 12826, 10597, 10361, 6088, 10718, 7547, 8593, 8506, 7729. Residual uncertainty about a 1 to 2 hour offset is small relative to the simulator's 2 h minimum slack but not zero.

Power: `node_power_consumption` is a list of 20 s samples of whole-job power in W (sum over all the job's nodes and both power supplies). Source: the field table (https://github.com/francescoantici/PM100-data/blob/main/documentation/job_features.md) says only "Power consumption of the job, recorded at Node level"; the generating script https://raw.githubusercontent.com/francescoantici/PM100-data/main/extract_data.py (`extract_job_power`) selects the job's nodes, does `groupby(timestamp).sum()` over nodes for `ps0` and for `ps1` and adds them. Empirical check: median per-job mean power scales linearly with `num_nodes_alloc` (1 node 690 W, 2 nodes 1,398 W, 4: 2,678 W, 8: 5,070 W, 16: 9,943 W, 32: 18,875 W; about 700 W per node). So `power_w` = mean of the series, with NO multiplication by nodes. All 231,238 jobs have a series (none empty). The mean was computed batch by batch (4,000 rows per batch). `energy_kwh` = power_w * r_act_h / 1000 (derived; PM100 has no measured energy).

Rows: in 231,238 (Zenodo text says 231,116; unchanged from A04); raw states COMPLETED 180,310, FAILED 29,840, CANCELLED 11,218, TIMEOUT 8,689, OUT_OF_MEMORY 1,011, NODE_FAIL 170; normalised COMPLETED 180,310, FAILED 31,021, CANCELLED 11,218, TIMEOUT 8,689; rows out 231,238; 477 users; submit 2020-05-05 15:55 to 2020-10-13 04:44 UTC; job_id unique.

- Fraction r_act > r_req: all rows 3.70 %; COMPLETED 0.0006 % (1 job).
- COMPLETED quantiles (5 / 25 / 50 / 75 / 95 %): r_req_h 0.167 / 0.833 / 9 / 24 / 24; r_act_h 0.000278 / 0.0025 / 0.0528 / 0.487 / 11.4; r_act/r_req 1.2e-05 / 0.00063 / 0.0281 / 0.215 / 0.737.
- TIMEOUT: 8,689 rows; share with r_act within 2 % of r_req 92.2 % (all rows within 2 %: 4.7 %).
- r_pred_h / r_act_h (COMPLETED, r_act > 0): 0.089 / 0.685 / 1.008 / 2.00 / 23.4. r_pred_h / r_req_h median 0.0287.
- n_hist = 0: 1.04 % of all rows (0.48 % of COMPLETED).
- power_w quantiles (W): 522 / 588 / 819 / 1,330 / 11,410 (no NaN).
- Total energy 1.228e6 kWh; share from jobs longer than 24 h: 14.1 %.

## 2. F-DATA / Fugaku (Kobe, Asia/Tokyo)
Licence CC-BY-4.0 (Zenodo API `metadata.license.id = cc-by-4.0`), record https://zenodo.org/records/11467483 (DOI 10.5281/zenodo.11467483), paper Antici et al., Scientific Data 12:1321 (2025), DOI 10.1038/s41597-025-05633-1. Downloaded to `data/raw/fdata/` with browser headers (a plain User-Agent hit a Zenodo 403 rate limit at first, as in A04). Months kept: 21_04 (existing) plus 23_01, 23_04, 23_07, 23_10 (all under 1.5 GB; the brief's example set). All five file md5 values equal the Zenodo checksums:

| File | Bytes | md5 (= Zenodo) | sha256 |
|---|---|---|---|
| 21_04.parquet | 150,514,262 | 3178b7481f639511a74b2be85f5079ba | a92259eb100339998a6ae5c7452200ef06a765500c50adbe42d66e43aff5068d |
| 23_01.parquet | 981,864,234 | 681603aba504a37da6c19d0cc173980a | ea4e39944f4b38e7d0aabe6f185d40bdb680aa4d426a841521ddc4395a84d2af |
| 23_04.parquet | 575,431,429 | 261dce6e2bdba46820186229d727b600 | 7213182439a75bd58607efb850e81dbadbe24be2144921338eccb0a4cb37d593 |
| 23_07.parquet | 968,169,044 | 9cd9e0aa7ebc418e0e5c8c2d977fe969 | eaed73c23bae77d51901bd946d7c7f1c80b17403305dab72f8e9435acb87a31f |
| 23_10.parquet | 885,571,255 | eb1d96b17237f15f29371ddf40ad9e38 | e04b97ba97519ca557cdfec739dfaec606f18fab3102801b5328c1b44e2642d7 |

(23_01 was first corrupted by two curl processes writing the same file; the md5 check caught it, the file was deleted and fetched again in six byte ranges; the md5 above is of the clean file. `logs/fdata_checksums.txt` still contains the line of the discarded bad copy, 985,726,762 B.)

Units (confirmed, with quotes):
- `duration`: seconds. Check: `edt - sdt` equals `duration` within 1 s for all rows of 21_04; the feature list says "Duration of the job execution in seconds" (`data/raw/fdata/feature_list.csv`).
- `elpl`: seconds. feature_list.csv: "Elapsed time limit (the time limit set to the job duration)", no unit; seconds inferred from values (a 1 s job has elpl 10, median 21,600 = 6 h, maximum 259,200 s in 21_04) and `duration <= elpl` for every 21_04 row.
- `econ`: Wh. Paper (https://www.nature.com/articles/s41597-025-05633-1): "each job data contains the econ feature giving the energy consumption in Watt-Hours". Check: `econ / (avgpcon * duration)` = 1/3600 (0.000278 median) in 21_04.
- `avgpcon` (also `minpcon`, `maxpcon`): W. The feature list calls it "Average node power consuption", but the paper states "The power consumption is the sum of the minimum, average, or maximum power consumption of the resources allocated to the job during its execution", and `econ = avgpcon * duration / 3600` with no node factor, so it is a whole-job power. Median `power_w / nodes` is about 93 to 102 W per node in five of six node-count bins (47.6 W in the 17 to 64 node bin; the cause was not investigated, possibly allocated nodes above used nodes, since 21_04 has jobs with `nnuma` 12 and `nnumu` 1); therefore `power_w` = `avgpcon` as is, `energy_kwh` = `econ` / 1000 (measured). 
- Timestamps carry an explicit +09 offset (JST), parsed to UTC.
- `nodes` = `nnuma` (allocated), fallback `nnumr`.

Rows: in 3,399,278 (per month of submit time: 21_04 116,977, 22_12 4,711, 23_01 889,780, 23_04 618,335, 23_06 3,220, 23_07 957,831, 23_09 12,299, 23_10 796,125; the 22_12, 23_06 and 23_09 rows are jobs whose `adt` lies in the month before the file's month); 1,410 users; submit 2021-04-01 to 2023-10-31 UTC. States: only `completed` 2,998,737 and `failed` 400,541; no TIMEOUT state exists in F-DATA, so the TIMEOUT rule has no rows and the history predictor uses COMPLETED jobs only. Rows out 3,399,278. In 21_04, 46,602 of 116,977 rows (40 %) repeat a `jid` (presumably array or bulk sub-jobs; the share over all months was not measured); all rows are kept and a repeated `jid` is made unique with a ".k" suffix, so job_id is unique. The history of a user runs across all five months (months are not contiguous, so the first jobs of each month use history from up to three months earlier, or none).

- Fraction r_act > r_req: all 0.0008 %; COMPLETED 0.0009 %.
- COMPLETED quantiles (5 / 25 / 50 / 75 / 95 %): r_req_h 0.167 / 1 / 4 / 17 / 72; r_act_h 0.00417 / 0.0658 / 0.544 / 2.5 / 18; r_act/r_req 0.00228 / 0.0422 / 0.232 / 0.573 / 0.873.
- TIMEOUT: none. As a proxy, FAILED rows within 2 % of r_req: 0.28 %; all rows within 2 %: 0.99 %.
- r_pred_h / r_act_h (COMPLETED, r_act > 0): 0.031 / 0.801 / 1.05 / 1.88 / 22.3. r_pred_h / r_req_h median 0.294.
- n_hist = 0: 1.91 % of all rows (1.45 % of COMPLETED).
- power_w quantiles (W): 42 / 85 / 113 / 536 / 7,110 (no NaN).
- Total energy 2.89e7 kWh; share from jobs longer than 24 h: 7.7 %.

## 3. KIT FH2 (ForHLR II, Karlsruhe, Europe/Berlin)
Source: Parallel Workloads Archive https://www.cs.huji.ac.il/labs/parallel/workload/l_kit_fh2/index.html, file `KIT-FH2-2016-1.swf.gz` (1,194,167 B), md5 4c136801c2728ad46f30e903544846c8, sha256 e1a4b12185dae1d2666f66649274883f85ae611b553edbc22726a5edec6239f5 (no published checksum). The archive offers only the original log "as received"; there is no cleaned version for this machine (the brief said cleaned). A request with only a short User-Agent got an error page; full browser headers and a Referer worked.

Header: UnixStartTime 1464739965 (= 2016-06-01 00:12:45 UTC = 02:12:45 CEST, equals the header's StartTime), TimeZoneString Europe/Berlin, 114,355 jobs, MaxProcs 24,048. Fields used: 2 submit (s after UnixStartTime), 3 wait, 4 run time, 5 allocated processors (fallback 8), 9 requested time, 11 status, 12 user, 15 queue. `nodes` = ceil(processors / 20) for queue 1 (thin nodes, whole nodes always allocated per the header) and / 48 for queue 2 (visualisation nodes). End time = submit + wait + run. `power_w` and `energy_kwh` = NaN (no power).

Status: all 114,355 rows have SWF status 1, so every job is COMPLETED and no TIMEOUT can be identified, although many jobs run to the limit (see below). The log does not hold the full workload of the machine (header disclaimer: special campaigns, privacy removals, no interactive jobs).

Rows in 114,355, out 114,355; 166 users; submit 2016-06-01 to 2018-01-04 UTC.
- Fraction r_act > r_req: 0 (run time is capped by the limit). Fraction within 2 % of r_req (all rows): 7.3 %; this is the best available proxy for time-outs.
- COMPLETED quantiles (5 / 25 / 50 / 75 / 95 %): r_req_h 0.167 / 0.333 / 4 / 24 / 72; r_act_h 0.015 / 0.0289 / 0.167 / 3.88 / 25.8; r_act/r_req 0.00118 / 0.0356 / 0.148 / 0.468 / 1.
- TIMEOUT share within 2 %: not defined (no TIMEOUT rows).
- r_pred_h / r_act_h: 0.0157 / 0.509 / 1.00 / 2.31 / 51.6. r_pred_h / r_req_h median 0.158.
- n_hist = 0: 0.20 %.
- power_w: all NaN. Energy: n/a.
- Median r_act/r_req 0.148 agrees with A04.

## Checks and caveats
- The three medians equal the A04 values (PM100 0.028, KIT 0.148; F-DATA 21_04 0.139 in A04 against 0.232 across five months here).
- F-DATA `power_w` per node varies by node-count bin (above); use `power_w` as given (whole job), not times nodes. PM100 likewise: never multiply by nodes.
- PM100 TIMEOUT jobs are the only strong evidence of limit-bound behaviour: 8,689 jobs, 92.2 % within 2 % of the limit. The predictor treats TIMEOUT runs as history, as specified (their `r_act_h` is the limit, so a user with time-outs gets a long prediction).
- F-DATA covers 2021 and 2023, PM100 2020, KIT 2016-2018: calendar alignment to EIA-930 years is needed by the simulator, as noted in A04.
- Nothing downloaded was executed; parquet and gz text were only read. Scripts live in `src/`, raw files in `data/raw/<trace>/`.

## USER STEPS NEEDED
1. NLR HPC Kestrel Jobs Data (DOI 10.7799/3023270, https://data.nlr.gov/submissions/302; the DOI redirects to https://www.osti.gov/servlets/purl/3023270 and then to the same page). Used for: the only job trace whose years (Aug 2023 to Dec 2025) and country (US, Golden CO, America/Denver) match EIA-930, with measured job energy. Status: HTTP 503 "Site under maintenance" on 2026-11-11 08:18 UTC (13:48 IST) and again at 09:34 UTC (15:04 IST), so the licence text ("View License") was not read and nothing was downloaded. DataCite (https://api.datacite.org/dois/10.7799/3023270) has an empty `rightsList`. What to do: when the site is back, open the page, read the licence under "View License", and tell me "kestrel ok" only if it is an open licence allowing research use with no login or click-through; then rerun the download (697 MB zip, md5 8f1d3be1cbe6345ef45e658a783c2aa0 per A04) into `data/raw/kestrel/`. Without it the job table has no US-site trace and no trace from the EIA-930 years with measured energy; PM100 and F-DATA remain the power-bearing traces and the paper can say so. `load_kestrel()` is a stub that raises until the schema and licence are checked (field names from A04: `submit_time`, `end_time`, `wallclock_req`, `wallclock_used`, `state_simple`, `consumed_energy_raw_watt_hours`, hashed `user`).
