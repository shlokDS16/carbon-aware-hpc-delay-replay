"""Publication figures for Paper A (SUSCOM). One function per figure; main builds the requested ones.

Usage: py src/figures.py [1 2 ... 13]   (default: all 13, SPEC v1 numbering)
Reads tables/*.csv, results/analysis_TEST_PM100_w.json and, for Figures 2-4 only, data/derived (RAM gate 3 GB, needed columns only).
No number is typed by hand. Figures 11 (X1) and 12 (robustness) are drawn from tables/ledger_TEST_sens_*.csv; a variant not run on a trace is left blank.
Writes figures/Figure_<n>.png (300 dpi), figures/Figure_<n>.pdf (vector, Type 42 fonts), figures/CAPTIONS.md and figures/FIGURE_DATA.md.
"""
import csv
import glob
import json
import os
import re
import subprocess
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAB = os.path.join(ROOT, "tables")
FIG = os.environ.get("A31_FIG_DIR", os.path.join(ROOT, "figures"))
SENS_DIR = os.environ.get("A31_SENS_DIR", TAB)
os.makedirs(FIG, exist_ok=True)

MM = 1 / 25.4
W1, W2 = 90 * MM, 190 * MM

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
    "font.size": 7.5, "axes.labelsize": 7.5, "axes.titlesize": 8, "xtick.labelsize": 7,
    "ytick.labelsize": 7, "legend.fontsize": 7, "axes.linewidth": 0.6,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": False,
    "grid.color": "#dddddd", "grid.linewidth": 0.5,
    "pdf.fonttype": 42, "ps.fonttype": 42, "savefig.dpi": 300, "figure.dpi": 100,
    "axes.unicode_minus": True,
})

INK, INK2, GRID = "#222222", "#555555", "#dddddd"

# fixed color / marker per arm (Okabe-Ito); baselines in greys
ARMS = {
    "oracle|act": ("oracle signal + actual runtime\n(upper bound)", "#0072B2", "o"),
    "oracle|req": ("oracle signal + requested\nwalltime", "#56B4E9", "s"),
    "lgbm|act": ("forecast + actual runtime", "#E69F00", "^"),
    "lgbm|req": ("forecast + requested walltime\n(forecast-and-request, D)", "#D55E00", "D"),
    "lgbm|pred": ("forecast + history-predicted\nruntime", "#009E73", "v"),
    "lgbm|pred2": ("forecast + capped predicted\nruntime", "#CC79A7", "P"),
    "night": ("night rule (start 00:00-03:59)", "#7a7a7a", "X"),
    "histprofile|req": ("historical profile + requested\nwalltime", "#b0b0b0", "h"),
}
ARM_ORDER = ["night", "histprofile|req", "oracle|act", "oracle|req", "lgbm|act", "lgbm|req", "lgbm|pred", "lgbm|pred2"]
TRACES = [("PM100", "PM100 (primary)"), ("FDATA", "F-DATA"), ("KIT_FH2", "KIT FH2")]
SLACKS = [2, 6, 12, 24]


def flat(label):
    return label.replace("\n", " ")


# ---------------------------------------------------------------- data access
def load_ledger(fn):
    return load_ledger_path(os.path.join(TAB, fn))


def load_ledger_path(path):
    d = {}
    with open(path, newline="") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            try:
                d[row[0]] = float(row[1])
            except ValueError:
                d[row[0]] = float("nan")
    return d


LT = load_ledger("ledger_TEST.csv")
LNL = load_ledger("ledger_TEST_nearlimit.csv")
LDEV = load_ledger("ledger_DEV.csv")
LSEC = load_ledger("ledger_TEST_secondary.csv")


def g(L, key):
    if key not in L:
        raise KeyError(key)
    return L[key]


def sav(tr, S, arm, kind="", w="w", ts=False):
    return g(LT, f"TEST.{tr}.{w}.{'twostage.' if ts else ''}S{S}.saving{kind}.{arm}")


def hyp(L, prefix, tr, S, h, w="w", ts=False):
    base = f"{prefix}.{tr}.{w}.{'twostage.' if ts else ''}S{S}.{h}"
    return g(L, base + ".est"), g(L, base + ".lo"), g(L, base + ".hi")


def pct(v, d=1):
    return f"{100 * v:.{d}f}"


def save(fig, n):
    fig.savefig(os.path.join(FIG, f"Figure_{n}.png"), dpi=300)
    fig.savefig(os.path.join(FIG, f"Figure_{n}.pdf"))
    plt.close(fig)


def panel_letter(ax, s, dx=-0.0, dy=1.04):
    ax.text(dx, dy, s, transform=ax.transAxes, fontsize=8.5, fontweight="bold", va="bottom", ha="left")


def style_x_grid(ax):
    ax.grid(axis="x", zorder=0)
    ax.set_axisbelow(True)


CAPTIONS = {}  # n -> (caption, keys)


# ---------------------------------------------------------------- Figure 1 (schematic)
def fig1():
    fig = plt.figure(figsize=(W2, 128 * MM))
    # ---- (a) timeline
    axa = fig.add_axes([0.07, 0.50, 0.91, 0.34])
    S, step = 12.0, 0.25
    t = np.linspace(0, 17, 400)
    actual = 330 - 120 * np.exp(-((t - 8.6) / 2.6) ** 2) - 35 * np.exp(-((t - 2.0) / 1.6) ** 2) + 18 * np.sin(t * 1.1)
    fcast = 330 - 85 * np.exp(-((t - 7.4) / 3.2) ** 2) - 20 * np.exp(-((t - 2.2) / 1.8) ** 2) + 6 * np.sin(t * 0.8)
    R_req, R_act = 4.0, 2.5

    def integ(sig, s, R):
        m = (t >= s) & (t <= s + R)
        return np.trapezoid(sig[m], t[m])

    cands = np.arange(0, S + 1e-9, step)
    s_hat = cands[int(np.argmin([integ(fcast, s, R_req) for s in cands]))]
    # window and candidate starts
    axa.axvspan(0, S, color="#eeeeee", zorder=0)
    axa.plot(t, actual, color=INK, lw=1.3, zorder=3)
    axa.plot(t, fcast, color=ARMS["lgbm|req"][1], lw=1.3, ls=(0, (4, 2)), zorder=3)
    ymin, ymax = 150, 380
    axa.set_ylim(ymin, ymax)
    axa.set_xlim(-0.4, 17.4)
    for c in cands:
        axa.plot([c, c], [ymin, ymin + (9 if abs(c * 2 - round(c * 2)) > 1e-9 else 14)], color=INK2, lw=0.4, zorder=2)
    # run now (actual runtime), shaded under actual curve
    m0 = (t >= 0) & (t <= R_act)
    axa.fill_between(t[m0], ymin + 16, actual[m0], color="#b0b0b0", alpha=0.55, zorder=1, lw=0)
    ms = (t >= s_hat) & (t <= s_hat + R_act)
    axa.fill_between(t[ms], ymin + 16, actual[ms], color=ARMS["lgbm|req"][1], alpha=0.35, zorder=1, lw=0)
    # planner's request box (R_req) outline
    axa.add_patch(Rectangle((s_hat, ymin + 16), R_req, 12, fill=False, ec=ARMS["lgbm|req"][1], lw=1.0, ls="--", zorder=4))
    axa.add_patch(Rectangle((s_hat, ymin + 16), R_act, 12, fc=ARMS["lgbm|req"][1], ec="none", alpha=0.75, zorder=4))
    axa.add_patch(Rectangle((0, ymin + 16), R_act, 12, fc="#7a7a7a", ec="none", alpha=0.85, zorder=4))
    axa.text(0.1, ymin + 31, "run now (start = arrival)", fontsize=7, color=INK, va="bottom")
    axa.text(s_hat + 0.1, ymin + 31, "delayed start chosen by the planner\n(solid: actual runtime; dashed: requested walltime)",
             fontsize=7, color=INK, va="bottom", bbox=dict(fc="white", ec="none", alpha=0.75, pad=0.6), zorder=6)
    # annotations
    axa.annotate("", xy=(0, 365), xytext=(S, 365), arrowprops=dict(arrowstyle="<->", lw=0.8, color=INK))
    axa.text(S / 2, 369, "slack window S (2, 6, 12 or 24 h; 12 h shown)", ha="center", va="bottom", fontsize=7)
    axa.text(S + 0.2, ymin + 30, "candidate starts\nevery 0.25 h (ticks)", fontsize=7, color=INK2, va="center")
    axa.axvline(0, color=INK, lw=0.7)
    axa.text(0.0, ymax + 2, "job arrives", fontsize=7, ha="center", va="bottom", clip_on=False)
    axa.set_xlabel("time since arrival (h)")
    axa.set_ylabel("grid carbon intensity\n(g CO$_2$e/kWh, illustrative)")
    axa.set_yticks([200, 250, 300, 350])
    axa.legend(handles=[
        Line2D([], [], color=INK, lw=1.3, label="actual intensity (known only afterwards; used by the oracle and to score every start)"),
        Line2D([], [], color=ARMS["lgbm|req"][1], lw=1.3, ls=(0, (4, 2)), label="past-only forecast issued at arrival (what a planner can use at arrival)")],
        loc="lower right", bbox_to_anchor=(1.0, 1.2), frameon=False, ncol=1, fontsize=7, handlelength=2.2, borderaxespad=0)
    panel_letter(axa, "(a)", dx=-0.065, dy=1.2)

    # ---- (b) 2x3 information design
    axb = fig.add_axes([0.0, 0.0, 1.0, 0.43])
    axb.set_xlim(0, 190)
    axb.set_ylim(0, 55)
    axb.axis("off")
    axb.text(0.5, 53.5, "(b)", fontsize=8.5, fontweight="bold", va="top", ha="left")
    axb.text(100, 53.5, "runtime estimate the planner uses for the job length", fontsize=7.5, ha="center", va="top", fontweight="bold")
    cols = [("actual runtime $R_{act}$\n(unknown at submission)", "act"),
            ("requested walltime $R_{req}$\n(known at submission)", "req"),
            ("predicted from the user's\nlast two jobs (secondary)", "pred")]
    rows = [("oracle", "oracle signal\n(actual intensity;\nnot available at arrival)"), ("lgbm", "LightGBM forecast\n(past-only;\navailable at arrival)")]
    x0, cw, ch, gap = 44, 46, 14, 2.5
    y_top = 41
    for j, (ct, ck) in enumerate(cols):
        axb.text(x0 + j * (cw + gap) + cw / 2, y_top + 1.5, ct, ha="center", va="bottom", fontsize=7)
    axb.text(2, y_top + 1.5, "signal the planner\noptimises over", fontsize=7.5, fontweight="bold", va="bottom", ha="left")
    notes = {("oracle", "act"): "upper bound", ("oracle", "req"): "perfect signal, user estimate",
             ("lgbm", "act"): "perfect runtime, real forecast", ("lgbm", "req"): "forecast-and-request arm D",
             ("oracle", "pred"): "", ("lgbm", "pred"): "past data only"}
    for i, (sk, st) in enumerate(rows):
        y = y_top - (i + 1) * ch - i * gap
        axb.text(x0 - 3, y + ch / 2, st, ha="right", va="center", fontsize=7)
        for j, (ct, ck) in enumerate(cols):
            arm = f"{sk}|{ck}"
            x = x0 + j * (cw + gap)
            if arm == "oracle|pred":
                axb.add_patch(FancyBboxPatch((x, y), cw, ch, boxstyle="round,pad=0,rounding_size=1.5", fc="none", ec="#bbbbbb", lw=0.6, ls=":"))
                axb.text(x + cw / 2, y + ch / 2, "(oracle|pred, supplement)", ha="center", va="center", fontsize=7, color=INK2)
                continue
            col = ARMS[arm][1]
            core = ck != "pred"
            axb.add_patch(FancyBboxPatch((x, y), cw, ch, boxstyle="round,pad=0,rounding_size=1.5", fc=col, ec=col if core else INK2,
                                         lw=1.2 if arm == "lgbm|req" else 0.6, alpha=0.30 if core else 0.2, ls="-" if core else "--"))
            axb.add_patch(FancyBboxPatch((x, y), cw, ch, boxstyle="round,pad=0,rounding_size=1.5", fc="none", ec=col if core else INK2,
                                         lw=1.6 if arm == "lgbm|req" else 0.8, ls="-" if core else "--"))
            axb.text(x + cw / 2, y + ch * 0.64, flat(ARMS[arm][0]).split(" (")[0], ha="center", va="center", fontsize=7, color=INK, fontweight="bold" if arm == "lgbm|req" else "normal")
            axb.text(x + cw / 2, y + ch * 0.26, notes[(sk, ck)], ha="center", va="center", fontsize=7, color=INK2)
    # footer: gap decomposition
    yb = 2
    axb.add_patch(FancyArrowPatch((x0 + cw / 2, y_top - ch - 0.5 + 0), (x0 + cw + gap + cw / 2, y_top - 2 * ch - gap - 0.5 + ch + 0), arrowstyle="-", lw=0))
    axb.text(2, 0.5,
             "Outcome per arm: saving = 1 - (carbon emitted by the arm) / (carbon emitted by running at arrival). The gap from oracle + actual runtime to the\n"
             "forecast-and-request arm D is split (Shapley) into a forecast term and a runtime-estimate term; H2 tests actual versus requested runtime under the forecast.",
             fontsize=7, color=INK, va="bottom", ha="left")
    save(fig, 1)



# ================================================================= A31 additions: helpers
def words(s):
    return len(s.replace("[", "").replace("]", "").split())


def cap(n, text, keys):
    assert words(text) <= 35, (n, words(text), text)
    CAPTIONS[n] = (text, keys)


class Skip(Exception):
    pass


LOGF = os.path.join(ROOT, "logs", "a31_figures.log")


def log(msg):
    print(msg, flush=True)
    os.makedirs(os.path.dirname(LOGF), exist_ok=True)
    with open(LOGF, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def free_gb():
    out = subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"],
                         capture_output=True, text=True).stdout
    return float(out.strip()) / 1048576.0


def ram_gate(name, need=3.0):
    f = free_gb()
    log(f"{name}: free RAM {f:.2f} GB (need {need})")
    if f < need:
        raise Skip(f"{name} skipped: free RAM {f:.2f} GB < {need} GB")


def peak_rss_mb():
    try:
        import psutil
        return psutil.Process().memory_info().peak_wset / 1e6 if hasattr(psutil.Process().memory_info(), "peak_wset") else psutil.Process().memory_info().rss / 1e6
    except Exception:
        return float("nan")


def log_rss(name):
    log(f"{name}: peak working set {peak_rss_mb():.0f} MB (limit 1500)")


LPH = load_ledger("ledger_TEST_posthoc.csv")
LAS = load_ledger("ledger_TEST_posthoc_armsync.csv")
LDATA = load_ledger("ledger_data.csv")
TRN = dict(TRACES)
TR_SHORT = {"PM100": "PM100", "FDATA": "F-DATA", "KIT_FH2": "KIT FH2"}
MTR = {"PM100": "o", "FDATA": "s", "KIT_FH2": "^"}
BLUE_SEQ, FC_COL = "#0072B2", "#D55E00"


def ph(*parts):
    return g(LPH, "posthoc." + ".".join(str(p) for p in parts))


def sig2(x):
    return f"{x:.2g}"


def hline_cap(ax, lo, hi, y, color, lw=0.9, cap_h=0.16, z=6):
    ax.plot([lo, hi], [y, y], color=color, lw=lw, zorder=z, solid_capstyle="butt")
    for v in (lo, hi):
        ax.plot([v, v], [y - cap_h, y + cap_h], color=color, lw=lw, zorder=z)


def pending_box(ax, text):
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(True)
        s.set_linestyle((0, (3, 2)))
        s.set_color(INK2)
        s.set_linewidth(0.8)
    ax.text(0.5, 0.5, text, transform=ax.transAxes, ha="center", va="center", fontsize=7.5, color=INK2)


# ---------------------------------------------------------------- Figure 1 wrapper
def fig1w():
    fig1()
    cap(1, "Study design. (a) The planner picks a start from the signal and runtime estimate it holds; emissions are scored on actual values. (b) The 2 x 2 design. Curves illustrative.", "[no ledger numbers]")


# ---------------------------------------------------------------- Figure 2 (data): BA character
def fig2():
    ram_gate("Figure 2")
    el = pd.read_csv(os.path.join(TAB, "ba_eligibility.csv")).set_index("ba")
    el = el[el.eligible]
    t0, t1 = pd.Timestamp("2025-07-01", tz="UTC"), pd.Timestamp("2026-07-01", tz="UTC")
    ci = pd.read_parquet(os.path.join(ROOT, "data", "derived", "ci_clean.parquet"), columns=["ba", "utc", "ci_clean"],
                         filters=[("utc", ">", t0), ("utc", "<=", t1)])
    mean_ci = ci.dropna().groupby("ba")["ci_clean"].mean()
    ch = pd.read_csv(os.path.join(TAB, "secondary_ba_character_TEST.csv"), index_col=0)
    df = el[["mean_gen_mw"]].join(ch, how="inner").join(mean_ci.rename("mean_ci"), how="inner")
    assert len(df) == 42, len(df)
    fig, ax = plt.subplots(figsize=(140 * MM, 88 * MM))
    ax.grid(zorder=0)
    ax.set_axisbelow(True)
    size = 6 + 38 * np.sqrt(df["mean_gen_mw"] / df["mean_gen_mw"].max())
    sc_ = ax.scatter(df["mean_ci"], df["median_daily_range"], s=size ** 1.0 * 2.2, c=df["share_solar"] * 100, cmap="Blues", vmin=0,
                     edgecolor=INK, linewidth=0.5, zorder=3)
    cb = fig.colorbar(sc_, ax=ax, pad=0.02, fraction=0.045)
    cb.set_label("solar share of generation (%)", fontsize=7)
    cb.ax.tick_params(labelsize=7, width=0.5, length=2)
    cb.outline.set_linewidth(0.5)
    ax.set_ylim(-24, None)
    ax.set_xlabel("mean carbon intensity, TEST year (g CO$_2$e/kWh)")
    ax.set_ylabel("median daily range of intensity (g CO$_2$e/kWh)")
    lab = list(df["median_daily_range"].sort_values(ascending=False).index[:5]) + list(df["mean_ci"].sort_values().index[:2]) + \
        list(df["mean_ci"].sort_values(ascending=False).index[:2]) + list(df["mean_gen_mw"].sort_values(ascending=False).index[:2])
    seen = set()
    offs = {"SPA": (-14, -10), "BPAT": (5, 4), "NEVP": (-26, 2), "MISO": (-4, -11), "LGEE": (-26, 4), "PACE": (3, 3)}
    for b in lab:
        if b in seen:
            continue
        seen.add(b)
        ax.annotate(b, (df.loc[b, "mean_ci"], df.loc[b, "median_daily_range"]), xytext=offs.get(b, (4, 3)), textcoords="offset points",
                    fontsize=7, color=INK)
    # size legend
    refs = [1000, 10000, 100000]
    hs = [Line2D([], [], marker="o", ls="none", mfc="white", mec=INK, mew=0.5,
                 ms=np.sqrt((6 + 38 * np.sqrt(r / df["mean_gen_mw"].max())) * 2.2), label=f"{r // 1000} GW") for r in refs]
    ax.legend(handles=hs, title="mean generation", loc="upper right", frameon=False, fontsize=7, title_fontsize=7, labelspacing=1.0,
              borderaxespad=0.2)
    fig.subplots_adjust(left=0.105, right=0.94, top=0.98, bottom=0.14)
    save(fig, 2)
    log_rss("Figure 2")
    lo, hi = df["median_daily_range"].min(), df["median_daily_range"].max()
    cap(2, f"The 42 grids differ widely in carbon intensity and in its daily swing. Median daily range runs from {lo:.0f} to {hi:.0f} g CO2e/kWh across BAs; "
           f"point area is mean generation, color solar share. TEST year.",
        "tables/secondary_ba_character_TEST.csv (median_daily_range, share_solar); tables/ba_eligibility.csv (mean_gen_mw); mean intensity from data/derived/ci_clean.parquet TEST year")


# ---------------------------------------------------------------- Figure 3 (data): runtime ratio ECDF
def fig3():
    ram_gate("Figure 3")
    import pyarrow.parquet as pq
    fig, ax = plt.subplots(figsize=(140 * MM, 80 * MM))
    ax.grid(zorder=0)
    ax.set_axisbelow(True)
    sty = {"PM100": ("#000000", "-"), "FDATA": ("#555555", (0, (5, 2))), "KIT_FH2": ("#999999", (0, (1.5, 1.5)))}
    meds = {}
    hand = []
    for tr, name in TRACES:
        t = pq.read_table(os.path.join(ROOT, "data", "derived", f"jobs_{tr}.parquet"), columns=["state", "r_act_h", "r_req_h"])
        st = t.column("state").to_numpy(zero_copy_only=False)
        ra = t.column("r_act_h").to_numpy()
        rq = t.column("r_req_h").to_numpy()
        del t
        m = (st == "COMPLETED") & (ra >= 1.0 / 60.0) & (rq > 0) & (rq <= 72.0)     # frozen main filter (PREREG s2)
        r = np.sort(ra[m] / rq[m])
        n = len(r)
        assert n == int(g(LDATA, f"data.{tr}.n_filtered_jobs")), (tr, n)
        meds[tr] = float(np.median(r))
        assert abs(meds[tr] - g(LDATA, f"data.{tr}.median_ratio")) < 1e-9, tr
        q = np.unique(np.concatenate([np.linspace(0, n - 1, 1500).astype(int), np.arange(0, n, max(1, n // 50))]))
        col, ls = sty[tr]
        ax.plot(r[q], (q + 1) / n, color=col, ls=ls, lw=1.4, drawstyle="steps-post", zorder=3)
        hand.append(Line2D([], [], color=col, ls=ls, lw=1.4, label=f"{name} (n = {n:,})"))
        del st, ra, rq, r
    ax.legend(handles=hand, loc="upper left", frameon=False, fontsize=7, borderaxespad=0.2)
    ax.axvline(1.0, color=INK2, lw=0.7)
    ax.text(1.04, 0.03, "actual = requested", fontsize=7, color=INK2, rotation=90, ha="left", va="bottom")
    ax.set_xscale("log")
    ax.set_xlim(2e-4, 3)
    ax.set_ylim(0, 1.0)
    ax.set_xlabel("actual runtime / requested walltime (log scale)")
    ax.set_ylabel("cumulative share of jobs")
    fig.subplots_adjust(left=0.115, right=0.98, top=0.98, bottom=0.15)
    save(fig, 3)
    log_rss("Figure 3")
    cap(3, f"Users request far more walltime than jobs use. Median actual-to-requested runtime ratio is {sig2(meds['PM100'])} on PM100, {sig2(meds['FDATA'])} on F-DATA "
           f"and {sig2(meds['KIT_FH2'])} on KIT FH2. Frozen filtered job populations.",
        "data.PM100.median_ratio; data.FDATA.median_ratio; data.KIT_FH2.median_ratio; data.<trace>.n_filtered_jobs (ECDF recomputed from data/derived/jobs_<trace>.parquet with the PREREG s2 filter and checked against both)")


# ---------------------------------------------------------------- Figure 4 (data): worked example
def fig4():
    ram_gate("Figure 4")
    sys.path.insert(0, os.path.join(ROOT, "src"))
    import simcore as sc
    ba, off = "ERCO", float(pd.read_csv(os.path.join(TAB, "ba_utc_offset.csv")).set_index("ba").loc["ERCO", "offset_h"])
    d = pd.read_parquet(os.path.join(ROOT, "data", "derived", "ci_clean.parquet"), filters=[("ba", "==", ba)],
                        columns=["utc", "ci_clean"]).sort_values("utc").reset_index(drop=True)
    origin = d.utc.iloc[0] - pd.Timedelta(hours=1)
    ci = d.ci_clean.ffill().bfill().to_numpy("float64")
    z = np.load(os.path.join(ROOT, "data", "derived", "forecasts", "lgbm", f"{ba}.npz"))
    issue = pd.to_datetime(z["issue_utc"], utc=True)
    fk = int(round((issue[0] - origin) / pd.Timedelta(hours=1)))
    loc = pd.Timestamp("2025-11-17 18:00")                    # Monday, local standard time
    a = ((loc - pd.Timedelta(hours=off)).tz_localize("UTC") - origin) / pd.Timedelta(hours=1)
    R_act, R_req, S = 1.5, 8.0, 12.0
    row = int(np.floor(a)) - fk
    w = z["fc"][row].astype("float64")
    w = np.concatenate([w, [w[-1]] * (sc.HP - len(w))])
    s_act = float(sc.plan_start(w[None, :], np.array([a]), np.array([R_act]), np.array([S]))[0]) - a
    s_req = float(sc.plan_start(w[None, :], np.array([a]), np.array([R_req]), np.array([S]))[0]) - a
    cum = sc.cum_hours(ci)
    mean_run = lambda s: float(sc.realised(cum, ci, np.array([a + s]), np.array([R_act]))[0] / R_act)  # noqa: E731
    m0, ma, mr = mean_run(0.0), mean_run(s_act), mean_run(s_req)
    assert s_act != s_req
    log(f"Figure 4 example: {ba}, arrival {loc} local, S={S}, R_act={R_act}, R_req={R_req}; start act {s_act:.2f} h, start req {s_req:.2f} h; "
        f"mean intensity during the run: now {m0:.0f}, act {ma:.0f}, req {mr:.0f}")
    k0 = int(np.floor(a))
    xs = np.arange(-24, 98)
    base = k0 - a
    fig, ax = plt.subplots(figsize=(140 * MM, 90 * MM))
    fl = np.floor(a)
    t_act = (fl + xs) - a
    ax.axvspan(0, S, color="#eeeeee", zorder=0, lw=0)
    ax.step(t_act, ci[k0 + xs], where="post", color=INK, lw=1.2, zorder=3)
    jj = np.arange(0, 98)
    ax.step(jj + base, w[jj], where="post", color=FC_COL, lw=1.2, ls=(0, (4, 2)), zorder=3)
    ymin = float(min(ci[k0 + xs].min(), w.min())) - 5
    ymax = float(max(ci[k0 + xs].max(), w.max())) + 6
    lane_h = (ymax - ymin) * 0.055
    y0 = ymin - 4.2 * lane_h
    ax.set_ylim(y0 - lane_h * 0.5, ymax + 40)
    ca, cr, cn = ARMS["lgbm|act"][1], ARMS["lgbm|req"][1], "#7a7a7a"
    lanes = [(0.0, R_act, R_act, cn, "run now"), (s_act, R_act, R_act, ca, "planner holds $R_{\mathrm{act}}$"), (s_req, R_req, R_act, cr, "planner holds $R_{\mathrm{req}}$")]
    for i, (s, Rb, Ra, col, lab) in enumerate(lanes):
        y = y0 + (len(lanes) - 1 - i) * 1.35 * lane_h
        if Rb != Ra:
            ax.add_patch(Rectangle((s, y), Rb, lane_h, fill=False, ec=col, lw=1.0, ls="--", zorder=4))
        ax.add_patch(Rectangle((s, y), Ra, lane_h, fc=col, ec="none", alpha=0.85, zorder=4))
        ax.text(s + Rb + 0.8, y + lane_h / 2, lab, fontsize=7, va="center", ha="left", color=INK, bbox=dict(fc="white", ec="none", alpha=0.85, pad=0.8), zorder=6)
    for s, col in ((s_act, ca), (s_req, cr)):
        ax.axvline(s, color=col, lw=0.9, ymin=0.0, ymax=1.0, zorder=2, ls=":")
    ax.axvline(0, color=INK, lw=0.7)
    ax.annotate("", xy=(0, ymax + 14), xytext=(S, ymax + 14), arrowprops=dict(arrowstyle="<->", lw=0.8, color=INK))
    ax.text(S + 1.5, ymax + 14, "slack window (12 h)", ha="left", va="center", fontsize=7)
    tk = np.arange(-24, 97, 12)
    ax.set_xticks(tk)
    ax.set_xticklabels([(loc + pd.Timedelta(hours=float(t))).strftime("%a\n%H:%M") for t in tk], fontsize=7)
    ax.set_xlim(-24, 98)
    ax.set_xlabel("local standard time (ERCO); the job arrives at 0")
    ax.set_ylabel("carbon intensity (g CO$_2$e/kWh)")
    ax.set_yticks([t for t in range(int(np.ceil(ymin / 50) * 50), int(ymax), 50)])
    ax.legend(handles=[Line2D([], [], color=INK, lw=1.2, label="actual intensity (scores every start)"),
                       Line2D([], [], color=FC_COL, lw=1.2, ls=(0, (4, 2)), label="past-only forecast issued at arrival")],
              loc="upper right", frameon=False, fontsize=7, borderaxespad=0.1, bbox_to_anchor=(1.0, 1.0), ncol=1)
    fig.subplots_adjust(left=0.1, right=0.985, top=0.985, bottom=0.17)
    save(fig, 4)
    log_rss("Figure 4")
    cap(4, f"Worked example (ERCO, 12 h slack; job runs {R_act:g} h, requests {R_req:g} h). On one forecast the planner starts {s_act:.1f} h after arrival holding the actual runtime, "
           f"{s_req:.1f} h holding the request. Illustration.",
        "illustrative single job: tables/ - none; data/derived/ci_clean.parquet (ERCO), data/derived/forecasts/lgbm/ERCO.npz, src/simcore.py plan_start")


# ---------------------------------------------------------------- Figure 5 (data): forecast skill by lead
def fig5():
    ram_gate("Figure 5")
    m = pd.read_csv(os.path.join(TAB, "secondary_forecast_mae.csv"))
    sm = pd.read_csv(os.path.join(TAB, "secondary_forecast_mae_summary.csv"))
    buckets = ["1-6", "7-24", "25-48", "49-96"]
    models = [("lgbm", "LightGBM forecast", FC_COL, "o", "-"), ("persistence", "persistence", "#555555", "s", (0, (5, 2))),
              ("snaive_day", "seasonal naive, day", "#7a7a7a", "^", (0, (1.5, 1.5))), ("snaive_week", "seasonal naive, week", "#999999", "v", (0, (3, 1.5, 1, 1.5))),
              ("profile7", "historical profile", "#b0b0b0", "D", "-")]
    fig, ax = plt.subplots(figsize=(140 * MM, 78 * MM))
    ax.grid(axis="y", zorder=0)
    ax.set_axisbelow(True)
    xs = np.arange(len(buckets))
    lab_y = []
    for i, (mk, lab, col, mrk, ls) in enumerate(models):
        sub = m[m.model == mk]
        mean = np.array([sub[sub.bucket == b]["mae"].mean() for b in buckets])
        q1 = np.array([sub[sub.bucket == b]["mae"].quantile(0.25) for b in buckets])
        q3 = np.array([sub[sub.bucket == b]["mae"].quantile(0.75) for b in buckets])
        for j, b in enumerate(buckets):
            ref = sm[(sm.model == mk) & (sm.bucket == b)]["mae_mean"].iloc[0]
            assert abs(ref - mean[j]) < 1e-6, (mk, b)
        dx = 0.0
        if mk == "lgbm":
            ax.fill_between(xs + dx, q1, q3, color=col, alpha=0.18, lw=0, zorder=2)
        ax.plot(xs + dx, mean, color=col, ls=ls, marker=mrk, ms=4.5, mec="white", mew=0.5, lw=1.4 if mk == "lgbm" else 1.1, zorder=3 + (mk == "lgbm"))
        lab_y.append([mean[-1] + {"lgbm": -2.2}.get(mk, 0), mk, lab])
    # end labels: keep at least 3.2 units apart (top down) so no two labels touch (layout only)
    lab_y.sort(key=lambda z: -z[0])
    for k in range(1, len(lab_y)):
        lab_y[k][0] = min(lab_y[k][0], lab_y[k - 1][0] - 3.2)
    for yy, mk, lab in lab_y:
        ax.text(xs[-1] + 0.13, yy, lab, fontsize=7, va="center", ha="left", color=INK if mk == "lgbm" else INK2)
    ax.set_xticks(xs)
    ax.set_xticklabels([b + " h" for b in buckets])
    ax.set_xlim(-0.2, xs[-1] + 1.15)
    ax.set_ylim(0, None)
    ax.set_xlabel("forecast lead")
    ax.set_ylabel("mean absolute error (g CO$_2$e/kWh)")
    fig.subplots_adjust(left=0.115, right=0.985, top=0.98, bottom=0.15)
    save(fig, 5)
    log_rss("Figure 5")
    a, b = sm[(sm.model == "lgbm") & (sm.bucket == "1-24")]["mae_mean"].iloc[0], sm[(sm.model == "persistence") & (sm.bucket == "1-24")]["mae_mean"].iloc[0]
    cap(5, f"The past-only LightGBM forecast has the lowest error in every lead bucket. At 1-24 h its mean absolute error is {a:.0f} g CO2e/kWh against {b:.0f} for persistence. "
           f"Mean over 42 BAs; band: LightGBM quartiles; TEST.",
        "tables/secondary_forecast_mae.csv and secondary_forecast_mae_summary.csv (TEST; lgbm and persistence, bucket 1-24)")
    # lowest-error check, written to the log
    for bk in buckets:
        best = sm[sm.bucket == bk].sort_values("mae_mean").iloc[0]["model"]
        assert best == "lgbm", (bk, best)


# ---------------------------------------------------------------- Figure 6 (main result)
def fig6():
    fig, axs = plt.subplots(1, 3, figsize=(W2, 100 * MM), sharey=True)
    ys = np.arange(len(ARM_ORDER))[::-1]
    for ax, (tr, name) in zip(axs, TRACES):
        style_x_grid(ax)
        yD = ys[ARM_ORDER.index("lgbm|req")]
        ax.axhspan(yD - 0.5, yD + 0.5, color="#fbe9dd", zorder=0, lw=0)
        ax.axvline(0, color=INK2, lw=0.7, zorder=1)
        xlo, xhi = 0.0, 0.0
        for y, arm in zip(ys, ARM_ORDER):
            lab, col, mk = ARMS[arm]
            v = 100 * sav(tr, 12, arm)
            lo, hi = 100 * sav(tr, 12, arm, "_lo"), 100 * sav(tr, 12, arm, "_hi")
            sl = 100 * g(LAS, f"posthoc.PH1arm.{tr}.w.S12.{arm}.sync_lo")
            sh = 100 * g(LAS, f"posthoc.PH1arm.{tr}.w.S12.{arm}.sync_hi")
            assert abs(100 * g(LAS, f"posthoc.PH1arm.{tr}.w.S12.{arm}.est") - v) < 1e-7
            ax.barh(y, hi - lo, left=lo, height=0.5, color=col, alpha=0.45, lw=0, zorder=3)
            hline_cap(ax, sl, sh, y, INK, lw=0.9, cap_h=0.22, z=4)
            ax.plot(v, y, marker=mk, ms=4.6, color=col, mec="white", mew=0.5, zorder=5, ls="none")
            xlo, xhi = min(xlo, sl), max(xhi, sh)
        ax.set_title(name, loc="left", fontsize=8, fontweight="bold", pad=17)
        ax.set_xlabel("saving vs run-now (% of emissions)")
        ax.set_ylim(-0.6, len(ARM_ORDER) - 0.4)
        ax.set_xlim(xlo - 0.35, xhi + 0.45)
        f = ph("PH4", tr, "w", "S12", "runnow_g_per_kwh", "est")
        sec = ax.secondary_xaxis("top", functions=(lambda x, f=f: x * f / 100.0, lambda y, f=f: y * 100.0 / f))
        sec.set_xlabel("absolute saving (g CO$_2$e/kWh)", fontsize=7)
        sec.tick_params(labelsize=7, width=0.6, length=2.5)
    axs[0].set_yticks(ys)
    axs[0].set_yticklabels([ARMS[a][0] for a in ARM_ORDER])
    for ax in axs[1:]:
        ax.tick_params(axis="y", length=0)
    fig.legend(handles=[
        Line2D([], [], color="#777777", lw=6, alpha=0.55, solid_capstyle="butt", label="calendar interval (fixed set of 42 BAs)"),
        Line2D([], [], color=INK, lw=0.9, marker="|", ms=7, label="synchronized-week interval (post-hoc)")],
        loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.55, 0.0), fontsize=7)
    fig.subplots_adjust(left=0.215, right=0.99, top=0.80, bottom=0.17, wspace=0.12)
    save(fig, 6)
    cap(6, f"Realized saving at 12 h slack. The forecast-and-request arm (D) saves {pct(sav('PM100', 12, 'lgbm|req'))} % on PM100 against {pct(sav('PM100', 12, 'oracle|act'))} % "
           f"for the oracle with actual runtime. Bars: calendar interval; whiskers: synchronized-week interval; 42 BAs, TEST year.",
        "TEST.PM100.w.S12.saving.lgbm|req; TEST.PM100.w.S12.saving.oracle|act; intervals TEST.<tr>.w.S12.saving_lo/_hi.<arm> and posthoc.PH1arm.<tr>.w.S12.<arm>.sync_lo/_hi (tables/ledger_TEST_posthoc_armsync.csv); top axis posthoc.PH4.<tr>.w.S12.runnow_g_per_kwh.est")


# ---------------------------------------------------------------- Figure 7 (Shapley)
def fig7():
    fig, axs = plt.subplots(1, 2, figsize=(W2, 72 * MM), gridspec_kw=dict(width_ratios=[1.0, 1.15]))
    cF, cR = "#E69F00", "#009E73"
    ys = np.arange(3)[::-1]
    ax = axs[0]
    style_x_grid(ax)
    rows = []
    for y, (tr, n) in zip(ys, TRACES):
        f = 100 * ph("PH2", tr, "w", "S12", "forecast", "est")
        r = 100 * ph("PH2", tr, "w", "S12", "runtime", "est")
        gap = 100 * g(LT, f"TEST.{tr}.w.S12.shapley.gap")
        assert abs(f + r - gap) < 1e-6, (tr, f + r, gap)
        sh_r = ph("PH2", tr, "w", "S12", "runtime_share", "est")
        ax.barh(y, f, height=0.5, color=cF, ec="white", lw=0.8, zorder=3)
        ax.barh(y, r, left=f, height=0.5, color=cR, ec="white", lw=0.8, zorder=3)
        ax.text(f / 2, y, f"{f:.2f}", ha="center", va="center", fontsize=7, color=INK, zorder=4)
        ax.text(f + r / 2, y, f"{r:.2f}", ha="center", va="center", fontsize=7, color=INK, zorder=4)
        ax.text(gap + 0.08, y + 0.02, f"gap {gap:.2f}\nruntime {sig2(100 * sh_r)} %", ha="left", va="center", fontsize=7, color=INK)
        rows.append((tr, f, r, gap))
    ax.set_yticks(ys)
    ax.set_yticklabels([TR_SHORT[t] for t, _ in TRACES])
    ax.set_ylim(-0.7, 2.6)
    ax.set_xlim(0, max(r_[3] for r_ in rows) * 1.6)
    ax.set_xlabel("oracle + actual runtime minus forecast-and-request arm (D)\n(percentage points of run-now emissions)")
    panel_letter(ax, "(a)", dx=-0.17, dy=1.02)
    ax2 = axs[1]
    style_x_grid(ax2)
    ax2.axvline(0, color=INK2, lw=0.7, zorder=1)
    yl, ylab = [], []
    for gi, (tr, n) in enumerate(TRACES):
        y0 = 2 - gi
        for off, (term, col, mk) in zip((0.26, 0.0, -0.26), (("forecast", cF, "o"), ("runtime", cR, "s"), ("runtime_minus_forecast", "#000000", "D"))):
            e = 100 * ph("PH2", tr, "w", "S12", term, "est")
            cl, ch_ = 100 * ph("PH2", tr, "w", "S12", term, "cal_lo"), 100 * ph("PH2", tr, "w", "S12", term, "cal_hi")
            sl, sh_ = 100 * ph("PH2", tr, "w", "S12", term, "sync_lo"), 100 * ph("PH2", tr, "w", "S12", term, "sync_hi")
            y = y0 + off
            ax2.barh(y, ch_ - cl, left=cl, height=0.2, color=col, alpha=0.45, lw=0, zorder=3)
            hline_cap(ax2, sl, sh_, y, INK, lw=0.8, cap_h=0.07, z=4)
            ax2.plot(e, y, marker=mk, ms=4.6, color=col, mec="white", mew=0.5, ls="none", zorder=5)
    ax2.set_yticks(ys)
    ax2.set_yticklabels([TR_SHORT[t] for t, _ in TRACES])
    ax2.set_ylim(-0.7, 2.6)
    ax2.set_xlabel("term and difference, with 95 % intervals\n(percentage points of run-now emissions)")
    panel_letter(ax2, "(b)", dx=-0.17, dy=1.02)
    fig.legend(handles=[Line2D([], [], color=cF, marker="o", lw=0, ms=5, label="forecast term (forecast instead of oracle signal)"),
                        Line2D([], [], color=cR, marker="s", lw=0, ms=5, label="runtime term (requested walltime instead of actual)"),
                        Line2D([], [], color="#000000", marker="D", lw=0, ms=5, label="runtime minus forecast"),
                        Line2D([], [], color="#777777", lw=6, alpha=0.55, solid_capstyle="butt", label="calendar interval"),
                        Line2D([], [], color=INK, lw=0.8, marker="|", ms=6, label="synchronized-week interval")],
               loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.0), fontsize=7)
    fig.subplots_adjust(left=0.085, right=0.985, top=0.93, bottom=0.37, wspace=0.16)
    save(fig, 7)
    sPM = sig2(100 * ph("PH2", "PM100", "w", "S12", "runtime_share", "est"))
    sKT = sig2(100 * ph("PH2", "KIT_FH2", "w", "S12", "runtime_share", "est"))
    sFD = sig2(100 * (1 - ph("PH2", "FDATA", "w", "S12", "runtime_share", "est")))
    # direction of the difference, as stated in the caption (runtime larger on PM100, KIT FH2; forecast larger on F-DATA)
    assert ph("PH2", "PM100", "w", "S12", "runtime_minus_forecast", "sync_lo") > 0 and ph("PH2", "KIT_FH2", "w", "S12", "runtime_minus_forecast", "sync_lo") > 0
    assert ph("PH2", "FDATA", "w", "S12", "runtime_minus_forecast", "cal_lo") < 0 < ph("PH2", "FDATA", "w", "S12", "runtime_minus_forecast", "cal_hi")
    cap(7, f"Shapley split of the gap between the oracle and the forecast-and-request arm, 12 h slack: runtime term larger on PM100 ({sPM} %) and KIT FH2 ({sKT} %), comparable on F-DATA "
           f"(difference interval includes zero). Post-hoc.",
        "posthoc.PH2.<tr>.w.S12.{forecast,runtime,runtime_minus_forecast}.{est,cal_lo,cal_hi,sync_lo,sync_hi}; posthoc.PH2.<tr>.w.S12.runtime_share.est; TEST.<tr>.w.S12.shapley.gap")


# ---------------------------------------------------------------- Figure 8 (slack, delay)
def fig8():
    arms = ["oracle|act", "oracle|req", "lgbm|act", "lgbm|req", "lgbm|pred"]
    fig = plt.figure(figsize=(W2, 150 * MM))
    gs = fig.add_gridspec(2, 3, left=0.065, right=0.99, top=0.925, bottom=0.2, hspace=0.62, wspace=0.28)
    axs = [fig.add_subplot(gs[0, j]) for j in range(3)]
    xs = np.arange(len(SLACKS))
    for ax, (tr, name) in zip(axs, TRACES):
        ax.grid(axis="y", zorder=0)
        ax.set_axisbelow(True)
        for arm in arms:
            lab, col, mk = ARMS[arm]
            v = np.array([100 * sav(tr, S, arm) for S in SLACKS])
            lo = np.array([100 * sav(tr, S, arm, "_lo") for S in SLACKS])
            hi = np.array([100 * sav(tr, S, arm, "_hi") for S in SLACKS])
            ax.fill_between(xs, lo, hi, color=col, alpha=0.30, lw=0, zorder=2)
            ax.plot(xs, v, color=col, lw=1.4, marker=mk, ms=4.6, mec="white", mew=0.5, zorder=3, ls="-" if arm.startswith("lgbm") else (0, (4, 1.5)))
        ax.axhline(0, color=INK2, lw=0.7)
        ax.set_xticks(xs)
        ax.set_xticklabels([str(s) for s in SLACKS])
        ax.set_xlabel("slack window S (h)")
        ax.set_title(name, loc="left", fontsize=8, fontweight="bold")
        ax.set_xlim(-0.2, len(SLACKS) - 0.8)
        ax.set_ylim(bottom=0)
        ax.set_ylabel("saving vs run-now (%)")
    panel_letter(axs[0], "(a)", dx=-0.2, dy=1.16)
    d = pd.read_csv(os.path.join(TAB, "secondary_delay.csv"))
    d = d[d.S == 12]
    axb = [fig.add_subplot(gs[1, j]) for j in range(3)]
    slopes = {}
    for ax, (tr, name) in zip(axb, TRACES):
        ax.grid(zorder=0)
        ax.set_axisbelow(True)
        sub = d[d.trace == tr].set_index("arm")
        xm = sub["mean_delay_h"].max() * 1.12
        for arm in ARM_ORDER:
            lab, col, mk = ARMS[arm]
            ax.plot(sub.loc[arm, "mean_delay_h"], 100 * sav(tr, 12, arm), marker=mk, ms=6, color=col, mec="white", mew=0.6, ls="none", zorder=3)
        sl = 100 * sav(tr, 12, "lgbm|req") / sub.loc["lgbm|req", "mean_delay_h"]
        slopes[tr] = sl
        ax.plot([0, xm], [0, sl * xm], color=ARMS["lgbm|req"][1], lw=0.8, ls=(0, (4, 2)), zorder=2)
        ax.text(0.04, 0.96, f"D (dashed):\n{sl:.2f} pp per hour of delay", transform=ax.transAxes, fontsize=7, color=INK, ha="left", va="top")
        ax.axhline(0, color=INK2, lw=0.7)
        ax.set_xlabel("mean start delay (h)")
        ax.set_ylabel("saving vs run-now (%)")
        ax.set_title(name, loc="left", fontsize=8, fontweight="bold")
        ax.set_xlim(0, xm)
        ax.set_ylim(bottom=min(0, ax.get_ylim()[0]))
    panel_letter(axb[0], "(b)", dx=-0.2, dy=1.16)
    hs = [Line2D([], [], color=ARMS[a][1], marker=ARMS[a][2], ms=5.5, lw=1.4 if a in arms else 0, ls=("-" if a.startswith("lgbm") else (0, (4, 1.5))) if a in arms else "none",
                 label=flat(ARMS[a][0]).replace(" (upper bound)", "").replace(" (forecast-and-request, D)", " (D)")) for a in ARM_ORDER]
    fig.legend(handles=hs, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.0))
    save(fig, 8)
    dd = d[d.trace == "PM100"].set_index("arm")["mean_delay_h"]
    cap(8, f"(a) Saving rises with slack; D stays below the oracle (PM100: {pct(sav('PM100', 2, 'lgbm|req'))} % at 2 h, "
           f"{pct(sav('PM100', 24, 'lgbm|req'))} % at 24 h). (b) Saving against mean delay, 12 h. Bands: calendar intervals.",
        "TEST.PM100.w.S2.saving.lgbm|req; TEST.PM100.w.S24.saving.lgbm|req; bands TEST.<tr>.w.S<S>.saving_lo/_hi.<arm>; delay tables/secondary_delay.csv (S=12; saving per hour derived in code)")


# ---------------------------------------------------------------- Figure 9 (per-BA)
def fig9():
    d = json.load(open(os.path.join(ROOT, "results", "analysis_TEST_PM100_w.json")))["slacks"]["12"]["per_ba"]
    pat = re.compile(r"^posthoc\.PH3\.PM100\.w\.S12\.([A-Z0-9]+)\.H2_(est|lo|hi)$")
    per = {}
    for k, v in LPH.items():
        mt = pat.match(k)
        if mt:
            per.setdefault(mt.group(1), {})[mt.group(2)] = v
    assert len(per) == 42, len(per)
    for b in per:
        assert abs(per[b]["est"] - d[b]["H2_est"]) < 1e-9, b
        assert abs(per[b]["lo"] - d[b]["H2_lo"]) < 1e-9, b
    bas = sorted(per, key=lambda b: per[b]["est"])
    n = len(bas)
    fig = plt.figure(figsize=(140 * MM, 192 * MM))
    ax = fig.add_axes([0.1, 0.275, 0.88, 0.7])
    axb = fig.add_axes([0.1, 0.165, 0.88, 0.075], sharex=ax)
    ax.grid(axis="x", zorder=0)
    ax.set_axisbelow(True)
    col, colo = ARMS["lgbm|req"][1], ARMS["oracle|act"][1]
    for i, b in enumerate(bas):
        e, lo, hi = 100 * per[b]["est"], 100 * per[b]["lo"], 100 * per[b]["hi"]
        hline_cap(ax, lo, hi, i, col, lw=1.3, cap_h=0.28, z=3)
        ax.plot(e, i, "o", color=col, ms=4.0, mec="white", mew=0.5, zorder=4)
        ax.plot(100 * d[b]["saving_oracle_act"], i, "D", mfc="white", mec=colo, mew=0.9, ms=3.8, zorder=4)
    ax.axvline(0, color=INK2, lw=0.7)
    pooled = 100 * g(LT, "TEST.PM100.w.S12.H2_runtime_penalty.est")
    ax.axvline(pooled, color=col, lw=0.9, ls=(0, (4, 2)), zorder=2)
    ax.set_yticks(range(n))
    ax.set_yticklabels(bas, fontsize=7)
    ax.set_ylim(-0.8, n - 0.2)
    ax.tick_params(axis="y", length=0)
    plt.setp(ax.get_xticklabels(), visible=False)
    ax.tick_params(axis="x", length=0)
    panel_letter(ax, "(a)", dx=-0.1, dy=1.005)
    est = np.array([100 * per[b]["est"] for b in bas])
    axb.grid(axis="x", zorder=0)
    axb.set_axisbelow(True)
    axb.boxplot(est, vert=False, widths=0.55, whis=1.5, patch_artist=True, boxprops=dict(facecolor=col, alpha=0.45, lw=0.7, edgecolor=INK),
                medianprops=dict(color=INK, lw=1.0), whiskerprops=dict(lw=0.7), capprops=dict(lw=0.7),
                flierprops=dict(marker="o", ms=3, mfc="none", mec=INK, mew=0.6))
    axb.set_yticks([])
    axb.axvline(0, color=INK2, lw=0.7)
    axb.axvline(pooled, color=col, lw=0.9, ls=(0, (4, 2)), zorder=2)
    axb.set_xlabel("percentage points of run-now emissions")
    panel_letter(axb, "(b)", dx=-0.1, dy=1.0)
    fig.legend(handles=[
        Line2D([], [], color=col, marker="o", lw=1.3, ms=4, label="runtime penalty H2: estimate and 95 % within-BA interval"),
        Line2D([], [], color=col, lw=0.9, ls=(0, (4, 2)), label="pooled H2 over the 42 BAs"),
        Line2D([], [], color=colo, marker="D", mfc="white", mew=0.9, lw=0, ms=4, label="oracle + actual runtime saving (BA ceiling)")],
        loc="lower center", ncol=1, frameon=False, bbox_to_anchor=(0.55, 0.0), fontsize=7)
    save(fig, 9)
    s = lambda k: int(ph("PH3", "PM100", "w", "S12", "summary", k))  # noqa: E731
    cap(9, f"Per-BA runtime penalty, PM100, 12 h slack: positive in {s('pos')} of {s('n')} BAs, interval above zero in {s('lo_gt0')}. "
           f"(a) 95 % within-BA bootstrap intervals; (b) box plot, whiskers at 1.5 times the interquartile range.",
        "posthoc.PH3.PM100.w.S12.summary.{pos,n,lo_gt0}; posthoc.PH3.PM100.w.S12.<BA>.H2_{est,lo,hi}; oracle saving results/analysis_TEST_PM100_w.json slacks.12.per_ba")


# ---------------------------------------------------------------- Figure 10 (explaining the saving)
def _char():
    ch = pd.read_csv(os.path.join(TAB, "secondary_ba_character_TEST.csv"), index_col=0)
    pb = pd.read_csv(os.path.join(TAB, "secondary_per_ba_S12.csv"))
    pb = pb[pb.trace == "PM100"].set_index("ba")
    sp = pd.read_csv(os.path.join(TAB, "secondary_spearman_character.csv"))
    sp = sp[(sp.trace == "PM100") & (sp.S == 12) & (sp.weight == "w") & (sp.character_source == "TEST_hours")]
    return ch.join(pb, how="inner"), sp


def _scatter_ax(ax, fig, xcol, ycol, stat, char, xlabel, ylabel, xscale=1.0, label_n=3, cmapchar=None,
                offs=((-4, 3, "right"), (-4, 6, "right"), (0, -10, "center"))):
    df, sp = _char()
    row = sp[(sp.stat == stat) & (sp.character == char)].iloc[0]
    ax.grid(zorder=0)
    ax.set_axisbelow(True)
    cm = "Oranges" if char != "share_solar" else "Blues"
    cvals = df["share_solar"] * 100 if char != "share_solar" else df["share_wind"] * 100
    sc_ = ax.scatter(df[xcol] * xscale, df[ycol] * 100, c=cvals, cmap=cm, s=22, edgecolor=INK, linewidth=0.5, zorder=3, vmin=0)
    cb = fig.colorbar(sc_, ax=ax, pad=0.02, fraction=0.06)
    cb.set_label("solar share (%)" if char != "share_solar" else "wind share (%)", fontsize=7)
    cb.ax.tick_params(labelsize=7, width=0.5, length=2)
    cb.outline.set_linewidth(0.5)
    ax.margins(x=0.16, y=0.08)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.text(0.04, 0.97, f"Spearman $\\rho$ = {row.rho:.2f}\n$n$ = {int(row.n_ba)} BAs", transform=ax.transAxes, va="top", ha="left", fontsize=7,
            bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.2))
    for i_, b in enumerate((df[ycol]).sort_values(ascending=False).index[:label_n]):
        ax.annotate(b, (df.loc[b, xcol] * xscale, df.loc[b, ycol] * 100), xytext=offs[i_ % 3][:2], textcoords="offset points",
                    fontsize=7, color=INK, ha=offs[i_ % 3][2])
    return row


def fig10():
    r = pd.read_csv(os.path.join(TAB, "secondary_retained_share.csv"))
    r = r[(r.unit == "pooled") & (r.S == 12) & (r.weight == "w")]
    classes = [("lt1", "< 1 h"), ("1-4", "1-4 h"), ("4-12", "4-12 h"), ("ge12", "≥ 12 h"), ("all", "all")]
    fig = plt.figure(figsize=(W2, 80 * MM))
    axa = fig.add_axes([0.06, 0.2, 0.29, 0.66])
    axb = fig.add_axes([0.43, 0.2, 0.2, 0.66])
    axc = fig.add_axes([0.735, 0.2, 0.195, 0.66])
    cq = ARMS["lgbm|req"][1]
    axa.grid(axis="y", zorder=0)
    axa.set_axisbelow(True)
    x = np.arange(len(classes))
    alph = {"PM100": 1.0, "FDATA": 0.62, "KIT_FH2": 0.34}
    for k, (tr, name) in enumerate(TRACES):
        sub = r[r.trace == tr].set_index("class")
        q = [sub.loc[c, "retained_lgbm_req"] for c, _ in classes]
        axa.bar(x + (k - 1) * 0.27, q, 0.26, color=cq, alpha=alph[tr], zorder=3, ec="white", lw=0.5, label=name)
    axa.axvline(3.5, color=GRID, lw=0.8, zorder=1)
    axa.set_xticks(x)
    axa.set_xticklabels([c[1] for c in classes])
    axa.set_xlabel("job-length class")
    axa.set_ylabel("share of oracle saving retained")
    axa.set_ylim(0, 1.0)
    axa.legend(loc="upper right", frameon=False, fontsize=7, ncol=1, borderaxespad=0.1)
    panel_letter(axa, "(a)", dx=-0.2, dy=1.05)
    r1 = _scatter_ax(axb, fig, "median_daily_range", "oracle_act_saving_S12", "oracle_act_saving", "median_daily_range",
                     "median daily range (g CO$_2$e/kWh)", "oracle saving, actual runtime (%)")
    panel_letter(axb, "(b)", dx=-0.3, dy=1.05)
    r2 = _scatter_ax(axc, fig, "share_solar", "runtime_penalty_S12", "runtime_penalty", "share_solar",
                     "solar share of generation (%)", "runtime penalty H2 (pp)", xscale=100.0,
                     offs=((-4, 3, "right"), (-4, 6, "right"), (0, 5, "center")))
    panel_letter(axc, "(c)", dx=-0.3, dy=1.05)
    save(fig, 10)
    sub = r[r.trace == "PM100"].set_index("class")
    for c in ("lt1", "ge12"):
        kk = f"TEST.PM100.w.S12.retained.lgbm_req.class_{c}"
        if kk in LSEC:
            assert abs(LSEC[kk] - sub.loc[c, "retained_lgbm_req"]) < 1e-9, kk
    cap(10, f"(a) PM100: D keeps {pct(sub.loc['lt1', 'retained_lgbm_req'], 0)} % of the oracle saving under 1 h and "
            f"{pct(sub.loc['ge12', 'retained_lgbm_req'], 0)} % at 12 h or more. (b), (c) PM100 per BA: Spearman rho {r1.rho:.2f} and {r2.rho:.2f}. Descriptive.",
        "TEST.PM100.w.S12.retained.lgbm_req.class_lt1 / .class_ge12 (tables/secondary_retained_share.csv); tables/secondary_spearman_character.csv; tables/secondary_per_ba_S12.csv; tables/secondary_ba_character_TEST.csv")


# ---------------------------------------------------------------- Figure 11 (X1 runtime accuracy; pending until the X1 ledger exists)
def fig11():
    fn = os.path.join(SENS_DIR, "ledger_TEST_sens_x1.csv")
    fig, axs = plt.subplots(1, 3, figsize=(W2, 72 * MM), sharey=False)
    have = os.path.exists(fn)
    if have:
        L = load_ledger_path(fn)
        pat = re.compile(r"^sens\.x1\.(PM100|FDATA|KIT_FH2)\.w\.S12\.saving(_lo|_hi)?\.(oracle|lgbm)\|(act|m[0-9.]+|ln|lnmu|req|pred)$")
        D = {}
        for k, v in L.items():
            mt = pat.match(k)
            if mt:
                D[(mt.group(1), mt.group(3), mt.group(4), (mt.group(2) or "")[1:] or "est")] = v
        have = len(D) > 0
    if not have:
        for ax, (tr, name) in zip(axs, TRACES):
            ax.set_title(name, loc="left", fontsize=8, fontweight="bold")
            pending_box(ax, "pending: X1 runtime-estimate sweep\n(tables/ledger_TEST_sens_x1.csv)\nexploratory, post-freeze")
        fig.subplots_adjust(left=0.04, right=0.99, top=0.9, bottom=0.08, wspace=0.12)
        save(fig, 11)
        cap(11, "Saving against runtime-estimate error (exploratory, post-freeze). Pending: the X1 sweep has not run; oracle and forecast signals, requested and predicted runtimes will be marked.",
            "pending: tables/ledger_TEST_sens_x1.csv keys sens.x1.<tr>.w.S12.saving[_lo|_hi].<oracle|lgbm>|<act|m*|req|pred>, sens.x1.<tr>.logerr_median.<rt>")
        return "pending"
    sigs = [("oracle", ARMS["oracle|act"][1], "oracle signal", "o"), ("lgbm", ARMS["lgbm|act"][1], "forecast signal", "^")]
    for ax, (tr, name) in zip(axs, TRACES):
        ax.grid(zorder=0)
        ax.set_axisbelow(True)
        for sg, col, lab, mk in sigs:
            pts = []
            for rt in {k[2] for k in D if k[0] == tr and k[1] == sg and re.match(r"^(act|m[0-9.]+)$", k[2])}:
                me = 0.0 if rt == "act" else float(L[f"sens.x1.{tr}.logerr_median.{rt}"])
                pts.append((me / np.log(2), 100 * D[(tr, sg, rt, "est")], 100 * D[(tr, sg, rt, "lo")], 100 * D[(tr, sg, rt, "hi")]))
            pts.sort()
            xx, yy, lo, hi = map(np.array, zip(*pts))
            ax.fill_between(xx, lo, hi, color=col, alpha=0.2, lw=0)
            ax.plot(xx, yy, color=col, marker=mk, ms=4, lw=1.3, mec="white", mew=0.5, label=f"{lab}, estimate = m x actual")
            for rt, mrk in (("req", "s"), ("pred", "D")):
                if (tr, sg, rt, "est") in D:
                    ax.plot(float(L[f"sens.x1.{tr}.logerr_median.{rt}"]) / np.log(2), 100 * D[(tr, sg, rt, "est")], mrk, mfc="white", mec=col, mew=1.2, ms=6, zorder=5)
        ax.axhline(0, color=INK2, lw=0.7)
        ax.set_title(name, loc="left", fontsize=8, fontweight="bold")
        ax.set_xlabel("median log$_2$(estimate / actual runtime)")
        ax.set_ylabel("saving vs run-now (%)")
    fig.legend(handles=[Line2D([], [], color=c, marker=m, lw=1.3, ms=4, label=f"{l}, estimate = m x actual") for _, c, l, m in sigs] +
               [Line2D([], [], color=INK2, marker="s", mfc="white", lw=0, ms=6, label="requested walltime"),
                Line2D([], [], color=INK2, marker="D", mfc="white", lw=0, ms=6, label="history-predicted runtime")],
               loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.0), fontsize=7)
    fig.subplots_adjust(left=0.06, right=0.99, top=0.92, bottom=0.27, wspace=0.28)
    save(fig, 11)
    cap(11, "Saving against runtime-estimate error (exploratory, post-freeze). The requested walltime and the history prediction are marked on each curve; 12 h slack, 42 BAs, calendar intervals.",
        "sens.x1.<tr>.w.S12.saving[_lo|_hi].<oracle|lgbm>|<act|m*|req|pred>; sens.x1.<tr>.logerr_median.<rt> (tables/ledger_TEST_sens_x1.csv)")
    return "final"


# ---------------------------------------------------------------- Figure 12 (interval types and robustness variants)
def fig12():
    hs = [("H1", "H1_deployable_saving", "H1: saving of D"), ("H2", "H2_runtime_penalty", "H2: runtime penalty"),
          ("H3", "H3_prediction_recovery", "H3: prediction recovery")]
    S = {}
    for nm in ("s1", "s2", "s2b", "s3a", "s3b", "s4", "shift", "x7", "x9"):
        fn = os.path.join(SENS_DIR, f"ledger_TEST_sens_{nm}.csv")
        S[nm] = load_ledger_path(fn) if os.path.exists(fn) else {}

    def trip(L, base, a="est", b="lo", c="hi"):
        ks = [f"{base}.{a}", f"{base}.{b}", f"{base}.{c}"] if base else None
        if ks and all(k in L for k in ks):
            return tuple(L[k] for k in ks)
        return None

    def trip_h(L, pre, tr, hn, mid=""):
        return trip(L, f"{pre}.{tr}.w.S12.{mid}{hn}")

    def v_cal(tr, hk, hn):
        return (ph("PH1", tr, "w", "S12", hk, "est"), ph("PH1", tr, "w", "S12", hk, "cal_lo"), ph("PH1", tr, "w", "S12", hk, "cal_hi"))

    def v_sync(tr, hk, hn):
        return (ph("PH1", tr, "w", "S12", hk, "est"), ph("PH1", tr, "w", "S12", hk, "sync_lo"), ph("PH1", tr, "w", "S12", hk, "sync_hi"))

    def v_ts(tr, hk, hn):
        return hyp(LT, "TEST", tr, 12, hn, ts=True)

    def v_nl(tr, hk, hn):
        return hyp(LNL, "TEST_nearlimit", tr, 12, hn)

    def v_u(tr, hk, hn):
        return hyp(LT, "TEST", tr, 12, hn, w="u")

    def v_s1(tr, hk, hn):
        nm = {"H1": "D_saving_lgbm_req"}.get(hk, hn)
        b = f"sens.s1.{tr}.w.S12.{nm}"
        return trip(S["s1"], b, "frozen_est", "tot_lo", "tot_hi")

    def v_pre(nm, mid=""):
        return lambda tr, hk, hn: trip_h(S[nm], f"sens.{nm}", tr, hn, mid)

    def v_shift(z):
        def f(tr, hk, hn):
            L = S["shift"]
            b = f"sens.shift.{tr}.w.S12.{z}"
            if hk == "H1":
                return tuple(L[f"{b}.saving{s}.lgbm|req"] for s in ("", "_lo", "_hi")) if f"{b}.saving.lgbm|req" in L else None
            return trip(L, f"{b}.contrast.{'H2_penalty' if hk == 'H2' else 'H3_recovery'}")
        return f

    def v_x7(tr, hk, hn):
        L = S["x7"]
        b = f"sens.x7.{tr}.w.S12"
        if hk == "H1":
            return tuple(L[f"{b}.saving{s}.lgbm|req"] for s in ("", "_lo", "_hi")) if f"{b}.saving.lgbm|req" in L else None
        return trip(L, f"{b}.contrast.{hn}")

    def v_x9(tr, hk, hn):
        L = S["x9"]
        b = f"sens.x9.{tr}.w.S12"
        if hk == "H1" and f"{b}.saving.cap:lgbm|req" in L:
            return tuple(L[f"{b}.saving{s}.cap:lgbm|req"] for s in ("", "_lo", "_hi"))
        return None

    # (label, group, getter)
    rows = [
        ("calendar interval", 0, v_cal), ("synchronized-week interval", 0, v_sync), ("two-stage interval (BAs, then blocks)", 0, v_ts),
        ("near-limit jobs excluded", 1, v_nl), ("unweighted (1 kW per job)", 1, v_u),
        ("S1 workload-sample interval", 2, v_s1),
        ("S2 data latency 6 h", 2, v_pre("s2", "k6.")), ("S2b data latency 24 h", 2, v_pre("s2b", "k24.")),
        ("S3a direct emission factors", 2, v_pre("s3a")), ("S3b oil factor 1116 g/kWh", 2, v_pre("s3b")),
        ("S4 TIMEOUT jobs included", 2, v_pre("s4")),
        ("arrivals shifted -3 h", 2, v_shift("m3")), ("arrivals shifted +3 h", 2, v_shift("p3")),
        ("X7 fossil-only proxy signal", 2, v_x7), ("X9 capacity cap (H1 only)", 2, v_x9),
    ]
    groups = {0: "interval type (frozen estimate)", 1: "frozen variants", 2: "post-freeze, exploratory"}
    tmk = {"PM100": ("o", "#000000"), "FDATA": ("s", "#555555"), "KIT_FH2": ("^", "#8a8a8a")}
    toff = {"PM100": 0.27, "FDATA": 0.0, "KIT_FH2": -0.27}
    # row positions (top to bottom), a header row before each group
    y = 0.0
    ypos, ghdr = [], []
    last_g = None
    for lab, gi, fn in rows:
        if gi != last_g:
            y -= 0.9
            ghdr.append((y, gi))
            y -= 0.1
            last_g = gi
        y -= 1.0
        ypos.append(y)
    fig, axs = plt.subplots(1, 3, figsize=(W2, 165 * MM), sharey=True)
    ntot = nzero = 0
    for ax, (hk, hn, ht) in zip(axs, hs):
        style_x_grid(ax)
        ax.axvline(0, color=INK2, lw=0.7, zorder=1)
        top_ex = [yy for (yy, g_) in ghdr if g_ == 2][0] + 0.4   # band starts below the last frozen row (its lowest marker sits at +0.63)
        ax.axhspan(ypos[-1] - 0.6, top_ex, color="#f3f3f3", zorder=0, lw=0)
        for (lab, gi, fn), yy in zip(rows, ypos):
            for tr, _ in TRACES:
                try:
                    r = fn(tr, hk, hn)
                except KeyError:
                    r = None
                if r is None or any(v is None for v in r):
                    continue
                e, lo, hi = r
                ntot += 1
                nzero += int(lo > 0)
                mk, col = tmk[tr]
                hline_cap(ax, 100 * lo, 100 * hi, yy + toff[tr], col, lw=0.9, cap_h=0.1, z=3)
                ax.plot(100 * e, yy + toff[tr], marker=mk, ms=3.8, color=col, mec="white", mew=0.4, ls="none", zorder=5)
        ax.set_title(ht, loc="left", fontsize=8, fontweight="bold")
        ax.set_xlabel("percentage points")
        ax.set_ylim(ypos[-1] - 0.75, 0.3)
        ax.margins(x=0.04)
    for ax in axs:
        xl = ax.get_xlim()
        ax.set_xlim(min(xl[0], 0 - 0.02 * (xl[1] - xl[0])), xl[1])
    axs[0].set_yticks(ypos)
    axs[0].set_yticklabels([r[0] for r in rows], fontsize=7)
    axs[0].tick_params(axis="y", length=0)
    for yy, gi in ghdr:
        axs[0].text(-0.02, yy, groups[gi], transform=axs[0].get_yaxis_transform(), ha="right", va="center", fontsize=7, fontweight="bold")
    fig.legend(handles=[Line2D([], [], color=tmk[t][1], marker=tmk[t][0], ms=4.5, lw=0.9, label=n) for t, n in TRACES],
               loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.6, 0.0), fontsize=7)
    fig.subplots_adjust(left=0.235, right=0.99, top=0.96, bottom=0.085, wspace=0.12)
    save(fig, 12)
    print("fig12 intervals drawn", ntot, "lower bound > 0:", nzero, flush=True)
    assert ntot == nzero, (ntot, nzero)
    cap(12, "Interval types and robustness variants for H1 to H3, 12 h slack. All drawn intervals exclude zero. Shaded rows are post-freeze and exploratory; blank means not run on that trace.",
        "posthoc.PH1.<tr>.w.S12.{H1,H2,H3}.{est,cal_lo,cal_hi,sync_lo,sync_hi}; TEST.<tr>.w.twostage.S12.H*; TEST_nearlimit.*, TEST.<tr>.u.*; sens.s1.<tr>.w.S12.{D_saving_lgbm_req,H2_runtime_penalty,H3_prediction_recovery}.{frozen_est,tot_lo,tot_hi}; sens.s2.<tr>.w.S12.k6.H*; sens.s2b.<tr>.w.S12.k24.H*; sens.s3a|s3b|s4.<tr>.w.S12.H*; sens.shift.PM100.w.S12.{m3,p3}.*; sens.x7.<tr>.w.S12.*; sens.x9.PM100.w.S12.saving.cap:lgbm|req")
    return "final"


# ---------------------------------------------------------------- Figure 13 (frozen variants)
def fig13():
    hs = [("H1_deployable_saving", "H1: saving of D"), ("H2_runtime_penalty", "H2: runtime penalty"),
          ("H3_prediction_recovery", "H3: prediction recovery")]
    variants = [
        ("primary: fixed 42 BAs", LT, "TEST", "w", False, "o", "#000000"),
        ("two-stage bootstrap", LT, "TEST", "w", True, "s", "#444444"),
        ("near-limit jobs excluded", LNL, "TEST_nearlimit", "w", False, "^", "#444444"),
        ("unweighted (1 kW per job)", LT, "TEST", "u", False, "v", "#444444"),
        ("DEV year", LDEV, "DEV", "w", False, "D", "#444444"),
    ]
    fig, axs = plt.subplots(3, 3, figsize=(W2, 128 * MM), sharey=True)
    ys = np.arange(len(variants))[::-1]
    for i, (tr, name) in enumerate(TRACES):
        for j, (h, ht) in enumerate(hs):
            ax = axs[i, j]
            style_x_grid(ax)
            ax.axvline(0, color=INK2, lw=0.7, zorder=1)
            for y, (vn, L, pre, w, ts, mk, c) in zip(ys, variants):
                e, lo, hi = hyp(L, pre, tr, 12, h, w=w, ts=ts)
                hline_cap(ax, 100 * lo, 100 * hi, y, c, lw=1.1, cap_h=0.14, z=3)
                ax.plot(100 * e, y, marker=mk, ms=4.6, color=c, mec="white", mew=0.5, zorder=4, ls="none")
            if i == 0:
                ax.set_title(ht, loc="left", fontsize=8, fontweight="bold")
            if i == 2:
                ax.set_xlabel("percentage points")
            if j == 0:
                ax.text(-0.09, 1.0, TR_SHORT[tr], transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, fontweight="bold")
            ax.set_ylim(-0.6, len(variants) - 0.4)
    axs[0, 0].set_yticks(ys)
    for i in range(3):
        axs[i, 0].set_yticklabels([v[0] for v in variants], fontsize=7)
        axs[i, 0].tick_params(axis="y", length=0)
    fig.subplots_adjust(left=0.215, right=0.99, top=0.95, bottom=0.13, wspace=0.1, hspace=0.3)
    fig.text(0.215, 0.012, "12 h slack, energy-weighted unless stated; bars are 95 % intervals of each variant's own bootstrap.", fontsize=7, color=INK2, va="bottom")
    save(fig, 13)
    pm = {}
    for nm, L, pre, w in (("p", LT, "TEST", "w"), ("n", LNL, "TEST_nearlimit", "w"), ("u", LT, "TEST", "u")):
        pm[nm] = [hyp(L, pre, tr, 12, "H1_deployable_saving", w=w)[0] for tr, _ in TRACES]
    # every H1 variant keeps the sign of the primary estimate on all three traces (stated in the caption)
    assert all(v > 0 for k in pm for v in pm[k])
    for L, pre, w in ((LT, "TEST", "w"), (LT, "TEST", "u"), (LNL, "TEST_nearlimit", "w"), (LDEV, "DEV", "w")):
        for tr, _ in TRACES:
            for h, _ in hs:
                assert hyp(L, pre, tr, 12, h, w=w)[0] > 0 and hyp(L, pre, tr, 12, h, w=w)[1] > 0, (pre, w, tr, h)
    cap(13, f"Frozen variants keep every contrast positive but change its size. PM100 saving of D: {pct(pm['p'][0])} % primary, {pct(pm['n'][0])} % without near-limit jobs, "
            f"{pct(pm['u'][0])} % unweighted. 12 h slack; 95 % intervals per variant.",
        "TEST.PM100.w.S12.H1_deployable_saving.est; TEST_nearlimit.PM100.w.S12.H1_deployable_saving.est; TEST.PM100.u.S12.H1_deployable_saving.est; all H1-H3 est/lo/hi in ledger_TEST, ledger_TEST_nearlimit, ledger_DEV for the three traces")


FIGS = {1: fig1w, 2: fig2, 3: fig3, 4: fig4, 5: fig5, 6: fig6, 7: fig7, 8: fig8, 9: fig9, 10: fig10, 11: fig11, 12: fig12, 13: fig13}

SOURCES = {
    1: "No data (schematic; illustrative curves are synthetic and labelled so). Arm definitions: research/PREREG.md s4.",
    2: "tables/ba_eligibility.csv (eligible BAs, mean_gen_mw); tables/secondary_ba_character_TEST.csv (median_daily_range, share_solar); mean intensity of the TEST year from data/derived/ci_clean.parquet (columns ba, utc, ci_clean; filtered rows). RAM gate 3 GB.",
    3: "data/derived/jobs_<trace>.parquet columns state, r_act_h, r_req_h with the frozen main filter (PREREG s2: COMPLETED, actual >= 1 min, 0 < requested <= 72 h); n and median checked against tables/ledger_data.csv data.<trace>.n_filtered_jobs and data.<trace>.median_ratio. RAM gate 3 GB.",
    4: "Illustration: data/derived/ci_clean.parquet (ERCO), data/derived/forecasts/lgbm/ERCO.npz, tables/ba_utc_offset.csv, plan_start of src/simcore.py (frozen planner); arrival 2025-11-17 18:00 local, 12 h slack, actual 1.5 h, requested 8 h. Not a result.",
    5: "tables/secondary_forecast_mae.csv (TEST, per BA, model, lead bucket) and tables/secondary_forecast_mae_summary.csv (mean checked).",
    6: "tables/ledger_TEST.csv TEST.<trace>.w.S12.saving[_lo|_hi].<arm> (calendar interval); tables/ledger_TEST_posthoc_armsync.csv posthoc.PH1arm.<trace>.w.S12.<arm>.{est,sync_lo,sync_hi} (new, src/posthoc_arm_sync.py); tables/ledger_TEST_posthoc.csv posthoc.PH4.<trace>.w.S12.runnow_g_per_kwh.est (top axis).",
    7: "tables/ledger_TEST_posthoc.csv posthoc.PH2.<trace>.w.S12.{forecast,runtime,runtime_minus_forecast,runtime_share}.{est,cal_lo,cal_hi,sync_lo,sync_hi}; check against tables/ledger_TEST.csv TEST.<trace>.w.S12.shapley.gap.",
    8: "tables/ledger_TEST.csv TEST.<trace>.w.S{2,6,12,24}.saving[_lo|_hi].<arm>; tables/secondary_delay.csv (S=12, mean_delay_h); saving per hour of delay derived in code.",
    9: "tables/ledger_TEST_posthoc.csv posthoc.PH3.PM100.w.S12.<BA>.H2_{est,lo,hi} and .summary.*; results/analysis_TEST_PM100_w.json slacks.12.per_ba.<BA>.{H2_est,H2_lo,saving_oracle_act} (consistency asserted); tables/ledger_TEST.csv TEST.PM100.w.S12.H2_runtime_penalty.est.",
    10: "tables/secondary_retained_share.csv (unit=pooled, S=12, weight=w, retained_lgbm_req); tables/secondary_per_ba_S12.csv; tables/secondary_ba_character_TEST.csv; tables/secondary_spearman_character.csv (PM100, S=12, w, TEST_hours).",
    11: "tables/ledger_TEST_sens_x1.csv (keys sens.x1.<trace>.w.S12.saving[_lo|_hi].<oracle|lgbm>|<act|m*|req|pred>, sens.x1.<trace>.logerr_median.<rt>); PENDING until that ledger exists: `py src/figures.py 11`.",
    12: "tables/ledger_TEST_posthoc.csv posthoc.PH1.<trace>.w.S12.{H1,H2,H3}; tables/ledger_TEST.csv TEST.<trace>.w.twostage.S12.H*; sensitivities tables/ledger_TEST_sens_s*.csv (PM100, S12); PENDING block until they exist: `py src/figures.py 12`.",
    13: "tables/ledger_TEST.csv (TEST.<trace>.w.S12.H*, .w.twostage., .u.), tables/ledger_TEST_nearlimit.csv (TEST_nearlimit.<trace>.w.S12.H*), tables/ledger_DEV.csv (DEV.<trace>.w.S12.H*). X4 load-concentration panel not built (waits for X4).",
}


def write_docs(done):
    prev = {}
    cp = os.path.join(FIG, "CAPTIONS.md")
    if os.path.exists(cp) and set(done) != set(FIGS):
        for blk in open(cp, encoding="utf-8").read().split("\n\n"):
            if blk.startswith("Figure "):
                try:
                    prev[int(blk.split(".")[0].split()[1])] = blk
                except ValueError:
                    pass
    for n in done:
        if n in CAPTIONS:
            c, keys = CAPTIONS[n]
            prev[n] = f"Figure {n}. {c}\n[ledger keys: {keys}]"
    with open(cp, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Figure captions (SPEC v1 numbering, 13 figures; numbers filled by src/figures.py from the ledgers, key in brackets; each caption is at most 35 words, asserted in code)\n\n")
        f.write("\n\n".join(prev[k] for k in sorted(prev)) + "\n")
    with open(os.path.join(FIG, "FIGURE_DATA.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# Figure data sources (Paper A, SPEC v1 numbering)\n\nPer figure: source files and key patterns. Built by `src/figures.py` (`py src/figures.py [n ...]`, default all 13).\n\n")
        for n in sorted(SOURCES):
            f.write(f"- Figure {n}: {SOURCES[n]}\n")


if __name__ == "__main__":
    req = [int(a) for a in sys.argv[1:]] or sorted(FIGS)
    done, status = [], {}
    for n in req:
        try:
            r = FIGS[n]()
            status[n] = r or "final"
            done.append(n)
            print("built", n, status[n], flush=True)
        except Skip as e:
            status[n] = "skipped"
            log(str(e))
    write_docs(done)
    log("status " + json.dumps(status))
