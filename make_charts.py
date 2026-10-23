"""Draw the findings charts, static (PNG) and animated (GIF), into results/charts/.

Each chart is one function draw(fig, k) where k in [0, 1] is how far the bars have grown;
the PNG is k = 1 and the GIF animates k from 0 to 1 with an ease-out, then holds.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.animation import FuncAnimation, PillowWriter  # noqa: E402

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from imtakpi import run_all, load, SYSTEMS, NAMES, CATEGORIES  # noqa: E402

OUT = ROOT / "results" / "charts"
OUT.mkdir(parents=True, exist_ok=True)
RES = run_all()
INV, NUT, LC = load()
COL = {"SI-IMTA": "#1D9E75", "SE-IMTA": "#378ADD", "SI-POLY": "#888780"}
SHORT = {"SI-IMTA": "Semi-intensive\nIMTA", "SE-IMTA": "Semi-extensive\nIMTA", "SI-POLY": "Semi-intensive\nfish polyculture"}
PROC_COL = {"Feeds": "#BA7517", "Transports": "#D85A30", "Energy consumption": "#534AB7", "Equipment": "#7F77DD",
            "Building impact": "#B4B2A9", "Vehicle": "#5F5E5A", "Chemical products": "#D4537E", "Fry": "#EF9F27",
            "Rejects fish": "#E24B4A", "Water consumption": "#85B7EB", "Direct activity": "#639922"}
FRAMES, HOLD = 30, 30
plt.rcParams.update({"font.size": 10, "font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#B4B2A9", "axes.titleweight": "bold", "axes.titlesize": 11})


def ease(i):
    t = min(i / FRAMES, 1.0)
    return 1 - (1 - t) ** 3


def render(name, size, draw):
    fig = plt.figure(figsize=size, dpi=100)
    draw(fig, 1.0)
    fig.savefig(OUT / f"{name}.png", dpi=150, bbox_inches="tight", facecolor="white")
    anim = FuncAnimation(fig, lambda i: (fig.clear(), draw(fig, ease(i))), frames=FRAMES + HOLD)
    anim.save(OUT / f"anim_{name}.gif", writer=PillowWriter(fps=20), savefig_kwargs={"facecolor": "white"})
    plt.close(fig)
    print("written", name, "(png + gif)")


# 1 Global warming by process, stacked
def gw(fig, k):
    ax = fig.add_subplot(111)
    procs = [p for p in PROC_COL if any(LC["amount"]["GW"][s].get(p, 0) for s in SYSTEMS)]
    for j, s in enumerate(SYSTEMS):
        bottom = 0
        for p in procs:
            v = LC["amount"]["GW"][s][p] * k
            ax.bar(j, v, 0.55, bottom=bottom, color=PROC_COL[p], label=p if j == 0 else None, edgecolor="white", linewidth=0.6)
            bottom += v
        if k > 0.97:
            ax.text(j, bottom + 60, f"{LC['amount']['GW'][s]['Total']:,.0f}", ha="center", fontweight="bold")
    ax.set_xticks(range(3), [SHORT[s] for s in SYSTEMS])
    ax.set_ylim(0, 3300)
    ax.set_ylabel("kg CO2-eq per tonne fish + oyster")
    ax.set_title("Global warming by process: feed dominates", loc="left")
    ax.legend(frameon=False, fontsize=8, loc="upper left", bbox_to_anchor=(1, 1))
    fig.tight_layout()


# 2 All 7 categories relative to the polyculture
def rel(fig, k):
    ax = fig.add_subplot(111)
    w = 0.26
    for j, s in enumerate(SYSTEMS):
        vals = [RES[s]["totals"][c] / RES["SI-POLY"]["totals"][c] * 100 for c in CATEGORIES]
        xs = [x + (j - 1) * w for x in range(len(CATEGORIES))]
        ax.bar(xs, [v * k for v in vals], w, color=COL[s], label=NAMES[s])
        if k > 0.97 and s != "SI-POLY":
            for x, v in zip(xs, vals):
                ax.text(x, v + 3, f"{v:.0f}", ha="center", fontsize=7.5, color="#444441")
    ax.axhline(100, color="#2C2C2A", lw=1, ls="--")
    ax.set_xticks(range(len(CATEGORIES)), ["Global\nwarming", "Energy\ndemand", "Primary\nproduction", "Acidifi-\ncation",
                                           "Eutrophi-\ncation", "Land\ncompetition", "Water\ndependence"], fontsize=8.5)
    ax.set_ylim(0, 225)
    ax.set_ylabel("% of fish polyculture (= 100)")
    ax.set_title("IMTA is lower in 6 of 7 categories; it needs more land", loc="left")
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.2))
    fig.tight_layout()


# 3 Where the nitrogen in the feed goes, per tonne
def nitro(fig, k):
    ax = fig.add_subplot(111)
    parts = [("fish_oyster", "in fish + oysters", "#534AB7"), ("macroalgae", "in macroalgae", "#1D9E75"),
             ("released", "released to water", "#E24B4A")]
    for row, s in enumerate(SYSTEMS):
        d, sc = RES[s]["nutrients"]["N"], RES[s]["scale"]
        left = 0
        for key, lab, c in parts:
            v = d[key] * sc * k
            if v >= 0:
                ax.barh(row, v, left=left, color=c, height=0.55, label=lab if row == 0 else None)
                if k > 0.97 and v > 6:
                    ax.text(left + v / 2, row, f"{v:.0f}", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
                left += v
            else:
                ax.barh(row, v, left=0, color=c, height=0.55, hatch="///", edgecolor="white")
                if k > 0.97:
                    ax.text(v - 1, row, f"{v:.0f}  net uptake", ha="right", va="center", fontsize=8.5, color=c)
        if k > 0.97:
            ax.text(left + 2, row, f"feed {d['feed'] * sc:.0f} kg N", va="center", fontsize=8.5, color="#444441")
    ax.axvline(0, color="#2C2C2A", lw=0.8)
    ax.set_yticks(range(3), [NAMES[s] for s in SYSTEMS])
    ax.invert_yaxis()
    ax.set_xlim(-30, 150)
    ax.set_xlabel("kg nitrogen per tonne fish + oyster")
    ax.set_title("Where the nitrogen in the feed goes", loc="left")
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.22))
    fig.tight_layout()


# 4 KPI scorecard
def score(fig, k):
    ax = fig.add_subplot(111)
    kp = {s: RES[s]["kpis"] for s in SYSTEMS}
    n = len(kp[SYSTEMS[0]])
    shown = int(round(k * n))
    for i in range(n):
        base = kp[SYSTEMS[0]][i]
        ax.text(-0.05, i, f"{base['id']}  {base['kpi']} ({base['unit']})", ha="right", va="center", fontsize=8.5)
        if i >= shown:
            continue
        for j, s in enumerate(SYSTEMS):
            kk = kp[s][i]
            v = kk["value"] * 100 if kk["unit"] == "%" else kk["value"]
            txt = f"{v:,.0f}" if abs(v) >= 100 else f"{v:.2f}" if abs(v) < 10 else f"{v:.1f}"
            baseline = base["dimension"] == "Environment" and s == "SI-POLY"
            fc = "#F1EFE8" if baseline else ("#C6EFCE" if kk["met"] else "#FFC7CE")
            ax.add_patch(plt.Rectangle((j + 0.04, i - 0.42), 0.92, 0.84, color=fc))
            ax.text(j + 0.5, i, txt + ("" if baseline else ("  ✓" if kk["met"] else "  ✗")), ha="center", va="center", fontsize=8.5)
    for j, s in enumerate(SYSTEMS):
        met = sum(x["met"] for x in kp[s])
        ax.text(j + 0.5, -0.75, SHORT[s], ha="center", va="bottom", fontsize=8.5, fontweight="bold")
        if k > 0.97:
            ax.text(j + 0.5, n + 0.1, f"{met} / {n} targets", ha="center", fontsize=9, fontweight="bold", color=COL[s])
    ax.set_xlim(-2.2, 3)
    ax.set_ylim(n + 0.6, -1.9)
    ax.axis("off")
    ax.set_title("KPI scorecard (green = target met; polyculture is the baseline for E-targets)", loc="left", fontsize=10)
    fig.tight_layout()


# 5 Process shares in every category, semi-intensive IMTA vs polyculture
def shares(fig, k):
    axs = fig.subplots(1, 3, sharey=True)
    for ax, s in zip(axs, SYSTEMS):
        for x, c in enumerate(CATEGORIES):
            d = LC["amount"][c][s]
            tot = sum(abs(v) for p, v in d.items() if p != "Total") or 1
            pos, neg = 0, 0
            for p, col in PROC_COL.items():
                v = d.get(p, 0) / tot * 100 * k
                if v >= 0:
                    ax.bar(x, v, 0.7, bottom=pos, color=col, label=p if (s == SYSTEMS[0] and x == 0) else None)
                    pos += v
                else:
                    ax.bar(x, v, 0.7, bottom=neg, color=col, hatch="///", edgecolor="white")
                    neg += v
        ax.set_xticks(range(len(CATEGORIES)), CATEGORIES, fontsize=8, rotation=0)
        ax.set_title(SHORT[s].replace("\n", " "), fontsize=9.5)
        ax.axhline(0, color="#2C2C2A", lw=0.6)
    axs[0].set_ylabel("share of the impact (%)")
    axs[0].set_ylim(-30, 102)
    fig.legend(frameon=False, fontsize=7.5, ncol=6, loc="lower center", bbox_to_anchor=(0.5, -0.01))
    fig.suptitle("Which process causes which impact (Annex 1, rounded amounts)", x=0.01, ha="left", fontweight="bold", fontsize=11)
    fig.tight_layout(rect=(0, 0.1, 1, 1))


render("01_gw_by_process", (8.4, 4.2), gw)
render("02_relative_to_polyculture", (8.4, 4.4), rel)
render("03_nitrogen_fate", (8.4, 3.6), nitro)
render("04_kpi_scorecard", (8.4, 5.6), score)
render("05_process_shares", (10, 4.4), shares)
