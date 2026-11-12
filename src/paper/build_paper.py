"""build_paper.py (paper A): fill the templates, place the floats, build the PDFs, report.

Adapted from paper_B/src/paper/build_paper.py (Paper B working pipeline; placement, highlights check and LaTeX driver copied and
changed for Paper A: ledgers, section list, PLACE table, fallback placement, build report).

Steps
 1. python -I src/paper/fill_ledger.py (strict on nothing; literal warnings are printed) on paper/sections/*.tmpl.tex, floats.tmpl.tex,
    main.tmpl.tex, supplement.tmpl.tex. Placeholders are <<key|fmt>> and <<PENDING:key|fmt>> (see fill_ledger.py).
 2. split paper/floats.tex at the "%%FLOAT <label>" markers
 3. copy each filled section to paper/sections/placed/<name>.tex and insert each float after the paragraph that holds its first \ref
    (PLACE table below). A float whose \ref is not yet in its host section is appended at the end of the host section and counted
    in the report ("floats without a \ref"); the section files themselves are never edited for layout.
 4. check that the highlights in 00_frontmatter match paper/highlights.tmpl.txt (at most 85 characters each after filling);
    write paper/highlights.txt (filled)
 5. unless --no-tex: pdflatex main, pdflatex supplement, bibtex main, pdflatex x2 (from paper/); then write paper/build_report.txt
Usage (from the paper_A root):  py -I src/paper/build_paper.py [--no-tex] [--no-fill] [--strict-literals]
Exit code 0 only if the fill, the placement and the LaTeX run all succeeded.
"""
import csv
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAPER = os.path.join(ROOT, "paper")
SEC = os.path.join(PAPER, "sections")

BODY = ["00_frontmatter", "01_intro", "02_related", "03_data", "04_method", "05_results", "06_discussion",
        "07_conclusion", "08_declarations"]
WORD_COUNT_SECTIONS = BODY[1:7]   # Introduction .. Conclusion (declarations and front matter excluded)

# host section -> ordered list of floats; each float follows the paragraph with its first \ref in that host (SPEC s6)
PLACE = {
    "01_intro": ["fig:design"],
    "02_related": ["tab:related"],
    "03_data": ["fig:grids", "fig:walltime", "tab:data"],
    "04_method": ["fig:example", "tab:arms"],
    "05_results": ["fig:forecast", "fig:savings", "tab:confirm", "fig:runtimex", "fig:shapley", "fig:slack", "fig:ba",
                   "fig:explain", "tab:secondary", "fig:robust", "tab:robust", "fig:frozen"],
}

HIGHLIGHT_MAX = 85
FILLED = "_filled"


def read(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()


def read_log(p):
    with open(p, encoding="utf-8", errors="replace", newline="") as f:
        return f.read()


def write(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(t)


def fill(strict_literals):
    files = sorted(glob.glob(os.path.join(SEC, "*.tmpl.tex")))
    files += [os.path.join(PAPER, n) for n in ("floats.tmpl.tex", "main.tmpl.tex", "supplement.tmpl.tex")]
    # table files: T*.tmpl.tex -> T*.tex; a plain T*.tex that holds <<...>> placeholders is filled into tables/_filled/T*.tex
    # and every input or tabfile call of it is redirected there by make_placed (so the writer's source file is never overwritten)
    for stale in glob.glob(os.path.join(PAPER, "tables", FILLED, "*.tex")):
        os.remove(stale)
    files += sorted(glob.glob(os.path.join(PAPER, "tables", "*.tmpl.tex")))
    for tp in sorted(glob.glob(os.path.join(PAPER, "tables", "*.tex"))):
        if ".tmpl." in os.path.basename(tp):
            continue
        if "<<" in read(tp):
            files.append(tp + "::" + os.path.join(PAPER, "tables", FILLED, os.path.basename(tp)))
    cmd = [sys.executable, "-I", os.path.join(ROOT, "src", "paper", "fill_ledger.py")]
    if strict_literals:
        cmd.append("--strict")
    cmd += files
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    print(r.stdout[-3000:])
    if r.stderr.strip():
        print(r.stderr[-6000:])
    if r.returncode != 0:
        sys.exit("fill_ledger failed")
    return r.stdout + r.stderr


def split_floats():
    t = read(os.path.join(PAPER, "floats.tex"))
    parts = re.split(r"^%%FLOAT (\S+)\s*$", t, flags=re.M)
    return {parts[i]: parts[i + 1].strip("\n") + "\n" for i in range(1, len(parts), 2)}


inline_floats = []


def place(text, labels, floats, host, unref):
    lines = text.split("\n")
    depth = 0
    depth_at = []
    for ln in lines:
        depth_at.append(depth)
        depth += len(re.findall(r"\\begin\{", re.sub(r"(?<!\\)%.*", "", ln)))
        depth -= len(re.findall(r"\\end\{", re.sub(r"(?<!\\)%.*", "", ln)))
    inserts = {}
    tail = []
    for lab in labels:
        tf = table_file(floats[lab])
        if tf and re.search(re.escape("\\tabfile{" + tf[0] + "}") + "|" + re.escape("\\input{" + tf[0] + "}"), text):
            inline_floats.append("%s (host %s)" % (lab, host))
            continue
        pat = re.compile(r"\\(?:auto|c)?ref\{[^}]*\b" + re.escape(lab) + r"\b[^}]*\}")
        idx = next((i for i, ln in enumerate(lines) if pat.search(re.sub(r"(?<!\\)%.*", "", ln))), None)
        if idx is None:
            unref.append("%s (host %s)" % (lab, host))
            tail.append(lab)
            continue
        j = idx
        while True:
            end_depth = depth_at[j + 1] if j + 1 < len(lines) else 0
            nxt_blank = (j + 1 >= len(lines)) or lines[j + 1].strip() == ""
            if end_depth == 0 and nxt_blank:
                break
            j += 1
        inserts.setdefault(j, []).append(lab)
    out = []
    for i, ln in enumerate(lines):
        out.append(ln)
        for lab in inserts.get(i, []):
            out.append("")
            out.append(floats[lab].rstrip("\n"))
    for lab in tail:
        out.append("")
        out.append("%% float %s appended: no \\ref{%s} in this section yet" % (lab, lab))
        out.append(floats[lab].rstrip("\n"))
    return "\n".join(out)


def table_file(flt):
    """Path of the table file a table float inputs (paper/tables first, then ../tables as LaTeX searches), or None."""
    m = re.search(r"\\(?:tabfile|input)\{([^}]+)\}", flt)
    if not m:
        return None
    for base in (PAPER, ROOT):
        p = os.path.join(base, m.group(1))
        if os.path.isfile(p):
            return m.group(1), p
    return m.group(1), None


def redirect(text):
    """Point every input or tabfile call of an unfilled table file at its filled copy in tables/_filled/."""
    names = [os.path.basename(p) for p in glob.glob(os.path.join(PAPER, "tables", FILLED, "*.tex"))]
    for n in names:
        text = text.replace("tables/" + n, "tables/%s/%s" % (FILLED, n))
    return text


def make_placed():
    floats = {k: redirect(v) for k, v in split_floats().items()}
    selfcont = []
    for lab, flt in list(floats.items()):
        tf = table_file(flt)
        if tf and tf[1] and re.search(r"\\begin\{table\*?\}", read(tf[1])):
            # self-contained table file (own table or table* environment, caption and label): input as it stands
            floats[lab] = "\\input{%s}\n" % tf[0]
            selfcont.append(lab)
    used = set()
    unref = []
    for name in BODY:
        t = redirect(read(os.path.join(SEC, name + ".tex")))
        if name in PLACE:
            for lab in PLACE[name]:
                if lab not in floats:
                    sys.exit("PLACE names float %s that is not in floats.tmpl.tex" % lab)
            t = place(t, PLACE[name], floats, name, unref)
            used.update(PLACE[name])
        write(os.path.join(SEC, "placed", name + ".tex"), t)
    missing = set(floats) - used
    if missing:
        sys.exit("floats not placed (add them to PLACE): %s" % sorted(missing))
    print("placed %d floats; %d without a \\ref in their host section (appended at its end); %d already inline in their section "
          "(not placed again): %s; self-contained table files: %s" % (len(used), len(unref), len(inline_floats), inline_floats, selfcont))
    return len(used) - len(inline_floats), unref


def highlights():
    fm = read(os.path.join(SEC, "00_frontmatter.tex"))
    m = re.search(r"\\begin\{highlights\}(.*?)\\end\{highlights\}", fm, flags=re.S)
    items = [s.strip() for s in re.split(r"\\item", m.group(1)) if s.strip()]
    items = [i.replace("\\,", " ").replace("\\%", "%") for i in items]
    txt = read(os.path.join(PAPER, "highlights.tmpl.txt")).strip().split("\n")
    tm = read(os.path.join(SEC, "00_frontmatter.tmpl.tex"))
    mm = re.search(r"\\begin\{highlights\}(.*?)\\end\{highlights\}", tm, flags=re.S)
    titems = [s.strip() for s in re.split(r"\\item", mm.group(1)) if s.strip()]
    if titems != [s.strip() for s in txt]:
        sys.exit("highlights.tmpl.txt differs from the frontmatter highlights")
    write(os.path.join(PAPER, "highlights.txt"), "\n".join(items) + "\n")
    lens = [len(i) for i in items]
    print("highlights (chars):", lens)
    too_long = [n for n in lens if n > HIGHLIGHT_MAX]
    if len(items) < 3 or len(items) > 5:
        print("WARN  highlights: %d bullets (journal asks for 3 to 5)" % len(items))
    if too_long:
        print("WARN  highlights: %d bullet(s) longer than %d characters" % (len(too_long), HIGHLIGHT_MAX))
    return lens


def tex():
    def run(cmd):
        r = subprocess.run(cmd, cwd=PAPER, capture_output=True, text=True, errors="replace")
        print(" ".join(cmd[:1] + cmd[-1:]), "->", r.returncode)
        return r
    pl = ["pdflatex", "-interaction=nonstopmode", "-file-line-error"]
    ok = True
    steps = (pl + ["main.tex"], pl + ["supplement.tex"], ["bibtex", "main"],
             pl + ["main.tex"], pl + ["supplement.tex"], pl + ["main.tex"])
    for i, step in enumerate(steps):
        r = run(step)
        # the first passes may fail on a stale .aux or .bbl; only the last pdflatex run of each document decides
        if step[0] == "pdflatex" and i >= 4 and r.returncode != 0:
            ok = False
    return ok


def word_count():
    n = 0
    for name in WORD_COUNT_SECTIONS:
        t = read(os.path.join(SEC, name + ".tex"))       # unplaced: prose only, no floats
        t = re.sub(r"(?<!\\)%.*", "", t)
        t = re.sub(r"\\begin\{(equation|align|gather|multline|figure|table|algorithm)\*?\}.*?\\end\{\1\*?\}", " ", t, flags=re.S)
        t = re.sub(r"\$[^$]*\$", " ", t)
        t = re.sub(r"\\(?:cite\w*|ref|eqref|label|autoref|url)\{[^}]*\}", " ", t)
        t = re.sub(r"\\[A-Za-z]+\*?(?:\[[^\]]*\])?", " ", t)
        t = re.sub(r"[{}\\]", " ", t)
        n += len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'.,%-]*", t))
    return n


def report(n_placed, unref, hl_lens, tex_ok, fill_log):
    lines = []
    log = os.path.join(PAPER, "main.log")
    pages, undefined, errors, multi = "n/a", [], [], []
    if os.path.isfile(log):
        lg = read_log(log)
        mm = re.search(r"Output written on main\.pdf \((\d+) pages?", lg)
        pages = mm.group(1) if mm else "no PDF"
        undefined = sorted(set(re.findall(r"(?:Reference|Citation) `([^']+)' on page \d+ undefined", lg)))
        errors = re.findall(r"^(?:[^\n]*?:\d+: |! )[^\n]*", lg, flags=re.M)[:10]
        multi = sorted(set(re.findall(r"Label `([^']+)' multiply defined", lg)))
    supp_log = os.path.join(PAPER, "supplement.log")
    supp_pages = "n/a"
    if os.path.isfile(supp_log):
        mm = re.search(r"Output written on supplement\.pdf \((\d+) pages?", read_log(supp_log))
        supp_pages = mm.group(1) if mm else "no PDF"
    pend = 0
    used = 0
    lp = os.path.join(PAPER, "ledger_used.csv")
    if os.path.isfile(lp):
        with open(lp, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                used += 1
                pend += r["source_file_row"] == "PENDING"
    bib = os.path.join(PAPER, "references.bib")
    nbib = len(re.findall(r"^@\w+\s*\{", read(bib), flags=re.M)) if os.path.isfile(bib) else 0
    lines.append("main.pdf pages: %s (review, 3p layout); supplement.pdf pages: %s" % (pages, supp_pages))
    lines.append("body word count (Introduction to Conclusion, prose only, tex-stripped, approximate): %d" % word_count())
    lines.append("ledger placeholders used: %d, of which PENDING (red [pending key] boxes): %d" % (used, pend))
    lines.append("floats placed: %d; floats without a \\ref in their host section: %d %s" % (n_placed, len(unref), unref))
    lines.append("highlights (chars): %s" % hl_lens)
    lines.append("references.bib entries: %d" % nbib)
    lines.append("undefined references or citations: %d %s" % (len(undefined), undefined))
    lines.append("multiply defined labels: %d %s" % (len(multi), multi))
    lines.append("LaTeX errors (first 10): %d %s" % (len(errors), errors))
    lines.append("LaTeX run ok: %s" % tex_ok)
    txt = "\n".join(lines) + "\n"
    write(os.path.join(PAPER, "build_report.txt"), txt)
    print("\n=== build report ===\n" + txt)
    return tex_ok and not errors


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    fill_log = ""
    if "--no-fill" not in sys.argv:
        fill_log = fill("--strict-literals" in sys.argv)
    n_placed, unref = make_placed()
    hl = highlights()
    ok = True
    if "--no-tex" not in sys.argv:
        ok = tex()
        ok = report(n_placed, unref, hl, ok, fill_log)
    sys.exit(0 if ok else 1)
