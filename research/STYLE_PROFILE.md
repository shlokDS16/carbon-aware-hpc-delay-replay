# STYLE PROFILE (SUSCOM), measured by agent A02, 2026-11-11

Sample (small, so read as indicative): three SUSCOM abstracts read in full and one SUSCOM introduction.
- Abstract A: 10.1016/j.suscom.2023.100857 (abstract from OpenAlex/Semantic Scholar, https://api.openalex.org/works/doi:10.1016/j.suscom.2023.100857)
- Abstract B: 10.1016/j.suscom.2023.100859 (abstract text from the ResearchGate record, https://www.researchgate.net/publication/368809195)
- Abstract C: 10.1016/j.suscom.2023.100856 (abstract text from https://www.zhangqiaokeyan.com/journal-foreign-detail/0704052096886.html and Google Scholar snippet)
- Introduction: 10.1016/j.suscom.2023.100857, read from the arXiv preprint v2 (arXiv:2109.05472) because ScienceDirect returns 403 to scripts. The arXiv text is the pre-revision version, so wording may differ slightly from the Elsevier version.
- Abstracts of 10.1016/j.suscom.2023.100950, 2024.100985 and 2024.100988 could not be obtained (Elsevier abstracts are absent from Crossref, OpenAlex, Semantic Scholar; ScienceDirect 403). The R Discovery text shown for ETFC is the abstract of a different, systematic-review paper and was discarded.

## Measurements (script: sentence split on . ? !; passive = crude regex on be-verb plus participle, so it over- and under-counts a little)
| Item | Words | Sentences | Mean sentence length (words) | Longest | Passive sentences | we/our/us | Hedging words |
|---|---|---|---|---|---|---|---|
| Abstract A (100857) | 180 | 7 | 25.7 | 38 | 2 (29 %) | 5 | 1 |
| Abstract B (100859) | 308 | 13 | 23.7 | 37 | 3 (23 %) | 3 | 5 |
| Abstract C (100856) | 247 | 9 | 27.4 | 38 | 4 (44 %) | 0 | 3 |
| Pooled abstracts | 735 | 29 | 25.3 | 38 | 9 (31 %) | 8 | 9 (1.2 per 100 words) |
| Introduction (100857, arXiv v2) | 833 | 33 | 25.2 | 83 (a run-on list sentence) | 11 (33 %) | 16 | 8 (1.0 per 100 words) |

Hedging list used: may, might, could, can, possibly, likely, seems, suggests, approximately, about, usually, often, generally, promising, potential.

## Findings
1. Sentence length: about 25 words on average, longest abstract sentence 38. A mean near 22 to 25 with a cap of 40 matches the journal and is safer than the 45 limit in the project rules.
2. Voice: roughly one sentence in three is passive; "we/our" is normal in two of three abstracts and in the introduction (16 uses in 833 words). Abstract C (single author) uses no "we" and says "this paper presents". Use "we" for what we did, passive for set-up and data description.
3. Hedging is light (about 1 per 100 words). The sampled abstracts state results directly ("we see a much softer growth ...") with one closing caveat sentence in Abstract A. Our own abstract can state results with numbers; only Abstract B gives numbers (percent gains against "multiple benchmarks", no intervals).
4. Abstract structure (all three): (i) context sentence on a growing demand or energy problem; (ii) gap or question; (iii) "we/this paper" method sentence(s); (iv) validation by simulation or analysis; (v) result sentence, numeric only in B; (vi) optional caveat or implication. Length 180 to 308 words, mean about 245. SUSCOM allows long abstracts, so a 220 to 250 word, number-bearing abstract fits.
5. Section order seen in the one introduction I could read: Introduction, Background (related work), Methodology, analysis sections, Discussion and Future Work, then appendices. Not verified for the Elsevier layout; the arXiv text is the preprint. The Introduction ends with a numbered list of contributions ("main findings and contributions ... (1) ... (2) ... (3)") plus a data and code availability sentence and a roadmap sentence.
6. English variant: mixed. Abstract A uses British forms (optimisations, analyse); Abstract C uses American (data center); Abstract B shows no marker. No sign the journal enforces one variant; choose one and stay consistent. Project rule: pick American or British once, check with the humanizer toolchain.
7. Title forms: see title_survey.csv (none of the 50 top titles is a finding-led statement; 6 are Name-colon, the rest descriptive noun phrases averaging 13 words).
8. Punctuation: the sampled abstracts have no em or en dashes, which suits the project rule.

## Recommendation for Paper A prose
Mean sentence 22 to 25 words, none above 40; passive at most 30 %; "we" for actions and decisions; about 1 hedge per 100 words and only where the data justify it; abstract 220 to 250 words with numbers and intervals; contributions as a numbered list at the end of the Introduction; Data and code availability sentence near the end of the Introduction; section order Introduction, Related work, Data, Methods, Results, Discussion and limitations, Conclusion.
