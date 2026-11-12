# Commands of every TEST run (PH5; written 2026-11-12 by agent A19)

Run from `paper_A`. Python launcher `py` (Python 3.14.3, numpy 2.4.2; see `research/ENVIRONMENT.txt`). Frozen code md5 as in `research/PREREG.md` line 4 (re-checked 2026-11-12: all five match).
"Recorded" = the command line itself is in a log or note. The simulator and analysis commands were typed interactively and their
command lines were NOT saved verbatim. They are reconstructed from the argument parser defaults, `RUN.txt`, the logs, and the ledger
`source` strings, and are marked "reconstructed". The reconstruction is checked by result: `src/rebuild_ledgers.py` (analysis step) reproduces
both stored ledgers exactly (4221 and 1407 rows, max abs difference 0).

## Inputs (before TEST)
| step | command | status |
|---|---|---|
| CI build and cleaning | `src/build_ci.py`, `src/clean_ci.py` (logs `logs/build_ci_final.log`, `logs/clean_ci_final.log`) | script names recorded; exact arguments not recorded |
| jobs | `PYTHONIOENCODING=utf-8 python src/prep_jobs.py` | recorded (research/A07_JOBS.md) |
| forecasts (final) | `python src/forecast.py --input data/derived/ci_clean.parquet --tag "" --shares data/derived/ci_hourly.parquet` | recorded (research/A05_FORECASTS.md; log `logs/a05_forecast_final.log`, 478 s) |

## TEST simulation (scored once, 2026-11-11, IST)
| run | command | status |
|---|---|---|
| main | `py src/simulate.py --period TEST --workers 3` (all other arguments at their defaults: `--tag ""`, `--fc-dir data/derived/forecasts`, `--reps 3`, `--n-jobs 20000`, `--seed 20261111`, `--states COMPLETED`, `--jobs data/derived/jobs.parquet`) | reconstructed from `results/sim_TEST/RUN.txt` (`reps=3 n_jobs=20000 seed=20261111 states=COMPLETED`, 42 BAs, 3 traces, 1219 s) and `logs/sim_TEST.log` (3 workers); the `--workers 3` value is read from the joblib line "n_jobs=3". Not recorded verbatim. |
| near-limit | `py src/simulate.py --period TEST --workers 3 --out-suffix _nearlimit --exclude-near-limit` | reconstructed from `results/sim_TEST_nearlimit/RUN.txt` (same settings, output folder suffix `_nearlimit`, `tag=` empty, 1174 s), `logs/sim_TEST_nearlimit.log` and the flag in `simulate.py` line 221. `RUN.txt` does not record `--exclude-near-limit` (A08 2c). Not recorded verbatim. |

## TEST analysis (frozen src/analyze.py, B = 2000, seed 7 + S)
Defaults: `--B 2000 --seed 7 --fc lgbm --primary-slack 12 --boot fixed`. Each command appends rows to the ledger named in the table; rows of one run are keyed by `TEST[<tag>].<trace>.<weight>[.twostage]`.
| run | command(s) | ledger | status |
|---|---|---|---|
| main, weighted and unweighted | `py src/analyze.py --period TEST --trace <T> --weight w` and `... --weight u`, for T in PM100, FDATA, KIT_FH2 | `tables/ledger_TEST.csv` (source `results/analysis_TEST_<T>_<w>.json`) | reconstructed from the ledger source strings and `src/analyze.py`; not recorded verbatim |
| two-stage | `py src/analyze.py --period TEST --trace <T> --weight w --boot twostage`, for the three traces | `tables/ledger_TEST.csv` (source `results/analysis_TEST_<T>_w_twostage.json`; keys `TEST.<T>.w.twostage.*`) | reconstructed; the flag is recorded in the file name and in the JSON field `boot` (A08 2c); command not recorded verbatim |
| near-limit | `py src/analyze.py --period TEST --tag _nearlimit --trace <T> --weight w`, for the three traces | `tables/ledger_TEST_nearlimit.csv` (source `results/analysis_TEST_nearlimit_<T>_w.json`) | reconstructed; not recorded verbatim |

The order in which the 12 analysis runs were made is not recorded (it does not change any value; `rebuild_ledgers.py` compares by key).

## Post-hoc and checks (recorded; written by the agent that ran them)
| step | command | output |
|---|---|---|
| PH1-PH4 | `py src/posthoc_inference.py` (defaults `--traces PM100,FDATA,KIT_FH2 --weights w,u --B 2000 --seed 7`) | `tables/ledger_TEST_posthoc.csv`, `results/analysis_TEST_posthoc_<trace>.json`, `research/A19_POSTHOC.md` |
| ledger rebuild | `py src/rebuild_ledgers.py` (about 70 s, peak RSS well under 1 GB, writes only to a temp folder) | prints PASS or the differences |
| environment | `py -m pip freeze` | `research/ENVIRONMENT.txt` |
| result checksums | `find results/sim_TEST results/sim_TEST_nearlimit data/derived/forecasts data/derived/forecasts_v0 -type f \| sort \| xargs md5sum`, then `md5sum results/analysis_TEST*.json` | `research/RESULTS_MD5.txt` (check: `md5sum -c research/RESULTS_MD5.txt`) |
