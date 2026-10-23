"""Transcribe INTEGRATE deliverable PI05#3 (Table 4, Table 5, Annex 1) into data/report/*.csv and build the LCIS2024 LCI in data/lci/.

Every number below is typed from the report; the page and table are given in the CSV "source" column."""
import csv, uuid
from pathlib import Path
import networkx as nx

R = Path(__file__).resolve().parent
D = R / "data" / "report"; D.mkdir(parents=True, exist_ok=True)
SYS = ["SI-IMTA", "SE-IMTA", "SI-POLY"]

# ---------------- Table 4 (per production pond, per cycle) ----------------
T4 = [
 ("cycle_length", "months", 5.3, 8.5, 26, "Table 4"),
 ("feed", "kg", 1888, 89, 10975, "Table 4"),
 ("seawater_used", "m3", 101110, 7185, 1201764, "Table 4"),
 ("fish_stocked", "kg", 677, 45, 91, "Table 4 (initial fish biomass)"),
 ("oyster_stocked", "kg flesh", 5.5, 14.4, 0, "Table 4 (initial oyster flesh biomass)"),
 ("diet_protein", "%", 42, 40, 42, "Table 4"),
 ("diet_lipid", "%", 18, 18, 18, "Table 4"),
 ("diet_cellulose", "%", 3, 3.5, 3, "Table 4"),
 ("diet_ash", "%", 9, 9, 9, "Table 4"),
 ("diet_phosphorus", "%", 1.4, 1.3, 1.4, "Table 4"),
 ("farm_area", "m2", 90000, 285000, 90000, "Table 4"),
 ("farm_pond_area", "m2", 23600, 200000, 23600, "Table 4"),
 ("production_pond_area", "m2", 700, 665, 1700, "Table 4"),
 ("fish_gain", "kg", 1099, 65, 6137, "Table 4"),
 ("oyster_gain", "kg flesh", 130, 94, 0, "Table 4"),
 ("macroalgae_gain", "kg", 1224, 35400, 0, "Table 4 (associated downstream production)"),
 ("fcr_reported", "-", 1.72, 0.56, 1.79, "Table 4"),
]
with open(D / "inventory_table4.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["parameter", "unit", *SYS, "source"])
    w.writerows(T4)

# ---------------- Table 5 (N and P, per pond per cycle) ----------------
T5 = [
 ("feed", "N", 126.9, 5.7, 737.5), ("feed", "P", 26.4, 1.2, 153.7),
 ("produced_biomass", "N", 29.0, 4.5, 148.8), ("produced_biomass", "P", 5.9, 1.0, 25.0),
 ("downstream_macroalgae", "N", 30.6, 1.8, 0), ("downstream_macroalgae", "P", 2.6, 0.1, 0),
 ("total_extracted", "N", 59.6, 6.2, 148.8), ("total_extracted", "P", 8.5, 1.1, 25.0),
 ("total_rejection", "N", 67.2, -0.5, 588.7), ("total_rejection", "P", 18.0, 0.0, 128.7),
 ("rejection_per_kg_product", "N", 0.055, -0.003, 0.10), ("rejection_per_kg_product", "P", 0.015, 0.000, 0.021),
]
with open(D / "nutrients_table5.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["item", "element", *SYS, "unit", "source"])
    for it, el, *v in T5:
        w.writerow([it, el, *v, "kg/kg" if it.startswith("rejection_per") else "kg", "Table 5"])

# ---------------- Annex 1 (per tonne of fish + oyster) ----------------
PROC = ["Building impact", "Energy consumption", "Water consumption", "Vehicle", "Rejects fish", "Chemical products",
        "Equipment", "Fry", "Feeds", "Transports", "Direct activity"]
CAT = {
 "GW":   ("Global warming (GWP100)", "kg CO2-eq", {
   "SI-IMTA": ([137, 330, 0, 32, 0, 0, 386, 43, 1549, 325, 0], [4.9, 11.8, 0, 1.1, 0, 0, 13.8, 1.5, 55.3, 11.6, 0], 2801),
   "SE-IMTA": ([12, 6, 0, 8, 0, 30, 228, 29, 733, 208, 0], [1.0, .5, 0, .6, 0, 2.4, 18.2, 2.3, 58.4, 16.6, 0], 1255),
   "SI-POLY": ([13, 474, 0, 80, 0, 0, 15, 1, 1873, 379, 0], [.5, 16.7, 0, 2.8, 0, 0, .5, 0, 66.0, 13.4, 0], 2836)}),
 "TCED": ("Total cumulative energy demand", "MJ-eq", {
   "SI-IMTA": ([2701, 45724, 0, 700, 0, 0, 14023, 469, 21028, 5483, 0], [3.0, 50.7, 0, .8, 0, 0, 15.6, .5, 23.3, 6.1, 0], 90127),
   "SE-IMTA": ([240, 82, 0, 150, 0, 664, 6248, 316, 7900, 3497, 0], [1.3, .4, 0, .8, 0, 3.5, 32.7, 1.7, 41.4, 18.3, 0], 19097),
   "SI-POLY": ([263, 65724, 0, 1749, 0, 0, 555, 12, 25185, 6409, 0], [.3, 65.8, 0, 1.8, 0, 0, .6, 0, 25.2, 6.4, 0], 99897)}),
 "NPPU": ("Net primary production use", "kg C", {
   "SI-IMTA": ([0, 0, 0, 0, 0, 0, 0, 55, 10423, 0, 0], [0, 0, 0, 0, 0, 0, 0, .5, 99.5, 0, 0], 10478),
   "SE-IMTA": ([0, 0, 0, 0, 0, 0, 0, 37, 4365, 0, 0], [0, 0, 0, 0, 0, 0, 0, .8, 99.2, 0, 0], 4402),
   "SI-POLY": ([0, 0, 0, 0, 0, 0, 0, 1, 12357, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, None, 0, 0], 12358)}),
 "AP":   ("Acidification", "kg SO2-eq", {
   "SI-IMTA": ([1, 2, 0, 1, 25, 0, 3, 0, 8, 2, 0], [3.0, 4.6, 0, 1.7, 59.1, 0, 7.3, .8, 19.2, 4.4, 0], 42),
   "SE-IMTA": ([0, 0, 0, 0, 0, 0, 1, 0, 3, 1, 0], [1.8, 1.1, 0, .8, 0, 2.4, 16.5, 3.7, 53.3, 20.4, 0], 6),
   "SI-POLY": ([0, 3, 0, 0, 29, 0, 0, 0, 10, 2, 0], [.3, 6.2, 0, .2, 65.5, 0, .3, 0, 23.0, 4.6, 0], 45)}),
 "EP":   ("Eutrophication", "kg PO4-eq", {
   "SI-IMTA": ([0, 1, 0, 0, 16, 0, 1, 0, 8, 0, 0], [.5, 2.3, 0, .2, 61.0, 0, 4.1, 1.2, 29.2, 1.5, 0], 26),
   "SE-IMTA": ([0, 0, 0, 0, -1, 0, 0, 0, 3, 0, 0], [.6, .7, 0, .2, None, 4.8, 4.0, 10.1, None, 12.1, 0], 2),
   "SI-POLY": ([0, 1, 0, 0, 51, 0, 0, 0, 8, 0, 0], [0, 1.4, 0, .3, 83.8, 0, .1, 0, 13.7, .7, 0], 61)}),
 "LC":   ("Land competition", "m2a", {
   "SI-IMTA": ([4, 8, 0, 1, 0, 0, 6, 40, 1942, 4, 941], [.1, .3, 0, 0, 0, 0, .2, 1.3, 65.9, .1, 31.9], 2946),
   "SE-IMTA": ([0, 0, 0, 0, 0, 0, 0, 27, 660, 3, 4194], [0, 0, 0, 0, 0, 0, 0, .5, 13.5, .1, 85.9], 4885),
   "SI-POLY": ([0, 12, 0, 2, 0, 0, 0, 1, 1897, 5, 460], [0, .5, 0, .1, 0, 0, 0, 0, 79.8, .2, 19.3], 2379)}),
 "WD":   ("Water dependence", "m3", {
   "SI-IMTA": ([1, 38, 82261, 1, 0, 0, 6, 148, 47, 3, 81336], [0, 0, 50.2, 0, 0, 0, 0, .1, 0, 0, 49.6], 163840),
   "SE-IMTA": ([0, 0, 45273, 0, 0, 1, 5, 100, 14, 2, 70297], [0, 0, 39.1, 0, 0, 0, 0, .1, 0, 0, 60.8], 115691),
   "SI-POLY": ([0, 54, 195829, 1, 0, 0, 0, 4, 44, 3, 197067], [0, 0, 49.8, 0, 0, 0, 0, 0, 0, 0, 50.1], 393002)}),
}
with open(D / "lcia_annex1.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["category", "category_name", "unit", "system", "process", "amount", "percent", "source"])
    for c, (cn, u, d) in CAT.items():
        for s in SYS:
            a, p, tot = d[s]
            for pr, x, y in zip(PROC, a, p):
                w.writerow([c, cn, u, s, pr, x, "" if y is None else y, "Annex 1"])
            w.writerow([c, cn, u, s, "Total", tot, 100, "Annex 1"])

with open(D / "systems.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["system", "name", "location", "species", "period", "water_exchange"])
    w.writerows([
     ["SI-IMTA", "Semi-intensive pond IMTA", "IPMA Aquaculture Research Station (EPPO), Olhao, Portugal",
      "meagre, white seabream, flathead mullet + Pacific oyster (triploid) + macroalgae (Ulva spp.)", "9 May - 16 Oct 2017", "pumped, 20-150 % of pond volume per day"],
     ["SE-IMTA", "Semi-extensive pond IMTA", "Estero Natural, Cadiz, Spain",
      "gilthead seabream + Pacific oyster + macroalgae (Ulva, Gracilaria) in a second pond", "21 Jan - 5 Nov 2019", "tidal"],
     ["SI-POLY", "Semi-intensive fishpond polyculture (conventional, fish only)", "IPMA Aquaculture Research Station (EPPO), Olhao, Portugal",
      "meagre + gilthead seabream", "27 May 2017 - 25 Jul 2019", "pumped, 20-150 % of pond volume per day"]])

# ---------------- LCIS2024 foreground LCI (per tonne fish + oyster) ----------------
inv = {r[0]: dict(zip(SYS, r[2:5])) for r in T4}
L = R / "data" / "lci"
rows, G = [], nx.DiGraph()
NAMES = {"SI-IMTA": "Semi-intensive pond IMTA", "SE-IMTA": "Semi-extensive pond IMTA", "SI-POLY": "Semi-intensive fishpond polyculture"}
for s in SYS:
    prod = inv["fish_gain"][s] + inv["oyster_gain"][s]
    k = 1000 / prod
    ap = (f"{NAMES[s]}, 1 t aquatic product (fish + oyster flesh), one cycle", s.lower(), "PT" if s != "SE-IMTA" else "ES", "t")
    nutr = {r[0] + "_" + r[1]: dict(zip(SYS, r[2:5])) for r in T5}

    def add(name, typ, amt, unit, comment):
        rows.append([*ap, name, typ, round(amt, 4), unit, comment])
        G.add_edge(name if typ != "production" else ap[0], ap[0] if typ != "production" else name, amount=round(amt, 4), unit=unit, type=typ)
    add("aquatic product (fish + oyster flesh), at farm gate", "production", 1, "t", "reference flow = functional unit")
    add("fish, live weight gain", "production", inv["fish_gain"][s] * k, "kg", "Table 4 x scaling")
    if inv["oyster_gain"][s]:
        add("oyster flesh, weight gain", "production", inv["oyster_gain"][s] * k, "kg", "Table 4 x scaling")
    if inv["macroalgae_gain"][s]:
        add("macroalgae, biomass gain", "co-product (outside FU)", inv["macroalgae_gain"][s] * k, "kg", "associated downstream production; not part of the functional unit")
    add("compound fish feed", "technosphere", inv["feed"][s] * k, "kg", f"{inv['diet_protein'][s]} % protein, {inv['diet_phosphorus'][s]} % P")
    add("fish fry / fingerlings", "technosphere", inv["fish_stocked"][s] * k, "kg", "Fry process in Piscentool used a carp-fry proxy")
    if inv["oyster_stocked"][s]:
        add("oyster spat (flesh)", "technosphere", inv["oyster_stocked"][s] * k, "kg", "")
    add("seawater, pumped or tidal", "resource", inv["seawater_used"][s] * k, "m3", "Table 4 x scaling (matches Water consumption in Annex 1)")
    add("land occupation, farm area allocated to the pond", "resource",
        inv["farm_area"][s] * inv["production_pond_area"][s] / inv["farm_pond_area"][s] * inv["cycle_length"][s] / 12 * k, "m2a",
        "farm area x pond share x cycle length (report allocation rule); compare Direct activity in Annex 1 LC")
    for el in ("N", "P"):
        add(f"{'Nitrogen' if el == 'N' else 'Phosphorus'}, to water (net rejection)", "emission",
            nutr[f"total_rejection_{el}"][s] * k, "kg", "Table 5 nutrient balance (Cho & Kaushik 1990); negative = net uptake")
(L / "dataset").mkdir(parents=True, exist_ok=True)
with open(L / "dataset" / "imta-integrate-lci.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ap_name", "ap_code", "ap_location", "ap_unit", "fp_name", "fp_type", "fp_amount", "fp_unit", "fp_comment"])
    w.writerows(rows)
PAR = [("protein_to_N", 6.25, "-", "standard", "N = protein / 6.25 (reproduces Table 5 feed N exactly)"),
       ("improvement_target", 0.10, "-", "assumption", "environmental KPI target: at least 10 % better than the conventional polyculture"),
       ("functional_unit", 1000, "kg", "report", "1 t aquatic product = fish + oyster flesh weight gain")]
with open(L / "dataset" / "parameters.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["par_name", "par_amount", "par_unit", "par_status", "par_comment"]); w.writerows(PAR)
(L / "network").mkdir(exist_ok=True)
nx.write_graphml(G, L / "network" / "imta-integrate-lci.graphml")

ts = "20261023-220000"; NAME = "imta-integrate-lci"; VER = "1.0.0"
udi_name = f"{NAME}-LCIS2024-{VER}-{ts}"
with open(L / "dataset_properties.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["property", "value"])
    w.writerows([["name", NAME], ["version", VER], ["schema_version", "LCIS2024"], ["creation_time", ts], ["udi_name", udi_name],
                 ["udi", str(uuid.uuid5(uuid.NAMESPACE_URL, udi_name))], ["software", "Piscentool (original study); Python 3.11; Excel"],
                 ["external_datasets", "Piscentool / SimaPro background (not redistributed)"], ["count_activities", 3],
                 ["count_flows", len(rows)], ["count_parameters", len(PAR)]])
print(len(rows), "LCI rows")
