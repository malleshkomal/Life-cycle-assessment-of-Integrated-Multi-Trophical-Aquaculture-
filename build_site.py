"""Build docs/index.html: one self-contained findings page (charts embedded, no internet needed).

Open it in any browser offline, or publish it with GitHub Pages (Settings -> Pages -> main /docs).
"""
import base64
import csv
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CH = ROOT / "results" / "charts"
NAME = {"SI-IMTA": "Semi-intensive pond IMTA", "SE-IMTA": "Semi-extensive pond IMTA", "SI-POLY": "Semi-intensive fish polyculture"}


def img(name, alt):
    b = base64.b64encode((CH / name).read_bytes()).decode()
    mime = "image/gif" if name.endswith(".gif") else "image/png"
    return f'<figure><img alt="{html.escape(alt)}" src="data:{mime};base64,{b}"><figcaption>{html.escape(alt)}</figcaption></figure>'


def fmt(v, unit):
    if unit == "%":
        return f"{v * 100:.0f} %"
    return f"{v:,.0f}" if abs(v) >= 100 else f"{v:.2f}"


kp = list(csv.DictReader(open(ROOT / "results/kpis.csv", encoding="utf-8")))
codes = list(dict.fromkeys(r["system"] for r in kp))
rows = ""
for kid in dict.fromkeys(r["id"] for r in kp):
    rs = {r["system"]: r for r in kp if r["id"] == kid}
    r0 = rs[codes[0]]
    sign = "≤" if r0["better_if"] == "lower" else "≥"
    cells = ""
    for c in codes:
        base = kid.startswith("E") and c == "SI-POLY"
        cls = "base" if base else ("ok" if rs[c]["met"] == "True" else "no")
        cells += f'<td class="{cls}">{fmt(float(rs[c]["value"]), r0["unit"])}</td>'
    tgt = fmt(float(r0["target"]), r0["unit"])
    rows += f"<tr><td>{kid}</td><td>{html.escape(r0['kpi'])}</td><td>{html.escape(r0['unit'])}</td><td>{sign} {tgt}</td>{cells}</tr>"
head = "".join(f"<th>{NAME[c]}</th>" for c in codes)
imp = list(csv.DictReader(open(ROOT / "results/impacts_per_tonne.csv", encoding="utf-8")))
irows = "".join(f"<tr><td>{r['name']}</td><td>{r['unit']}</td>" + "".join(f"<td>{float(r[c]):,.0f}</td>" for c in codes)
                + f"<td>{r['SI-IMTA vs POLY']}</td><td>{r['SE-IMTA vs POLY']}</td></tr>" for r in imp)
flow = (CH / "06_flow_si_imta.svg").read_text(encoding="utf-8")

page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pond IMTA LCA Findings</title>
<style>
:root{{--bg:#fbfaf7;--fg:#1f1e1c;--mut:#5f5e5a;--line:#d3d1c7;--ok:#c6efce;--no:#ffc7ce;--base:#f1efe8}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#1c1b19;--fg:#ecebe6;--mut:#b4b2a9;--line:#444441;--ok:#27500a;--no:#791f1f;--base:#2c2c2a}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,-apple-system,Segoe UI,Arial,sans-serif}}
main{{max-width:920px;margin:0 auto;padding:24px 16px 64px}} h1{{font-size:1.6rem;margin:.2em 0}} h2{{font-size:1.2rem;margin-top:2em}}
.note{{border-left:4px solid #1d9e75;padding:8px 12px;background:rgba(29,158,117,.08)}}
table{{border-collapse:collapse;width:100%;font-size:.88rem}} th,td{{border:1px solid var(--line);padding:5px 8px;text-align:left}}
td.ok{{background:var(--ok)}} td.no{{background:var(--no)}} td.base{{background:var(--base)}} .wrap{{overflow-x:auto}}
figure{{margin:16px 0}} .flow{{overflow-x:auto;background:#fff;border-radius:10px;border:1px solid var(--line)}} .flow svg{{display:block;max-width:100%;height:auto}}
img{{max-width:100%;height:auto;background:#fff;border-radius:6px}} figcaption{{color:var(--mut);font-size:.85rem}}
</style></head><body><main>
<h1>Life cycle assessment of pond IMTA and fish polyculture</h1>
<p>Three earthen-pond systems from the INTEGRATE project: <b>semi-intensive pond IMTA</b> (fish + oysters + macroalgae, Portugal),
<b>semi-extensive pond IMTA</b> (seabream + oysters + macroalgae pond, Spain) and a conventional <b>semi-intensive fish polyculture</b> (fish only, Portugal).
Functional unit: 1 tonne of aquatic product (fish + oyster flesh) at the farm gate, one production cycle.</p>
<p class="note">Inventory and impact results are taken from INTEGRATE deliverable PI05#3 (IPMA &amp; CTAQUA, 2020; Piscentool).
The KPI framework, targets, nutrient-balance re-calculation and data checks are added in this repository.</p>
<h2>Key findings</h2>
<ol>
<li><b>Semi-extensive IMTA has the lowest impacts</b> in 6 of 7 categories: global warming −56 %, energy −81 %, eutrophication −97 % against the polyculture. It takes up more nitrogen than the feed brings (net uptake).</li>
<li><b>Semi-intensive IMTA vs polyculture</b> (same site, same target density): eutrophication −57 % and water dependence −58 %, because oysters and macroalgae keep 47 % of the feed nitrogen in products (polyculture: 20 %). Global warming is almost the same (−1 %).</li>
<li><b>Feed is the hotspot</b> for global warming (55–66 %) and primary production use (&gt;99 %). Uneaten feed and excretion (“Rejects fish”) drive acidification and eutrophication in the semi-intensive systems.</li>
<li><b>Land is the trade-off:</b> both IMTA systems need more land per tonne (+24 % and +105 %).</li>
<li><b>Data checks:</b> the tables agree (feed N, water per tonne, process sums), with two findings to clarify – the semi-extensive FCR of 0.56 includes oyster gain, and the polyculture land value does not follow the pond-area rule.</li>
</ol>
<h2>Impacts per tonne of fish + oyster</h2><div class="wrap"><table><tr><th>Category</th><th>Unit</th>{head}<th>SI-IMTA vs POLY</th><th>SE-IMTA vs POLY</th></tr>{irows}</table></div>
<h2>KPI scorecard</h2><p style="color:var(--mut);font-size:.9rem">Environmental targets: at least 10 % better than the polyculture (grey = baseline). Circularity targets are placeholders.</p>
<div class="wrap"><table><tr><th>ID</th><th>KPI</th><th>Unit</th><th>Target</th>{head}</tr>{rows}</table></div>
<h2>How the fish waste is used (semi-intensive IMTA)</h2>
<div class="flow">{flow}</div>
<p style="font-size:.9rem">All three systems side by side: open <code>flow.html</code> in the same folder.</p>
<h2>Charts</h2>
{img("anim_02_relative_to_polyculture.gif", "All seven impact categories relative to the fish polyculture (= 100)")}
{img("anim_01_gw_by_process.gif", "Global warming by process, kg CO2-eq per tonne")}
{img("anim_03_nitrogen_fate.gif", "Where the nitrogen in the feed goes, per tonne")}
{img("anim_05_process_shares.gif", "Which process causes which impact")}
{img("anim_04_kpi_scorecard.gif", "KPI scorecard")}
<h2>Method and sources</h2>
<p>Primary source: INTEGRATE (2020) deliverable PI05#3, <i>LCA of aquaculture systems: comparison between semi-intensive/extensive pond IMTA and semi-intensive traditional fishpond production</i>
(Interreg Atlantic Area EAPA_232/2016; IPMA, CTAQUA). Nutrient emissions: Cho &amp; Kaushik (1990). Software: Piscentool (Wilfart et al. 2012).
Methodological background: Hala, Chougule et al. (2024), <i>Aquaculture</i> 590, 741035. Inventory shared in the LCIS2024 structure (Nair, Chougule et al. 2025, <i>J. Clean. Prod.</i> 520, 146120).</p>
<p style="color:var(--mut);font-size:.85rem">Komal Mallesh Chougule · code MIT · KPI layer CC BY 4.0</p>
</main></body></html>"""
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs" / "index.html").write_text(page, encoding="utf-8")
print("written docs/index.html", round(len(page) / 1024), "kB")
