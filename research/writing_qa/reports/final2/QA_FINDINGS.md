# QA_FINDINGS (run_qa.py, 2026-11-12 11:18)

Tools run: custom, lt, vale, checktext. Source: paper/sections/*.tmpl.tex. Manuscript not modified. Every finding is a candidate to read, not a verdict; false positives are expected (see QA_FILTERED.csv for what the filters removed).

## Counts by tool and severity

| tool | error | clarity | style | total |
|---|---|---|---|---|
| custom | 0 | 9 | 0 | 9 |
| languagetool | 11 | 4 | 2 | 17 |
| vale | 0 | 8 | 57 | 65 |
| **all** | 11 | 21 | 59 | 91 |

Filtered as false positives before counting: 542 (by tool: {'languagetool': 409, 'vale': 133}).

## Counts by section

| section | error | clarity | style | total |
|---|---|---|---|---|

## Counts by rule (top 25)

- vale / write-good.Passive: 57
- vale / write-good.TooWordy: 5
- custom / SENT_LEN_45: 5
- custom / ABBREV_FIRST_USE: 4
- languagetool / MORFOLOGIK_RULE_EN_US: 3
- vale / write-good.Weasel: 3
- languagetool / EN_A_VS_AN: 2
- languagetool / UPPERCASE_SENTENCE_START: 2
- languagetool / WORD_CONTAINS_UNDERSCORE: 2
- languagetool / EN_COMPOUNDS_QUARTER_HOUR: 2
- languagetool / ON_SKYPE: 1
- languagetool / THE_PUNCT: 1
- languagetool / METRIC_UNITS_EN_US: 1
- languagetool / COLLECTIVE_NOUN_VERB_AGREEMENT_VBP: 1
- languagetool / NOW: 1
- languagetool / NON_STANDARD_WORD: 1

## research-humanizer check_text.py output per section

### 00_frontmatter
```
Sentences: 15   Paragraphs: 8
Words per sentence: mean 21.5, sd 10.4, min 9, max 40
Under 12 words: 13 %   Over 30 words: 27 %   In 15 to 25: 33 %

Paragraphs most worth rewriting first (top 5):
  none stand out; read for argument and specificity instead
```
### 01_intro
```
Sentences: 51   Paragraphs: 11
Words per sentence: mean 25.0, sd 10.5, min 4, max 46
Under 12 words: 12 %   Over 30 words: 33 %   In 15 to 25: 33 %

Sentences over 45 words: 1
  [46] The distance between a forecast-driven and a perfect-information scheduler is therefore already know...

Runs of sentences with the same opener: 1
  'section': Section REF places the study among earlier work...

Paragraphs most worth rewriting first (top 5):
  none stand out; read for argument and specificity instead
```
### 02_related
```
Sentences: 45   Paragraphs: 8
Words per sentence: mean 22.8, sd 8.0, min 8, max 45
Under 12 words: 11 %   Over 30 words: 13 %   In 15 to 25: 44 %

Paragraphs most worth rewriting first (top 5):
  score 3: Attenni et al. REF simulate spatial, temporal and spatio-temporal shifting of cloud worklo...
  score 3: The ReBase study REF compares a forecast-driven mixed-integer baseline with learned correc...
```
### 03_data
```
Sentences: 72   Paragraphs: 16
Words per sentence: mean 18.8, sd 8.6, min 4, max 43
Under 12 words: 25 %   Over 30 words: 11 %   In 15 to 25: 46 %

AI-vocabulary and stock-phrase hits (review; technical uses are fine):
    1  robust

Paragraphs most worth rewriting first (top 5):
  score 3: The factors MATH are the lifecycle medians of the IPCC fifth assessment report REF for coa...
  score 2: Cleaning follows four fixed rules, none tuned on development or test data. R1 builds a com...
```
### 04_method
```
Sentences: 131   Paragraphs: 27
Words per sentence: mean 20.0, sd 9.1, min 5, max 44
Under 12 words: 20 %   Over 30 words: 15 %   In 15 to 25: 39 %

Runs of sentences with the same opener: 1
  'the': The remaining arms are secondary, and four exploratory arms ...

Paragraphs most worth rewriting first (top 5):
  score 3: This is the delay-to-lowest-integral policy of earlier temporal-shifting studies REF . No ...
  score 3: With one earlier job, MATH is that job's runtime capped at the request, and with none it i...
  score 3: Every number in the paper is read from a ledger written by script from saved results. The ...
```
### 05_results
```
Sentences: 143   Paragraphs: 23
Words per sentence: mean 21.7, sd 10.4, min 3, max 48
Under 12 words: 16 %   Over 30 words: 22 %   In 15 to 25: 34 %

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
Words per sentence: mean 22.5, sd 10.3, min 4, max 43
Under 12 words: 16 %   Over 30 words: 23 %   In 15 to 25: 37 %

Paragraphs most worth rewriting first (top 5):
  score 3: Per unit of job energy, MATH removes <<posthoc.PH4.PM100.w.S12.lgbm|req.g_per_kwh.est|.1f>...
  score 3: F. Data vintage. The planner is given intensity up to the hour before arrival, but EIA pub...
```
### 07_conclusion
```
Sentences: 17   Paragraphs: 3
Words per sentence: mean 25.1, sd 10.1, min 5, max 41
Under 12 words: 12 %   Over 30 words: 35 %   In 15 to 25: 35 %

Paragraphs most worth rewriting first (top 5):
  none stand out; read for argument and specificity instead
```
### 08_declarations
```
Sentences: 22   Paragraphs: 7
Words per sentence: mean 16.5, sd 11.0, min 4, max 41
Under 12 words: 45 %   Over 30 words: 18 %   In 15 to 25: 23 %

Runs of sentences with the same opener: 1
  'the': The PM100 and F-DATA job traces are released under CC BY 4.0...

Paragraphs most worth rewriting first (top 5):
  score 3: [OWNER: roles per author; names stay placeholders]. [AUTHOR 1] : Conceptualization, Data c...
```
### S_supplement
```
Sentences: 133   Paragraphs: 46
Words per sentence: mean 21.5, sd 10.2, min 3, max 44
Under 12 words: 20 %   Over 30 words: 23 %   In 15 to 25: 38 %

Runs of sentences with the same opener: 3
  'the': The space was num\_leaves 15 to 127, max\_depth 3 to 10, lea...
  'table': Table REF scales the absolute savings to a steady 1 MW of de...
  'the': The noisy-input arms replace the forecast by the realized in...
Stacked hedges: 1

Paragraphs most worth rewriting first (top 5):
  score 3: Replay outcomes at 12 h slack under the frozen and the tuned LightGBM forecaster, energy-w...
```

## All findings


### S_supplement.tmpl

- L4 [error] languagetool/MORFOLOGIK_RULE_EN_US: Possible spelling mistake found. [Ssection] -> Section  
  > Ssection Stable Sfigure Sequation
- L4 [error] languagetool/MORFOLOGIK_RULE_EN_US: Possible spelling mistake found. [Sfigure] -> Figure  
  > Ssection Stable Sfigure Sequation
- L4 [error] languagetool/MORFOLOGIK_RULE_EN_US: Possible spelling mistake found. [Sequation] -> Equation  
  > Ssection Stable Sfigure Sequation

### 02_related.tmpl

- L8 [clarity] vale/write-good.Weasel: 'several' is a weasel word!  
  > CarbonCast [1] forecasts grid carbon intensity several days ahead from source-level forecasts.

### 03_data.tmpl

- L8 [clarity] vale/write-good.TooWordy: 'Monitor' is too wordy.  
  > Energy Information Administration (EIA) Form EIA-930 Hourly Electric Grid Monitor, which reports hourly net generation by fuel for balancing authorities (BAs) [1].
- L8 [clarity] vale/write-good.TooWordy: 'equivalent' is too wordy.  
  > For BA b and hour t, the carbon intensity is the generation-weighted mean of lifecycle emission factors, X, in g COXe per kWh (grams of COX-equivalent), where X is generation from fuel f and X its fac

### 01_intro.tmpl

- L9 [clarity] vale/write-good.Weasel: 'mostly' is a weasel word!  
  > These studies mostly give the scheduler the true carbon signal or a noise-perturbed copy of it, and most give it the true job length.
- L9 [style] vale/write-good.Passive: 'been developed' may be passive voice. Use active voice if you can.  
  > Simulation studies place delay-tolerant jobs at low-carbon hours [1], a production system shifts flexible load with day-ahead forecasts [1], and the forecast itself has been developed as a separate pr
- L9 [style] vale/write-good.Passive: 'are assumed' may be passive voice. Use active voice if you can.  
  > Wiesner et al. compare an optimal signal with forecasts that carry injected error, Sukprasert et al. include a prediction-error scenario, and Attenni et al. state that runtimes are assumed available t

### 04_method.tmpl

- L10 [clarity] custom/SENT_LEN_45: Sentence has 51 words (limit 45). -> Split at the first coordinating clause.  
  > Candidate starts lie on a 15-min grid, X The planner sees a signal X, piecewise constant on 98 hourly intervals that begin at X. This width covers the longest plan and realization window, X h, for eve

### 05_results.tmpl

- L10 [style] languagetool/ON_SKYPE: The name of this brand needs to be capitalized. [slack] -> Slack  
  > Every other result is secondary, post-hoc or exploratory, and slack is X h unless stated.

### 01_intro.tmpl

- L11 [style] vale/write-good.Passive: 'is built' may be passive voice. Use active voice if you can.  
  > Its forecast is built from past data only, and its runtime information is the walltime that the user requested at submission, an upper bound that the system enforces by killing the job.

### 02_related.tmpl

- L12 [style] vale/write-good.Passive: 'are assumed' may be passive voice. Use active voice if you can.  
  > They state that job runtimes are assumed known to the scheduler and that a trained operational forecaster remains future work; these are the two inputs measured here.

### 01_intro.tmpl

- L13 [style] vale/write-good.Passive: 'is reported' may be passive voice. Use active voice if you can.  
  > In the studies compared in Section 1 (Table 1), the gap between a scheduler with realistic inputs and a perfect-information scheduler is reported for forecast error alone, or for simulated job-length 

### 02_related.tmpl

- L14 [clarity] vale/write-good.TooWordy: 'utilization' is too wordy.  
  > It reports the wind-utilization gap of its own method to the oracle by forecast horizon, from 1.03 percent at the shortest horizon to 11.33 percent at the longest.

### 05_results.tmpl

- L14 [style] vale/write-good.Passive: 'is replayed' may be passive voice. Use active voice if you can.  
  > The three values are close because every trace is replayed on the same grids in the same year, so savings per kWh are the better cross-trace comparison.

### 00_frontmatter.tmpl

- L15 [clarity] custom/ABBREV_FIRST_USE: Abbreviation KIT is used at its first main-text occurrence without a definition in the same sentence. -> Spell out the term and give (KIT).  
  > Delaying jobs by up to 12 h saved N, N and N g COXe per kWh of job energy on PM100, F-DATA and KIT FH2, and N, N and N g with 24 h of slack.
- L15 [clarity] custom/ABBREV_FIRST_USE: Abbreviation FH2 is used at its first main-text occurrence without a definition in the same sentence. -> Spell out the term and give (FH2).  
  > Delaying jobs by up to 12 h saved N, N and N g COXe per kWh of job energy on PM100, F-DATA and KIT FH2, and N, N and N g with 24 h of slack.
- L15 [clarity] custom/ABBREV_FIRST_USE: Abbreviation PM100 is used at its first main-text occurrence without a definition in the same sentence. -> Spell out the term and give (PM100).  
  > Delaying jobs by up to 12 h saved N, N and N g COXe per kWh of job energy on PM100, F-DATA and KIT FH2, and N, N and N g with 24 h of slack.
- L15 [style] vale/write-good.Passive: 'are supported' may be passive voice. Use active voice if you can.  
  > Tests of the saving, the cost of the requested walltime and its recovery by prediction (H1 to H3) are supported on PM100 (p<0.0005, Holm-adjusted <0.0015); the other traces are secondary replications.
- L15 [style] vale/write-good.Passive: 'are modeled' may be passive voice. Use active voice if you can.  
  > These are modeled bounds from a counterfactual replay of non-U.S. traces, on production-average rather than marginal intensity (a fossil-only proxy credits far less) and with free capacity, not avoide

### 05_results.tmpl

- L16 [style] vale/write-good.Passive: 'is supported' may be passive voice. Use active voice if you can.  
  > In relative terms, D saves N of run-now emissions on PM100 (calendar interval N to N; synchronized-week interval N to N), and H1 is supported (p<0.0005, Holm-adjusted <0.0015).

### 01_intro.tmpl

- L17 [style] vale/write-good.Passive: 'is known' may be passive voice. Use active voice if you can.  
  > The forecast-and-request arm D uses only what is known at submission, under the data-availability assumption of Section 1 that the intensity of the hour just ended is available at arrival; the label d

### 08_declarations.tmpl

- L17 [style] vale/write-good.Passive: 'are archived' may be passive voice. Use active voice if you can.  
  > Code, derived data and result ledgers are archived on Zenodo ([ZENODO DOI]), together with the pre-registration, its checksum and a checksum list (SHA256SUMS.txt); the source repository is private unt

### 03_data.tmpl

- L20 [error] languagetool/THE_PUNCT: Articles like ‘a’ are rarely followed by punctuation. A word may be missing after ‘a’, or the punctuation mark may not be necessary. [a,] -> a  
  > The frozen design assumes that, at arrival, the intensity of the hour ending at X is available at a, the moment of arrival.
- L20 [clarity] languagetool/EN_A_VS_AN: Use “an” instead of ‘a’ if the following word starts with a vowel sound, e.g. ‘an article’, ‘an hour’. [a] -> an  
  > The planner needs data that a deployed scheduler would hold at the arrival time a of the job.

### 02_related.tmpl

- L21 [clarity] vale/write-good.TooWordy: 'utilization' is too wordy.  
  > These works target waiting time and utilization, not carbon.
- L21 [style] vale/write-good.Passive: 'are killed' may be passive voice. Use active voice if you can.  
  > Mu'alem and Feitelson [1] find user estimates on three IBM SP2 logs to be rather poor but a good upper bound, because few jobs are killed at their limit.

### 04_method.tmpl

- L23 [clarity] custom/SENT_LEN_45: Sentence has 47 words (limit 45). -> Split at the first coordinating clause.  
  > Realized emissions are then scored on the actual intensity X over the true run, X which is in g COXe when P is in W, c in g COXe per kWh and t in h. Any job whose 98-interval window touches an unusabl
- L23 [style] vale/write-good.Passive: 'is excluded' may be passive voice. Use active voice if you can.  
  > Realized emissions are then scored on the actual intensity X over the true run, X which is in g COXe when P is in W, c in g COXe per kWh and t in h. Any job whose 98-interval window touches an unusabl

### 08_declarations.tmpl

- L23 [style] vale/write-good.Passive: 'is used' may be passive voice. Use active voice if you can.  
  > The KIT ForHLR II workload log was graciously provided by Mehmet Soysal, and it is used under the citation request of the Parallel Workloads Archive [1].

### 03_data.tmpl

- L26 [style] vale/write-good.Passive: 'is used' may be passive voice. Use active voice if you can.  
  > The KIT FH2 log is used under the citation request of the Parallel Workloads Archive [1], with the acknowledgement that the archive asks for (see the Acknowledgements).

### 02_related.tmpl

- L27 [style] vale/write-good.Passive: 'is limited' may be passive voice. Use active voice if you can.  
  > Among the three outside works compared above, we did not find an evaluation that combines a past-only carbon forecast, requested walltimes and real HPC traces; this statement is limited to the papers 

### 00_frontmatter.tmpl

- L28 [error] languagetool/UPPERCASE_SENTENCE_START: This sentence does not start with an uppercase letter. [carbon-aware] -> Carbon-aware  
  > carbon-aware scheduling HPC batch jobs temporal shifting walltime estimates carbon intensity forecasting pre-registration Shapley decomposition

### 03_data.tmpl

- L28 [style] vale/write-good.Passive: 'is standardized' may be passive voice. Use active voice if you can.  
  > Each trace is standardized to the same fields: submit time in local site time, requested walltime X, actual runtime X, final state, user and the mean power P of the job.

### 02_related.tmpl

- L29 [error] languagetool/UPPERCASE_SENTENCE_START: This sentence does not start with an uppercase letter. [tables] -> Tables  
  > tables/T1_related.texT1 comparison of the closest studies

### 03_data.tmpl

- L30 [clarity] vale/write-good.Weasel: 'usually' is a weasel word!  
  > Older studies of other machines also find that user estimates are poor [1] but usually safe upper bounds [1].

### 05_results.tmpl

- L30 [style] vale/write-good.Passive: 'is read' may be passive voice. Use active voice if you can.  
  > The absolute gap between the two widens with the slack, and the retained share moves less regularly, at N, N, N and N. The retained share has no meaning independent of the slack, so it is read togethe

### 03_data.tmpl

- L32 [style] vale/write-good.Passive: 'be identified' may be passive voice. Use active voice if you can.  
  > Every KIT FH2 job has status completed, so timeouts cannot be identified there, although N of its jobs run to within 2 % of the limit.
- L34 [style] vale/write-good.Passive: 'be read' may be passive voice. Use active voice if you can.  
  > A fourth trace, the NLR Kestrel jobs data, would have matched both the EIA-930 years and a U.S. site, but its host returned a maintenance error on two attempts and its license could not be read, so it

### 05_results.tmpl

- L36 [style] vale/write-good.Passive: 'are unadjusted' may be passive voice. Use active voice if you can.  
  > These correlations are unadjusted and computed over the fixed set of BAs; the values for F-DATA and KIT FH2 are in Table 1, all eight correlations are in Table 1, and the replay does not test why they

### S_supplement.tmpl

- L37 [clarity] languagetool/EN_A_VS_AN: Use “a” instead of ‘an’ if the following word doesn’t start with a vowel sound, e.g. ‘a sentence’, ‘a university’. [an] -> a  
  > Scripts are in and ledgers in ; each plan file has an md5 sum fixed before its runs.

### 06_discussion.tmpl

- L37 [style] vale/write-good.Passive: 'are excluded' may be passive voice. Use active voice if you can.  
  > The signal is the production-average carbon intensity of the balancing authority from EIA-930; imports and storage are excluded and three of the nine emission factors are judgment values.

### S_supplement.tmpl

- L40 [style] languagetool/METRIC_UNITS_EN_US: Writing for an international audience? Consider adding the metric equivalent. [3pt] -> 3pt (1.42 l); 3pt (1.42 liters); 3pt (ca. 1,420 cm³)  
  > 3pt

### 03_data.tmpl

- L40 [style] vale/write-good.Passive: 'is replayed' may be passive voice. Use active voice if you can.  
  > A job that arrived on a given weekday and clock time at its home site is replayed on a U.S. grid at that weekday and clock time in the BA's standard local time.

### 06_discussion.tmpl

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

### S_supplement.tmpl

- L54 [error] languagetool/WORD_CONTAINS_UNDERSCORE: An underscore (_) within a word is atypical (except in technical contexts, nicknames, etc.). Make sure that the word ‘PANEL_DECISIONS’ is correct. [PANEL_DECISIONS] -> PANEL DECISIONS; PANEL-DECISIONS  
  > H1 to H3 & Saving of the forecast-and-request arm, runtime penalty and prediction recovery on PM100 at 12 h slack; Holm over three & confirmatory & PREREG s6 & ; \ H1 to H3, other traces & Same contra
- L54 [clarity] custom/SENT_LEN_45: Sentence has 590 words (limit 45). -> Split at the first coordinating clause.  
  > H1 to H3 & Saving of the forecast-and-request arm, runtime penalty and prediction recovery on PM100 at 12 h slack; Holm over three & confirmatory & PREREG s6 & ; \ H1 to H3, other traces & Same contra
- L54 [style] vale/write-good.Passive: 'is reported' may be passive voice. Use active voice if you can.  
  > H1 to H3 & Saving of the forecast-and-request arm, runtime penalty and prediction recovery on PM100 at 12 h slack; Holm over three & confirmatory & PREREG s6 & ; \ H1 to H3, other traces & Same contra

### 06_discussion.tmpl

- L55 [style] vale/write-good.Passive: 'are archived' may be passive voice. Use active voice if you can.  
  > The frozen scripts, the pre-registration and its checksum, the environment lock file, the checksum of every result file and the exact run commands are archived at [ZENODO DOI], and the code is kept in
- L55 [style] vale/write-good.Passive: 'is kept' may be passive voice. Use active voice if you can.  
  > The frozen scripts, the pre-registration and its checksum, the environment lock file, the checksum of every result file and the exact run commands are archived at [ZENODO DOI], and the code is kept in

### 05_results.tmpl

- L60 [style] vale/write-good.Passive: 'is reported' may be passive voice. Use active voice if you can.  
  > These cover three traces, two signals, X and X. These are point estimates with no paired interval, so the direction is reported without a significance claim.
- L60 [style] vale/write-good.Passive: 'are marked' may be passive voice. Use active voice if you can.  
  > The requested walltime and the history prediction are marked at their measured error and not on the multiplier curve, and the padded and quantile operator rules sit beside them (Section 1).

### 04_method.tmpl

- L64 [style] vale/write-good.Passive: 'was selected' may be passive voice. Use active voice if you can.  
  > It was selected on DEV, before the test year was scored, because the final forecaster beat the seasonal naive day on 1 to 24 h error in most BAs (Section 1).
- L64 [style] vale/write-good.Passive: 'was scored' may be passive voice. Use active voice if you can.  
  > It was selected on DEV, before the test year was scored, because the final forecaster beat the seasonal naive day on 1 to 24 h error in most BAs (Section 1).

### 05_results.tmpl

- L64 [style] vale/write-good.Passive: 'is unchanged' may be passive voice. Use active voice if you can.  
  > Capping the forecast lead at 24 h raised the saving of D on PM100 from N to N (X3; the frozen lead is unchanged; Section 1).

### 04_method.tmpl

- L66 [clarity] languagetool/EN_COMPOUNDS_QUARTER_HOUR: This word is normally spelled with a hyphen. [quarter hour] -> quarter-hour  
  > The first is a forecast-free threshold rule that starts at the first quarter hour whose observed intensity lies below its trailing 7-day 25th percentile (else at a+S).
- L77 [style] vale/write-good.Passive: 'is reported' may be passive voice. Use active voice if you can.  
  > A lower error does not imply a higher saving, since the planner uses only the ranking of intensities inside a window, so saving is reported beside error rather than inferred from it.
- L81 [style] vale/write-good.Passive: 'was submitted' may be passive voice. Use active voice if you can.  
  > It is the mean actual runtime of the user's two most recent jobs that ended before this job was submitted in state COMPLETED or TIMEOUT, capped at the request, X

### S_supplement.tmpl

- L89 [error] languagetool/WORD_CONTAINS_UNDERSCORE: An underscore (_) within a word is atypical (except in technical contexts, nicknames, etc.). Make sure that the word ‘max_depth’ is correct. [max_depth] -> max depth; max-depth  
  > The space was num_leaves 15 to 127, max_depth 3 to 10, learning rate 0.01 to 0.15 (log scale), min_data_in_leaf 50 to 1000 (log), feature and bagging fractions 0.6 to 1.0, L1 and L2 penalties X to 10 

### 04_method.tmpl

- L128 [clarity] custom/SENT_LEN_45: Sentence has 51 words (limit 45). -> Split at the first coordinating clause.  
  > The saving of an arm is one minus its emissions over the run-now emissions, pooled over BAs, days, runtime classes and replicates, X Because jobs are pooled before the ratio is taken, X is carbon-weig
- L128 [style] vale/write-good.Passive: 'are pooled' may be passive voice. Use active voice if you can.  
  > The saving of an arm is one minus its emissions over the run-now emissions, pooled over BAs, days, runtime classes and replicates, X Because jobs are pooled before the ratio is taken, X is carbon-weig
- L128 [style] vale/write-good.Passive: 'is taken' may be passive voice. Use active voice if you can.  
  > The saving of an arm is one minus its emissions over the run-now emissions, pooled over BAs, days, runtime classes and replicates, X Because jobs are pooled before the ratio is taken, X is carbon-weig
- L133 [clarity] custom/SENT_LEN_45: Sentence has 52 words (limit 45). -> Split at the first coordinating clause.  
  > The three confirmatory hypotheses, tested on PM100 at X h, concern X where each hypothesis states X. H1 says that the forecast-and-request arm D saves emissions, H2 that knowing the actual runtime add
- L161 [style] vale/write-good.Passive: 'were added' may be passive voice. Use active voice if you can.  
  > With the job energy X in kWh (X in W, X in h) and X in g COXe per kWh of job energy, X The absolute effects were added after the freeze (post-hoc) from the saved results.
- L171 [error] languagetool/NON_STANDARD_WORD: The word ‘7+S’ is not standard English. Did you mean “7’S” (curly apostrophe) or “7'S” (straight apostrophe)? [7+S] -> 7’S; 7'S  
  > With N draws and seed 7+S, the interval of a statistic T with draws X is the percentile interval X the empirical quantiles of the draws.
- L171 [style] vale/write-good.Passive: 'are cut' may be passive voice. Use active voice if you can.  
  > For each BA, the per-day sums of Algorithm 1 are cut into consecutive 7-day blocks that start at the BA's first arrival day, and a remainder shorter than 7 days is kept fixed.
- L171 [style] vale/write-good.Passive: 'is kept' may be passive voice. Use active voice if you can.  
  > For each BA, the per-day sums of Algorithm 1 are cut into consecutive 7-day blocks that start at the BA's first arrival day, and a remainder shorter than 7 days is kept fixed.
- L183 [style] vale/write-good.Passive: 'are shared' may be passive voice. Use active voice if you can.  
  > Pooling over BAs first is exact because the indices are shared; the same code gives an interval for the difference X and for each Shapley term under both bootstraps.
- L238 [style] vale/write-good.Passive: 'are recorded' may be passive voice. Use active voice if you can.  
  > The simulator refuses the test period unless the md5 sum of the registration (starting cfe98401) matches the stored value, and the sums of the five analysis scripts are recorded.
- L238 [style] vale/write-good.Passive: 'was written' may be passive voice. Use active voice if you can.  
  > The secondary-analysis code was written after the test run and only reads saved results (row 3), and test arrivals span 2025-07-07 to 2026-06-14 (row 4), and the post-hoc inference below was added (ro
- L238 [style] vale/write-good.Passive: 'was added' may be passive voice. Use active voice if you can.  
  > The secondary-analysis code was written after the test run and only reads saved results (row 3), and test arrivals span 2025-07-07 to 2026-06-14 (row 4), and the post-hoc inference below was added (ro
- L240 [style] vale/write-good.Passive: 'is reported' may be passive voice. Use active voice if you can.  
  > A post-freeze result is reported beside the frozen value and is never promoted to a confirmatory claim; the analysis registry in the supplement lists every analysis with its status, file and ledger.

### S_supplement.tmpl

- L258 [style] vale/write-good.Passive: 'is fitted' may be passive voice. Use active voice if you can.  
  > The noise scale is fitted per balancing authority and lead on the development year so that the absolute error equals that of the LightGBM forecast at leads of 1 to 24 h (the scale at lead 24 is held f
- L258 [style] vale/write-good.Passive: 'is held' may be passive voice. Use active voice if you can.  
  > The noise scale is fitted per balancing authority and lead on the development year so that the absolute error equals that of the LightGBM forecast at leads of 1 to 24 h (the scale at lead 24 is held f
- L258 [style] vale/write-good.Passive: 'is matched' may be passive voice. Use active voice if you can.  
  > The second version is matched at every lead to 96 h. The question is whether injecting noise of the forecast's size understates or overstates the loss from the trained forecast.
- L435 [style] vale/write-good.Passive: 'was refitted' may be passive voice. Use active voice if you can.  
  > The signal is the intensity of fossil generation only (coal, natural gas and oil with the lifecycle factors of the frozen signal), cleaned with the frozen rules; the frozen forecasting pipeline was re
- L435 [style] vale/write-good.Passive: 'is undefined' may be passive voice. Use active voice if you can.  
  > It is undefined for a balancing authority without fossil generation: SPA (hydro-only) has no usable day and is excluded from this item only, leaving N of 42.
- L435 [style] vale/write-good.Passive: 'is excluded' may be passive voice. Use active voice if you can.  
  > It is undefined for a balancing authority without fossil generation: SPA (hydro-only) has no usable day and is excluded from this item only, leaving N of 42.
- L461 [clarity] languagetool/EN_COMPOUNDS_QUARTER_HOUR: This word is normally spelled with a hyphen. [quarter hour] -> quarter-hour  
  > The threshold rule starts a job at the first quarter hour whose last completed hourly intensity lies below its trailing 7-day 25th percentile, else at the end of the window.
- L461 [clarity] vale/write-good.TooWordy: 'multiple' is too wordy.  
  > The padded estimate is the smaller of the request and a fixed multiple of the prediction (Section 1), and the quantile estimate is the user's 90th percentile of past runtimes (at least five past jobs)
- L538 [style] vale/write-good.Passive: 'are generated' may be passive voice. Use active voice if you can.  
  > All cells come from the frozen test ledger and are generated by script from its keys; only D and H1 to H3 on PM100 at 12 h are confirmatory, and every other cell is secondary.
