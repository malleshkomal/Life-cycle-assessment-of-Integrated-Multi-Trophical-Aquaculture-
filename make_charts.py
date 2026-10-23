"""Draw the findings charts into results/charts/."""
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from imtakpi import run_all  # noqa: E402

OUT = ROOT / "results" / "charts"
OUT.mkdir(parents=True, exist_ok=True)
RES = run_all()
NAMES = {"imta-A": "A: fish monoculture", "imta-C": "C: IMTA + waste valorisation"}
COL = {"fish": "#534AB7", "seaweed": "#1D9E75", "mussels": "#BA7517", "sea": "#D85A30"}
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=150)
    plt.close(fig)


# 1 nitrogen balance
fig, ax = plt.subplots(figsize=(8, 3.6))
for i, code in enumerate(RES):
    d = RES[code]["nutrients"]["N"]
    left = 0
    for key, lab, c in [("fish", "kept in fish", COL["fish"]), ("seaweed", "taken up by seaweed", COL["seaweed"]),
                        ("mussels", "taken up by mussels", COL["mussels"]), ("to_sea", "lost to the sea", COL["sea"])]:
        ax.barh(i, d[key], left=left, color=c, label=lab if i == 0 else None)
        if d[key] > 150:
            ax.text(left + d[key] / 2, i, f"{d[key]:,.0f}", ha="center", va="center", color="white", fontsize=9)
        left += d[key]
ax.set_yticks(range(len(RES)), [NAMES[c] for c in RES])
ax.set_xlabel("kg nitrogen per year (feed contains 4,200 kg N)")
ax.set_title("1. Where the nitrogen from the feed goes")
ax.legend(ncol=4, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.28), frameon=False)
save(fig, "01_nitrogen_balance.png")

# 2 climate by contributor
groups = {"Feed": ["fishmeal, 63-65% protein", "fish oil, from anchovy", "soybean meal", "wheat grain, feed", "rape oil, crude"],
          "Electricity": ["electricity, low voltage"], "Boat fuel": ["diesel", "Carbon dioxide, fossil"],
          "Ropes, nets": ["polypropylene, granulate"], "Transport": ["transport, freight, lorry 16-32 metric ton, EURO6"],
          "Waste loops": ["composting, seaweed residues"], "Credits": ["ground limestone (avoided)", "mineral N fertiliser (avoided)"]}
fig, ax = plt.subplots(figsize=(8, 3.8))
w = 0.38
for j, code in enumerate(RES):
    c = RES[code]["contrib"]
    vals = [sum(c.get(f, (0, 0))[0] for f in fl) / 1000 for fl in groups.values()]
    ax.bar([i + (j - 0.5) * w for i in range(len(groups))], vals, w, label=NAMES[code], color=["#888780", "#1D9E75"][j])
ax.set_xticks(range(len(groups)), list(groups))
ax.set_ylabel("t CO2-eq per year (whole farm)")
ax.set_title("2. Climate change by contributor (illustrative factors)")
ax.axhline(0, color="black", lw=0.6)
ax.legend(frameon=False)
save(fig, "02_climate_by_contributor.png")

def fmt(v):
    return f"{v:,.0f}" if abs(v) >= 100 else f"{v:.3g}"


# 3 KPI scorecard
codes = list(RES)
kp = RES[codes[0]]["kpis"]
fig, ax = plt.subplots(figsize=(8, 4.6))
ax.axis("off")
cell = [[k["id"], k["kpi"], f"{'≤' if k['better_if'] == 'lower' else '≥'} {k['target']:g}"] +
        [fmt(RES[c]['kpis'][i]['value']) for c in codes] for i, k in enumerate(kp)]
t = ax.table(cellText=cell, colLabels=["ID", "KPI", "Target"] + [NAMES[c] for c in codes], loc="center", cellLoc="left",
             colWidths=[0.06, 0.36, 0.12, 0.22, 0.26])
t.auto_set_font_size(False)
t.set_fontsize(8)
t.scale(1, 1.35)
for i in range(len(kp)):
    for j, c in enumerate(codes):
        t[i + 1, 3 + j].set_facecolor("#C6EFCE" if RES[c]["kpis"][i]["met"] else "#FFC7CE")
ax.set_title("3. KPI scorecard: green = target met, red = not met", pad=4)
save(fig, "03_kpi_scorecard.png")

# 4 trade-off: per kg vs farm total
fig, axs = plt.subplots(1, 2, figsize=(8, 3.4))
labels = ["A", "C"]
axs[0].bar(labels, [RES[c]["kpis"][0]["value"] for c in codes], color=["#888780", "#1D9E75"])
axs[0].set_title("per kg sea bream (kg CO2-eq/kg)", fontsize=9)
axs[1].bar(labels, [RES[c]["climate_total"] / 1000 for c in codes], color=["#888780", "#1D9E75"])
axs[1].set_title("whole farm (t CO2-eq/yr)", fontsize=9)
fig.suptitle("4. IMTA is better per kg, but the farm as a whole emits more", fontsize=10)
save(fig, "04_per_kg_vs_total.png")

# 5 openLCA run 3 contributions
rows = [r for r in csv.DictReader(open(ROOT / "data/openlca_results/contributions_grouped.csv"))
        if r["run"] == "run3" and r["impact_category"] == "Climate change"]
rows.sort(key=lambda r: float(r["result"]))
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.barh([r["contributor_group"] for r in rows], [float(r["result"]) / 40000 for r in rows], color="#534AB7")
ax.set_xlabel("kg CO2-eq per kg sea bream (economic allocation)")
ax.set_title("5. openLCA run 3 (ecoinvent 3.7, EF 3.1)\nelectricity provider is lignite-dominated – known issue, not final", fontsize=9)
save(fig, "05_openlca_run3_contributions.png")
print("charts written to", OUT)
