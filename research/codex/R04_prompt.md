Round R04 (Paper A). Confirm the R03 fixes before the freeze. Read-only.

Re-read research/PREREG.md, src/simcore.py, src/simulate.py and src/analyze.py. Changes made for your R03 points:
1. analyze.py: null-centred p, one-sided (1 + #{T* - T >= T}) / (B + 1); two-sided |T* - T| >= |T|. Holm over H1-H3.
2. Primary bootstrap "fixed": all 42 BAs kept, 7-day blocks resampled within BA, remainder kept as a short last
   block. "twostage" (BAs then blocks) is a sensitivity.
3. Planner width 98 intervals (simcore.HP); forecasts padded with the lead-96 value for intervals 96-97; usable-hour
   exclusion and the period-end margin (100 h) cover the 98 h window.
4. H4 demoted to secondary item 9; pred2 = min(req, 2 x pred) and a near-limit exclusion (R_act >= 0.98 R_req) added as
   secondaries; D justified by final skill (38/42 vs snaive_day, 41/42 vs profile7, from tables/forecast_skill.csv);
   exact eligibility rule (90 %, D0003) and input md5s in section 2; PM100 power wording fixed.

DEV rerun (PM100, energy-weighted, S = 12 h): lgbm|req 1.73 % [1.65, 1.81] (fixed) and [1.36, 2.17] (twostage);
H2 1.95 pp [1.88, 2.03] fixed, [1.37, 2.65] twostage; H3 0.96 pp; pred2 2.19 %; near-limit exclusion: lgbm|req 1.91 %,
H2 2.29 pp. F-DATA H3 0.31 pp [0.16, 0.45]. Point estimates match the pre-fix run to 0.01 pp at S = 12 h.

Questions (at most 3 lines each):
1. Are the four fixes implemented correctly in the code? Point to any line that is still wrong.
2. The fixed-BA intervals are narrow (temporal uncertainty only). Is reporting both bootstraps, with fixed as primary
   and twostage beside every confirmatory estimate, acceptable to a SUSCOM referee?
3. Anything else that must change before the md5 freeze?
End with: VERDICT: FREEZE | FREEZE AFTER FIXES (list) | DO NOT FREEZE (reason); confidence 0-1.
