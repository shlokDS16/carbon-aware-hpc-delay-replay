r"""Build an inline-context Codex prompt (the Codex shell cannot start since the 2026-11-12 restart).
Usage from paper_A: py -I research/codex/make_bundle.py <base_prompt.md> <out.md>
"""
import csv
import glob
import os
import re
import sys

base, out_path = sys.argv[1], sys.argv[2]
brief = open(base, encoding="utf-8").read()
head = brief.split("Read:", 1)[0]
questions = "Questions" + brief.split("Questions", 1)[1]
parts = [head,
         "IMPORTANT: your shell cannot start in this workspace. Do NOT run commands or read files. Everything you need "
         "is included below: the filled manuscript sections, selected ledger rows (key,value) and audit excerpts.\n",
         questions]
alg = re.compile(r"\\begin\{algorithm\}.*?\\end\{algorithm\}", re.S)
for f in ["00_frontmatter", "01_intro", "02_related", "03_data", "04_method", "05_results", "06_discussion",
          "07_conclusion"]:
    s = open(f"paper/sections/{f}.tex", encoding="utf-8").read()
    parts.append(f"\n===== {f} =====\n" + alg.sub("[algorithm omitted]", s))
parts.append("\n===== table T1_related =====\n" + open("paper/tables/T1_related.tex", encoding="utf-8").read())
want = ("saving.lgbm|req", "saving.oracle|act", "saving.lgbm|pred", "saving.lgbm|act", "saving.oracle|req",
        "H1_", "H2_", "H3_", "shapley", "g_per_job", "g_per_kwh", "runnow", "retained", "|m")
rows = []
files = ["tables/ledger_TEST.csv", "tables/ledger_TEST_posthoc.csv"] + sorted(glob.glob("tables/ledger_TEST_sens_*.csv"))
for f in files:
    for row in csv.reader(open(f, encoding="utf-8")):
        if not row or row[0] == "key":
            continue
        k = row[0]
        if ".u." in k or "twostage" in k or k.endswith((".p", ".p_holm")):
            continue
        if ("S12" in k or "S24" in k) and any(w in k for w in want):
            try:
                rows.append(f"{k},{float(row[1]):.5g}")
            except ValueError:
                pass
parts.append("\n===== selected ledger rows (S12/S24, energy-weighted) =====\n" + "\n".join(rows[:3000]))
a13 = open("research/journal/A13_OVERLAP_AUDIT.md", encoding="utf-8").read()
i = a13.find("## 4")
parts.append("\n===== overlap audit excerpt =====\n" + a13[:1500] + "\n...\n" + (a13[i:i + 5000] if i > 0 else ""))
parts.append("\n===== literature audit excerpt =====\n" + open("research/journal/A20_LIT_LICENCE.md", encoding="utf-8").read()[:5000])
for extra in sys.argv[3:]:
    if os.path.exists(extra):
        parts.append(f"\n===== {extra} =====\n" + open(extra, encoding="utf-8").read()[:8000])
open(out_path, "w", encoding="utf-8").write("\n".join(parts))
print(out_path, os.path.getsize(out_path), "bytes,", len(rows), "ledger rows")
