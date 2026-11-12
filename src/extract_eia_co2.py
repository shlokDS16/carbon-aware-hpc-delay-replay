"""A06: extract the hourly CO2 columns from a per-BA EIA-930 Excel file (stream read) into a small CSV."""
import sys, os, openpyxl, csv
ba = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "data", "raw", "eia930_emissions", f"{ba}.xlsx")
dst = os.path.join(ROOT, "data", "raw", "eia930_emissions", f"{ba}_co2_hourly.csv")
wb = openpyxl.load_workbook(src, read_only=True)
ws = wb["Published Hourly Data"]
it = ws.iter_rows(values_only=True)
hdr = next(it)
keep = [0, 1, 15] + list(range(76, 91))  # BA, UTC, Adjusted NG, CO2 columns
with open(dst, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow([hdr[i] for i in keep])
    for r in it:
        w.writerow([r[i] for i in keep])
print("done")
