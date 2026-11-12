# Carbon-aware delay scheduling of HPC batch jobs: replay code, ledgers and pre-registration

Code and small result files for the manuscript "History-based runtime estimates raise the modeled carbon savings of forecast-guided HPC batch scheduling" (Sustainable Computing: Informatics and Systems, under review).
The raw data are not included. Licences of the inputs: EIA-930 (U.S. Energy Information Administration, public domain), PM100 and F-DATA
(CC BY 4.0), KIT ForHLR II workload log (Parallel Workloads Archive; citation request, see the manuscript).

- `src/`: pipeline (EIA-930 download and cleaning, job-trace preparation, forecasters, simulator, analysis, post-hoc and sensitivity scripts, figures).
- `tables/`: result ledgers (`ledger_*.csv`, one row per reported number) and table sources.
- `results/`: small JSON and CSV results (simulation arrays are not included).
- `research/`: pre-registration (`PREREG.md` with its md5 file), deviations, plans and checksums.
- `paper/ledger_used.csv`: every number in the manuscript with its source row.

Reproduce: see `research/RUN_COMMANDS.md`; `src/rebuild_ledgers.py` rebuilds the frozen test ledgers from the saved results.
Archive: Zenodo https://doi.org/10.5281/zenodo.24152932. Contact: Balaji N, n.balaji@vit.ac.in (corresponding author).

## License
Code (`src/`): MIT License (`LICENSE`). Result ledgers, small result files and documentation (`tables/`, `results/`, `research/`, `paper/`): CC BY 4.0 (`LICENSE-DATA`). Both licences are listed on the Zenodo record.
