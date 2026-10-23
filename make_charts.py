"""Draw the findings charts (static PNG) into results/charts/.

Figure 1  Impacts per tonne: change against the fish-only pond, all 7 categories
Figure 2  Global warming by process
Figure 3  Where the nitrogen in the feed goes
Figure 4  Which process drives which impact (heatmap)
Figure 5  KPI scorecard
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from imtakpi import run_all, load, SYSTEMS, NAMES, CATEGORIES  # noqa: E402

OUT = ROOT / "results" / "charts"
OUT.mkdir(parents=True, exist_ok=True)
RES = run_all()
INV, NUT, LC = load()

COL = {"SI-IMTA": "#1D9E75", "SE-IMTA": "#378ADD", "SI-POLY": "#888780"}
INK, MUTED, GRID = "#2C2C2A", "#6B6A64", "#E4E2DA"
CAT_LABEL = {"GW": "Global warming", "TCED": "Cumulative energy demand", "NPPU": "Net primary production use",
             "AP": "Acidification", "EP": "Eutrophication", "LC": "Land competition", "WD": "Water dependence"}
SRC = "Source: INTEGRATE deliverable PI05#3 (IPMA, CTAQUA 2020)"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": "#B4B2A9", "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False})


def header(fig, title, subtitle):
    fig.text(0.01, 0.985, title, ha="left", va="top", fontsize=13, fontweight="bold", color=INK)
    fig.text(0.01, 0.925, subtitle, ha="left", va="top", fontsize=9.5, color=MUTED)


def footer(fig, text=SRC):
    fig.text(0.01, 0.01, text, ha="left", va="bottom", fontsize=8, color=MUTED)


def save(fig, name):
    fig.savefig(OUT / name, dpi=200, facecolor="white")
    plt.close(fig)
    print("written", name)


# ---------------------------------------------------------------- Figure 1
def fig_relative():
    fig, ax = plt.subplots(figsize=(9, 4.8))
    fig.subplots_adjust(left=0.27, right=0.95, top=0.78, bottom=0.13)
    header(fig, "1  IMTA lowers six of seven impacts; it needs more land",
           "Change per tonne of fish + oyster against the fish-only pond (semi-intensive polyculture = 0 %)")
    cats = CATEGORIES
    h = 0.36
    for j, s in enumerate(["SI-IMTA", "SE-IMTA"]):
        vals = [(RES[s]["totals"][c] / RES["SI-POLY"]["totals"][c] - 1) * 100 for c in cats]
        ys = [i + (j - 0.5) * h for i in range(len(cats))]
        ax.barh(ys, vals, h * 0.92, color=COL[s], label=NAMES[s])
        for y, v in zip(ys, vals):
            ax.text(v + (3 if v >= 0 else -3), y, f"{v:+.0f} %", va="center", ha="left" if v >= 0 else "right", fontsize=8.5, color=INK)
    ax.axvline(0, color=INK, lw=1)
    ax.set_yticks(range(len(cats)), [CAT_LABEL[c] for c in cats])
    ax.invert_yaxis()
    ax.set_xlim(-125, 135)
    ax.set_xticks([-100, -75, -50, -25, 0, 25, 50, 75, 100])
    ax.set_xticklabels([f"{x:+d} %" if x else "0" for x in ax.get_xticks().astype(int)])
    ax.xaxis.grid(True, color=GRID)
    ax.set_axisbelow(True)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.text(-62, len(cats) - 0.35, "← better than fish-only pond", ha="center", fontsize=8.5, color=MUTED)
    ax.text(62, len(cats) - 0.35, "worse →", ha="center", fontsize=8.5, color=MUTED)
    fig.legend(frameon=False, ncol=2, loc="upper left", bbox_to_anchor=(0.005, 0.89), fontsize=9.5)
    footer(fig, SRC + ", Annex 1")
    save(fig, "01_change_vs_fish_pond.png")


# ---------------------------------------------------------------- Figure 2
GROUPS = [("Feeds", ["Feeds"], "#BA7517"), ("Transport", ["Transports"], "#D85A30"),
          ("Energy (pumping, aeration)", ["Energy consumption"], "#534AB7"), ("Equipment", ["Equipment"], "#AFA9EC"),
          ("Other (buildings, vehicles,\nchemicals, fry)", ["Building impact", "Vehicle", "Chemical products", "Fry"], "#B4B2A9")]


def fig_gw():
    fig, ax = plt.subplots(figsize=(9, 5))
    fig.subplots_adjust(left=0.09, right=0.70, top=0.80, bottom=0.14)
    header(fig, "2  Feed is the largest source of greenhouse gases",
           "Global warming by process, kg CO2-eq per tonne of fish + oyster (share of the total in the bar)")
    for j, s in enumerate(SYSTEMS):
        tot = RES[s]["totals"]["GW"]
        bottom = 0
        for lab, procs, c in GROUPS:
            v = sum(LC["amount"]["GW"][s][p] for p in procs)
            ax.bar(j, v, 0.58, bottom=bottom, color=c, edgecolor="white", linewidth=0.8, label=lab if j == 0 else None)
            if v / tot >= 0.07:
                ax.text(j, bottom + v / 2, f"{v / tot:.0%}", ha="center", va="center", fontsize=9,
                        color="white" if c not in ("#AFA9EC", "#B4B2A9") else INK)
            bottom += v
        ax.text(j, tot + 50, f"{tot:,.0f}", ha="center", va="bottom", fontsize=11, fontweight="bold", color=INK)
    ax.set_xticks(range(3), [NAMES[s].replace(" pond ", "\npond ").replace(" fish ", "\nfish ") for s in SYSTEMS])
    ax.set_ylim(0, 3200)
    ax.set_ylabel("kg CO2-eq per tonne")
    ax.yaxis.grid(True, color=GRID)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", length=0)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], frameon=False, loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=9)
    footer(fig, SRC + ", Annex 1")
    save(fig, "02_global_warming_by_process.png")


# ---------------------------------------------------------------- Figure 3
def fig_nitrogen():
    fig, ax = plt.subplots(figsize=(9, 4.4))
    fig.subplots_adjust(left=0.27, right=0.97, top=0.80, bottom=0.25)
    header(fig, "3  Oysters and macroalgae keep feed nitrogen out of the water",
           "Fate of the nitrogen in the feed, kg N per tonne of fish + oyster")
    parts = [("fish_oyster", "in fish + oysters", "#534AB7"), ("macroalgae", "in macroalgae", "#1D9E75"),
             ("released", "released to water", "#E24B4A")]
    for row, s in enumerate(SYSTEMS):
        d, sc = RES[s]["nutrients"]["N"], RES[s]["scale"]
        left = 0
        for key, lab, c in parts:
            v = d[key] * sc
            if v >= 0:
                ax.barh(row, v, left=left, color=c, height=0.56, label=lab if row == 0 else None)
                if v > 7:
                    ax.text(left + v / 2, row, f"{v:.0f}", ha="center", va="center", color="white", fontsize=9.5, fontweight="bold")
                left += v
            else:
                ax.barh(row, v, color="#F7C1C1", height=0.56, edgecolor="#E24B4A", hatch="////", linewidth=0)
        extra = f"   ·   net uptake from water: {-d['released'] * sc:.0f} kg N" if d["released"] < 0 else ""
        ax.text(left + 2, row, f"feed: {d['feed'] * sc:.0f} kg N   ·   kept in products: {d['use_efficiency']:.0%}" + extra,
                va="center", fontsize=8.5, color=MUTED)
    ax.axvline(0, color=INK, lw=1)
    ax.set_yticks(range(3), [NAMES[s] for s in SYSTEMS])
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.invert_yaxis()
    ax.set_xlim(-10, 225)
    ax.set_xlabel("kg N per tonne")
    ax.xaxis.grid(True, color=GRID)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=3, loc="upper left", bbox_to_anchor=(-0.05, -0.2), fontsize=9)
    footer(fig, SRC + ", Tables 4 and 5; feed N recalculated from protein / 6.25")
    save(fig, "03_nitrogen_fate.png")


# ---------------------------------------------------------------- Figure 4
ROWS = [("Feeds", ["Feeds"]), ("Rejects fish (uneaten feed, excretion)", ["Rejects fish"]),
        ("Energy consumption", ["Energy consumption"]), ("Transports", ["Transports"]), ("Equipment", ["Equipment"]),
        ("Direct activity (farm area, water mgmt.)", ["Direct activity"]), ("Water consumption", ["Water consumption"]),
        ("Other (buildings, vehicles, chemicals, fry)", ["Building impact", "Vehicle", "Chemical products", "Fry"])]


def fig_heat():
    cmap = LinearSegmentedColormap.from_list("t", ["#FFFFFF", "#9FE1CB", "#0F6E56"])
    fig, axs = plt.subplots(1, 3, figsize=(12, 4.9), sharey=True)
    fig.subplots_adjust(left=0.235, right=0.99, top=0.80, bottom=0.10, wspace=0.05)
    header(fig, "4  Which process drives which impact",
           "Share of each impact category per process (%). Negative = removal (net nutrient uptake). Rounded Annex 1 amounts.")
    for ax, s in zip(axs, SYSTEMS):
        grid = []
        for lab, procs in ROWS:
            line = []
            for c in CATEGORIES:
                d = LC["amount"][c][s]
                tot = sum(abs(v) for p, v in d.items() if p != "Total") or 1
                line.append(sum(d[p] for p in procs) / tot * 100)
            grid.append(line)
        ax.imshow([[max(v, 0) for v in r] for r in grid], cmap=cmap, vmin=0, vmax=100, aspect="auto")
        for i, r in enumerate(grid):
            for j, v in enumerate(r):
                if abs(v) >= 0.5:
                    ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=8.5,
                            color="white" if v > 60 else ("#A32D2D" if v < 0 else INK))
        ax.set_xticks(range(len(CATEGORIES)), CATEGORIES, fontsize=8.5)
        ax.xaxis.tick_top()
        ax.set_title(NAMES[s], fontsize=10, color=COL[s], fontweight="bold", pad=22)
        ax.set_xticks([x - 0.5 for x in range(1, len(CATEGORIES))], minor=True)
        ax.set_yticks([y - 0.5 for y in range(1, len(ROWS))], minor=True)
        ax.grid(which="minor", color="white", lw=1.5)
        ax.tick_params(which="both", length=0)
        for sp in ax.spines.values():
            sp.set_visible(False)
    axs[0].set_yticks(range(len(ROWS)), [r[0] for r in ROWS], fontsize=9)
    footer(fig, SRC + ", Annex 1.  GW global warming · TCED energy demand · NPPU primary production use · "
                "AP acidification · EP eutrophication · LC land · WD water")
    save(fig, "04_process_heatmap.png")


# ---------------------------------------------------------------- Figure 5
def fig_score():
    kp = {s: RES[s]["kpis"] for s in SYSTEMS}
    n = len(kp[SYSTEMS[0]])
    fig, ax = plt.subplots(figsize=(9.5, 6.6))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.86, bottom=0.05)
    header(fig, "5  KPI scorecard: 13 KPIs per tonne of fish + oyster",
           "Green = target met, red = not met, grey = baseline (environmental targets: 10 % better than the fish-only pond)")
    x0 = 3.5
    ax.text(0, -1.2, "KPI", fontweight="bold", fontsize=9.5, va="center")
    ax.text(3.0, -1.2, "Target", fontweight="bold", fontsize=9.5, va="center", ha="right")
    for j, s in enumerate(SYSTEMS):
        ax.text(x0 + j * 1.6 + 0.75, -1.2, NAMES[s].replace(" pond ", "\npond ").replace(" fish ", "\nfish "),
                ha="center", va="center", fontsize=9, fontweight="bold", color=COL[s])
    for i in range(n):
        base = kp[SYSTEMS[0]][i]
        if i == 7:
            ax.axhline(i - 0.5, xmin=0, xmax=1, color="#B4B2A9", lw=0.8)
        ax.text(0, i, f"{base['id']}  {base['kpi']}", va="center", fontsize=9)
        ax.text(0.33, i + 0.33, base["unit"], va="center", fontsize=7.5, color=MUTED)
        t = base["target"] * (100 if base["unit"] == "%" else 1)
        sign = "≤" if base["better_if"] == "lower" else "≥"
        ax.text(3.0, i, f"{sign} {t:,.0f}" if abs(t) >= 100 else f"{sign} {t:g}", va="center", ha="right", fontsize=9, color=MUTED)
        for j, s in enumerate(SYSTEMS):
            kk = kp[s][i]
            v = kk["value"] * 100 if kk["unit"] == "%" else kk["value"]
            txt = f"{v:,.0f}" if abs(v) >= 100 else (f"{v:.2f}" if abs(v) < 10 else f"{v:.1f}")
            baseline = base["dimension"] == "Environment" and s == "SI-POLY"
            fc = "#F1EFE8" if baseline else ("#C6EFCE" if kk["met"] else "#FFC7CE")
            ax.add_patch(plt.Rectangle((x0 + j * 1.6 + 0.05, i - 0.42), 1.4, 0.84, color=fc, lw=0))
            ax.text(x0 + j * 1.6 + 0.75, i, txt, ha="center", va="center", fontsize=9.5)
    for j, s in enumerate(SYSTEMS):
        met = sum(x["met"] for x in kp[s])
        ax.text(x0 + j * 1.6 + 0.75, n + 0.15, f"{met} / {n}", ha="center", va="center", fontsize=12, fontweight="bold", color=COL[s])
    ax.text(3.0, n + 0.15, "targets met", ha="right", va="center", fontsize=9.5, fontweight="bold")
    ax.text(-0.0, 3.0, "", fontsize=1)
    ax.set_xlim(-0.05, x0 + 3 * 1.6 + 0.1)
    ax.set_ylim(n + 0.7, -1.9)
    ax.axis("off")
    footer(fig, "Targets are placeholders for a stakeholder workshop.  " + SRC)
    save(fig, "05_kpi_scorecard.png")


# ---------------------------------------------------------------- Key numbers
def fig_key_numbers():
    tot = {s: RES[s]["totals"] for s in SYSTEMS}
    ch = lambda s, c: (tot[s][c] / tot["SI-POLY"][c] - 1) * 100  # noqa: E731
    nk = {s: RES[s]["nutrients"]["N"]["use_efficiency"] * 100 for s in SYSTEMS}
    fs = {s: LC["amount"]["GW"][s]["Feeds"] / tot[s]["GW"] * 100 for s in SYSTEMS}
    short = {"SI-IMTA": "Semi-int.\nIMTA", "SE-IMTA": "Semi-ext.\nIMTA", "SI-POLY": "Fish-only\npond"}
    # big number, label, context, colour, values per system, unit, highlighted systems, number format
    tiles = [
        (f"{ch('SI-IMTA', 'EP'):.0f} %", "eutrophication", "semi-intensive IMTA vs fish-only pond", "#1D9E75",
         {s: tot[s]["EP"] for s in SYSTEMS}, "kg PO4-eq / t", ["SI-IMTA"], "{:.0f}"),
        (f"{nk['SI-IMTA']:.0f} %", "of feed nitrogen kept in products", f"semi-intensive IMTA (fish-only pond {nk['SI-POLY']:.0f} %)", "#0F6E56",
         nk, "% of feed N", ["SI-IMTA"], "{:.0f} %"),
        (f"{ch('SE-IMTA', 'GW'):.0f} %", "global warming", "semi-extensive IMTA vs fish-only pond", "#378ADD",
         {s: tot[s]["GW"] for s in SYSTEMS}, "kg CO2-eq / t", ["SE-IMTA"], "{:,.0f}"),
        (f"{min(fs.values()):.0f}–{max(fs.values()):.0f} %", "of greenhouse gases from feed", "the hotspot in all three systems", "#BA7517",
         fs, "% of global warming", SYSTEMS, "{:.0f} %"),
        (f"+{ch('SI-IMTA', 'LC'):.0f} / +{ch('SE-IMTA', 'LC'):.0f} %", "land competition", "IMTA needs more land: the trade-off", "#E24B4A",
         {s: tot[s]["LC"] for s in SYSTEMS}, "m2a / t", ["SI-IMTA", "SE-IMTA"], "{:,.0f}"),
    ]
    fig = plt.figure(figsize=(14, 5.6))
    fig.text(0.012, 0.975, "Key numbers", fontsize=14, fontweight="bold", color=INK, va="top")
    fig.text(0.012, 0.915, "per tonne of fish + oyster · INTEGRATE pond study (Portugal, Spain) · "
             "bars: the values behind each number, highlighted = the system the number refers to", fontsize=9.5, color=MUTED, va="top")
    n, left, right, gap = len(tiles), 0.012, 0.988, 0.012
    w = (right - left - gap * (n - 1)) / n
    for i, (big, lab, ctx, c, vals, unit, hi, fmt) in enumerate(tiles):
        x = left + i * (w + gap)
        bg = fig.add_axes([x, 0.06, w, 0.78])
        bg.set_xlim(0, 1)
        bg.set_ylim(0, 1)
        bg.axis("off")
        bg.add_patch(plt.Rectangle((0, 0), 1, 1, color="#FAF9F5", zorder=0))
        bg.add_patch(plt.Rectangle((0, 0.975), 1, 0.025, color=c))
        bg.text(0.06, 0.88, big, fontsize=20 if len(big) < 9 else 15.5, fontweight="bold", color=c, va="center")
        bg.text(0.06, 0.765, lab, fontsize=10, color=INK, va="center")
        bg.text(0.06, 0.70, ctx, fontsize=8, color=MUTED, va="center")
        ax = fig.add_axes([x + w * 0.08, 0.13, w * 0.86, 0.41])
        ys = [vals[s] for s in SYSTEMS]
        cols = [c if s in hi else "#D3D1C7" for s in SYSTEMS]
        ax.bar(range(3), ys, 0.62, color=cols)
        top = max(ys) * 1.28
        for j, v in enumerate(ys):
            ax.text(j, v + top * 0.03, fmt.format(v), ha="center", va="bottom", fontsize=8.5,
                    color=INK if SYSTEMS[j] in hi else MUTED, fontweight="bold" if SYSTEMS[j] in hi else "normal")
        ax.set_ylim(0, top)
        ax.set_xticks(range(3), [short[s] for s in SYSTEMS], fontsize=7.6)
        ax.set_yticks([])
        ax.set_facecolor("none")
        for sp in ("left", "top", "right"):
            ax.spines[sp].set_visible(False)
        ax.tick_params(axis="x", length=0, colors=MUTED)
        ax.set_title(unit, fontsize=8, color=MUTED, loc="left", pad=4)
    save(fig, "00_key_numbers.png")


# ---------------------------------------------------------------- Radar
def fig_radar():
    import numpy as np
    cats = CATEGORIES
    ang = np.linspace(0, 2 * np.pi, len(cats), endpoint=False).tolist()
    ang += ang[:1]
    fig = plt.figure(figsize=(9, 7.6))
    header(fig, "Environmental profile of the three systems",
           "Each impact per tonne as % of the fish-only pond (grey shape = 100 %). Smaller shape = lower impact.")
    ax = fig.add_axes([0.17, 0.13, 0.66, 0.66], polar=True)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    for s in ["SI-POLY", "SI-IMTA", "SE-IMTA"]:
        v = [RES[s]["totals"][c] / RES["SI-POLY"]["totals"][c] * 100 for c in cats]
        v += v[:1]
        ax.plot(ang, v, color=COL[s], lw=2.2 if s != "SI-POLY" else 1.6, label=NAMES[s])
        ax.fill(ang, v, color=COL[s], alpha=0.18 if s != "SI-POLY" else 0.07)
        if s == "SE-IMTA":
            for a, val in zip(ang[:-1], v[:-1]):
                ax.text(a, val + (20 if val < 150 else -34), f"{val:.0f}", color=COL[s], fontsize=8, ha="center", va="center", fontweight="bold", bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))
    ax.set_xticks(ang[:-1], [CAT_LABEL[c].replace(" ", "\n", 1) for c in cats], fontsize=9, color=INK)
    ax.set_ylim(0, 220)
    ax.set_yticks([50, 100, 150, 200], ["50", "100", "150", "200"], fontsize=7.5, color=MUTED)
    ax.set_rlabel_position(90 / 7)
    ax.grid(color=GRID)
    ax.spines["polar"].set_color(GRID)
    fig.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 0.035), ncol=3, fontsize=9)
    footer(fig, SRC + ", Annex 1")
    save(fig, "06_environmental_profile.png")


# ---------------------------------------------------------------- KPI framework diagram
def fig_framework():
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    fig = plt.figure(figsize=(13, 5.4))
    header(fig, "KPI framework: from report data to a scorecard",
           "Every step is a live formula in the Excel tool and a function in src/imtakpi/model.py")
    ax = fig.add_axes([0.0, 0.03, 1, 0.82])
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 5.4)
    ax.axis("off")
    cols = [
        (0.15, "1  Data", "#BA7517", "#FAEEDA", ["Table 4 – inventory", "feed, water, fish,", "oyster, macroalgae", "", "Table 5 – N and P", "", "Annex 1 – 7 impacts", "x 11 processes"]),
        (2.75, "2  Scale", "#993556", "#FBEAF0", ["functional unit:", "1 t fish + oyster", "", "factor =", "1,000 / (fish gain", "+ oyster gain)", "", "SI-IMTA: 0.814"]),
        (5.35, "3  KPI values", "#0F6E56", "#E1F5EE", ["Environment E1–E7", "GW, energy, NPPU,", "acid., eutroph.,", "land, water", "", "Circularity C1–C6", "N and P use eff., N", "released, FCR, non-fed", "biomass, feed share"]),
        (7.95, "4  Targets", "#185FA5", "#E6F1FB", ["E: 10 % better than", "the fish-only pond", "(value x 0.9)", "", "C: fixed values,", "e.g. N use ≥ 35 %,", "FCR ≤ 1.75", "", "yellow input cells"]),
        (10.55, "5  Score", "#3B6D11", "#EAF3DE", ["value vs target", "→ met / not met", "", "Semi-intensive IMTA  9/13", "Semi-extensive IMTA 12/13", "Fish-only pond          0/13", "", "(baseline for E1–E7)"]),
    ]
    W_, H_ = 2.3, 4.6
    for i, (x, title, edge, fill, lines) in enumerate(cols):
        ax.add_patch(FancyBboxPatch((x, 0.35), W_, H_, boxstyle="round,pad=0.02,rounding_size=0.15", fc=fill, ec=edge, lw=1.6))
        ax.add_patch(FancyBboxPatch((x, 0.35 + H_ - 0.62), W_, 0.62, boxstyle="round,pad=0.02,rounding_size=0.15", fc=edge, ec=edge, lw=1.6))
        ax.text(x + W_ / 2, 0.35 + H_ - 0.31, title, ha="center", va="center", color="white", fontsize=12, fontweight="bold")
        for j, ln in enumerate(lines):
            ax.text(x + 0.14, 0.35 + H_ - 0.95 - j * 0.40, ln, fontsize=9.2, color=INK, va="center",
                    fontweight="bold" if ln.startswith(("Environment", "Circularity", "Table", "E:", "C:")) else "normal")
        if i < len(cols) - 1:
            ax.add_patch(FancyArrowPatch((x + W_ + 0.03, 0.35 + H_ / 2), (cols[i + 1][0] - 0.03, 0.35 + H_ / 2),
                                         arrowstyle="-|>", mutation_scale=18, color="#5F5E5A", lw=1.6))
    save(fig, "07_kpi_framework.png")


# ---------------------------------------------------------------- Distance to target
def fig_distance():
    fig, ax = plt.subplots(figsize=(9.5, 6.4))
    fig.subplots_adjust(left=0.33, right=0.96, top=0.80, bottom=0.12)
    header(fig, "How far each system is from its KPI targets",
           "Margin to target in % (right of the line = target met). Fish-only pond not shown for E1–E7 (it is the baseline).")
    ids = [k["id"] for k in RES[SYSTEMS[0]]["kpis"]]
    ax.axvspan(0, 160, color="#EAF3DE", zorder=0)
    ax.axvspan(-110, 0, color="#FCEBEB", zorder=0)
    for j, s in enumerate(SYSTEMS):
        for i, k in enumerate(RES[s]["kpis"]):
            if k["dimension"] == "Environment" and s == "SI-POLY":
                continue
            t, v = k["target"], k["value"]
            m = ((t - v) if k["better_if"] == "lower" else (v - t)) / abs(t) * 100
            y = i + (j - 1) * 0.22
            mm = max(min(m, 150), -100)
            ax.plot([0, mm], [y, y], color=COL[s], lw=1.4, alpha=0.6)
            ax.scatter(mm, y, s=46, color=COL[s], zorder=3, edgecolor="white", linewidth=0.8,
                       marker=">" if m > 150 else "o")
    ax.axvline(0, color=INK, lw=1.2)
    ax.text(0, -1.05, "target", ha="center", fontsize=8.5, color=INK)
    ax.set_yticks(range(len(ids)), [f"{k['id']}  {k['kpi']}" for k in RES[SYSTEMS[0]]["kpis"]], fontsize=9)
    ax.axhline(6.5, color="#B4B2A9", lw=0.8, ls="--")
    ax.invert_yaxis()
    ax.set_xlim(-110, 160)
    ax.set_xticks([-100, -50, 0, 50, 100, 150], ["-100 %", "-50 %", "0", "+50 %", "+100 %", "≥ +150 %"])
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("margin to target")
    from matplotlib.lines import Line2D
    hs = [Line2D([], [], marker="o", ls="", color=COL[s], markersize=7, label=NAMES[s]) for s in SYSTEMS]
    fig.legend(handles=hs, frameon=False, loc="upper left", bbox_to_anchor=(0.005, 0.895), ncol=3, fontsize=9)
    footer(fig, SRC + ".  ► = margin above +150 %")
    save(fig, "08_kpi_distance_to_target.png")


fig_key_numbers()
fig_radar()
fig_framework()
fig_distance()
fig_relative()
fig_gw()
fig_nitrogen()
fig_heat()
fig_score()
