"""KPI model for the INTEGRATE pond study (deliverable PI05#3).

Three systems: SI-IMTA (semi-intensive pond IMTA, Portugal), SE-IMTA (semi-extensive pond IMTA, Spain)
and SI-POLY (semi-intensive fishpond polyculture, fish only, Portugal = conventional baseline).

Inputs are the report's own tables (data/report/*.csv). The model
  1. scales the pond inventory (Table 4) to the functional unit, 1 t of aquatic product (fish + oyster flesh),
  2. recomputes the N and P balance from the feed recipe and checks it against Table 5,
  3. reads the impact results per process (Annex 1, Piscentool),
  4. evaluates 13 KPIs against targets, and
  5. runs data-consistency checks between the tables.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "report"
SYSTEMS = ["SI-IMTA", "SE-IMTA", "SI-POLY"]
BASELINE = "SI-POLY"
NAMES = {"SI-IMTA": "Semi-intensive pond IMTA", "SE-IMTA": "Semi-extensive pond IMTA",
         "SI-POLY": "Semi-intensive fish polyculture"}
CATEGORIES = ["GW", "TCED", "NPPU", "AP", "EP", "LC", "WD"]
PROTEIN_TO_N = 6.25
IMPROVEMENT = 0.10   # environmental KPIs: target = at least 10 % better than the conventional baseline

# id, dimension, name, unit, better_if, target (None = relative to baseline)
KPI_DEF = [
    ("E1", "Environment", "Global warming", "kg CO2-eq/t", "lower", None, "GW"),
    ("E2", "Environment", "Cumulative energy demand", "MJ-eq/t", "lower", None, "TCED"),
    ("E3", "Environment", "Net primary production use", "kg C/t", "lower", None, "NPPU"),
    ("E4", "Environment", "Acidification", "kg SO2-eq/t", "lower", None, "AP"),
    ("E5", "Environment", "Eutrophication", "kg PO4-eq/t", "lower", None, "EP"),
    ("E6", "Environment", "Land competition", "m2a/t", "lower", None, "LC"),
    ("E7", "Environment", "Water dependence", "m3/t", "lower", None, "WD"),
    ("C1", "Circularity", "Nitrogen use efficiency", "%", "higher", 0.35, None),
    ("C2", "Circularity", "Phosphorus use efficiency", "%", "higher", 0.30, None),
    ("C3", "Circularity", "Net N released to water", "kg N/t", "lower", 60.0, None),
    ("C4", "Circularity", "Fish feed conversion ratio", "kg/kg", "lower", 1.75, None),
    ("C5", "Circularity", "Share of non-fed (extractive) biomass", "%", "higher", 0.50, None),
    ("C6", "Circularity", "Feed share of global warming", "%", "lower", 0.60, None),
]


def _read(name):
    with open(DATA / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load():
    """Return inventory {param: {system: value}}, nutrients {(item, el): {system: value}}, lcia {cat: {system: {process: amount}}}."""
    inv = {r["parameter"]: {s: float(r[s]) for s in SYSTEMS} for r in _read("inventory_table4.csv")}
    nut = {(r["item"], r["element"]): {s: float(r[s]) for s in SYSTEMS} for r in _read("nutrients_table5.csv")}
    lcia, units, pct = {}, {}, {}
    for r in _read("lcia_annex1.csv"):
        lcia.setdefault(r["category"], {}).setdefault(r["system"], {})[r["process"]] = float(r["amount"])
        pct.setdefault(r["category"], {}).setdefault(r["system"], {})[r["process"]] = float(r["percent"]) if r["percent"] else None
        units[r["category"]] = (r["category_name"], r["unit"])
    return inv, nut, {"amount": lcia, "percent": pct, "units": units}


def per_tonne(inv, s):
    """Scaling factor from one pond cycle to the functional unit (1 t fish + oyster flesh)."""
    return 1000.0 / (inv["fish_gain"][s] + inv["oyster_gain"][s])


def nutrient_balance(inv, nut, s):
    """N and P balance per pond and cycle; feed N/P recomputed from the recipe, outputs from Table 5."""
    out = {}
    for el in ("N", "P"):
        feed = inv["feed"][s] * (inv["diet_protein"][s] / 100 / PROTEIN_TO_N if el == "N" else inv["diet_phosphorus"][s] / 100)
        prod = nut[("produced_biomass", el)][s]
        algae = nut[("downstream_macroalgae", el)][s]
        out[el] = {"feed": feed, "fish_oyster": prod, "macroalgae": algae,
                   "extracted": prod + algae, "released": feed - prod - algae,
                   "use_efficiency": (prod + algae) / feed if feed else 0.0}
    return out


def evaluate(s, inv, nut, lc):
    nb = nutrient_balance(inv, nut, s)
    k = per_tonne(inv, s)
    tot = {c: lc["amount"][c][s]["Total"] for c in CATEGORIES}
    harvest = inv["fish_gain"][s] + inv["oyster_gain"][s] + inv["macroalgae_gain"][s]
    val = {"C1": nb["N"]["use_efficiency"], "C2": nb["P"]["use_efficiency"],
           "C3": nb["N"]["released"] * k,
           "C4": inv["feed"][s] / inv["fish_gain"][s],
           "C5": (inv["oyster_gain"][s] + inv["macroalgae_gain"][s]) / harvest,
           "C6": lc["amount"]["GW"][s]["Feeds"] / tot["GW"]}
    kpis = []
    for kid, dim, name, unit, better, target, cat in KPI_DEF:
        v = tot[cat] if cat else val[kid]
        if cat:
            target = lc["amount"][cat][BASELINE]["Total"] * (1 - IMPROVEMENT)
        met = v <= target if better == "lower" else v >= target
        if cat and s == BASELINE:
            met = False   # the baseline cannot beat itself
        kpis.append({"id": kid, "dimension": dim, "kpi": name, "unit": unit, "better_if": better,
                     "target": target, "value": v, "met": met})
    return {"kpis": kpis, "nutrients": nb, "scale": k, "totals": tot,
            "contrib": {c: lc["amount"][c][s] for c in CATEGORIES}}


def checks(inv, nut, lc):
    """Consistency checks between Table 4, Table 5 and Annex 1. Returns a list of dicts (check, system, report, model, ok)."""
    res = []

    def add(name, s, rep, mod, rel=0.0, absolute=0.0):
        ok = abs(rep - mod) <= max(rel * abs(rep), absolute)
        res.append({"check": name, "system": s, "report": rep, "model": round(mod, 4), "ok": ok})
    for s in SYSTEMS:
        nb = nutrient_balance(inv, nut, s)
        k = per_tonne(inv, s)
        add("Feed N = feed x protein / 6.25 (Table 5)", s, nut[("feed", "N")][s], nb["N"]["feed"], absolute=0.1)
        add("Feed P = feed x P content (Table 5)", s, nut[("feed", "P")][s], nb["P"]["feed"], absolute=0.1)
        add("N rejection = feed - extracted (Table 5)", s, nut[("total_rejection", "N")][s], nb["N"]["released"], absolute=0.2)
        add("Water use per t = Annex 1 water consumption", s, lc["amount"]["WD"][s]["Water consumption"], inv["seawater_used"][s] * k, rel=0.01)
        add("FCR = feed / fish gain (Table 4)", s, inv["fcr_reported"][s], inv["feed"][s] / inv["fish_gain"][s], absolute=0.02)
        add("Land: allocated farm area = Direct activity in LC (Annex 1)", s, lc["amount"]["LC"][s]["Direct activity"],
            inv["farm_area"][s] * inv["production_pond_area"][s] / inv["farm_pond_area"][s] * inv["cycle_length"][s] / 12 * k, rel=0.05)
        for c in CATEGORIES:
            parts = sum(v for p, v in lc["amount"][c][s].items() if p != "Total")
            add(f"{c}: sum of processes = total (Annex 1)", s, lc["amount"][c][s]["Total"], parts, rel=0.005, absolute=2.0)
    return res


def run_all():
    inv, nut, lc = load()
    return {s: evaluate(s, inv, nut, lc) for s in SYSTEMS}
