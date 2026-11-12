# S3 emission-factor sets (post-freeze, exploratory sensitivity; code: src/sens_s3.py)

Source of every value: `src/emission_factors.csv` (md5 8c5c21e790f966d6f3b9af95c11c8eff), columns `lifecycle_g_per_kwh` and `direct_g_per_kwh`.
The CSV already carries a direct (combustion) value for every fuel with its citation, so the IPCC 2006 Guidelines Vol 2
fallback and heat-rate conversions are NOT needed. The citations are as written in the CSV; A16 did not re-open the
original documents (to be checked when the paper cites them).

| fuel | frozen lifecycle | S3a direct (combustion) | S3b lifecycle, oil 1116 | direct-value source named in the CSV |
|---|---|---|---|---|
| coal | 820 | 760 | 820 | IPCC AR5 WGIII Annex III Table A.III.2 (Schlomer et al. 2014): Coal-PC direct median 760 |
| natural_gas | 490 | 370 | 490 | same table: Gas-CC direct median 370 |
| nuclear | 12 | 0 | 12 | same table: nuclear direct 0 |
| oil | 650 | 1116 | 1116 | EIA FAQ 74, US 2023 petroleum 2.46 lb/kWh = 1116 g/kWh (the CSV also lists EIA-930 ERCO petroleum 941 g/kWh as a cross-check) |
| hydro | 24 | 0 | 24 | same table: hydropower direct 0 |
| solar | 48 | 0 | 48 | same table: solar PV direct 0 |
| wind | 11 | 0 | 11 | same table: wind onshore direct 0 |
| other | 230 | 0 | 230 | biogenic CO2 not counted (AR5 note ii; EIA FAQ 74); judgement mapping, as the CSV states |
| unknown | 700 | 575 | 700 | Electricity Maps default "assumes thermal" (direct 575); an assumption; unknown share is 0 in all eligible BAs |

Notes
- S3b changes ONLY oil (650 to 1116); the CSV states the oil share is <= 2.7 % in every eligible BA, so the CI moves by <= 13 g/kWh.
- Imports, exports and storage stay excluded in both sets (production-based signal), as in the frozen CI.
- The 1116 g/kWh oil value in S3b is a direct (combustion) value used inside a lifecycle set; this is the sensitivity the
  v2 plan specifies ("lifecycle factors with oil 1116 instead of 650"), not a claim that 1116 is a lifecycle value.
- Pipeline check (2026-11-12): CI rebuilt as sum_f share_f x EF_f with the frozen lifecycle factors reproduces `ci_hourly.ci`
  to 5e-5 g/kWh over 140,160 valid hours (CISO, ERCO), and the A06 cleaning of it reproduces `ci_clean.parquet`
  (flags and usable days identical; ci_clean within 6e-5).
