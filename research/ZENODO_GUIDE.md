# Zenodo guide: publish the Paper A slim archive (owner steps)

Written 2026-11-12 by agent A37. Checked the same day against the public Zenodo help page
https://help.zenodo.org/docs/deposit/create-new-upload/ . The upload form itself sits behind your login, so only the labels the help page names are
verified: **New upload** (in the drop-down of the plus icon in the page header), **Upload files**, **Get a DOI now!**, **Resource type**, **Title**,
**Creators** with the button **Add creator**, **Save draft**, **Publish**. Labels marked "(form)" below were not visible to us. If a label or the layout
differs, follow the nearest label with the same meaning and tell the controller what you saw. Nothing was uploaded or published by an agent; you do every
step. Never paste a password or token into the chat.

Owner rule: the owner uploads. Recommended route (see `GITHUB_GUIDE.md`, section 6): this manual upload, not the GitHub integration.

## 0. What to upload
One file: `submission/archive/paper_A_repro.zip` (built by `python src/paper/build_package.py`; rebuild it after the last result lands, then re-check
the checksum in `submission/SHA256SUMS.txt`). Snapshot of 2026-11-12 11:33: 508 files, 5.9 MB zipped (19.6 MB unzipped) (limit of Zenodo: 50 GB per record, 100 files; a single zip is allowed).

ORDER OF STEPS (updated 2026-11-12 by the controller): (1) reserve the DOI (section 2) and send it to the controller; (2) the controller writes the DOI,
release date and repository link into the manuscript, `CITATION.cff` and README, and rebuilds the zip; (3) you upload the rebuilt zip (section 3) and
check its SHA-256; (4) Save draft until submission; Publish when you decide.

Contents (all small; no raw data, no simulation arrays):
| Folder in the zip | What | Size |
|---|---|---|
| `src/` | pipeline code: download, cleaning, job preparation, forecasters, simulator, analysis, post-hoc and sensitivity scripts, figures, `rebuild_ledgers.py` | 0.5 MB |
| `tables/` | result ledgers (`ledger_*.csv`) and table sources | 4.5 MB (2.4 MB zipped with the rest) |
| `results/` | small JSON and CSV result files (each under 5 MB); not `results/sim_*` (about 3.5 GB) | 5 MB |
| `research/` | pre-registration `PREREG.md` and its `.md5`, deviations, panel decisions, post-freeze plans, `RESULTS_MD5.txt`, run commands, pipeline spec, data ledger | 1 MB |
| `paper/` | `ledger_used.csv` (every manuscript number with its source row) and `references.bib` | small |
| root | `README.md`, `LICENSE`, `CITATION.cff` (from `submission/repo_files/`; the owner fills the bracketed fields before upload) | small |

Left out on purpose: `data/raw` (4.4 GB), `data/derived` (1.7 GB), `results/sim_*` (about 3.5 GB), publisher PDFs under `research/sources/`
(copyright), agent scratch folders, build artefacts. Input data stay at their own sources (listed in the README and the manuscript).

Before uploading, open the zip once and confirm that `README.md`, `LICENSE` and `CITATION.cff` have no `[OWNER: ...]` left.

## 1. Sign in and open a new upload
1. Go to https://zenodo.org and log in with your own account (ORCID, GitHub or e-mail).
2. In the page header click the plus icon and choose **New upload**.
3. The form opens with the basic-information fields at the top and the access options further down.

## 2. Reserve the DOI first (so the manuscript can cite it)
1. Scroll to the field for the Digital Object Identifier (form). Click **Get a DOI now!**. Zenodo reserves a DOI and shows it.
2. Copy that DOI. Send it to the controller: it goes into the manuscript (Data availability and Code availability sections), the cover letter,
   `CITATION.cff` and the README. The reserved DOI does not resolve until you click **Publish**.
3. Keep the upload as a draft until the zip is final (section 5).

## 3. Files
1. Click **Upload files** (or drag the zip into the box) and select `paper_A_repro.zip`.
2. Wait for the progress bar to complete. Check that the size shown matches the local file (about 5.9 MB; it changes slightly after the DOI is added).

## 4. Metadata (suggested text; fill only what is true)
| Field | Entry |
|---|---|
| **Resource type** | **Software** (code plus ledgers). If the list does not offer it, **Dataset**. |
| **Title** | `Code, result ledgers and pre-registration for: History-based runtime estimates raise the modeled carbon savings of forecast-guided HPC batch scheduling` |
| **Creators** (**Add creator**, in this order) | 1. Goenka, Shlok Kumar; 2. N, Balaji; 3. G N, Balaji. Affiliation for each: "School of Computer Science and Engineering, Vellore Institute of Technology, Vellore, India". Role (if asked): leave default or "Researcher". Add ORCID iDs if you have them. |
| **Description** (form) | "Replay code, frozen pre-registration (with md5), result ledgers and small result files for a counterfactual replay of three real HPC job traces (PM100, F-DATA, KIT FH2) on 42 U.S. balancing-authority carbon-intensity series (EIA-930). Raw data are not included; the README lists their sources and licences. `src/rebuild_ledgers.py` rebuilds the frozen test ledgers from the saved results." |
| **License** (form, name may be **Licenses**) | Search and select **MIT License** for code and ledgers. The input data keep their own licences, stated in the README: EIA-930 public domain (U.S. government work); PM100 and F-DATA CC BY 4.0; KIT ForHLR II workload log (Parallel Workloads Archive) under a citation request. Because the zip carries no raw input data, the MIT licence covers what is in it. (Alternative if you prefer a data-style licence for the ledgers: CC BY 4.0.) |
| **Keywords** (form) | carbon-aware scheduling; HPC batch jobs; temporal shifting; walltime estimates; carbon intensity forecasting; pre-registration |
| **Related works** (form; name may differ) | Add the manuscript DOI or preprint URL once it exists, relation `is supplement to`; add the source links of the three traces and `https://www.eia.gov/electricity/gridmonitor/` with relation `is derived from` (or `references`). |
| **Version** | `1.0.0` |
| **Funding, Contributors, Communities** | Skip unless your funder or journal asks. |

## 5. Access options and save versus publish
* **Save draft** keeps the form and the reserved DOI private and editable. Use it until the manuscript is submitted and the zip is final.
* A draft can be shown to the editor or reviewers with a secret link: open the draft, click **Share**, open the **Links** tab, create a link with
  the permission "Can preview draft", copy it. If the journal review is anonymous, make the creator entry anonymous until acceptance
  (metadata of a published record is public even when files are restricted).
* **Publish** is irreversible for the DOI and metadata (files may be corrected for 30 days, then only through a new version). Click it only when the
  controller confirms the zip is final, then send the published DOI (it is the reserved DOI) to the controller.
* After publishing: the controller puts the DOI into the manuscript, `CITATION.cff`, README and cover letter, and rebuilds the package.

## 6. What to tell the controller when done
`done: <DOI> (reserved|published), zip SHA-256 <value from submission/SHA256SUMS.txt>, licence chosen <name>`.
