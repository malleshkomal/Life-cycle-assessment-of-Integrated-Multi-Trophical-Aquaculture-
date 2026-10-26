"""Build the offline Excel KPI tool excel/IMTA_KPI_decision_tool.xlsx from data/report/*.csv.

Every result cell is a live formula; the yellow cells hold the report's numbers and can be changed.
Recalculate with LibreOffice (or just open the file in Excel) to see the values.
"""
import csv
import sys
from io import BytesIO
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, RadarChart, Reference, Series
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.series import SeriesLabel
from openpyxl.drawing.image import Image
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from PIL import Image as PILImage

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from imtakpi import KPI_DEF, SYSTEMS, NAMES, CATEGORIES  # noqa: E402
from imtakpi.model import IMPROVEMENT  # noqa: E402

D = ROOT / "data" / "report"
F = "Arial"
TITLE, BOLD, NORM = Font(name=F, size=14, bold=True), Font(name=F, bold=True), Font(name=F)
BLUE, ITAL = Font(name=F, color="0000FF"), Font(name=F, italic=True, color="595959")
HFILL, HFONT = PatternFill("solid", fgColor="0F6E56"), Font(name=F, bold=True, color="FFFFFF")
SFILL, YFILL = PatternFill("solid", fgColor="E1F5EE"), PatternFill("solid", fgColor="FFF2CC")
GOOD, BAD = PatternFill("solid", fgColor="C6EFCE"), PatternFill("solid", fgColor="FFC7CE")
th = Side(style="thin", color="BFBFBF")
BOX = Border(top=th, bottom=th, left=th, right=th)
COLS = ["C", "D", "E"]                      # SI-IMTA, SE-IMTA, SI-POLY
SRC = "Source: INTEGRATE deliverable PI05#3 (IPMA & CTAQUA, 2020)"
SYS_COLOR = {"SI-IMTA": "1D9E75", "SE-IMTA": "378ADD", "SI-POLY": "888780"}
GROUPS = [("Feeds", ["Feeds"], "534AB7"), ("Rejects fish (uneaten feed, excretion)", ["Rejects fish"], "E24B4A"),
          ("Energy consumption", ["Energy consumption"], "EF9F27"), ("Transports", ["Transports"], "378ADD"),
          ("Equipment", ["Equipment"], "5F5E5A"), ("Direct activity (farm area, water mgmt.)", ["Direct activity"], "1D9E75"),
          ("Water consumption", ["Water consumption"], "85B7EB"),
          ("Other (buildings, vehicles, chemicals, fry)", ["Building impact", "Vehicle", "Chemical products", "Fry"], "D3D1C7")]
CAT_NAMES = {"GW": "Global warming", "TCED": "Cumulative energy demand", "NPPU": "Net primary production use",
             "AP": "Acidification", "EP": "Eutrophication", "LC": "Land competition", "WD": "Water dependence"}

wb = Workbook()


def sheet(name, title, note=SRC):
    ws = wb.create_sheet(name)
    ws["A1"], ws["A1"].font = title, TITLE
    ws["A2"], ws["A2"].font = note, ITAL
    return ws


def header(ws, r, labels):
    for i, lab in enumerate(labels):
        c = ws.cell(row=r, column=i + 1, value=lab)
        c.font, c.fill, c.border = HFONT, HFILL, BOX
        c.alignment = Alignment(wrap_text=True, vertical="center")


def section(ws, r, text, n=6):
    for i in range(n):
        ws.cell(row=r, column=i + 1).fill = SFILL
    ws.cell(row=r, column=1, value=text).font = BOLD


def put(ws, ref, v, fmt="#,##0.00", inp=False, bold=False):
    c = ws[ref]
    c.value, c.number_format, c.border = v, fmt, BOX
    c.font = BLUE if inp else (BOLD if bold else NORM)
    if inp:
        c.fill = YFILL
    return c


def widths(ws, d):
    for k, v in d.items():
        ws.column_dimensions[k].width = v


def color(series, hex_):
    series.graphicalProperties.solidFill = hex_
    series.graphicalProperties.line.solidFill = hex_


def bars_down(ch, lo=None, hi=None):
    """Horizontal bars listed top to bottom, labels clear of negative bars."""
    ch.x_axis.scaling.orientation, ch.x_axis.tickLblPos = "maxMin", "low"
    ch.y_axis.scaling.min, ch.y_axis.scaling.max = lo, hi
    return ch


def band(ws, r, text, ncols, fill="0F6E56", size=12, first=1, tall=False):
    """A coloured title band across ncols columns (tall=False keeps the row height, so pictures and charts stay anchored)."""
    for j in range(first, first + ncols):
        ws.cell(row=r, column=j).fill = PatternFill("solid", fgColor=fill)
    c = ws.cell(row=r, column=first, value=text)
    c.font, c.alignment = Font(name=F, bold=True, size=size, color="FFFFFF"), Alignment(vertical="center")
    if tall:
        ws.row_dimensions[r].height = 24
    return c


def labels(ch):
    ch.dataLabels = DataLabelList()
    ch.dataLabels.showVal = True
    for k in ("showSerName", "showCatName", "showLegendKey", "showPercent", "showBubbleSize", "showLeaderLines"):
        setattr(ch.dataLabels, k, False)
    return ch


def chart_size(ch, w=18, h=9):
    ch.width, ch.height = w, h
    return ch


def rows(name):
    with open(D / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


SYSHEAD = [NAMES[s] for s in SYSTEMS]

# ------------------------------------------------------------------ README (filled in at the end, once every tab exists)
rd = wb.active
rd.title = "README"

# ------------------------------------------------------------------ Goal & scope
gs = sheet("Goal & scope", "Life cycle assessment of pond IMTA and fish polyculture - goal and scope (ISO 14040/44)")
header(gs, 4, ["Item", "Choice in the study", "Note"])
gsrows = [
    ("Goal", "Compare the potential environmental impacts of semi-intensive and semi-extensive pond IMTA with a conventional semi-intensive fishpond polyculture.", "INTEGRATE project (Interreg Atlantic Area, EAPA_232/2016), WP5 Action 2"),
    ("Functional unit", "1 tonne of aquatic product (fish + oyster flesh weight gain) at the farm gate, one production cycle", "Macroalgae are an associated downstream product and are not part of the functional unit"),
    ("System boundary", "Farm operation plus production of inputs: fry and oyster spat, feeds, energy, equipment, buildings, vehicles, chemicals, transport; emissions from uneaten feed and excretion", "Packaging and transport to the retailer excluded (not full cradle-to-gate)"),
    ("Allocation", "None between fish and oysters (mass sum); infrastructure, vehicles and electricity allocated by production-pond area / total pond area", "See Hala, Chougule et al. (2024) for why allocation is a key IMTA challenge"),
    ("Nutrient emissions", "Nutrient balance: N and P in feed minus N and P retained in harvested biomass (Cho & Kaushik 1990)", "Table 5"),
    ("Software", "Piscentool (Excel interface, project Piscenlit; Wilfart et al. 2012), SimaPro background", "Fry: carp-fry LCA profile used as default"),
    ("Impact categories", "GW kg CO2-eq; TCED MJ-eq; NPPU kg C; Acidification kg SO2-eq; Eutrophication kg PO4-eq; Land competition m2a; Water dependence m3", "CML-type midpoints with the aquaculture-specific NPPU and WD"),
    ("Data", "Primary data from daily farm records (water renewal, aeration, feed, mortality), feed supplier data, facility records", "Experimental-scale ponds (665-1,700 m2)"),
    ("Baseline", "Semi-intensive fishpond polyculture (fish only)", "Annex 1 labels it 'Semi-intensive MONO'"),
]
for i, (a, b, c) in enumerate(gsrows):
    for j, v in enumerate((a, b, c)):
        cell = gs.cell(row=5 + i, column=1 + j, value=v)
        cell.font, cell.border = (BOLD if j == 0 else NORM), BOX
        cell.alignment = Alignment(wrap_text=True, vertical="top")
widths(gs, {"A": 20, "B": 80, "C": 55})

# ------------------------------------------------------------------ Metadata
md = sheet("Metadata", "Metadata (LCIS2024 structure, Nair, Chougule et al. 2025)")
header(md, 4, ["Element", "Label", "Value"])
props = {r["property"]: r["value"] for r in rows("../lci/dataset_properties.csv")}
mrows = [("Dataset", "Name", props["name"]), ("Dataset", "Version", props["version"]), ("Dataset", "UDI", props["udi"]),
         ("Dataset", "Description", "Foreground LCI and LCIA results of three earthen-pond aquaculture systems from INTEGRATE deliverable PI05#3"),
         ("Dataset", "Functional unit", "1 t aquatic product (fish + oyster flesh) at farm gate"),
         ("Dataset", "Region", "Portugal (Olhao, Ria Formosa) and Spain (Cadiz)"),
         ("Dataset", "Time period", "2017-2019 (one production cycle per system)"),
         ("Source", "Report", "LCA of aquaculture systems: comparison between semi-intensive/extensive pond IMTA and semi-intensive traditional fishpond production. Deliverable PI05#3, submitted 23/07/2020"),
         ("Source", "Lead / contributing partners", "IPMA; IPMA and CTAQUA"),
         ("Source", "Software", "Piscentool"),
         ("Licence", "Data", "Report data belong to the INTEGRATE partners; KPI layer CC BY 4.0"),
         ("Licence", "Code", "MIT"),
         ("Glossary", "Abbreviations", "IMTA integrated multi-trophic aquaculture; POLY polyculture; SI semi-intensive; SE semi-extensive; FCR feed conversion ratio; NPPU net primary production use; TCED total cumulative energy demand; WD water dependence; LC land competition")]
for i, r in enumerate(mrows):
    for j, v in enumerate(r):
        c = md.cell(row=5 + i, column=1 + j, value=v)
        c.font, c.border = NORM, BOX
        c.alignment = Alignment(wrap_text=True, vertical="top")
widths(md, {"A": 14, "B": 26, "C": 110})

# ------------------------------------------------------------------ Inventory
inv = sheet("Inventory", "Inventory - Table 4 of the report (per production pond and cycle) and scaling to the functional unit")
header(inv, 4, ["Parameter", "Unit", *SYSHEAD, "Source / note"])
R = {}  # key -> row
r = 5
for row in rows("inventory_table4.csv"):
    R[row["parameter"]] = r
    inv.cell(row=r, column=1, value=row["parameter"].replace("_", " ")).font = NORM
    inv.cell(row=r, column=2, value=row["unit"]).font = NORM
    for col, s in zip(COLS, SYSTEMS):
        put(inv, f"{col}{r}", float(row[s]), "#,##0.0#", inp=True)
    inv.cell(row=r, column=6, value=row["source"]).font = ITAL
    r += 1
r += 1
section(inv, r, "Scaling to the functional unit (formulas)")
r += 1
derived = [
    ("product", "fish + oyster flesh gain", "kg", "={c}%d+{c}%d" % (R["fish_gain"], R["oyster_gain"]), "functional unit basis"),
    ("scale", "scaling factor to 1 t", "-", "=1000/{c}%d", "1,000 kg / product"),
    ("fcr_fish", "FCR, feed / fish gain", "kg/kg", "={c}%d/{c}%d" % (R["feed"], R["fish_gain"]), "compare with reported FCR"),
    ("fcr_all", "feed / (fish + oyster gain)", "kg/kg", "={c}%d/{c}%%d" % R["feed"], "explains the reported 0.56 of the semi-extensive IMTA"),
    ("land", "farm area allocated to the pond x cycle", "m2a", "={c}%d*{c}%d/{c}%d*{c}%d/12" % (R["farm_area"], R["production_pond_area"], R["farm_pond_area"], R["cycle_length"]), "report rule: pond area / total pond area"),
]
for key, lab, unit, f, note in derived:
    R[key] = r
    if key == "scale":
        f = f % R["product"]
    if key == "fcr_all":
        f = f % R["product"]
    inv.cell(row=r, column=1, value=lab).font = NORM
    inv.cell(row=r, column=2, value=unit).font = NORM
    for col in COLS:
        put(inv, f"{col}{r}", f.format(c=col), "#,##0.00##")
    inv.cell(row=r, column=6, value=note).font = ITAL
    r += 1
widths(inv, {"A": 38, "B": 10, "C": 22, "D": 22, "E": 22, "F": 60})
inv.freeze_panes = "C5"

# ------------------------------------------------------------------ Nutrient balance
nb = sheet("Nutrient balance", "Nutrient balance - where the N and P in the feed go (per pond and cycle, Table 5)")
header(nb, 4, ["Item", "Unit", *SYSHEAD, "Source / note"])
t5 = {(x["item"], x["element"]): x for x in rows("nutrients_table5.csv")}
NB = {}
r = 5
put(nb, f"A{r}", "protein to N factor", "@")
put(nb, f"C{r}", 6.25, "0.00", inp=True)
nb[f"F{r}"], nb[f"F{r}"].font = "N = protein / 6.25", ITAL
NB["k"] = r
r += 2
for el in ("N", "P"):
    section(nb, r, f"{'Nitrogen' if el == 'N' else 'Phosphorus'} (kg {el})")
    r += 1
    NB[(el, "feed")] = r
    nb.cell(row=r, column=1, value=f"{el} in feed")
    nb.cell(row=r, column=2, value="kg")
    for col in COLS:
        f = (f"=Inventory!{col}{R['feed']}*Inventory!{col}{R['diet_protein']}/100/$C${NB['k']}" if el == "N"
             else f"=Inventory!{col}{R['feed']}*Inventory!{col}{R['diet_phosphorus']}/100")
        put(nb, f"{col}{r}", f)
    nb[f"F{r}"], nb[f"F{r}"].font = "formula from feed and recipe", ITAL
    r += 1
    for item, lab in (("produced_biomass", f"{el} in fish + oysters"), ("downstream_macroalgae", f"{el} in macroalgae")):
        NB[(el, item)] = r
        nb.cell(row=r, column=1, value=lab)
        nb.cell(row=r, column=2, value="kg")
        for col, s in zip(COLS, SYSTEMS):
            put(nb, f"{col}{r}", float(t5[(item, el)][s]), "#,##0.0", inp=True)
        nb[f"F{r}"], nb[f"F{r}"].font = "Table 5", ITAL
        r += 1
    calc = [("released", f"{el} released to water (net)", "={c}%d-{c}%d-{c}%d" % (NB[(el, "feed")], NB[(el, "produced_biomass")], NB[(el, "downstream_macroalgae")]), "#,##0.0", "negative = net uptake from the environment"),
            ("reported", f"{el} rejection reported", None, "#,##0.0", "Table 5, for comparison"),
            ("eff", f"{el} use efficiency", "=({c}%d+{c}%d)/{c}%d" % (NB[(el, "produced_biomass")], NB[(el, "downstream_macroalgae")], NB[(el, "feed")]), "0.0%", "N or P in all products / N or P in feed"),
            ("per_t", f"{el} released per t product", "={c}%d*Inventory!{c}%d", "#,##0.00", "kg per tonne fish + oyster")]
    for key, lab, f, fmt, note in calc:
        NB[(el, key)] = r
        nb.cell(row=r, column=1, value=lab)
        nb.cell(row=r, column=2, value="kg" if key != "eff" else "%")
        for col, s in zip(COLS, SYSTEMS):
            if key == "reported":
                put(nb, f"{col}{r}", float(t5[("total_rejection", el)][s]), fmt, inp=True)
            elif key == "per_t":
                put(nb, f"{col}{r}", f.format(c=col) % (NB[(el, "released")], R["scale"]), fmt, bold=True)
            else:
                put(nb, f"{col}{r}", f.format(c=col), fmt, bold=(key == "eff"))
        nb[f"F{r}"], nb[f"F{r}"].font = note, ITAL
        r += 1
    r += 1
widths(nb, {"A": 34, "B": 8, "C": 22, "D": 22, "E": 22, "F": 48})

# ------------------------------------------------------------------ LCI per tonne
lci = sheet("LCI per tonne", "Foreground LCI per functional unit (1 t fish + oyster flesh) - inputs and outputs, all formulas")
lci["A3"], lci["A3"].font = ("Table 1 INPUTS = what the farm takes in. Table 2 OUTPUTS = what leaves the farm. "
                             "Amounts per tonne of fish + oyster flesh; all values are formulas on the Inventory and Nutrient balance tabs."), ITAL
scaled = lambda k: "=Inventory!{c}%d*Inventory!{c}%d" % (R[k], R["scale"])  # noqa: E731
IO = {"INPUTS": ("185FA5", "E6F1FB"), "OUTPUTS": ("0F6E56", "E1F5EE")}
tables = [
    ("INPUTS", "1  INPUTS - what the farm takes in", [
        ("From the technosphere (products of other processes)", [
            ("compound fish feed", "technosphere", scaled("feed"), "kg", "40-42 % protein"),
            ("fish fry / fingerlings", "technosphere", scaled("fish_stocked"), "kg", "carp-fry proxy in Piscentool"),
            ("oyster spat (flesh)", "technosphere", scaled("oyster_stocked"), "kg", "")]),
        ("From nature (resources)", [
            ("seawater, pumped or tidal", "resource", scaled("seawater_used"), "m3", "equals Water consumption in Annex 1"),
            ("land, farm area allocated to the pond", "resource", scaled("land"), "m2a", "compare Direct activity, Land competition")]),
        ("Included in the impact results, but the report gives no quantities", [
            (name, "technosphere", None, "", f"only its impacts are reported: process '{proc}' in LCIA (Annex 1)")
            for name, proc in (("electricity / fuel for pumping and aeration", "Energy consumption"),
                               ("equipment (pumps, aerators, nets)", "Equipment"), ("buildings", "Building impact"),
                               ("vehicles", "Vehicle"), ("chemical products", "Chemical products"),
                               ("transport of inputs", "Transports"))]),
    ]),
    ("OUTPUTS", "2  OUTPUTS - what leaves the farm", [
        ("Products (the functional unit)", [
            ("aquatic product, fish + oyster flesh, at farm gate", "reference product", "=1", "t", "functional unit"),
            ("fish, live weight gain", "product", scaled("fish_gain"), "kg", "part of the 1 t"),
            ("oyster flesh, weight gain", "product", scaled("oyster_gain"), "kg", "part of the 1 t")]),
        ("Co-product (outside the functional unit)", [
            ("macroalgae, biomass gain", "co-product", scaled("macroalgae_gain"), "kg", "harvested; not allocated any burden")]),
        ("Emissions to nature", [
            ("nitrogen, to water (net)", "emission", "='Nutrient balance'!{c}%d" % NB[("N", "per_t")], "kg N", "negative = net uptake from the water"),
            ("phosphorus, to water (net)", "emission", "='Nutrient balance'!{c}%d" % NB[("P", "per_t")], "kg P", "negative = net uptake from the water")]),
    ]),
]
LCI = {}
rr = 5
for io, title, groups in tables:
    dark, light = IO[io]
    band_fill = PatternFill("solid", fgColor=dark)
    for j in range(1, 8):
        lci.cell(row=rr, column=j).fill = band_fill
    lci.cell(row=rr, column=1, value=title).font = Font(name=F, bold=True, size=13, color="FFFFFF")
    lci.row_dimensions[rr].height = 22
    rr += 1
    for j, lab in enumerate(["Flow (fp_name)", "Kind", *SYSHEAD, "Unit", "Comment"]):
        c = lci.cell(row=rr, column=1 + j, value=lab)
        c.font, c.fill, c.border = Font(name=F, bold=True, color=dark), PatternFill("solid", fgColor=light), BOX
        c.alignment = Alignment(wrap_text=True, vertical="center")
    rr += 1
    for sub, items in groups:
        lci.cell(row=rr, column=1, value=sub).font = Font(name=F, bold=True, italic=True, color=dark)
        rr += 1
        for name, kind, f, unit, note in items:
            LCI[name] = rr
            c = lci.cell(row=rr, column=1, value="   " + name)
            c.font, c.border = NORM, BOX
            c = lci.cell(row=rr, column=2, value=kind)
            c.font, c.border = Font(name=F, color=dark), BOX
            for col in COLS:
                if f is None:
                    put(lci, f"{col}{rr}", "n/a", "@").alignment = Alignment(horizontal="right")
                else:
                    put(lci, f"{col}{rr}", f.format(c=col), "#,##0.0")
            lci.cell(row=rr, column=6, value=unit).font = NORM
            lci.cell(row=rr, column=7, value=note).font = ITAL
            rr += 1
    rr += 2
widths(lci, {"A": 48, "B": 18, "C": 22, "D": 22, "E": 22, "F": 8, "G": 52})
lci.freeze_panes = "C5"

# ------------------------------------------------------------------ LCIA (Annex 1)
la = sheet("LCIA (Annex 1)", "Life cycle impact assessment per tonne of fish + oyster - Annex 1 of the report (Piscentool)")
la["A3"], la["A3"].font = "Amounts are as printed (rounded to whole units); shares are calculated from the reported total.", ITAL
header(la, 4, ["Process", "Unit", *SYSHEAD, "", "Share SI-IMTA", "Share SE-IMTA", "Share POLY"])
ann = rows("lcia_annex1.csv")
PROCS = [p for p in dict.fromkeys(x["process"] for x in ann) if p != "Total"]
LA = {}
r = 5
for cat in CATEGORIES:
    sub = [x for x in ann if x["category"] == cat]
    unit = sub[0]["unit"]
    section(la, r, f"{cat} - {sub[0]['category_name']} ({unit})", 9)
    r += 1
    first = r
    for p in PROCS:
        la.cell(row=r, column=1, value=p).font = NORM
        la.cell(row=r, column=2, value=unit).font = NORM
        for col, s in zip(COLS, SYSTEMS):
            v = next(float(x["amount"]) for x in sub if x["system"] == s and x["process"] == p)
            put(la, f"{col}{r}", v, "#,##0", inp=True)
        LA[(cat, p)] = r
        r += 1
    la.cell(row=r, column=1, value="Sum of processes").font = ITAL
    for col in COLS:
        put(la, f"{col}{r}", f"=SUM({col}{first}:{col}{r - 1})", "#,##0")
    LA[(cat, "sum")] = r
    r += 1
    la.cell(row=r, column=1, value="Total (reported)").font = BOLD
    la.cell(row=r, column=2, value=unit).font = NORM
    for col, s in zip(COLS, SYSTEMS):
        v = next(float(x["amount"]) for x in sub if x["system"] == s and x["process"] == "Total")
        put(la, f"{col}{r}", v, "#,##0", inp=True, bold=True)
    LA[(cat, "Total")] = r
    for rr in range(first, r):
        if rr == LA[(cat, "sum")]:
            continue
        for col, pc in zip(COLS, ("G", "H", "I")):
            put(la, f"{pc}{rr}", f"=IF({col}${r}=0,0,{col}{rr}/{col}${r})", "0.0%")
    r += 2
widths(la, {"A": 24, "B": 11, "C": 18, "D": 18, "E": 18, "F": 2, "G": 13, "H": 13, "I": 13})
la.freeze_panes = "C5"

# ------------------------------------------------------------------ Contribution analysis
ca = sheet("Contribution analysis", "Contribution analysis - which process drives which impact, per tonne of fish + oyster")
ca["A3"], ca["A3"].font = ("All values are formulas on the LCIA (Annex 1) tab. Share = process / sum of the absolute process amounts, "
                           "so a negative share is a removal (net nutrient uptake)."), ITAL


def lcia_sum(col, cat, procs):
    return "+".join(f"'LCIA (Annex 1)'!{col}{LA[(cat, p)]}" for p in procs)


def lcia_abs(col, cat):
    return f"SUMPRODUCT(ABS('LCIA (Annex 1)'!{col}{LA[(cat, PROCS[0])]}:{col}{LA[(cat, PROCS[-1])]}))"


r = 5
section(ca, r, "1  Share of each impact per process group (heatmap) and contribution chart per system", 8)
r += 2
for col, s in zip(COLS, SYSTEMS):
    top = r
    ca.cell(row=r, column=1, value=NAMES[s]).font = Font(name=F, bold=True, color=SYS_COLOR[s])
    r += 1
    header(ca, r, ["Process group", *CATEGORIES])
    hdr = r
    r += 1
    for lab, procs, _ in GROUPS:
        ca.cell(row=r, column=1, value=lab).font = NORM
        for j, cat in enumerate(CATEGORIES):
            ref = ca.cell(row=r, column=2 + j).coordinate
            put(ca, ref, f"=IF({lcia_abs(col, cat)}=0,0,({lcia_sum(col, cat, procs)})/{lcia_abs(col, cat)})", "0%")
        r += 1
    ca.conditional_formatting.add(f"B{hdr + 1}:H{r - 1}", ColorScaleRule(start_type="num", start_value=0, start_color="FFFFFF",
                                                                         end_type="num", end_value=1, end_color="0F6E56"))
    ch = BarChart()
    ch.type, ch.grouping, ch.overlap = "bar", "stacked", 100
    ch.title = f"Contribution per impact category - {NAMES[s]}"
    ch.x_axis.title, ch.y_axis.title, ch.y_axis.number_format = "impact category", "share of impact", "0%"
    for i, (lab, _, hx) in enumerate(GROUPS):
        se = Series(Reference(ca, min_col=2, max_col=8, min_row=hdr + 1 + i), title=lab)
        color(se, hx)
        ch.series.append(se)
    ch.set_categories(Reference(ca, min_col=2, max_col=8, min_row=hdr))
    bars_down(ch, hi=1)
    ca.add_chart(chart_size(ch, 20, 8.5), f"J{top}")
    r = top + 19
section(ca, r, "2  Contribution per impact category, absolute amounts per tonne (stacked by process group)", 8)
r += 2
for cat in CATEGORIES:
    top = r
    unit = next(x["unit"] for x in ann if x["category"] == cat)
    ca.cell(row=r, column=1, value=f"{cat} - {CAT_NAMES[cat]} ({unit} per t)").font = BOLD
    r += 1
    header(ca, r, ["Process group", "", *SYSHEAD])
    hdr = r
    r += 1
    for lab, procs, _ in GROUPS:
        ca.cell(row=r, column=1, value=lab).font = NORM
        for col in COLS:
            put(ca, f"{col}{r}", f"={lcia_sum(col, cat, procs)}", "#,##0")
        r += 1
    ca.cell(row=r, column=1, value="Total (reported)").font = BOLD
    for col in COLS:
        put(ca, f"{col}{r}", f"='LCIA (Annex 1)'!{col}{LA[(cat, 'Total')]}", "#,##0", bold=True)
    ch = BarChart()
    ch.type, ch.grouping, ch.overlap = "col", "stacked", 100
    ch.title, ch.y_axis.title = f"{CAT_NAMES[cat]} by process", f"{unit} per t fish + oyster"
    for i, (lab, _, hx) in enumerate(GROUPS):
        se = Series(Reference(ca, min_col=3, max_col=5, min_row=hdr + 1 + i), title=lab)
        color(se, hx)
        ch.series.append(se)
    ch.set_categories(Reference(ca, min_col=3, max_col=5, min_row=hdr))
    ca.add_chart(chart_size(ch, 20, 8.5), f"J{top}")
    r = top + 19
widths(ca, {"A": 40, "B": 9, "C": 18, "D": 18, "E": 18, "F": 9, "G": 9, "H": 9})

# ------------------------------------------------------------------ Comparison
cp = sheet("Comparison", "Comparison per tonne of fish + oyster, and change against the polyculture baseline")
header(cp, 4, ["Impact category", "Unit", *SYSHEAD, "SI-IMTA vs POLY", "SE-IMTA vs POLY", "Lowest"])
CP = {}
for i, cat in enumerate(CATEGORIES):
    rr = 5 + i
    CP[cat] = rr
    cp.cell(row=rr, column=1, value=f"{cat} - {CAT_NAMES[cat]}").font = NORM
    cp.cell(row=rr, column=2, value=next(x["unit"] for x in ann if x["category"] == cat)).font = NORM
    for col in COLS:
        put(cp, f"{col}{rr}", f"='LCIA (Annex 1)'!{col}{LA[(cat, 'Total')]}", "#,##0")
    put(cp, f"F{rr}", f"=C{rr}/E{rr}-1", "+0%;-0%;0%")
    put(cp, f"G{rr}", f"=D{rr}/E{rr}-1", "+0%;-0%;0%")
    put(cp, f"H{rr}", f'=INDEX($C$4:$E$4,MATCH(MIN(C{rr}:E{rr}),C{rr}:E{rr},0))', "@")
for col in ("F", "G"):
    cp.conditional_formatting.add(f"{col}5:{col}11", CellIsRule(operator="lessThan", formula=["0"], fill=GOOD))
    cp.conditional_formatting.add(f"{col}5:{col}11", CellIsRule(operator="greaterThan", formula=["0"], fill=BAD))
r = 14
section(cp, r, "Implied impact per kg of feed (Feeds process / feed per tonne) - a check that the feed model is consistent", 8)
r += 1
header(cp, r, ["Indicator", "Unit", *SYSHEAD])
for j, (cat, unit) in enumerate((("GW", "kg CO2-eq/kg feed"), ("TCED", "MJ-eq/kg feed"), ("NPPU", "kg C/kg feed"))):
    rr = r + 1 + j
    cp.cell(row=rr, column=1, value=f"{CAT_NAMES[cat]} of feed").font = NORM
    cp.cell(row=rr, column=2, value=unit).font = NORM
    for col in COLS:
        put(cp, f"{col}{rr}", f"='LCIA (Annex 1)'!{col}{LA[(cat, 'Feeds')]}/'LCI per tonne'!{col}{LCI['compound fish feed']}", "0.00")
widths(cp, {"A": 34, "B": 13, "C": 22, "D": 22, "E": 22, "F": 15, "G": 15, "H": 30})
ch = BarChart()
ch.type, ch.grouping, ch.overlap = "bar", "clustered", 0
ch.title, ch.y_axis.title = "Change against fish polyculture (negative = better)", "change"
ch.add_data(Reference(cp, min_col=6, max_col=7, min_row=4, max_row=11), titles_from_data=True)
ch.set_categories(Reference(cp, min_col=1, min_row=5, max_row=11))
ch.height, ch.width, ch.y_axis.number_format = 9, 18, "0%"
cp.add_chart(ch, "A21")

# ------------------------------------------------------------------ KPI framework
kp = sheet("KPI framework", "KPI framework - 13 KPIs per tonne of fish + oyster")
kp["A5"], kp["A5"].font = "Improvement target for environmental KPIs (better than polyculture by at least):", BOLD
put(kp, "F5", IMPROVEMENT, "0%", inp=True)
kp["G5"], kp["G5"].font = "E-targets = polyculture value x (1 - this). Circularity targets are set per KPI (yellow).", ITAL
header(kp, 7, ["ID", "Dimension", "KPI", "Unit", "Better if", "Target",
               *[f"Value {s}" for s in SYSTEMS], *[f"Met {s}" for s in SYSTEMS], "Formula"])
formula_txt = {
    "C1": "(N in fish + oysters + macroalgae) / N in feed", "C2": "(P in fish + oysters + macroalgae) / P in feed",
    "C3": "net N released per pond x scaling factor", "C4": "feed / fish weight gain",
    "C5": "(oyster + macroalgae gain) / total harvest", "C6": "Feeds process / total global warming"}
KP = {}
for i, (kid, dim, name, unit, better, target, cat) in enumerate(KPI_DEF):
    rr = 8 + i
    KP[kid] = rr
    for j, v in enumerate((kid, dim, name, unit, better)):
        c = kp.cell(row=rr, column=1 + j, value=v)
        c.font, c.border = (BOLD if j == 0 else NORM), BOX
    pct = unit == "%"
    fmt = "0.0%" if pct else ("#,##0.00" if kid in ("C3", "C4", "E4", "E5") else "#,##0")
    if cat:
        put(kp, f"F{rr}", f"='LCIA (Annex 1)'!E{LA[(cat, 'Total')]}*(1-$F$5)", fmt)
        for col, vc in zip(COLS, ("G", "H", "I")):
            put(kp, f"{vc}{rr}", f"='LCIA (Annex 1)'!{col}{LA[(cat, 'Total')]}", fmt, bold=True)
        ftxt = f"Annex 1 total; target = polyculture x (1 - improvement)"
    else:
        put(kp, f"F{rr}", target, fmt, inp=True)
        src = {
            "C1": "='Nutrient balance'!{c}%d" % NB[("N", "eff")],
            "C2": "='Nutrient balance'!{c}%d" % NB[("P", "eff")],
            "C3": "='Nutrient balance'!{c}%d" % NB[("N", "per_t")],
            "C4": "=Inventory!{c}%d" % R["fcr_fish"],
            "C5": "=(Inventory!{c}%d+Inventory!{c}%d)/(Inventory!{c}%d+Inventory!{c}%d+Inventory!{c}%d)" % (
                R["oyster_gain"], R["macroalgae_gain"], R["fish_gain"], R["oyster_gain"], R["macroalgae_gain"]),
            "C6": "='LCIA (Annex 1)'!{c}%d/'LCIA (Annex 1)'!{c}%d" % (LA[("GW", "Feeds")], LA[("GW", "Total")]),
        }[kid]
        for col, vc in zip(COLS, ("G", "H", "I")):
            put(kp, f"{vc}{rr}", src.format(c=col), fmt, bold=True)
        ftxt = formula_txt[kid]
    op = "<=" if better == "lower" else ">="
    for vc, mc, s in zip(("G", "H", "I"), ("J", "K", "L"), SYSTEMS):
        if cat and s == "SI-POLY":
            put(kp, f"{mc}{rr}", "baseline", "@")
        else:
            put(kp, f"{mc}{rr}", f'=IF({vc}{rr}{op}$F{rr},"✓","✗")', "@")
        kp[f"{mc}{rr}"].alignment = Alignment(horizontal="center")
    kp.cell(row=rr, column=13, value=ftxt).font = ITAL
last = 8 + len(KPI_DEF) - 1
for mc, vc in zip(("J", "K", "L"), ("G", "H", "I")):
    kp.conditional_formatting.add(f"{mc}8:{mc}{last}", FormulaRule(formula=[f'{mc}8="✓"'], fill=GOOD))
    kp.conditional_formatting.add(f"{mc}8:{mc}{last}", FormulaRule(formula=[f'{mc}8="✗"'], fill=BAD))
    kp.conditional_formatting.add(f"{vc}8:{vc}{last}", FormulaRule(formula=[f'{mc}8="✓"'], fill=GOOD))
    kp.conditional_formatting.add(f"{vc}8:{vc}{last}", FormulaRule(formula=[f'{mc}8="✗"'], fill=BAD))
r = last + 2
put(kp, f"A{r}", "Targets met", "@", bold=True)
for mc in ("J", "K", "L"):
    put(kp, f"{mc}{r}", f'=COUNTIF({mc}8:{mc}{last},"✓")&" / "&COUNTA({mc}8:{mc}{last})', "@", bold=True)
KP["score"] = r
kp[f"A{r + 2}"], kp[f"A{r + 2}"].font = ("Targets are placeholders for a stakeholder workshop. Polyculture environmental KPIs show 'baseline' "
                                         "because the target is defined relative to it."), ITAL
widths(kp, {"A": 6, "B": 12, "C": 36, "D": 13, "E": 9, "F": 12, "G": 14, "H": 14, "I": 14, "J": 10, "K": 10, "L": 10, "M": 52})
kp.freeze_panes = "G8"

# ------------------------------------------------------------------ Dashboard
db = wb.create_sheet("Dashboard")
widths(db, {"A": 2, **{chr(ord("B") + i): 13 for i in range(12)}, "N": 2})
for rr_ in (1, 2):
    for j in range(1, 15):
        db.cell(row=rr_, column=j).fill = PatternFill("solid", fgColor="0F6E56")
db["B1"].value, db["B1"].font = "Dashboard: pond IMTA vs fish polyculture", Font(name=F, bold=True, size=18, color="FFFFFF")
db["B2"].value, db["B2"].font = "Per tonne of fish + oyster flesh · " + SRC + " · all values live", Font(name=F, italic=True, color="E1F5EE")
db.row_dimensions[1].height = 34

# scorecards, one per system
env_rows = [KP[k[0]] for k in KPI_DEF if k[6]]
circ_rows = [KP[k[0]] for k in KPI_DEF if not k[6]]
SITE = {"SI-IMTA": "Olhao, Portugal · fish + oysters + Ulva", "SE-IMTA": "Cadiz, Spain · tidal, fish + oysters + algae pond",
        "SI-POLY": "Olhao, Portugal · fish only (baseline)"}
for (c1, c2), sy, mc in zip((("B", "E"), ("F", "I"), ("J", "M")), SYSTEMS, ("J", "K", "L")):
    hx = SYS_COLOR[sy]
    light = PatternFill("solid", fgColor="F7F7F5")
    edge = Side(style="medium", color=hx)
    rows_ = [(4, NAMES[sy], Font(name=F, bold=True, size=12, color="FFFFFF"), PatternFill("solid", fgColor=hx), 22),
             (5, "KPI targets met", Font(name=F, color="5F5E5A"), light, 16),
             (6, f"='KPI framework'!{mc}{KP['score']}", Font(name=F, bold=True, size=26, color=hx), light, 38),
             (7, f'="Environment "&COUNTIF(\'KPI framework\'!{mc}{min(env_rows)}:{mc}{max(env_rows)},"✓")&" / 7   ·   Circularity "'
                 f'&COUNTIF(\'KPI framework\'!{mc}{min(circ_rows)}:{mc}{max(circ_rows)},"✓")&" / 6"', Font(name=F, bold=True, color="2C2C2A"), light, 18),
             (8, SITE[sy], Font(name=F, italic=True, size=9, color="5F5E5A"), light, 16)]
    for rr_, v, fnt, fill_, h in rows_:
        db.merge_cells(f"{c1}{rr_}:{c2}{rr_}")
        c = db[f"{c1}{rr_}"]
        c.value, c.font, c.alignment = v, fnt, Alignment(horizontal="center", vertical="center")
        db.row_dimensions[rr_].height = h
        for j in range(ord(c1), ord(c2) + 1):
            cc = db[f"{chr(j)}{rr_}"]
            cc.fill = fill_
            cc.border = Border(left=edge if chr(j) == c1 else None, right=edge if chr(j) == c2 else None,
                               top=edge if rr_ == 4 else None, bottom=edge if rr_ == 8 else None)
if sum(1 for _ in env_rows) != 7 or len(circ_rows) != 6:
    raise ValueError("scorecard assumes 7 environmental and 6 circularity KPIs")

# key indicators with the best system highlighted
band(db, 10, "Key indicators per tonne   (green = best of the three)", 12, first=2, tall=True)
hdr_ = 11
for c1, c2, lab in (("B", "E", "Indicator"), ("F", "F", "Unit"), ("G", "H", NAMES["SI-IMTA"]), ("I", "J", NAMES["SE-IMTA"]),
                    ("K", "L", NAMES["SI-POLY"]), ("M", "M", "vs baseline*")):
    if c1 != c2:
        db.merge_cells(f"{c1}{hdr_}:{c2}{hdr_}")
    c = db[f"{c1}{hdr_}"]
    c.value, c.font, c.fill = lab, HFONT, HFILL
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for j in range(ord(c1), ord(c2) + 1):
        db[f"{chr(j)}{hdr_}"].fill, db[f"{chr(j)}{hdr_}"].border = HFILL, BOX
db.row_dimensions[hdr_].height = 30
indicators = [("Global warming", "kg CO2-eq", "=Comparison!{c}%d" % CP["GW"], "#,##0", "lower"),
              ("Cumulative energy demand", "MJ-eq", "=Comparison!{c}%d" % CP["TCED"], "#,##0", "lower"),
              ("Acidification", "kg SO2-eq", "=Comparison!{c}%d" % CP["AP"], "#,##0.0", "lower"),
              ("Eutrophication", "kg PO4-eq", "=Comparison!{c}%d" % CP["EP"], "#,##0.0", "lower"),
              ("Land competition", "m2a", "=Comparison!{c}%d" % CP["LC"], "#,##0", "lower"),
              ("Water dependence", "m3", "=Comparison!{c}%d" % CP["WD"], "#,##0", "lower"),
              ("Nitrogen use efficiency", "%", "='Nutrient balance'!{c}%d" % NB[("N", "eff")], "0%", "higher"),
              ("Net N released to water", "kg N", "='Nutrient balance'!{c}%d" % NB[("N", "per_t")], "0.0", "lower")]
for i, (lab, unit, f, fmt, better) in enumerate(indicators):
    rr_ = hdr_ + 1 + i
    db.merge_cells(f"B{rr_}:E{rr_}")
    db[f"B{rr_}"].value, db[f"B{rr_}"].font = lab, BOLD
    db[f"F{rr_}"].value, db[f"F{rr_}"].font = unit, ITAL
    for c1, c2, col in (("G", "H", "C"), ("I", "J", "D"), ("K", "L", "E")):
        db.merge_cells(f"{c1}{rr_}:{c2}{rr_}")
        put(db, f"{c1}{rr_}", f.format(c=col), fmt)
        db[f"{c1}{rr_}"].alignment = Alignment(horizontal="center")
    best = "MIN" if better == "lower" else "MAX"
    put(db, f"M{rr_}", f"=IF(K{rr_}=0,\"\",MIN(G{rr_},I{rr_})/K{rr_}-1)" if better == "lower" else f"=(MAX(G{rr_},I{rr_})-K{rr_})*100",
        "+0%;-0%;0%" if better == "lower" else '+0" pp";-0" pp"')
    db[f"M{rr_}"].alignment = Alignment(horizontal="center")
    for c1 in ("G", "I", "K"):
        db.conditional_formatting.add(f"{c1}{rr_}", FormulaRule(formula=[f"{c1}{rr_}={best}($G{rr_},$I{rr_},$K{rr_})"],
                                                                fill=GOOD, font=Font(name=F, bold=True, color="0F6E56")))
    for j in range(ord("B"), ord("N")):
        db[f"{chr(j)}{rr_}"].border = BOX
        if i % 2:
            db[f"{chr(j)}{rr_}"].fill = PatternFill("solid", fgColor="F7F7F5")
last_ind = hdr_ + len(indicators)
db[f"B{last_ind + 1}"].value = "* best IMTA system against the fish-only pond (for N use efficiency: difference in percentage points)."
db[f"B{last_ind + 1}"].font = Font(name=F, italic=True, size=9, color="5F5E5A")

# chart data (bottom of the sheet)
cd = last_ind + 40
band(db, cd, "Chart data (feeds the charts above; all formulas)", 12, fill="5F5E5A", size=11, first=2)
DASH_GW = [("Feeds", ["Feeds"], "BA7517"), ("Transport", ["Transports"], "D85A30"), ("Energy", ["Energy consumption"], "534AB7"),
           ("Equipment", ["Equipment"], "AFA9EC"), ("Other", ["Building impact", "Vehicle", "Chemical products", "Fry"], "B4B2A9")]
t1 = cd + 2
db[f"B{t1 - 1}"].value, db[f"B{t1 - 1}"].font = "Global warming by process, kg CO2-eq/t", BOLD
for j, lab in enumerate(["Process", "SI-IMTA", "SE-IMTA", "SI-POLY"]):
    c = db.cell(row=t1, column=2 + j, value=lab)
    c.font, c.fill, c.border = HFONT, HFILL, BOX
for i, (lab, procs, _) in enumerate(DASH_GW):
    db.cell(row=t1 + 1 + i, column=2, value=lab).border = BOX
    for j, col in enumerate(COLS):
        put(db, db.cell(row=t1 + 1 + i, column=3 + j).coordinate, "=" + "+".join(f"'LCIA (Annex 1)'!{col}{LA[('GW', p_)]}" for p_ in procs), "#,##0")
t2 = t1 + len(DASH_GW) + 3
db[f"B{t2 - 1}"].value, db[f"B{t2 - 1}"].font = "KPI targets met", BOLD
for j, lab in enumerate(["System", "Environment", "Circularity"]):
    c = db.cell(row=t2, column=2 + j, value=lab)
    c.font, c.fill, c.border = HFONT, HFILL, BOX
for i, (sy, mc) in enumerate(zip(SYSTEMS, ("J", "K", "L"))):
    db.cell(row=t2 + 1 + i, column=2, value=sy).border = BOX
    put(db, f"C{t2 + 1 + i}", f"=COUNTIF('KPI framework'!{mc}{min(env_rows)}:{mc}{max(env_rows)},\"✓\")", "0")
    put(db, f"D{t2 + 1 + i}", f"=COUNTIF('KPI framework'!{mc}{min(circ_rows)}:{mc}{max(circ_rows)},\"✓\")", "0")
t3 = t2 + 6
db[f"B{t3 - 1}"].value, db[f"B{t3 - 1}"].font = "Change against the fish-only pond", BOLD
for j, lab in enumerate(["Impact", "SI-IMTA", "SE-IMTA"]):
    c = db.cell(row=t3, column=2 + j, value=lab)
    c.font, c.fill, c.border = HFONT, HFILL, BOX
for i, cat in enumerate(CATEGORIES):
    db.cell(row=t3 + 1 + i, column=2, value=CAT_NAMES[cat]).border = BOX
    put(db, f"C{t3 + 1 + i}", f"=Comparison!F{CP[cat]}", "+0%;-0%;0%")
    put(db, f"D{t3 + 1 + i}", f"=Comparison!G{CP[cat]}", "+0%;-0%;0%")
t4 = t3 + len(CATEGORIES) + 3
db[f"B{t4 - 1}"].value, db[f"B{t4 - 1}"].font = "Fate of feed nitrogen, kg N/t", BOLD
for j, lab in enumerate(["System", "in fish + oysters", "in macroalgae", "released (net)"]):
    c = db.cell(row=t4, column=2 + j, value=lab)
    c.font, c.fill, c.border = HFONT, HFILL, BOX
    c.alignment = Alignment(wrap_text=True)
for i, (col, sy) in enumerate(zip(COLS, SYSTEMS)):
    db.cell(row=t4 + 1 + i, column=2, value=sy).border = BOX
    for j, key in enumerate(("produced_biomass", "downstream_macroalgae", "released")):
        put(db, db.cell(row=t4 + 1 + i, column=3 + j).coordinate,
            f"='Nutrient balance'!{col}{NB[('N', key)]}*Inventory!{col}{R['scale']}", "#,##0.0")

# 2 x 2 chart grid
ch_top = last_ind + 3
band(db, ch_top, "Charts", 12, first=2, tall=True)
g1 = BarChart()
g1.type, g1.grouping, g1.overlap, g1.gapWidth = "col", "stacked", 100, 60
g1.title, g1.y_axis.title = "Global warming by process", "kg CO2-eq per t"
for i, (lab, _, hx) in enumerate(DASH_GW):
    se = Series(Reference(db, min_col=3, max_col=5, min_row=t1 + 1 + i), title=lab)
    color(se, hx)
    g1.series.append(se)
g1.set_categories(Reference(db, min_col=3, max_col=5, min_row=t1))
db.add_chart(chart_size(g1, 15.5, 8), f"B{ch_top + 2}")
g2 = BarChart()
g2.type, g2.grouping, g2.overlap, g2.gapWidth = "col", "stacked", 100, 60
g2.title, g2.y_axis.title = "KPI targets met (of 13)", "targets met"
g2.add_data(Reference(db, min_col=3, max_col=4, min_row=t2, max_row=t2 + 3), titles_from_data=True)
g2.set_categories(Reference(db, min_col=2, min_row=t2 + 1, max_row=t2 + 3))
for se, hx in zip(g2.series, ("378ADD", "1D9E75")):
    color(se, hx)
g2.y_axis.scaling.min, g2.y_axis.scaling.max, g2.y_axis.majorUnit = 0, 13, 1
db.add_chart(labels(chart_size(g2, 15.5, 8)), f"H{ch_top + 2}")
g3 = BarChart()
g3.type, g3.grouping, g3.gapWidth = "bar", "clustered", 60
g3.title = "Change against the fish-only pond (left = better)"
g3.add_data(Reference(db, min_col=3, max_col=4, min_row=t3, max_row=t3 + len(CATEGORIES)), titles_from_data=True)
g3.set_categories(Reference(db, min_col=2, min_row=t3 + 1, max_row=t3 + len(CATEGORIES)))
for se, sy in zip(g3.series, ("SI-IMTA", "SE-IMTA")):
    color(se, SYS_COLOR[sy])
g3.y_axis.number_format = "0%"
bars_down(g3, -1, 1.25)
db.add_chart(chart_size(g3, 15.5, 9), f"B{ch_top + 19}")
g4 = BarChart()
g4.type, g4.grouping, g4.overlap, g4.gapWidth = "bar", "stacked", 100, 60
g4.title, g4.y_axis.title = "Where the feed nitrogen goes", "kg N per t"
g4.add_data(Reference(db, min_col=3, max_col=5, min_row=t4, max_row=t4 + 3), titles_from_data=True)
g4.set_categories(Reference(db, min_col=2, min_row=t4 + 1, max_row=t4 + 3))
for se, hx in zip(g4.series, ("534AB7", "1D9E75", "E24B4A")):
    color(se, hx)
bars_down(g4)
db.add_chart(labels(chart_size(g4, 15.5, 9)), f"H{ch_top + 19}")
db.freeze_panes = "A3"

# ------------------------------------------------------------------ Charts
cs = sheet("Charts", "Charts - all live: they update when an input or target changes")
cs["A4"].value, cs["A4"].font = "Contents (click to jump)", BOLD
CHART_TOC = []
r = 12


def block(title, heads):
    global r
    band(cs, r, title, 16)
    CHART_TOC.append((title, r))
    header(cs, r + 1, heads)
    r += 2
    return r - 1


# 1 Environmental profile (radar)
hdr = block("1  Environmental profile: each impact per tonne as % of the fish-only pond (100 % = baseline)", ["Impact category", "", *SYSHEAD])
for cat in CATEGORIES:
    cs.cell(row=r, column=1, value=CAT_NAMES[cat]).font = NORM
    for col in COLS:
        put(cs, f"{col}{r}", f"=Comparison!{col}{CP[cat]}/Comparison!$E{CP[cat]}", "0%")
    r += 1
rc = RadarChart()
rc.type, rc.title = "marker", "Environmental profile (% of fish-only pond; smaller = lower impact)"
rc.add_data(Reference(cs, min_col=3, max_col=5, min_row=hdr, max_row=r - 1), titles_from_data=True)
rc.set_categories(Reference(cs, min_col=1, min_row=hdr + 1, max_row=r - 1))
for se, sy in zip(rc.series, SYSTEMS):
    color(se, SYS_COLOR[sy])
    se.graphicalProperties.line.width = 28000
rc.y_axis.number_format = "0%"
rc.y_axis.scaling.min, rc.y_axis.scaling.max, rc.y_axis.majorUnit = 0, 2.5, 0.5
cs.add_chart(chart_size(rc, 16, 10), f"H{hdr - 1}")
r = hdr + 20

# 2 Change against the fish-only pond
hdr = block("2  Change per tonne against the fish-only pond (negative = better)", ["Impact category", "", "SI-IMTA vs POLY", "SE-IMTA vs POLY"])
for cat in CATEGORIES:
    cs.cell(row=r, column=1, value=CAT_NAMES[cat]).font = NORM
    for col, src in (("C", "F"), ("D", "G")):
        put(cs, f"{col}{r}", f"=Comparison!{src}{CP[cat]}", "+0%;-0%;0%")
    r += 1
bc2 = BarChart()
bc2.type, bc2.grouping, bc2.title = "bar", "clustered", "Change against the fish-only pond"
bc2.add_data(Reference(cs, min_col=3, max_col=4, min_row=hdr, max_row=r - 1), titles_from_data=True)
bc2.set_categories(Reference(cs, min_col=1, min_row=hdr + 1, max_row=r - 1))
for se, sy in zip(bc2.series, ("SI-IMTA", "SE-IMTA")):
    color(se, SYS_COLOR[sy])
bc2.y_axis.number_format = "0%"
bars_down(bc2, -1, 1.5)
cs.add_chart(labels(chart_size(bc2, 16, 9)), f"H{hdr - 1}")
r = hdr + 20

# 3-4 Nutrient fate per tonne
for el, name in (("N", "nitrogen"), ("P", "phosphorus")):
    hdr = block(f"{3 if el == 'N' else 4}  Fate of the {name} in the feed, kg {el} per tonne (negative release = net uptake from the water)",
                ["System", "", f"in fish + oysters", f"in macroalgae", f"released to water (net)"])
    for col, sy in zip(COLS, SYSTEMS):
        cs.cell(row=r, column=1, value=NAMES[sy]).font = NORM
        sc = f"Inventory!{col}{R['scale']}"
        for out, key in (("C", "produced_biomass"), ("D", "downstream_macroalgae"), ("E", "released")):
            put(cs, f"{out}{r}", f"='Nutrient balance'!{col}{NB[(el, key)]}*{sc}", "#,##0.0")
        r += 1
    nc = BarChart()
    nc.type, nc.grouping, nc.overlap = "bar", "stacked", 100
    nc.title, nc.y_axis.title = f"Where the feed {name} goes", f"kg {el} per t fish + oyster"
    nc.add_data(Reference(cs, min_col=3, max_col=5, min_row=hdr, max_row=r - 1), titles_from_data=True)
    nc.set_categories(Reference(cs, min_col=1, min_row=hdr + 1, max_row=r - 1))
    for se, hx in zip(nc.series, ("534AB7", "1D9E75", "E24B4A")):
        color(se, hx)
    bars_down(nc)
    cs.add_chart(labels(chart_size(nc, 16, 7.5)), f"H{hdr - 1}")
    r = hdr + 17

# 5 KPI targets met
env = [KP[k[0]] for k in KPI_DEF if k[6]]
circ = [KP[k[0]] for k in KPI_DEF if not k[6]]
hdr = block("5  KPI targets met per system", ["System", "", "Environmental (of 7)", "Circularity (of 6)", "Total (of 13)"])
for mc, sy in zip(("J", "K", "L"), SYSTEMS):
    cs.cell(row=r, column=1, value=NAMES[sy]).font = NORM
    put(cs, f"C{r}", f"=COUNTIF('KPI framework'!{mc}{min(env)}:{mc}{max(env)},\"✓\")", "0")
    put(cs, f"D{r}", f"=COUNTIF('KPI framework'!{mc}{min(circ)}:{mc}{max(circ)},\"✓\")", "0")
    put(cs, f"E{r}", f"=C{r}+D{r}", "0", bold=True)
    r += 1
kc = BarChart()
kc.type, kc.grouping, kc.overlap = "col", "stacked", 100
kc.title, kc.y_axis.title = "KPI targets met (of 13)", "targets met"
kc.add_data(Reference(cs, min_col=3, max_col=4, min_row=hdr, max_row=r - 1), titles_from_data=True)
kc.set_categories(Reference(cs, min_col=1, min_row=hdr + 1, max_row=r - 1))
for se, hx in zip(kc.series, ("378ADD", "1D9E75")):
    color(se, hx)
kc.y_axis.scaling.min, kc.y_axis.scaling.max, kc.y_axis.majorUnit = 0, 13, 1
cs.add_chart(labels(chart_size(kc, 16, 8)), f"H{hdr - 1}")
r = hdr + 18

# 6 Margin to target
hdr = block("6  Margin to target per KPI (positive = target met; capped at -100 % and +150 %; blank = baseline)", ["KPI", "", *SYSHEAD])
for kid, dim, name, unit, better, target, cat in KPI_DEF:
    k = KP[kid]
    cs.cell(row=r, column=1, value=f"{kid} {name}").font = NORM
    for vc, col, sy in zip(("G", "H", "I"), COLS, SYSTEMS):
        t, v = f"'KPI framework'!$F{k}", f"'KPI framework'!{vc}{k}"
        m = f"({t}-{v})/ABS({t})" if better == "lower" else f"({v}-{t})/ABS({t})"
        f = "=NA()" if cat and sy == "SI-POLY" else f"=MAX(-1,MIN(1.5,{m}))"
        put(cs, f"{col}{r}", f, "+0%;-0%;0%")
    r += 1
mc_ = BarChart()
mc_.type, mc_.grouping, mc_.title = "bar", "clustered", "Margin to KPI target (right of 0 = met)"
mc_.add_data(Reference(cs, min_col=3, max_col=5, min_row=hdr, max_row=r - 1), titles_from_data=True)
mc_.set_categories(Reference(cs, min_col=1, min_row=hdr + 1, max_row=r - 1))
for se, sy in zip(mc_.series, SYSTEMS):
    color(se, SYS_COLOR[sy])
mc_.y_axis.number_format = "0%"
bars_down(mc_, -1, 1.5)
cs.add_chart(chart_size(mc_, 18, 13), f"H{hdr - 1}")
widths(cs, {"A": 40, "B": 2, "C": 18, "D": 18, "E": 20, "F": 2})
for i, (title, row_) in enumerate(CHART_TOC):
    c = cs.cell(row=5 + i, column=1, value=title)
    c.hyperlink, c.font = f"#'Charts'!A{row_}", Font(name=F, color="0563C1", underline="single")

# ------------------------------------------------------------------ Figures (static) + their data (live)
fg = sheet("Figures", "Figures - the report charts drawn by make_charts.py, each with its data table on the right")
fg["A3"], fg["A3"].font = ("The pictures are static (published values). The tables next to them are live formulas, "
                           "so they update when you change an input."), ITAL
DC = 16  # data tables start in column P


def ftable(top, title, head, body):
    """Write a data table at column P; body rows are [label, value or formula, ...] with a number format per row."""
    fg.cell(row=top, column=DC, value=title).font = BOLD
    for j, h in enumerate(head):
        c = fg.cell(row=top + 1, column=DC + j, value=h)
        c.font, c.fill, c.border = HFONT, HFILL, BOX
        c.alignment = Alignment(wrap_text=True, vertical="center")
    for i, (fmt, vals) in enumerate(body):
        rr = top + 2 + i
        fg.cell(row=rr, column=DC, value=vals[0]).font = NORM
        fg.cell(row=rr, column=DC, value=vals[0]).border = BOX
        for j, v in enumerate(vals[1:]):
            c = fg.cell(row=rr, column=DC + 1 + j)
            put(fg, c.coordinate, v, fmt)
    return top + 2 + len(body)


def per_sys(fmt, label, f):
    return (fmt, [label, *[f.format(c=col) for col in COLS]])


ann_gw = lambda c, p: f"'LCIA (Annex 1)'!{c}{LA[('GW', p)]}"  # noqa: E731
FIG_GW = [("Feeds", ["Feeds"]), ("Transport", ["Transports"]), ("Energy (pumping, aeration)", ["Energy consumption"]),
          ("Equipment", ["Equipment"]), ("Other (buildings, vehicles, chemicals, fry)", ["Building impact", "Vehicle", "Chemical products", "Fry"])]
SH = ["", *SYSHEAD]


def data_for(name, top):
    if name.startswith("00"):
        return ftable(top, "Data: key numbers (per tonne of fish + oyster)", ["Indicator", *SYSHEAD], [
            per_sys("#,##0", "Eutrophication, kg PO4-eq/t", "=Comparison!{c}%d" % CP["EP"]),
            per_sys("0%", "Eutrophication vs fish-only pond", "=Comparison!{c}%d/Comparison!$E%d-1" % (CP["EP"], CP["EP"])),
            per_sys("0%", "Feed nitrogen kept in products", "='Nutrient balance'!{c}%d" % NB[("N", "eff")]),
            per_sys("#,##0", "Global warming, kg CO2-eq/t", "=Comparison!{c}%d" % CP["GW"]),
            per_sys("0%", "Global warming vs fish-only pond", "=Comparison!{c}%d/Comparison!$E%d-1" % (CP["GW"], CP["GW"])),
            per_sys("0%", "Share of global warming from feed", "=%s/'LCIA (Annex 1)'!{c}%d" % (ann_gw("{c}", "Feeds"), LA[("GW", "Total")])),
            per_sys("#,##0", "Land competition, m2a/t", "=Comparison!{c}%d" % CP["LC"]),
            per_sys("0%", "Land competition vs fish-only pond", "=Comparison!{c}%d/Comparison!$E%d-1" % (CP["LC"], CP["LC"])),
        ])
    if name.startswith("01"):
        return ftable(top, "Data: change per tonne against the fish-only pond", ["Impact category", "SI-IMTA vs POLY", "SE-IMTA vs POLY"],
                      [("+0%;-0%;0%", [CAT_NAMES[c], f"=Comparison!F{CP[c]}", f"=Comparison!G{CP[c]}"]) for c in CATEGORIES])
    if name.startswith("02"):
        body = [per_sys("#,##0", lab, "=" + "+".join(ann_gw("{c}", p) for p in procs)) for lab, procs in FIG_GW]
        body.append(per_sys("#,##0", "Total (reported)", "='LCIA (Annex 1)'!{c}%d" % LA[("GW", "Total")]))
        body.append(per_sys("0%", "Feed share of total", "=%s/'LCIA (Annex 1)'!{c}%d" % (ann_gw("{c}", "Feeds"), LA[("GW", "Total")])))
        return ftable(top, "Data: global warming by process, kg CO2-eq per tonne", ["Process", *SYSHEAD], body)
    if name.startswith("03"):
        sc = "*Inventory!{c}%d" % R["scale"]
        return ftable(top, "Data: fate of the feed nitrogen, kg N per tonne", ["Item", *SYSHEAD], [
            per_sys("#,##0.0", "N in feed", "='Nutrient balance'!{c}%d" % NB[("N", "feed")] + sc),
            per_sys("#,##0.0", "in fish + oysters", "='Nutrient balance'!{c}%d" % NB[("N", "produced_biomass")] + sc),
            per_sys("#,##0.0", "in macroalgae", "='Nutrient balance'!{c}%d" % NB[("N", "downstream_macroalgae")] + sc),
            per_sys("#,##0.0", "released to water (net; negative = uptake)", "='Nutrient balance'!{c}%d" % NB[("N", "released")] + sc),
            per_sys("0%", "kept in products (N use efficiency)", "='Nutrient balance'!{c}%d" % NB[("N", "eff")]),
        ])
    if name.startswith("04"):
        rr = top
        for col, sy in zip(COLS, SYSTEMS):
            body = [("0%", [lab, *[f"=IF({lcia_abs(col, c)}=0,0,({lcia_sum(col, c, procs)})/{lcia_abs(col, c)})" for c in CATEGORIES]])
                    for lab, procs, _ in GROUPS]
            rr = ftable(rr, f"Data: share of each impact per process - {NAMES[sy]}", ["Process group", *CATEGORIES], body) + 1
            fg.conditional_formatting.add(f"Q{rr - 1 - len(GROUPS)}:W{rr - 2}", ColorScaleRule(
                start_type="num", start_value=0, start_color="FFFFFF", end_type="num", end_value=1, end_color="0F6E56"))
        return rr
    if name.startswith("05"):
        body = []
        for kid, dim, kname, unit, better, target, cat in KPI_DEF:
            k = KP[kid]
            fmt = "0.0%" if unit == "%" else "#,##0.00"
            body.append((fmt, [f"{kid} {kname} ({unit})", f"='KPI framework'!F{k}", *[f"='KPI framework'!{vc}{k}" for vc in ("G", "H", "I")],
                               *[f"='KPI framework'!{mc}{k}" for mc in ("J", "K", "L")]]))
        body.append(("@", ["Targets met", "", "", "", "", *[f"='KPI framework'!{mc}{KP['score']}" for mc in ("J", "K", "L")]]))
        return ftable(top, "Data: KPI scorecard", ["KPI", "Target", "Value SI-IMTA", "Value SE-IMTA", "Value SI-POLY",
                                                    "Met SI-IMTA", "Met SE-IMTA", "Met SI-POLY"], body)
    if name.startswith("06"):
        return ftable(top, "Data: each impact as % of the fish-only pond", ["Impact category", *SYSHEAD],
                      [("0%", [CAT_NAMES[c], *[f"=Comparison!{col}{CP[c]}/Comparison!$E{CP[c]}" for col in COLS]]) for c in CATEGORIES])
    if name.startswith("07"):
        return ftable(top, "Data: the framework steps with this workbook's numbers", ["Step", *SYSHEAD], [
            per_sys("#,##0", "1 Data: fish + oyster gain per pond, kg", "=Inventory!{c}%d" % R["product"]),
            per_sys("0.000", "2 Scale: factor to 1 t = 1,000 / gain", "=Inventory!{c}%d" % R["scale"]),
            per_sys("#,##0.0", "3 KPI example: N in feed per pond, kg", "='Nutrient balance'!{c}%d" % NB[("N", "feed")]),
            per_sys("0%", "3 KPI example: N use efficiency (C1)", "='Nutrient balance'!{c}%d" % NB[("N", "eff")]),
            ("0%", ["4 Target: improvement vs fish-only pond", "='KPI framework'!$F$5", "='KPI framework'!$F$5", "='KPI framework'!$F$5"]),
            ("@", ["5 Score: targets met", *[f"='KPI framework'!{mc}{KP['score']}" for mc in ("J", "K", "L")]]),
        ])
    if name.startswith("08"):
        body = []
        for kid, dim, kname, unit, better, target, cat in KPI_DEF:
            k = KP[kid]
            vals = []
            for vc, sy in zip(("G", "H", "I"), SYSTEMS):
                t, v = f"'KPI framework'!$F{k}", f"'KPI framework'!{vc}{k}"
                m = f"({t}-{v})/ABS({t})" if better == "lower" else f"({v}-{t})/ABS({t})"
                vals.append('="baseline"' if cat and sy == "SI-POLY" else "=" + m)
            body.append(("+0%;-0%;0%", [f"{kid} {kname}", *vals]))
        return ftable(top, "Data: margin to target (positive = met; not capped)", ["KPI", *SYSHEAD], body)
    return top


FIG_TITLE = {"00": "Key numbers", "01": "Change against the fish-only pond", "02": "Global warming by process",
             "03": "Fate of the feed nitrogen", "04": "Which process drives which impact", "05": "KPI scorecard",
             "06": "Environmental profile", "07": "KPI framework", "08": "Margin to KPI target"}
pngs = sorted((ROOT / "results" / "charts").glob("*.png"))
fg["A4"].value, fg["A4"].font = "Contents (click to jump)", BOLD
toc_row = 5
r = toc_row + len(pngs) + 2
for png in pngs:
    with PILImage.open(png) as im:                      # downscale the 200-dpi PNGs to keep the workbook small
        im = im.convert("RGB")
        im.thumbnail((1400, 1400))
        buf = BytesIO()
        im.save(buf, "PNG", optimize=True)
    img = Image(buf)
    scale = 900 / img.width
    img.width, img.height = 900, int(img.height * scale)
    title = f"Figure {int(png.name[:2])}  ·  {FIG_TITLE.get(png.name[:2], png.stem)}"
    band(fg, r, title, 23)
    c = fg.cell(row=toc_row, column=1, value=title)
    c.hyperlink, c.font = f"#'Figures'!A{r}", Font(name=F, color="0563C1", underline="single")
    toc_row += 1
    fg.cell(row=r + 1, column=1, value=f"results/charts/{png.name} (static picture)").font = Font(name=F, italic=True, size=9, color="5F5E5A")
    fg.add_image(img, f"A{r + 2}")
    end_data = data_for(png.name, r + 2)
    r = max(r + 2 + int(img.height / 17) + 3, end_data + 3)   # LibreOffice rows are ~17 px
widths(fg, {"P": 44, **{chr(ord("Q") + i): 14 for i in range(7)}})

# ------------------------------------------------------------------ Flow diagrams (static) + their data (live)
fl = sheet("Flow diagrams", "Flow diagrams - how the fish waste is used in each system (per pond and production cycle)")
fl["A3"], fl["A3"].font = ("Each system: a flow diagram drawn with cells and its data table on the right. "
                           "All numbers are live: they update when you change an input."), ITAL
BOXC = {"feed": ("FAEEDA", "BA7517"), "fry": ("FBEAF0", "993556"), "water": ("E6F1FB", "185FA5"), "energy": ("EEEDFE", "534AB7"),
        "pond": ("E1F5EE", "0F6E56"), "oys": ("FAECE7", "993C1D"), "alg": ("EAF3DE", "3B6D11"), "fish": ("EEEDFE", "3C3489"),
        "sea": ("FCEBEB", "A32D2D"), "none": ("F1EFE8", "888780")}
ARROW = Font(name=F, bold=True, size=16, color="5F5E5A")
widths(fl, {"A": 26, "B": 5, "C": 26, "D": 5, "E": 26, "F": 5, "G": 26, "H": 3, "I": 40, "J": 14, "K": 8})


def box(r0, col, kind, title, value):
    """A 2-row box: title (bold) above a value line (text or formula)."""
    fill_, edge = BOXC[kind]
    side = Side(style="medium", color=edge)
    for i, v in enumerate((title, value)):
        c = fl[f"{col}{r0 + i}"]
        c.value, c.fill = v, PatternFill("solid", fgColor=fill_)
        c.font = Font(name=F, bold=(i == 0), size=11 if i == 0 else 10, color=edge)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = Border(left=side, right=side, top=side if i == 0 else None, bottom=side if i == 1 else None)


def arrow(ref, sym, label=None):
    fl[ref].value, fl[ref].font = sym, ARROW
    fl[ref].alignment = Alignment(horizontal="center", vertical="center")


r = 5
for col, sy in zip(COLS, SYSTEMS):
    imta, tidal = sy != "SI-POLY", sy == "SE-IMTA"
    inv_ = lambda k: f"Inventory!{col}{R[k]}"  # noqa: E731
    nb_ = lambda el, k: f"'Nutrient balance'!{col}{NB[(el, k)]}"  # noqa: E731
    fl.cell(row=r, column=1, value=NAMES[sy]).font = Font(name=F, bold=True, size=13, color=SYS_COLOR[sy])
    t = r + 2
    for rr in range(t, t + 11):
        fl.row_dimensions[rr].height = 18
    # inputs (column A) -> pond (C) -> middle (E) -> outputs (G)
    box(t, "A", "feed", "Fish feed", f'=TEXT({inv_("feed")},"#,##0")&" kg · "&TEXT({nb_("N", "feed")},"#,##0.0")&" kg N"')
    box(t + 3, "A", "fry", "Fry + oyster spat" if imta else "Fry", f'=TEXT({inv_("fish_stocked")}+{inv_("oyster_stocked")},"#,##0")&" kg stocked"')
    box(t + 6, "A", "water", "Seawater", f'=TEXT({inv_("seawater_used")},"#,##0")&" m3 · {"tidal" if tidal else "pumped"}"')
    box(t + 9, "A", "energy", "Energy", "almost none (tides)" if tidal else "pumping + aeration")
    arrow(f"B{t + 1}", "↘"), arrow(f"B{t + 3}", "→"), arrow(f"B{t + 6}", "↗"), arrow(f"B{t + 9}", "↗")
    box(t + 3, "C", "pond", "Fish pond" + (" + oysters" if imta else ""), "feed → fish → waste")
    box(t, "E", "oys" if imta else "none", "Oysters", "filter particles" if imta else "none in this system")
    box(t, "G", "oys" if imta else "none", "Oyster flesh", f'=TEXT({inv_("oyster_gain")},"#,##0")&" kg"' if imta else "–")
    arrow(f"D{t + 2}", "↗"), arrow(f"F{t}", "→")
    fl[f"E{t + 3}"].value, fl[f"E{t + 3}"].font = "harvest  →  →  →", Font(name=F, bold=True, color="534AB7")
    fl[f"E{t + 3}"].alignment = Alignment(horizontal="center", vertical="center")
    arrow(f"D{t + 3}", "→"), arrow(f"F{t + 3}", "→")
    box(t + 3, "G", "fish", "Fish", f'=TEXT({inv_("fish_gain")},"#,##0")&" kg gained"')
    arrow(f"D{t + 5}", "↘")
    box(t + 6, "E", "alg" if imta else "none", "Macroalgae", ("Ulva + Gracilaria" if tidal else "Ulva") + " take up N, P" if imta else "none in this system")
    box(t + 6, "G", "alg" if imta else "none", "Macroalgae harvest",
        f'=TEXT({inv_("macroalgae_gain")},"#,##0")&" kg · "&TEXT({nb_("N", "downstream_macroalgae")},"0.0")&" kg N"' if imta else "–")
    arrow(f"F{t + 6}", "→"), arrow(f"E{t + 8}", "↓")
    rep = nb_("N", "reported")
    box(t + 9, "E", "sea", "Lagoon / estuary", f'=IF({rep}<0,"net uptake "&TEXT(-{rep},"0.0")&" kg N",TEXT({rep},"0.0")&" kg N released")')
    fl[f"G{t + 9}"].value = f'="N in products: "&TEXT({nb_("N", "produced_biomass")}+{nb_("N", "downstream_macroalgae")},"0.0")&" kg N"'
    fl[f"G{t + 10}"].value = f'="N use efficiency: "&TEXT({nb_("N", "eff")},"0%")'
    fl[f"G{t + 9}"].font, fl[f"G{t + 10}"].font = BOLD, NORM

    # data table (column I)
    items = [
        ("Fish feed", "=" + inv_("feed"), "kg", "#,##0"),
        ("N in feed", "=" + nb_("N", "feed"), "kg N", "#,##0.0"),
        ("Fry + oyster spat stocked", f"={inv_('fish_stocked')}+{inv_('oyster_stocked')}", "kg", "#,##0"),
        ("Seawater", "=" + inv_("seawater_used"), "m3", "#,##0"),
        ("Fish gained", "=" + inv_("fish_gain"), "kg", "#,##0"),
        ("Oyster flesh gained", "=" + inv_("oyster_gain"), "kg", "#,##0"),
        ("Macroalgae harvest", "=" + inv_("macroalgae_gain"), "kg", "#,##0"),
        ("N in fish + oysters", "=" + nb_("N", "produced_biomass"), "kg N", "#,##0.0"),
        ("N in macroalgae", "=" + nb_("N", "downstream_macroalgae"), "kg N", "#,##0.0"),
        ("N in products", f"={nb_('N', 'produced_biomass')}+{nb_('N', 'downstream_macroalgae')}", "kg N", "#,##0.0"),
        ("N released (Table 5; minus = net uptake)", "=" + rep, "kg N", "#,##0.0"),
        ("N use efficiency", "=" + nb_("N", "eff"), "%", "0%"),
    ]
    fl[f"I{t}"].value, fl[f"I{t}"].font = "Data (live)", BOLD
    for j, h in enumerate(["Flow", "Value", "Unit"]):
        c = fl.cell(row=t + 1, column=9 + j, value=h)
        c.font, c.fill, c.border = HFONT, HFILL, BOX
    for i, (lab, f, unit, fmt) in enumerate(items):
        rr = t + 2 + i
        fl.cell(row=rr, column=9, value=lab).font = NORM
        put(fl, f"J{rr}", f, fmt, bold=lab in ("N in products", "N use efficiency"))
        fl.cell(row=rr, column=11, value=unit).font = NORM

    r = t + len(items) + 5
wb.move_sheet(fl, offset=wb.sheetnames.index("Goal & scope") + 1 - wb.sheetnames.index("Flow diagrams"))

# ------------------------------------------------------------------ Data checks
dc = sheet("Data checks", "Data checks - do the report's tables agree with each other?")
header(dc, 4, ["Check", "System", "Reported", "Recalculated", "Difference", "OK?", "Explanation"])
checks_def = []
for col, s in zip(COLS, SYSTEMS):
    checks_def += [
        ("Feed N = feed x protein / 6.25", s, f"='Nutrient balance'!{col}{NB[('N', 'feed')]}", float(t5[("feed", "N")][s]), 0.1, "Table 5 feed N is reproduced from Table 4"),
        ("N rejection = feed - extracted", s, f"='Nutrient balance'!{col}{NB[('N', 'released')]}", f"='Nutrient balance'!{col}{NB[('N', 'reported')]}", 0.2, "rounding only"),
        ("Water per t = Annex 1 water consumption", s, f"='LCI per tonne'!{col}{LCI['seawater, pumped or tidal']}", f"='LCIA (Annex 1)'!{col}{LA[('WD', 'Water consumption')]}", 0.01, "confirms the functional unit = fish + oyster gain"),
        ("FCR = feed / fish gain", s, f"=Inventory!{col}{R['fcr_fish']}", f"=Inventory!{col}{R['fcr_reported']}", 0.02,
         "semi-extensive: reported 0.56 = feed / (fish + oyster gain), a different definition" if s == "SE-IMTA" else "matches"),
        ("Land: allocated farm area vs Direct activity (LC)", s, f"='LCI per tonne'!{col}{LCI['land, farm area allocated to the pond']}", f"='LCIA (Annex 1)'!{col}{LA[('LC', 'Direct activity')]}", 0.05,
         "polyculture does not match the pond-area rule x 26 months; to clarify with the authors" if s == "SI-POLY" else "pond-area allocation rule reproduced within 5 %"),
    ]
for i, (name, s, calc, rep, tol, expl) in enumerate(checks_def):
    rr = 5 + i
    dc.cell(row=rr, column=1, value=name).font = NORM
    dc.cell(row=rr, column=2, value=s).font = NORM
    put(dc, f"C{rr}", rep, "#,##0.00", inp=not str(rep).startswith("="))
    put(dc, f"D{rr}", calc, "#,##0.00")
    put(dc, f"E{rr}", f"=D{rr}-C{rr}", "#,##0.00")
    rel = tol < 0.1 and "Water" in name or "Land" in name
    test = f"ABS(E{rr})<={tol}*ABS(C{rr})" if rel else f"ABS(E{rr})<={tol}"
    put(dc, f"F{rr}", f'=IF({test},"✓","check")', "@")
    dc[f"F{rr}"].alignment = Alignment(horizontal="center")
    dc.cell(row=rr, column=7, value=expl).font = ITAL
lastc = 4 + len(checks_def)
dc.conditional_formatting.add(f"F5:F{lastc}", FormulaRule(formula=['F5="✓"'], fill=GOOD))
dc.conditional_formatting.add(f"F5:F{lastc}", FormulaRule(formula=['F5="check"'], fill=PatternFill("solid", fgColor="FFEB9C")))
widths(dc, {"A": 44, "B": 10, "C": 14, "D": 14, "E": 12, "F": 8, "G": 80})

# ------------------------------------------------------------------ Sources
so = sheet("Sources", "Sources")
srcs = [
    ("Primary source", "INTEGRATE project (2020). LCA of aquaculture systems: comparison between semi-intensive/extensive pond IMTA and semi-intensive traditional fishpond production. Deliverable PI05#3, Interreg Atlantic Area EAPA_232/2016. Lead partner IPMA; contributing partners IPMA and CTAQUA."),
    ("Related conference paper", "Cunha, M. E., Malta, E., Partida, B., Agraso, M. M., Ribeiro, L. Comparative life cycle assessment of semi-intensive and extensive pond IMTA and semi-intensive conventional fishpond production. Aquaculture Europe 2021. https://aquaeas.org/Program/PaperDetail/38885"),
    ("Software", "Wilfart, A., Aubin, J. et al. (2012). Piscentool: a tool to assess sustainability in aquaculture systems. 8th LCA Food conference, Saint-Malo."),
    ("Nutrient balance", "Cho, C. Y., Kaushik, S. J. (1990). Nutritional energetics in fish: energy and protein utilization in rainbow trout. World Review of Nutrition and Dietetics 61: 132-172."),
    ("Impact categories", "Aubin, J., Papatryphon, E., van der Werf, H. M. G., Chatzifotis, S. (2009). Assessment of the environmental impact of carnivorous finfish production systems using LCA. J. Cleaner Production 17: 354-361."),
    ("IMTA LCA review", "Hala, A. F., Chougule, K., Cunha, M. E., Caria Mendes, M., Oliveira, I., Bradley, T., Forbes, J., Galileu Speranza, L. (2024). Life cycle assessment of integrated multi-trophic aquaculture: a review on methodology and challenges for its sustainability evaluation. Aquaculture 590, 741035."),
    ("LCI schema", "Nair, R. R., Chougule, K. M., Gomez Trillos, J. C., Brand-Daniels, U. (2025). A generalized schema to publish and share life cycle inventories (LCI). J. Cleaner Production 520, 146120."),
]
for i, (a, b) in enumerate(srcs):
    dc_ = so.cell(row=4 + i, column=1, value=a)
    dc_.font = BOLD
    c = so.cell(row=4 + i, column=2, value=b)
    c.font, c.alignment = NORM, Alignment(wrap_text=True, vertical="top")
widths(so, {"A": 22, "B": 130})

# ------------------------------------------------------------------ README content
def build_readme():
    ws = rd
    widths(ws, {"A": 3, "B": 30, "C": 30, "D": 24, "E": 24, "F": 52})
    DARK = PatternFill("solid", fgColor="0F6E56")
    LINK = Font(name=F, color="0563C1", underline="single")

    def text(r, value, font=NORM, h=None, cols="B:F", fill=None):
        ws.merge_cells(f"{cols[0]}{r}:{cols[-1]}{r}")
        c = ws[f"{cols[0]}{r}"]
        c.value, c.font = value, font
        c.alignment = Alignment(wrap_text=True, vertical="top")
        if fill:
            c.fill = fill
        if h:
            ws.row_dimensions[r].height = h
        return r + 1

    def heading(r, n, title):
        for col in "BCDEF":
            ws[f"{col}{r}"].fill = SFILL
        ws[f"B{r}"].value, ws[f"B{r}"].font = f"{n}   {title}", Font(name=F, bold=True, size=12, color="0F6E56")
        ws.row_dimensions[r].height = 20
        return r + 2

    def head(r, labels, merge=None):
        for col, lab in zip("BCDEF", labels):
            c = ws[f"{col}{r}"]
            c.value, c.font, c.fill, c.border = lab, HFONT, HFILL, BOX
            c.alignment = Alignment(wrap_text=True, vertical="center")
        if merge:
            ws.merge_cells(f"{merge[0]}{r}:{merge[1]}{r}")
        return r + 1

    def row(r, values, merge=None, fonts=None, h=None):
        for i, (col, v) in enumerate(zip("BCDEF", values)):
            c = ws[f"{col}{r}"]
            c.value, c.border = v, BOX
            c.font = (fonts or {}).get(i, NORM)
            c.alignment = Alignment(wrap_text=True, vertical="top")
        if merge:
            ws.merge_cells(f"{merge[0]}{r}:{merge[1]}{r}")
        if h:
            ws.row_dimensions[r].height = h
        return r + 1

    # title band
    for col in "ABCDEF":
        ws[f"{col}1"].fill = DARK
        ws[f"{col}2"].fill = DARK
    ws["B1"].value, ws["B1"].font = "Pond IMTA vs fish polyculture: LCA results and circular KPI decision tool", Font(name=F, bold=True, size=16, color="FFFFFF")
    ws["B2"].value, ws["B2"].font = SRC + " · KPI layer by K. M. Chougule", Font(name=F, italic=True, color="E1F5EE")
    ws.row_dimensions[1].height = 30
    r = 4

    r = heading(r, "1", "What this workbook does")
    r = text(r, "It takes the inventory and the life cycle impact results of the INTEGRATE pond study and turns them into a KPI "
                "decision tool: 13 KPIs (7 environmental, 6 circularity) with targets and a pass / fail score for three farm designs. "
                "Every result is a live formula: change a yellow input and the KPIs, charts and tables update.", h=48)
    r = text(r, "Functional unit: 1 tonne of aquatic product (fish + oyster flesh) at the farm gate, one production cycle. "
                "Macroalgae are a co-product outside the functional unit.", font=BOLD, h=32)
    r += 1

    r = heading(r, "2", "Systems compared")
    r = head(r, ["Code", "System", "Site", "", "Species and role"], merge=("D", "E"))
    systems = [("SI-IMTA", "Semi-intensive pond IMTA", "IPMA research station, Olhao, Portugal",
                "Meagre, white seabream, mullet + oysters + macroalgae (Ulva)"),
               ("SE-IMTA", "Semi-extensive pond IMTA", "Estero Natural, Cadiz, Spain",
                "Gilthead seabream + oysters; macroalgae pond fed by the fishpond outflow; tidal water exchange"),
               ("SI-POLY", "Semi-intensive fish polyculture", "IPMA research station, Olhao, Portugal",
                "Meagre + gilthead seabream, fish only. Conventional baseline")]
    for code, name, site, sp in systems:
        r = row(r, [code, name, site, None, sp], merge=("D", "E"),
                fonts={0: Font(name=F, bold=True, color=SYS_COLOR[code]), 1: BOLD}, h=32)
    r += 1

    r = heading(r, "3", "Key results (live, per tonne of fish + oyster)")
    r = head(r, ["Indicator", "", *SYSHEAD], merge=("B", "C"))
    results = [("KPI targets met (of 13)", "='KPI framework'!{m}%d" % KP["score"], "@"),
               ("Global warming, kg CO2-eq/t", "=Comparison!{c}%d" % CP["GW"], "#,##0"),
               ("Eutrophication, kg PO4-eq/t", "=Comparison!{c}%d" % CP["EP"], "#,##0"),
               ("Land competition, m2a/t", "=Comparison!{c}%d" % CP["LC"], "#,##0"),
               ("Water dependence, m3/t", "=Comparison!{c}%d" % CP["WD"], "#,##0"),
               ("Nitrogen use efficiency", "='Nutrient balance'!{c}%d" % NB[("N", "eff")], "0%"),
               ("Net N released, kg N/t (minus = uptake)", "='Nutrient balance'!{c}%d" % NB[("N", "per_t")], "0.0")]
    for lab, f, fmt in results:
        ws.merge_cells(f"B{r}:C{r}")
        ws[f"B{r}"].value, ws[f"B{r}"].font, ws[f"B{r}"].border = lab, NORM, BOX
        ws[f"C{r}"].border = BOX
        for col, out, m in zip(COLS, "DEF", ("J", "K", "L")):
            put(ws, f"{out}{r}", f.format(c=col, m=m), fmt, bold=lab.startswith("KPI"))
            ws[f"{out}{r}"].alignment = Alignment(horizontal="right")
        r += 1
    r = text(r, "Semi-extensive IMTA scores best on 6 of 7 impacts; both IMTA systems need more land than the fish-only pond.", font=ITAL)
    r += 1

    r = heading(r, "4", "Tabs (click a name to open it)")
    r = head(r, ["Tab", "What you find there", "", "", "Type"], merge=("C", "E"))
    tabs = [
        ("Goal & scope", "Functional unit, boundary, software, impact categories, allocation", "Reference"),
        ("Flow diagrams", "How the fish waste is used in each system, with the flows", "Diagrams + data (live)"),
        ("Metadata", "Dataset description in the LCIS2024 structure", "Reference"),
        ("Inventory", "Table 4 of the report per pond and cycle (yellow), scaled to 1 t of product", "Input + calculation"),
        ("Nutrient balance", "N and P from feed to fish + oysters, macroalgae and water (Table 5)", "Input + calculation"),
        ("LCI per tonne", "Foreground inventory for one functional unit, grouped into inputs and outputs", "Calculation"),
        ("LCIA (Annex 1)", "Impacts per tonne for 11 processes and 7 categories, with shares", "Input + calculation"),
        ("Contribution analysis", "Share of each process in each impact (heatmap) and contribution charts", "Calculation + charts"),
        ("Comparison", "Totals side by side and change against the fish-only pond", "Calculation + chart"),
        ("KPI framework", "13 KPIs with targets and pass / fail; the improvement target is in F5", "Input + calculation"),
        ("Dashboard", "Score per system and two summary charts", "Results + charts"),
        ("Charts", "Radar profile, change vs baseline, N and P fate, targets met, margin to target", "Charts (live)"),
        ("Figures", "Report figures from make_charts.py, each with its data table", "Pictures + data"),
        ("Data checks", "Cross-checks between the report tables; two findings flagged on purpose", "Quality check"),
        ("Sources", "Report, method references and publications", "Reference"),
    ]
    for name, what, typ in tabs:
        assert name in wb.sheetnames, name
        ws.merge_cells(f"C{r}:E{r}")
        c = ws[f"B{r}"]
        c.value, c.hyperlink, c.font, c.border = name, f"#'{name}'!A1", LINK, BOX
        ws[f"C{r}"].value, ws[f"C{r}"].font = what, NORM
        ws[f"F{r}"].value, ws[f"F{r}"].font = typ, ITAL
        for col in "CDEF":
            ws[f"{col}{r}"].border = BOX
        r += 1
    r += 1

    r = heading(r, "5", "Colour code")
    legend = [(put(ws, f"B{r}", 1888, "#,##0", inp=True), "Input from the report. You can change it."),
              (None, "Formula. Do not type over it."),
              (None, "KPI target met"),
              (None, "KPI target not met")]
    put(ws, f"B{r + 1}", "=B%d*2" % r, "#,##0")
    put(ws, f"B{r + 2}", "✓", "@").fill = GOOD
    put(ws, f"B{r + 3}", "✗", "@").fill = BAD
    for i, (_, lab) in enumerate(legend):
        ws.merge_cells(f"C{r + i}:F{r + i}")
        ws[f"C{r + i}"].value, ws[f"C{r + i}"].font = lab, NORM
        ws[f"B{r + i}"].alignment = Alignment(horizontal="center")
    r += len(legend) + 1

    r = heading(r, "6", "Things to try")
    r = head(r, ["Step", "Where", "", "What happens", ""], merge=("D", "F"))
    tries = [("Change the improvement target from 10 % to 0 %", "KPI framework", "F5",
              "More environmental KPIs pass for the semi-intensive IMTA"),
             ("Lower the semi-intensive IMTA feed", "Inventory", "C%d" % R["feed"],
              "Feed N, N released, FCR and N use efficiency update"),
             ("Set the semi-intensive IMTA oyster gain to 0", "Inventory", "C%d" % R["oyster_gain"],
              "The functional unit shrinks and per-tonne values rise")]
    for step, tab, cell, what in tries:
        ws.merge_cells(f"D{r}:F{r}")
        ws[f"B{r}"].value, ws[f"B{r}"].font = step, NORM
        c = ws[f"C{r}"]
        c.value, c.hyperlink, c.font = f"{tab} {cell}", f"#'{tab}'!{cell}", LINK
        ws[f"D{r}"].value, ws[f"D{r}"].font = what, NORM
        for col in "BCDEF":
            ws[f"{col}{r}"].border = BOX
            ws[f"{col}{r}"].alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r].height = 30
        r += 1
    r += 1

    r = heading(r, "7", "About")
    about = [("Data source", "INTEGRATE deliverable PI05#3 (IPMA & CTAQUA, 2020): Table 4 inventory, Table 5 nutrients, Annex 1 impacts"),
             ("Added here", "Scaling to the functional unit, recalculated N and P balance, 13 KPIs with targets, data checks, charts"),
             ("Targets", "Placeholders for a stakeholder workshop; change them in the KPI framework tab"),
             ("Licence", "Report data: INTEGRATE partners. KPI layer: CC BY 4.0. Code: MIT"),
             ("Repository", "github.com/malleshkomal/Life-cycle-assessment-of-Integrated-Multi-Trophical-Aquaculture-"),
             ("Works offline", "No macros, no external links")]
    for k, v in about:
        r = row(r, [k, v, None, None, None], merge=("C", "F"), fonts={0: BOLD}, h=30 if len(v) > 90 else None)
    ws.freeze_panes = "A4"


build_readme()

for ws in wb.worksheets:
    ws.sheet_view.showGridLines = ws.title in ("LCIA (Annex 1)",)
out = ROOT / "excel" / "IMTA_KPI_decision_tool.xlsx"
out.parent.mkdir(exist_ok=True)
wb.save(out)
print("written", out.relative_to(ROOT))
