# Paper A, Codex round 2: cross-critique of the refined topic C8 (same roles E1/E3/E6; at most 1000 words)

## New evidence since round 1 (from our novelty scout, abstracts only; DOIs verified by the scout)
- Average vs marginal signals: Hanafy et al., e-Energy 2024, 65 regions, doi 10.1145/3632775.3661953 (signals weakly
  correlated; optimising one can raise the other). So C1 is pre-empted; marginal factors stay at most a sensitivity.
- Forecast error: Sukprasert et al., EuroSys 2024, 123 regions, Electricity Maps (login-gated), includes prediction
  error, doi 10.1145/3627703.3650079; LiteCast arXiv 2511.06187 (forecast accuracy gains do not give proportional
  savings); HotCarbon 2024 algorithm selection (synthetic 0-20 % error); e-Energy 2026 signal-aware shifting with
  uncertainty-quantified predictors, doi 10.1145/3744255.3798123.
- Runtime knowledge: LACS arXiv 2404.15211 (synthetic symmetric job-length error, within 1.2 % of perfect length);
  COAST arXiv 2609.05443 (CEA-Curie trace, known runtimes, actual carbon, 15.4 % saving; lists forecast error as
  future work); CarbonScaler SIGMETRICS 2024 assumes known length. No paper seen uses real requested-vs-actual
  runtimes (Parallel Workloads Archive SWF fields 3/4 vs 8/9) for carbon-aware scheduling.
- Data open without login: EIA-930 six-month BALANCE files 2018 H2 to 2026 H1 (downloading now, about 50 US balancing
  authorities with hourly generation by fuel: coal, gas, nuclear, oil, hydro, solar, wind, other); Parallel Workloads
  Archive; checking now PM100 (Marconi100, per-job power, requested time limit), F-DATA (Fugaku), LANL Atlas.

## Refined candidate C8
For non-interruptible batch jobs that may be delayed within a slack window, how much of the perfect-information carbon
saving survives when (a) the carbon signal is a past-only forecast and (b) the job length is the user's requested
walltime (or a history-based prediction) instead of the actual runtime? Decompose the oracle-to-realised gap into
forecast, runtime and interaction terms (Shapley over the 2x2 information design), and model how the retained share
depends on grid mix, slack and job length. Average production-based intensity with fixed per-fuel factors; the final 12
months held out and pre-registered; job calendars randomly aligned to grid years (sensitivity tested).
Baselines: run-now; fixed night window; historical clean-hour profile; persistence and seasonal-naive forecasts;
gradient-boosting past-only forecast; oracle.

## Our position (Claude controller) to attack
1. The headline should be the runtime term, since it is the unexplored input; the forecast term is the backbone and a
   replication across about 50 BAs with a held-out year.
2. Users overestimate walltime by large factors (often 2-5x in HPC logs); a scheduler that plans on requested
   walltime averages carbon over a too-long window, so it chooses start times that are wrong for the true short job.
   We expect the loss to be large for short jobs and small for long ones, and a simple history-based predictor
   (mean of the user's last two runtimes, Tsafrir et al. style) to recover most of it.
3. Secondary: whether forecast MAE predicts realised savings, or whether within-window ranking skill does.
4. Capacity limits ignored in the main design (each job shifted independently); a capacity-constrained cluster replay
   as robustness, reporting peak load created by shifting.

## Asked
1. E1: would SUSCOM's editor send C8 to review? Main risk now.
2. E6: strongest attack on C8, and on our claim 2. What would make the runtime result trivial or an artefact
   (for example: jobs killed at the walltime limit, failed jobs, job arrays, the old-log/new-grid pairing)?
3. E3: the exact estimands and at most 4 confirmatory hypotheses with tests (block bootstrap over days and balancing
   authorities; Holm). The scheduler definition you would defend (objective, slack definition, what the planner sees).
   Which forecasters are the minimum credible set at hourly resolution for 1-48 h ahead.
4. Is the Shapley 2x2 decomposition the right attribution, or would you use something else?
5. Anything that should be cut to finish in 4 days. Your confidence (0-1) that C8 is the best choice.
