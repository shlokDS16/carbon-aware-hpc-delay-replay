## 1. E1 editor’s desk view

| Candidate | Send to review? | Main risk |
|---|---|---|
| **C1** | **Probably no, as framed.** | Average-versus-marginal emissions is a consequential question, but Siler-Evans regression and a merit-order heuristic may not support credible hourly marginal factors. |
| **C2** | **Yes, narrowly.** | Forecast-aware shifting is established; the paper needs a sharper contribution than “realistic forecasts reduce ideal savings.” |
| **C3** | **Maybe.** | Consumption-based accounting could change decisions, but flow-tracing assumptions and data provenance may dominate the result. |
| **C4** | **Maybe.** | Alibaba’s 2020 PAI trace is real and public, but a laptop GPU power curve cannot establish cluster-level energy savings or generalize cleanly. |
| **C5** | **Probably no.** | The Azure trace supplies request timing and token counts, not a representative service plus energy ground truth; one consumer GPU narrows relevance. |
| **C6** | **Maybe.** | Requested-versus-actual runtime error is interesting, but trace fields may not mean comparable estimates and actual runtimes; scheduling results could be simulation artifacts. |
| **C7** | **No under this deadline.** | Strong framing, but too many coupled uncertainties, data sources, and modeling choices for a defensible preregistered study in four days. |

## 2. E3: top two — C2 and C6

**C2 estimand:** Across eligible BA-hour blocks in the held-out year, what fraction of *perfect-foresight emissions savings* does a prespecified past-only forecast policy retain, relative to an unshifted schedule, under fixed job energy, deadline/slack, and shifting constraints? Report the distribution across authorities, not just a pooled mean.

Confirmatory hypotheses:

1. Past-only shifting reduces emissions versus no shifting, averaged across held-out blocks.
2. Retained savings are materially below perfect foresight.
3. Forecast-aware scheduling beats a simple persistence forecast policy.
4. Benefits vary by region and slack; preregister the interaction and avoid post-hoc region selection.

Baselines: no shifting; perfect foresight as an upper bound; persistence; day-ahead seasonal climatology; and a forecast-agnostic “shift to historically clean hours” policy. Include an oracle with identical constraints so the comparison isolates forecast error. Use contiguous time blocks for uncertainty and Holm correction across confirmatory tests.

**C6 estimand:** For batch jobs with both requested and observed runtimes, estimate the change in emissions and deadline-miss rate from scheduling with observed runtimes versus requested runtimes, under the same carbon signal and job constraints. Baselines: no carbon awareness, requested-runtime scheduling, oracle actual-runtime scheduling, and a simple slack-aware policy. The make-or-break analysis is a paired replay on jobs with verified semantics and nontrivial deadlines, reporting the emissions–miss-rate frontier. If the trace does not support that pairing, drop C6.

## 3. E6: hostile referee

**C2 attack:** “This is known: temporal shifting and forecast error have already been studied, including uncertainty-aware forecasting and analyses of shifting limitations. More regions and another forecast baseline are not a contribution.” A recent HotCarbon paper explicitly studies uncertainty-aware decarbonization and temporal shifting; *On the Limitations of Carbon-Aware Temporal and Spatial Workload Shifting in the Cloud* analyzes sensitivity to prediction error. ([Li et al., 2024, HotCarbon](https://hotcarbon.org/assets/2024/pdf/hotcarbon24-final84.pdf); [EuroSys 2024 paper](https://lass.cs.umass.edu/papers/pdf/eurosys24-shiftinglimitations.pdf)) Pre-empt by making the estimand decision-centered—retained fraction of attainable savings under a transparent, preregistered policy—and demonstrate out-of-sample results across BAs and years, with no tuning on the held-out period. Be explicit that historical EIA intensity is not a live operational forecast.

**C6 attack:** “Requested runtimes are not necessarily operator predictions; the trace’s observed runtimes may include contention and failures. A replay that treats them as known at submission gives an unrealistic oracle and cannot show deployable benefit.” Pre-empt by auditing the trace schema and eligibility before analysis; exclude ambiguous jobs, model runtime uncertainty using only information available at submission, and present oracle results only as an upper bound. I would change my view if trace documentation does not establish requested and observed runtime semantics.

## 4. Better lane-A candidates

No stronger candidate is clearly feasible in the time available. A focused **C2 plus runtime/slack sensitivity** is more credible than C7’s full integrated error budget. The PAI 2020 trace is genuinely public and comes from a large production GPU cluster, but its characterization has already appeared in Weng et al., 2022, NSDI; a new claim must be about energy or scheduling, not trace description. ([Alibaba trace documentation](https://github.com/alibaba/clusterdata/blob/master/cluster-trace-gpu-v2020/README.md))

## 5. Ranking and recommendation

**C2 > C6 > C1 > C4 > C3 > C5 > C7.** Recommend **C2**, with **0.72 confidence**. Its advantages are a tractable held-out evaluation and a clear decision-level estimand; its novelty risk is substantial, and the cited prior work means the framing must be precise. C6 is the backup only if trace semantics survive an immediate audit. Browse-based literature check was targeted, not exhaustive.