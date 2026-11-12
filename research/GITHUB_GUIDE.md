# GitHub guide: create a PRIVATE repository for Paper A's code (owner steps)

Written 2026-11-12 by agent A37. Checked the same day against GitHub's docs page
https://docs.github.com/en/repositories/creating-and-managing-repositories/quickstart-for-repositories . Labels that page names: the **+** icon
(tooltip "Create something new") in the upper-right corner of any page, then **New repository**; the field **Repository name**; a description field;
a visibility choice (the page does not name the options in the web steps; the CLI section names `--public`, `--private`, `--internal`);
the **Add README** toggle; the button **Create repository**. The page does not cover the owner selector, `.gitignore` or licence pickers, so those are
described from general knowledge: confirm them on screen. If the layout differs, follow the nearest label with the same meaning and tell the controller what
you saw. No agent has created a repository, pushed, or logged in. The controller does nothing until you send the repository link.

## 1. Create the repository (web, about 2 minutes)
1. Log in at https://github.com with your own account.
2. In the upper-right corner click the **+** icon ("Create something new"), then **New repository**.
3. **Owner**: your own account (the default).
4. **Repository name**: suggested `carbon-aware-hpc-delay-replay` (short, descriptive, no title wording that is still unapproved). Any name is fine.
5. Description (optional): `Replay code, result ledgers and pre-registration for carbon-aware delay scheduling of HPC batch jobs`.
6. Visibility: choose **Private** (the repository stays private until the paper is accepted; the journal-facing archive is the Zenodo record).
7. Leave **Add README**, **.gitignore** and **license** OFF (the controller pushes these files from the local folder; an initial README on GitHub
   would make the first push fail with a conflict).
8. Click **Create repository**.
9. Copy the repository address (for example `https://github.com/<your-account>/carbon-aware-hpc-delay-replay`) and send it to the controller in the chat as
   `done: <repository link>`.

## 2. What goes in, what stays out
In (about 12 MB with the ledgers): `src/` (all scripts), `tables/` (ledgers and table sources), `research/` plans, pre-registration and checksums,
small JSON and CSV files under `results/`, `paper/ledger_used.csv`, `paper/references.bib`, `README.md`, `LICENSE` (MIT; copyright holders
Shlok Kumar Goenka, Balaji N and Balaji G N, already filled), `CITATION.cff` (title and the three authors filled; DOI, release date and repository link
are added by the controller after you send the link and the reserved DOI). The ready files are in `submission/repo_files/` (`.gitignore`, `LICENSE`, `CITATION.cff`, `README.md`).

Out (by `.gitignore`): `data/raw/` (4.4 GB), `data/derived/` (1.7 GB), `data/scratch_a06/`, `results/sim_*/` (about 3.5 GB) and `results/_secondary_cache.pkl`,
`*.npz`, `*.pkl`, `__pycache__/`, paper build artefacts (`paper/*.aux`, `.log`, `.out`, `.blg`, `.spl`, draft PDFs), `logs/`, `graphify-out/`, `submission/`,
and `research/sources/`, `research/agents/`, `research/team/` (publisher PDFs and agent scratch: copyright and noise). GitHub refuses single files over 100 MB;
none of the included files comes near that.

## 3. How you log in on the laptop (no token ever goes into the chat)
1. Open your own terminal (PowerShell). Run `gh auth status`. On 2026-11-12 it showed you logged in to github.com as `shlokDS16` through the keyring,
   so you may not need to do anything.
2. If it says you are not logged in, run `gh auth login`, choose **GitHub.com**, **HTTPS**, and **Login with a web browser**; copy the one-time code that
   the terminal prints into the page that opens, and approve. The token is stored in the Windows credential store, not in any file of the project.
3. Never paste a token, a one-time code or a password into the chat.

## 4. Commands the controller runs AFTER you send the link
Run from `paper_A/`, one call each, only after the link arrives (`<LINK>` is the link you send). The controller will not create the repository.
```
cd "C:\Users\Shlok\Downloads\Sustainable Computing papers\paper_A"
git init -b main
copy submission\repo_files\.gitignore .gitignore        (PowerShell: Copy-Item)
copy submission\repo_files\LICENSE LICENSE
copy submission\repo_files\CITATION.cff CITATION.cff
copy submission\repo_files\README.md README.md          (replaces the old one-line README.md; the old one is kept as README_old.txt first)
git add src tables research results paper/ledger_used.csv paper/references.bib README.md LICENSE CITATION.cff .gitignore
git status --short | head -50                            (check: no data/, no results/sim_*, no PDFs from research/sources)
git commit -m "Paper A: replay code, ledgers and pre-registration" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git remote add origin <LINK>.git
git push -u origin main
```
Checks before the push: `git count-objects -vH` shows a size of a few tens of MB at most; `git ls-files | wc -l` is a few hundred; `wm scan .` reports 0
findings on the tracked text files. If the push asks for credentials, stop and ask you to run `gh auth login` in your terminal. After the push the controller
opens `<LINK>` read-only (private repository: you must be logged in) and reports the commit hash.

## 5. Who may see it
Private means only you and the people you add (repository **Settings**, **Collaborators**, **Add people**). To let an editor or reviewer read it before
publication, add them as collaborators with read access (they need a GitHub account), or use the Zenodo secret link of the draft record instead
(`ZENODO_GUIDE.md`, section 5). Put the link in the manuscript's Code availability section only when the owner says so; it currently reads
"[GITHUB LINK: owner to provide]".

## 6. GitHub and Zenodo: recommendation
Two routes exist. (a) The GitHub-Zenodo integration: in Zenodo, account settings, GitHub tab, switch the repository on, then publish a GitHub release; Zenodo
archives the release automatically. (b) The manual upload of `paper_A_repro.zip` described in `ZENODO_GUIDE.md`.

Recommended: (b) manual upload. Reasons: the integration works only for repositories that Zenodo can read (it needs access to the repository, and the
archive of a private repository is not a straightforward route); the archive then contains the whole repository rather than the curated slim set; the DOI cannot
be reserved before the release exists, but the manuscript needs the DOI at submission; and the owner rule is that the owner uploads. The private
GitHub repository is the working copy; Zenodo holds the frozen citable snapshot. If the owner later makes the repository public (after acceptance), the
integration can create a second, versioned record from a release; this is optional.
