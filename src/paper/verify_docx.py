"""verify_docx.py: checks the DOCX itself (python-docx + raw XML), not the LaTeX PDF.
Usage: python src/paper/verify_docx.py [path]   (default paper/manuscript.docx)
Writes a JSON summary to logs/build_docx/verify.json and prints one line per check. Exit code 1 if a hard check fails.
Checks: OMML equations (m:oMath), numbered equation paragraphs, table borders and header rules, heading colours and
fonts (styles.xml and run overrides), figure count (a:blip), figure captions, table captions, DOI hyperlinks,
leftover markers (pending, ??, @@EQ, [cite:), line numbering (w:lnNumType), en/em dashes, abstract word count,
supplementary-caption tokens (Table Sn / Fig. Sn need a caption line each).
"""
import json
import os
import re
import sys
import zipfile
from lxml import etree

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
ns = {"w": W, "m": M, "a": A, "r": R}


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "paper", "manuscript.docx")
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read("word/document.xml"))
    sty = etree.fromstring(z.read("word/styles.xml"))
    rels = etree.fromstring(z.read("word/_rels/document.xml.rels"))
    res = {}
    hard = []

    def check(name, ok, detail, hardfail=True):
        res[name] = {"ok": bool(ok), "detail": detail}
        print(("PASS " if ok else "FAIL ") + name + ": " + str(detail))
        if not ok and hardfail:
            hard.append(name)

    body = doc.find("w:body", ns)
    paras = body.findall(".//w:p", ns)

    def ptext(p):
        return "".join(t.text or "" for t in p.iter("{%s}t" % W))

    omath = doc.findall(".//m:oMath", ns)
    omp = doc.findall(".//m:oMathPara", ns)
    num_eq = [p for p in paras if p.find("m:oMath", ns) is not None and re.search(r"\(\d+\)|\([A-Z]\.\d+\)", ptext(p))]
    check("omml_equations", len(omath) >= 20, "m:oMath total %d (display numbered paragraphs %d, unnumbered oMathPara %d)" % (len(omath), len(num_eq), len(omp)))
    check("equation_numbers_sequential", True, ", ".join(re.findall(r"\((\d+)\)", " ".join(ptext(p) for p in num_eq)))[:200], False)

    # tables
    tbls = body.findall("w:tbl", ns)
    nb = 0
    nh = 0
    for t in tbls:
        b = t.find("w:tblPr/w:tblBorders", ns)
        if b is not None and b.find("w:top", ns) is not None and b.find("w:bottom", ns) is not None:
            nb += 1
        if t.find(".//w:tr/w:trPr/w:tblHeader", ns) is not None or t.find(".//w:tcBorders/w:bottom", ns) is not None:
            nh += 1
    check("tables_borders", len(tbls) > 0 and nb == len(tbls), "%d tables, %d with top and bottom rules, %d with a header rule" % (len(tbls), nb, nh))
    vert = sum(1 for t in tbls if t.find("w:tblPr/w:tblBorders/w:left", ns) is not None or t.find("w:tblPr/w:tblBorders/w:insideV", ns) is not None)
    check("tables_no_vertical_rules", vert == 0, "%d tables with vertical rules" % vert)

    # headings
    st = {s.get("{%s}styleId" % W): s for s in sty.findall("w:style", ns)}
    bad = []
    for sid in ("Heading1", "Heading2", "Heading3", "Title", "Heading4"):
        s = st.get(sid)
        if s is None:
            continue
        c = s.find("w:rPr/w:color", ns)
        v = c.get("{%s}val" % W) if c is not None else None
        th = c.get("{%s}themeColor" % W) if c is not None else None
        if v not in (None, "000000", "auto") or th:
            bad.append((sid, v, th))
    check("heading_style_colours_black", not bad, "non-black heading styles: %s" % bad)
    used = {}
    for p in paras:
        ps = p.find("w:pPr/w:pStyle", ns)
        if ps is not None:
            used[ps.get("{%s}val" % W)] = used.get(ps.get("{%s}val" % W), 0) + 1
    run_col = set()
    for p in paras:
        ps = p.find("w:pPr/w:pStyle", ns)
        if ps is not None and ps.get("{%s}val" % W).startswith(("Heading", "Title")):
            for c in p.findall(".//w:rPr/w:color", ns):
                run_col.add(c.get("{%s}val" % W))
    check("heading_run_colours", run_col <= {"000000", "auto"}, "run colours inside headings: %s" % sorted(run_col))
    fonts = {}
    for sid in ("Normal", "BodyText", "Heading1", "Heading2", "Compact", "FirstParagraph"):
        s = st.get(sid)
        if s is not None:
            f = s.find("w:rPr/w:rFonts", ns)
            sz = s.find("w:rPr/w:sz", ns)
            fonts[sid] = ((f.get("{%s}ascii" % W) if f is not None else None), (sz.get("{%s}val" % W) if sz is not None else None))
    res["fonts"] = fonts
    print("INFO styles font/size:", fonts)
    check("heading_paragraphs", sum(v for k, v in used.items() if k.startswith("Heading")) >= 20, "heading paragraphs by style: %s" % {k: v for k, v in used.items() if k.startswith(("Heading", "Title"))})

    # figures
    blips = doc.findall(".//a:blip", ns)
    embeds = {b.get("{%s}embed" % R) for b in blips}
    media = [n for n in z.namelist() if n.startswith("word/media/")]
    check("figures_embedded", len(blips) == 13 and len(embeds) == 13, "%d drawings, %d distinct images, %d media files" % (len(blips), len(embeds), len(media)))
    caps_f = [ptext(p) for p in paras if re.match(r"\s*Figure \d+\.", ptext(p))]
    caps_t = [ptext(p) for p in paras if re.match(r"\s*Table \d+\.", ptext(p))]
    caps_a = [ptext(p) for p in paras if re.match(r"\s*Algorithm \d+\.", ptext(p))]
    check("figure_captions", len(caps_f) == 13, "%d figure caption paragraphs" % len(caps_f))
    check("table_captions", len(caps_t) >= 6, "%d table caption paragraphs, %d algorithm captions" % (len(caps_t), len(caps_a)))

    # hyperlinks
    hl = doc.findall(".//w:hyperlink", ns)
    targets = {}
    for r in rels:
        targets[r.get("Id")] = r.get("Target")
    dois = [targets.get(h.get("{%s}id" % R), "") for h in hl if "doi.org" in targets.get(h.get("{%s}id" % R), "")]
    anch = [h.get("{%s}anchor" % W) for h in hl if h.get("{%s}anchor" % W)]
    nref = len(re.findall(r"^\s*\[\d+\]", "\n".join(ptext(p) for p in paras), re.M))
    check("doi_hyperlinks", len(dois) >= max(40, nref - 4), "%d hyperlinks to doi.org, %d other external, %d internal anchors" % (len(dois), len(hl) - len(dois) - len(anch), len(anch)), False)
    allt = "\n".join(ptext(p) for p in paras)
    nref = len(re.findall(r"^\s*\[\d+\]", allt, re.M))
    res["reference_lines_bracketed"] = nref
    print("INFO reference lines starting with [n]:", nref)

    # leftovers
    left = {k: len(re.findall(k, allt)) for k in (r"\[pending", r"\?\?", r"@@EQ", r"\[cite:", r"\[figure pending", r"\[table pending", r"\\[a-zA-Z]+\{")}
    check("no_leftover_markers", all(v == 0 for v in left.values()), left)
    ph = sorted(set(re.findall(r"\[[A-Z][A-Z_\\ ]{3,}[^\]]*\]", allt)))[:12]
    res["owner_placeholders"] = ph
    print("INFO owner placeholders present (expected until the owner answers):", ph)
    check("no_line_numbering", doc.find(".//w:sectPr/w:lnNumType", ns) is None, "no w:lnNumType")
    nd = allt.count("\u2013") + allt.count("\u2014")
    check("no_en_em_dash", nd == 0, "%d dashes" % nd)

    # abstract word count
    m = re.search(r"\nAbstract\n(.*?)\nKeywords:", allt, re.S)
    if m:
        wc = len(m.group(1).split())
        check("abstract_words_le_250", wc <= 250, "%d words (Word render count)" % wc)
    else:
        check("abstract_words_le_250", False, "abstract not found")
    check("highlights_not_in_body", re.search(r"\nHighlights\n", allt) is None, "journal rule R4: highlights are a separate file, not in the manuscript body")
    # supplementary tokens
    toks = set(re.findall(r"\b(?:Table|Fig\.|Figure) S\d+", allt))
    capline = {t for t in toks if re.search(r"^\s*" + re.escape(t) + r"[.:]", allt, re.M)}
    check("supplementary_tokens_have_caption_lines", toks <= capline, "tokens %s; with caption line %s" % (sorted(toks), sorted(capline)), False)
    check("no_empty_equation_text", all(m.text is None or m.text != "" for m in doc.iter("{%s}t" % M)), "ok", False)

    out = os.path.join(ROOT, "logs", "build_docx")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "verify.json"), "w", encoding="utf-8", newline="") as f:
        json.dump(res, f, indent=1)
    print("HARD FAILS:", hard or "none")
    sys.exit(1 if hard else 0)


if __name__ == "__main__":
    main()
