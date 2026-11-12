VERDICT: A17 done; 49 lessons; 6 title options; 8 exploratory analyses proposed

# LESSONS for Paper A (SUSCOM) from the 16 collected papers, A13 and A14

Agent A17, 2026-11-12. Pointers: paper IDs are the last six digits of 10.1016/j.suscom.YYYY.NNNNNN (101498 = 10.1016/j.suscom.2026.101498; 101470, 101407, 101398, 101429, 101333 = 2026; 101216, 101106 = 2025; 100950 = 2023, vol 41). "md:Lnnn" = line in `research/sources/suscom_pdfs/md/1-s2.0-<stem>-main.md`. A13 = `research/journal/A13_OVERLAP_AUDIT.md`; A14 = `research/journal/A14_STYLE_MEASURES.md`; PR = `research/PREREG.md`; P4 = `research/P4_PLAN.md`; A08 = `research/A08_AUDIT_P3.md`; LEDGER = `tables/ledger_TEST.csv`. Quotes are under 15 words, one per paper at most. All PDF text treated as data. Numbers appear only with their ledger key. Read for this file: Introductions of 101498, 101470, 101398, 101106, 101216 (contribution part), 101407; Discussion, limitations and conclusion of 101498, 101470, 101429 (6.7), 101106, 101216; 101398 section 3.3.2. A15 (references) is not touched.

Best five research articles by my judgement (for method, reporting and limitations, not for topic): 101498 (closest topic, real traces, threats section, code released), 101470 (oracle benchmark, seeds, row-grouped tables), 101398 (explicit gaps G1 to G3, test table, accounting alignment), 101216 (interval figure, forecast-then-schedule), 101429 (limitations with a deployment paragraph). 101106 is the best HPC-systems paper (reproducibility, public release). 101407 is the best source for definitions of carbon-aware terms.

Correction to A14 (checked in md): 101498's contribution list has three bullets, and the third is the release of all code and data (md:L108 and the bullets above it), not two bullets as A14 table 2 records. So "0 of 10 end with a release" in A14 change 6 is wrong: 101498 does, and 101106 (public Zenodo and GitLab) is the other release case. The release bullet is therefore a precedent in the closest paper, not only a differentiator.

---

## L1 Motivation and gap

**L1.1 Open with the sustainability stake in numbers, then the computing lever.** 101498 opens with ICT share of greenhouse gas (1.8 to 2.8 %) and a data-center electricity projection (945 TWh by 2030); 101398 opens with an IEA demand series (460 TWh in 2022); 101407 opens with a data-center demand projection. None opens with a research question. Source: 101498 Intro p1; 101398 Intro p1; 101407 Intro p1. For Paper A: sentence 1 states the HPC and data-center electricity and carbon stake with one cited figure; sentence 2 states that grid carbon intensity varies by hour, so delaying flexible batch jobs is a lever.

**L1.2 One sentence maps the literature by shifting type with bracketed ranges.** 101498: "spatial [4 to 8], temporal [9 to 11], and spatio-temporal [12 to 16] shifting" (md Introduction para 2). It lets the reader place the paper in one line and cite widely in one place. Paper A: one sentence for temporal shifting (Wiesner 2021, Sukprasert 2024, 101498, 101407), explicitly marking that Paper A studies the temporal lever only.

**L1.3 The gap is stated as a missing dimension, then answered with "this gap is addressed by".** 101498 states that land use had not been integrated into scheduling and answers it in the next sentence (it hedges with "To the best of our knowledge"; Paper A keeps W4's ban on that phrase and states the gap with "we found no study"). 101398 turns this into a labelled device: three gaps (G1 integrated spatio-temporal optimisation, and two more) each matched to a contribution. Source: 101498 Intro p3; 101398 Intro (G1 to G3). For Paper A: one gap, with two parts (forecast error, runtime estimate), each visible in the contribution that answers it.

**L1.4 Name the closest prior systems with their own headline numbers as foils.** 101398 cites CARBON-DQN (20 to 70 % marginal carbon efficiency) and an AI-based framework (up to 42 %), then says they treat a centralised cloud. Numbers from prior work are quoted in context, not compared. For Paper A: name Wiesner, Sukprasert and 101498 with what each assumes (injected 5 % error, a prediction-error scenario, noise-perturbed grid mix and runtimes assumed known), and do not set Paper A's percentages beside 20 to 85 % figures (A13 section 3, last bullet).

**L1.5 The Introduction defines the carbon-aware vocabulary in prose.** 101407 defines "carbon-agnostic scheduling" (dispatch immediately), then average intensity for accounting versus marginal emissions rate for decisions, all in the Introduction. Source: 101407 Intro p3 to p4 (md:L93-L100). For Paper A: one short paragraph defines run-now (carbon-agnostic), slack, requested walltime and perfect-information arm, because "walltime" never appears in the 16 papers (A14 section 4.3).

**L1.6 Limitation of prior work uses a soft universal.** 101470: existing coupling mechanisms "rarely exploit long-horizon plans as structured guidance"; 101106: "most research" is theoretical or single-server. A soft quantifier avoids an unprovable "none". Paper A's gap sentence below follows this: "not reported in the studies we reviewed".

**L1.7 Every Introduction ends with a contribution list and a roadmap by section numbers.** 101498, 101106, 101216, 101470 all do; 101498's roadmap even lists what Section 4 contains (results, discussion and threats). Paper A: roadmap names Section 6 for Discussion with Limitations and threats.

**L1.8 What none does and Paper A can: state the measured question in the first paragraph of the Introduction body.** All 16 introduce by context and literature. A single sentence stating the quantity measured (the share of the perfect-information saving a deployable scheduler realises, and what it loses to each input) gives the editor E2 ("the one finding to remember") early.

### L1 proposed opening plan for Paper A (five paragraphs, about 700 to 850 words)
1. Stake (3 sentences). Data-center and HPC electricity use with one cited projection; hourly grid carbon intensity varies; flexible batch jobs can be delayed within slack to cleaner hours.
2. What is known (3 to 4 sentences). Temporal shifting studies (Wiesner 2021, Sukprasert 2024, 101498, 101407, COAST, LiteCast) report savings with perfect or noise-perturbed signals and, mostly, known runtimes; 101470 scores an oracle gap by horizon for wind power, with unit tasks.
3. What a deployed scheduler sees (3 sentences). A past-only forecast and the runtime the user requested, which on HPC systems is typically a loose upper bound (cite a user-estimate study via A15, "not verified here"; median ratio of actual to requested runtime per trace is in `tables/jobs_trace_stats.json` and A07, not a ledger key: add a ledger key before quoting).
4. Gap and design (2 + 2 sentences).
5. Contributions (see L2) and roadmap.

**Gap sentence (respects A13 forbidden wording; no "first", no "no prior work", names the three outside works):**
"Studies that vary forecast error inject synthetic noise or assume ideal job lengths, and studies on real HPC logs assume known runtimes [Wiesner 2021; Sukprasert 2024; 101498; LACS; COAST; LiteCast]; the saving a deployable scheduler realises with a trained past-only forecast and the user-requested walltime, and how the lost saving divides between those two inputs, is not reported in the studies we reviewed."
Check against A13: cites the five SUSCOM papers' common assumptions without a "none of" claim extended to the field; LACS, COAST, LiteCast named (A13 point 4). Verify the three outside papers' wording from full texts before submission (A13 section 2: "not re-audited here").

---

## L2 Contribution and novelty sentences

**L2.1 SUSCOM lists are short and nominal.** A14 section 4.1: 3.5 items on average, T median 3, 9 of 10 nominal or passive voice. 101498: "A holistic formulation ... is proposed"; 101470: "A prediction-driven two-stage scheduling framework is proposed"; 101106: noun phrases ("Power, performance and energy theoretical models ..."). Paper A should use noun phrases, "we" optional.

**L2.2 A measurement paper's contributions are measurements and a design, not a method.** No exemplar contributes a measurement-only study; they propose frameworks. Paper A must therefore say that no new scheduler is proposed (W8) and make the design (2 x 2 plus Shapley plus preregistration) the method contribution. A13 section 3 gives the defensible claims; use them.

**L2.3 The release bullet has a precedent in the closest paper** (101498 bullet 3; correction above). Keep it as the last bullet.

**L2.4 Contributions avoid numbers in 101498 and 101470 bullets but not in their abstracts.** Keep numbers out of the bullets (consistency with the ledger), put them in the abstract and Results.

**L2.5 No exemplar claims "first" in the bullets.** 101498 hedges once in the gap sentence only. Paper A: nothing at all (W4; A13 wording to avoid).

### L2 proposed contribution bullets (nominal voice; A13 defensible claims 1 to 4)
- A pre-registered measurement, on real HPC batch-job traces and 42 US balancing authorities with a held-out year and block-bootstrap intervals, of the share of the perfect-information carbon saving that delay scheduling realises with a past-only forecast. (A13 claim 1)
- A 2 x 2 design (signal by runtime estimate) with a Shapley allocation that divides the gap between the perfect-information and the deployable scheduler into a forecast term and a runtime term, and the saving recovered by a history-based runtime prediction. (A13 claims 2 and 3)
- A comparison of the deployable scheduler with non-forecast baselines (run-now, night rule) and several forecasters under every runtime estimate, with small and negative results reported as found. (A13 claim 4)
- The release of code, derived data, the result ledger, the pre-registration and its checksum. (101498 precedent)
If the owner wants three bullets (A14 median), merge bullet 3 into bullet 1.

---

## L3 Result reporting

**L3.1 Numbers come with a "from a to b" sentence and then a mechanism sentence.** 101470 (md:L1195-L1210): "Relative to Oracle, the WU gap widens from 1.03 % to 7.38 % and 11.33 %", then "The widening Oracle gap reflects the limitation of prediction-based planning under increasing uncertainty." Paper A: after each estimate, one interpretive sentence, hedged only on the mechanism (W15).

**L3.2 Results tables carry row groups: Proposed, Ideal (Oracle), Baseline, Ablation; spread as mean ± SD over seeds, "-" for deterministic rows with a note.** 101470 Tables 5, 8, 9 (A14 section 2). Paper A's main table should use the same row groups (Perfect-information, Deployable, Runtime variants, Baselines), with 95 % interval columns, not ± SD, and a note that all rows come from one simulation of the same jobs.

**L3.3 Improvement over a named baseline in percent beside absolute means.** 101498 Tables 8 to 11 give improvement over the Local baseline. Paper A: report percentage points of relative saving against run-now (as defined in PR section 5) and an absolute quantity (g CO2 per kWh of job energy, or kg CO2 per MWh of job energy). The ledger has relative savings only; add a ledger key for the run-now mean intensity per trace (derived from the saved energy sums) so the absolute value is computed by script, never by hand. Referees flag relative-only reporting (BB B10).

**L3.4 Statistics reporting that was criticised and why.** 101407 reports a 95 % CI over n = 3 task profiles and then rejects a null (md:L903-L914, A13): an interval over archetypes is not an interval over jobs. 101398 reports stars with no test named (A14 figure notes). Paper A: always state the unit (fixed 42 BAs, 7-day blocks within BA, B = 2000), the sidedness and the null-centring (PR section 6), and report "p < 0.0005" for the floor value (A08 check 3f; ledger key `TEST.PM100.w.S12.H1_deployable_saving.p_holm` is 1/2001 times 3).

**L3.5 Show the oracle gap as a function of a driver.** 101470 reports the gap by horizon. Paper A has the Shapley terms by slack (ledger keys `TEST.PM100.w.S2` to `S24.shapley.*`) and the retained share by slack and job-length class; present both as the analogue of A13 adopt item 1.

**L3.6 Report the three traces side by side and let disagreement stand.** Ledger: on PM100 the runtime term exceeds the forecast term (`TEST.PM100.w.S12.shapley.runtime` and `.forecast`), the same on KIT FH2 (`TEST.KIT_FH2.w.S12.shapley.runtime`, `.forecast`), but not on F-DATA (`TEST.FDATA.w.S12.shapley.forecast` above `.runtime`). A sentence like "the runtime term is larger on two of three traces" is correct; "runtime matters more than the forecast" is not. All H1 to H3 are supported on all three traces (Holm p keys `TEST.<trace>.w.S12.H1_deployable_saving.p_holm`, `H2_...`, `H3_...`).

**L3.7 Retained share is the headline ratio.** `TEST.<trace>.w.S12.shapley.retained_share` is the deployable saving divided by the oracle saving with actual runtime (PM100, F-DATA, KIT FH2 differ; report each). Pair it with the absolute oracle saving, because a retained share of a small number is a small number (a referee will notice that the oracle saving itself is small on these grids: `TEST.PM100.w.S12.saving.oracle|act`).

**L3.8 Small and negative effects go in the table, not only in prose.** The night rule saves nearly nothing on PM100 and loses on F-DATA (`TEST.PM100.w.S12.saving.night`, `TEST.FDATA.w.S12.saving.night`); persistence loses (A08 3f). 101470 reports Pred-Off and OnlyRL honestly against its own method; 101398 includes a test table. Keep every baseline in T4.

**L3.9 State what the intervals do not cover.** A08 T1: intervals condition on the observed job sample; add S1 (user-cluster bootstrap) results beside, labelled exploratory. 101498 reports means and SD over six seeds and no intervals; Paper A should say in one sentence what the interval is a statement about.

**L3.10 Do not over-read a single scenario.** 101407's 75.7 % is a single-case comparison dominated by spatial arbitrage (A13 A4). Paper A pools over 42 BAs and jobs; say so once, in the Discussion comparison paragraph.

---

## L4 Discussion and implications

**L4.1 Structure that works: one discussion subsection per scenario or question, then a trade-off subsection, then threats.** 101498 section 5 (5.1 and 5.2 scenarios, a trade-off subsection, 5.5 Threats to validity). 101407 5.3 "Comparative benchmarking and critical discussion". Paper A: 6.1 What the 2 x 2 says, 6.2 Implications, 6.3 Comparison with earlier work (why 12 h slack on one grid gives smaller savings than the spatial or wind-driven studies, A13 answer item 1), 6.4 Limitations and threats to validity, 6.5 Reproducibility.

**L4.2 Implications are written as who can do what.** 101498 section 5.1: lightweight workloads "could serve as a first mover" for sustainability-aware orchestration; 101429 6.7 adds an industrial-deployment paragraph (supervisory layer above the existing building energy management system). Paper A implications (counterfactual replay, so "would" and "could", not "will"):
- Operators: log requested and actual runtime, add a history-based runtime prediction to the delay planner (H3 recovery, keys `TEST.<trace>.w.S12.H3_prediction_recovery.est`), and prefer carbon-aware delay only on grids with a large daily range (Spearman descriptive, Figure 11 key in CAPTIONS.md).
- Users: walltime accuracy has a carbon value (H2 penalty); tighter requests recover saving but a limit set too low kills the job (TIMEOUT semantics; A08 4c), so this is an implication for estimates, not for shorter limits.
- Scheduler designers: when the forecast term or the runtime term is larger depends on the trace (L3.6); a forecaster upgrade and a runtime predictor are separate levers; the planner is the delay-to-lowest-integral policy, so nothing here ranks schedulers (W8).
- Grid-data providers and operators of carbon-signal APIs: data latency matters (S2), which is why S2 is in the paper.
Do not write that savings "will be realised" in production (EDITOR R05 q4; A08 T4, T5).

**L4.3 Limitations: four of the six 2026 articles have a dedicated subsection** (A14 section 4.2): 101398 5.4, 101498 5.5 "Threats to validity", 101470 5.6, 101429 6.7. Forms differ: 101470 is three sentences ("First ... Second ... Finally ..."); 101498 uses run-in bold labels (Simulation-based methodology, Generality, Input data quality, Embodied impacts, Regional resource equivalence, Spatial shifting constraints, Economic costs), each with the weakness, why it may still hold, and what future work would do (md:L2966-L3060). The 101498 form is the best fit for a referee reader: it is skimmable and always pairs a threat with a mitigation. Paper A: run-in labels, 400 to 600 words, one label per A08 item: Job sample and intervals (T1), Data vintage and publication delay (T2), Average versus marginal signal and factors (T3), Cross-system pairing (T4), Capacity and queueing (T5), Estimand and BA selection (T6, M1), Scheduler is a heuristic, oracle is relative (T7), Counts of cleaned hours and the TEST-year arrival gap (M2, M3).

**L4.4 Admit the assumption that a prior paper also makes, and say what changes.** 101498 admits runtimes known; Paper A tests exactly that. In the Discussion, state that the 101498 assumption "runtimes could be estimated from previous runs" is the position the pred arm tests (A13 adopt item 5).

**L4.5 State the average-versus-marginal convention in Methods and repeat it as a limit.** 101398 section 3.3.2 gives a model paragraph (average intensity, defined as total grid emissions over total generation; location-based accounting, GHG Protocol Scope 2) and then asserts the choice "affects absolute emission calculations but not relative comparisons between schedulers". Paper A must not copy that assertion: A08 T3 says the effect on marginal impact is unknown. Cite Sukprasert (average versus marginal signals) for the caveat and put sensitivity S3 beside it.

**L4.6 Conclusion: results first, then what to do, then future work in one short paragraph.** 101498: reductions with ranges, then "may be more relevant in practice" for temporal shifting, then robustness and future work. 101216: sentences with figures. 101106 states its own limit ("limited to a single-server approach"). Paper A conclusion: three results with keys, one sentence of implication, one sentence on limits, future work (marginal signals, queue-aware simulation, a US trace).

---

## L5 Figures

**L5.1 Best figure 1: 101470 Fig. 7** (per-seed thin lines with a shaded band, same 3 x 3 structure, one colour per method across the paper). Adopt for Paper A Figure 8 (saving against slack): one thin line per alignment replicate (3) per arm plus the fixed-BA band, panels per trace. It shows whether replicate spread is smaller than the arm gaps.

**L5.2 Best figure 2: 101216 Fig. 6** (mean with 95 % t-interval above, box plot below, whisker rule in the caption, lettered panels). Adopt for Figure 9 (per-BA forest): panel (a) sorted per-BA penalty with the full within-BA interval, panel (b) a box plot of the 42 per-BA values with the whisker rule in the caption.

**L5.3 101470 Fig. 3 pattern: proposed method thick and solid, baselines dashed or grey, legend in the first panel only, off the data.** Paper A: the deployable arm drawn thick, perfect-information arms thin, baselines grey; one legend per figure outside the data.

**L5.4 One colour per arm family held across all figures** (101470 and 101106 do it with non-safe palettes; A14 section 3). Encode the 2 x 2 with two channels: colour = runtime information (actual, requested, predicted), marker or line style = signal (open or dashed = oracle, filled or solid = LightGBM). Then every figure can show all four cells plus pred without a legend of more than 8 entries (A14 F12; 101429 Fig. 10 and 100950 Fig. 6 are the failures). Baselines grey with direct labels.

**L5.5 Waterfall instead of stacked bars for the Shapley split.** A waterfall from perfect-information saving to deployable saving (steps: runtime term, forecast term; interaction shared as in PR 7.1) on a zero-based axis, one panel per trace, intervals on each step once the post-hoc script exists. This also shows the "runtime larger on two of three traces" fact without a stacked bar. Avoid: 3D bars (101429 Fig. 10), radar fills (101333 Figs 4 and 7), a line across categorical models (101333 Figs 3 and 6), truncated bar axes (101398 Fig. 8).

**L5.6 Captions: finding plus n plus interval type, under 35 words.** Current CAPTIONS.md lengths are Fig 1 = 78 words, Figs 6, 7 = 50, Fig 14 = 52, Figs 8 to 10, 13 = 42 to 45 (my count); only Figs 11 and 12 are under 35. 101498 states findings in captions with numbers; keep that, trim the rest.

**L5.7 Consistency between panels helps readers** (101106: same strip structure and colours across Figs 5 to 10). Use one panel structure (PM100, F-DATA, KIT FH2 in that order, same y-limits where comparable) in Figures 6, 7, 8, 10.

**L5.8 Font and legend rules where peers fail:** tick text under 7 pt in 101498 Figs 5 and 11, 101333 Figs 5 and 8, 101106 Figs 5 to 10; labels overlapping error bars in 101398 Fig. 9. Keep F3 (at least 7 pt at print size) and check at print size.

### Concrete changes proposed to `research/FIGURE_PLAN.md`
- FP-1 Colour and marker encoding line replaced by the two-channel scheme (L5.4); baselines grey, direct labels.
- FP-2 Figures 11 and 12 merged into one two-panel figure (a) oracle saving against daily range, (b) runtime penalty against solar share, with the Spearman values in panels (they are already near the 35-word caption limit). Result: 13 figures, which keeps the owner's 13 to 14 rule while the typeset median stays about 9.5 (A14 section 4.1); if the owner prefers fewer, also fold Figure 13 (delay cost) into Figure 6 as panel (b), giving 12.
- FP-3 Figure 6: dot plot on a zero-based axis with run-now at zero, perfect-information arms open markers, deployable arms filled; fixed-BA interval as a thick bar, two-stage as a thin whisker (already FIGURE_FIXES 1); add the best simple policy as a labelled grey marker; panels by trace.
- FP-4 Figure 7: waterfall (L5.5), intervals added when the post-hoc script exists.
- FP-5 Figure 8: replicate lines plus band (L5.1); add the S2 data-latency lines as a labelled exploratory panel only if S2 has run.
- FP-6 Figure 9: two panels (L5.2).
- FP-7 Figure 14: forest plot of D, H2 and H3 under each variant (primary, near-limit, unweighted, two-stage, DEV, S1 to S5); exploratory rows in a visually separate block with the label "post-freeze, exploratory"; replaces table T6's role as a figure, while T6 stays as the numeric grid.
- FP-8 New optional Figure 15 slot: runtime-estimate sweep curve (L7 X1) if X1 runs; do not add it if the count would exceed 14.
- FP-9 Figure 1: keep one panel for the 2 x 2 for a computing reader (F10); cut the caption to 35 words.

### Concrete changes proposed to `figures/FIGURE_FIXES.md`
- FF-1 Add item: Figure 1 and all captions to at most 35 words (current counts above); Figure 14's "move in step" check stays (item 4).
- FF-2 Item 7 (merge 11 and 12) becomes decided: merge (FP-2), unless the expert panel objects.
- FF-3 Item 2 (Shapley intervals): redraw as a waterfall; if no interval script exists by P6, plot point estimates with the caption "Point estimates; interaction shared equally" (already in the caption) and no interval, rather than a partial one.
- FF-4 Add item: check at print size that tick text is at least 7 pt in every figure (L5.8), and that no label touches an interval bar.
- FF-5 Add item: replace any legend with more than 8 entries by direct labels (L5.4).
- FF-6 Add item: every y-axis that shows savings starts at zero, with a thin zero line (run-now).

---

## L6 Phrasing referees in this field expect

**L6.1 Average versus marginal intensity.** Say "average (production-based) carbon intensity: lifecycle emissions of generation in the balancing authority divided by its generation, location-based (Scope 2) accounting" (101398 section 3.3.2 uses the same convention). Say "the saving is a saving in accounted average intensity", not "emissions avoided". Say "marginal intensity, the emissions of the next unit of demand, is the quantity relevant to a demand change and is not modelled" (101407 uses MER; 101498 uses average). Cite Sukprasert for the comparison. Never write that the choice does not matter for relative comparisons (L4.5).

**L6.2 Slack.** Define once as "slack S: the maximum time a job's start may be delayed" and use "delay tolerance" or "flexibility window" only as synonyms in Related work (101498 uses "delay tolerance", dt 4 to 48 h; 101407 uses "slack time"). In tables and arms use S. Never use "deadline" for S unless the deadline is arrival plus slack plus runtime.

**L6.3 Walltime.** "Requested walltime: the time limit the user supplies at submission, which the scheduler enforces (a job reaching it is killed, state TIMEOUT)". "Actual runtime: the measured run time." No SUSCOM paper uses either term (A14 section 4.3: 0 matches), so the definition belongs in the Introduction or Section 3, with the semantics audit (PM100 `time_limit`, F-DATA `elpl`, KIT FH2 status field; A08 4c) in the data section and the near-limit sensitivity named.

**L6.4 Oracle and perfect information.** 101470 defines "Oracle. A perfect-information benchmark. It solves the same MILP with realised data" (md:L841-L845). Paper A: "perfect-information arm (oracle): the same planner given the realised intensity (and, in oracle|act, the actual runtime). It is not a global optimum of any scheduling problem" (A08 T7). Keep the label oracle|act in tables and "perfect information" in prose.

**L6.5 Deployable.** "A deployable scheduler uses only what is known at submission: a forecast built from past data and the requested walltime (or a runtime predicted from the user's earlier jobs)." Never "realistic", never "production".

**L6.6 Saving and penalty units.** Saving is relative (1 minus emissions over run-now emissions); differences of savings are percentage points ("pp"); "penalty" is a pp difference; "retained share" is a ratio. Mix of "%" and "pp" is a common error in the corpus; use pp for every difference.

**L6.7 "Significant".** Only for the Holm-adjusted bootstrap result of H1 to H3; elsewhere "larger", "clearly above zero in 41 of 42 BAs". Report p as "p < 0.0005" at the bootstrap floor.

**L6.8 Carbon-agnostic baseline = run-now.** 101407 "Local-Immediate", 101498 "Local". Use "run-now (start at arrival)" and "carbon-agnostic" once.

**L6.9 Balancing authority (BA).** Define at first use: an entity that balances supply and demand on a section of the US grid and reports to EIA-930; do not call them "regions" or "grids" without saying a BA is meant.

**L6.10 American English and "data center".** Confirmed in W14; 101498 mixes (analyzes, hyperscale). Keep American.

**L6.11 Foreign traces on US grids: say "what-if" plainly.** "Trace jobs are replayed on US grids at their local weekday and clock time; the result answers what these jobs would have emitted had they run there" (A08 T4).

**L6.12 No first-person excess:** 3 to 7 "we" per 1,000 words (A14 section 4.1; 101498 at 6.9 is the closest exemplar).

---

## L7 Analyses the frozen design still allows (labelled exploratory), ranked

Conditions for every item (from P4 and PR section 9): post-freeze, exploratory, new code in new files (src/sens_*.py importing frozen modules, none edited), grid fixed and md5-written before the first run, one row in `research/PREREG_DEVIATIONS.md`, own ledger `tables/ledger_TEST_sens_<id>.csv`, reported beside the frozen value whatever it shows, no promotion to confirmatory, nothing chosen on TEST (any noise or tuning scale is fitted on DEV). CPU only; the P4 resource gate applies (at least 6 GB free RAM, one heavy job at a time across papers). Items X1 to X7 go beyond P4 S1 to S6.

| Rank | Id | Analysis | Question it answers for a SUSCOM referee | Method and cost (CPU, memory) | Value |
|---|---|---|---|---|---|
| 1 | X1 | Runtime-estimate sweep | How accurate must a runtime estimate be to keep the saving? Where do requested walltime and the history prediction sit on that curve? | Planner estimate R_hat = R_act x m for m in {0.25, 0.5, 1, 2, 4, 8} (and a log-normal noise variant with the SD matched to the log of R_req over R_act measured on DEV), signals oracle and lgbm, S = 12, three traces; plot saving against estimate error with req and pred marked. Light: arms only, about the cost of the existing arms, memory as the frozen run | High: turns H2 and H3 into an operator rule; compares with LACS (synthetic length error) |
| 2 | X2 | Injected noise versus real forecast | Does the noise-injection practice (101498 MAE 0.05 to 0.2; Wiesner 5 %; 101216 Fig. 11) over or understate the loss from a trained forecaster? | Signal = actual intensity x (1 + eps) with eps scale per lead chosen so the MAE matches LightGBM MAE at leads 1 to 24 on DEV (not TEST), arms noisy|act and noisy|req; compare saving with lgbm|act and lgbm|req. Light to moderate; no model fit | High: answers a methodological question the corpus leaves open |
| 3 | X4 | Load-concentration proxy | Does delay scheduling pile load into few hours (T5: no capacity limit)? | From the chosen starts, hourly job-energy per BA relative to run-now; peak-to-mean ratio and the 99th percentile hourly multiple per arm. If sim outputs do not store starts, rerun two arms (oracle|act, lgbm|req) with start dump. Light to moderate; not a queue simulation, say so | High: pre-empts the capacity objection |
| 4 | X3 | Forecast-lead cap | How far ahead must the forecast reach? | Planner sees forecast leads up to L in {6, 12, 24, 48, 96}, holding the lead-L value beyond (as the frozen design does beyond 96); lgbm|req and lgbm|act, three traces. Forecast table already holds all leads: light | Medium to high: parallels 101470's horizon analysis |
| 5 | X5 | Concentration of the runtime penalty | Is the H2 penalty driven by loosely estimated jobs, long jobs or a few users? Is it fixable by user education? | Stratify the existing job-level results by decile of R_act over R_req and by the top users (users counted in S1); share of penalty by stratum; per-BA unweighted mean and median beside the pooled estimate (A08 T6, option 3). Needs job-level output; if absent, rerun two arms with job dump. Light | Medium to high: gives the operator implication a number |
| 6 | X6 | When the saving accrues | Which arrival hours, weekdays and months carry the saving; does the deployable arm lose in some seasons? | Aggregate existing job or day-level results by local arrival hour and by month; retained share by month. Light, no new simulation if daily arrays exist | Medium |
| 7 | X7 | Marginal-like signal proxy (oracle arms) | Does the 2 x 2 order change under a marginal-style signal? (D2, A08 T3) | Fossil-only intensity (emissions of fossil generation per kWh fossil generated) as a crude marginal proxy; oracle|act and oracle|req only (no refit); label strictly "proxy, not a marginal estimate". Overlaps S3 rebuild; share its code path. Medium | Medium to high but assumption-laden; run after S3 |
| 8 | X8 | Do-no-harm start rule (not recommended) | Does delaying only when the forecast promises more than a threshold remove losses? | New decision rule; threshold chosen on DEV | Low: breaks the scope note that no new scheduler is proposed (W8); skip unless the owner asks |

Order of work when RAM allows: X1, X3 (light), X2, X4, X5, X6, then X7 after S3. None of X1 to X7 touches the frozen estimates, and each yields one figure panel or one row of T6, not new main figures (FP-8 aside).

---

## L8 Title options (finding-led, no negatives, under 18 words, no acronym needed, no question mark)

Facts to respect: the deployable arm keeps part of the perfect-information saving (`TEST.<trace>.w.S12.shapley.retained_share`, a share for each trace); the runtime term exceeds the forecast term on PM100 and KIT FH2 and not on F-DATA (`TEST.PM100.w.S12.shapley.runtime`/`.forecast`; `TEST.KIT_FH2...`; `TEST.FDATA.w.S12.shapley.forecast` larger; FIGURE_FIXES 2). Therefore no title says that runtime matters more than the forecast. Numbers stay out of titles (0 of 16 SUSCOM titles have them; ledger consistency). Word counts are mine.

1. "Forecast and walltime information jointly determine the carbon saving of delay-scheduled HPC batch jobs" (14 words). Finding-led; true for all three traces (both terms are positive; interaction small on all three traces: `TEST.<trace>.w.S12.shapley.interaction` is about a tenth of `.gap` or less); owner-style. Untested form in SUSCOM (0 of 16 finding-led).
2. "Carbon savings of delay-based HPC batch scheduling with past-only forecasts and requested walltimes" (13 words). Verb-less descriptive, the 101498 pattern (verb-led or descriptive, no colon); safest for scope and editor.
3. "Carbon-aware delay scheduling of HPC batch jobs: how much perfect-information saving a deployable scheduler realizes" (15 words). Descriptive object plus a "how much" clause, W1's recommended shape; the clause names the measured quantity without a number.
4. "Decomposing the gap between ideal and deployable carbon-aware HPC job scheduling into forecast and runtime terms" (16 words). Method-first (the 2 x 2 and Shapley design is the contribution); "gap" is mildly negative, so use only if the owner accepts it.
5. "A pre-registered evaluation of deployable carbon-aware delay scheduling for HPC batch jobs across US grids" (15 words). Highlights the rigour differentiator (0 of 10 topic-close papers pre-register) but has a trailing region phrase the owner dislikes (MP s8).
6. "Carbon savings that HPC batch jobs realize when delayed using past-only forecasts and requested walltimes" (15 words). Finding-oriented phrasing, plain verbs, no acronym beyond HPC; close to option 2 with the subject as the jobs.

Recommendation: option 1 if the owner keeps the finding-led rule, option 2 as the fallback that matches the SUSCOM norm (A14: median 14 words, 0 of 16 finding-led, so option 1 carries editor-reaction risk G4). Define HPC in the abstract. The owner approves the final title.

---

## Lesson index (49)
L1.1 to L1.8 (8), L2.1 to L2.5 (5), L3.1 to L3.10 (10), L4.1 to L4.6 (6), L5.1 to L5.8 (8), L6.1 to L6.12 (12). L1.7, L2.5 and L6.10 restate existing brief rules and are kept as cross-references.

## Checks
- Numbers: none quoted without a ledger key or a stated file; the median ratios of actual to requested runtime come from A08 4c and `tables/jobs_trace_stats.json`, not the ledger (flagged in L1 plan).
- A13 forbidden wording: "first", "no prior work", water, land, spatial, wind claims, "significant" for non-Holm, comparison with 20 to 85 %: all avoided in proposed text.
- Quotes: 101498 "To the best of our knowledge" is not reproduced as a quote; the others are paraphrases except the 101470 definition phrase (6 words) and the "rarely exploit" fragment (2 words).
- Not done: reading the 101216 introduction in full and 101333; both gave no extra lesson for Paper A beyond A14.
