"""build_bib.py (paper A): write paper/references.bib from the verified reference tables, fetching every entry from its source.

Inputs : research/journal/A15_REFERENCES.csv and A20_REFERENCES_ADD.csv (rows with verified_crossref starting "yes"; a DOI is required),
         plus the extra entries listed in EXTRA below (each fetched or opened and checked here, never written from memory).
Source : https://doi.org/<doi> with "Accept: application/x-bibtex" (Crossref and DataCite content negotiation); web-page entries are
         opened with HTTP GET and the page title is compared with the title in EXTRA; the access date is the date of the fetch.
Output : paper/references.bib (keys = the CSV key column, DOI and url kept, url set to https://doi.org/<doi>; claim and section ties in
         the annote field, which BibTeX styles do not print), paper/bib_fetch_log.csv (one row per entry: key, source, http status,
         title check) and paper/bib_cache/<key>.txt (raw response).
Network: Crossref, doi.org, DataCite via doi.org and the named official pages only; on HTTP 429 it waits and retries.
Usage  : py -I src/paper/build_bib.py [--refresh]      (cached responses are reused unless --refresh)
"""
import csv
import datetime
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAPER = os.path.join(ROOT, "paper")
CACHE = os.path.join(PAPER, "bib_cache")
JOURNAL = os.path.join(ROOT, "research", "journal")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bibtex_ascii import texify, protect_caps  # noqa: E402

UA = "paperA-bibtool/1.0"
TODAY = datetime.date.today().isoformat()

# (key, type, doi or None, url, expected title words, extra fields, claim/section tie)
EXTRA = [
    dict(key="eia930_about", kind="web", url="https://www.eia.gov/electricity/930-content/about.html",
         title_has="EIA-930", author="{U.S. Energy Information Administration}",
         title="About the {EIA-930} data (Hourly Electric Grid Monitor)", year="",
         tie="EIA-930 schedule, revisions and data quality (A20_LIT_LICENCE s3); Data 3.1"),
    dict(key="eia930_instructions", kind="web", url="https://www.eia.gov/survey/form/eia_930/instructions.pdf",
         title_has=None, author="{U.S. Energy Information Administration}",
         title="{EIA-930} Hourly and Daily Balancing Authority Operations Report: Data Filing Instructions", year="",
         tie="EIA-930 reporting deadlines and revision rules (A20_LIT_LICENCE s3); Data 3.1"),
    dict(key="ke2017lightgbm", kind="web",
         url="https://proceedings.neurips.cc/paper_files/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html",
         title_has="LightGBM", author="Ke, Guolin and Meng, Qi and Finley, Thomas and Wang, Taifeng and Chen, Wei and Ma, Weidong and Ye, Qiwei and Liu, Tie-Yan",
         title="{LightGBM}: A Highly Efficient Gradient Boosting Decision Tree", year="2017", booktitle="Advances in Neural Information Processing Systems 30",
         tie="forecaster used for the past-only signal; Method 4.3"),
    dict(key="holm1979", kind="crossref_search", title="A Simple Sequentially Rejective Multiple Test Procedure", author="Holm", year="1979", tie="Holm correction of H1-H3; Method 4.7"),
    dict(key="pm100_dataset", kind="doi", doi="10.5281/zenodo.10127767", tie="PM100 job-trace dataset (Zenodo); Data 3.2"),
    dict(key="fdata_dataset", kind="doi", doi="10.5281/zenodo.11467483", tie="F-DATA job-trace dataset (Zenodo, A04 s(b)); Data 3.2"),
    dict(key="electricitymaps_method", kind="web", url="https://www.electricitymaps.com/methodology", title_has="Methodology",
         author="{Electricity Maps}", title="Electricity Maps methodology", year="",
         tie="commercial carbon-intensity provider methodology; cite only if Introduction or Data 3.1 needs it"),
    dict(key="ghg_scope2", kind="web", url="https://ghgprotocol.org/scope_2_guidance", title_has="Scope 2",
         author="{Greenhouse Gas Protocol}", title="{GHG} Protocol Scope 2 Guidance: An amendment to the {GHG} Protocol Corporate Standard", year="2015",
         tie="location-based accounting convention; Method 4.6 and Discussion 6.4"),
]


def http(url, accept=None, tries=6):
    delay = 5
    for n in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA, **({"Accept": accept} if accept else {})})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, r.read().decode("utf-8", errors="replace"), r.geturl()
        except urllib.error.HTTPError as e:
            if e.code == 429 and n < tries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            return e.code, "", url
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if n < tries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            return 0, str(e), url
    return 0, "", url


def cached(key, fetch, refresh):
    p = os.path.join(CACHE, key + ".txt")
    if os.path.isfile(p) and not refresh:
        with open(p, encoding="utf-8", newline="") as f:
            body = f.read()
        st, _, rest = body.partition("\n")
        return int(st), rest
    st, text, _ = fetch()
    os.makedirs(CACHE, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write("%d\n%s" % (st, text))
    return st, text


def words(s):
    s = re.sub(r"\{\\[^}]*\}|\\.|[{}$]", "", s.lower())
    return set(re.findall(r"[a-z0-9]{3,}", s))


def parse_bib(bib):
    """Brace-aware parse of one BibTeX entry (Crossref returns it on one line): (type, key, [(name, value)])."""
    m = re.match(r"\s*@(\w+)\s*\{\s*([^,\s]*)\s*,", bib)
    if not m:
        raise ValueError("not a BibTeX entry")
    i, n, fields = m.end(), len(bib), []
    while i < n:
        mm = re.compile(r"[\s,]*([A-Za-z][\w-]*)\s*=\s*").match(bib, i)
        if not mm:
            break
        name, i = mm.group(1), mm.end()
        if i < n and bib[i] == "{":
            depth, j = 0, i
            while j < n:
                depth += bib[j] == "{"
                depth -= bib[j] == "}"
                j += 1
                if depth == 0:
                    break
            val, i = bib[i + 1:j - 1], j
        elif i < n and bib[i] == '"':
            j = bib.index('"', i + 1)
            val, i = bib[i + 1:j], j + 1
        else:
            mv = re.compile(r"[^,}\s]+").match(bib, i)
            val, i = mv.group(0), mv.end()
        fields.append((name, val))
    return m.group(1), m.group(2), fields


def field(bib, name):
    for k, v in parse_bib(bib)[2]:
        if k.lower() == name.lower():
            return v
    return None


def normalise(bib, key, doi, tie, title_fallback=None):
    typ, _, fields = parse_bib(bib)
    fields = [(k, protect_caps(texify(v)) if k.lower() == "title" else (v if k.lower() in ("month",) else texify(v))) for k, v in fields]
    out = [(k, v) for k, v in fields if k.lower() not in ("url", "doi", "annote", "series", "collection", "publisher_url")]
    if title_fallback and not any(k.lower() == "title" for k, _ in out):
        out.insert(0, ("title", title_fallback))
    out.append(("doi", doi))
    # T13 (A34): the DOI prints once. The url field is dropped when it only repeats https://doi.org/<doi>; the bibliography style
    # prints both fields, so keeping the url duplicated the DOI in the reference list.
    pub = " ".join(v for k, v in out if k.lower() == "publisher").lower()
    if re.search(r"arxiv|ssrn|researchsquare|preprints", pub) or doi.lower().startswith(("10.48550/", "10.2139/", "10.21203/")):
        out.append(("note", "Preprint, not peer reviewed"))      # journal rule R9: preprints are marked
    if key.endswith("_dataset") or doi.lower().startswith("10.5281/zenodo"):
        out = [(k, ("[dataset] " + v) if k.lower() == "title" else v) for k, v in out]   # journal rule R9: dataset references
    if tie:
        out.append(("annote", tie.replace("{", "(").replace("}", ")").replace("%", " percent")))
    body = ",\n".join("  %s = %s" % (k, v if k.lower() == "month" and re.fullmatch(r"[A-Za-z]+", v) else "{%s}" % v) for k, v in out)
    return "@%s{%s,\n%s\n}\n" % (typ, key, body)


def cited_keys():
    keys = {}
    for fn in sorted(os.listdir(os.path.join(PAPER, "sections"))):
        if fn.endswith(".tmpl.tex"):
            with open(os.path.join(PAPER, "sections", fn), encoding="utf-8") as f:
                for m in re.finditer(r"\\(?:cite\w*)\*?(?:\[[^\]]*\])*\{([^}]*)\}", f.read()):
                    for k in m.group(1).split(","):
                        keys.setdefault(k.strip(), set()).add(fn.split("_")[0])
    return keys


def write_map(entries, unverified):
    rows = {}
    for fn in ("A15_REFERENCES.csv", "A20_REFERENCES_ADD.csv"):
        with open(os.path.join(JOURNAL, fn), encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                rows.setdefault(r["key"].strip(), (r["claim"].strip(), r["paper_A_section"].strip(), r["status"].strip()))
    for e in EXTRA:
        rows.setdefault(e["key"], (e["tie"], "see claim", "added by A23"))
    cites = cited_keys()
    L = ["# REFERENCES_MAP.md (Paper A; generated by src/paper/build_bib.py on %s; do not edit by hand)" % TODAY, "",
         "%d entries in `paper/references.bib`. Claim and section come from the `claim` and `paper_A_section` columns of "
         "`research/journal/A15_REFERENCES.csv` and `A20_REFERENCES_ADD.csv` (EXTRA entries: from the tie written in `build_bib.py`). "
         "`cited in` lists the section templates that cite the key today (00 = front matter ... 08 = declarations); `-` = not cited yet." % len(entries), "",
         "| key | claim | planned section | status | cited in |", "|---|---|---|---|---|"]
    for k in sorted(entries):
        c, s, st = rows.get(k, ("", "", ""))
        L.append("| %s | %s | %s | %s | %s |" % (k, c.replace("|", "/"), s.replace("|", "/"), st, ", ".join(sorted(cites.get(k, []))) or "-"))
    missing = sorted(k for k in cites if k not in entries)
    L += ["", "## Cited in the templates but not in references.bib", ""] + (["- `%s` (cited in %s)" % (k, ", ".join(sorted(cites[k]))) for k in missing] or ["none"])
    L += ["", "## Left out (not verified)", ""] + ["- `%s`: %s" % (u[1], u[2]) for u in unverified]
    with open(os.path.join(PAPER, "REFERENCES_MAP.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")


def main(refresh):
    log = []
    entries = {}
    seen_dois = {}
    unverified = []
    # 1. CSV rows
    for fn in ("A15_REFERENCES.csv", "A20_REFERENCES_ADD.csv"):
        with open(os.path.join(JOURNAL, fn), encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                key, doi = r["key"].strip(), r["doi"].strip()
                if doi.startswith("http") and any(e["key"] == key for e in EXTRA):
                    log.append([key, fn, "skip", "web page; entry built from the opened page (EXTRA)"])
                    continue
                ok = r["verified_crossref"].strip().lower().startswith("yes") and doi and not doi.startswith("http")
                if not ok:
                    unverified.append((fn, key, "verified_crossref=%r doi=%r" % (r["verified_crossref"][:30], doi[:40])))
                    continue
                if key in entries:
                    log.append([key, fn, "skip", "duplicate key (kept the first)"])
                    continue
                if doi.lower() in seen_dois:
                    log.append([key, fn, "skip", "same DOI as %s (kept that key)" % seen_dois[doi.lower()]])
                    continue
                st, text = cached(key, lambda d=doi: http("https://doi.org/" + d, "application/x-bibtex"), refresh)
                if st != 200 or not text.strip().startswith("@"):
                    unverified.append((fn, key, "doi.org returned %s" % st))
                    log.append([key, fn, st, "NOT FETCHED"])
                    continue
                t_csv = words(r["title"])
                t_got = words(field(text, "title") or "")
                inter = len(t_csv & t_got) / max(1, min(len(t_csv), len(t_got)))
                tie = "%s | %s" % (r["claim"].strip(), r["paper_A_section"].strip())
                entries[key] = normalise(text, key, doi, tie, r["title"].strip())
                seen_dois[doi.lower()] = key
                log.append([key, fn, st, ("title overlap %.2f%s%s" % (inter, "" if field(text, "title") else " (Crossref record has no title: taken from the CSV; no author in the record)", "" if inter >= 0.6 else " LOW: check by eye"))])
                time.sleep(0.3)
    # 2. extras
    for e in EXTRA:
        key = e["key"]
        if e["kind"] == "doi":
            if e["doi"].lower() in seen_dois:
                log.append([key, "EXTRA", "skip", "same DOI as %s" % seen_dois[e["doi"].lower()]])
                continue
            st, text = cached(key, lambda d=e["doi"]: http("https://doi.org/" + d, "application/x-bibtex"), refresh)
            if st != 200 or not text.strip().startswith("@"):
                unverified.append(("EXTRA", key, "doi.org returned %s" % st))
                continue
            entries[key] = normalise(text, key, e["doi"], e["tie"])
            log.append([key, "EXTRA", st, "title: %s" % (field(text, "title") or "")[:70]])
        elif e["kind"] == "crossref_search":
            url = ("https://api.crossref.org/works?rows=5&query.title=" + urllib.request.quote(e["title"])
                   + "&query.author=" + urllib.request.quote(e["author"]) + "&filter=from-pub-date:%s,until-pub-date:%s" % (e["year"], e["year"]))
            st, text = cached(key + "_search", lambda u=url: http(u), refresh)
            hit = None
            try:
                for it in json.loads(text)["message"]["items"]:
                    if words(" ".join(it.get("title", []))) == words(e["title"]):
                        hit = it["DOI"]
                        break
            except (ValueError, KeyError):
                pass
            if not hit:
                unverified.append(("EXTRA", key, "no Crossref record with the exact title '%s' (%s); the paper has no Crossref DOI" % (e["title"], e["year"])))
                continue
            st2, bib = cached(key, lambda d=hit: http("https://doi.org/" + d, "application/x-bibtex"), refresh)
            if st2 != 200 or not bib.strip().startswith("@"):
                unverified.append(("EXTRA", key, "doi.org returned %s for %s" % (st2, hit)))
                continue
            entries[key] = normalise(bib, key, hit, e["tie"])
            log.append([key, "EXTRA", st2, "Crossref exact-title match -> %s" % hit])
        else:  # web page
            st, text = cached(key, lambda u=e["url"]: http(u), refresh)
            if st != 200:
                unverified.append(("EXTRA", key, "GET %s returned %s" % (e["url"], st)))
                continue
            tm = re.search(r"<title>(.*?)</title>", text, flags=re.S | re.I)
            page_title = html.unescape(re.sub(r"\s+", " ", tm.group(1))).strip() if tm else ""
            has = e.get("title_has")
            if has and has.lower() not in (page_title + " " + text[:5000]).lower():
                unverified.append(("EXTRA", key, "page text lacks %r (title %r)" % (has, page_title[:60])))
                continue
            typ = "inproceedings" if e.get("booktitle") else "misc"
            lines = ["@%s{%s," % (typ, key), "  author = {%s}," % e["author"], "  title = {%s}," % e["title"]]
            if e.get("booktitle"):
                lines.append("  booktitle = {%s}," % e["booktitle"])
            if e.get("year"):
                lines.append("  year = {%s}," % e["year"])
            lines.append("  url = {%s}," % e["url"])
            lines.append("  note = {Accessed %s}," % TODAY if typ == "misc" else "  note = {Accessed %s}," % TODAY)
            lines.append("  annote = {%s}" % e["tie"])
            entries[key] = "\n".join(lines) + "\n}\n"
            log.append([key, "EXTRA", st, "page title: %s" % page_title[:70]])
    # write
    with open(os.path.join(PAPER, "references.bib"), "w", encoding="utf-8", newline="\n") as f:
        f.write("%% references.bib: generated by src/paper/build_bib.py on %s. Do not edit by hand; re-run the script.\n"
                "%% Entries come from doi.org content negotiation (Crossref, DataCite) or from the opened web page; keys are the CSV keys.\n\n" % TODAY)
        for k in sorted(entries):
            f.write(entries[k] + "\n")
    with open(os.path.join(PAPER, "bib_fetch_log.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["key", "source", "http_status", "check"])
        w.writerows(log)
        for u in unverified:
            w.writerow([u[1], u[0], "UNVERIFIED", u[2]])
    write_map(entries, unverified)
    print("%d entries written; %d left out" % (len(entries), len(unverified)))
    for u in unverified:
        print("  left out:", u)
    return 0


if __name__ == "__main__":
    sys.exit(main("--refresh" in sys.argv))
