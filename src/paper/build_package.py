"""build_package.py: build paper_A/submission/ in one command once the last results have landed.

Usage (from paper_A/, Python 3.14, NOT with -I because python-docx and lxml live in the user site):
    python src/paper/build_package.py [--rebuild] [--no-docx] [--no-wm] [--no-archive] [--no-texcheck]
  --rebuild      run the whole chain first: fill_ledger + LaTeX (src/paper/build_paper.py), then DOCX (build_docx.py)
  --no-docx      reuse paper/manuscript.docx as is
  --no-wm        skip the hidden-unicode scans
  --no-archive   skip the slim Zenodo archive (submission/archive/paper_A_repro.zip)
  --no-texcheck  skip the test compile of latex_source.zip

Writes submission/: manuscript.pdf, manuscript.docx, latex_source.zip, highlights.docx, Figure_1..13 (.png 300 dpi + .pdf),
supplementary.pdf, cover_letter.docx (filled from paper/cover_letter.tmpl.md), README.md, SHA256SUMS.txt, wm_report.txt,
package_check.json, archive/paper_A_repro.zip. It never uploads, pushes or publishes anything, and never cleans hidden characters:
wm findings are only reported.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPER = os.path.join(ROOT, "paper")
SUB = os.path.join(ROOT, "submission")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
WM = os.path.join(os.path.expanduser("~"), ".claude", "skills", "hidden-unicode", "scripts", "wm.ps1")
NFIG = 13
checks = {}


def log(msg):
    print(msg, flush=True)


def rd(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()


def wr(p, s):
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)


def need(path, what):
    if not os.path.isfile(path):
        checks[what] = "MISSING " + path
        log("MISSING " + path)
        return False
    return True


# ------------------------------------------------------------------ 0 rebuild chain
def rebuild():
    for cmd in ([sys.executable, os.path.join(HERE, "build_paper.py")],):
        r = run(cmd, cwd=ROOT)
        log("build_paper rc=%d %s" % (r.returncode, r.stdout.strip().splitlines()[-1:] or ""))
        checks["build_paper_rc"] = r.returncode
        if r.returncode:
            sys.exit("build_paper failed; stop. " + r.stderr[-500:])


def build_docx():
    r = run([sys.executable, os.path.join(HERE, "build_docx.py"), "main"], cwd=ROOT)
    log("build_docx rc=%d %s" % (r.returncode, r.stdout.strip().splitlines()[-1:] or r.stderr[-300:]))
    checks["build_docx_rc"] = r.returncode
    r = run([sys.executable, os.path.join(HERE, "verify_docx.py")], cwd=ROOT)
    fails = [l for l in r.stdout.splitlines() if l.startswith("FAIL")]
    checks["verify_docx_rc"] = r.returncode
    checks["verify_docx_fails"] = fails
    log("verify_docx rc=%d fails=%s" % (r.returncode, fails))


# ------------------------------------------------------------------ 1 straight copies
def copy_main():
    for src, dst in (("main.pdf", "manuscript.pdf"), ("manuscript.docx", "manuscript.docx"), ("supplement.pdf", "supplementary.pdf")):
        p = os.path.join(PAPER, src)
        if need(p, "copy_" + dst):
            shutil.copyfile(p, os.path.join(SUB, dst))
            log("copied %s -> %s (%d bytes)" % (src, dst, os.path.getsize(p)))


# ------------------------------------------------------------------ 2 figures
def figure_sources():
    """Printed figure number -> source file stem. The source files keep the old FIGURE_PLAN numbering (figures/Figure_<k>),
    which differs from the order LaTeX prints (e.g. printed Figure 2 is figures/Figure_3). Read the label of each float in
    paper/floats.tex and its printed number in paper/main.aux, so submission/Figure_<n> is the figure the text calls Figure n."""
    fl = rd(os.path.join(PAPER, "floats.tex"))
    aux = rd(os.path.join(PAPER, "main.aux"))
    num = {m.group(1): m.group(2) for m in re.finditer(r"\\newlabel\{(fig:[^}]+)\}\{\{(\d+)\}", aux)}
    out = {}
    for m in re.finditer(r"\\figfile\{figures/(Figure_\d+)\.pdf\}.*?\\label\{(fig:[^}]+)\}", fl, flags=re.S):
        out[int(num[m.group(2)])] = m.group(1)
    if sorted(out) != list(range(1, NFIG + 1)):
        sys.exit("figure map incomplete: %s" % out)
    checks["figure_map_printed_to_source"] = {str(k): v for k, v in sorted(out.items())}
    return out


def figures():
    from PIL import Image
    out = []
    fmap = figure_sources()
    for n in range(1, NFIG + 1):
        for ext in ("png", "pdf"):
            p = os.path.join(ROOT, "figures", "%s.%s" % (fmap[n], ext))
            if not need(p, "figure_%d_%s" % (n, ext)):
                continue
            shutil.copyfile(p, os.path.join(SUB, "Figure_%d.%s" % (n, ext)))
        pp = os.path.join(SUB, "Figure_%d.png" % n)
        if os.path.isfile(pp):
            im = Image.open(pp)
            dpi = im.info.get("dpi", (0, 0))
            out.append({"fig": n, "px": im.size, "dpi": [round(float(dpi[0])), round(float(dpi[1]))] if dpi[0] else None})
    checks["figures"] = out
    low = [o for o in out if not o["dpi"] or o["dpi"][0] < 300]
    checks["figures_below_300dpi_or_untagged"] = [o["fig"] for o in low]
    log("figures: %d png checked; dpi < 300 or untagged: %s" % (len(out), [o["fig"] for o in low]))


# ------------------------------------------------------------------ 3 highlights
def highlights():
    import docx
    from docx.shared import Pt, RGBColor
    lines = [l.strip() for l in rd(os.path.join(PAPER, "highlights.txt")).splitlines() if l.strip()]
    d = docx.Document()
    st = d.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(11)
    d.core_properties.author = ""
    d.core_properties.comments = ""
    d.core_properties.title = "Highlights"
    for l in lines:
        d.add_paragraph(l, style="List Bullet")
    d.save(os.path.join(SUB, "highlights.docx"))
    mx = max(len(l) for l in lines)
    checks["highlights"] = {"n": len(lines), "max_chars": mx, "ok": 3 <= len(lines) <= 5 and mx <= 85}
    log("highlights.docx: %d bullets, longest %d characters (limit 85)" % (len(lines), mx))


# ------------------------------------------------------------------ 4 cover letter
def cite_names():
    bib = rd(os.path.join(PAPER, "references.bib"))
    names = {}
    for m in re.finditer(r"@\w+\{(suscom_\d+),(.*?)\n\}", bib, re.S):
        body = m.group(2)
        a = re.search(r"author = \{([^}]*)\}", body)
        y = re.search(r"year = \{(\d+)\}", body)
        first = a.group(1).split(" and ")[0].split(",")[0] if a else m.group(1)
        names[m.group(1)] = "%s et al., %s" % (first, y.group(1) if y else "n.d.")
    return names


def cover_letter():
    import fill_ledger as fl
    tmpl = rd(os.path.join(PAPER, "cover_letter.tmpl.md"))
    tmpl = re.sub(r"<!--.*?-->\s*", "", tmpl, flags=re.S)
    src = fl.load_sources(fl.ledger_paths(os.path.join(ROOT, "tables")), ROOT)
    errors, warnings, ledger = list(src.errors), [], []
    allow_dev = fl.read_list(os.path.join(PAPER, "ALLOW_DEV_KEYS.txt"), True)
    filled = fl.fill_text(tmpl, "paper/cover_letter.tmpl.md", src, allow_dev, set(), errors, warnings, ledger)
    names = cite_names()
    filled = re.sub(r"\[(suscom_\d+)\]", lambda m: "(" + names.get(m.group(1), m.group(1)) + ")", filled)
    filled = filled.replace("PENDING", "PENDING")
    checks["cover_letter_ledger_errors"] = errors
    checks["cover_letter_placeholders"] = len(ledger)
    if errors:
        log("cover letter: ledger errors (left as <<..>>): %s" % errors[:3])
    wr(os.path.join(PAPER, "cover_letter.md"), filled)
    ref = os.path.join(HERE, "docx_assets", "reference.docx")
    out = os.path.join(SUB, "cover_letter.docx")
    r = run(["pandoc", "-f", "markdown-smart", "-t", "docx", os.path.join(PAPER, "cover_letter.md"), "--reference-doc", ref, "-o", out])
    log("cover_letter.docx pandoc rc=%d %s" % (r.returncode, r.stderr[:200]))
    checks["cover_letter_pandoc_rc"] = r.returncode
    words = len(re.sub(r"[*_]", "", filled).split())
    checks["cover_letter_words"] = words
    left = re.findall(r"\[(?:OWNER|USER)[^\]]*\]|\[[A-Z_]{6,}[^\]]*\]", filled)
    checks["cover_letter_owner_placeholders"] = len(left)
    log("cover letter: %d words, %d owner placeholders" % (words, len(left)))


# ------------------------------------------------------------------ 5 LaTeX source zip
def latex_zip(texcheck):
    kp = lambda f: run(["kpsewhich", f]).stdout.strip()
    files = {}
    for f in ("main.tex", "papertitle.tex", "references.bib", "references_manual.bib", "main.bbl", "supplement.tex", "supplement.aux"):
        files[f] = os.path.join(PAPER, f)
    for d, _, fs in os.walk(os.path.join(PAPER, "sections", "placed")):
        for f in fs:
            files["sections/placed/" + f] = os.path.join(d, f)
    files["sections/S_supplement.tex"] = os.path.join(PAPER, "sections", "S_supplement.tex")
    # the placed sections point to tables/_filled/... and tables/T3_arms.tex relative to paper/; keep paper-relative paths
    files2 = dict(files)
    for f in os.listdir(os.path.join(PAPER, "tables")):
        p = os.path.join(PAPER, "tables", f)
        if os.path.isfile(p):
            files2["tables/" + f] = p
    for f in os.listdir(os.path.join(PAPER, "tables", "_filled")):
        files2["tables/_filled/" + f] = os.path.join(PAPER, "tables", "_filled", f)
    for n in range(1, NFIG + 1):
        files2["figures/Figure_%d.pdf" % n] = os.path.join(ROOT, "figures", "Figure_%d.pdf" % n)
    for f in ("elsarticle.cls", "elsarticle-num.bst"):
        p = kp(f)
        if p:
            files2[f] = p
        else:
            checks["latex_missing_" + f] = True
    zp = os.path.join(SUB, "latex_source.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for k in sorted(files2):
            if os.path.isfile(files2[k]):
                if k.endswith(".tex"):
                    # A46: ship the sources without internal comment lines (agent notes, owner rules)
                    with open(files2[k], encoding="utf-8", newline="") as fh:
                        txt = fh.read()
                    txt = "".join(l for l in txt.splitlines(True) if not re.match(r"^\s*%", l))
                    z.writestr(k, txt)
                else:
                    z.write(files2[k], k)
            else:
                checks.setdefault("latex_zip_missing_files", []).append(k)
        z.writestr("BUILD.txt", "pdflatex main; bibtex main; pdflatex main; pdflatex main  (run in this folder; main.bbl is included)\n"
                                "The class elsarticle and the style elsarticle-num come from TeX Live / MiKTeX; copies are included.\n")
    log("latex_source.zip: %d files, %d bytes" % (len(files2), os.path.getsize(zp)))
    checks["latex_zip_files"] = len(files2)
    if texcheck:
        tmp = tempfile.mkdtemp(prefix="a37_tex_")
        with zipfile.ZipFile(zp) as z:
            z.extractall(tmp)
        ok = True
        for cmd in (["pdflatex", "-interaction=nonstopmode", "main.tex"], ["pdflatex", "-interaction=nonstopmode", "main.tex"]):
            r = run(cmd, cwd=tmp)
            ok = ok and os.path.isfile(os.path.join(tmp, "main.pdf"))
        pdf = os.path.join(tmp, "main.pdf")
        log_ = rd(os.path.join(tmp, "main.log")) if os.path.isfile(os.path.join(tmp, "main.log")) else ""
        err = re.findall(r"^!.*$", log_, re.M)[:3]
        checks["latex_zip_builds"] = {"pdf": os.path.isfile(pdf), "first_errors": err, "undefined_refs": len(re.findall(r"undefined", log_))}
        log("latex_source.zip test compile in %s: %s" % (tmp, checks["latex_zip_builds"]))


# ------------------------------------------------------------------ 6 slim Zenodo archive
ARCH_RESEARCH = ("PREREG.md", "PREREG.md5", "PREREG_DEVIATIONS.md", "PANEL_DECISIONS.md", "PANEL_DECISIONS.md5", "P4_PLAN.md", "P4_PLAN.md5",
                 "P4_PLAN_AMEND.md", "P4_PLAN_AMEND.md5", "P4_PLAN_AMEND2.md", "P4_PLAN_AMEND2.md5", "P4_PLAN_X.md", "P4_PLAN_X.md5",
                 "POSTHOC_ADD.md", "POSTHOC_ADD.md5", "RESULTS_MD5.txt", "RUN_COMMANDS.md", "PIPELINE_SPEC.md", "A26_DATA_LEDGER.md",
                 "A06_DATA_AUDIT.md", "ENVIRONMENT.txt")


def archive():
    ad = os.path.join(SUB, "archive")
    os.makedirs(ad, exist_ok=True)
    zp = os.path.join(ad, "paper_A_repro.zip")
    n = 0
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        def add(p, arc):
            nonlocal n
            z.write(p, "paper_A_repro/" + arc.replace("\\", "/"))
            n += 1
        for d, dirs, fs in os.walk(os.path.join(ROOT, "src")):
            dirs[:] = [x for x in dirs if x != "__pycache__"]
            for f in fs:
                if not f.endswith((".pyc",)):
                    add(os.path.join(d, f), os.path.relpath(os.path.join(d, f), ROOT))
        for d, dirs, fs in os.walk(os.path.join(ROOT, "tables")):
            for f in fs:
                add(os.path.join(d, f), os.path.relpath(os.path.join(d, f), ROOT))
        for d, dirs, fs in os.walk(os.path.join(ROOT, "results")):
            dirs[:] = [x for x in dirs if not x.startswith("sim_")]
            for f in fs:
                p = os.path.join(d, f)
                if f.endswith((".json", ".csv")) and os.path.getsize(p) <= 5_000_000:
                    add(p, os.path.relpath(p, ROOT))
        for f in ARCH_RESEARCH:
            p = os.path.join(ROOT, "research", f)
            if os.path.isfile(p):
                add(p, "research/" + f)
        for f in ("ledger_used.csv", "references.bib"):
            p = os.path.join(PAPER, f)
            if os.path.isfile(p):
                add(p, "paper/" + f)
        for f in ("LICENSE", "CITATION.cff", "README.md"):
            p = os.path.join(SUB, "repo_files", f)
            if os.path.isfile(p):
                add(p, f)
    checks["archive"] = {"files": n, "bytes": os.path.getsize(zp), "sha256": sha256(zp)}
    log("archive %s: %d files, %d bytes" % (zp, n, os.path.getsize(zp)))


# ------------------------------------------------------------------ 7 hidden-unicode
def wm_scan():
    if not os.path.isfile(WM):
        checks["wm"] = "not available"
        wr(os.path.join(SUB, "wm_report.txt"), "wm.ps1 not found at %s\n" % WM)
        return
    out = []
    tot = {}

    def wm(args, label):
        r = run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", WM] + args, timeout=900)
        out.append("=== %s (rc=%d)\n%s%s" % (label, r.returncode, r.stdout[-6000:], r.stderr[-1000:]))
        tot[label] = r.returncode
        log("wm %s rc=%d" % (label, r.returncode))
    # text files: scan a staging copy of every text deliverable (not the zips)
    stage = tempfile.mkdtemp(prefix="a37_wm_")
    for f in ("README.md", "highlights.docx", "cover_letter.docx", "manuscript.docx", "manuscript.pdf", "supplementary.pdf"):
        p = os.path.join(SUB, f)
        if os.path.isfile(p):
            shutil.copyfile(p, os.path.join(stage, f))
    shutil.copyfile(os.path.join(PAPER, "cover_letter.md"), os.path.join(stage, "cover_letter.md"))
    shutil.copyfile(os.path.join(PAPER, "highlights.txt"), os.path.join(stage, "highlights.txt"))
    for sub in ("sections/placed",):
        d = os.path.join(PAPER, sub)
        for f in os.listdir(d):
            shutil.copyfile(os.path.join(d, f), os.path.join(stage, "sec_" + f))
    for f in ("main.tex", "references.bib", "references_manual.bib"):
        shutil.copyfile(os.path.join(PAPER, f), os.path.join(stage, f))
    wm(["scan", stage], "scan(text deliverables + tex + bib)")
    wm(["audit", stage], "audit(text deliverables + docx + pdf)")
    for f in ("manuscript.docx", "manuscript.pdf", "cover_letter.docx", "highlights.docx"):
        if os.path.isfile(os.path.join(stage, f)):
            wm(["inspect", os.path.join(stage, f)], "inspect " + f)
    wr(os.path.join(SUB, "wm_report.txt"), "wm findings are reported, never auto-cleaned. rc 0 clean, 1 findings, 2 error.\n" + "\n".join(out))
    checks["wm"] = tot
    shutil.rmtree(stage, ignore_errors=True)


# ------------------------------------------------------------------ 8 README and checksums
def readme():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M IST")
    txt = """# Paper A submission package (Sustainable Computing: Informatics and Systems)

Built by `src/paper/build_package.py` on %s. Nothing in this folder has been uploaded or published.
Owner placeholders still to fill are listed in `OWNER_REPORT.md` (title, authors, affiliations, corresponding e-mail, Zenodo DOI,
GitHub link, AI-declaration scope, funding, CRediT).

| File | Upload slot in the submission system |
|---|---|
| `manuscript.docx` | Manuscript (the file that is submitted; verified by `src/paper/verify_docx.py` and a Word render) |
| `manuscript.pdf` | LaTeX PDF of the same text (reading copy; PDF is not accepted as the source file) |
| `latex_source.zip` | Source files, if the system asks for LaTeX (class `elsarticle`, `BUILD.txt` inside) |
| `highlights.docx` | Highlights (separate editable file; 3 to 5 bullets, at most 85 characters each) |
| `Figure_1` to `Figure_13` (`.png` 300 dpi, `.pdf` vector) | Figures, one file each |
| `supplementary.pdf` | Supplementary material |
| `cover_letter.docx` | Cover letter |
| `archive/paper_A_repro.zip` | NOT a journal upload: the slim archive that the owner uploads to Zenodo (`research/ZENODO_GUIDE.md`) |
| `SHA256SUMS.txt` | SHA-256 of every file in this folder (excluding itself) |
| `wm_report.txt` | hidden-unicode scan, audit and inspect output (reported, not cleaned) |
| `OWNER_REPORT.md` | One page for the owner: status, decisions, checks, file list |

Separate uploads that are not in this folder: the Elsevier competing-interest declaration file (made in the Elsevier declarations tool).
""" % now
    wr(os.path.join(SUB, "README.md"), txt)


def sums():
    lines = []
    for d, dirs, fs in os.walk(SUB):
        for f in sorted(fs):
            if f in ("SHA256SUMS.txt",) or f.endswith(".pyc"):
                continue
            p = os.path.join(d, f)
            rel = os.path.relpath(p, SUB).replace("\\", "/")
            lines.append("%s  %s" % (sha256(p), rel))
    wr(os.path.join(SUB, "SHA256SUMS.txt"), "\n".join(sorted(lines, key=lambda s: s.split("  ", 1)[1])) + "\n")
    log("SHA256SUMS.txt: %d entries" % len(lines))


def main():
    ap = argparse.ArgumentParser()
    for a in ("rebuild", "no_docx", "no_wm", "no_archive", "no_texcheck"):
        ap.add_argument("--" + a.replace("_", "-"), action="store_true")
    a = ap.parse_args()
    os.makedirs(SUB, exist_ok=True)
    if a.rebuild:
        rebuild()
    if not a.no_docx:
        build_docx()
    copy_main()
    figures()
    highlights()
    cover_letter()
    latex_zip(not a.no_texcheck)
    if not a.no_archive:
        archive()
    readme()
    if not a.no_wm:
        wm_scan()
    sums()
    checks["built"] = datetime.datetime.now().isoformat(timespec="seconds")
    wr(os.path.join(SUB, "package_check.json"), json.dumps(checks, indent=1, default=str))
    log("done; see submission/package_check.json")


if __name__ == "__main__":
    main()
