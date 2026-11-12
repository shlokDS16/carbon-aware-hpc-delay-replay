VERDICT: E-IMPACT done; 8 framing fixes; 5 light computations proposed

# E-IMPACT, Paper A (SUSCOM): the honest case that the effect matters

Expert E-IMPACT, 2026-11-12. Read: paper/sections 00, 01, 05, 06, 07; research/PANEL_DECISIONS.md; A09, A19; ledgers (grep and csv reads only); tables/secondary_retained_share.csv, x1_runtime_sweep.csv, jobs_trace_stats.json; data/derived/jobs_*.parquet (read-only sums); A13, A14, LESSONS (grep). No frozen result is touched, no TEST re-run.

Status vocabulary: PRE = pre-registered (H1 to H3 confirmatory on PM100, relative savings on all traces), SEC = secondary, POST = post-hoc (PH ledgers), NEW = needs the computation in section 2.
Unit note: 1 g CO2e per kWh = 1 kg per MWh = 1 t per GWh. Say this once in Section 5.1; it makes every g/kWh figure a ready-made scale factor.

## 0. The core diagnosis

The effect looks small for three fixable reasons, all of presentation:
1. The paper leads with a share of run-now emissions (1.9, 3.8, 1.5 %). That share is diluted by the long, flat tail of each grid's intensity and by the carbon-weighted pooling over 42 BAs, most of them flat. It is the least decision-relevant way to state the result.
2. The ceiling is not named. The perfect-information arm itself saves only 5.75, 7.22, 4.02 % at 12 h. A reader who sees "1.9 %" without "ceiling 5.75 %" reads failure; with the ceiling it reads "a third of what is physically available on these grids at this slack".
3. The Discussion currently ends the effect-size story with "The absolute effect is modest" (06_discussion, end of Implications). Remove that sentence; it concedes the referee's point without the evidence below.

## 1. The strongest honest case, item by item

Keys: TEST.* from tables/ledger_TEST.csv; secondary keys from ledger_TEST_secondary.csv; posthoc.* from ledger_TEST_posthoc.csv. T in {PM100, FDATA, KIT_FH2}. Numbers read on 2026-11-12.

### 1.1 Retained share against the ceiling (decision-relevant quantity)
- D retained share at 12 h: 0.33, 0.53, 0.38 (key TEST.T.w.S12.shapley.retained_share; intervals post-hoc, posthoc.PH1.* retained share: PM100 31.7 to 34.2 %, FDATA 49.7 to 55.5 %, KIT 36.9 to 38.2 %). Status: SEC/POST (share), PRE (numerator).
- History-based prediction retained share: 0.509, 0.602, 0.463 (secondary key TEST.T.w.S12.retained.lgbm_pred; PM100 0.509 read from A09). Status: SEC. So a simple predictor from the user's last two jobs lifts the retained share from "a third to a half" to "about a half to three fifths".
- Sentence: "On the same grids, the same planner with perfect information is the ceiling; the deployable arm keeps 0.33 to 0.53 of it, and a runtime prediction from the user's recent jobs keeps 0.46 to 0.60."
- Guard: the oracle is the same heuristic, not a global optimum (already Limitation C); say "ceiling of this planner".

### 1.2 Absolute effect per job and per kWh (already pre-computed, POST, PH4)
Read at S12 (g CO2e per kWh / per job; calendar interval in brackets):
- D: PM100 6.64 [6.32, 6.97] / 47.1 [44.9, 49.4]; FDATA 13.20 [12.09, 14.27] / 126.5; KIT_FH2 5.27 [5.14, 5.41] / 27.4. Keys posthoc.PH4.T.w.S12.lgbm|req.g_per_kwh.est and .g_per_job.est.
- Oracle: 20.14, 25.03, 14.02 g/kWh (posthoc.PH4.T.w.S12.oracle|act.g_per_kwh.est).
- Run-now: 350.1, 346.6, 349.2 g/kWh (posthoc.PH4.T.w.S12.runnow_g_per_kwh.est).
- Sentence: "At 12 h of slack the deployable arm removes 6.6, 13.2 and 5.3 g CO2e from every kWh of job energy, that is 6.6, 13.2 and 5.3 t CO2e per GWh."
- Why it matters to a referee: g/kWh is the cross-trace comparable; the three run-now means coincide (347 to 350), so the traces differ in saving, not in baseline.

### 1.3 Annual scale (needs computation C1; inputs exist)
- Run-now annual energy of a trace: not in any ledger. File data/derived/jobs_<trace>.parquet gives analyzed-job energy_kwh and submit_utc (main filter COMPLETED, r_act >= 1 min, 0 < r_req <= 72 h). I read it: PM100 768,337 kWh over 159 days of submit span (5 May to 13 Oct 2020), which is 1.76 GWh per year-equivalent; F-DATA 26.09 GWh over five sampled, non-contiguous months (cannot be annualized cleanly); KIT FH2 has no energy (1 kW assumed).
- Arithmetic (stated computation, not yet keyed): PM100 trace year-equivalent saving = 1.76 GWh x 6.64 t/GWh = 11.7 t CO2e at 12 h (oracle 35.5 t at 20.14 t/GWh). This is small because the PM100 release is a power-instrumented subset of one system, so do NOT headline it.
- Headline instead the unit scenario: per MW of continuous job power, one year is 8.76 GWh, so D removes 58, 116 and 46 t CO2e per MW-year (6.64, 13.20, 5.27 x 8.76) and 10 MW is 581, 1,157 and 461 t. Say the 10 MW and full-load figures are an illustrative scaling assumption (a facility's real mean load factor and share of delay-tolerant jobs set the real value), and the saving applies only to job energy that is delay-tolerant within 12 h.
- Status: NEW/POST. Sentence in 5.1 below.

### 1.4 Larger savings at 24 h slack (PRE relative; g from POST)
- D at 24 h: 2.68, 5.67, 2.20 % (TEST.T.w.S24.saving.lgbm|req = 0.0268, 0.0567, 0.0220); in g/kWh 9.37 [8.98, 9.74], 19.65 [18.49, 20.79], 7.68 [7.45, 7.90] (posthoc.PH4.T.w.S24.lgbm|req.g_per_kwh.est); per job 66.5, 188.2, 40.0 g.
- Oracle at 24 h: 8.62, 11.06, 6.22 % (TEST.T.w.S24.saving.oracle|act); history prediction at 24 h: 4.26, 6.58, 2.95 % (TEST.T.w.S24.saving.lgbm|pred).
- Slack curve D, PM100: 0.26, 0.79, 1.90, 2.68 % at 2, 6, 12, 24 h. Doubling the slack from 12 to 24 h raises D by 1.41, 1.49, 1.46 times (keys above, ratios by arithmetic). Status: SEC (slack is a registered grid cell; relative values are registered outputs, no p-values).
- Context check to add (one sentence, one source): A13 records that Attenni et al. report temporal-only savings of 6 to 12 % at delay tolerances up to 48 h (A13 md:L1414-1417, L136). Paper A's oracle at 24 h (6.2 to 11.1 %) falls inside that band, which shows the replay environment is not unusually poor in variation. Frame as a consistency check, not a comparison (A13 and LESSONS L1.4 forbid numeric headline comparison); needs one confirming read of that PDF before it is written.
- Sentence: "With a day of slack the deployable arm removes 9.4, 19.7 and 7.7 g per kWh."

### 1.5 High-variation and solar-heavy grids (SEC, point estimates; computation C2 adds intervals)
- Source: tables/secondary_retained_share.csv (unit = BA, class = all, weight = w). Per-BA D saving is the column saving_lgbm_req. These per-BA values are in the csv, NOT in ledger_TEST_secondary.csv (the ledger keeps only pooled, class and trace rows), so they have no key yet; computation C2 keys them.
- PM100 at 12 h: median BA 1.63 %, 12 of 42 BAs at or above 3 %, best BA (PNM) 6.49 % against oracle 21.2 %; at 24 h median 2.52 %, 18 of 42 at or above 3 %, 7 at or above 5 %, PNM 9.64 %. F-DATA at 12 h: median 3.34 %, 22 of 42 at or above 3 %, 14 at or above 5 %, PNM 16.0 %, IID 11.5 %; at 24 h PNM 22.0 %, IID 15.1 %. KIT FH2 at 12 h: median 1.37 %, PNM 4.88 %. No BA has a negative D saving at 12 h in any trace (SPA, constant intensity, has 0).
- Mechanism evidence (already in the paper): across BAs oracle saving rises with median daily range (Spearman 0.82 PM100; keys in ledger_TEST_secondary, spearman rows) and runtime penalty with solar share (0.87).
- The pooled figure is carbon-weighted (Limitation F), so it is dominated by flat, high-carbon grids. A site on a volatile solar-heavy grid should read the per-BA column, not the pooled one. Sentence: "On the one third of BAs with the largest daily swing, the deployable saving at 24 h exceeds 5 % on PM100 and reaches 22 % on F-DATA in the best case."
- Careful: "one third" is not a count I verified; use the counts above (7 of 42 BAs at or above 5 % at 24 h on PM100). Per-BA point estimates carry sampling noise (each BA has about 60,000 replayed jobs, 3 alignments); wait for C2 intervals before printing a best-case BA in the abstract. Never print a BA name as a recommendation.

### 1.6 Value of better runtime information, in g per job (POST, from PH4 differences; intervals via C3)
Point differences from the PH4 keys (S12):
- H2 (actual minus requested runtime, lgbm): 54.3 g/job (PM100; 7.64 g/kWh), 49.9 g/job (FDATA; 5.21), 23.8 g/job (KIT; 4.58). Exact runtimes would more than double D on PM100 (14.28 vs 6.64 g/kWh).
- H3 (history prediction minus requested): 25.7 g/job (PM100; 3.61 g/kWh), 17.8 (FDATA; 1.85), 6.4 (KIT; 1.23).
- As a share of D's own saving: the prediction raises D by 54 %, 14 % and 23 % (72.77/47.12, 144.2/126.5, 33.83/27.44; arithmetic on posthoc.PH4.T.w.S12.lgbm|pred and lgbm|req .g_per_job.est). H3 is PRE on PM100 (1.03 pp, p < 0.0005); the g and ratio forms are POST.
- Why this is the most telling reframing: in pp the prediction adds "1.03 pp"; as a ratio it raises the saving by about half on the primary trace. The same information costs one log of past runtimes.
- Sentence: "A runtime prediction from the user's last two jobs raises the deployable saving by 54 % on PM100 (from 47 to 73 g per job), 14 % on F-DATA and 23 % on KIT FH2."

### 1.7 Against simple rules (PRE for D; baseline rows are secondary)
At 12 h, PM100 (TEST.PM100.w.S12.saving.<arm>): D 1.90 %, night rule 0.29 %, persistence|req -0.20 %, seasonal naive day|req 0.96 %, profile7|req 1.11 %. In g/kWh: D 6.64, profile7|req 3.88, night 1.00 [0.77, 1.24], persistence|req -0.70 [-0.79, -0.61] (posthoc.PH4.PM100.w.S12.<arm>.g_per_kwh.est). So D is 1.7 times the best simple past-only signal (6.64 / 3.88) and 6.6 times the night rule on PM100.
- Harm: the night rule is negative at 24 h on all three traces (-0.40 %, -2.23 %, -0.65 %; TEST.T.w.S24.saving.night) and on F-DATA at 12 h (-0.24 %); persistence|req is negative on all three traces at every slack (e.g. S12: -0.20, -0.46, -0.14 %). Persistence delays jobs 2.4 h and increases emissions by 0.70 g per kWh on PM100 (interval excludes zero). Emphasize: a naive carbon-aware rule can make emissions worse; the effect of the information is not only a gain, it is the difference between a gain and a loss.
- Sentence: "Simple rules do not substitute: a night-only rule saves 1.0 g per kWh at best (PM100, 12 h) and costs emissions at 24 h on every trace, and persistence increases emissions on every trace and slack."
- Cost-effectiveness (POST, PH7): D saves 0.35 pp per hour of delay on PM100 vs 0.06 pp for the night rule (posthoc.PH7.PM100.w.S12.lgbm|req.saving_per_delay_hour = 0.00345; night = 0.00065), 5.3 times the night rule per hour of waiting. Mean delay 5.5 h (D) vs 4.4 h (night).

### 1.8 Reliability and what a small mean hides (computation C4, optional)
A 1.9 % mean saving that is positive in most BA-weeks is a different object from one that is positive on average and negative half the time. No arm-level loss is reported for D; per-BA, no BA is negative at 12 h. C4 turns that into a number.

### 1.9 What NOT to claim
- Do not annualize PM100 to a full-system figure (subset trace, warm-season span).
- Do not present the best-BA values as expected savings; they are post-selection maxima.
- Do not state "x t CO2e avoided in the real world": average (not marginal) signal, no queue, foreign traces (Limitations A, B, D).
- Do not compare headline percentages with 20 to 85 % spatial studies (A13, LESSONS L1.4).

## 2. Light post-hoc computations (ranked; each labeled post-hoc; none alters frozen results)

All write to a new ledger (e.g. tables/ledger_TEST_posthoc_impact.csv) with a new PREREG_DEVIATIONS row; import frozen analyze.py/posthoc_inference.py unchanged; assert reproduction of existing point estimates to 1e-12 first, as A19 did.

C1 (rank 1). Scale table: t CO2e per GWh, per MW-year, per year-equivalent of the PM100 trace.
- Input: posthoc.PH4.T.w.S{12,24}.<arm>.g_per_kwh.{est,lo,hi}; data/derived/jobs_PM100.parquet (energy_kwh, submit_utc, main filter as in prep_jobs); jobs_FDATA.parquet (energy by month); state KIT as not available.
- Formula: t_per_GWh = g_per_kWh (identity); t_per_MWyear = g_per_kWh x 8.76; trace_year_t = g_per_kWh x E_trace_kWh x 365 / span_days / 1e6 (PM100 only, flagged subset, warm-season span). Intervals are the frozen PH4 intervals scaled by the same constant (the scale is not random).
- Output keys: posthoc.C1.T.w.S{12,24}.<arm>.t_per_GWh.{est,lo,hi}; .t_per_MWyear.*; posthoc.C1.PM100.trace_energy_kwh, .span_days, .trace_year_t.<arm>.*; arms lgbm|req, lgbm|pred, oracle|act.
- Run time: under 10 s. Referee value: answers "so what, in tonnes" with units that transfer to any site; guard rails in 1.3.

C2 (rank 2). Per-BA absolute savings with intervals and the spread of the pooled figure.
- Input: results/ per-BA aggregates already used by src/secondary.py (results/_secondary_cache.pkl) and the frozen per_ba_boot function (seed 7 + 100 + j, B = 500, 50 weekly blocks, as PH3).
- Formula: per BA b, D_b = saving of lgbm|req relative to the BA's run-now emissions, with 95 % percentile interval; also per-BA run-now mean intensity (g/kWh) and D in g/kWh = D_b x run-now_b; summary: median over BAs, number of BAs with lower bound above 0, number with D above 3 % and above 5 %, unweighted mean over BAs (to contrast the carbon-weighted pooled value); S12 and S24; arms lgbm|req, lgbm|pred, oracle|act.
- Output keys: posthoc.C2.T.w.S{12,24}.ba.<BA>.D.{est,lo,hi}, .D_g_per_kwh.est, posthoc.C2.T.w.S{12,24}.summary.{median,n_lo_gt0,n_ge3pct,n_ge5pct,unweighted_mean}.
- Run time: about 30 s (same cost as PH3). Referee value: turns the "which grids" question (1.5) from a point-estimate csv into a keyed, bounded result; tests the Limitation F worry that the pooled value is dominated by flat grids.

C3 (rank 3). Absolute contrasts with intervals: value of information and of the forecaster in g.
- Input: the PH4 energy-extended bootstrap (reproduces the frozen draws exactly, per A19).
- Formula: for contrast K in {H2 = lgbm|act - lgbm|req, H3 = lgbm|pred - lgbm|req, PH6 = lgbm|req - profile7|req, D - night, D - persistence|req}: g/kWh and g/job (same draws, difference of per-draw savings x run-now), plus the relative uplift ratio K_pred = lgbm|pred / lgbm|req - 1 with percentile interval.
- Output keys: posthoc.C3.T.w.S{12,24}.<K>.{g_per_kwh,g_per_job,ratio}.{est,lo,hi}.
- Run time: about 30 s. Referee value: the 54 % uplift (1.6) and "1.7 times the best simple rule" (1.7) become intervalled statements instead of ratios of two point estimates.

C4 (rank 4). Reliability of the saving: share of BA-weeks (and of BA-days) with positive saving, and the 5th percentile of the weekly saving.
- Input: per-block (7-day, per BA) saved aggregates that the bootstrap resamples (verify the layout in src/analyze.py before writing; if only day sums are stored, use days).
- Formula: for each BA-week block, s = (E_runnow - E_D) / E_runnow computed from block carbon sums; report fraction of blocks with s > 0, with s > 1 %, the 5th percentile and the mean over the worst 10 % of blocks, for D and for persistence|req and night as contrast.
- Output keys: posthoc.C4.T.w.S12.D.{frac_pos,frac_gt1pct,p05,worst10_mean}.
- Run time: under 30 s. Referee value: shows the mean saving is not carried by a few lucky weeks, and that persistence and the night rule lose in a visible share of weeks. If the stored blocks cannot support it, drop C4 (it is the only item with an unverified input layout).

C5 (rank 5). Slack-equivalence table (information value expressed as extra slack).
- Input: existing keys only, TEST.T.w.S{2,6,12,24}.saving.{lgbm|req,lgbm|pred,oracle|act}.
- Formula: for each arm, linear interpolation of saving against log2(slack) over the four registered slacks, then the slack at which lgbm|pred (and lgbm|req) reaches the oracle|act saving at 6 h, if inside 2 to 24 h; else report "outside the registered range". Example read from keys: on PM100 oracle at 6 h is 2.98 % while D at 24 h is 2.68 %, so D does not match it even with four times the slack, but lgbm|pred at 12 h (2.93 %) is within 0.05 pp of it; on F-DATA and KIT the equivalence differs, so the table must give all three traces and no general statement.
- Output keys: posthoc.C5.T.w.<arm>.slack_to_match_oracle6h.
- Run time: under 5 s. Referee value: expresses information value in the unit an operator controls (hours of tolerated delay). Interpolation is crude with four points; label descriptive; drop if the paper is over length.

## 3. Exact rewrites (placeholders <<key|fmt>>; formats pct1, pct2, pp2, .1f, int as already used in the templates)

### 3.1 Abstract sentences 1 to 3 (replace current sentences 1 to 3; keep the later sentences; recount words after the swap: the new block is about 82 words against about 70 now, so cut the clause "(PM100, F-DATA and KIT FH2)" if the count nears 250)
1. We replayed three real high-performance computing (HPC) job traces (PM100, F-DATA and KIT FH2) on 42 U.S. balancing authorities over a held-out year, giving a delay planner only a past-only forecast of carbon intensity and the requested walltime.
2. With up to 12 h of slack, delaying jobs saved <<posthoc.PH4.PM100.w.S12.lgbm|req.g_per_kwh.est|.1f>>, <<posthoc.PH4.FDATA.w.S12.lgbm|req.g_per_kwh.est|.1f>> and <<posthoc.PH4.KIT_FH2.w.S12.lgbm|req.g_per_kwh.est|.1f>> g CO$_2$e per kWh of job energy, equal to <<TEST.PM100.w.S12.H1_deployable_saving.est|pct1>>, <<TEST.FDATA.w.S12.H1_deployable_saving.est|pct1>> and <<TEST.KIT_FH2.w.S12.H1_deployable_saving.est|pct1>> of run-now emissions (pre-registered), and <<posthoc.PH4.PM100.w.S24.lgbm|req.g_per_kwh.est|.1f>>, <<posthoc.PH4.FDATA.w.S24.lgbm|req.g_per_kwh.est|.1f>> and <<posthoc.PH4.KIT_FH2.w.S24.lgbm|req.g_per_kwh.est|.1f>> g with 24 h.
3. The same planner given perfect information is the ceiling, and the deployable policy kept <<TEST.PM100.w.S12.shapley.retained_share|.2f>>, <<TEST.FDATA.w.S12.shapley.retained_share|.2f>> and <<TEST.KIT_FH2.w.S12.shapley.retained_share|.2f>> of it, rising to <<TEST.PM100.w.S12.retained.lgbm_pred|.2f>>, <<TEST.FDATA.w.S12.retained.lgbm_pred|.2f>> and <<TEST.KIT_FH2.w.S12.retained.lgbm_pred|.2f>> when a runtime prediction from the user's recent jobs replaced the requested walltime.
(Check the build resolves secondary-ledger keys in the abstract; if it only reads ledger_TEST.csv and posthoc, route the retained.lgbm_pred keys through the secondary ledger loader used by 05_results. The pre-registration, "measurement, no new scheduler" and "post-hoc conversion" statements stay in the later abstract sentences; the abstract must still say that the per-kWh figures are a post-hoc conversion, as the current sentence 3 does.)

### 3.2 First contribution bullet (no numbers, per LESSONS L2.4)
A pre-registered measurement, on three real HPC traces and 42 U.S. balancing authorities with a held-out year, of the carbon saving that delay scheduling realizes with only a past-only forecast and the requested walltime, stated per kWh and per job, as a share of the perfect-information saving, and beside the saving of a history-based runtime prediction and of simple night-only and persistence rules.

### 3.3 Discussion paragraph "What the size of the effect means" (insert as a new subsection after "Implications as hypotheses", replacing the sentence "The absolute effect is modest..."; about 190 words)
\subsection{What the size of the effect means}\label{sec:disc:size}
Per unit of job energy the saving is large enough to scale. The deployable policy removes <<posthoc.PH4.PM100.w.S12.lgbm|req.g_per_kwh.est|.1f>>, <<posthoc.PH4.FDATA.w.S12.lgbm|req.g_per_kwh.est|.1f>> and <<posthoc.PH4.KIT_FH2.w.S12.lgbm|req.g_per_kwh.est|.1f>> t CO$_2$e per GWh at 12 h of slack, and <<posthoc.PH4.PM100.w.S24.lgbm|req.g_per_kwh.est|.1f>>, <<posthoc.PH4.FDATA.w.S24.lgbm|req.g_per_kwh.est|.1f>> and <<posthoc.PH4.KIT_FH2.w.S24.lgbm|req.g_per_kwh.est|.1f>> t at 24 h, so a system drawing 1 MW of delay-tolerant job power for a year (8.76 GWh) would see <<NEW:posthoc.C1.PM100.w.S12.lgbm|req.t_per_MWyear.est|.0f>> to <<NEW:posthoc.C1.FDATA.w.S12.lgbm|req.t_per_MWyear.est|.0f>> t on these replays; this is an illustrative scaling, not a facility estimate. The share of run-now emissions looks small because each grid's intensity varies around a large mean; the perfect-information ceiling is only <<TEST.PM100.w.S12.saving.oracle|act|pct1>>, <<TEST.FDATA.w.S12.saving.oracle|act|pct1>> and <<TEST.KIT_FH2.w.S12.saving.oracle|act|pct1>>, so the deployable policy keeps a third to a half of what the planner can reach at this slack. Rules that avoid forecasts do not close the gap: persistence increases emissions, and the night-only rule is lower than the deployable policy on every trace. The saving is larger on grids with a large daily swing (<<NEW:posthoc.C2.PM100.w.S24.summary.n_ge5pct|int>> of 42 BAs above 5 % at 24 h on PM100) and a runtime prediction raises the PM100 saving by <<NEW:posthoc.C3.PM100.w.S12.pred_uplift.ratio.est|pct0>>. All of this holds as a bound under free capacity and average intensity, not as avoided marginal emissions.
(Until C1 to C3 run, use the point values given in sections 1.3 to 1.6 and mark the NEW keys pending; do not print the NEW numbers by hand.)

### 3.4 One highlight (Elsevier limit 85 characters including spaces; 80 characters at the 12 h values)
Past-only delay saves <<posthoc.PH4.KIT_FH2.w.S12.lgbm|req.g_per_kwh.est|.1f>> to <<posthoc.PH4.FDATA.w.S12.lgbm|req.g_per_kwh.est|.1f>> g CO2e per kWh of HPC job energy at 12 h slack
(Replace highlight 2 or 5 with it; keep the highlights.tmpl.txt pair in sync, as build_paper.py checks. "5.3 to 13.2" is KIT FH2 to F-DATA; PM100 6.6 lies inside. A second candidate, 80 characters: "Runtime prediction lifts the deployable saving by 14 to 55 % on three HPC traces", valid only after C3 prints the ratio with the keys above.)

### 3.5 Other framing fixes (the 8 counted in the verdict)
1. Results 5.1 (main result): lead with g per kWh and t per GWh, then the percentage, then the ceiling; move the sentence "Both would limit what the replay can recover" after the ceiling.
2. Delete "The absolute effect is modest" (Discussion, Implications) and insert subsection 3.3.
3. Abstract and Conclusion: add the 24 h values and the prediction retained shares (3.1); conclusion has no new numbers by SPEC, so only repeat keys already in the abstract.
4. Results Heterogeneity: add the per-BA breakdown of the deployable saving (median BA, count of BAs at or above 3 % and 5 %) beside the existing oracle and penalty correlations (needs C2).
5. Results 5.1 Baseline ladder: add the g per kWh column for night, persistence and profile7 (keys in 1.7) and the harm sentence (night negative at 24 h on all three traces, persistence on all).
6. Discussion Implications: replace the pp form of the prediction recovery by the g per job and ratio form (1.6), keeping the pp in Results.
7. Discussion Comparison: add the single consistency sentence (oracle at 24 h lies in the 6 to 12 % temporal-only band of Attenni et al.) after confirming the number in the source; no other numeric comparison.
8. Method 4.x: state the unit identity (1 g/kWh = 1 kg/MWh = 1 t/GWh) and that the 8.76 GWh per MW-year scale is arithmetic, with the status of each new number (PRE/SEC/POST) in the registry table.

## 4. Titles (<= 16 words, finding-led, flowing, no question, no negative, true on all three traces; the owner approves; PANEL rule A3: no "jointly determine")
T1 (16 words): Past-only carbon-aware delay of HPC jobs keeps a third to a half of its ideal saving
- True at S = 12 h on all three traces (0.33, 0.53, 0.38). Risk: at 2 h the share is 0.25 on PM100, so the title is slack-specific; the abstract states the slack. "Ideal" must be defined as the same planner with perfect information; "past-only" is shorthand for past-only forecast plus requested walltime.
T2 (16 words): Replayed HPC jobs delayed on a past-only forecast save 5 to 13 g CO2e per kWh
- Numbers must come from keys (posthoc.PH4.T.w.S12.lgbm|req.g_per_kwh.est: 6.6, 13.2, 5.3; "5 to 13" is the rounded range) and the title file should be generated or checked by build_paper.py. Risk: omits the walltime input and the slack, and a numeric title is rare in SUSCOM (A14: median 14 words, 0 of 16 finding-led); prefer T1 for editor reaction, T2 if the owner wants an absolute number in the title.

## 5. Ordering advice for the paper's first page
Abstract: design (S1), absolute g per kWh with relative in the same sentence and 24 h values (S2), ceiling and prediction shares (S3), then the existing hypothesis, weak-result and bounds sentences. Introduction paragraph 4: already has the right order; add the 24 h absolute sentence in one clause. Results 5.1: g per kWh, then percent, then ceiling. This is presentation of existing keys and the computations above, no change to any confirmatory result.

## 6. Verification log
- Checked by reading: every g/kWh and g/job number above against ledger_TEST_posthoc.csv (PH4, PH7 keys read by script); S24 and S12 relative savings against ledger_TEST.csv; per-BA statistics recomputed from tables/secondary_retained_share.csv (504 BA rows, 42 BAs x 4 slacks x 3 traces); PM100 trace energy, span and job counts recomputed from data/derived/jobs_PM100.parquet and jobs_FDATA.parquet using the main filter from 03_data (COMPLETED, r_act >= 1 min, 0 < r_req <= 72 h): PM100 108,329 jobs, 159 days, 768,337 kWh; F-DATA 2,661,645 jobs, 26.09 GWh over non-contiguous months.
- Not verified: the Attenni et al. 6 to 12 % figure beyond A13's quotation; that the saved blocks support C4; that the abstract build can read secondary-ledger keys.
- 8.76 GWh per MW-year = 8,760 h x 1 MW (arithmetic). 58, 116, 46 t per MW-year = 6.64, 13.20, 5.27 x 8.76 (arithmetic from PH4 keys).
