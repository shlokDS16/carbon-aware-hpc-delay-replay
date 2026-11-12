VERDICT: A06 done; 37 eligible BAs; factors verified 6/9; EIA emissions validation yes (ERCO only)

> Controller note (2026-11-11, D0003): the final build (`src/clean_ci.py --final`) uses at least 90 % valid hours per period instead of 95 %, decided on data quality before any DEV or TEST outcome. Final outputs: `tables/ba_eligibility.csv` (42 eligible BAs, md5 8fe037d0b2f50778057e6668ec040927) and `data/derived/ci_clean.parquet`. The counts below describe the v0 (95 %) build.

# A06 data audit, cleaning and emission-factor verification (2026-11-11)

Files written: `src/clean_ci.py`, `src/schema_check_ci.py`, `src/extract_eia_co2.py`, `src/validate_eia_ci.py`, `src/emission_factors.csv` (updated),
`data/derived/ci_clean_v0.parquet`, `tables/ba_eligibility_v0.csv`, `tables/cleaning_counts_v0.csv`, `tables/schema_break_check_v0.csv`,
`tables/schema_break_windows_v0.csv`, `tables/eia_co2_validation_ERCO_v0.csv`, `data/raw/eia930_emissions/ERCO.xlsx` (75.3 MB) and `ERCO_co2_hourly.csv`.
Everything uses the provisional `ci_hourly_v0.parquet` (built with oil 650, other 700, unknown 700). The final build must be re-run with the new CSV (`other` is now 230); then `python src/clean_ci.py --final` and `python src/schema_check_ci.py --final`.

## Part 1. Emission factors

### (a) AR5 table confirmed
Source: IPCC AR5 WGIII Annex III, Table A.III.2 "Emissions of selected electricity supply technologies (gCO2eq/kWh)"
(https://www.ipcc.ch/site/assets/uploads/2018/02/ipcc_wg3_ar5_annex-iii.pdf, read in full; chapter DOI 10.1017/cbo9781107415416.025, resolved on Crossref).
Columns: direct emissions min/median/max; infrastructure and supply chain; biogenic CO2; methane; lifecycle min/median/max.

| Technology | Direct (min / median / max) | Lifecycle (min / median / max) | CSV lifecycle | CSV direct |
|---|---|---|---|---|
| Coal PC | 670 / 760 / 870 | 740 / 820 / 910 | 820 | 760 |
| Gas combined cycle | 350 / 370 / 490 | 410 / 490 / 650 | 490 | 370 |
| Nuclear | 0 | 3.7 / 12 / 110 | 12 | 0 |
| Hydropower | 0 | 1.0 / 24 / 2200 | 24 | 0 |
| Solar PV utility | 0 | 18 / 48 / 180 | 48 | 0 |
| Wind onshore | 0 | 7.0 / 11 / 56 | 11 | 0 |
| Biomass dedicated (used for "other") | n.a. (note ii) | 130 / 230 / 420 | 230 | 0 |
| Geothermal | 0 | 6.0 / 38 / 79 | (folded into other) | 0 |

All six medians already in the CSV (820, 490, 12, 24, 48, 11) match the table. verified = yes for these six.

### (b) Oil, other, unknown
- **Oil**: AR5 Table A.III.2 has no oil row. Lifecycle 650 = Electricity Maps default (`config/defaults.yaml` in electricitymaps-contrib, source "UK POST 2014", comment cites the UK Parliamentary Office of Science and Technology 2006 "Carbon footprint of electricity generation"; same table on their wiki "Default emission factors"). I read their config, not the POSTnote, so verified = no. Direct 1116 g/kWh = EIA FAQ 74 (https://www.eia.gov/tools/faqs/faq.php?id=74&t=11), US 2023 petroleum 2.46 lb CO2/kWh x 453.592. EIA's own BA factor for petroleum in ERCO is 2.03 lb/kWh = 941 g/kWh (from the EIA-930 ERCO workbook, see (c)). Electricity Maps' direct 406 (EIA 2020 / BEIS 2021 US-UK blend) is not used: it is far below the EIA US figure. The lifecycle 650 is lower than the US direct 1116, an inconsistency inherited from the UK source. It is harmless here: oil share in eligible BAs is at most 2.7 % (NWMT) and 2.1 % (NYIS), so switching oil lifecycle from 650 to 1116 moves a BA mean CI by at most 12.6 g/kWh (NWMT), 9.9 (NYIS), 2.9 (ISNE), under 2 elsewhere. Report as a sensitivity.
- **Other**: lifecycle 230 (AR5 biomass dedicated median), direct 0 (biogenic CO2 not counted, AR5 note ii; EIA FAQ 74 treats biomass as carbon neutral). Same as Electricity Maps' biomass default. Geothermal (38) is folded into "other" by the schema map and is rare. EIA's "Other" is a mixed category (the EIA-930 About page says BAs may mask generation under OTH), so this is a judgement mapping: verified = no. It matters: the pilot value 700 was wrong for biomass-heavy BAs. Mean "other" share is 25.7 % in GVL and 18.3 % in SPA; moving 700 to 230 lowers their mean CI by 121 and 86 g/kWh, and CPLE 58, AVA 56, LDWP 40, FPL 39 g/kWh. Rerun everything with the new value.
- **Unknown**: lifecycle 700, direct 575 (Electricity Maps "assumes thermal"). Assumption only, verified = no. Unknown share is 0 in all eligible BAs, so no effect on the study.
- de Chalendar et al. 2019 (doi 10.1073/pnas.1912950116, resolved on Crossref; text read on PMC6926065) uses direct (combustion) emissions and states it does not account for life-cycle emissions, so it is not a source for lifecycle oil, other or unknown. It supports using a direct-emissions variant as a sensitivity.
- Result: **verified 6/9** (coal, gas, nuclear, hydro, solar, wind). Oil, other, unknown = no (reasons above). `eia_columns` untouched; column names unchanged. The `source` field in the CSV now carries the DOI/URL and table for each row.

### (c) EIA hourly CO2: yes, but not in the six-month CSV files
- The six-month files (`https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_<BALANCE|INTERCHANGE|SUBREGION>_<YYYY>_<Jan_Jun|Jul_Dec>.csv`, listed in `.../sixMonthFiles/EIA930_File_List_Meta.csv`) contain no CO2 column (checked the 65-column header). There is no emissions six-month file (the grid-monitor site answers HTTP 200 with an HTML page for any filename, so a 200 status proves nothing).
- CO2 is in the **per-BA Excel workbooks**: `https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx` (region files `.../xls/Region_<REG>.xlsx`), found in the grid-monitor JavaScript (`respondentPath`), sheet "Published Hourly Data". Documented at https://www.eia.gov/electricity/930-content/about.html ("Estimated CO2 emissions ... beginning July 1, 2018") and in the PUDL docs (https://docs.catalyst.coop/pudl/en/stable/data_sources/eia930.html). Columns: `CO2 Factor: COL/NG/OIL` (lbs/kWh, BA fleet factors), `CO2 Emissions: COL/NG/OIL/Other/Generated/Imported/Exported/Consumed` (metric tons), `CO2 Emissions Intensity for Generated Electricity` and `for Consumed Electricity` (lbs/kWh). Timestamps are end-of-hour UTC. Method (About page): EPA kg/MMBtu factors times EIA-923 fuel use, BA fleet factors for coal, gas and petroleum, one US factor for other fuels, CHP excluded.
- Files are large (CISO 98 MB, ERCO 75 MB). Downloaded ONE: `data/raw/eia930_emissions/ERCO.xlsx` (75,309,284 bytes, equal to the server Content-Length) with `curl -A "Mozilla/5.0" -C - --retry 5`. CO2 columns extracted to `ERCO_co2_hourly.csv` by `src/extract_eia_co2.py` (stream read, about 1 min).
- Validation, ERCO only (70,008 matched valid hours, 2018-07 to 2026-06; `tables/eia_co2_validation_ERCO_v0.csv`; EIA intensity = lbs/kWh x 453.592; EIA mean 354 g/kWh):

| Our series | hourly r | daily r | mean bias, ours minus EIA (g/kWh) | MAE |
|---|---|---|---|---|
| Lifecycle CI (AR5 medians, as in the paper) | 0.981 | 0.983 | -0.9 (TRAIN -3.2, DEV +4.0, TEST +7.8) | 10.8 |
| Direct CI, AR5 direct medians (760, 370) | 0.997 | 0.998 | -70.3 | 70.3 |
| Direct CI, EIA US 2023 factors (1048, 435, 1116) | 0.999 | 0.999 | +5.4 | 6.5 |

  Reading: the temporal shape agrees with EIA almost perfectly (r 0.98 to 0.999), so the fuel-mix pipeline and the schema mapping are right. The near-zero mean bias of the lifecycle CI is partly coincidence: the lifecycle uplift roughly offsets the gap between ERCO's EIA fleet coal factor (about 1100 g/kWh) and the AR5 coal median. Level agreement in other BAs will differ; only ERCO was checked, so no per-BA bias is available for the others.

## Part 2. Audit and cleaning (`src/clean_ci.py`; constants at the top of the file)

Fixed rules (no tuning on DEV or TEST; a timestamp belongs to the period of its hour start, i.e. stamp minus 1 h):
1. **Grid (R1)**: one complete hourly end-of-hour UTC grid per BA from 2018-07-01 09:00 to 2026-07-01 00:00 (70,108 h). Starting at 09:00 because every BA is reporting by 08:00 UTC on 2018-07-01; earlier hours cannot be repaired (no past value). Costs 8 h of TRAIN.
2. **Invalid hour (R2)**: `gen_total_mw` missing or <= 0, or CI missing; CI set to NaN. (In the files all rows exist; invalid hours appear as generation 0.)
3. **Outlier (R3)**: d_t = CI_t minus CI_{t-1}; robust z = |d_t - med| / max(1.4826 x MAD, 1 g/kWh), med and MAD over a centred 30-day window (721 h, at least 168 h); outlier if z > 8 or CI outside [0, 1100]. The 1 g/kWh scale floor stops constant-CI hydro BAs from giving infinite z. A one-hour spike flags both its up and down steps and both hours are repaired; a persistent step flags only its first hour.
4. **Repair (R4)**: maximal run of NaN (invalid plus outlier) hours of length <= 3 h: linear interpolation (flag 1; flag 2 where the hour was an outlier). 4 to 168 h: same hour one week earlier from the already repaired series (flag 3). Longer runs, or runs whose week-earlier hour is itself missing: stay NaN (flag 4) and the whole UTC calendar day (hour-start date) is marked unusable. **Additive deviation from the spec**: flag value 4 and column `usable_day` were added to `ci_clean_v0.parquet` (columns: ba, utc, ci_clean, flag, usable_day); flags 0 to 3 are as in the spec. Downstream code must skip or handle NaN and unusable days.
5. **Eligibility (R5)**: first valid hour on or before 2018-09-01 and last valid hour on or after 2026-06-30 23:00 UTC; at least 95 % valid (neither invalid nor outlier) hours in each of TRAIN, DEV, TEST; mean generation over valid hours >= 100 MW; std of ci_clean in TRAIN > 1 g/kWh. (My first draft demanded a valid hour on 2018-07-02, which wrongly dropped ERCO, SWPP, BANC and others over a few early-July 2018 gap days; relaxed once before looking at any DEV or TEST result.)

### Counts per rule (37 eligible BAs together, 2,594,440 BA-hours; all 70 BAs are in `tables/cleaning_counts_v0.csv`)
| Rule | Hours or runs |
|---|---|
| R2 invalid (generation <= 0 or missing) | 7,916 h |
| R3 outliers (z > 8; none from the range test) | 10,151 h (0.39 %) |
| R4 short runs, linear | 8,294 runs, 9,734 h |
| R4 week-earlier fill | 191 runs, 2,579 h |
| R4 long runs left NaN | 12 runs, 5,754 h; 252 unusable BA-days |
| Output flags | 0: 2,576,373; 1: 115; 2: 9,619; 3: 2,579; 4: 5,754 |

All 70 BAs: 218,294 invalid h, 59,350 outliers. Highest outlier rates among eligible BAs: SPA 2.5 %, SEC 1.6 %, CISO 1.3 %, PGE 1.0 %, GVL 0.9 %. Long gaps: PJM 1,680 h (71 days), SWPP 1,461 h, TEPC 1,012 h, SRP 575 h, FPL 504 h, BANC 263 h, LDWP 215 h, PACW 23 h, ERCO 21 h.
Caution for the PREREG: the outlier rule also removes some genuine fast ramps (solar in CISO, hydro in PGE); interpolating those hours changes them slightly. A no-outlier-repair sensitivity is cheap.

### Eligible BAs (37)
AECI AVA AZPS BANC BPAT CISO CPLE DUK ERCO FMPP FPL GVL IPCO ISNE JEA LDWP LGEE MISO NWMT NYIS PACE PACW PGE PJM PNM PSCO PSEI SC SCEG SEC SOCO SPA SRP SWPP TEPC TVA WALC
Some are small (GVL 213 MW, SPA 683 MW). The 100 MW floor is low; the controller may want a size cut for the main analysis (not applied here).

### Dropped (33 of 70; reasons per BA in `ba_eligibility_v0.csv`)
- Ended or started outside the span: AEC (ends 2021-09), EEI (2020-02), GLHB (2020-03 to 2022-09), GRIF (2023-11), HGMA (2025-06), OVEC (2018-12), WACM (ends 2026-04), WAUW (2026-04), WWA (2025-10), BHBA, SWPW, SIKE (start 2026 or mid-2025), NSB (no valid hour), HST (1.6 to 2.9 % valid).
- Under 95 % valid in at least one period: AVRN, CPLW, DEAA, EPE, FPC (DEV 0.935), GRID (TRAIN 0.949), IID, NEVP, SEPA, TAL, TEC, TIDC (TEST 0.941), YAD, GWA.
- Constant series (std of CI in TRAIN <= 1 g/kWh): CHPD, DOPD, GCPD, SCL, TPWR (all hydro, CI about 24).
- Mean generation < 100 MW: GWA, HST, SIKE, WAUW, WWA (all also fail another rule).
GRID and FPC fail narrowly; thresholds are fixed so they stay dropped.

### Schema change 2024-07-01
Code and tables: `src/schema_check_ci.py`, `tables/schema_break_windows_v0.csv` (and the coarser monthly `tables/schema_break_check_v0.csv`).
1. **Coverage test (decisive)**: mapped-fuel generation divided by reported Net Generation (Adjusted), 14 days before vs after 1 July, 2022 to 2024. The before/after shift is within +-0.02 for every eligible BA in 2024 except CISO (-0.010), WALC (-0.036; 2023: -0.051, same sign and size, so not a break) and a handful at +-0.003. So the old-to-new column mapping (hydro = hydro excl. pumped + pumped storage, solar and wind without-battery columns, geothermal into other) preserves the total. Battery storage columns are not mapped (excluded by design in `build_ci.py`); WALC and CISO have coverage above 1 for that or another reason I did not trace.
2. **Level test**: change in mean CI, 17-30 June vs 1-14 July, 2024 versus the mean and sd of the same difference in 2019-2023. Flags (|z| > 3 and |excess| > 15 g/kWh): 3 of 37, DUK (z -3.4), FMPP (-4.4), NWMT (+5.2). The mix itself moved in each (NWMT coal share 17 % to 54 % in the 2024 window as hydro and wind fell; FMPP and DUK shifted between coal and gas) with coverage unchanged, so these look physical rather than schema artefacts. The coarser monthly June-to-July comparison versus 2023 flags 14 BAs, but it is dominated by weather noise (jumps of 50 to 100 g/kWh in both directions); not used.
3. Conclusion: **no BA shows a schema-induced jump; none dropped or flagged for it.**

## Notes for the controller
- `ci_clean_v0` ci_clean: float32, min 12, max 820.
- Final build: updated CSV is ready; `python src/build_ci.py` (no `--pilot` needed, no TO_VERIFY left; the `PROVISIONAL` dict is now unused), then `python src/clean_ci.py --final` and `python src/schema_check_ci.py --final`. Eligibility may shift by a BA when `other` goes from 700 to 230.
- `data/scratch_a06/` holds fetched pages, Electricity Maps config and the AR5 PDF (safe to delete after you copy the AR5 PDF if wanted).

## USER STEPS NEEDED
None. Optional: to validate more BAs, download `https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx` (60 to 100 MB each) into `data\raw\eia930_emissions\`, then `python src\extract_eia_co2.py <BA>` and `python src\validate_eia_ci.py <BA>`.
