"""Core calculations: inventory -> impacts -> economic allocation -> nutrient balance -> KPIs.

All inputs are read from the LCIS2024-structured files in data/lci/ and from a factor table.
The shipped factor table (data/factors_illustrative.csv) is ILLUSTRATIVE, not ecoinvent.
"""
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FEED = ["fishmeal, 63-65% protein", "fish oil, from anchovy", "soybean meal", "wheat grain, feed", "rape oil, crude"]
FISH, SEAWEED, MUSSELS = "Sea bream, fresh, at farm gate", "Seaweed, fresh, at farm gate", "Mussels, fresh, at farm gate"

# KPI id: (name, unit, better_if, target)
KPI_DEF = {
    "E1": ("Carbon footprint of fish", "kg CO2-eq/kg", "lower", 2.0),
    "E2": ("Marine eutrophication of fish", "kg N-eq/kg", "lower", 0.08),
    "E4": ("Feed share of climate impact", "-", "lower", 0.75),
    "C1": ("Nitrogen recovery rate", "-", "higher", 0.15),
    "C2": ("Phosphorus recovery rate", "-", "higher", 0.10),
    "C3": ("Nitrogen use efficiency", "-", "higher", 0.35),
    "C4": ("Feed conversion ratio", "kg/kg", "lower", 1.7),
    "C5": ("Share of non-fed biomass", "-", "higher", 0.5),
    "C6": ("By-product valorisation rate", "-", "higher", 0.5),
    "B1": ("Eco-efficiency", "EUR/t CO2-eq", "higher", 3000),
    "B2": ("Revenue share of extractive species", "-", "higher", 0.25),
}


def _rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load(factors=None):
    lci = _rows(ROOT / "data/lci/dataset/imta-cirkpi-lci.csv")
    par = {r["par_name"]: float(r["par_amount"]) for r in _rows(ROOT / "data/lci/dataset/parameters.csv")}
    fac = {r["flow"]: (float(r["climate_kgCO2eq_per_unit"]), float(r["marine_eutrophication_kgNeq_per_unit"]))
           for r in _rows(factors or ROOT / "data/factors_illustrative.csv")}
    inv = defaultdict(dict)
    for r in lci:
        inv[r["ap_code"]][r["fp_name"]] = (r["fp_type"], float(r["fp_amount"]))
    return dict(inv), par, fac


def impacts(x, fac):
    """Return farm totals and contributions per flow: amount x factor (avoided products negative)."""
    cc = eu = 0.0
    contrib = {}
    for f, (t, v) in x.items():
        if t == "production":
            continue
        sign = -1 if t == "avoided product" else 1
        c, e = fac.get(f, (0.0, 0.0))
        contrib[f] = (sign * v * c, sign * v * e)
        cc += sign * v * c
        eu += sign * v * e
    return cc, eu, contrib


def nutrient_balance(x, par):
    amt = lambda f: x.get(f, (None, 0.0))[1]
    fish, sw, mu = amt(FISH), amt(SEAWEED), amt(MUSSELS)
    residues = par["seaweed_residues"] if amt("composting, seaweed residues") > 0 else 0.0
    out = {}
    for el in ("N", "P"):
        feed_in = par["feed_total"] * par[f"{el}_feed"]
        in_fish = fish * par[f"{el}_fish"]
        in_sw = (sw + residues) * par[f"{el}_seaweed"]
        in_mu = mu * par[f"{el}_mussels"]
        released = feed_in - in_fish
        out[el] = {"feed": feed_in, "fish": in_fish, "seaweed": in_sw, "mussels": in_mu,
                   "released": released, "recovered": in_sw + in_mu, "to_sea": released - in_sw - in_mu}
    return out


def evaluate(code, x, par, fac):
    amt = lambda f: x.get(f, (None, 0.0))[1]
    fish, sw, mu = amt(FISH), amt(SEAWEED), amt(MUSSELS)
    cc, eu, contrib = impacts(x, fac)
    rev = {"fish": fish * par["price_fish"], "seaweed": sw * par["price_seaweed"], "mussels": mu * par["price_mussels"]}
    share = rev["fish"] / sum(rev.values())
    nb = nutrient_balance(x, par)
    residues = par["seaweed_residues"] if amt("composting, seaweed residues") > 0 else 0.0
    shells = amt("ground limestone (avoided)")
    potential = (par["seaweed_residues"] if sw > 0 else 0.0) + mu * par["shell_share"]
    cc_feed = sum(contrib[f][0] for f in FEED if f in contrib)
    val = {
        "E1": cc * share / fish,
        "E2": eu * share / fish,
        "E4": cc_feed / cc,
        "C1": nb["N"]["recovered"] / nb["N"]["released"],
        "C2": nb["P"]["recovered"] / nb["P"]["released"],
        "C3": (nb["N"]["fish"] + nb["N"]["recovered"]) / nb["N"]["feed"],
        "C4": par["feed_total"] / fish,
        "C5": (sw + mu) / (fish + sw + mu),
        "C6": (residues + shells) / potential if potential else 0.0,
        "B1": sum(rev.values()) / (cc / 1000),
        "B2": (rev["seaweed"] + rev["mussels"]) / sum(rev.values()),
    }
    kpis = []
    for k, (name, unit, better, target) in KPI_DEF.items():
        v = val[k]
        met = v <= target if better == "lower" else v >= target
        kpis.append({"scenario": code, "id": k, "kpi": name, "unit": unit, "value": v,
                     "better_if": better, "target": target, "met": met})
    return {"code": code, "climate_total": cc, "eutrophication_total": eu, "share_fish": share,
            "contrib": contrib, "nutrients": nb, "kpis": kpis}


def run_all(factors=None):
    inv, par, fac = load(factors)
    return {code: evaluate(code, x, par, fac) for code, x in sorted(inv.items())}
