VERDICT: A11 done; v0; 62 rules; 9 open gaps

# Journal expert brief, Paper A, SUSCOM (give this file to every drafting, figure and reviewer agent)

Written 2026-11-12 by agent A11. Short names: JB = `_shared/JOURNAL_BASICS.md`; JP = `_shared/JOURNAL_PROFILE_SUSCOM.md` (P.n = its "Paywalled pass" items, which win over earlier sections where they differ); JPA = `paper_A/research/JOURNAL_PROFILE_A.md`; SP = `STYLE_PROFILE.md`; BB = `BEST_PAPER_BAR.md`; FP = `FIGURE_PLAN.md`; MP = `_shared/MEGA_PROMPT.md`; PR = `PREREG.md`; PB = `paper_B/research/JOURNAL_EXPERT_BRIEF.md`. Numbers: only ledger keys from `tables/ledger_TEST.csv` (and `ledger_TEST_*.csv`, `ledger_DEV*.csv`); never type a result. Facts not in the files are marked "not established".

## 1. The paper in five lines
1. Question (PR s1, D0004): for non-interruptible HPC batch jobs that may be delayed inside a slack window to lower-carbon hours, how much of the perfect-information carbon saving is realised when the scheduler sees only a past-only forecast of grid carbon intensity and only the user's requested walltime (or a history-based runtime prediction)?
2. Data: EIA-930 hourly average carbon intensity, 42 balancing authorities (BAs), TRAIN 2018-07..2024-06, DEV 2024-07..2025-06, TEST 2025-07..2026-06; job traces PM100 (primary), F-DATA and KIT FH2 (secondary) (PR s2-3).
3. Design: pre-registered, frozen by md5 before TEST; 2x2 of signal (oracle, LightGBM forecast) by runtime estimate (actual, requested), plus a history predictor; simple-policy ladder; stratified block bootstrap, Holm over H1-H3; Shapley split of the oracle-to-deployable gap (PR s4-7).
4. Finding: see ledger keys `TEST.PM100.w.S12.H1_deployable_saving.*`, `...H2_runtime_penalty.*`, `...H3_prediction_recovery.*`, and the Shapley keys `TEST.PM100.w.S12.shapley`. State each with the PR s8 wording; never quote a number from this brief.
5. Why SUSCOM: lane A "making computing sustainable" (scheduling and allocation; algorithms for reduced energy for HPC; JB s2) and a niche JPA s1 found empty inside the journal (no SUSCOM paper on carbon-intensity forecasting for computing, runtime estimates in carbon-aware scheduling, or EIA-930; the search was Crossref only, so say "we found none").

## 2. Journal rules (source in brackets)
R1. Article type: "original and timely research papers and survey articles"; no formal type list. Paper A is a research paper. [JB s3]
R2. Word or page limit: none stated in the guide. Plan 8,500 to 10,000 body words, 10 to 14 typeset pages; do not pad above about 10,000. [JB s3; JP s8, P.2 item 6, P.5 item 3] (BB B11 says 9 to 11k; use the JP figure, which rests on typeset papers.)
R3. Abstract: at most 250 words, stand-alone, no references, abbreviations defined; working range 200 to 230 words, one paragraph. [JB s3; JP P.2 item 2, P.5 item 1] Count on the Word render. (STYLE_PROFILE and BB say 220 to 250; the controller's update supersedes: stay at or below 230.)
R4. Highlights: required at submission; 3 to 5 bullets; at most 85 characters each including spaces; separate editable file with "highlights" in the file name; do not embed in the manuscript body. [JB s3; JP P.2 item 14, P.5 item 6]
R5. Keywords: 1 to 7, English, avoid multi-word keywords containing "and" or "of"; aim at 5 to 6. [JB s3; JP P.2 item 4]
R6. Graphical abstract: optional; separate file at least 1328 px wide, readable at 13 cm. Decision on whether to make one: open (not established that it helps).
R7. Source files: .docx or .tex, PDF not accepted as source. Template: the guide names none; elsarticle is the Elsevier default (JP s3 tags it not verified). Follow elsarticle and say so. [JB s3; PB s0 rule 6]
R8. Numbered sections 1, 1.1; abstract unnumbered; acknowledgements directly before references; appendices A, B with Eq. (A.1). [JB s3]
R9. References: numbered in square brackets in order of appearance; include DOIs; mark preprints "preprint"; cite datasets with [dataset] and software as references; journal names per LTWA at proof. Target 40 to 55 (median 36 to 42, range 21 to 78). Every DOI a blue clickable link (owner rule, D0012). [JB s3; JP P.2 item 9, P.5 item 2; progress.md D0012]
R10. Declarations: competing-interest file from the Elsevier declarations tool (separate upload); funding sentence (exact no-funding wording in JB s4, `[USER]` flag until the owner says otherwise); CRediT (14 roles) after the Conclusion and before References. [JB s4; MP s12]
R11. Generative-AI declaration: ONLY in its own section before the reference list, with the Elsevier template title and sentence verbatim (JB s4). Never in Methods, Acknowledgements, cover letter or title page. Scope wording: confirm with the owner; never change a statement the owner or professor has edited. [JB s4; MP s12; owner rule, D0012]
R12. Data availability: Option C. Deposit and link: Zenodo DOI for code, derived data, ledger, PREREG and `SHA256SUMS.txt`; state source licences (EIA-930 public domain; PM100 and F-DATA CC-BY-4.0; KIT FH2 licence terms from the Parallel Workloads Archive: check before release). The owner uploads Zenodo manually from our guide; use placeholders until the DOI exists. Never leave the section empty. [JB s4; JP s12, P.5 item 9; PR s2; D0012]
R13. Code availability: private GitHub; the owner gives the link before any push; wording uses a placeholder until then. [D0012]
R14. Figures: separate files, vector PDF with embedded fonts plus 300 dpi PNG, colour-blind-safe, one image per file; no AI manipulation of primary images. Tables: editable text, notes below, no vertical rules or shading. [JB s3]
R15. Peer review: single anonymized, at least two reviewers; editors may desk-reject; first-decision time 1 day (publisher insights page; JIF year not verified). [JB s1]
R16. Author names, affiliations and emails stay as placeholders `[USER]`. [D0012; MP s12]

## 3. Style rules for writers
Title
W1. Owner wants a finding-led title with no negatives and no trailing region or dataset phrase (MP s8). SUSCOM titles are descriptive (0 of 50 finding-led; mean 13.4 words; the topic-close ones 14 to 15 words; no Name-colon). [EXEMPLARS s4; JPA s5] Recommendation: a descriptive object plus a finding clause, under 18 words, no question mark, no acronym, no colon-method name. Shape: "Carbon-aware delay scheduling of HPC batch jobs: <finding clause>". The colon form occurs in 15 of 50 titles, so it is accepted. The owner approves the final title; it stays provisional until all analyses are done (MP s8).
Abstract (200 to 230 words, one paragraph, 6 to 9 sentences)
W2. Moves in order: (1) sustainability context in one sentence, with the computing lever; (2) gap in one sentence (deployable saving is rarely scored with real forecasts and real runtime estimates); (3) design with data named (42 BAs, three job traces, held-out year, pre-registered); (4) two to four results with interval each (H1, H2, H3 and the Shapley split); (5) one honest weak or null result; (6) one implication sentence for operators. [JP P.2 item 3; SP finding 4; JPA s5] Three to five numbers; every one a ledger key. Define abbreviations at first use in the abstract (BA, HPC, EIA).
Introduction
W3. Paragraph 1 states the sustainability outcome and the computing contribution (MP s4; JP s15 item 1). Then: the closest SUSCOM papers and what they assume (runtimes known, noise-injected forecasts: 101498); the gap sentence; the design in two sentences; 3 to 4 numbered contributions with "we", the last one the release (code, derived data, ledger, preregistration; Zenodo placeholder); a roadmap sentence listing sections by number. [JPA s5; JP Lane A additions]
W4. Contribution verbs: "we quantify", "we measure", "we decompose", "we release". Banned: "novel", "first", "to the best of our knowledge", "groundbreaking". [PB s2 rule 4; JP s14 shows these as common weakness in the corpus]
Sections
W5. Order: 1 Introduction; 2 Related work (with comparison table); 3 Data; 4 Method (arms, estimands, scheduler, forecasting, inference); 5 Results (RQ-by-RQ or H1-H3, then secondaries); 6 Discussion (trade-offs, delay cost, BA character, Threats to validity, Reproducibility); 7 Conclusion; then CRediT, declarations, AI declaration section, data and code availability, references. A separate Related work section appears in 13 of 14 typeset papers. [JP P.2 items 5, 12; JPA s5]
Related work
W6. One comparison table (T1 in FP): rows are Wiesner 2021, Sukprasert 2024, Radovanovic 2023, CarbonCast 2022 (stronger venues), and SUSCOM 101498, 101216, 101470, 101407, 100950 (closest SUSCOM); columns: data and scale, carbon signal (oracle, noise-injected, real forecast), runtime handling (assumed known, requested, predicted), baselines, uncertainty reported, code released. Fill cells only from what was read; abstract-only cells say "abstract only" and "not established" (JPA s4: 101216, 101470, 101407, 100950 not read in full). [BB B9; JPA s4]
W7. Positioning claims allowed at present: none of the four closest read papers scores real requested-versus-actual runtimes; none decomposes the forecast cost and the runtime cost; 101498 itself lists noise-injected forecasts and known runtimes as threats; 101470 has an oracle (abstract level). Do not say "no prior work". [JPA s4-5]
W8. The scheduler is the delay-to-lowest-integral policy of Wiesner and Sukprasert; say that no new scheduler is proposed. [PR s7 scope note]
Threats and reproducibility
W9. Threats to validity: a lettered list a) to e) inside Discussion, 300 to 400 words, plain admissions (101498 pattern). Must cover: grid data assumed available at arrival (EIA publication delay; PR s3), foreign traces placed on US grids (S6, P4_PLAN), non-interruptible jobs with no capacity limit and no migration, average (not marginal) intensity with lifecycle factors of documented judgement for oil, other and unknown, KIT FH2 with 1 kW per job, unscored forecaster tuning (HPO gap, D0012, until S5 is done). [JPA s5; PR s2-4; P4_PLAN]
W10. Reproducibility subsection: one-command rerun, frozen md5s, ledger, Zenodo placeholder (101106 has a dedicated heading). [JPA s2.2]
W11. Preregistration disclosure: state the freeze date, md5, each deviation (PREREG_DEVIATIONS.md) and that the P4 items S1 to S5 are post-freeze and exploratory, labelled as such in text, tables and captions. [PR s9; P4_PLAN]
Register and mechanics
W12. "We" for actions and decisions (contributions, Methods steps); passive for set-up and data description; about 8 to 9 "we" per 1,000 words at most; at most 30 % passive. [JP s14; SP finding 2]
W13. Sentences: mean 22 to 25 words, none above 40, hard cap 45; one claim per sentence. [SP finding 1; MP s9]
W14. No em or en dashes (use commas, colons, "to"). One English variant: American (measured in the SUSCOM paper and all four stronger-venue texts); e.g. "data center". [JP s14; SP finding 6]
W15. Hedging about 1 per 100 words, on mechanisms and interpretations only, never on measured numbers. [SP finding 3]
W16. Every number is a ledger key; a missing key is an error; numbers identical across abstract, highlights, results, conclusion, cover letter. [CLAUDE.md evidence rule 1; MP s11]
W17. Every claim about practice (EIA publication delay, HPC user behaviour with walltimes, grid mixes) carries a citation or is softened. [MP s11]
W18. Show absolute (kgCO2 or g per job-hour) and relative effects with intervals; relative-only reporting is a flagged weakness. [BB B10]
W19. Describe each result with the PR s8 wording; secondary and post-freeze items are never called confirmatory; H4 is descriptive (demoted on Codex R03).
W20. No disparaging wording about prior work; negative and null results stated plainly. [CLAUDE.md rule 6]
W21. Define each abbreviation again at first use in the body; keep arm labels exactly: oracle|act, oracle|req, lgbm|act, lgbm|req (D), lgbm|pred, lgbm|pred2, run-now, night, persistence, seasonal naive day and week, profile7, histprofile. [FP; PR s4]

## 4. Figure and table rules
F1. Count: the project rule is 13 to 14 figures (FP has 14), but the typeset median is 9 (range 3 to 25) and padding is a visible weakness. Keep each figure only if it carries new information; merge near-duplicates (FP 11 and 12 are candidates). Tables 4 to 6 (median 4.5). [CLAUDE.md MP s7; JP P.5 item 4]
F2. Okabe-Ito, one fixed colour per arm family across all figures (FP style line); baselines grey; matplotlib plus seaborn via the `dataviz` skill; no saturated defaults. [MP s7; JP s9]
F3. Widths 90, 140 or 190 mm; text at least 7 pt at print size; 300 dpi PNG plus vector PDF with embedded fonts; one image per file. [MP s7; JB s3]
F4. Multi-panel figures: (a), (b) lettering, panel titles naming the trace or BA group, shared legend placed off the data, units in every axis label, one unit per axis (no "%" with "g/kWh" on one axis). [JP P.2 items 10-11]
F5. Uncertainty visible: 95 % intervals on every headline estimate (0 of 20 read papers show any; this is where Paper A is ahead). [JP s9, s11]
F6. Captions: short title clause plus one sentence stating the finding, then n (BAs, jobs) and the interval type, then "Exploratory, post-freeze" where applicable. Tension to manage: typeset captions are 1 to 18 words and descriptive; the owner wants finding-stating, self-contained captions. Resolve by keeping the total at about 20 to 35 words and never above 35. [JP P.5 item 5; owner rule]
F7. Every figure cited in order in the text; every figure viewed at print size by the controller before inclusion; no overlaps, even spacing. [MP s7; CLAUDE rule]
F8. Tables: booktabs three rules, visible lines in the DOCX, no `\resizebox`, notes below, generated from the ledger by script, true minus sign. [MP s7, s11; JB s3]
F9. Main result table (T4): one row per estimand H1 to H4; columns estimate, 95 % interval and interval type (fixed-BA stratified block bootstrap), raw p, Holm p, decision, n BAs, plus the same on F-DATA and KIT FH2 in a second block; baselines beside it (run-now, night, histprofile, persistence, seasonal naive, oracle). Best value in bold, consistent decimals. [PR s6; JP P.2 item 7; BB B4-B5]
F10. Figure 1 is the schematic of the 2x2 design for a computing reader, written so that no carbon-grid jargon is needed to follow it. [FP 1]
F11. At least one algorithm box (the preregistered simulation and bootstrap procedure); more only where a component is introduced (6 of 14 papers have one). Equations: 15 to 25 numbered and referenced. [JP P.2 item 8; MP s7]

## 5. Personas for reviewer agents
### 5a. SUSCOM handling editor (decision within about a day)
Checks first: scope (computing for or of sustainability), importance of the finding, clarity for a computing reader, declarations complete.
Likely rejection reasons: reads as energy-systems rather than computing (the owner's earlier desk rejection elsewhere was scope only, JP s16 item 6); incremental scheduling benchmark; missing declarations or empty data statement; overclaim.
| # | Question | Where answered |
|---|---|---|
| E1 | Why SUSCOM and not an energy-systems journal? | Abstract sentence 1; Intro para 1; scope block "scheduling and allocation", HPC algorithms |
| E2 | What is the one finding to remember? | Title; abstract moves 3-4; highlights 1-2; contribution 1 |
| E3 | Is it new relative to Wiesner, Sukprasert and the SUSCOM papers? | Intro gap sentence; T1 |
| E4 | Which SUSCOM papers does it cite and position against? | Related work, T1 (101498, 101216, 101470, 101407, 100950) |
| E5 | Open data and code with licences? | Data and code availability; Zenodo placeholder |
| E6 | Abstract at most 250 words; highlights 3 to 5 at most 85 characters; keywords at most 7? | R3-R5; Word render count |
| E7 | AI declaration in its own section only? | R11 |
| E8 | Any "novel", "first", unsupported practice claim? | W4, W17 |
### 5b. Domain referee: carbon-aware computing and HPC scheduling
Checks first: realism of the job model and signal; whether the baseline ladder includes the simple policies that Sukprasert finds capture most gain; average versus marginal intensity; whether results depend on one trace.
Likely rejection reasons: average intensity answers a marginal question; delay-only, no interruptibility, no capacity limit; US grids with Japanese, Italian and German traces; requested-walltime semantics (censoring at the limit, killed jobs) not audited; improvement reported relative to run-now only; EIA publication delay ignored.
| # | Question | Where answered |
|---|---|---|
| D1 | Is saving measured against run-now and against the best simple policy? | T4 baselines; PR s7 item 5; BB B5 |
| D2 | Why average and not marginal intensity; are factors defensible? | Method; threats (a); sensitivity S3 (exploratory) |
| D3 | Are walltime semantics audited (status codes, kill-at-limit share, requested to actual ratio)? | Data section; A07_JOBS.md; near-limit sensitivity (PR s7 item 11) |
| D4 | Do foreign traces on US grids bias the result? | Results by trace; threats (b); S6 limitation text |
| D5 | Is forecast error real and past-only; was the forecaster tuned fairly? | Method s4.x; forecast-skill figure; HPO sensitivity S5 labelled exploratory |
| D6 | What does the saving cost in delay? | FP 13 delay-cost figure |
| D7 | Does the 2x2 conclusion hold across slack 2, 6, 12, 24 h and by BA character? | FP 8, 11, 12 |
| D8 | EIA data delay: does the planner see data it could not have? | Threats (a); S2 sensitivity |
### 5c. Statistics and reproducibility referee
Checks first: unit of inference, preregistration and freeze, multiplicity, dependence handling, leakage.
Likely rejection reasons: intervals that ignore job-sampling variance (A08 threat; S1); inference target unclear (fixed 42 BAs versus a population); post-freeze analyses presented as confirmatory; one-sided p with a null-centred bootstrap not explained.
| # | Question | Where answered |
|---|---|---|
| S1 | Unit of inference and target? | PR s5-6: the fixed set of 42 BAs; two-stage bootstrap shown beside as a population reading |
| S2 | Freeze, md5, TEST scored once; deviations? | Method; PREREG_DEVIATIONS.md; W11 |
| S3 | Bootstrap design (7-day blocks within BA, B = 2000, null-centred one-sided p), Holm over H1-H3? | PR s6; equations and algorithm |
| S4 | Leakage: forecasts causal, user history only from jobs ended before submission, HPO on TRAIN only? | Method; assertions in `src/prep_jobs.py`; PR s3 |
| S5 | Are the intervals complete (alignment replicates, job sample)? | S1 sensitivity; disclose if not run |
| S6 | Rerun? | Reproducibility subsection; Zenodo; ledger keys |
| S7 | Effect sizes and intervals for every headline, absolute and relative? | T4; W18 |
### 5d. Desk-reject screen (run before every submission candidate)
- [ ] Title descriptive object plus finding clause, under 18 words, no negatives, no question mark.
- [ ] Abstract at most 250 words (target 200 to 230); sentence 1 states the sustainability outcome; numbers match the ledger.
- [ ] Intro cites and positions against 101498, 101216, 101470, 101407, 100950 and the stronger venues.
- [ ] Highlights 3 to 5, each at most 85 characters; keywords 1 to 7.
- [ ] Data and code statements non-empty (placeholders allowed pre-release, real DOI before submission).
- [ ] AI declaration only in its own section; competing-interest file; CRediT; funding sentence.
- [ ] No "novel", "first", unsupported practice claims; no em or en dashes; American English.
- [ ] Every result has a baseline and an interval; negative results present.

## 6. The owner's standing rules (D0012) as a P6-P8 checklist
- [ ] AI use stated only in the AI-declaration section (R11).
- [ ] Writers' room per section: senior writer, `research-humanizer` with `check_text.py`, line editor (Grammarly catalogue or the writing_qa substitute, at most 3 passes, scores not measured reported as "not measured"), meaning auditor; iterate until all agree. [D0012; MP s9]
- [ ] Every DOI or URL reference a blue clickable link (hyperref colours).
- [ ] Private GitHub; owner gives link before any push; Zenodo uploaded manually by the owner from a click-by-click guide checked against the live UI.
- [ ] Position against SUSCOM A1-A5 (`_shared/PAYWALLED_SUSCOM_LANE_A.md`) explicitly; cite 100950.
- [ ] Elsevier elsarticle template and the Guide for Authors followed exactly (except the owner's AI-section rule).
- [ ] Frame as an important finding for the journal, not an incremental benchmark (PB s2 rule 7), stated as a measured decomposition, not a ranking.
- [ ] Author names and details are placeholders `[USER]`.
- [ ] Research-grade HPO gap closed or disclosed: frozen LightGBM has no HPO; S5 (Optuna, TRAIN-only) reported beside frozen values, labelled exploratory (D0012; A05_FORECASTS.md).
- [ ] One Codex thread `research/codex/THREAD.md`; multi-expert review at P7 (editor, domain referee, statistics referee) plus a Sonnet senior reviewer; all blocking points closed.
- [ ] `hidden-unicode` `wm scan`, `wm clean`, `wm audit` at 0 findings on every text file, the PDF and the DOCX.
- [ ] DOCX verified on its own Word render (ruled tables, black headings, OMML equations, scope-bar algorithms); ledger check 0 missing keys; dash sweep.
- [ ] Never use Fable; Sonnet for drafting and review; replies of at most 5 lines; reports in files (CLAUDE.md agents section).

## 7. Open gaps (v1 after paywalled pass)
G1. Paper A's own 16 lane-A PDFs (`_shared/PAYWALLED_SUSCOM_LANE_A.md`, Part A and B) are not analysed. Until they are, T1 cells for 101216, 101470, 101407, 100950 are "abstract only" or "not established".
G2. Whether 101470 (ReBase) and 101216 build the oracle and the prediction-quality study in a way that overlaps the 2x2: not established; may force a rewording of W7 and the novelty sentence.
G3. Topic-close caption style, baselines, statistics and limitations sections: known only for 101498 and 101106 in full (captions of 101498 not extracted). The 14-paper typeset set is mostly ML forecasting, so it sets the format floor, not the rigour model (JP P.1 caveat).
G4. Title shape: no evidence that a finding clause is accepted in SUSCOM (0 of 50 finding-led); the recommendation in W1 is an inference from the colon-subtitle titles. Editor reaction not established.
G5. Highlights: required by the guide; none visible in typeset PDFs; no exemplar text for style (numbers or not). Not established.
G6. Abstract word range: the 250 limit is from the guide; the 200 to 230 range is from typeset medians; JP says the limit should be re-verified on the live guide before submission.
G7. JIF year, quartile, article-length limits, LaTeX template, unit rules: not verified (JB s8).
G8. Whether SUSCOM accepts or expects an Algorithm box and a separate Reproducibility subsection: seen in some papers (6 of 14; 101106), not a rule.
G9. KIT FH2 licence wording and the EIA-930 publication-delay citation for the data-availability and threats text: not yet read from the sources; check before drafting R12 and W9.
