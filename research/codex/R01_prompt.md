# Paper A, Codex round 1: topic choice (you play E1 editor, E3 systems/statistics expert, E6 hostile referee)

You have 25+ years of expertise at the level of the best groups publishing carbon- and energy-aware computing in
Sustainable Computing: Informatics and Systems (SUSCOM), IEEE TSUSC, TPDS, FGCS, EuroSys, e-Energy. Create rather than
generate. Do not defer to Claude: disagree where the evidence says so. Token-efficient answer (at most 900 words).
Do not invent references: if you name prior work, give authors, year and venue only when you are sure, and mark
anything uncertain "(verify)". This thread will be reused for every expert discussion of this paper.

Charter: You are a dynamic-learning expert. You hold views as hypotheses. For every choice (question, data, model,
algorithm, test, figure, journal) you ask: why this, why not the strongest alternative, what evidence would change my
mind, and what would a hostile referee of the target journal say. You argue from evidence, not authority. You change
your view when another expert's evidence is better and you say so explicitly; you never agree just to end a
discussion. You write your position, the alternatives you rejected and why, and your confidence.

## Facts
- Journal: SUSCOM (Elsevier), JIF 6.2, CiteScore 13.2, acceptance 5 %, desk decision in about 1 day. Scope "making
  computing sustainable": power-aware software, scheduling and allocation, green data centres, runtime systems for
  power saving, models for joint power-performance optimisation, monitoring tools.
- SUSCOM most-cited 2023-2026 lane-A papers: #1 (409 cites) "Trends in AI inference energy consumption: beyond the
  performance-vs-parameter laws of deep learning"; then cloud task scheduling and VM placement with metaheuristics
  (7 of the top 17 lane-A papers), edge/fog offloading (5), AI/data-centre carbon (3: incl. "Spatio-temporal
  management of renewable energy consumption, carbon emissions, and cost in data centers", 2024). Most are simulated
  workloads with metaheuristics; a rigorous study on real traces or measured energy would stand out.
- Open special issue: "Energy-aware Artificial Intelligence: Theory, Algorithms, and Systems" (deadline 15 Dec 2026).
- Constraints: computational only; about 2 days of compute on a laptop (24 CPU threads, 31 GB RAM with about 6 GB
  free, one RTX 5070 Ti Laptop 12 GB GPU shared with other projects); full manuscript due Sun 15 Nov 2026 (4 days).
  Public, licence-clear data only. Pre-registration, held-out period, block bootstrap, Holm correction, baselines.
- Excluded topics (author's prior papers): battery health; water-quality conformal; LLM cognitive experiments; tabular
  foundation models; video streaming stall metrics; diffusion LM review; wind power forecasting; ECG labels; energy-aware
  LLM routing; InSAR floods; retinopathy. A sibling paper (lane "computing for sustainability": buildings, grids,
  transport) is written in parallel and must not overlap.

## Candidates
C1 Average vs marginal emission factors in carbon-aware temporal shifting (EIA-930 US hourly balancing-authority data
2019-2025; marginal factors by Siler-Evans regression and a merit-order heuristic; real job traces).
C2 Share of perfect-foresight savings of temporal shifting retained under honest past-only carbon forecasts across about
60 US balancing authorities; held-out final year.
C3 Production-based vs consumption-based (flow-traced, de Chalendar method) carbon intensity in carbon-aware decisions.
C4 Idle and low-utilisation GPU energy in production ML clusters (Alibaba PAI 2020 trace + measured utilisation-power
curve on the laptop GPU); savings from power capping or consolidation.
C5 LLM serving energy on a consumer GPU under real request traces (Azure LLM inference traces), batching window and
power cap vs energy per token and latency, NVML energy counters.
C6 Job runtime estimate error (Parallel Workloads Archive: requested vs actual runtimes) and carbon-aware batch
scheduling savings and deadline violations.
C7 Integrated error budget of carbon-aware temporal shifting: decomposes idealised-to-realised savings into forecast
error, runtime uncertainty, accounting choice, slack and interruptibility, across many regions and years with real job
traces and a pre-registered held-out year.

## Asked
1. E1 desk view: for each candidate, would SUSCOM's editor send it to review? One line each, with the main risk.
2. E3: for your top two, the sharpest estimand, the confirmatory hypotheses (at most 4), the baselines a referee
   expects, and the single analysis most likely to produce a large, robust, publishable effect.
3. E6: the strongest "this is already known / not novel / not credible" attack on your top two, and how to pre-empt it.
4. Propose up to two better candidates in lane A if you see them (feasible under the constraints).
5. Ranking and your recommendation, with confidence (0-1).
