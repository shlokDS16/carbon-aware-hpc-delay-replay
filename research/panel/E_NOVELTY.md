VERDICT: E-NOVELTY done; contribution needs work (the measurement is unmatched, but the text still sells it as "gap known, we add inputs"; the X1 asymmetry and the runtime-over-forecast result are not yet in the contribution); 9 fixes

Sources read: A13_OVERLAP_AUDIT, A20_LIT_LICENCE, A15_REFERENCES.csv and A20_REFERENCES_ADD.csv (keys), 01_intro.tex, 02_related.tex, T1_related.tex, PANEL_DECISIONS D0016, ledgers TEST, TEST_posthoc (PH2), TEST_sens_x1, TEST_sens_s5. The ReBase and 101498 PDF text was not re-read; their facts come from A13 (line pointers md:Lnnn there). Numbers below are copied from ledger rows, in percentage points of run-now emissions (w weighting, S = 12 h) unless marked.

## 1. What Paper A measures that none of the compared works measures

Paper A is the only entry in which all four of these hold in one experiment: (a) a trained, past-only carbon forecaster, (b) per-job runtime information of three kinds (actual, user-requested walltime, history prediction), (c) a perfect-information arm built from the same planner, so a gap exists, and (d) real HPC job traces replayed on many grids with a frozen held-out year. Its distinct measured quantity is therefore the SPLIT of the perfect-information gap into a forecast part and a runtime part, plus the runtime-accuracy curve (X1). Where each work stops, using only the files:

| Work | Where it stops (source) | Missing relative to Paper A |
|---|---|---|
| ReBase 101470 | Oracle = realized wind and workload; gap by horizon 1.03 to 11.33 % wind-utilisation gap; unit tasks of equal energy, "no runtimes at all"; gap "attributed to forecast quality only" (A13 A3, md:L238-248, L841-845, L1195-1210) | Per-job runtime; a second information factor; grid carbon intensity; real HPC jobs |
| 101498 (Attenni) | Runtimes "assumed available"; forecast = true mix plus synthetic noise (MAE 0.05-0.2); no oracle arm; one week per season, 4-5 regions (A13 A1, md:L3043-3047, L1135-1160) | Trained forecaster, oracle arm, runtime input, gap |
| 101216 (Zhai 2025) | Injected wind-error sweep incl. MAE 0; aggregate workload; no per-job runtime (A13 A2) | Everything per-job; carbon signal |
| LiteCast | Real forecaster vs actual-intensity oracle on 50 regions and a KIT FH2 replay (3.4 % average saving, about 2 points below oracle); job length known, requested time not mentioned; weather and demand inputs; one year, no held-out year (A20 s1.1) | Runtime information; a second factor; past-only forecaster; held-out year |
| COAST | CEA-Curie log, actual runtimes, actual UK intensity, no forecast, 1 grid, 157 held-out windows (A20 s1.2) | Forecast, oracle gap, requested walltime |
| LACS | Elastic jobs, one grid (CAISO), simulated forecast error AND simulated length-prediction error (up to 60 %), swept separately in Sect. 5.4 and 5.5, two baselines; no trace (A20 s1.3) | Real requested walltimes, real traces, 2x2 grid with Shapley allocation, many grids. LACS is the nearest on the "two uncertainties" idea; it is PARTIAL on C1, C2, C3, C4 |
| Wiesner 2021, Sukprasert 2024 | Optimal or ideal vs injected-error forecasts; runtime treatment "not extracted" in the files (A13 s1) | Same as above; do not assert they ignore runtime |
| Tsafrir 2007, Mu'alem 2001 | Real requested vs actual runtimes and history predictors, but scored on waiting time and utilisation, no carbon (A20 s1.4, s1.5) | Carbon; forecast; oracle |

Three measured statements with no counterpart in the compared set (all from ledgers, all at S = 12 h, TEST year):
- M1 Retained share. The deployable arm D = lgbm|req keeps 0.33, 0.53, 0.38 of the oracle|act saving (PM100, F-DATA, KIT FH2; TEST shapley.retained_share 32.95, 52.76, 37.57 %).
- M2 Split. Gap = forecast term + runtime term + interaction (PM100 3.86 = 1.56 + 2.30 + 0.24; F-DATA 3.41 = 1.76 + 1.65 + 0.29; KIT FH2 2.51 = 1.03 + 1.48 + 0.34). The runtime term exceeds the forecast term on PM100 and KIT FH2 with the interval of (runtime minus forecast) excluding zero (PH2: 0.75 [0.67, 0.83]; 0.45 [0.42, 0.49]) and is not distinguishable on F-DATA (-0.11 [-0.29, 0.08], calendar interval). Per PANEL A3 this is stated per trace, as a descriptive allocation, never "runtime matters more" in general.
- M3 Curve. Saving as a function of the planner's runtime-estimate error (X1), with requested walltime and history prediction located against it (section 4).

Consequence for framing: the referee's strongest point ("ReBase and LiteCast already compare against an oracle") is answered by M2 and M3, not by M1. Today the Introduction foregrounds M1 and the 2x2 only in contribution 2. Reorder emphasis: the novelty is the second information factor and its split, with M1 as the setting.

## 2. Contribution bullets (replace the four in 01_intro.tex) and the gap sentence

Gap sentence (Introduction paragraph 4; replaces "is not reported in the studies we reviewed" sentence, keeps its bound):
"Among the studies compared in Section 2 (Table 1), forecast-versus-oracle gaps are reported with a single information factor, either forecast error or, in one elastic-job study on one grid, simulated job-length error, and none combines a trained past-only carbon forecast, user-requested walltimes and real HPC traces, or divides the gap between the two inputs."

Check against files: LACS has both factors synthetically on one grid (so "either ... or" is wrong if read as exclusive). Safer, single sentence to adopt:
"In the studies compared in Section 2, the gap between a deployable and a perfect-information scheduler is reported for forecast error alone, or for simulated job-length error on one grid; none of them divides it between a trained carbon forecast and the runtime a user actually requests on real HPC jobs."
Use this one. (It is bounded: "in the studies compared"; no "first".)

Contribution bullets (we voice; numbers stay out of bullets per SPEC point 6, they live in the abstract and Section 5):
1. We split the gap between a perfect-information and a deployable delay scheduler into a forecast term, a runtime term and their interaction, using a signal-by-runtime-estimate design with a descriptive Shapley allocation, on three real HPC job traces replayed on 42 U.S. balancing authorities, and report which term is larger per trace with intervals for the difference.
2. We measure the saving that survives realistic inputs, a trained past-only forecast and the user-requested walltime, in absolute (g CO2e per kWh) and relative terms and as a share of the same planner's perfect-information saving, in a pre-registered evaluation on a held-out year with calendar and synchronized-week intervals.
3. We map the cost of runtime error with a sweep of the planner's runtime estimate, show that over-estimates cost more than under-estimates of the same factor, and locate the requested walltime and a history-based prediction on that curve; we check that the forecast term does not come from an under-tuned model with a 100-trial tuned forecaster and simple baselines (exploratory, labeled).
4. We release code, derived data, the result ledger, the pre-registration and its checksum (Zenodo), so that every number in the paper traces to a ledger key.

Rationale: bullet 1 is the unmatched item (A13 C3 NONE, LACS PARTIAL only); 2 is C1/C5 as measurement at scale (A13 says explicitly it is a replication-with-real-forecaster, not novel in concept, so it is worded as "survives realistic inputs"); 3 is C2/C4 plus X1; 4 is the release (A13 s6: A2-A5 do not release code, A1 does; mention once).
Avoid in bullets: "first", "novel framework", "proposes a scheduler", "significant" outside H1-H3.

## 3. Table 1 improvements (T1_related.tex)

Current table has 10 columns of free text at \scriptsize; the difference is not visible at a glance. Keep it as Table 1 but add a compact second block (or replace the narrow text columns Statistics and Code, moving those to the supplement) with symbols that can be scanned. Proposed scan columns, filled only from A13/A20:

| Study | Runtime info used | Forecast | Oracle arm | Gap decomposed | Real jobs (HPC) | Held-out eval | Intervals |
|---|---|---|---|---|---|---|---|
| Wiesner 2021 | not reported | injected error | yes (optimal) | no | no (nightly, ML jobs) | no | no |
| Sukprasert 2024 | not reported | error scenario | yes (ideal) | no | no (synthetic) | no | yes (averages with intervals) |
| Radovanovic 2023 | not reported | production | no | no | no (fleet load) | measured in deployment | 95 % bands |
| Attenni 2026 (101498) | assumed known | noise-perturbed truth | no | no | no (Azure, Spark; not HPC) | no | no (mean, SD over 6 seeds) |
| Zhai 2025 (101216) | none | trained | no (error sweep) | no | no (aggregate load) | CV | no |
| Zhai 2026 ReBase (101470) | none (unit tasks) | trained | yes | by horizon only | no | chronological split | no (SD over 5 seeds) |
| Liow 2026 (101407) | duration given | fetched, not scored | no | no | no | no | CI over 3 profiles |
| Chen 2024 (100950) | none | none | no | no | no | no | no |
| Bostandoost 2024 (LACS) | simulated length error | simulated error | yes (online, offline) | two sweeps, no 2x2 | no | no | distributions |
| Feng 2026 (COAST) | actual runtime | none | no | no | yes (CEA-Curie) | yes (157 windows) | paired tests |
| Joseph 2025 (LiteCast) | length known | trained, weather inputs | yes | no | yes (KIT FH2 replay) | no | no found |
| This paper | actual, requested, history | past-only trained | yes | 2x2 Shapley | yes (3 traces) | frozen year | block bootstrap |

Rules for the cells: write "Not reported" where the text read gives no value (as now); the "Real jobs" column says "HPC" only for COAST, LiteCast and this paper (Attenni's Azure and Spark are real traces but not HPC, A13). For "Held-out eval" use only what A13/A20 show (COAST 157 held-out windows; Zhai 2026 chronological 0.8/0.2; LiteCast "no held-out year"). Add a footnote symbol convention and keep the existing note on preprint extractions. Order rows by theme (oracle-gap studies first), and bold the "This paper" row's cells that no other row has: "Gap decomposed = 2x2 Shapley" and "Runtime info = requested and history". Drop "Decision" and "Code" from the main table (to supplement); the Code column is the only place where release matters, and bullet 4 covers it.

Table fit: 8 symbol columns plus Study fit in \begin{table*} at \footnotesize without shrinking text below 7 pt.

## 4. Presenting X1 and the S5 check

X1 (tables/ledger_TEST_sens_x1.csv, results exploratory, S = 12 h, w weighting; saving in % of run-now; keys sens.x1.<trace>.w.S12.saving.<signal>|<arm>):

| Trace, signal | m0.25 | m0.5 | act | m2 | m4 | m8 | req | pred |
|---|---|---|---|---|---|---|---|---|
| PM100 oracle | 3.24 | 4.34 | 5.75 | 3.92 | 2.87 | 2.10 | 3.33 | 4.18 |
| PM100 lgbm | 2.33 | 3.17 | 4.08 | 2.78 | 2.21 | 1.92 | 1.90 | 2.93 |
| F-DATA oracle | 4.91 | 5.92 | 7.22 | 4.89 | 3.64 | 2.24 | 5.42 | 5.92 |
| F-DATA lgbm | 3.71 | 4.46 | 5.31 | 3.41 | 2.74 | 1.93 | 3.81 | 4.34 |
| KIT oracle | 2.25 | 2.90 | 4.02 | 2.30 | 1.53 | 1.18 | 2.37 | 2.65 |
| KIT lgbm | 1.68 | 2.12 | 2.82 | 1.63 | 1.24 | 1.10 | 1.51 | 1.86 |

What the ledger supports on all three traces (not a PM100 result only):
1. Peak at the true runtime: the act arm is the maximum in all six rows.
2. Asymmetry: for every one of the 12 pairs (3 traces x 2 signals x factors 2 and 4), the under-estimate by factor k saves more than the over-estimate by k (e.g. F-DATA oracle 5.92 vs 4.89 at k = 2, 4.91 vs 3.64 at k = 4; smallest margin PM100 lgbm at k = 4, 2.33 vs 2.21). Wording: "Under-estimating a job's runtime by a factor k cost less saving than over-estimating it by the same factor in all twelve comparisons". Do NOT call it significant: the arm intervals are calendar intervals for each arm (saving_lo/hi) and no paired interval for the m0.25-minus-m4 difference exists in the ledger; PM100 lgbm k = 4 intervals nearly touch (2.23 to 2.42 vs 2.12 to 2.31). Report the point estimates and say "direction holds in 12 of 12". If a difference interval is wanted, it needs a new one-line post-hoc run (flag as post-hoc, own ledger).
3. Link to the data: requested walltime over-states runtime on the three traces (median runtime is 14.3, 30.6, 17.8 % of the request, intro) so the requested-walltime arm sits on the costly, over-estimate side; the History prediction has median log error near 0 (logerr_median.pred 0.01, 0.04, 0.00).
4. Caveat to state: req is not a uniform multiple of the actual runtime. It saves more than a uniform multiplier with the same median error (e.g. PM100 oracle|req 3.33 at median log error 1.95 vs m4 2.87 at 1.39; F-DATA oracle req 5.42 vs m2 4.89 although req's median log error is 1.19 > 0.69), so the multiplier curve is a reference line, not a model of requested walltime. Say "req and pred are marked at their measured error, not placed on the curve". The log-normal variant ln is on the figure only if its matching rule is stated; ledger contrasts say requested walltime is worse than matched noise on PM100 (lgbm req minus ln -0.65 [-0.72, -0.58]) and similar elsewhere, so no general claim about "worse than random noise".
5. How it extends the contribution: LACS sweeps simulated length error on one grid and elastic jobs; X1 sweeps the planner's estimate error on real jobs on 42 grids with the same planner that is scored against the oracle. That is the "operator-facing" form of M2. State: "the replay suggests that, when a runtime estimate must err, erring low costs less than erring high", as a hypothesis (PANEL A4), plus the mechanism note only if it is tested; none is in the ledger, so no mechanism claim (do not say "because the planner picks later windows").
6. Status label: exploratory (P4_PLAN_X), post-freeze, not confirmatory; keep one figure panel in the main text (PANEL B).

S5, "is the forecast term just a weak model?" (tables/ledger_TEST_sens_s5.csv; 100 Optuna trials on TRAIN only, objective 1-24 h MAE):
- Validation MAE 1-24 h: 25.50 (frozen lgbm) vs 25.34 (tuned), 0.6 % lower; the day-persistence baseline is 31.46 (sens.s5.val_mae_1_24).
- Result at S = 12 h, w, tuned vs frozen (pp): PM100 lgbm|req 1.96 vs 1.90, forecast term 1.50 vs 1.56, runtime term 2.29 vs 2.30; F-DATA 3.90 vs 3.81, 1.68 vs 1.76, 1.64 vs 1.65; KIT FH2 1.55 vs 1.51, 1.00 vs 1.03, 1.47 vs 1.48. Retained share moves by 1 point (32.95 to 34.02; 52.76 to 54.03; 37.57 to 38.52).
- Sentence: "Tuning the forecaster on the training years lowered validation MAE by 0.6 percent and changed the forecast term by at most 0.08 percentage points on the three traces, so the forecast term is not an artifact of an under-tuned model; the run-time term was unchanged to the second decimal." Careful: this shows insensitivity to tuning within LightGBM, not that no other model class could close the gap; say so, and add the caveat that the oracle-minus-forecast term is bounded by the information in past intensity (a different feature set, such as weather or day-ahead grid forecasts as in LiteCast, is out of scope). Do not say "the forecast cannot be improved".
- Do not present S5 as a rescue of the forecast term; present it as the reason the runtime term is not inflated by a weak forecaster (a weaker forecast would raise the forecast term, so the observed runtime-over-forecast ordering on PM100 and KIT FH2 is conservative with respect to tuning).

## 5. Remaining overlap risks and the exact sentences

R1 ReBase and LiteCast "already compare against an oracle" (A13 C1 SUBSTANTIAL for ReBase as concept; LiteCast SUBSTANTIAL in A20). Related work, Position paragraph, replace the sentence "The forecast-to-oracle gap is known...":
"A forecast-to-oracle gap is already reported for wind-powered unit tasks by forecast horizon [ReBase] and for a lightweight forecaster on 50 regions with a KIT FH2 replay [LiteCast]; both give the scheduler the job's length or no length at all, and neither divides the gap between inputs, which is what this study adds."
Fix needed: "both give the scheduler the job's length or no length" is clumsy; use: "ReBase uses unit tasks without runtimes and LiteCast treats job length as known; neither divides the gap between inputs, which is what this study adds." (verified in A13 A3 and A20 s1.1).

R2 LACS also studies forecast error and length error (A20 s1.3 marks C1 to C4 all PARTIAL). The current Related-work sentence ("Three works outside this journal bound...") is accurate but the Position paragraph says "we did not find an evaluation that combines a past-only carbon forecast, requested walltimes and real HPC traces". Keep, and add after it: "LACS varies simulated forecast error and simulated length error separately for elastic jobs on one grid; the present study replaces both with a trained forecaster and recorded requested walltimes, and crosses them." (verified wording from A20; "crosses" = the 2x2.)

R3 "42 grids, real traces" (Attenni, LiteCast). Add in Related work 2.2 after the Attenni sentences: "Their traces are real but not HPC batch jobs, arrivals are synthetic, and the horizon is one week per season." (A13 s2 point 2.) No statement about the field.

R4 Tsafrir/Mu'alem: runtime prediction is not new. Sentence already in section 2.3 ("These works target waiting time and utilization, not carbon"). Add in Discussion: "The history predictor is the last-two-jobs mean of Tsafrir et al.; its value here is as an input to a carbon planner, not as a predictor." (A20 s1.4). Check the exact predictor definition in Methods (A20 says mean of the user's last two jobs); if Paper A's predictor differs, say "a history predictor in the spirit of".

R5 Statistical positioning versus Liow (CI over n = 3). Already in Related work; keep that sentence and add in Discussion: "The 42 balancing authorities are a fixed set, not a sample of grids; intervals are over calendar blocks (PREREG s.6)." (A13 s2 point 3).

R6 Representativeness and counterfactual (editor P1/P2): US grids plus non-US traces. Already in the Introduction limits; keep one sentence in Discussion.

R7 Do not compare Paper A's 1.5 to 3.8 % savings with 20 to 85 % (Attenni), 70 % (Chen), 75.7 % (Liow), or the 3.4 % LiteCast KIT number without the setting note. If the comparison with LiteCast is made, use: "LiteCast reports an average 3.4 percent saving on a KIT FH2 replay [A20]; the settings differ in slack rule (recorded waiting time against a fixed 12 h), grids (50 against 42) and inputs, so the numbers are not comparable" (A20 s1.1: slack assigned from the trace's waiting time; do not assert anything beyond that).

R8 Venue status of COAST (arXiv, venue unconfirmed) and LiteCast (arXiv): keep "preprint", as in the current text.

## 6. Fix list (9)

1. Replace the gap sentence in Introduction paragraph 4 with the bounded one in section 2.
2. Replace the four contribution bullets with the section 2 text; keep nominal or "we" consistently ("we" already used in the paper).
3. Reorder the Introduction emphasis: lead the contributions with the gap decomposition and runtime-versus-forecast per trace, M1 second.
4. Introduction paragraph 2 closing sentence ("The distance ... is therefore already known; ReBase reports it ...") add LiteCast to it, so the referee does not find the overlap for you.
5. Position paragraph in 2.4: replace with R1 + R2 sentences; add R3 in 2.2.
6. T1: add the scan columns of section 3; move Decision and Code to the supplement; bold the unmatched cells.
7. Add the X1 asymmetry and the "req and pred marked at measured error" caveat (section 4 points 2 and 4) as a result paragraph and one panel; label exploratory; add a paired-difference interval only if a post-hoc run is approved.
8. Add the S5 sentence of section 4 to Robustness; fold in the caveat that tuning within LightGBM only.
9. In Discussion add R4, R5, R7 sentences; state per-trace that the runtime term exceeds the forecast term on PM100 and KIT FH2 only (PH2 intervals), and that F-DATA is not distinguishable.

Unverified and to confirm before print: (i) Tsafrir predictor definition vs Paper A's pred arm (Methods); (ii) Table 1 "Held-out eval" and "Intervals" cells for Wiesner, Sukprasert, Radovanovic come from preprint extractions (A13 note) and stay marked as such; (iii) the KIT FH2 slack rule difference in R7 rests on A20 s1.1 only.
