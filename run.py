"""Run the KPI model and write results/*.csv.

    python run.py
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from imtakpi import run_all, load, checks, SYSTEMS, NAMES, CATEGORIES  # noqa: E402

OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
res = run_all()
inv, nut, lc = load()

with open(OUT / "kpis.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["system", "id", "dimension", "kpi", "unit", "better_if", "target", "value", "met"])
    for s in SYSTEMS:
        for k in res[s]["kpis"]:
            w.writerow([s, k["id"], k["dimension"], k["kpi"], k["unit"], k["better_if"], round(k["target"], 4), round(k["value"], 4), k["met"]])

with open(OUT / "impacts_per_tonne.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["category", "name", "unit", *SYSTEMS, "SI-IMTA vs POLY", "SE-IMTA vs POLY"])
    for c in CATEGORIES:
        t = [res[s]["totals"][c] for s in SYSTEMS]
        w.writerow([c, *lc["units"][c], *t, f"{t[0] / t[2] - 1:+.0%}", f"{t[1] / t[2] - 1:+.0%}"])

with open(OUT / "nutrient_balance.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["system", "element", "feed_kg", "fish_oyster_kg", "macroalgae_kg", "released_kg", "use_efficiency", "released_per_t_kg"])
    for s in SYSTEMS:
        for el, d in res[s]["nutrients"].items():
            w.writerow([s, el, round(d["feed"], 2), d["fish_oyster"], d["macroalgae"], round(d["released"], 2),
                        round(d["use_efficiency"], 4), round(d["released"] * res[s]["scale"], 2)])

ck = checks(inv, nut, lc)
with open(OUT / "data_checks.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["check", "system", "report", "model", "ok"])
    w.writeheader()
    w.writerows(ck)

print(f"{'KPI':<42}" + "".join(f"{s:>12}" for s in SYSTEMS))
for i, k in enumerate(res[SYSTEMS[0]]["kpis"]):
    cells = ""
    for s in SYSTEMS:
        kk = res[s]["kpis"][i]
        v = kk["value"] * 100 if kk["unit"] == "%" else kk["value"]
        cells += f"{v:>10,.{0 if abs(v) >= 100 else 2}f} {'✓' if kk['met'] else '✗'}"
    print(f"{k['id']} {k['kpi'] + ' (' + k['unit'] + ')':<39}{cells}")
print("targets met:", {s: sum(k["met"] for k in res[s]["kpis"]) for s in SYSTEMS})
bad = [c for c in ck if not c["ok"]]
print(f"data checks: {len(ck) - len(bad)}/{len(ck)} pass")
for c in bad:
    print("  differs:", c["check"], c["system"], "report", c["report"], "model", c["model"])
