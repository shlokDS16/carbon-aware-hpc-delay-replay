VERDICT: A47 done; findings 725 (213 after filtering; errors 11); style cells inside corpus IQR 25 of 63; Binoculars section medians 96/91/93/96/98/93/98/87/85/93 (00_frontmatter..S_supplement; all 95); lowest paragraph S_supplement:485 pct 35; overlap max 0.07 (0 sentences at or above 0.30; one standard-declaration sentence at 1.00 filtered)

Scope: shared toolchain, all tools (custom, LanguageTool picky, Vale, check_text, CoEdIT-large, Binoculars-style vs 450 human SUSCOM paragraphs, 6-gram overlap vs 58 texts), all 10 stems incl. S_supplement (already in paper_A.json; no config change). Manuscript not modified. Config used: a scratchpad copy of configs/paper_A.json with output_dir=research/writing_qa/reports/final (shared config untouched). Post-processing: paper_A/tools/writing_qa make_report.py + build_profile.py with QA_REP=final. Earlier reports in reports/ untouched. Outputs in reports/final/: QA_FINDINGS.md/.csv, QA_FILTERED.csv, QA_BINO.csv, QA_BINO_summary.json, QA_SUMMARY.json, style_metrics.json, raw/, gpu_run.log. Scores are these tools' measurements, not Grammarly's (Grammarly AI-detector and plagiarism: not measured). Note: the toolchain prints file names as "*.tmpl.tmpl.tex" in the raw CSV (suffix doubled); the processed report uses the correct names.

GPU: at start 7.9 GB free, then 4 GB (an unrelated python process, PID 34212, 99 % load). Polled from 10:31; 11.9 GB were free at 10:44. GPU_SCHEDULE row added 10:45 (IN USE) and set DONE after the run (CoEdIT 657 sentences in 351 s, then Binoculars).

## Template md5 at read time (start of run) and change during the run
00 86754c8c8c8accd98d16c0a3c2dd394d | 01 b6a7e703bba87b301570171dd885bfab | 02 9a02ecb01cbb4b3875e5f0dd182d18f4 | 03 bbb0b88e856e8e4c1cadd56e0d376711 | 05 8ce64af7872452df2c791ca78c4e936c | 07 6d0734d60791302f27b436bc4e4f9cb3 (unchanged at end)
04 3b2041cd5487282eb21cf10957e70133 (at end 1d843154e92370737f2b0a51fbb77a35, mtime 10:45)
06 097a037e42c9c36060983d6f852da407 (at end dd0c6238fde681cf5bd6be3938c363f6, 10:49)
08 39e62006c5435d685714c4336f947395 (at end 9036d0c0a109f2ea724375fec6c7e43b, 10:32)
S  c2b512f8b653dad94f8a5c7676341dc9 (at end 78758f047b17b263b822795a09ecef89, 10:53)
A46 edited four files during the run, so the CPU pass (10:31) and the GPU pass (10:45 to 10:53) may have read different versions of 04, 06, 08 and S. Rerun after A46 finishes if exact numbers matter.

## Counts
Raw 725 (213 kept; 512 removed by filters: technical term 230, dropped rule 133, short passive 90, connective 43, other 16).
By tool (kept): coedit 115 (8 error, 39 clarity, 68 style), custom 25 (clarity), languagetool 8 (3 error, 4 clarity, 1 style), vale 65 (8 clarity, 57 style; 57 are write-good Passive), overlap 0 (its one hit is the standard declaration sentence, filtered).
By file (error/clarity/style/total): 00_frontmatter 0/6/2/8; 01_intro 1/10/13/24; 02_related 2/7/8/17; 03_data 2/5/17/24; 04_method 0/11/33/44; 05_results 1/12/20/33; 06_discussion 4/5/12/21; 07_conclusion 0/0/1/1; 08_declarations 0/2/6/8; S_supplement 1/18/14/33.

## Before / after (A38 to A47)
- Raw findings 587 to 725; kept 193 to 213. Errors: A38 7 LanguageTool + 1 Vale (+11 CoEdIT GEC) to 11 kept in total (3 LT, 8 CoEdIT, 0 Vale). Most of the A38 real items (Thus comma, 15-min hyphen, "There are N replicates", afterwards, "Power ... no") no longer appear except the "no" at 06_discussion L47.
- Sentences over 45 words (custom): 22 to 21 (S_supplement 10, 04_method 5, 01_intro 4, 00_frontmatter 1, 05_results 1). Longest: S_supplement L248 87 words, L172 73, L81 72.
- Style cells outside the corpus IQR: 39 of 63 to 38 of 63 (inside 25 of 63). Same direction as A38: sentence length mean and SD above in intro, results, discussion, conclusion; connectives, nominalisations, boosters, first person below; citations above in related, methods, discussion.
- Binoculars: A38 median 96 (section medians 87 to 99), lowest 05_results L23 (46). Now all-paragraph median 95 (95.3 on 123 paragraphs); lowest S_supplement L485 (35), then S_supplement L172 (50), 01_intro L15 (54), S_supplement L79 (55), 01_intro L27 (56). 0 of 123 paragraphs below the corpus 10th percentile (score 0.935; corpus median 1.027). Min percentile per section 96/54/89/60/66/59/88/85/65/35.
- Overlap: max sentence containment 0.05 to 0.07 (02_related L12 vs paperA_corpus SUSCOM_S2210537926002088); 0 sentences at or above 0.30; 6-gram share 0.2 % (24 of 12313). The 08_declarations competing-interests sentence matches a SUSCOM paper at 1.00 (standard Elsevier wording; filtered; CoEdIT offers a paraphrase, optional).

## Remaining findings (file:line in .tmpl.tex; all are candidates, read before acting)
Grammar and wording (CoEdIT/LanguageTool):
- 01_intro L15: "Four limits frame these numbers", suggestion "limitations".
- 02_related L21: "keep ... only as kill times and schedule with the mean runtime", suggestion "schedules" (check the parallel verb).
- 02_related L27: "recorded" to "records" (check tense against source).
- 05_results L50: "describes" to "describe" (check subject agreement in the current text).
- 06_discussion L35: "same sizes" to "size" (optional); L41: "saving" to "savings" and LT collective-noun agreement ("D keeps N ... and N of jobs ... are/is"); L47 LT "no" to "now/not" (check intent).
- 04_method L66 and S_supplement L435: "quarter hour" to "quarter-hour" (real hyphenation fix).
- S_supplement L337: CoEdIT drops "in", "traces" to "tracks" (the latter is a false positive).
False positives (leave): 03_data L8 "generation-weighted" to "generated"; 03_data L20 and S_supplement L32 (a/an before a math symbol or empty macro); 05_results L10 "slack" (variable name).
Abbreviation first use (custom): 00_frontmatter L15 PM100, KIT, FH2 appear in the abstract sentence without expansion (the abstract is read alone; expand or accept); 06_discussion L49 MAE without definition in that sentence (verify it is defined earlier in the main text).
Long sentences to split (words): 00 L15 52; 01 L13 56, L15 53, L21 57, L22 48; 04 L10 51, L23 47, L128 51, L133 52, L240 64; 05 L58 46; S L81 72, L172 73 and 52, L177 47, L193 47, L223 47, L248 87, L253 46, L267 51, L485 64.
CoEdIT clarity rewrites (11, 12 to 35 % shorter, optional): 01 L15, L17; 02 L14, L27; 05 L16, L30, L52; 06 L13, L21; S L223, L435.
Vale (non-passive): weasel "several" 02 L8, "mostly" 01 L9, "usually" 03 L30; too wordy "equivalent" 03 L8, "utilization" 02 L14 and L21 (term of art), "multiple" S L435, "Monitor" 03 L8 (proper name, ignore). Passive voice: 57 hits, on longer sentences only.
Machine-text (not a defect list): the paragraphs scoring lowest against the human corpus, if a more varied register is wanted: S_supplement L485, L172, L79; 01_intro L15, L27.

## Reading
Correctness is close to clean: no spelling or punctuation errors remain, only a handful of agreement and hyphenation candidates. The remaining differences from the SUSCOM style are structural (long sentences with high SD, few connectives and nominalisations). No paragraph reads as machine-like against the human corpus. No overlap risk in the folders searched (paywalled and web text not searched).
