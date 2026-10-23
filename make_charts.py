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


fig_relative()
fig_gw()
fig_nitrogen()
fig_heat()
fig_score()
