"""Draw the animated waste-flow diagram of the IMTA farm (scenario C) as SVG.

Output: results/charts/06_waste_flow_animated.svg (shown in the README) and docs/flow.html (offline page).
Numbers come from the model (src/imtakpi), so the diagram stays consistent with the KPIs.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from imtakpi import run_all, load  # noqa: E402

res = run_all()["imta-C"]
inv, par, _ = load()
x = inv["imta-C"]
N = res["nutrients"]["N"]
shells = x["ground limestone (avoided)"][1]
fert = x["mineral N fertiliser (avoided)"][1]
residues = par["seaweed_residues"]
mussels = x["Mussels, fresh, at farm gate"][1]

W, H = 1140, 560
NW, NH = 170, 66
# node: key -> (x, y, fill, stroke, title, subtitle, delay)
NODES = {
    "feed":  (25, 235, "#FAEEDA", "#BA7517", "Fish feed", f"{par['feed_total']/1000:.0f} t · {N['feed']:,.0f} kg N", 0.0),
    "fish":  (255, 235, "#EEEDFE", "#534AB7", "Fish cages", "sea bream, fed", 0.3),
    "bream": (485, 235, "#EEEDFE", "#534AB7", "Sea bream", f"{x['Sea bream, fresh, at farm gate'][1]/1000:.0f} t product", 0.9),
    "sw":    (485, 70, "#E1F5EE", "#0F6E56", "Seaweed lines", f"takes up {N['seaweed']:,.0f} kg N", 0.9),
    "mu":    (485, 400, "#FAECE7", "#993C1D", "Mussel lines", f"filters {N['mussels']:,.0f} kg N", 0.9),
    "sea":   (255, 440, "#FCEBEB", "#A32D2D", "Lost to the sea", f"{N['to_sea']:,.0f} kg N", 0.9),
    "swfood": (715, 15, "#E1F5EE", "#0F6E56", "Seaweed food", f"{x['Seaweed, fresh, at farm gate'][1]/1000:.0f} t product", 1.5),
    "comp":  (715, 125, "#EAF3DE", "#3B6D11", "Composting", f"{residues/1000:.0f} t residues", 1.5),
    "fert":  (955, 125, "#EAF3DE", "#3B6D11", "Soil fertiliser", f"replaces {fert:.0f} kg mineral N", 2.1),
    "mufood": (715, 345, "#FAECE7", "#993C1D", "Mussels", f"{mussels/1000:.0f} t product", 1.5),
    "crush": (715, 455, "#E6F1FB", "#185FA5", "Shell crushing", f"{shells/1000:.0f} t shells", 1.5),
    "lime":  (955, 455, "#E6F1FB", "#185FA5", "Lime", f"replaces {shells/1000:.0f} t limestone", 2.1),
}


def port(k, side):
    x0, y0 = NODES[k][0], NODES[k][1]
    return {"l": (x0, y0 + NH / 2), "r": (x0 + NW, y0 + NH / 2), "t": (x0 + NW / 2, y0), "b": (x0 + NW / 2, y0 + NH)}[side]


def curve(a, b):
    (x1, y1), (x2, y2) = a, b
    if abs(y1 - y2) < 1:
        return f"M{x1},{y1} L{x2},{y2}"
    if abs(x1 - x2) < 1:
        return f"M{x1},{y1} L{x2},{y2}"
    mx = (x1 + x2) / 2
    return f"M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}"


# edges: (from, side, to, side, colour, label, width, delay)
EDGES = [
    ("feed", "r", "fish", "l", "#BA7517", "feed", 6, 0.2),
    ("fish", "r", "bream", "l", "#534AB7", "harvest", 5, 0.7),
    ("fish", "t", "sw", "l", "#1D9E75", "dissolved N, P", 4, 0.7),
    ("fish", "b", "mu", "l", "#D85A30", "particles", 4, 0.7),
    ("fish", "b", "sea", "t", "#E24B4A", "unused N", 4, 0.7),
    ("sw", "r", "swfood", "l", "#1D9E75", "harvest", 4, 1.3),
    ("sw", "r", "comp", "l", "#639922", "residues", 4, 1.3),
    ("comp", "r", "fert", "l", "#639922", "compost", 4, 1.9),
    ("mu", "r", "mufood", "l", "#D85A30", "harvest", 4, 1.3),
    ("mu", "r", "crush", "l", "#378ADD", "shells", 4, 1.3),
    ("crush", "r", "lime", "l", "#378ADD", "lime", 4, 1.9),
]

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" font-family="Segoe UI, Arial, sans-serif">',
       "<title>How the waste is used in the IMTA farm</title>",
       "<desc>Fish waste feeds seaweed and mussels; seaweed residues are composted into fertiliser; mussel shells are crushed into lime.</desc>",
       """<style>
.flow{fill:none;stroke-linecap:round;stroke-dasharray:10 9;animation:dash 1.2s linear infinite, show .6s ease-out both}
.base{fill:none;stroke-linecap:round;opacity:.18;animation:show .6s ease-out both}
.node{animation:pop .6s cubic-bezier(.2,.8,.2,1.2) both}
.lab{font-size:12px;fill:#444441;animation:show .6s ease-out both}
.t{font-size:15px;font-weight:600}.s{font-size:12px}
@keyframes dash{to{stroke-dashoffset:-38}}
@keyframes show{from{opacity:0}to{opacity:1}}
@keyframes pop{from{opacity:0;transform:scale(.85)}to{opacity:1;transform:scale(1)}}
</style>""",
       f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
       '<text x="25" y="30" font-size="18" font-weight="600" fill="#2C2C2A">How the waste is used: IMTA with waste valorisation</text>',
       '<text x="25" y="52" font-size="12" fill="#5F5E5A">one year · scenario C · nitrogen in kg N</text>']
for i, (a, sa, b, sb, col, lab, w, d) in enumerate(EDGES):
    path = curve(port(a, sa), port(b, sb))
    svg.append(f'<path class="base" d="{path}" stroke="{col}" stroke-width="{w + 6}" style="animation-delay:{d}s"/>')
    svg.append(f'<path id="e{i}" class="flow" d="{path}" stroke="{col}" stroke-width="{w}" style="animation-delay:0s,{d}s"/>')
    svg.append(f'<circle r="{w/2 + 2.5}" fill="{col}" opacity="0"><set attributeName="opacity" to="1" begin="{d + .4}s"/>'
               f'<animateMotion dur="2.4s" begin="{d + .4}s" repeatCount="indefinite"><mpath href="#e{i}"/></animateMotion></circle>')
    (x1, y1), (x2, y2) = port(a, sa), port(b, sb)
    lx, ly = (x1 + x2) / 2, (y1 + y2) / 2 - 8
    if lab in ("unused N",):
        lx, ly = x1 + 8, (y1 + y2) / 2
    if lab == "particles":
        lx, ly = x1 + 95, y1 + 70
    if lab == "dissolved N, P":
        lx, ly = x1 + 70, y1 - 70
    svg.append(f'<text class="lab" x="{lx}" y="{ly}" text-anchor="{"start" if lab in ("unused N", "particles", "dissolved N, P") else "middle"}" style="animation-delay:{d + .3}s">{lab}</text>')
for k, (x0, y0, fill, stroke, t, s, d) in NODES.items():
    svg.append(f'<g class="node" style="animation-delay:{d}s;transform-origin:{x0 + NW/2}px {y0 + NH/2}px">'
               f'<rect x="{x0}" y="{y0}" width="{NW}" height="{NH}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
               f'<text class="t" x="{x0 + NW/2}" y="{y0 + 27}" text-anchor="middle" fill="{stroke}">{t}</text>'
               f'<text class="s" x="{x0 + NW/2}" y="{y0 + 48}" text-anchor="middle" fill="{stroke}">{s}</text></g>')
svg.append(f'<text x="{W - 25}" y="{H - 12}" text-anchor="end" font-size="11" fill="#888780">Illustrative data · github.com/malleshkomal</text>')
svg.append("</svg>")
out = "\n".join(svg)
(ROOT / "results" / "charts").mkdir(parents=True, exist_ok=True)
(ROOT / "results" / "charts" / "06_waste_flow_animated.svg").write_text(out, encoding="utf-8")

page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>IMTA Waste Flow</title>
<style>body{{margin:0;background:#fbfaf7;color:#1f1e1c;font:16px/1.6 system-ui,Segoe UI,Arial,sans-serif}}
main{{max-width:1140px;margin:0 auto;padding:20px 16px 48px}} .wrap{{overflow-x:auto;background:#fff;border-radius:12px;border:1px solid #d3d1c7}}
svg{{display:block;max-width:100%;height:auto}} ol{{padding-left:1.2em}} li{{margin:.3em 0}} .k{{font-weight:600}}</style></head><body><main>
<h1 style="font-size:1.5rem">How the waste is used in the IMTA farm</h1>
<div class="wrap">{out}</div>
<ol>
<li><span class="k" style="color:#BA7517">Feed</span> goes to the fish: {N['feed']:,.0f} kg nitrogen per year. The fish keep {N['fish']:,.0f} kg N.</li>
<li><span class="k" style="color:#1D9E75">Seaweed</span> takes up dissolved fish waste ({N['seaweed']:,.0f} kg N, incl. collected residues); <span class="k" style="color:#D85A30">mussels</span> filter particles ({N['mussels']:,.0f} kg N).</li>
<li>{N['to_sea']:,.0f} kg N is still <span class="k" style="color:#E24B4A">lost to the sea</span> – {N['recovered']/N['released']:.0%} of the fish waste is recovered.</li>
<li><span class="k" style="color:#639922">Seaweed residues</span> ({residues/1000:.0f} t) are composted and replace {fert:.0f} kg of mineral nitrogen fertiliser.</li>
<li><span class="k" style="color:#378ADD">Mussel shells</span> ({shells/1000:.0f} t) are crushed into lime and replace {shells/1000:.0f} t of ground limestone.</li>
</ol>
<p style="color:#5f5e5a;font-size:.85rem">Illustrative data. Part of the repository “Life cycle assessment of fish monoculture and IMTA aquaculture”.</p>
</main></body></html>"""
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs" / "flow.html").write_text(page, encoding="utf-8")
print("written results/charts/06_waste_flow_animated.svg and docs/flow.html")
