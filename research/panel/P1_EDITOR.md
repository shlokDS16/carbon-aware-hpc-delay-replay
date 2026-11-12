VERDICT: P1 editor: SEND OUT AFTER CHANGES; make the importance case explicit (absolute g CO2 effect, key G12 missing) and put the finding plus "measurement, no new scheduler" in the first 150 abstract words

Reviewer: P1 (handling editor persona, brief s5a, desk screen s5d). Inputs read: JOURNAL_EXPERT_BRIEF v1, SPEC v0 s1-s6, LESSONS L8, A14 table, Figures 6 and 7 (viewed). Anything not in the brief is "not established".

## 1. Desk-reject screen (5d)
| # | Item | Verdict | Reason and fix |
|---|---|---|---|
| 1 | Title <= 16 words, no "first", no runtime-beats-forecast claim | PASS | SPEC s1 options 1 (14 w) and 2 (13 w) comply. Only risk is G4 (0 of 16 SUSCOM titles finding-led). |
| 2 | Abstract <= 250 (target 200-230); sentence 1 sustainability; numbers = ledger | RISK | SPEC s3 plans ~208 words, fine. Move 4 carries about 9 numbers (D, oracle, retained, H2, H3, both Shapley terms, F-DATA contrast) vs W2 "three to five". Cut to 5. Sentence 1 must name the computing lever, not only grid carbon (E1 scope). |
| 3 | Intro positions against 101498, 101216, 101470, 101407, 100950 + stronger venues | PASS with RISK | SPEC s5.1 pt 2 and s5.2.2 list all. LACS, COAST, LiteCast are "NEW, to read" (G10); a gap sentence resting on unread papers is an overclaim risk. Read them before the Introduction is frozen. |
| 4 | Highlights 3-5, <= 85 chars; keywords 1-7 | PASS | SPEC s4: 5 bullets, 65-77 chars. Keywords are not listed in SPEC: add (<= 7, no "and"/"of" phrases). Bullet 3 (runtime term exceeds forecast term on two of three traces) rests on a 52/48 near-tie on F-DATA and terms without intervals (see 5.3). |
| 5 | Data and code statements non-empty | PASS (placeholders) | SPEC s5.8 Option C. KIT FH2 licence and Zenodo DOI open (item 8, G9); must be real before submission. |
| 6 | AI declaration own section only; competing interest; CRediT; funding | PASS | SPEC s5.8 lists all in order. R11 wording cannot be checked against any typeset exemplar (A14); owner-rule driven, journal requirement not established. |
| 7 | No "novel"/"first"/unsupported practice claims; dashes; American English | RISK | Plan is clean, but practice claims are unbacked until read: walltime-inaccuracy figures (Tsafrir, Mualem; item 11) and EIA publication delay (G9). Quote none until read. |
| 8 | Limitations run-in labels; definitions paragraph; T1 with A13 columns | PASS with RISK | SPEC 6.4, Intro pt 5, T1. T1 has "to read" cells for three rows; a submitted table cannot carry them. |
| 9 | Figures: two-channel encoding, zero-based axes, captions <= 35 words, no F12 failures | RISK | Viewed. Fig 6 is readable but still the old encoding (FF1): the thick fixed-BA bar is nearly invisible, one marker shape per row rather than colour = runtime and style = signal, axis says "% of emissions" while text uses pp. Fig 7 is a stacked bar plus a redundant share panel, not the waterfall SPEC promises, no intervals, shares to 0 decimals invite over-reading (F-DATA 52/48). Fig 1 caption 78 words. 8 of 14 figures unbuilt or pending. |
| 10 | Every result has baseline and interval; negatives present | PASS (C3 RISK) | Night, persistence, histprofile kept; negatives in abstract move 5. Shapley terms lack intervals (FF2). |

Scope check (E1): the largest desk risk is "reads as energy-systems". EIA-930 dominates Data (350 words) and Introduction paragraphs 1 to 2. Keep the computing object (schedulers, walltime semantics, history predictors, job traces) in the lead of title, abstract and Introduction.

## 2. Fit and significance
- Fit: strong. Lane "scheduling and allocation / HPC algorithms" (brief s1 line 5); niche empty in-journal by Crossref only, so write "we found none".
- First 150 words: SPEC s3 moves 1 to 3 use about 93 words, so the result starts near word 95 and finishes after 165. For a decision within a day, the result must sit inside 150 words. Fix: moves 1+2 in about 35 words, headline result by word ~80, details after.
- Story clarity: good ("a deployed scheduler sees only a past-only forecast and the requested walltime"). The 2 x 2 plus Shapley split is the hook: it turns a benchmark into an actionable answer (log runtimes, add a history predictor).
- Importance weakness: deployable saving is small (Fig 6: roughly 1.5 to 3.8 % across traces; D about 1.9 % on PM100). Editor asks "so what?". G12 (absolute effect key) is open. Without g CO2 per job-kWh or a per-system-year figure, rigour is the selling point, not importance.
- I would send out with enthusiasm if: (i) page 1 states the retained share and the walltime cost in words; (ii) pre-registration and release are visible early (0 of 10 topic-close papers pre-register, A14 F5); (iii) the weak result is stated; (iv) an absolute effect is present.
- Do not oversell replication: H1-H3 are confirmatory on PM100 only (PR s6); F-DATA and KIT FH2 are secondary what-if replays on US grids (D4, W25).

## 3. Title ranking
1. SPEC option 2 (13 w), "Carbon savings of delay-based HPC batch scheduling with past-only forecasts and requested walltimes": matches the SUSCOM norm (descriptive dominates, A14), names the computing object and the deployable condition, no claim risk. Weakness: no finding.
2. LESSONS option 3 (15 w), "...: how much perfect-information saving a deployable scheduler realizes": names the measured quantity (has a colon, which the brief W1 discourages only for method names).
3. SPEC option 1 (14 w), "Forecast and walltime information jointly determine ...": true but "jointly determine" is close to a tautology for any 2 x 2 with positive terms; referee reads it as vague; also untested form (G4).
Suggested alternative (13 w, no colon, no negatives, no number, true on all three traces): "How much carbon saving survives forecasts and requested walltimes in delay-scheduled HPC batch jobs". Owner decides; fallback is option 2.

## 4. Structure, length, counts
- Structure: keep SPEC s5 order (matches W5; separate Related work in 13 of 14 papers). Fold 6.5 Reproducibility into one paragraph if words are tight (1 of 15 papers has a dedicated one).
- Length: SPEC arithmetic is about 11,500 with captions against the 11,000 R2 ceiling. Cut 6.3 to 150 words and 2.1 to 300; target about 10,500 (median typeset 11.1k).
- Figures: 13 (merge FP 11+12) is right; owner rule (13-14) is met; do not add. A 12-figure option exists by folding the delay-cost figure (150-word subsection) into Fig 8.
- Tables: T1-T6 is the minimum of the 6-9 plan; keep six.
- Algorithms: five is too many (topic-close 0-3; F11 "more only where a component is introduced"). Merge Algorithm 1 (Plan) and 2 (RuntimeEstimate) since E2 and E6 already carry them; keep AlignAndSample (unique, answers D4/S4) and the bootstrap; let the final Study algorithm call the others by name. Target 3 to 4 boxes, which also satisfies the owner's "several".
- Equations: E1-E19 is inside 12-25; make E17 (mean delay) and E18 (Spearman) inline, not numbered; E4 can be a sentence.
- References: about 68 planned vs R9 target 40-55 (median 49, topic-close 40.5, max 78). Owner wants a high, well-used count: 58 to 65 is defensible if each entry is cited for a stated reason. Remove the "reserve" entry (friedman2001), do not cite lists of 12 in one sentence in 2.1, and cite the ten SUSCOM neighbours with a clause each only if read.

## 5. Five changes that most raise acceptance chance (ranked)
1. Add the absolute effect (G12 key: run-now mean intensity per trace; g CO2 per job-kWh, and one per-system-year illustration), beside every relative saving and retained share (T4, W18, E19). It answers "so what" for a 1.9 % saving.
2. Re-cut the abstract and Introduction opening: finding and "measurement, no scheduler proposed" inside the first 150 words; abstract move 4 down to 5 numbers; computing lever in sentence 1 (SPEC s3, s5.1).
3. Make C3 defensible: intervals on the Shapley terms (FF2) before claiming runtime term larger on two of three traces; otherwise write "similar size" and drop highlight 3 and the abstract trace contrast. Fig 7 shows 60/40, 59/41 and a 48/52 near-tie.
4. Close the evidence gaps a referee will find: read LACS, COAST, LiteCast and complete T1 (G10, G1r); rebuild Figures 6 and 7 per FF1/FF2 (two-channel encoding, visible fixed-BA interval, true waterfall) and build the eight pending figures.
5. Fit the journal's norms: 3 to 4 algorithms, 58 to 65 justified references, about 10,500 words, 13 figures; keep S1-S5 and X1-X7 in a labelled exploratory block (F14) and run only what finishes.

Not established: SUSCOM word or page limit, template, JIF, editor reaction to finding-led titles (G4, G7).
