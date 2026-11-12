"""Post-process a pandoc docx: numbered native equations, ruled tables, column alignment, table font size,
typographic apostrophes, dash sanitising. Returns a small stats dict."""
import copy
import json
import re
import shutil
import zipfile
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
NS = {"w": W, "m": M}
TEXTW = 9026


def q(tag):
    p, t = tag.split(":")
    return "{%s}%s" % (NS[p], t)


def sub(parent, tag, **attrs):
    el = etree.SubElement(parent, q(tag))
    for k, v in attrs.items():
        el.set(q("w:" + k), str(v))
    return el


def insert_in_order(parent, el, order):
    """Insert el into parent so that the child order follows the schema sequence `order` (list of local names)."""
    name = etree.QName(el).localname
    idx = order.index(name)
    pos = len(parent)
    for k, ch in enumerate(parent):
        ln = etree.QName(ch).localname
        if ln in order and order.index(ln) > idx:
            pos = k
            break
    parent.insert(pos, el)


TBLPR_ORDER = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize", "tblStyleColBandSize", "tblW", "jc",
               "tblCellSpacing", "tblInd", "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook", "tblCaption", "tblDescription"]
TCPR_ORDER = ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap", "tcMar", "textDirection", "tcFitText", "vAlign", "hideMark"]
PPR_ORDER = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd",
             "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi",
             "adjustRightInd", "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc", "textDirection",
             "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr", "pPrChange"]
RPR_ORDER = ["rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike", "dstrike", "outline", "shadow", "emboss", "imprint",
             "noProof", "snapToGrid", "vanish", "webHidden", "color", "spacing", "w", "kern", "position", "sz", "szCs", "highlight", "u",
             "effect", "bdr", "shd", "fitText", "vertAlign", "rtl", "cs", "em", "lang", "eastAsianLayout", "specVanish", "oMath"]


def get_child(parent, tag, order):
    el = parent.find(q(tag))
    if el is None:
        el = etree.Element(q(tag))
        insert_in_order(parent, el, order)
    return el


def set_border(parent, side, sz):
    for ex in parent.findall(q("w:" + side)):
        parent.remove(ex)
    b = etree.SubElement(parent, q("w:" + side))
    b.set(q("w:val"), "single")
    b.set(q("w:sz"), str(sz))
    b.set(q("w:space"), "0")
    b.set(q("w:color"), "000000")
    return b


def fix_equations(body, stats):
    n = 0
    for para in list(body.iter(q("w:p"))):
        omp = para.find(q("m:oMathPara"))
        if omp is None:
            continue
        num = None
        for r in omp.iter(q("m:r")):
            t = "".join(x.text or "" for x in r.iter(q("m:t")))
            mm = re.search(r"@@EQ:([^@]+)@@", t)
            if mm:
                num = mm.group(1)
                r.getparent().remove(r)
                break
        if num is None:
            continue
        oMath = omp.find(q("m:oMath"))
        # new paragraph properties
        old = para.find(q("w:pPr"))
        style = None
        if old is not None and old.find(q("w:pStyle")) is not None:
            style = old.find(q("w:pStyle")).get(q("w:val"))
        if old is not None:
            para.remove(old)
        ppr = etree.Element(q("w:pPr"))
        if style:
            sub(ppr, "w:pStyle", val=style)
        tabs = sub(ppr, "w:tabs")
        sub(tabs, "w:tab", val="center", pos=TEXTW // 2)
        sub(tabs, "w:tab", val="right", pos=TEXTW)
        sub(ppr, "w:spacing", before=60, after=60)
        para.insert(0, ppr)
        para.remove(omp)
        r1 = sub(para, "w:r")
        sub(r1, "w:tab")
        para.append(oMath)
        r2 = sub(para, "w:r")
        sub(r2, "w:tab")
        r3 = sub(para, "w:r")
        tt = sub(r3, "w:t")
        tt.text = "(%s)" % num
        n += 1
    stats["equation_paragraphs"] = n


BAR_W = 260   # dxa per scope level (about 4.6 mm)


def _cell_text(tc):
    return "".join(x.text or "" for x in tc.iter(q("w:t")))


def _set_tcw(tc, w, span=1):
    tcPr = tc.find(q("w:tcPr"))
    if tcPr is None:
        tcPr = etree.Element(q("w:tcPr"))
        tc.insert(0, tcPr)
    for tag in ("tcW", "gridSpan"):
        for ex in tcPr.findall(q("w:" + tag)):
            tcPr.remove(ex)
    tw = etree.Element(q("w:tcW"))
    tw.set(q("w:w"), str(w))
    tw.set(q("w:type"), "dxa")
    insert_in_order(tcPr, tw, TCPR_ORDER)
    if span > 1:
        gs = etree.Element(q("w:gridSpan"))
        gs.set(q("w:val"), str(span))
        insert_in_order(tcPr, gs, TCPR_ORDER)
    return tcPr


def alg_scope_bars(t, stats):
    """algorithm2e 'vlined' look in Word: each block level is a narrow column whose left border is the scope bar and whose
    bottom border closes the block (the small end tick); the line text spans the remaining columns. Text stays editable."""
    rows = t.findall(q("w:tr"))
    lv = []
    for row in rows:
        tcs = row.findall(q("w:tc"))
        m = re.search(r"@@L(\d+)@@", _cell_text(tcs[-1])) if tcs else None
        lv.append(int(m.group(1)) if m else None)
        if m:
            for x in tcs[-1].iter(q("w:t")):
                if x.text and "@@L" in x.text:
                    x.text = re.sub(r"@@L\d+@@", "", x.text)
                    # drop the leading space the marker left behind
                    x.text = x.text.lstrip("\xa0 ") if x.text.strip() else x.text
    depth = max([v for v in lv if v is not None] or [0])
    grid = t.find(q("w:tblGrid"))
    gcols = grid.findall(q("w:gridCol"))
    total = TEXTW                 # full text width, fixed layout (pandoc gives the two columns equal widths)
    w0 = 520                      # line-number column
    tblPr = t.find(q("w:tblPr"))
    for tag in ("tblW", "tblLayout"):
        for ex in tblPr.findall(q("w:" + tag)):
            tblPr.remove(ex)
    tw = etree.Element(q("w:tblW"))
    tw.set(q("w:w"), str(TEXTW))
    tw.set(q("w:type"), "dxa")
    insert_in_order(tblPr, tw, TBLPR_ORDER)
    lay = etree.Element(q("w:tblLayout"))
    lay.set(q("w:type"), "fixed")
    insert_in_order(tblPr, lay, TBLPR_ORDER)
    textw = total - w0 - depth * BAR_W
    for g in gcols:
        grid.remove(g)
    for w in [w0] + [BAR_W] * depth + [textw]:
        sub(grid, "w:gridCol", w=w)
    for ri, (row, L) in enumerate(zip(rows, lv)):
        tcs = row.findall(q("w:tc"))
        numtc, txttc = tcs[0], tcs[-1]
        _set_tcw(numtc, w0)
        if L is None:   # Input / Data / Output rows span every bar column
            _set_tcw(txttc, total - w0, span=depth + 1)
            continue
        nxt = next((v for v in lv[ri + 1:] if v is not None), 0)
        for i in range(1, L + 1):
            bar = etree.Element(q("w:tc"))
            tcPr = _set_tcw(bar, BAR_W)
            bd = etree.Element(q("w:tcBorders"))
            set_border(bd, "left", 6)
            if nxt < i:
                set_border(bd, "bottom", 6)
            insert_in_order(tcPr, bd, TCPR_ORDER)
            p = copy.deepcopy(numtc.find(q("w:p")))
            for r in p.findall(q("w:r")):
                p.remove(r)
            bar.append(p)
            txttc.addprevious(bar)
        _set_tcw(txttc, textw + (depth - L) * BAR_W, span=depth - L + 1)
    # a line that is only a formula would be shown by Word as centred display math: keep it inline-left
    for p in t.iter(q("w:p")):
        kids = [c for c in p if c.tag != q("w:pPr")]
        if not kids or not any(c.tag == q("m:oMath") for c in kids):
            continue
        if all(c.tag == q("m:oMath") or (c.tag == q("w:r") and not "".join(x.text or "" for x in c.iter(q("w:t"))).replace("\u200b", "").strip())
               for c in kids):
            para = etree.Element(q("m:oMathPara"))
            pp = etree.SubElement(para, q("m:oMathParaPr"))
            jc = etree.SubElement(pp, q("m:jc"))
            jc.set(q("m:val"), "left")
            for c in kids:
                if c.tag == q("m:oMath"):
                    para.append(c)
            p.append(para)
            stats["alg_math_left"] = stats.get("alg_math_left", 0) + 1
    stats["alg_scope_depth"] = stats.get("alg_scope_depth", []) + [depth]


def math_only_align(p, a, stats):
    """Word shows a paragraph that holds only a formula as centred display math. In a table cell, wrap it in an
    m:oMathPara justified like its column (l, c or r) so it reads as inline text of that column."""
    kids = [c for c in p if c.tag != q("w:pPr")]
    if not kids or not any(c.tag == q("m:oMath") for c in kids):
        return
    if not all(c.tag == q("m:oMath") or (c.tag == q("w:r") and not "".join(x.text or "" for x in c.iter(q("w:t"))).replace("\u200b", "").strip())
               for c in kids):
        return
    para = etree.Element(q("m:oMathPara"))
    pp = etree.SubElement(para, q("m:oMathParaPr"))
    jc = etree.SubElement(pp, q("m:jc"))
    jc.set(q("m:val"), {"r": "right", "c": "center"}.get(a, "left"))
    for c in kids:
        if c.tag == q("m:oMath"):
            para.append(c)
    p.append(para)
    stats["table_math_cells"] = stats.get("table_math_cells", 0) + 1


def full_width(t, stats):
    """Every table (and every panel of a multi-panel table) spans the full text width, as in the PDF, with the
    LaTeX column proportions kept."""
    tblPr = t.find(q("w:tblPr"))
    for ex in tblPr.findall(q("w:tblW")):
        tblPr.remove(ex)
    tw = etree.Element(q("w:tblW"))
    tw.set(q("w:w"), "5000")
    tw.set(q("w:type"), "pct")
    insert_in_order(tblPr, tw, TBLPR_ORDER)
    grid = t.find(q("w:tblGrid"))
    gcols = grid.findall(q("w:gridCol")) if grid is not None else []
    tot = sum(int(g.get(q("w:w"))) for g in gcols)
    if tot:
        f = TEXTW / tot
        for g in gcols:
            g.set(q("w:w"), str(int(round(int(g.get(q("w:w"))) * f))))
        for tcw in t.iter(q("w:tcW")):
            if tcw.get(q("w:type")) == "dxa":
                tcw.set(q("w:w"), str(int(round(int(tcw.get(q("w:w"))) * f))))
    stats["tables_full_width"] = stats.get("tables_full_width", 0) + 1


def fix_tables(body, meta, stats):
    tbls = [c for c in body if c.tag == q("w:tbl")]
    stats["tables"] = len(tbls)
    stats["tablemeta"] = len(meta)
    stats["table_borders_ok"] = 0
    stats["table_no_header"] = 0
    for t, md in zip(tbls, meta):
        if md["kind"] == "alg":
            alg_scope_bars(t, stats)
        else:
            full_width(t, stats)
        tblPr = t.find(q("w:tblPr"))
        for ex in tblPr.findall(q("w:tblBorders")):
            tblPr.remove(ex)
        bd = etree.Element(q("w:tblBorders"))
        for side in ("top", "bottom"):
            set_border(bd, side, 12)
        insert_in_order(tblPr, bd, TBLPR_ORDER)
        for ex in tblPr.findall(q("w:tblCellMar")):
            tblPr.remove(ex)
        cm = etree.Element(q("w:tblCellMar"))
        for side, v in (("top", 20), ("left", 60), ("bottom", 20), ("right", 60)):
            sub(cm, "w:" + side, w=v, type="dxa")
        insert_in_order(tblPr, cm, TBLPR_ORDER)
        rows = t.findall(q("w:tr"))
        hdr = [r for r in rows if r.find(q("w:trPr")) is not None and r.find(q("w:trPr")).find(q("w:tblHeader")) is not None]
        if not hdr:
            stats["table_no_header"] += 1
            if md.get("head_rows"):
                hdr = rows[:md["head_rows"]]
                stats["alg_head_rule"] = stats.get("alg_head_rule", 0) + 1
        # header rule under the last header row
        if hdr:
            for tc in hdr[-1].findall(q("w:tc")):
                tcPr = get_child(tc, "w:tcPr", ["tcPr"]) if tc.find(q("w:tcPr")) is None else tc.find(q("w:tcPr"))
                if tc.find(q("w:tcPr")) is None:
                    tc.insert(0, tcPr)
                tb = tcPr.find(q("w:tcBorders"))
                if tb is None:
                    tb = etree.Element(q("w:tcBorders"))
                    insert_in_order(tcPr, tb, TCPR_ORDER)
                set_border(tb, "bottom", 6)
        stats["table_borders_ok"] += 1
        # white space between a table and the body paragraph that follows it
        nxt = t.getnext()
        if nxt is not None and nxt.tag == q("w:p"):
            ppr = nxt.find(q("w:pPr"))
            if ppr is None:
                ppr = etree.Element(q("w:pPr"))
                nxt.insert(0, ppr)
            sp = ppr.find(q("w:spacing"))
            if sp is None:
                sp = etree.Element(q("w:spacing"))
                insert_in_order(ppr, sp, PPR_ORDER)
            if int(sp.get(q("w:before"), "0")) < 160:
                sp.set(q("w:before"), "160")
        # keep short tables and algorithms on one page: keep-with-next on every row but the last, rows do not split,
        # and the caption paragraph before the table stays with it
        if len(rows) <= 40 and (md["kind"] == "alg" or len(rows) <= 14):
            for ri, row in enumerate(rows):
                trPr = row.find(q("w:trPr"))
                if trPr is None:
                    trPr = etree.Element(q("w:trPr"))
                    row.insert(1 if row.find(q("w:tblPrEx")) is not None else 0, trPr)
                if trPr.find(q("w:cantSplit")) is None:
                    trPr.insert(0, etree.Element(q("w:cantSplit")))
                if ri < len(rows) - 1:
                    for p in row.iter(q("w:p")):
                        ppr = p.find(q("w:pPr"))
                        if ppr is None:
                            ppr = etree.Element(q("w:pPr"))
                            p.insert(0, ppr)
                        if ppr.find(q("w:keepNext")) is None:
                            insert_in_order(ppr, etree.Element(q("w:keepNext")), PPR_ORDER)
            prev = t.getprevious()
            if prev is not None and prev.tag == q("w:p"):
                ppr = prev.find(q("w:pPr"))
                if ppr is None:
                    ppr = etree.Element(q("w:pPr"))
                    prev.insert(0, ppr)
                if ppr.find(q("w:keepNext")) is None:
                    insert_in_order(ppr, etree.Element(q("w:keepNext")), PPR_ORDER)
        size = 16 if md.get("wide") else 18
        align = md["align"]
        for ri, row in enumerate(rows):
            ishdr = row in hdr
            col = 0
            for tc in row.findall(q("w:tc")):
                span = 1
                tcPr = tc.find(q("w:tcPr"))
                if tcPr is not None and tcPr.find(q("w:gridSpan")) is not None:
                    span = int(tcPr.find(q("w:gridSpan")).get(q("w:val")))
                a = align[col] if col < len(align) else "l"
                if span > 1 and md["kind"] != "alg":   # spanning group heads (PM100 over two columns) are centred
                    a = "c"
                for p in tc.findall(q("w:p")):
                    ppr = get_child(p, "w:pPr", ["pPr"]) if p.find(q("w:pPr")) is None else p.find(q("w:pPr"))
                    if p.find(q("w:pPr")) is None:
                        p.insert(0, ppr)
                    for ex in ppr.findall(q("w:jc")):
                        ppr.remove(ex)
                    math_only_align(p, a, stats)
                    if a in ("r", "c"):
                        jc = etree.Element(q("w:jc"))
                        jc.set(q("w:val"), "right" if a == "r" else "center")
                        insert_in_order(ppr, jc, PPR_ORDER)
                    for r in p.iter(q("w:r")):
                        rpr = r.find(q("w:rPr"))
                        if rpr is None:
                            rpr = etree.Element(q("w:rPr"))
                            r.insert(0, rpr)
                        for tag in ("sz", "szCs"):
                            for ex in rpr.findall(q("w:" + tag)):
                                rpr.remove(ex)
                            e = etree.Element(q("w:" + tag))
                            e.set(q("w:val"), str(size))
                            insert_in_order(rpr, e, RPR_ORDER)
                        if ishdr and md["kind"] != "alg" and rpr.find(q("w:b")) is None:
                            b = etree.Element(q("w:b"))
                            insert_in_order(rpr, b, RPR_ORDER)
                col += span


def fix_text(root, stats):
    n_dash = 0
    for t in root.iter(q("w:t"), q("m:t")):
        s = t.text or ""
        if "\u200b" in s:
            # pandoc's OMML uses a ZWSP as the empty superscript of an n-ary operator; an empty m:t is equivalent
            stats["zwsp_removed"] = stats.get("zwsp_removed", 0) + s.count("\u200b")
            s = s.replace("\u200b", "")
        if "–" in s or "—" in s:
            n_dash += s.count("–") + s.count("—")
            s = s.replace("–", "-").replace("—", "-")
        if t.tag == q("w:t"):
            s = re.sub(r"(?<=\w)'(?=\w)", "’", s)
            s = re.sub(r"(?<=\w)'(?=\s|$|[.,;:)])", "’", s)
            s = re.sub(r"(?<=\s)'(?=\w)", "‘", s)
        t.text = s
    stats["dashes_replaced"] = n_dash


def post(raw, out, meta, title):
    stats = {}
    shutil.copyfile(raw, out)
    zin = zipfile.ZipFile(raw)
    zout = zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "word/document.xml":
            root = etree.fromstring(data)
            body = root.find(q("w:body"))
            fix_equations(body, stats)
            fix_tables(body, meta, stats)
            fix_text(root, stats)
            data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
        elif item.filename in ("word/footnotes.xml", "word/endnotes.xml", "word/comments.xml"):
            root = etree.fromstring(data)
            fix_text(root, {})
            data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
        elif item.filename == "word/styles.xml":
            # owner rule: DOI and URL links blue and clickable (the reference doc had set every style colour to black)
            s_ = data.decode("utf-8")
            s_, k = re.subn(r'(<w:style [^>]*w:styleId="Hyperlink"[^>]*>(?:(?!</w:style>).)*?<w:color w:val=")000000(")', r"\g<1>0000FF\g<2>", s_, flags=re.S)
            stats["hyperlink_style_blue"] = k
            data = s_.encode("utf-8")
        elif item.filename == "docProps/core.xml":
            s = data.decode("utf-8")
            s = re.sub(r"<dc:title>.*?</dc:title>", "<dc:title>%s</dc:title>" % re.sub(r"[<>&]", "", title), s, flags=re.S)
            data = s.encode("utf-8")
        zout.writestr(item, data)
    zout.close()
    return stats
