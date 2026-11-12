# Paper A topic candidates (P2, draft v1, 2026-11-11)

Lane A: making computing sustainable. Constraint: real public data or credible measurement; about 2 days of compute
on a laptop (24 CPU threads, one 12 GB GPU shared with other projects); deadline Sun 15 Nov.
Excluded (owner's prior work): battery health, water-quality conformal, LLM cognitive experiments, tabular foundation
models, Puffer streaming stall metric, diffusion LM review, wind power ML forecasting and ensemble calibration, ECG
label provenance, CORAL/SOMRA LLM routing (so no energy-aware LLM routing), InSAR flood, diabetic retinopathy.

## C1. Average versus marginal emission signals in carbon-aware temporal shifting
Question: when deferrable computing jobs are shifted in time to low average carbon intensity hours, how often and by
how much does the saving shrink, vanish or reverse when the same schedule is scored with marginal emission factors?
Data: EIA-930 hourly balancing-authority generation by fuel and interchange (US, public domain, 2019-2025); marginal
factors estimated by the Siler-Evans regression method and a merit-order heuristic; real job arrival and duration
traces (Azure, Alibaba, Google or Parallel Workloads Archive).

## C2. How much of the oracle carbon saving of temporal shifting survives honest past-only forecasts
Question: across about 60 US balancing authorities and several years, what share of perfect-foresight savings of
carbon-aware temporal shifting is retained with past-only forecasts (persistence, seasonal naive, gradient boosting),
and how does retention depend on grid mix and slack window? Held-out final year.

## C3. Production-based versus consumption-based (flow-traced) carbon intensity for spatial and temporal shifting
Question: does accounting for imports (consumption-based intensity via flow tracing, de Chalendar et al. method) change
which region or hour a carbon-aware scheduler picks, and the savings it reports?

## C4. Idle and low-utilisation GPU energy in production ML clusters
Question: how much energy do production GPU clusters spend at low utilisation, and how much would power capping or
consolidation save? Data: Alibaba PAI GPU trace 2020 (utilisation per task) plus a measured utilisation-to-power
curve on an RTX 5070 Ti Laptop GPU via NVML.

## C5. LLM serving energy on a consumer GPU under real request traces
Question: under real arrival traces (Azure LLM inference traces 2023/2024), how do batching window and GPU power cap
trade energy per token against latency, measured with NVML energy counters?

## C6. Job runtime uncertainty and carbon-aware scheduling of batch jobs
Question: carbon-aware schedulers assume known job durations; with real user runtime estimates (Parallel Workloads
Archive logs record requested and actual runtimes) or predicted runtimes, how much of the saving is lost, and do
deadline violations rise?

## C7 (integrated). An error budget for carbon-aware temporal shifting
Question: decompose the gap between the saving reported in idealised studies and the saving realised in practice into
(a) forecast error of the carbon signal, (b) job runtime uncertainty, (c) accounting choice (average vs marginal,
production vs consumption), (d) slack and interruptibility, across many grid regions, years and real job traces, with
a pre-registered held-out year. Combines C1, C2, C3 and C6 into one evaluation.

## C8 (refined after A03 and Codex R01, 2026-11-11 13:10). Realised saving of carbon-aware batch scheduling under honest carbon forecasts and real user runtime estimates
Question: for non-interruptible batch jobs that a scheduler may delay within a slack window, how much of the
perfect-information carbon saving survives when (a) the carbon signal is a past-only forecast and (b) the job length is
the user's requested walltime (or a simple history-based prediction) instead of the actual runtime? Decompose the
oracle-to-realised gap into forecast, runtime and interaction terms (Shapley over the 2x2 design), and model how the
retained share depends on grid mix, slack and job length.
Data: EIA-930 hourly fuel mix for about 50-60 US balancing authorities 2019-2026 (average production-based intensity
with fixed per-fuel factors; final 12 months held out, pre-registered); modern HPC job traces with requested and actual
runtimes and, where available, measured job power (candidates: PM100 / Marconi100, F-DATA / Fugaku, LANL Atlas,
Parallel Workloads Archive cleaned logs); random alignment of job calendars to grid years, tested for sensitivity.
Baselines: run-now, fixed night window, historical-clean-hour rule, persistence and seasonal-naive forecasts, gradient
boosting past-only forecast, oracle.
