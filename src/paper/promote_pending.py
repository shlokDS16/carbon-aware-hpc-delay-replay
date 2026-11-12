r"""Promote <<PENDING:key|fmt>> to <<key|fmt>> in every template once the key exists in a ledger.

Run from paper_A: py -I src/paper/promote_pending.py
Reads tables/ledger_*.csv (key,value,source). Edits paper/sections/*.tmpl.tex, paper/tables/*.tex,
paper/floats.tmpl.tex, paper/highlights.tmpl.txt, paper/sections/S_supplement.tmpl.tex in place (UTF-8, newline="").
Keys contain '|', so the format is split off at the last '|'. Prints a count per file.
"""
import csv
import glob
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
keys = set()
for f in glob.glob(str(ROOT / "tables" / "ledger_*.csv")):
    with open(f, encoding="utf-8", newline="") as fh:
        for row in csv.reader(fh):
            if row and row[0] != "key":
                keys.add(row[0])

pat = re.compile(r"<<PENDING:([^>]*)>>")
files = (glob.glob(str(ROOT / "paper" / "sections" / "*.tmpl.tex"))
         + glob.glob(str(ROOT / "paper" / "tables" / "*.tex"))
         + [str(ROOT / "paper" / "floats.tmpl.tex"), str(ROOT / "paper" / "highlights.tmpl.txt")])
total = 0
for f in files:
    p = Path(f)
    if not p.exists():
        continue
    with open(p, encoding="utf-8", newline="") as fh:
        s = fh.read()
    n = 0

    def repl(m):
        global n_
        body = m.group(1)
        key = body.rsplit("|", 1)[0]
        if key in keys:
            return "<<" + body + ">>"
        return m.group(0)

    new = pat.sub(repl, s)
    n = len(pat.findall(s)) - len(pat.findall(new))
    if n:
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(new)
        print(f"{p.relative_to(ROOT)}: promoted {n}")
        total += n
print(f"total promoted: {total}; keys loaded: {len(keys)}")
