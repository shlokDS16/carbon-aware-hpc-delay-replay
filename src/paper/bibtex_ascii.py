"""bibtex_ascii.py (paper A): make fetched BibTeX text ASCII-safe for bibtex (accents as LaTeX commands, entities and ampersands escaped)."""
import html
import re
import unicodedata

ACCENT = {"̀": "`", "́": "'", "̂": "^", "̃": "~", "̈": '"', "̄": "=", "̇": ".",
          "̆": "u", "̌": "v", "̧": "c", "̨": "k", "̊": "r", "̋": "H"}
SPECIAL = {"’": "'", "‘": "`", "“": "``", "”": "''", "–": "--", "—": "---", "−": "-",
           "ß": r"{\ss}", "ø": r"{\o}", "Ø": r"{\O}", "ł": r"{\l}", "Ł": r"{\L}", "æ": r"{\ae}",
           " ": " ", " ": " ", "­": "", "ı": r"{\i}", "′": "'", "‐": "-", "‑": "-"}


def texify(s):
    s = html.unescape(s)
    out = []
    for ch in unicodedata.normalize("NFD", s):
        if ch in SPECIAL:
            out.append(SPECIAL[ch])
        elif ch in ACCENT and out:
            base = out.pop()
            cmd = ACCENT[ch]
            out.append("{\\%s%s}" % (cmd, base) if not cmd.isalpha() else "{\\%s %s}" % (cmd, base))
        elif ord(ch) < 128:
            out.append(ch)
        else:
            out.append("?")
    return re.sub(r"(?<!\\)&", r"\\&", "".join(out))


def protect_caps(title):
    """Brace acronyms and U.S.-style tokens in a title so the bibliography style keeps their capitals."""
    title = re.sub(r"(?<![{\w\\])((?:[A-Z]\.){2,}|[A-Z]{2,}[A-Za-z0-9-]*)(?![\w}])", r"{\1}", title)
    # production review 2026-11-12: CamelCase system names (LiteCast, ReBase, CarbonScaler) and proper nouns that
    # elsarticle-num would lowercase; references.bib was patched by hand the same way
    title = re.sub(r"(?<![{\w\\])([A-Z][a-z]+[A-Z][A-Za-z0-9]*)(?![\w}])", r"{\1}", title)
    for noun in ("Fugaku", "Shapley", "Sobol'", "European"):
        title = re.sub(r"(?<![{\w\\])(%s)(?![\w}])" % re.escape(noun), r"{\1}", title)
    return title
