# QA_FINDINGS (run_qa.py, 2026-11-12 10:28)

Tools run: custom, lt, vale, checktext. Source: paper/sections/*.tmpl.tex. Manuscript not modified. Every finding is a candidate to read, not a verdict; false positives are expected (see QA_FILTERED.csv for what the filters removed).

## Counts by tool and severity

| tool | error | clarity | style | total |
|---|---|---|---|---|
| custom | 0 | 8 | 0 | 8 |
| languagetool | 2 | 0 | 1 | 3 |
| vale | 0 | 0 | 19 | 19 |
| **all** | 2 | 8 | 20 | 30 |

Filtered as false positives before counting: 158 (by tool: {'languagetool': 127, 'vale': 31}).

## Counts by section

| section | error | clarity | style | total |
|---|---|---|---|---|

## Counts by rule (top 25)

- vale / write-good.Passive: 19
- custom / ABBREV_FIRST_USE: 7
- languagetool / ON_SKYPE: 1
- languagetool / COLLECTIVE_NOUN_VERB_AGREEMENT_VBP: 1
- languagetool / NOW: 1
- custom / SENT_LEN_45: 1

## research-humanizer check_text.py output per section

### 05_results
```
Sentences: 144   Paragraphs: 23
Words per sentence: mean 21.6, sd 10.4, min 3, max 48
Under 12 words: 16 %   Over 30 words: 22 %   In 15 to 25: 33 %

Sentences over 45 words: 2
  [48] The arm lgbm pred saves <<TEST.PM100.w.S12.saving.lgbm|pred|pct2>> and keeps <<TEST.PM100.w.S12.reta...
  [46] Independent noise with the absolute error of the LightGBM forecast (X2) gives a saving of <<sens.x2....

Runs of sentences with the same opener: 2
  'the': The saving lost between oracle act and MATH is the gap MATH ...
  'the': The perfect-information arm waits <<TEST.PM100.S12.delay_h.o...

Paragraphs most worth rewriting first (top 5):
  none stand out; read for argument and specificity instead
```
### 06_discussion
```
Sentences: 92   Paragraphs: 19
Words per sentence: mean 22.5, sd 10.4, min 4, max 43
Under 12 words: 16 %   Over 30 words: 23 %   In 15 to 25: 37 %

Paragraphs most worth rewriting first (top 5):
  score 3: Per unit of job energy, MATH removes <<posthoc.PH4.PM100.w.S12.lgbm|req.g_per_kwh.est|.1f>...
  score 3: F. Data vintage. The planner is given intensity up to the hour before arrival, but EIA pub...
```
### 07_conclusion
```
Sentences: 17   Paragraphs: 3
Words per sentence: mean 25.5, sd 10.0, min 5, max 41
Under 12 words: 12 %   Over 30 words: 35 %   In 15 to 25: 29 %

Paragraphs most worth rewriting first (top 5):
  none stand out; read for argument and specificity instead
```

## All findings


### 07_conclusion.tmpl

- L4 [clarity] custom/ABBREV_FIRST_USE: Abbreviation HPC is used at its first main-text occurrence without a definition in the same sentence. -> Spell out the term and give (HPC).  
  > This study replayed three real HPC job traces on N U.S. balancing authorities over a held-out year to measure how much carbon saving a delay planner keeps when it uses only a past-only forecast and th
- L8 [style] vale/write-good.Passive: 'are archived' may be passive voice. Use active voice if you can.  
  > Code, derived data and result ledgers are archived on Zenodo ([ZENODO DOI: owner to publish]); the source repository is private until publication ([GITHUB LINK: owner to provide]).

### 05_results.tmpl

- L10 [clarity] custom/ABBREV_FIRST_USE: Abbreviation PM100 is used at its first main-text occurrence without a definition in the same sentence. -> Spell out the term and give (PM100).  
  > Only H1 to H3 carry a p-value, and they are confirmatory on PM100 at 12 h slack.
- L10 [style] languagetool/ON_SKYPE: The name of this brand needs to be capitalized. [slack] -> Slack  
  > Every other result is secondary, post-hoc or exploratory, and slack is X h unless stated.
- L14 [clarity] custom/ABBREV_FIRST_USE: Abbreviation KIT is used at its first main-text occurrence without a definition in the same sentence. -> Spell out the term and give (KIT).  
  > Confirmatory on PM100 (H1); secondary replications on F-DATA and KIT FH2.
- L14 [clarity] custom/ABBREV_FIRST_USE: Abbreviation FH2 is used at its first main-text occurrence without a definition in the same sentence. -> Spell out the term and give (FH2).  
  > Confirmatory on PM100 (H1); secondary replications on F-DATA and KIT FH2.
- L14 [style] vale/write-good.Passive: 'is replayed' may be passive voice. Use active voice if you can.  
  > The three values are close because every trace is replayed on the same grids in the same year, so savings per kWh are the better cross-trace comparison.
- L16 [style] vale/write-good.Passive: 'is supported' may be passive voice. Use active voice if you can.  
  > In relative terms, D saves N of run-now emissions on PM100 (calendar interval N to N; synchronized-week interval N to N), and H1 is supported (p<0.0005, Holm-adjusted <0.0015).
- L30 [style] vale/write-good.Passive: 'is read' may be passive voice. Use active voice if you can.  
  > The absolute gap between the two widens with the slack, and the retained share moves less regularly, at N, N, N and N. The retained share has no meaning independent of the slack, so it is read togethe
- L34 [clarity] custom/ABBREV_FIRST_USE: Abbreviation BA is used at its first main-text occurrence without a definition in the same sentence. -> Spell out the term and give (BA).  
  > Post-hoc intervals for the per-BA counts; descriptive associations with no p-values.
- L36 [style] vale/write-good.Passive: 'are unadjusted' may be passive voice. Use active voice if you can.  
  > These correlations are unadjusted and computed over the fixed set of BAs; the values for F-DATA and KIT FH2 are in Table 1, all eight correlations are in Table 1, and the replay does not test why they

### 06_discussion.tmpl

- L37 [clarity] custom/ABBREV_FIRST_USE: Abbreviation EIA is used at its first main-text occurrence without a definition in the same sentence. -> Spell out the term and give (EIA).  
  > The signal is the production-average carbon intensity of the balancing authority from EIA-930; imports and storage are excluded and three of the nine emission factors are judgment values.
- L37 [style] vale/write-good.Passive: 'are excluded' may be passive voice. Use active voice if you can.  
  > The signal is the production-average carbon intensity of the balancing authority from EIA-930; imports and storage are excluded and three of the nine emission factors are judgment values.
- L41 [error] languagetool/COLLECTIVE_NOUN_VERB_AGREEMENT_VBP: Possible verb agreement error. Did you mean “is”? (Some collective nouns can be treated as both singular and plural, so ‘are’ is not always incorrect.) [are] -> is  
  > Under this cap D keeps N of its uncapped saving, and N of jobs are displaced from their uncapped start (Section 1).
- L45 [style] vale/write-good.Passive: 'is given' may be passive voice. Use active voice if you can.  
  > The planner is given intensity up to the hour before arrival, but EIA publishes generation by source about a day late and revises it for days afterward [1], and the archived series holds revised value

### 05_results.tmpl

- L46 [style] vale/write-good.Passive: 'is chosen' may be passive voice. Use active voice if you can.  
  > The forecast-and-request arm thus waits about as long as the perfect-information arm and realizes a smaller saving per hour of waiting, as expected when the window is chosen with imperfect inputs.

### 06_discussion.tmpl

- L47 [error] languagetool/NOW: Did you mean “now” (at this moment) instead of ‘no’ (negation)? Or possibly even ‘not’? [no] -> now; not  
  > Power is a whole-job mean taken as constant, and energy weighting favors long jobs (in the raw PM100 log, jobs over 24 h supply N of the energy, but no analyzed PM100 job is that long).
- L47 [style] vale/write-good.Passive: 'is read' may be passive voice. Use active voice if you can.  
  > Weighting jobs equally raises D to N, N and N, so the energy-weighted headline is the more conservative of the two; KIT FH2 carries 1 kW per job and is read mainly through the unweighted rows.
- L49 [clarity] custom/ABBREV_FIRST_USE: Abbreviation MAE is used at its first main-text occurrence without a definition in the same sentence. -> Spell out the term and give (MAE).  
  > D was chosen on development MAE (it beat the seasonal naive day on 1 to 24 h error in N of N BAs), and MAE rank is not saving rank; hyperparameters were frozen before the test year, and S5 tunes the f
- L49 [style] vale/write-good.Passive: 'was chosen' may be passive voice. Use active voice if you can.  
  > D was chosen on development MAE (it beat the seasonal naive day on 1 to 24 h error in N of N BAs), and MAE rank is not saving rank; hyperparameters were frozen before the test year, and S5 tunes the f
- L49 [style] vale/write-good.Passive: 'were frozen' may be passive voice. Use active voice if you can.  
  > D was chosen on development MAE (it beat the seasonal naive day on 1 to 24 h error in N of N BAs), and MAE rank is not saving rank; hyperparameters were frozen before the test year, and S5 tunes the f
- L49 [style] vale/write-good.Passive: 'are given' may be passive voice. Use active voice if you can.  
  > Three confirmatory tests (H1 to H3, PM100, Holm) sit beside a large sensitivity grid, so p values are given for H1 to H3 only, and the registry (Section 1) and the all-cells table list every analysis.
- L51 [style] vale/write-good.Passive: 'is reported' may be passive voice. Use active voice if you can.  
  > S4 (secondary, run after the freeze; PREREG item 6, deviation row 2) includes timeouts on PM100 and gives N for D, and a near-limit exclusion is reported.
- L55 [style] vale/write-good.Passive: 'are archived' may be passive voice. Use active voice if you can.  
  > The frozen scripts, the pre-registration and its checksum, the environment lock file, the checksum of every result file and the exact run commands are archived at [ZENODO_DOI_PLACEHOLDER], and the cod
- L55 [style] vale/write-good.Passive: 'is kept' may be passive voice. Use active voice if you can.  
  > The frozen scripts, the pre-registration and its checksum, the environment lock file, the checksum of every result file and the exact run commands are archived at [ZENODO_DOI_PLACEHOLDER], and the cod
- L55 [style] vale/write-good.Passive: 'be supplied' may be passive voice. Use active voice if you can.  
  > The frozen scripts, the pre-registration and its checksum, the environment lock file, the checksum of every result file and the exact run commands are archived at [ZENODO_DOI_PLACEHOLDER], and the cod

### 05_results.tmpl

- L58 [clarity] custom/SENT_LEN_45: Sentence has 46 words (limit 45). -> Split at the first coordinating clause.  
  > A higher oil factor (S3b) gives N, and including jobs that hit their limit (S4) gives N. Tuning the LightGBM forecaster with a 100-trial search on the training years only (S5, exploratory; Section 1) 
- L60 [style] vale/write-good.Passive: 'is reported' may be passive voice. Use active voice if you can.  
  > These cover three traces, two signals, X and X. These are point estimates with no paired interval, so the direction is reported without a significance claim.
- L60 [style] vale/write-good.Passive: 'are marked' may be passive voice. Use active voice if you can.  
  > The requested walltime and the history prediction are marked at their measured error and not on the multiplier curve, and the padded and quantile operator rules sit beside them (Section 1).
- L64 [style] vale/write-good.Passive: 'is unchanged' may be passive voice. Use active voice if you can.  
  > Capping the forecast lead at 24 h raised the saving of D on PM100 from N to N (X3; the frozen lead is unchanged; Section 1).
