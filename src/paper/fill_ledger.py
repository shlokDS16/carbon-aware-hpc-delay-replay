#!/usr/bin/env python
r"""fill_ledger.py (paper A) - the only route by which numbers enter the manuscript.

Adapted from paper_B/src/paper/fill_ledger.py (Paper B working pipeline; helper, math-mode scanner, formatter and literal-scan code
copied from it, placeholder syntax, sources and engine rewritten for Paper A).

Reads *.tmpl.tex (and highlights, via build_paper.py), replaces <<key|fmt>> placeholders with values from Paper A's ledgers:
  tables/ledger_TEST.csv  ledger_TEST_nearlimit.csv  ledger_TEST_secondary.csv  ledger_DEV.csv  ledger_TEST_posthoc.csv
  tables/ledger_TEST_sens_*.csv   (each only when present; columns key,value,source)
A key present in more than one ledger is an error. Writes the filled .tex (same name without ".tmpl") and paper/ledger_used.csv.

Placeholder syntax (SINGLE LINE):   <<key|fmt>>     <<PENDING:key|fmt>>
  Paper A keys contain '|' (arm names such as lgbm|req), so the format is ALWAYS present and is split off the END with
  rsplit('|', 1): <<TEST.PM100.w.S12.saving.lgbm|req|pct1>> is key "TEST.PM100.w.S12.saving.lgbm|req" with format pct1.
  A missing key, a missing or unknown format, an empty value, or a non-numeric value with a numeric format is an ERROR listing file:line.
  <<PENDING:key|fmt>> renders as a red [pending key] box (\pendingkey) and is counted; if the key already exists in a ledger the fill
  reports a WARNING ("remove PENDING").
  fmts   : .Nf  fixed decimals          .Ng  significant digits (never exponent; integer-valued numbers print exactly)
           pctN value*100, N decimals, then \,\%        ppN  value*100, N decimals, then \,pp (percentage points)
           int  rounded, thousands separator {,}        sci  m \times 10^{k}
           p    p-value, 3 significant digits, below 0.001 -> <0.001      raw  string as is, LaTeX-escaped
  Minus rule : negative numbers are emitted as "-" when the placeholder sits in math mode and as "$-$" in text mode.
  Admission  : keys that start with "DEV." are development-year rows and are admitted only if listed in paper/ALLOW_DEV_KEYS.txt.
  Literals   : decimals (3.14), thousands groups (9{,}550) and percentages (12 \%) in template prose outside placeholders are reported
               unless listed in paper/ALLOW_LITERALS.txt (compared after removing spaces, ~, \ and braces); --strict makes them errors.

Usage:  python -I src/paper/fill_ledger.py [--strict] [--check-only] [files...]
Standard library only (csv module), so it works under python -I.
"""
import argparse
import csv
import glob
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LEDGER_FILES = ["ledger_TEST.csv", "ledger_TEST_nearlimit.csv", "ledger_TEST_secondary.csv", "ledger_DEV.csv",
                "ledger_TEST_posthoc.csv", "ledger_data.csv"]          # plus ledger_TEST_sens_*.csv (glob)
LEDGER_COLS = ["file", "line", "placeholder", "key", "fmt", "rendered", "source_file_row"]

PH_RE = re.compile(r"<<([^<>\n]+?)>>")

MATH_ENVS = {"equation", "align", "gather", "multline", "eqnarray", "displaymath",
             "math", "flalign", "alignat"}


class FillError(Exception):
    pass


# ----------------------------------------------------------------- helpers
def read_text(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()


def read_list(path, inline_comments):
    """Lines of an allow-list file; '#' lines are comments; absent file = empty."""
    out = set()
    if not path or not os.path.isfile(path):
        return out
    for ln in read_text(path).splitlines():
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        if inline_comments:
            s = re.split(r"\s+#", s, maxsplit=1)[0].strip()
        out.add(s)
    return out


def norm_literal(s):
    return re.sub(r"\\,|[\s~\\{}]", "", s)


def lineno(text, pos):
    return text.count("\n", 0, pos) + 1


# ------------------------------------------------------------ math / comments
def scan_modes(text):
    """Return (math, comment) bytearrays: 1 where position is in math / a % comment."""
    n = len(text)
    math_ = bytearray(n)
    comm = bytearray(n)
    i = 0
    dollar = False       # inside $...$
    ddollar = False      # inside $$...$$
    paren = False        # \( ... \)
    brack = False        # \[ ... \]
    env_depth = 0
    envre = re.compile(r"\\(begin|end)\{([A-Za-z]+)\*?\}")
    while i < n:
        c = text[i]
        in_math = dollar or ddollar or paren or brack or env_depth > 0
        if c == "%":
            j = text.find("\n", i)
            j = n if j < 0 else j
            for k in range(i, j):
                comm[k] = 1
            i = j
            continue
        if c == "\\":
            nxt = text[i + 1] if i + 1 < n else ""
            if nxt == "(":
                paren = True
                i += 2
                continue
            if nxt == ")":
                paren = False
                i += 2
                continue
            if nxt == "[":
                brack = True
                i += 2
                continue
            if nxt == "]":
                brack = False
                i += 2
                continue
            m = envre.match(text, i)
            if m:
                if m.group(2) in MATH_ENVS:
                    env_depth += 1 if m.group(1) == "begin" else -1
                    env_depth = max(env_depth, 0)
                for k in range(i, m.end()):
                    math_[k] = 1 if (env_depth > 0 or in_math) else 0
                i = m.end()
                continue
            # any other escape (\\ \$ \% \&): consume two chars
            if in_math:
                math_[i] = 1
                if i + 1 < n:
                    math_[i + 1] = 1
            i += 2
            continue
        if c == "$":
            if text.startswith("$$", i):
                ddollar = not ddollar
                i += 2
                continue
            dollar = not dollar
            i += 1
            continue
        if in_math:
            math_[i] = 1
        i += 1
    return math_, comm



# ----------------------------------------------------------------- sources
class Source:
    def __init__(self):
        self.rows = {}      # key -> dict(row..., _loc=...)
        self.errors = []


def ledger_paths(tables_dir):
    paths = [os.path.join(tables_dir, n) for n in LEDGER_FILES]
    paths += sorted(glob.glob(os.path.join(tables_dir, "ledger_TEST_sens_*.csv")))
    # post-hoc extensions (armsync: Figure 6 whiskers; impact: B1-B4), added by the controller 2026-11-12
    paths += sorted(glob.glob(os.path.join(tables_dir, "ledger_TEST_posthoc_*.csv")))
    return paths


def load_sources(paths, rel_to, optional_missing=True):
    """Missing ledger files are skipped silently (posthoc and sens_* appear over time) and listed in src.missing."""
    src = Source()
    src.missing = []
    src.loaded = []
    src.dups_same = 0
    for path in paths:
        rel = os.path.relpath(path, rel_to).replace("\\", "/")
        if not os.path.isfile(path):
            src.missing.append(rel)
            continue
        src.loaded.append(rel)
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            rd = csv.reader(f)
            try:
                header = next(rd)
            except StopIteration:
                src.errors.append("%s:1: empty ledger file" % rel)
                continue
            header = [h.strip() for h in header]
            if "key" not in header or "value" not in header:
                src.errors.append("%s:1: header lacks key/value columns" % rel)
                continue
            prev_end = rd.line_num
            for r in rd:
                start = prev_end + 1
                prev_end = rd.line_num
                if not r or all(not c.strip() for c in r):
                    continue
                row = {h: (r[i] if i < len(r) else "") for i, h in enumerate(header)}
                key = row["key"].strip()
                if not key:
                    src.errors.append("%s:%d: row with empty key" % (rel, start))
                    continue
                row["_loc"] = "%s:%d" % (rel, start)
                if key in src.rows:
                    # a repeated key is tolerated only when the value is the same (ledger_TEST_secondary.csv repeats 72 keys of
                    # ledger_TEST.csv and of itself with equal values); a differing value is an error
                    old = src.rows[key]
                    a, b = to_float(old["value"]), to_float(row["value"])
                    same = (abs(a - b) <= 1e-9 * max(1.0, abs(a))) if (a is not None and b is not None)                         else old["value"].strip() == row["value"].strip()
                    if same:
                        src.dups_same += 1
                    else:
                        src.errors.append("%s: duplicate key '%s' with a different value (first at %s)"
                                          % (row["_loc"], key, old["_loc"]))
                    continue
                src.rows[key] = row
    return src


# ------------------------------------------------------------------ format
def to_float(s):
    try:
        v = float(s.strip())
    except (ValueError, AttributeError):
        return None
    if math.isnan(v) or math.isinf(v):
        return None
    return v


def minus(in_math):
    return "-" if in_math else "$-$"


def sig_str(x, nsig):
    """x to nsig significant digits, never exponent; integer-valued stays exact."""
    if x == int(x) and abs(x) >= 10 ** nsig:
        return str(int(x))
    s = format(x, ".%dg" % nsig)
    if "e" in s or "E" in s:
        from decimal import Decimal
        s = format(Decimal(s), "f")
    return s


def signed(body_abs, neg, in_math):
    """Prefix a minus (LaTeX-aware) unless the rendered magnitude is zero."""
    if neg and re.search(r"[1-9]", body_abs):
        return minus(in_math) + body_abs
    return body_abs


def latex_escape(s):
    out = []
    for ch in s:
        if ch == "\\":
            out.append(r"\textbackslash{}")
        elif ch in "&%$#_{}":
            out.append("\\" + ch)
        elif ch == "~":
            out.append(r"\textasciitilde{}")
        elif ch == "^":
            out.append(r"\textasciicircum{}")
        else:
            out.append(ch)
    return "".join(out)


FMT_RE = re.compile(r"^(?:\.(\d+)([fg])|pct(\d+)|int|sci|p|raw)$")



FMT_RE = re.compile(r"^(?:\.(\d+)([fg])|pct(\d+)|pp(\d+)|int|sci|p|raw)$")


def split_key_fmt(content):
    """'key|fmt' -> (key, fmt) splitting at the LAST '|' (keys such as lgbm|req contain '|'); fmt None if absent or invalid."""
    if "|" not in content:
        return content.strip(), None
    key, fmt = content.rsplit("|", 1)
    key, fmt = key.strip(), fmt.strip()
    if not FMT_RE.match(fmt):
        return content.strip(), None     # the last segment is not a format, so the whole text is the key
    return key, fmt


def render(raw, fmt, in_math):
    """Render the raw CSV string; raises FillError on problems."""
    m = FMT_RE.match(fmt)
    if not m:
        raise FillError("unknown fmt '%s'" % fmt)
    if fmt == "raw":
        return latex_escape(raw), fmt
    x = to_float(raw)
    if x is None:
        raise FillError("non-numeric value '%s' with numeric fmt '%s'" % (raw, fmt))
    neg = x < 0
    ax = abs(x)
    if m.group(2) == "f":
        body = format(ax, ".%df" % int(m.group(1)))
        return signed(body, neg, in_math), fmt
    if m.group(2) == "g":
        nsig = max(int(m.group(1)), 1)
        return signed(sig_str(ax, nsig), neg, in_math), fmt
    if m.group(3) is not None:
        body = format(ax * 100.0, ".%df" % int(m.group(3))) + r"\,\%"
        return signed(body, neg, in_math), fmt
    if m.group(4) is not None:
        body = format(ax * 100.0, ".%df" % int(m.group(4))) + r"\,pp"
        return signed(body, neg, in_math), fmt
    if fmt == "int":
        body = format(int(round(ax)), ",").replace(",", "{,}")
        return signed(body, neg, in_math), fmt
    if fmt == "sci":
        if x == 0:
            return "0", fmt
        mant, exp = ("%.1e" % ax).split("e")
        body = r"%s\times 10^{%d}" % (mant, int(exp))
        if neg:
            body = "-" + body
        return (body if in_math else "$" + body + "$"), fmt
    if fmt == "p":
        if x < 0 or x > 1:
            raise FillError("p-value %s outside [0,1]" % raw)
        if x < 0.001:
            return ("<0.001" if in_math else "$<$0.001"), fmt
        return sig_str(x, 3), fmt
    raise FillError("unhandled fmt '%s'" % fmt)


# ---------------------------------------------------------- literal scanning
SKIP_ARG_CMDS = (r"label|ref|eqref|pageref|autoref|cref|Cref|nameref|cite\w*|"
                 r"includegraphics|input|include|url|href|vspace|hspace|setlength|"
                 r"addtolength|rule|usepackage|documentclass|bibliographystyle|"
                 r"bibliography|geometry|setcounter|numberwithin|renewcommand|"
                 r"newcommand|providecommand|def|hypersetup|captionsetup")
SKIP_ARG_RE = re.compile(
    r"\\(?:%s)\*?(?:\s*\[[^\]]*\])*\s*\{[^{}]*\}(?:\s*\{[^{}]*\})?" % SKIP_ARG_CMDS)
OPTION_RE = re.compile(r"\[[^\]\n]*=[^\]\n]*\]")
UNIT_RE = re.compile(
    r"\d+(?:\.\d+)?\s*(?:pt|cm|mm|em|ex|in|bp|sp|dd|cc|pc|\\(?:text|line|column|paper)"
    r"(?:width|height)|\\(?:hsize|vsize|baselineskip|parindent))")
LITERAL_RE = re.compile(
    r"(?<![\w.\\])(?:\d+\.\d+|\d{1,3}(?:\{,\}\d{3})+)(?:\s*(?:\\,|~)?\s*\\%)?(?![\w])"
    r"|(?<![\w.\\])\d+(?:\s*(?:\\,|~)?\s*\\%)")


def find_literals(text, comm, ph_spans, allow):
    """Yield (pos, literal) for result-like numbers in prose."""
    n = len(text)
    mask = bytearray(n)

    def cover(a, b):
        for k in range(a, b):
            mask[k] = 1

    for k in range(n):
        if comm[k]:
            mask[k] = 1
    for a, b in ph_spans:
        cover(a, b)
    for rx in (SKIP_ARG_RE, OPTION_RE, UNIT_RE):
        for m in rx.finditer(text):
            cover(m.start(), m.end())
    out = []
    for m in LITERAL_RE.finditer(text):
        if mask[m.start()]:
            continue
        lit = m.group(0)
        if norm_literal(lit) in allow:
            continue
        out.append((m.start(), lit))
    return out



# ------------------------------------------------------------------- engine
PENDING_RENDER = r"\pendingkey{}"


def fill_text(text, relname, src, allow_dev, allow_lit, errors, warnings, ledger):
    math_, comm = scan_modes(text)
    spans = []
    pieces = []
    last = 0
    for m in PH_RE.finditer(text):
        a, b = m.span()
        if comm[a]:
            continue
        spans.append((a, b))
        content = m.group(1).strip()
        pending = content.startswith("PENDING:")
        if pending:
            content = content[len("PENDING:"):].strip()
        key, fmt = split_key_fmt(content)
        ln = lineno(text, a)
        where = "%s:%d: %s" % (relname, ln, m.group(0))
        pieces.append(text[last:a])
        last = b
        try:
            if fmt is None:
                raise FillError("format missing or unknown (every placeholder needs <<key|fmt>>; fmts: .Nf .Ng pctN ppN int sci p raw; "
                                "got '%s')" % content)
            row = src.rows.get(key)
            if pending:
                if row is not None:
                    warnings.append("%s: key '%s' now exists in %s: remove PENDING" % (where, key, row["_loc"]))
                pieces.append(PENDING_RENDER)
                ledger.append({"file": relname, "line": ln, "placeholder": m.group(0), "key": key, "fmt": fmt,
                               "rendered": "[pending key]", "source_file_row": "PENDING"})
                continue
            if row is None:
                raise FillError("key '%s' not found in any ledger" % key)
            if key.startswith("DEV.") and key not in allow_dev:
                raise FillError("key '%s' is a development-year row (%s) and is not in ALLOW_DEV_KEYS.txt" % (key, row["_loc"]))
            raw = row.get("value", "")
            if raw is None or raw.strip() == "":
                raise FillError("value empty for key '%s' (%s)" % (key, row["_loc"]))
            rendered, used_fmt = render(raw, fmt, bool(math_[a]))
        except FillError as e:
            errors.append("%s -> %s" % (where, e))
            pieces.append(m.group(0))
            continue
        pieces.append(rendered)
        ledger.append({"file": relname, "line": ln, "placeholder": m.group(0), "key": key, "fmt": used_fmt,
                       "rendered": rendered, "source_file_row": row["_loc"]})
    pieces.append(text[last:])
    for pos, lit in find_literals(text, comm, spans, allow_lit):
        warnings.append("%s:%d: literal-number warning: '%s' outside a placeholder"
                        % (relname, lineno(text, pos), lit))
    return "".join(pieces)


def out_path_for(tmpl):
    d, base = os.path.split(tmpl)
    if ".tmpl." not in base:
        raise FillError("%s: input must contain .tmpl. in its name (x.tmpl.tex -> x.tex)" % tmpl)
    return os.path.join(d, base.replace(".tmpl.", ".", 1))


def run(files, root, strict=False, check_only=False, out=sys.stdout, err=sys.stderr):
    tables_dir = os.path.join(root, "tables")
    allow_dev = read_list(os.path.join(root, "paper", "ALLOW_DEV_KEYS.txt"), True)
    allow_lit = {norm_literal(s) for s in read_list(os.path.join(root, "paper", "ALLOW_LITERALS.txt"), False)}
    ledger_out = os.path.join(root, "paper", "ledger_used.csv")
    if not files:
        files = sorted(glob.glob(os.path.join(root, "paper", "sections", "*.tmpl.tex")))
    src = load_sources(ledger_paths(tables_dir), root)
    errors = list(src.errors)
    warnings = []
    literal_warnings = []
    ledger = []
    outputs = []
    for f in files:
        explicit = None
        if "::" in f:                      # SRC::DEST: fill SRC (no .tmpl. in its name) into DEST
            f, explicit = f.split("::", 1)
            explicit = os.path.abspath(explicit)
        f = os.path.abspath(f)
        try:
            dest = explicit or out_path_for(f)
            text = read_text(f)
        except (FillError, OSError) as e:
            errors.append(str(e))
            continue
        rel = os.path.relpath(f, root).replace("\\", "/")
        w = []
        filled = fill_text(text, rel, src, allow_dev, allow_lit, errors, w, ledger)
        for x in w:
            (literal_warnings if "literal-number warning" in x else warnings).append(x)
        outputs.append((dest, filled))
    for w in warnings:
        print("WARN  " + w, file=err)
    for w in literal_warnings:
        print(("ERROR " if strict else "WARN  ") + w, file=err)
    if strict and literal_warnings:
        errors.append("%d literal-number warning(s) treated as errors (--strict)" % len(literal_warnings))
    for e in errors:
        print("ERROR " + e, file=err)
    n_pending = sum(1 for r in ledger if r["source_file_row"] == "PENDING")
    if errors:
        print("fill_ledger: FAILED (%d error(s), %d warning(s)); nothing written" % (len(errors), len(warnings) + len(literal_warnings)),
              file=out)
        return 1
    if not check_only:
        for dest, filled in outputs:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf-8", newline="") as fh:
                fh.write(filled)
        with open(ledger_out, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=LEDGER_COLS, lineterminator="\n")
            w.writeheader()
            w.writerows(ledger)
    print("fill_ledger: OK (%d file(s), %d placeholder(s) of which %d PENDING, %d warning(s), %d literal warning(s); ledgers loaded: %s; absent: %s; repeated keys with equal values tolerated: %d)%s"
          % (len(outputs), len(ledger), n_pending, len(warnings), len(literal_warnings),
             ", ".join(src.loaded) or "none", ", ".join(src.missing) or "none", src.dups_same, " [check-only]" if check_only else ""), file=out)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="*", help="*.tmpl.* files (default paper/sections/*.tmpl.tex)")
    ap.add_argument("--strict", action="store_true", help="literal-number warnings are errors")
    ap.add_argument("--check-only", action="store_true", help="validate, write nothing")
    ap.add_argument("--root", default=ROOT, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    return run(a.files, a.root, a.strict, a.check_only)


if __name__ == "__main__":
    sys.exit(main())
