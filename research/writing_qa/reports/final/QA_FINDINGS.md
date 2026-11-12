# QA_FINDINGS, Paper A (A38, 2026-11-12 10:53)

Source: paper/sections/*.tmpl.tex (prose only; <<key|fmt>> becomes N, citations [1], inline math X, \Arm macros dropped). The manuscript was not modified and no text left this machine. Every finding is a candidate to read, not a verdict. Primary toolchain: `_shared/tools/writing_qa` (run_qa.py --config configs/paper_A.json); post-processing and style statistics: `paper_A/tools/writing_qa`.

## Summary by tool and severity

| tool | error | clarity | style | total |
|---|---|---|---|---|
| coedit | 8 | 39 | 68 | 115 |
| custom | 0 | 25 | 0 | 25 |
| languagetool | 3 | 4 | 1 | 8 |
| vale | 0 | 8 | 57 | 65 |
| **all** | 11 | 76 | 126 | 213 |

Findings after filtering: 213. Removed as false positives: 512 (by filter reason: {'technical term / name': 230, 'dropped rule': 133, 'passive in a short sentence (academic norm)': 90, 'ordinary academic connective': 43, 'CoEdIT replaces a defined domain term or switches US/UK spelling (not an error)': 5, 'front-matter placeholder, keyword line or table-file macro (LaTeX artefact)': 5, 'placeholder': 3, 'inline math or code token kept as text by texclean (LaTeX artefact)': 2}). All removed rows, with the reason, are in QA_FILTERED.csv.

## Summary by section

| section | error | clarity | style | total |
|---|---|---|---|---|
| 00_frontmatter | 0 | 6 | 2 | 8 |
| 01_intro | 1 | 10 | 13 | 24 |
| 02_related | 2 | 7 | 8 | 17 |
| 03_data | 2 | 5 | 17 | 24 |
| 04_method | 0 | 11 | 33 | 44 |
| 05_results | 1 | 12 | 20 | 33 |
| 06_discussion | 4 | 5 | 12 | 21 |
| 07_conclusion | 0 | 0 | 1 | 1 |
| 08_declarations | 0 | 2 | 6 | 8 |
| S_supplement | 1 | 18 | 14 | 33 |

## Summary by rule (top 25)

- coedit / GEC: 103
- vale / write-good.Passive: 57
- custom / SENT_LEN_45: 21
- coedit / CLARITY_REWRITE: 11
- vale / write-good.TooWordy: 5
- custom / ABBREV_FIRST_USE: 4
- vale / write-good.Weasel: 3
- languagetool / EN_A_VS_AN: 2
- languagetool / EN_COMPOUNDS_QUARTER_HOUR: 2
- languagetool / THE_PUNCT: 1
- languagetool / ON_SKYPE: 1
- languagetool / COLLECTIVE_NOUN_VERB_AGREEMENT_VBP: 1
- languagetool / NOW: 1
- coedit / PARAPHRASE: 1

## Style comparison with the SUSCOM corpus

Corpus: 15 papers (12 SUSCOM empirical papers 2021-2026 with usable text, 3 open exemplars: Wiesner 2021, Sukprasert 2024, CarbonCast 2022; the surveys 100989 and 101080 and two papers with unusable two-column text are excluded). Interquartile ranges are over per-paper values (papers with at least 150 words of the section type). Paper A values come from the template prose, where N, X and [1] stand for numbers, math and citations. Section type of Paper A: related work is compared with the corpus 'related' sections, data and method with 'methods'. Corpus section typing is by heading keywords and is approximate.

Metrics outside the corpus interquartile range: **38 of 63** (section type x metric cells with at least 3 corpus papers).

Outside the range (section, metric, Paper A, corpus [Q1, median, Q3]):

- abstract, sentence length, SD: 12.6 ABOVE corpus [4.8, 5.3, 9.6]
- abstract, nominalisations per 100 words: 4.4 BELOW corpus [4.9, 5.8, 7.8]
- abstract, connectives per 1000 words: 3.2 BELOW corpus [4.5, 11.3, 15.8]
- intro, sentence length, mean (words): 27.0 ABOVE corpus [19.1, 22.7, 24.2]
- intro, sentence length, SD: 12.8 ABOVE corpus [9.0, 10.4, 11.6]
- intro, hedges per 1000 words: 0.8 BELOW corpus [1.1, 1.7, 3.6]
- intro, boosters per 1000 words: 0.0 BELOW corpus [1.5, 2.8, 4.2]
- intro, nominalisations per 100 words: 5.6 BELOW corpus [6.0, 7.4, 8.3]
- intro, connectives per 1000 words: 7.1 BELOW corpus [12.1, 16.5, 18.9]
- related, sentence length, SD: 7.8 BELOW corpus [7.9, 8.5, 9.3]
- related, nominalisations per 100 words: 2.9 BELOW corpus [5.6, 6.6, 8.0]
- related, connectives per 1000 words: 7.9 BELOW corpus [13.4, 17.5, 21.8]
- related, citations per 1000 words: 32.4 ABOVE corpus [12.0, 13.5, 19.6]
- methods, nominalisations per 100 words: 3.2 BELOW corpus [5.3, 6.3, 7.0]
- methods, first person per 1000 words: 2.2 BELOW corpus [3.5, 6.9, 12.2]
- methods, citations per 1000 words: 5.7 ABOVE corpus [1.6, 2.3, 3.2]
- results, sentence length, mean (words): 23.8 ABOVE corpus [19.5, 20.5, 21.4]
- results, sentence length, SD: 11.9 ABOVE corpus [9.5, 10.3, 11.3]
- results, passive sentences (%): 11.3 BELOW corpus [19.2, 26.9, 31.9]
- results, boosters per 1000 words: 0.3 BELOW corpus [1.3, 2.0, 3.1]
- results, nominalisations per 100 words: 3.0 BELOW corpus [4.3, 5.9, 6.8]
- results, first person per 1000 words: 0.0 BELOW corpus [1.3, 3.0, 12.4]
- results, connectives per 1000 words: 4.1 BELOW corpus [12.2, 15.9, 20.1]
- results, citations per 1000 words: 0.3 BELOW corpus [1.3, 2.8, 4.1]
- discussion, sentence length, mean (words): 23.3 ABOVE corpus [18.8, 20.7, 21.8]
- discussion, sentence length, SD: 11.1 ABOVE corpus [7.1, 10.3, 10.7]
- discussion, passive sentences (%): 13.2 BELOW corpus [16.1, 21.4, 35.4]
- discussion, boosters per 1000 words: 0.0 BELOW corpus [1.7, 2.4, 6.5]
- discussion, nominalisations per 100 words: 3.6 BELOW corpus [5.7, 7.3, 7.8]
- discussion, first person per 1000 words: 2.8 BELOW corpus [4.1, 4.3, 11.2]
- discussion, connectives per 1000 words: 6.6 BELOW corpus [12.0, 12.3, 26.0]
- discussion, citations per 1000 words: 2.8 ABOVE corpus [0.0, 0.8, 1.8]
- conclusion, sentence length, mean (words): 26.1 ABOVE corpus [17.5, 20.6, 24.6]
- conclusion, sentence length, SD: 10.3 ABOVE corpus [7.8, 8.5, 10.1]
- conclusion, hedges per 1000 words: 6.8 ABOVE corpus [0.0, 0.0, 6.5]
- conclusion, nominalisations per 100 words: 2.9 BELOW corpus [5.3, 6.5, 9.7]
- conclusion, first person per 1000 words: 0.0 BELOW corpus [2.1, 6.5, 21.2]
- conclusion, connectives per 1000 words: 0.0 BELOW corpus [12.5, 18.1, 29.4]

Full comparison:

| section type | metric | Paper A | corpus Q1 | median | Q3 | papers | position |
|---|---|---|---|---|---|---|---|
| abstract | sentence length, mean (words) | 26.2 | 22 | 24.8 | 30.6 | 13 | inside |
| abstract | sentence length, SD | 12.6 | 4.8 | 5.3 | 9.6 | 13 | ABOVE |
| abstract | passive sentences (%) | 16.7 | 11.1 | 22.2 | 28.6 | 13 | inside |
| abstract | hedges per 1000 words | 0.0 | 0.0 | 0.0 | 0.0 | 13 | inside |
| abstract | boosters per 1000 words | 0.0 | 0.0 | 4.3 | 9.3 | 13 | inside |
| abstract | nominalisations per 100 words | 4.4 | 4.9 | 5.8 | 7.8 | 13 | BELOW |
| abstract | first person per 1000 words | 3.2 | 0.0 | 14.2 | 20.0 | 13 | inside |
| abstract | connectives per 1000 words | 3.2 | 4.5 | 11.3 | 15.8 | 13 | BELOW |
| abstract | citations per 1000 words | 0.0 | 0.0 | 0.0 | 0.0 | 13 | inside |
| intro | sentence length, mean (words) | 27.0 | 19.1 | 22.7 | 24.2 | 15 | ABOVE |
| intro | sentence length, SD | 12.8 | 9.0 | 10.4 | 11.6 | 15 | ABOVE |
| intro | passive sentences (%) | 19.1 | 14.6 | 19.2 | 21.4 | 15 | inside |
| intro | hedges per 1000 words | 0.8 | 1.1 | 1.7 | 3.6 | 15 | BELOW |
| intro | boosters per 1000 words | 0.0 | 1.5 | 2.8 | 4.2 | 15 | BELOW |
| intro | nominalisations per 100 words | 5.6 | 6.0 | 7.4 | 8.3 | 15 | BELOW |
| intro | first person per 1000 words | 6.3 | 1.7 | 6.5 | 9.9 | 15 | inside |
| intro | connectives per 1000 words | 7.1 | 12.1 | 16.5 | 18.9 | 15 | BELOW |
| intro | citations per 1000 words | 9.4 | 9.3 | 12.0 | 13.8 | 15 | inside |
| related | sentence length, mean (words) | 22.6 | 19.3 | 20.6 | 23.4 | 13 | inside |
| related | sentence length, SD | 7.8 | 7.9 | 8.5 | 9.3 | 13 | BELOW |
| related | passive sentences (%) | 15.6 | 9.8 | 17.2 | 21.7 | 13 | inside |
| related | hedges per 1000 words | 2.9 | 0.6 | 1.2 | 2.9 | 13 | inside |
| related | boosters per 1000 words | 0.0 | 0.0 | 1.4 | 1.9 | 13 | inside |
| related | nominalisations per 100 words | 2.9 | 5.6 | 6.6 | 8.0 | 13 | BELOW |
| related | first person per 1000 words | 1.0 | 0.0 | 4.5 | 8.8 | 13 | inside |
| related | connectives per 1000 words | 7.9 | 13.4 | 17.5 | 21.8 | 13 | BELOW |
| related | citations per 1000 words | 32.4 | 12.0 | 13.5 | 19.6 | 13 | ABOVE |
| methods | sentence length, mean (words) | 21.1 | 18 | 19.7 | 21.6 | 12 | inside |
| methods | sentence length, SD | 10.7 | 9.5 | 11.5 | 12.6 | 12 | inside |
| methods | passive sentences (%) | 27.1 | 26.7 | 35.9 | 44.7 | 12 | inside |
| methods | hedges per 1000 words | 1.5 | 0.5 | 2.0 | 2.2 | 12 | inside |
| methods | boosters per 1000 words | 0.7 | 0.0 | 1.2 | 1.2 | 12 | inside |
| methods | nominalisations per 100 words | 3.2 | 5.3 | 6.3 | 7.0 | 12 | BELOW |
| methods | first person per 1000 words | 2.2 | 3.5 | 6.9 | 12.2 | 12 | BELOW |
| methods | connectives per 1000 words | 8.7 | 7.7 | 12.7 | 14.5 | 12 | inside |
| methods | citations per 1000 words | 5.7 | 1.6 | 2.3 | 3.2 | 12 | ABOVE |
| results | sentence length, mean (words) | 23.8 | 19.5 | 20.5 | 21.4 | 10 | ABOVE |
| results | sentence length, SD | 11.9 | 9.5 | 10.3 | 11.3 | 10 | ABOVE |
| results | passive sentences (%) | 11.3 | 19.2 | 26.9 | 31.9 | 10 | BELOW |
| results | hedges per 1000 words | 2.2 | 1.3 | 1.3 | 4.2 | 10 | inside |
| results | boosters per 1000 words | 0.3 | 1.3 | 2.0 | 3.1 | 10 | BELOW |
| results | nominalisations per 100 words | 3.0 | 4.3 | 5.9 | 6.8 | 10 | BELOW |
| results | first person per 1000 words | 0.0 | 1.3 | 3.0 | 12.4 | 10 | BELOW |
| results | connectives per 1000 words | 4.1 | 12.2 | 15.9 | 20.1 | 10 | BELOW |
| results | citations per 1000 words | 0.3 | 1.3 | 2.8 | 4.1 | 10 | BELOW |
| discussion | sentence length, mean (words) | 23.3 | 18.8 | 20.7 | 21.8 | 3 | ABOVE |
| discussion | sentence length, SD | 11.1 | 7.1 | 10.3 | 10.7 | 3 | ABOVE |
| discussion | passive sentences (%) | 13.2 | 16.1 | 21.4 | 35.4 | 3 | BELOW |
| discussion | hedges per 1000 words | 7.1 | 4.3 | 4.9 | 8.3 | 3 | inside |
| discussion | boosters per 1000 words | 0.0 | 1.7 | 2.4 | 6.5 | 3 | BELOW |
| discussion | nominalisations per 100 words | 3.6 | 5.7 | 7.3 | 7.8 | 3 | BELOW |
| discussion | first person per 1000 words | 2.8 | 4.1 | 4.3 | 11.2 | 3 | BELOW |
| discussion | connectives per 1000 words | 6.6 | 12.0 | 12.3 | 26.0 | 3 | BELOW |
| discussion | citations per 1000 words | 2.8 | 0.0 | 0.8 | 1.8 | 3 | ABOVE |
| conclusion | sentence length, mean (words) | 26.1 | 17.5 | 20.6 | 24.6 | 10 | ABOVE |
| conclusion | sentence length, SD | 10.3 | 7.8 | 8.5 | 10.1 | 10 | ABOVE |
| conclusion | passive sentences (%) | 17.6 | 5.0 | 20.0 | 33.3 | 10 | inside |
| conclusion | hedges per 1000 words | 6.8 | 0.0 | 0.0 | 6.5 | 10 | ABOVE |
| conclusion | boosters per 1000 words | 0.0 | 0.0 | 2.1 | 5.3 | 10 | inside |
| conclusion | nominalisations per 100 words | 2.9 | 5.3 | 6.5 | 9.7 | 10 | BELOW |
| conclusion | first person per 1000 words | 0.0 | 2.1 | 6.5 | 21.2 | 10 | BELOW |
| conclusion | connectives per 1000 words | 0.0 | 12.5 | 18.1 | 29.4 | 10 | BELOW |
| conclusion | citations per 1000 words | 0.0 | 0.0 | 0.0 | 0.0 | 10 | inside |

## Machine-text score (Binoculars-style), calibrated on the human corpus

Score = Binoculars-style (Qwen2.5-1.5B pair). LOW score = more machine-like. Reference: 450 human paragraphs of the SUSCOM and exemplar corpus (median 1.027, 10th percentile 0.935). Percentile = share of corpus paragraphs scoring at or below the Paper A paragraph; no absolute threshold is used. Not equivalent to Grammarly's AI detector.

| section | paragraphs | median percentile | min percentile | paragraphs below corpus 10th pct |
|---|---|---|---|---|
| 00_frontmatter | 1 | 96 | 96 | 0 |
| 01_intro | 10 | 91 | 54 | 0 |
| 02_related | 8 | 93 | 89 | 0 |
| 03_data | 15 | 96 | 60 | 0 |
| 04_method | 25 | 98 | 66 | 0 |
| 05_results | 23 | 93 | 59 | 0 |
| 06_discussion | 18 | 98 | 88 | 0 |
| 07_conclusion | 3 | 87 | 85 | 0 |
| 08_declarations | 4 | 85 | 65 | 0 |
| S_supplement | 16 | 93 | 35 | 0 |
| **all** | 123 | 95 | 35 | 0 |

Five lowest-percentile paragraphs (section, source line): S_supplement L485 (35); S_supplement L172 (50); 01_intro L15 (54); S_supplement L79 (55); 01_intro L27 (56)

## Overlap with the corpus and the open exemplar texts (6-gram containment)

Sources: 58 full texts (Paper A style corpus, open exemplars on disk, shared SUSCOM and top-field corpora). Sentences with at least 10 words: 587; sentences with containment at least 0.30: 0. This is a partial substitute for a commercial plagiarism database: it does not search paywalled or web content.

| section | maximum sentence containment | line | source |
|---|---|---|---|
| 02_related | 0.07 | 12 | paperA_corpus:SUSCOM_S2210537926002088 |

Five highest sentences: 0.07 02_related L12 (paperA_corpus:SUSCOM_S2210537926002088); 0.05 02_related L16 (paperA_corpus:SUSCOM_S2210537926001083); 0.00 S_supplement L796 (); 0.00 S_supplement L754 (); 0.00 S_supplement L712 ()

## Extra filters applied here (on top of the toolchain's own filters)

- front-matter placeholders, keyword line, table-file macros; standard declaration wording flagged by overlap; LanguageTool rules triggered by inline math or code identifiers kept as text (THE_SENT_END, DT_PRP, NON_STANDARD_WORD, WORD_CONTAINS_UNDERSCORE, THE_SUPERLATIVE on a math letter).

## All findings


### 00_frontmatter

- L15 [clarity] coedit/GEC: CoEdIT proposes a correction: p 0.0005 -> p0.0005 -> Tests of the saving, the cost of the requested walltime, and its recovery by prediction (H1 to H3) are supported on PM100 (p0.0005, Holm-adjusted 0.0015); the other traces are secondary replications.  
  > Tests of the saving, the cost of the requested walltime and its recovery by prediction (H1 to H3) are supported on PM100 (p<0.0005, Holm-adjusted <0.0015); the other traces are secondary replications.
- L15 [clarity] custom/SENT_LEN_45: Sentence has 52 words (limit 45). -> Split at the first coordinating clause.  
  > Delaying jobs by up to 12 h saved N, N and N g COXe per kWh of job energy on PM100, F-DATA and KIT FH2, and N, N and N g with 24 h. At 12 h these post-hoc values convert pre-registered relative saving
- L15 [clarity] custom/ABBREV_FIRST_USE: Abbreviation KIT is used at its first main-text occurrence without a definition in the same sentence. -> Spell out the term and give (KIT).  
  > Delaying jobs by up to 12 h saved N, N and N g COXe per kWh of job energy on PM100, F-DATA and KIT FH2, and N, N and N g with 24 h. At 12 h these post-hoc values convert pre-registered relative saving
- L15 [clarity] custom/ABBREV_FIRST_USE: Abbreviation FH2 is used at its first main-text occurrence without a definition in the same sentence. -> Spell out the term and give (FH2).  
  > Delaying jobs by up to 12 h saved N, N and N g COXe per kWh of job energy on PM100, F-DATA and KIT FH2, and N, N and N g with 24 h. At 12 h these post-hoc values convert pre-registered relative saving
- L15 [clarity] custom/ABBREV_FIRST_USE: Abbreviation PM100 is used at its first main-text occurrence without a definition in the same sentence. -> Spell out the term and give (PM100).  
  > Delaying jobs by up to 12 h saved N, N and N g COXe per kWh of job energy on PM100, F-DATA and KIT FH2, and N, N and N g with 24 h. At 12 h these post-hoc values convert pre-registered relative saving
- L15 [style] vale/write-good.Passive: 'are supported' may be passive voice. Use active voice if you can.  
  > Tests of the saving, the cost of the requested walltime and its recovery by prediction (H1 to H3) are supported on PM100 (p<0.0005, Holm-adjusted <0.0015); the other traces are secondary replications.
- L15 [style] vale/write-good.Passive: 'are modeled' may be passive voice. Use active voice if you can.  
  > These are modeled bounds from a counterfactual replay of non-U.S. traces, on production-average rather than marginal intensity (a fossil-only proxy credits far less) and with free capacity, not avoide
- L20 [clarity] coedit/GEC: CoEdIT proposes a correction: perfect-information -> perfect information -> The forecast-and-request policy keeps part of the perfect information saving  
  > The forecast-and-request policy keeps part of the perfect-information saving

### 01_intro

- L9 [clarity] coedit/GEC: CoEdIT proposes a correction: with -> using -> The distance between a forecast-driven and a perfect-information scheduler is therefore already known; ReBase reports it by forecast horizon for wind-powered data centers [1], and LiteCast reports it   
  > The distance between a forecast-driven and a perfect-information scheduler is therefore already known; ReBase reports it by forecast horizon for wind-powered data centers [1], and LiteCast reports it 
- L9 [clarity] vale/write-good.Weasel: 'mostly' is a weasel word!  
  > These studies mostly give the scheduler the true carbon signal or a noise-perturbed copy of it, and most give it the true job length.
- L9 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> an -> Wiesner et al. compare an optimal signal with forecasts that carry an injected error, Sukprasert et al. include a prediction-error scenario, and Attenni et al. state that runtimes are assumed availabl  
  > Wiesner et al. compare an optimal signal with forecasts that carry injected error, Sukprasert et al. include a prediction-error scenario, and Attenni et al. state that runtimes are assumed available t
- L9 [style] vale/write-good.Passive: 'been developed' may be passive voice. Use active voice if you can.  
  > Simulation studies place delay-tolerant jobs at low-carbon hours [1], a production system shifts flexible load with day-ahead forecasts [1], and the forecast itself has been developed as a separate pr
- L9 [style] vale/write-good.Passive: 'are assumed' may be passive voice. Use active voice if you can.  
  > Wiesner et al. compare an optimal signal with forecasts that carry injected error, Sukprasert et al. include a prediction-error scenario, and Attenni et al. state that runtimes are assumed available t
- L11 [style] vale/write-good.Passive: 'is built' may be passive voice. Use active voice if you can.  
  > Its forecast is built from past data only, and its runtime information is the walltime that the user requested at submission, an upper bound that the system enforces by killing the job.
- L13 [clarity] custom/SENT_LEN_45: Sentence has 56 words (limit 45). -> Split at the first coordinating clause.  
  > In the studies compared in Section 1 (Table 1), the gap between a scheduler with realistic inputs and a perfect-information scheduler is reported for forecast error alone, or for simulated job-length 
- L13 [style] coedit/GEC: CoEdIT proposes a correction: the -> a -> A saving that holds only under perfect inputs is an upper bound, and a decision to assess carbon-aware delay needs a saving that survives imperfect inputs.  
  > A saving that holds only under perfect inputs is an upper bound, and a decision to assess carbon-aware delay needs the saving that survives imperfect inputs.
- L13 [style] vale/write-good.Passive: 'is reported' may be passive voice. Use active voice if you can.  
  > In the studies compared in Section 1 (Table 1), the gap between a scheduler with realistic inputs and a perfect-information scheduler is reported for forecast error alone, or for simulated job-length 
- L15 [error] coedit/GEC: CoEdIT proposes a correction: limits -> limitations -> Four limitations frame these numbers; the first is that the replay is a counterfactual because jobs from non-U.S. systems run on U.S. signals at their local clock time.  
  > Four limits frame these numbers; the first is that the replay is a counterfactual, because jobs from non-U.S. systems run on U.S. signals at their local clock time.
- L15 [clarity] coedit/GEC: CoEdIT proposes a correction: (none) -> system -> Figure 1 shows what the deployed system and the perfect-information scheduler each see.  
  > Figure 1 shows what the deployed and the perfect-information scheduler each see.
- L15 [clarity] coedit/CLARITY_REWRITE: CoEdIT rewrite is 17% shorter with the same numbers and placeholders. -> A forecast-free threshold rule, added after the freeze, saved more than D on PM100 and KIT FH2, and history-based prediction saved more than that rule on all three traces.  
  > A forecast-free threshold rule, added after the freeze, saved more than D on PM100 and KIT FH2, and the forecast planner with the history-based prediction saved more than that rule on all three traces
- L15 [clarity] custom/SENT_LEN_45: Sentence has 53 words (limit 45). -> Split at the first coordinating clause.  
  > At 12 h of slack, delay scheduling with a past-only LightGBM forecast and the requested walltime saved N, N and N g COXe per kWh of job energy on PM100, F-DATA and KIT FH2 (a post-hoc conversion of th
- L15 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> The -> The run-now means were N, N, and N g COXe per kWh, so the relative savings are N, N, and N of run-now emissions.  
  > Run-now means were N, N and N g COXe per kWh, so the relative savings are N, N and N of run-now emissions.
- L15 [style] coedit/GEC: CoEdIT proposes a correction: by -> with -> Replacing the requested walltime with a prediction from the user's earlier jobs raised the saving on all three traces.  
  > Replacing the requested walltime by a prediction from the user's earlier jobs raised the saving on all three traces.
- L15 [style] coedit/GEC: CoEdIT proposes a correction: a -> (none) -> The pre-registered test of the saving of D is confirmatory on PM100 and secondary replication on the other two traces.  
  > The pre-registered test of the saving of D is confirmatory on PM100 and a secondary replication on the other two traces.
- L15 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> by -> The signal is production-average intensity, so the savings are not avoided by marginal emissions.  
  > The signal is production-average intensity, so the savings are not avoided marginal emissions.
- L17 [clarity] coedit/CLARITY_REWRITE: CoEdIT rewrite is 28% shorter with the same numbers and placeholders. -> Carbon intensity is the average, production-based, location-based intensity of an entity that balances supply and demand on a section of the U.S. grid.  
  > Carbon intensity is the average, production-based, location-based intensity of a balancing authority (BA), an entity that balances supply and demand on a section of the U.S. grid and reports to the U.
- L17 [style] vale/write-good.Passive: 'is known' may be passive voice. Use active voice if you can.  
  > The forecast-and-request arm D uses only what is known at submission, under the data-availability assumption of Section 1 that the intensity of the hour just ended is available at arrival; the label d
- L21 [clarity] coedit/GEC: CoEdIT proposes a correction: perfect-information -> perfect information -> We split the gap between a perfect information and a forecast-and-request delay scheduler into a forecast term, a runtime term, and their interaction, using a signal-by-runtime-estimate design with a   
  > We split the gap between a perfect-information and a forecast-and-request delay scheduler into a forecast term, a runtime term and their interaction, using a signal-by-runtime-estimate design with a d
- L21 [clarity] custom/SENT_LEN_45: Sentence has 57 words (limit 45). -> Split at the first coordinating clause.  
  > We split the gap between a perfect-information and a forecast-and-request delay scheduler into a forecast term, a runtime term and their interaction, using a signal-by-runtime-estimate design with a d
- L22 [clarity] custom/SENT_LEN_45: Sentence has 48 words (limit 45). -> Split at the first coordinating clause.  
  > We measure the saving that survives realistic inputs, a trained past-only forecast and the user-requested walltime, in absolute (g COXe per kWh) and relative terms and as a share of the same planner's
- L22 [style] coedit/GEC: CoEdIT proposes a correction: the -> (none) -> We measure the saving that survives realistic inputs, a trained past-only forecast and user-requested walltime, in absolute (g COXe per kWh) and relative terms and as a share of the same planner's per  
  > We measure the saving that survives realistic inputs, a trained past-only forecast and the user-requested walltime, in absolute (g COXe per kWh) and relative terms and as a share of the same planner's
- L24 [style] coedit/GEC: CoEdIT proposes a correction: in -> on -> We release code, derived data, the result ledger, the pre-registration, and its checksum on Zenodo so that every number on the paper traces to a ledger key.  
  > We release code, derived data, the result ledger, the pre-registration and its checksum on Zenodo, so that every number in the paper traces to a ledger key.

### 02_related

- L6 [clarity] coedit/GEC: CoEdIT proposes a correction: beside -> alongside -> Sukprasert et al. [1] extend the evaluation to 123 regions with synthetic job classes that differ in length, deadline, and interruptibility, report ideal upper bounds alongside simple and sophisticate  
  > Sukprasert et al. [1] extend the evaluation to 123 regions with synthetic job classes that differ in length, deadline and interruptibility, report ideal upper bounds beside simple and sophisticated po
- L6 [clarity] coedit/GEC: CoEdIT proposes a correction: Radovanovi c -> Radovanovi'c; (none) -> the -> Radovanovi'c et al. [1] report a production system that shifts the flexible load of a large cloud fleet using day-ahead carbon forecasts.  
  > Radovanovi\'c et al. [1] report a production system that shifts flexible load of a large cloud fleet using day-ahead carbon forecasts.
- L8 [clarity] vale/write-good.Weasel: 'several' is a weasel word!  
  > CarbonCast [1] forecasts grid carbon intensity several days ahead from source-level forecasts.
- L12 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> the -> Attenni et al. [1] simulate the spatial, temporal, and spatio-temporal shifting of cloud workloads over carbon, water, and land use.  
  > Attenni et al. [1] simulate spatial, temporal and spatio-temporal shifting of cloud workloads over carbon, water and land use.
- L12 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> to be -> They state that job runtimes are assumed to be known to the scheduler and that a trained operational forecaster remains future work; these are the two inputs measured here.  
  > They state that job runtimes are assumed known to the scheduler and that a trained operational forecaster remains future work; these are the two inputs measured here.
- L12 [style] vale/write-good.Passive: 'are assumed' may be passive voice. Use active voice if you can.  
  > They state that job runtimes are assumed known to the scheduler and that a trained operational forecaster remains future work; these are the two inputs measured here.
- L14 [clarity] coedit/CLARITY_REWRITE: CoEdIT rewrite is 21% shorter with the same numbers and placeholders. -> It reports this gap to the oracle by forecast horizon, from 1.03 percent at the shortest to 11.33 percent at the longest.  
  > It reports the wind-utilization gap of its own method to the oracle by forecast horizon, from 1.03 percent at the shortest horizon to 11.33 percent at the longest.
- L14 [clarity] vale/write-good.TooWordy: 'utilization' is too wordy.  
  > It reports the wind-utilization gap of its own method to the oracle by forecast horizon, from 1.03 percent at the shortest horizon to 11.33 percent at the longest.
- L14 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> the -> Its tasks are unit tasks of equal energy, so no job runtime enters, and the gap is attributed to the forecast error alone.  
  > Its tasks are unit tasks of equal energy, so no job runtime enters, and the gap is attributed to forecast error alone.
- L14 [style] coedit/GEC: CoEdIT proposes a correction: as -> (none) -> Their interval is over three task profiles, and forecast error is named a limitation.  
  > Their interval is over three task profiles, and forecast error is named as a limitation.
- L21 [error] coedit/GEC: CoEdIT proposes a correction: schedule -> schedules -> Tsafrir et al. [1] keep user estimates only as kill times and schedules with the mean runtime of the user's last two jobs.  
  > Tsafrir et al. [1] keep user estimates only as kill times and schedule with the mean runtime of the user's last two jobs.
- L21 [clarity] vale/write-good.TooWordy: 'utilization' is too wordy.  
  > These works target waiting time and utilization, not carbon.
- L21 [style] vale/write-good.Passive: 'are killed' may be passive voice. Use active voice if you can.  
  > Mu'alem and Feitelson [1] find user estimates on three IBM SP2 logs to be rather poor but a good upper bound, because few jobs are killed at their limit.
- L27 [error] coedit/GEC: CoEdIT proposes a correction: recorded -> records -> LACS [1] varies simulated forecast error and simulated length error separately for elastic jobs on one grid; the present study replaces both with a trained forecaster and records requested walltimes a  
  > LACS [1] varies simulated forecast error and simulated length error separately for elastic jobs on one grid; the present study replaces both with a trained forecaster and recorded requested walltimes,
- L27 [clarity] coedit/CLARITY_REWRITE: CoEdIT rewrite is 24% shorter with the same numbers and placeholders. -> We did not find any evaluation that combined a past-only carbon forecast, requested walltimes, and real HPC traces among the three outside works compared above.  
  > Among the three outside works compared above, we did not find an evaluation that combines a past-only carbon forecast, requested walltimes and real HPC traces; this statement is limited to the papers 
- L27 [style] coedit/GEC: CoEdIT proposes a correction: is -> has; (none) -> been -> A forecast-to-oracle gap has already been reported for wind-powered unit tasks by forecast horizon [1] and for a lightweight forecaster on 50 regions with a KIT FH2 replay [1].  
  > A forecast-to-oracle gap is already reported for wind-powered unit tasks by forecast horizon [1] and for a lightweight forecaster on 50 regions with a KIT FH2 replay [1].
- L27 [style] vale/write-good.Passive: 'is limited' may be passive voice. Use active voice if you can.  
  > Among the three outside works compared above, we did not find an evaluation that combines a past-only carbon forecast, requested walltimes and real HPC traces; this statement is limited to the papers 

### 03_data

- L8 [error] coedit/GEC: CoEdIT proposes a correction: generation -> generated -> For BA b and hour t, the carbon intensity is the generation-weighted mean of lifecycle emission factors, X, in g COXe per kWh (grams of COX-equivalent), where X is generated from fuel f and X its fact  
  > For BA b and hour t, the carbon intensity is the generation-weighted mean of lifecycle emission factors, X, in g COXe per kWh (grams of COX-equivalent), where X is generation from fuel f and X its fac
- L8 [clarity] vale/write-good.TooWordy: 'Monitor' is too wordy.  
  > Energy Information Administration (EIA) Form EIA-930 Hourly Electric Grid Monitor, which reports hourly net generation by fuel for balancing authorities (BAs) [1].
- L8 [clarity] vale/write-good.TooWordy: 'equivalent' is too wordy.  
  > For BA b and hour t, the carbon intensity is the generation-weighted mean of lifecycle emission factors, X, in g COXe per kWh (grams of COX-equivalent), where X is generation from fuel f and X its fac
- L8 [style] coedit/GEC: CoEdIT proposes a correction: are -> is -> The six-month balance files from 2018 H2 to 2026 H1 are used for N candidate BAs, and the data is in the public domain.  
  > The six-month balance files from 2018 H2 to 2026 H1 are used for N candidate BAs, and the data are in the public domain.
- L12 [style] coedit/GEC: CoEdIT proposes a correction: an -> (none) -> The unknown-fuel share is zero in every eligible BA, and accounting-factor sensitivity (S3) is described in Section 1.  
  > The unknown-fuel share is zero in every eligible BA, and an accounting-factor sensitivity (S3) is described in Section 1.
- L14 [style] coedit/GEC: CoEdIT proposes a correction: on -> to -> Cleaning follows four fixed rules, none tuned to development or test data.  
  > Cleaning follows four fixed rules, none tuned on development or test data.
- L16 [style] coedit/GEC: CoEdIT proposes a correction: The -> (none) -> Fuel-column mapping showed no schema-induced jump at the July 2024 schema change in any eligible BA.  
  > The fuel-column mapping showed no schema-induced jump at the July 2024 schema change in any eligible BA.
- L18 [clarity] coedit/GEC: CoEdIT proposes a correction: (none) -> based -> The BAs are selected based on data coverage and are not a sample, so the inference target is this fixed set (Section 1).  
  > The BAs are selected on data coverage and are not a sample, so the inference target is this fixed set (Section 1).
- L20 [error] languagetool/THE_PUNCT: Articles like ‘a’ are rarely followed by punctuation. A word may be missing after ‘a’, or the punctuation mark may not be necessary. [a,] -> a  
  > The frozen design assumes that, at arrival, the intensity of the hour ending at X is available at a, the moment of arrival.
- L20 [clarity] languagetool/EN_A_VS_AN: Use “an” instead of ‘a’ if the following word starts with a vowel sound, e.g. ‘an article’, ‘an hour’. [a] -> an  
  > The planner needs data that a deployed scheduler would hold at the arrival time a of the job.
- L20 [style] coedit/GEC: CoEdIT proposes a correction: a -> (none) -> The planner needs data that a deployed scheduler would hold at the arrival time of the job.  
  > The planner needs data that a deployed scheduler would hold at the arrival time a of the job.
- L20 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> The -> The EIA states that net generation by source is typically published by 11:00 Eastern on the next day, and that values are revised afterward [1].  
  > EIA states that net generation by source is typically published by 11:00 Eastern on the next day, and that values are revised afterward [1].
- L24 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> The -> The PM100 comes from the Marconi100 system at CINECA in Bologna and holds Slurm records with sampled node power [1].  
  > PM100 comes from the Marconi100 system at CINECA in Bologna and holds Slurm records with sampled node power [1].
- L26 [style] vale/write-good.Passive: 'is used' may be passive voice. Use active voice if you can.  
  > The KIT FH2 log is used under the citation request of the Parallel Workloads Archive [1], with the acknowledgement that the archive asks for (see the Acknowledgements).
- L28 [style] vale/write-good.Passive: 'is standardized' may be passive voice. Use active voice if you can.  
  > Each trace is standardized to the same fields: submit time in local site time, requested walltime X, actual runtime X, final state, user and the mean power P of the job.
- L30 [clarity] vale/write-good.Weasel: 'usually' is a weasel word!  
  > Older studies of other machines also find that user estimates are poor [1] but usually safe upper bounds [1].
- L32 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> its -> Every KIT FH2 job has its status completed, so timeouts cannot be identified there, although N of its jobs run to within 2 % of the limit.  
  > Every KIT FH2 job has status completed, so timeouts cannot be identified there, although N of its jobs run to within 2 % of the limit.
- L32 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> will -> Jobs that run to the limit are censored in runtime; we will return to them in Section 1 and in the limitations.  
  > Jobs that run to the limit are censored in runtime; we return to them in Section 1 and in the limitations.
- L32 [style] vale/write-good.Passive: 'be identified' may be passive voice. Use active voice if you can.  
  > Every KIT FH2 job has status completed, so timeouts cannot be identified there, although N of its jobs run to within 2 % of the limit.
- L34 [style] coedit/GEC: CoEdIT proposes a correction: a -> (none) -> A job table records completed work and not a queue, so it carries no capacity constraint, and the replay is bound under free capacity.  
  > A job table records completed work and not a queue, so it carries no capacity constraint, and the replay is a bound under free capacity.
- L34 [style] vale/write-good.Passive: 'be read' may be passive voice. Use active voice if you can.  
  > A fourth trace, the NLR Kestrel jobs data, would have matched both the EIA-930 years and a U.S. site, but its host returned a maintenance error on two attempts and its license could not be read, so it
- L38 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> The -> The TEST (2025-07-01 to 2026-06-30) was scored once after the pre-registration was frozen.  
  > TEST (2025-07-01 to 2026-06-30) was scored once, after the pre-registration was frozen.
- L40 [style] coedit/GEC: CoEdIT proposes a correction: in -> from -> The traces were recorded from 2016 to 2018 (KIT FH2), 2020 (PM100), and 2021 and 2023 (F-DATA).  
  > The traces were recorded in 2016 to 2018 (KIT FH2), 2020 (PM100) and 2021 and 2023 (F-DATA).
- L40 [style] vale/write-good.Passive: 'is replayed' may be passive voice. Use active voice if you can.  
  > A job that arrived on a given weekday and clock time at its home site is replayed on a U.S. grid at that weekday and clock time in the BA's standard local time.

### 04_method

- L10 [clarity] custom/SENT_LEN_45: Sentence has 51 words (limit 45). -> Split at the first coordinating clause.  
  > Candidate starts lie on a 15-min grid, X The planner sees a signal X, piecewise constant on 98 hourly intervals that begin at X. This width covers the longest plan and realization window, X h, for eve
- L10 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> of -> A slack of X h is the longest delay a scheduler may impose; 12 h is the primary value.  
  > A slack X h is the longest delay a scheduler may impose; 12 h is the primary value.
- L10 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> a -> Candidate starts lie on a 15-min grid, X The planner sees a signal X, a piecewise constant on 98 hourly intervals that begin at X. This width covers the longest plan and realization window, X h, for e  
  > Candidate starts lie on a 15-min grid, X The planner sees a signal X, piecewise constant on 98 hourly intervals that begin at X. This width covers the longest plan and realization window, X h, for eve
- L23 [clarity] custom/SENT_LEN_45: Sentence has 47 words (limit 45). -> Split at the first coordinating clause.  
  > Realized emissions are then scored on the actual intensity X over the true run, X which is in g COXe when P is in W, c in g COXe per kWh and t in h. Any job whose 98-interval window touches an unusabl
- L23 [style] vale/write-good.Passive: 'is excluded' may be passive voice. Use active voice if you can.  
  > Realized emissions are then scored on the actual intensity X over the true run, X which is in g COXe when P is in W, c in g COXe per kWh and t in h. Any job whose 98-interval window touches an unusabl
- L62 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> as -> An arm pairs a signal with a runtime estimate and is written as signal|estimate.  
  > An arm pairs a signal with a runtime estimate and is written signal|estimate.
- L64 [style] vale/write-good.Passive: 'was selected' may be passive voice. Use active voice if you can.  
  > It was selected on DEV, before the test year was scored, because the final forecaster beat the seasonal naive day on 1 to 24 h error in most BAs (Section 1).
- L64 [style] vale/write-good.Passive: 'was scored' may be passive voice. Use active voice if you can.  
  > It was selected on DEV, before the test year was scored, because the final forecaster beat the seasonal naive day on 1 to 24 h error in most BAs (Section 1).
- L66 [clarity] languagetool/EN_COMPOUNDS_QUARTER_HOUR: This word is normally spelled with a hyphen. [quarter hour] -> quarter-hour  
  > The first is a forecast-free threshold rule that starts at the first quarter hour whose observed intensity lies below its trailing 7-day 25th percentile (else at a+S).
- L70 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> the -> It predicts the difference between the actual intensity and the profile7 value under an absolute-error objective.  
  > It predicts the difference between actual intensity and the profile7 value, under an absolute-error objective.
- L75 [clarity] coedit/GEC: CoEdIT proposes a correction: (none) -> into -> Inputs repaired by interpolation or outlier replacement are replaced by the last earlier unflagged value, so repairs cannot leak into the future.  
  > Inputs repaired by interpolation or outlier replacement are replaced by the last earlier unflagged value, so repairs cannot leak the future.
- L77 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> a -> On DEV, the forecaster had a lower 1 to 24 h mean absolute error than the seasonal naive day in N of N BAs and lower than profile7 in N of them.  
  > On DEV, the forecaster had lower 1 to 24 h mean absolute error than the seasonal naive day in N of N BAs and lower than profile7 in N of them.
- L77 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> the -> A lower error does not imply a higher saving since the planner uses only the ranking of intensities inside a window, so saving is reported beside the error rather than inferred from it.  
  > A lower error does not imply a higher saving, since the planner uses only the ranking of intensities inside a window, so saving is reported beside error rather than inferred from it.
- L77 [style] vale/write-good.Passive: 'is reported' may be passive voice. Use active voice if you can.  
  > A lower error does not imply a higher saving, since the planner uses only the ranking of intensities inside a window, so saving is reported beside error rather than inferred from it.
- L81 [style] vale/write-good.Passive: 'was submitted' may be passive voice. Use active voice if you can.  
  > It is the mean actual runtime of the user's two most recent jobs that ended before this job was submitted in state COMPLETED or TIMEOUT, capped at the request, X
- L88 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> was -> The factor 2 in pred2 was fixed before any test result and was not tuned.  
  > The factor 2 in pred2 was fixed before any test result and not tuned.
- L92 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> The; the -> (none) -> The clock time is read in BA's standard local time (a fixed offset, with no daylight saving shift).  
  > Clock time is read in the BA's standard local time (a fixed offset, with no daylight saving shift).
- L92 [style] coedit/GEC: CoEdIT proposes a correction: on -> to -> Outcomes are summed per arrival day and per runtime class, and the replicates are added to a common calendar-day index.  
  > Outcomes are summed per arrival day and per runtime class, and the replicates are added on a common calendar-day index.
- L128 [clarity] custom/SENT_LEN_45: Sentence has 51 words (limit 45). -> Split at the first coordinating clause.  
  > The saving of an arm is one minus its emissions over the run-now emissions, pooled over BAs, days, runtime classes and replicates, X Because jobs are pooled before the ratio is taken, X is carbon-weig
- L128 [style] vale/write-good.Passive: 'are pooled' may be passive voice. Use active voice if you can.  
  > The saving of an arm is one minus its emissions over the run-now emissions, pooled over BAs, days, runtime classes and replicates, X Because jobs are pooled before the ratio is taken, X is carbon-weig
- L128 [style] vale/write-good.Passive: 'is taken' may be passive voice. Use active voice if you can.  
  > The saving of an arm is one minus its emissions over the run-now emissions, pooled over BAs, days, runtime classes and replicates, X Because jobs are pooled before the ratio is taken, X is carbon-weig
- L133 [clarity] custom/SENT_LEN_45: Sentence has 52 words (limit 45). -> Split at the first coordinating clause.  
  > The three confirmatory hypotheses, tested on PM100 at X h, concern X where each hypothesis states X. H1 says that the forecast-and-request arm D saves emissions, H2 that knowing the actual runtime add
- L140 [clarity] coedit/GEC: CoEdIT proposes a correction: (none) -> expressed -> Differences of savings are expressed in percentage points (pp).  
  > Differences of savings are in percentage points (pp).
- L161 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> the -> Relative savings hide the scale, so absolute effects are also reported.  
  > Relative savings hide scale, so absolute effects are also reported.
- L161 [style] vale/write-good.Passive: 'were added' may be passive voice. Use active voice if you can.  
  > With the job energy X in kWh (X in W, X in h) and X in g COXe per kWh of job energy, X The absolute effects were added after the freeze (post-hoc) from the saved results.
- L167 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> The -> The mean start delay, X, is reported per arm.  
  > Mean start delay, X, is reported per arm.
- L171 [style] vale/write-good.Passive: 'are cut' may be passive voice. Use active voice if you can.  
  > For each BA, the per-day sums of Algorithm 1 are cut into consecutive 7-day blocks that start at the BA's first arrival day, and a remainder shorter than 7 days is kept fixed.
- L171 [style] vale/write-good.Passive: 'is kept' may be passive voice. Use active voice if you can.  
  > For each BA, the per-day sums of Algorithm 1 are cut into consecutive 7-day blocks that start at the BA's first arrival day, and a remainder shorter than 7 days is kept fixed.
- L176 [clarity] coedit/GEC: CoEdIT proposes a correction: (none) -> being -> It treats the job sample as fixed and describes weather and calendar variation within each BA, with the BAs being resampled independently.  
  > It treats the job sample as fixed and describes weather and calendar variation within each BA, with the BAs resampled independently.
- L176 [style] coedit/GEC: CoEdIT proposes a correction: the -> a -> It is called a calendar interval.  
  > It is called the calendar interval.
- L178 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> and -> The synchronized-week interval (post-hoc, PH1) uses the same week indices for all BAs in each draw, with blocks aligned on the calendar weeks of the common test span (N blocks), and X with the same se  
  > The synchronized-week interval (post-hoc, PH1) uses the same week indices for all BAs in each draw, with blocks aligned on the calendar weeks of the common test span (N blocks), X with the same seed r
- L183 [style] vale/write-good.Passive: 'are shared' may be passive voice. Use active voice if you can.  
  > Pooling over BAs first is exact because the indices are shared; the same code gives an interval for the difference X and for each Shapley term under both bootstraps.
- L185 [clarity] coedit/GEC: CoEdIT proposes a correction: original-users -> original user -> It resamples users with replacement, draws a new job sample and alignment from the resampled pool, and then applies the frozen blocks, with N outer draws and N inner draws each, plus an original user   
  > It resamples users with replacement, draws a new job sample and alignment from the resampled pool, and then applies the frozen blocks, with N outer draws and N inner draws each, plus an original-users
- L185 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> is; (none) -> is -> The check reports a normal-approximation total by the law of total variance beside the percentile version, X, where X is the frozen estimate, X is the variance of the frozen calendar-bootstrap draws,   
  > The check reports a normal-approximation total by the law of total variance beside the percentile version, X where X is the frozen estimate, X the variance of the frozen calendar-bootstrap draws and X
- L194 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> an -> For H1 to H3, the one-sided p-value is null-centered with an estimate T and draws X, X so the smallest attainable value is X, written p  0.0005.  
  > For H1 to H3 the one-sided p-value is null-centered: with estimate T and draws X, X so the smallest attainable value is X, written p < 0.0005.
- L238 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> has -> Nothing in the frozen code or estimates has changed.  
  > Nothing in the frozen code or estimates changed.
- L238 [style] vale/write-good.Passive: 'are recorded' may be passive voice. Use active voice if you can.  
  > The simulator refuses the test period unless the md5 sum of the registration (starting cfe98401) matches the stored value, and the sums of the five analysis scripts are recorded.
- L238 [style] vale/write-good.Passive: 'was written' may be passive voice. Use active voice if you can.  
  > The secondary-analysis code was written after the test run and only reads saved results (row 3), and test arrivals span 2025-07-07 to 2026-06-14 (row 4), and the post-hoc inference below was added (ro
- L238 [style] vale/write-good.Passive: 'was added' may be passive voice. Use active voice if you can.  
  > The secondary-analysis code was written after the test run and only reads saved results (row 3), and test arrivals span 2025-07-07 to 2026-06-14 (row 4), and the post-hoc inference below was added (ro
- L240 [clarity] coedit/GEC: CoEdIT proposes a correction: run -> running -> An item that did not run is stated as not running.  
  > An item that did not run is stated as not run.
- L240 [clarity] custom/SENT_LEN_45: Sentence has 64 words (limit 45). -> Split at the first coordinating clause.  
  > They are the synchronized-week interval, Shapley-term intervals, per-BA H2 intervals, absolute effects, the paired comparison of lgbm|req with profile7|req, and saving per hour of delay; B1 to B4 add 
- L240 [style] vale/write-good.Passive: 'is reported' may be passive voice. Use active voice if you can.  
  > A post-freeze result is reported beside the frozen value and is never promoted to a confirmatory claim; the analysis registry in the supplement lists every analysis with its status, file and ledger.
- L242 [style] coedit/GEC: CoEdIT proposes a correction: in -> on; (none) -> a -> Every number on the paper is read from a ledger written by a script from saved results.  
  > Every number in the paper is read from a ledger written by script from saved results.
- L244 [style] coedit/GEC: CoEdIT proposes a correction: of -> for -> The package holds an environment lock file, the md5 sum of every result and forecast file, and the commands for each run.  
  > The package holds an environment lock file, the md5 sum of every result and forecast file, and the commands of each run.

### 05_results

- L10 [clarity] coedit/GEC: CoEdIT proposes a correction: (none) -> would have -> Every estimate is a replay; it states what a job trace would have emitted under each arm on the N grids in the test year, and not what a facility would have emitted.  
  > Every estimate is a replay: it states what a job trace would have emitted under each arm on the N grids in the test year, and not what a facility emitted.
- L10 [style] coedit/GEC: CoEdIT proposes a correction: the -> a -> The calendar interval is the frozen block bootstrap, and the synchronized-week interval is a post-hoc variant that shares week indices across BAs (Section 1).  
  > The calendar interval is the frozen block bootstrap, and the synchronized-week interval is the post-hoc variant that shares week indices across BAs (Section 1).
- L10 [style] languagetool/ON_SKYPE: The name of this brand needs to be capitalized. [slack] -> Slack  
  > Every other result is secondary, post-hoc or exploratory, and slack is X h unless stated.
- L14 [style] vale/write-good.Passive: 'is replayed' may be passive voice. Use active voice if you can.  
  > The three values are close because every trace is replayed on the same grids in the same year, so savings per kWh are the better cross-trace comparison.
- L16 [clarity] coedit/GEC: CoEdIT proposes a correction: p 0.0005 -> p0.0005 -> In relative terms, D saves N of run-now emissions on PM100 (calendar interval N to N; synchronized-week interval N to N), and H1 is supported (p0.0005, Holm-adjusted 0.0015).  
  > In relative terms, D saves N of run-now emissions on PM100 (calendar interval N to N; synchronized-week interval N to N), and H1 is supported (p<0.0005, Holm-adjusted <0.0015).
- L16 [clarity] coedit/CLARITY_REWRITE: CoEdIT rewrite is 35% shorter with the same numbers and placeholders. -> The perfect information arm saves N (calendar interval N to N), so D keeps N of it.  
  > The perfect-information arm saves N (calendar interval N to N), so D keeps N of it (calendar interval N to N; synchronized-week interval N to N).
- L16 [style] vale/write-good.Passive: 'is supported' may be passive voice. Use active voice if you can.  
  > In relative terms, D saves N of run-now emissions on PM100 (calendar interval N to N; synchronized-week interval N to N), and H1 is supported (p<0.0005, Holm-adjusted <0.0015).
- L22 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> and -> Secondary (forecast skill), post-hoc and descriptive (decomposition), and confirmatory on PM100 (H3).  
  > Secondary (forecast skill), post-hoc and descriptive (decomposition), confirmatory on PM100 (H3).
- L22 [style] coedit/GEC: CoEdIT proposes a correction: the -> (none) -> Error alone does not say whether the forecaster matters for saving.  
  > Error alone does not say whether the forecaster matters for the saving.
- L22 [style] coedit/GEC: CoEdIT proposes a correction: by -> with -> Replacing it with profile7 under the requested walltime lowers the saving by N on PM100 (calendar interval N to N; synchronized-week interval N to N), by N on F-DATA and by N on KIT FH2, and all three  
  > Replacing it by profile7 under the requested walltime lowers the saving by N on PM100 (calendar interval N to N; synchronized-week interval N to N), by N on F-DATA and by N on KIT FH2, and all three i
- L26 [clarity] coedit/GEC: CoEdIT proposes a correction: p 0.0005 -> p0.0005 -> The prediction recovery H3 is N on PM100 (calendar interval N to N; synchronized-week interval N to N), and H3 is supported (p0.0005, Holm-adjusted 0.0015).  
  > The prediction recovery H3 is N on PM100 (calendar interval N to N; synchronized-week interval N to N), and H3 is supported (p<0.0005, Holm-adjusted <0.0015).
- L26 [style] coedit/GEC: CoEdIT proposes a correction: the -> (none) -> A prediction from the user's past jobs narrows the distance between the believed and the actual runtime, which is the likely route to recovery; the replay does not test the route directly.  
  > A prediction from the user's past jobs narrows the distance between the believed and the actual runtime, which is the likely route to the recovery; the replay does not test the route directly.
- L30 [clarity] coedit/GEC: CoEdIT proposes a correction: (none) -> time; (none) -> price -> A longer window gives the planner more variation to use and more forecast lead time to get wrong, which may explain why the share price stops rising between 12 h and 24 h.  
  > A longer window gives the planner more variation to use and more forecast lead to get wrong, which may explain why the share stops rising between 12 h and 24 h.
- L30 [clarity] coedit/CLARITY_REWRITE: CoEdIT rewrite is 14% shorter with the same numbers and placeholders. -> The absolute gap between the two narrows with the slack, and the retained share moves less regularly. SEP> The retained share has no meaning without the slack, so it is read together with the absolute  
  > The absolute gap between the two widens with the slack, and the retained share moves less regularly, at N, N, N and N. The retained share has no meaning independent of the slack, so it is read togethe
- L30 [style] vale/write-good.Passive: 'is read' may be passive voice. Use active voice if you can.  
  > The absolute gap between the two widens with the slack, and the retained share moves less regularly, at N, N, N and N. The retained share has no meaning independent of the slack, so it is read togethe
- L34 [clarity] coedit/GEC: CoEdIT proposes a correction: a -> (none); oracle -> ORA -> One BA, SPA, has constant intensity in the test year, so its ORA saving is zero, and its retained share is undefined.  
  > One BA, SPA, has a constant intensity in the test year, so its oracle saving is zero and its retained share is undefined.
- L36 [style] vale/write-good.Passive: 'are unadjusted' may be passive voice. Use active voice if you can.  
  > These correlations are unadjusted and computed over the fixed set of BAs; the values for F-DATA and KIT FH2 are in Table 1, all eight correlations are in Table 1, and the replay does not test why they
- L38 [clarity] coedit/GEC: CoEdIT proposes a correction: perfect-information -> perfect information -> By job length, the perfect information saving on PM100 falls from N for jobs under 1 h to N for jobs of 12 h or more.  
  > By job length, the perfect-information saving on PM100 falls from N for jobs under 1 h to N for jobs of 12 h or more.
- L38 [clarity] coedit/GEC: CoEdIT proposes a correction: N -> (none) -> D keeps N of the saving in the shortest class, N and N in the two middle classes, and N in the longest, which holds N of the replayed jobs (Figure 1).  
  > D keeps N of the saving in the shortest class, N and N in the two middle classes and N in the longest, which holds N of the N replayed jobs (Figure 1).
- L42 [clarity] coedit/GEC: CoEdIT proposes a correction: (none) -> shown -> The retained shares of the two traces are shown in Table 1.  
  > The retained shares of the two traces are in Table 1.
- L42 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> the -> Secondary; replications in the direction, never confirmations.  
  > Secondary; replications in direction, never confirmations.
- L46 [style] vale/write-good.Passive: 'is chosen' may be passive voice. Use active voice if you can.  
  > The forecast-and-request arm thus waits about as long as the perfect-information arm and realizes a smaller saving per hour of waiting, as expected when the window is chosen with imperfect inputs.
- L50 [error] coedit/GEC: CoEdIT proposes a correction: describes -> describe -> The calendar and synchronized-week intervals describe weather and calendar variation over the fixed BAs, the two-stage interval adds variation across BAs, and none of them describe the job sample.  
  > The calendar and synchronized-week intervals describe weather and calendar variation over the fixed BAs, the two-stage interval adds variation across BAs, and none of them describes the job sample.
- L52 [clarity] coedit/CLARITY_REWRITE: CoEdIT rewrite is 14% shorter with the same numbers and placeholders. -> On every trace where the workload-sample spread is larger than the calendar spread, the total-variance intervals for D, H2 and H3 are not zero, and each of the N outer samples gives a positive value f  
  > The total-variance interval is N to N. On every trace the workload-sample spread exceeds the calendar spread, the total-variance intervals of the saving of D, H2 and H3 exclude zero, and each of the N
- L58 [clarity] custom/SENT_LEN_45: Sentence has 46 words (limit 45). -> Split at the first coordinating clause.  
  > A higher oil factor (S3b) gives N, and including jobs that hit their limit (S4) gives N. Tuning the LightGBM forecaster with a 100-trial search on the training years only (S5, exploratory; Section 1) 
- L60 [style] vale/write-good.Passive: 'is reported' may be passive voice. Use active voice if you can.  
  > These cover three traces, two signals, X and X. These are point estimates with no paired interval, so the direction is reported without a significance claim.
- L60 [style] vale/write-good.Passive: 'are marked' may be passive voice. Use active voice if you can.  
  > The requested walltime and the history prediction are marked at their measured error and not on the multiplier curve, and the padded and quantile operator rules sit beside them (Section 1).
- L62 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> or -> The rule uses no forecast and no runtime: it starts a job at the first quarter-hour whose observed intensity lies below its trailing 7-day 25th percentile, or else at the end of the window (Section 1)  
  > The rule uses no forecast and no runtime: it starts a job at the first quarter-hour whose observed intensity lies below its trailing 7-day 25th percentile, else at the end of the window (Section 1).
- L62 [style] coedit/GEC: CoEdIT proposes a correction: on -> of -> The quantile estimate gives the same ordering on every trace of the point estimates (Table 1, Panel D); no paired interval was computed for it.  
  > The quantile estimate gives the same ordering on every trace on the point estimates (Table 1, Panel D); no paired interval was computed for it.
- L64 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> a -> The runtime penalty comes from a few users (X5), and the saving accrues mainly from evening and night arrivals (X6; Sections 1 and 1).  
  > The runtime penalty comes from few users (X5), and the saving accrues mainly from evening and night arrivals (X6; Sections 1 and 1).
- L64 [style] vale/write-good.Passive: 'is unchanged' may be passive voice. Use active voice if you can.  
  > Capping the forecast lead at 24 h raised the saving of D on PM100 from N to N (X3; the frozen lead is unchanged; Section 1).
- L68 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> the -> Further exploratory detail is in the supplement with its status, the workload-sample table (S1), the arm table of the forecast-free rule and the padded and quantile estimates, the clock-shift detail,   
  > Further exploratory detail is in the supplement with its status: the workload-sample table (S1), the arm table of the forecast-free rule and the padded and quantile estimates, the clock-shift detail, 
- L68 [style] coedit/GEC: CoEdIT proposes a correction: a -> the -> None of it changes the conclusion above.  
  > None of it changes a conclusion above.

### 06_discussion

- L9 [clarity] coedit/GEC: CoEdIT proposes a correction: (none) -> up -> The interaction is not zero (N, N, and N), so the two losses do not add up.  
  > The interaction is not zero (N, N and N), so the two losses do not add.
- L13 [clarity] coedit/CLARITY_REWRITE: CoEdIT rewrite is 35% shorter with the same numbers and placeholders. -> For operators, logging the requested and the actual runtime and adding a history-based predictor to a delay planner could be worth testing in a production scheduler.  
  > For operators, logging the requested and the actual runtime and adding a history-based predictor to a delay planner could be worth testing in a production scheduler, because the prediction raised the 
- L21 [clarity] coedit/CLARITY_REWRITE: CoEdIT rewrite is 16% shorter with the same numbers and placeholders. -> Also, not every week D saves something in N of the BA-weeks on PM100. SEP> At least one BA has no positive week on every trace.  
  > The saving is also not realized in every week: D saves something in N of the BA-weeks on PM100, and at least one BA has no positive week on every trace.
- L21 [style] coedit/GEC: CoEdIT proposes a correction: in -> (none) -> The saving is also not realized every week D saves something in N of the BA-weeks on PM100, and at least one BA has no positive week on every trace.  
  > The saving is also not realized in every week: D saves something in N of the BA-weeks on PM100, and at least one BA has no positive week on every trace.
- L35 [error] coedit/GEC: CoEdIT proposes a correction: sizes -> size -> The agreement in sign across three workloads shows that the contrasts do not depend on one workload and not that a U.S. site would see the same size.  
  > The agreement in sign across three workloads shows that the contrasts do not depend on one workload, and not that a U.S. site would see the same sizes.
- L35 [clarity] coedit/GEC: CoEdIT proposes a correction: could not -> cannot -> Arrival clock time is read in each balancing authority's standard time, and a U.S. trace such as NLR Kestrel cannot be obtained.  
  > Arrival clock time is read in each balancing authority's standard time, and a U.S. trace such as NLR Kestrel could not be obtained.
- L37 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> for; on -> at -> We account for emissions at average intensity, as the temporal-shifting studies the planner follows do, and a saving in average intensity is not avoided emissions because the marginal generator at an   
  > We account emissions on average intensity, as the temporal-shifting studies the planner follows do, and a saving in average intensity is not avoided emissions, because the marginal generator at an hou
- L37 [style] vale/write-good.Passive: 'are excluded' may be passive voice. Use active voice if you can.  
  > The signal is the production-average carbon intensity of the balancing authority from EIA-930; imports and storage are excluded and three of the nine emission factors are judgment values.
- L41 [error] coedit/GEC: CoEdIT proposes a correction: saving -> savings -> Every job starts when the planner says, so the savings are bounds that a capacity-limited site cannot exceed with the same inputs, and they are not forecasts of a site's savings.  
  > Every job starts when the planner says, so the savings are bounds that a capacity-limited site cannot exceed with the same inputs, and they are not forecasts of a site's saving.
- L41 [error] languagetool/COLLECTIVE_NOUN_VERB_AGREEMENT_VBP: Possible verb agreement error. Did you mean “is”? (Some collective nouns can be treated as both singular and plural, so ‘are’ is not always incorrect.) [are] -> is  
  > Under this cap D keeps N of its uncapped saving, and N of jobs are displaced from their uncapped start (Section 1).
- L45 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> the -> The planner is given intensity up to the hour before arrival, but the EIA publishes generation by source about a day late and revises it for days afterward [1], and the archived series holds revised v  
  > The planner is given intensity up to the hour before arrival, but EIA publishes generation by source about a day late and revises it for days afterward [1], and the archived series holds revised value
- L45 [style] vale/write-good.Passive: 'is given' may be passive voice. Use active voice if you can.  
  > The planner is given intensity up to the hour before arrival, but EIA publishes generation by source about a day late and revises it for days afterward [1], and the archived series holds revised value
- L47 [error] languagetool/NOW: Did you mean “now” (at this moment) instead of ‘no’ (negation)? Or possibly even ‘not’? [no] -> now; not  
  > Power is a whole-job mean taken as constant, and energy weighting favors long jobs (in the raw PM100 log, jobs over 24 h supply N of the energy, but no analyzed PM100 job is that long).
- L47 [style] vale/write-good.Passive: 'is read' may be passive voice. Use active voice if you can.  
  > Weighting jobs equally raises D to N, N and N, so the energy-weighted headline is the more conservative of the two; KIT FH2 carries 1 kW per job and is read mainly through the unweighted rows.
- L49 [clarity] custom/ABBREV_FIRST_USE: Abbreviation MAE is used at its first main-text occurrence without a definition in the same sentence. -> Spell out the term and give (MAE).  
  > D was chosen on development MAE (it beat the seasonal naive day on 1 to 24 h error in N of N BAs), and MAE rank is not saving rank; hyperparameters were frozen before the test year, and S5 tunes the f
- L49 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> the; (none) -> of -> D was chosen on the development of MAE (it beat the seasonal naive day on 1 to 24 h error in N of N BAs), and MAE rank is not saving rank; hyperparameters were frozen before the test year, and S5 tune  
  > D was chosen on development MAE (it beat the seasonal naive day on 1 to 24 h error in N of N BAs), and MAE rank is not saving rank; hyperparameters were frozen before the test year, and S5 tunes the f
- L49 [style] vale/write-good.Passive: 'was chosen' may be passive voice. Use active voice if you can.  
  > D was chosen on development MAE (it beat the seasonal naive day on 1 to 24 h error in N of N BAs), and MAE rank is not saving rank; hyperparameters were frozen before the test year, and S5 tunes the f
- L49 [style] vale/write-good.Passive: 'were frozen' may be passive voice. Use active voice if you can.  
  > D was chosen on development MAE (it beat the seasonal naive day on 1 to 24 h error in N of N BAs), and MAE rank is not saving rank; hyperparameters were frozen before the test year, and S5 tunes the f
- L49 [style] vale/write-good.Passive: 'are given' may be passive voice. Use active voice if you can.  
  > Three confirmatory tests (H1 to H3, PM100, Holm) sit beside a large sensitivity grid, so p values are given for H1 to H3 only, and the registry (Section 1) and the all-cells table list every analysis.
- L51 [style] vale/write-good.Passive: 'is reported' may be passive voice. Use active voice if you can.  
  > S4 (secondary, run after the freeze; PREREG item 6, deviation row 2) includes timeouts on PM100 and gives N for D, and a near-limit exclusion is reported.
- L55 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> for -> A single script rebuilds every ledger from the stored result files and checks for equality.  
  > A single script rebuilds every ledger from the stored result files and checks equality.

### 07_conclusion

- L8 [style] vale/write-good.Passive: 'are archived' may be passive voice. Use active voice if you can.  
  > Code, derived data and result ledgers are archived on Zenodo ([ZENODO DOI: owner to publish]); the source repository is private until publication ([GITHUB LINK: owner to provide]).

### 08_declarations

- L8 [clarity] coedit/PARAPHRASE: High n-gram overlap with a source (suscom:p324: containment 1.00, longest shared run 26 words). Candidate paraphrase. -> The authors declare that they do not have any known competing financial interests or personal relationships which may have affected the work described in this paper.  
  > The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.
- L14 [clarity] coedit/GEC: CoEdIT proposes a correction: take -> took -> After using this tool, the authors reviewed and edited the content as needed and took full responsibility for the content of the published article.  
  > After using this tool, the authors reviewed and edited the content as needed and take full responsibility for the content of the published article.
- L14 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> the -> During the preparation of this work, the authors used [AI-DECLARATION SCOPE, the owner to confirm Claude (Anthropic) to draft and edit the text, to write analysis and plotting code under the authors'   
  > During the preparation of this work the authors used [AI-DECLARATION SCOPE: owner to confirm: Claude (Anthropic) to draft and edit the text, to write analysis and plotting code under the authors' dire
- L17 [style] coedit/GEC: CoEdIT proposes a correction: are -> is -> The EIA-930 hourly grid data is published by the U.S.  
  > The EIA-930 hourly grid data are published by the U.S.
- L17 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> The -> The Energy Information Administration and are in the public domain [1].  
  > Energy Information Administration and are in the public domain [1].
- L17 [style] vale/write-good.Passive: 'are archived' may be passive voice. Use active voice if you can.  
  > Code, derived data and result ledgers are archived on Zenodo ([ZENODO DOI: owner to publish]), together with the pre-registration, its checksum and a checksum list (SHA256SUMS.txt); the source reposit
- L20 [style] vale/write-good.Passive: 'are archived' may be passive voice. Use active voice if you can.  
  > Code, derived data and result ledgers are archived on Zenodo ([ZENODO DOI: owner to publish]); the source repository is private until publication ([GITHUB LINK: owner to provide]).
- L23 [style] vale/write-good.Passive: 'is used' may be passive voice. Use active voice if you can.  
  > The KIT ForHLR II workload log was graciously provided by Mehmet Soysal, and it is used under the citation request of the Parallel Workloads Archive [1].

### S_supplement

- L8 [style] coedit/GEC: CoEdIT proposes a correction: a -> the; a -> the -> A grid with a large daily swing offers more to the shift, and a solar-heavy grid has a sharp midday minimum that the wrong runtime estimate can miss; the replay does not test either reading.  
  > A grid with a large daily swing offers more to a shift, and a solar-heavy grid has a sharp midday minimum that a wrong runtime estimate can miss; the replay does not test either reading.
- L32 [clarity] languagetool/EN_A_VS_AN: Use “a” instead of ‘an’ if the following word doesn’t start with a vowel sound, e.g. ‘a sentence’, ‘a university’. [an] -> a  
  > Scripts are in and ledgers in ; each plan file has an md5 sum fixed before its runs.
- L32 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> are -> Scripts are in, and ledgers are in; each plan file has an md5 sum fixed before its runs.  
  > Scripts are in and ledgers in ; each plan file has an md5 sum fixed before its runs.
- L79 [clarity] coedit/GEC: CoEdIT proposes a correction: refit on -> refitted for -> The number of iterations came from early stopping on the same window, and the model was then refitted for the full training period.  
  > The number of iterations came from early stopping on the same window, and the model was then refit on the full training period.
- L81 [clarity] custom/SENT_LEN_45: Sentence has 72 words (limit 45). -> Split at the first coordinating clause.  
  > The tuned model has a lower MAE than the frozen one in every lead band, and a lower error than the tuned profile rival on N of N balancing authorities at leads of 1 to 24 h. Yet the replay outcomes mo
- L115 [clarity] coedit/GEC: CoEdIT proposes a correction: (none) -> expressed -> H2, H3, and the Shapley terms are expressed in percentage points.  
  > H2, H3 and the Shapley terms are in percentage points.
- L172 [clarity] custom/SENT_LEN_45: Sentence has 73 words (limit 45). -> Split at the first coordinating clause.  
  > Table 1 compares the N balancing authorities with the largest median daily intensity range in the training years (training-year threshold N g/kWh; quartile fixed on training data only) with the other 
- L172 [clarity] custom/SENT_LEN_45: Sentence has 52 words (limit 45). -> Split at the first coordinating clause.  
  > At 24 h of slack, D removes N, N and N g COXe per job on PM100, F-DATA and KIT FH2, against N, N and N g per kWh for the perfect-information arm; the 24 h saving of D on PM100 has a calendar interval 
- L177 [clarity] custom/SENT_LEN_45: Sentence has 47 words (limit 45). -> Split at the first coordinating clause.  
  > Run-now mean intensity of job energy (g COXe per kWh), saving of D in g per kWh with its calendar interval, and t COXe per MW-year of steady load for D (12 h, with interval), pred and act (12 h), and 
- L193 [clarity] custom/SENT_LEN_45: Sentence has 47 words (limit 45). -> Split at the first coordinating clause.  
  > Pooled saving of D and of act against run-now, and the share of the perfect-information saving that D keeps, in the top quartile of balancing authorities by training-year median daily intensity range 
- L223 [clarity] coedit/GEC: CoEdIT proposes a correction: (none) -> the; with -> using -> Each of the N outer samples resamples the users of a trace with replacement and replays each sample using the frozen calendar procedure.  
  > Each of N outer samples resamples the users of a trace with replacement and replays each sample with the frozen calendar procedure.
- L223 [clarity] coedit/CLARITY_REWRITE: CoEdIT rewrite is 12% shorter with the same numbers and placeholders. -> All total-variance intervals for D, H2 and H3 exclude zero on all three traces, and the tightest is H3 on F-DATA.  
  > All total-variance intervals of the saving of D, H2 and H3 exclude zero on all three traces, and the tightest is H3 on F-DATA.
- L223 [clarity] custom/SENT_LEN_45: Sentence has 47 words (limit 45). -> Split at the first coordinating clause.  
  > Table 1 gives the frozen estimate, the standard deviation across outer samples, the same spread when users are not resampled (original-users control; alignment replicates only), the total-variance int
- L248 [clarity] custom/SENT_LEN_45: Sentence has 87 words (limit 45). -> Split at the first coordinating clause.  
  > The noisy-input arms replace the forecast by the realized intensity plus independent noise, clipped at zero, with a scale per balancing authority and lead fitted on the development year so that the ab
- L248 [style] vale/write-good.Passive: 'is held' may be passive voice. Use active voice if you can.  
  > The noisy-input arms replace the forecast by the realized intensity plus independent noise, clipped at zero, with a scale per balancing authority and lead fitted on the development year so that the ab
- L248 [style] vale/write-good.Passive: 'is matched' may be passive voice. Use active voice if you can.  
  > The noisy-input arms replace the forecast by the realized intensity plus independent noise, clipped at zero, with a scale per balancing authority and lead fitted on the development year so that the ab
- L253 [clarity] custom/SENT_LEN_45: Sentence has 46 words (limit 45). -> Split at the first coordinating clause.  
  > Saving with the requested walltime for the trained forecast (D), the noisy-input arm matched at leads 1 to 24 h and the arm matched at every lead, and with the actual runtime; paired differences (nois
- L267 [clarity] custom/SENT_LEN_45: Sentence has 51 words (limit 45). -> Split at the first coordinating clause.  
  > From the start times of every replayed job, hourly job power is computed per balancing authority and replicate, and Table 1 gives its peak and its 99th percentile as multiples of its mean, the same tw
- L267 [style] vale/write-good.Passive: 'is computed' may be passive voice. Use active voice if you can.  
  > From the start times of every replayed job, hourly job power is computed per balancing authority and replicate, and Table 1 gives its peak and its 99th percentile as multiples of its mean, the same tw
- L272 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> the -> Peak and the 99th percentile of hourly job power as multiples of the mean, ratios to run-now, and share of hours above twice the mean.  
  > Peak and 99th percentile of hourly job power as multiples of the mean, ratios to run-now, and share of hours above twice the mean.
- L337 [error] coedit/GEC: CoEdIT proposes a correction: in -> (none); traces -> tracks -> The saving accrues from evening and night arrivals and is near zero for arrivals between about 07:00 and 11:00 on PM100 and KIT FH2; it is positive every month on all three tracks.  
  > The saving accrues from evening and night arrivals and is near zero for arrivals between about 07:00 and 11:00 on PM100 and KIT FH2; it is positive in every month on all three traces.
- L409 [style] vale/write-good.Passive: 'was refitted' may be passive voice. Use active voice if you can.  
  > The signal is the intensity of fossil generation only (coal, natural gas and oil with the lifecycle factors of the frozen signal), cleaned with the frozen rules; the frozen forecasting pipeline was re
- L409 [style] vale/write-good.Passive: 'is undefined' may be passive voice. Use active voice if you can.  
  > It is undefined for a balancing authority without fossil generation: SPA (hydro-only) has no usable day and is excluded from this item only, leaving N of 42.
- L409 [style] vale/write-good.Passive: 'is excluded' may be passive voice. Use active voice if you can.  
  > It is undefined for a balancing authority without fossil generation: SPA (hydro-only) has no usable day and is excluded from this item only, leaving N of 42.
- L435 [clarity] coedit/CLARITY_REWRITE: CoEdIT rewrite is 19% shorter with the same numbers and placeholders. -> When the planner holds the history-based prediction, the paired difference of the threshold rule minus pred is N on F-DATA and N on KIT FH2.  
  > When the planner holds the history-based prediction, the paired difference of the threshold rule minus pred is N on F-DATA (N to N) and N on KIT FH2 (N to N).
- L435 [clarity] languagetool/EN_COMPOUNDS_QUARTER_HOUR: This word is normally spelled with a hyphen. [quarter hour] -> quarter-hour  
  > The threshold rule starts a job at the first quarter hour whose last completed hourly intensity lies below its trailing 7-day 25th percentile, else at the end of the window.
- L435 [clarity] vale/write-good.TooWordy: 'multiple' is too wordy.  
  > The padded estimate is the smaller of the request and a fixed multiple of the prediction (Section 1), and the quantile estimate is the user's 90th percentile of past runtimes (at least five past jobs)
- L435 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> or -> The threshold rule starts a job at the first quarter hour whose last completed hourly intensity lies below its trailing 7-day 25th percentile, or else at the end of the window.  
  > The threshold rule starts a job at the first quarter hour whose last completed hourly intensity lies below its trailing 7-day 25th percentile, else at the end of the window.
- L462 [style] coedit/GEC: CoEdIT proposes a correction: the -> (none) -> The level of saving depends on the arrival clock time relative to the local daily cycle; the sign stays positive, and the prediction recovery H3 stays positive under both shifts.  
  > The level of the saving depends on the arrival clock time relative to the local daily cycle; the sign stays positive and the prediction recovery H3 stays positive under both shifts.
- L485 [clarity] custom/SENT_LEN_45: Sentence has 64 words (limit 45). -> Split at the first coordinating clause.  
  > On PM100, D saves N under the cap against N uncapped, which is N of the uncapped saving; N of jobs (N of energy) are displaced from the uncapped start, and the paired cap cost is N. Jobs that alone ex
- L485 [style] vale/write-good.Passive: 'are displaced' may be passive voice. Use active voice if you can.  
  > On PM100, D saves N under the cap against N uncapped, which is N of the uncapped saving; N of jobs (N of energy) are displaced from the uncapped start, and the paired cap cost is N. Jobs that alone ex
- L488 [style] coedit/GEC: CoEdIT proposes a correction: (none) -> a -> All cells come from the frozen test ledger and are generated by a script from its keys; only D and H1 to H3 on PM100 at 12 h are confirmatory, and every other cell is secondary.  
  > All cells come from the frozen test ledger and are generated by script from its keys; only D and H1 to H3 on PM100 at 12 h are confirmatory, and every other cell is secondary.
- L488 [style] vale/write-good.Passive: 'are generated' may be passive voice. Use active voice if you can.  
  > All cells come from the frozen test ledger and are generated by script from its keys; only D and H1 to H3 on PM100 at 12 h are confirmatory, and every other cell is secondary.
