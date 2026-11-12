Round R08 (Paper A). Acceptance-risk review. Read-only. The owner asks to fix every risk to acceptance at SUSCOM.
Play five roles and label them: [EDITOR] SUSCOM handling editor deciding desk reject vs review; [IMPACT] a referee who
thinks 1.3 to 3.8 % savings are too small to matter; [OVERLAP] a referee who knows ReBase (SUSCOM 101470), LiteCast
and COAST and suspects incremental work; [VALIDITY] a referee doubting simulated replays (foreign traces on US grids,
average not marginal intensity, no queue capacity, EIA delay); [AUTHOR] the senior author who must answer all four.

Read: paper/main_draft3.pdf (current draft; red boxes = runs still finishing) or the filled paper/sections/*.tex;
research/PANEL_DECISIONS.md; research/journal/A13_OVERLAP_AUDIT.md and A20_LIT_LICENCE.md (what ReBase, LiteCast,
COAST, LACS do); tables/ledger_TEST.csv, ledger_TEST_posthoc.csv, ledger_TEST_secondary.csv, ledger_TEST_sens_*.csv
(S2 latency 1-6 h, S2b 24-48 h, S3a direct factors, S3b oil, S4 timeouts, S5 tuned forecaster, X1 runtime-accuracy
sweep; others still running); figures/CAPTIONS.md.

Questions (at most 6 lines per role per question; every proposed number must name its ledger key or say "needs a
light post-hoc computation from <file>"):
1. Each role's single strongest objection, stated as the referee would write it.
2. [AUTHOR] For each objection, the best answer the existing results support, and any LIGHT post-hoc computation on
   saved results that would make the answer decisive (examples to judge: annual tCO2e for a PM100-scale system;
   saving in the top quartile of BAs by daily range; saving at 24 h slack; the value of perfect runtime information in
   g per job; how close lgbm|pred gets to oracle|act in high-variation BAs). Rank them by value per hour of work.
3. Reframing: the contribution and title sentence that makes a modest but well-measured effect read as important
   for this journal (finding-led, no negatives, no question, true on all traces, not overclaiming).
4. Any other acceptance risk we have not listed, with the fix.
End with: VERDICT: ACCEPTABLE AFTER (list) | RISKY (reason); confidence 0-1.
