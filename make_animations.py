"""Draw animated GIF versions of the findings charts into results/charts/ (shown in the README)."""
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.animation import FuncAnimation, PillowWriter  # noqa: E402

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from imtakpi import run_all  # noqa: E402

OUT = ROOT / "results" / "charts"
OUT.mkdir(parents=True, exist_ok=True)
RES = run_all()
CODES = list(RES)
NAMES = {"imta-A": "A: fish monoculture", "imta-C": "C: IMTA + waste valorisation"}
GREY, TEAL, PURPLE, AMBER, CORAL = "#888780", "#1D9E75", "#534AB7", "#BA7517", "#D85A30"
FRAMES, HOLD = 30, 25          # growth frames, then hold the final picture
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.spines.left": False, "axes.grid": False})


def ease(i):
    t = min(i / FRAMES, 1.0)
    return 1 - (1 - t) ** 3     # ease-out


def save(fig, anim, name):
    anim.save(OUT / name, writer=PillowWriter(fps=20))
    plt.close(fig)
    print("written", name)


# 1 nitrogen balance: segments fill from left to right
parts = [("fish", "kept in fish", PURPLE), ("seaweed", "taken up by seaweed", TEAL),
         ("mussels", "taken up by mussels", AMBER), ("to_sea", "lost to the sea", CORAL)]
fig, ax = plt.subplots(figsize=(8, 3.4))


def draw_n(i):
    ax.clear()
    k = ease(i)
    for row, code in enumerate(CODES):
        d = RES[code]["nutrients"]["N"]
        left, total = 0, d["feed"] * k
        for key, lab, c in parts:
            w = max(0.0, min(d[key], total - left))
            ax.barh(row, w, left=left, color=c, height=0.55, label=lab if row == 0 else None)
            if w > 200 and k > 0.95:
                ax.text(left + w / 2, row, f"{d[key]:,.0f}", ha="center", va="center", color="white", fontsize=9)
            left += d[key]
    ax.set_xlim(0, 4300)
    ax.set_yticks(range(len(CODES)), [NAMES[c] for c in CODES])
    ax.set_xlabel("kg nitrogen per year (feed contains 4,200 kg N)")
    ax.set_title("Where the nitrogen from the feed goes", loc="left", fontsize=11)
    ax.legend(ncol=4, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.3), frameon=False)
    fig.tight_layout()


save(fig, FuncAnimation(fig, draw_n, frames=FRAMES + HOLD), "anim_01_nitrogen_balance.gif")

# 2 climate by contributor: bars grow
groups = {"Feed": ["fishmeal, 63-65% protein", "fish oil, from anchovy", "soybean meal", "wheat grain, feed", "rape oil, crude"],
          "Electricity": ["electricity, low voltage"], "Boat fuel": ["diesel", "Carbon dioxide, fossil"],
          "Transport": ["transport, freight, lorry 16-32 metric ton, EURO6"], "Ropes, nets": ["polypropylene, granulate"],
          "Waste loops\n(net)": ["composting, seaweed residues", "ground limestone (avoided)", "mineral N fertiliser (avoided)"]}
vals = {c: [sum(RES[c]["contrib"].get(f, (0, 0))[0] for f in fl) / 1000 for fl in groups.values()] for c in CODES}
fig, ax = plt.subplots(figsize=(8, 3.6))


def draw_c(i):
    ax.clear()
    k = ease(i)
    w = 0.38
    for j, (code, col) in enumerate(zip(CODES, (GREY, TEAL))):
        xs = [x + (j - 0.5) * w for x in range(len(groups))]
        ax.bar(xs, [v * k for v in vals[code]], w, color=col, label=NAMES[code])
        if k > 0.95:
            for x, v in zip(xs, vals[code]):
                if abs(v) >= 1:
                    ax.text(x, v + 1.2, f"{v:.0f}", ha="center", fontsize=8, color="#444441")
                elif j == 1 and abs(v) > 0:
                    ax.text(x, 1.2, f"{v:+.2f}", ha="center", fontsize=8, color="#444441")
    ax.set_ylim(0, 95)
    ax.set_xticks(range(len(groups)), list(groups))
    ax.set_ylabel("t CO2-eq per year (whole farm)")
    ax.set_title("Climate change by contributor (illustrative factors)", loc="left", fontsize=11)
    ax.legend(frameon=False)
    fig.tight_layout()


save(fig, FuncAnimation(fig, draw_c, frames=FRAMES + HOLD), "anim_02_climate_by_contributor.gif")

# 3 trade-off: per kg vs whole farm
per_kg = [RES[c]["kpis"][0]["value"] for c in CODES]
total = [RES[c]["climate_total"] / 1000 for c in CODES]
fig, axs = plt.subplots(1, 2, figsize=(8, 3.3))


def draw_t(i):
    k = ease(i)
    for ax, data, title, top, fmt in [(axs[0], per_kg, "per kg sea bream (kg CO2-eq/kg)", 3.4, "{:.2f}"),
                                      (axs[1], total, "whole farm (t CO2-eq per year)", 150, "{:.0f}")]:
        ax.clear()
        ax.bar(["A", "C"], [v * k for v in data], color=[GREY, TEAL], width=0.55)
        ax.set_ylim(0, top)
        ax.set_yticks([])
        ax.set_title(title, fontsize=9)
        if k > 0.95:
            for x, v in enumerate(data):
                ax.text(x, v + top * 0.03, fmt.format(v), ha="center", fontsize=10)
    fig.suptitle("IMTA is better per kg, but the farm as a whole emits more", fontsize=11, x=0.02, ha="left")
    fig.tight_layout()


save(fig, FuncAnimation(fig, draw_t, frames=FRAMES + HOLD), "anim_03_per_kg_vs_total.gif")

# 4 KPIs: circularity KPIs (share of target reached), A vs C
ids = ["C1", "C2", "C3", "C5", "C6", "B2"]
kp = {c: {k["id"]: k for k in RES[c]["kpis"]} for c in CODES}
fig, ax = plt.subplots(figsize=(8, 3.6))


def draw_k(i):
    ax.clear()
    k = ease(i)
    w = 0.38
    for j, (code, col) in enumerate(zip(CODES, (GREY, TEAL))):
        ys = [y + (j - 0.5) * w for y in range(len(ids))]
        ax.barh(ys, [kp[code][x]["value"] * 100 * k for x in ids], w, color=col, label=NAMES[code])
    for y, x in enumerate(ids):
        ax.plot([kp[CODES[0]][x]["target"] * 100] * 2, [y - 0.45, y + 0.45], color="#2C2C2A", lw=1.2, ls="--")
    ax.set_yticks(range(len(ids)), [f"{x} {kp[CODES[0]][x]['kpi']}" for x in ids], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, 105)
    ax.set_xlabel("%   (dashed line = target)")
    ax.set_title("Circularity and economic KPIs", loc="left", fontsize=11)
    ax.legend(frameon=False, loc="lower right", fontsize=8)
    fig.tight_layout()


save(fig, FuncAnimation(fig, draw_k, frames=FRAMES + HOLD), "anim_04_circularity_kpis.gif")

# 5 openLCA run 3 contributions
rows = [r for r in csv.DictReader(open(ROOT / "data/openlca_results/contributions_grouped.csv"))
        if r["run"] == "run3" and r["impact_category"] == "Climate change"]
rows.sort(key=lambda r: float(r["result"]))
fig, ax = plt.subplots(figsize=(8, 3.6))


def draw_o(i):
    ax.clear()
    k = ease(i)
    v = [float(r["result"]) / 40000 for r in rows]
    ax.barh([r["contributor_group"] for r in rows], [x * k for x in v],
            color=[CORAL if r["contributor_group"] == "Electricity generation" else PURPLE for r in rows])
    ax.set_xlim(0, 3.6)
    ax.set_xlabel("kg CO2-eq per kg sea bream (economic allocation)")
    ax.set_title("openLCA run 3 (ecoinvent 3.7, EF 3.1) – not final:\nelectricity provider is lignite-dominated (known issue)", loc="left", fontsize=10)
    fig.tight_layout()


save(fig, FuncAnimation(fig, draw_o, frames=FRAMES + HOLD), "anim_05_openlca_run3.gif")
