"""Compute impacts, nutrient balances and KPIs for all scenarios and write results/.

Usage:
    python run.py                         # illustrative factors
    python run.py --factors my_factors.csv  # your own per-unit factors (e.g. 1 unit of each input calculated in openLCA)
"""
import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from imtakpi import run_all  # noqa: E402

LABEL = {"imta-A": "A: fish monoculture", "imta-C": "C: IMTA + waste valorisation"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--factors", default=None)
    a = ap.parse_args()
    res = run_all(a.factors)
    out = ROOT / "results"
    out.mkdir(exist_ok=True)

    with open(out / "kpis.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["scenario", "id", "kpi", "unit", "value", "better_if", "target", "met"])
        w.writeheader()
        for r in res.values():
            for k in r["kpis"]:
                w.writerow({**k, "value": round(k["value"], 4)})
    with open(out / "nutrient_balance.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["scenario", "element", "feed", "kept_in_fish", "seaweed", "mussels", "released_by_fish", "recovered", "to_sea"])
        for code, r in res.items():
            for el, d in r["nutrients"].items():
                w.writerow([code, el] + [round(d[k], 1) for k in ("feed", "fish", "seaweed", "mussels", "released", "recovered", "to_sea")])
    with open(out / "impacts.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["scenario", "flow", "climate_kgCO2eq_per_year", "marine_eutrophication_kgNeq_per_year"])
        for code, r in res.items():
            for flow, (c, e) in r["contrib"].items():
                w.writerow([code, flow, round(c, 2), round(e, 3)])
            w.writerow([code, "TOTAL (farm)", round(r["climate_total"], 1), round(r["eutrophication_total"], 2)])

    codes = list(res)
    print(f"{'KPI':45s}" + "".join(f"{LABEL.get(c, c):>32s}" for c in codes))
    for i, k in enumerate(res[codes[0]]["kpis"]):
        line = f"{k['id']} {k['kpi']:42s}"
        for c in codes:
            kk = res[c]["kpis"][i]
            line += f"{kk['value']:>30.4f} {'✓' if kk['met'] else '✗'}"
        print(line)
    for c in codes:
        met = sum(k["met"] for k in res[c]["kpis"])
        print(f"{LABEL.get(c, c)}: {met} of {len(res[c]['kpis'])} targets met; farm climate change {res[c]['climate_total']:,.0f} kg CO2-eq/yr")
    print(f"\nResults written to {out}")


if __name__ == "__main__":
    main()
