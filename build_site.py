"""Build docs/index.html: one self-contained findings page (charts embedded, no internet needed).

Open it in any browser offline, or publish it with GitHub Pages (Settings -> Pages -> main /docs).
"""
import base64
import csv
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CH = ROOT / "results" / "charts"


def img(name, alt):
    b = base64.b64encode((CH / name).read_bytes()).decode()
    mime = "image/gif" if name.endswith(".gif") else "image/png"
    return f'<figure><img alt="{html.escape(alt)}" src="data:{mime};base64,{b}"><figcaption>{html.escape(alt)}</figcaption></figure>'


def fmt(v):
    return f"{v:,.0f}" if abs(v) >= 100 else f"{v:.3g}"


kp = list(csv.DictReader(open(ROOT / "results/kpis.csv", encoding="utf-8")))
codes = list(dict.fromkeys(r["scenario"] for r in kp))
name = {"imta-A": "A: fish monoculture", "imta-C": "C: IMTA + waste valorisation"}
rows = ""
for kid in dict.fromkeys(r["id"] for r in kp):
    rs = {r["scenario"]: r for r in kp if r["id"] == kid}
    r0 = rs[codes[0]]
    sign = "≤" if r0["better_if"] == "lower" else "≥"
    cells = "".join(f'<td class="{"ok" if rs[c]["met"] == "True" else "no"}">{fmt(float(rs[c]["value"]))}</td>' for c in codes)
    rows += f"<tr><td>{kid}</td><td>{html.escape(r0['kpi'])}</td><td>{html.escape(r0['unit'])}</td><td>{sign} {float(r0['target']):g}</td>{cells}</tr>"
head = "".join(f"<th>{name.get(c, c)}</th>" for c in codes)

page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>IMTA LCA Findings</title>
<style>
:root{{--bg:#fbfaf7;--fg:#1f1e1c;--mut:#5f5e5a;--line:#d3d1c7;--ok:#c6efce;--no:#ffc7ce}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#1c1b19;--fg:#ecebe6;--mut:#b4b2a9;--line:#444441;--ok:#27500a;--no:#791f1f}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,-apple-system,Segoe UI,Arial,sans-serif}}
main{{max-width:900px;margin:0 auto;padding:24px 16px 64px}} h1{{font-size:1.6rem;margin:.2em 0}} h2{{font-size:1.2rem;margin-top:2em}}
.note{{border-left:4px solid #ba7517;padding:8px 12px;background:rgba(186,117,23,.08)}}
table{{border-collapse:collapse;width:100%;font-size:.9rem}} th,td{{border:1px solid var(--line);padding:6px 8px;text-align:left}}
td.ok{{background:var(--ok)}} td.no{{background:var(--no)}} .wrap{{overflow-x:auto}}
figure{{margin:16px 0}} .flow{{overflow-x:auto;background:#fff;border-radius:10px;border:1px solid var(--line)}} .flow svg{{display:block;max-width:100%;height:auto}} img{{max-width:100%;height:auto;background:#fff;border-radius:6px}} figcaption{{color:var(--mut);font-size:.85rem}}
</style></head><body><main>
<h1>Life cycle assessment of fish monoculture and IMTA aquaculture</h1>
<p>Circular KPI decision tool: gilthead sea bream farm in Portugal, <b>A: fish monoculture</b> vs <b>C: IMTA</b> (fish + seaweed + mussels) with valorisation of seaweed residues and mussel shells.
Functional unit: 1 kg fresh sea bream at farm gate, economic allocation.</p>
<p class="note">Demonstration study. Activity data are assumptions checked against literature ranges; KPI values use <b>illustrative</b> impact factors, not ecoinvent. ecoinvent results and their open issues are shown in section 5.</p>
<h2>Key findings</h2>
<ol>
<li><b>IMTA lowers the footprint per kg of fish</b> (2.90 → 2.12 kg CO2-eq/kg) and recovers about 18 % of the nitrogen the fish release.</li>
<li><b>The farm as a whole emits about 9 % more CO2</b> (energy, boats, ropes, transport) – an absolute-vs-relative trade-off.</li>
<li><b>Waste valorisation lifts circularity KPIs</b> (by-product valorisation 0 → 100 %) but its climate effect is small next to feed.</li>
<li><b>Feed is the hotspot</b>; in ecoinvent, land use change from Brazilian soy is a major contributor.</li>
</ol>
<h2>KPI scorecard</h2><div class="wrap"><table><tr><th>ID</th><th>KPI</th><th>Unit</th><th>Target</th>{head}</tr>{rows}</table></div>
<h2>How the waste is used</h2>
<div class="flow">{(CH / "06_waste_flow_animated.svg").read_text(encoding="utf-8").split("?>")[-1]}</div>
<h2>Charts</h2>
{img("anim_01_nitrogen_balance.gif", "Nitrogen balance: where the nitrogen from the feed goes")}
{img("anim_02_climate_by_contributor.gif", "Climate change by contributor, whole farm (illustrative factors)")}
{img("anim_03_per_kg_vs_total.gif", "Per kg of fish vs whole farm")}
{img("anim_04_circularity_kpis.gif", "Circularity and economic KPIs against their targets")}
{img("anim_05_openlca_run3.gif", "openLCA run 3 with ecoinvent 3.7 / EF 3.1 – not final (electricity provider issue)")}
<h2>Method and sources</h2>
<p>LCI shared in the LCIS2024 structure (Nair, Chougule, Gomez &amp; Brand-Daniels 2025, <i>J. Clean. Prod.</i> 520, 146120). Functional unit and allocation choices follow the IMTA challenges discussed in Hala, Chougule et al. (2024), <i>Aquaculture</i> 590, 741035.
Full documentation, data and code: see the repository README, <code>docs/</code> and <code>sources/REFERENCES.md</code>.</p>
<p style="color:var(--mut);font-size:.85rem">Komal Mallesh Chougule · CC BY 4.0 (data) · MIT (code)</p>
</main></body></html>"""
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs" / "index.html").write_text(page, encoding="utf-8")
print("written docs/index.html", round(len(page) / 1024), "kB")
