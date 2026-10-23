"""Animated flow diagrams: how the fish waste is used in each pond system (one production cycle).

Output: results/charts/06_flow_<system>.svg (one per system) and docs/flow.html (offline page with tabs).
All numbers come from data/report (Tables 4 and 5 of INTEGRATE deliverable PI05#3) via the model.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from imtakpi import run_all, load, SYSTEMS, NAMES  # noqa: E402

RES = run_all()
INV, NUT, LC = load()
W, H, NW, NH = 1140, 600, 190, 70
FILE = {"SI-IMTA": "06_flow_si_imta.svg", "SE-IMTA": "06_flow_se_imta.svg", "SI-POLY": "06_flow_si_poly.svg"}
PLACE = {"SI-IMTA": "IPMA research station, Olhao, Portugal · 700 m² pond · 5.3 months",
         "SE-IMTA": "Estero Natural, Cadiz, Spain · 665 m² fish enclosure + macroalgae pond · 8.5 months",
         "SI-POLY": "IPMA research station, Olhao, Portugal · 1,700 m² pond · 26 months · fish only"}
STYLE = """<style>
.flow{fill:none;stroke-linecap:round;stroke-dasharray:10 9;animation:dash 1.2s linear infinite, show .6s ease-out both}
.base{fill:none;stroke-linecap:round;opacity:.16;animation:show .6s ease-out both}
.node{animation:pop .6s cubic-bezier(.2,.8,.2,1.2) both}
.lab{font-size:12px;fill:#444441;animation:show .6s ease-out both}
.t{font-size:15px;font-weight:600}.s{font-size:12px}
@keyframes dash{to{stroke-dashoffset:-38}}
@keyframes show{from{opacity:0}to{opacity:1}}
@keyframes pop{from{opacity:0;transform:scale(.85)}to{opacity:1;transform:scale(1)}}
</style>"""


def kg(v):
    return f"{v:,.0f}" if abs(v) >= 100 else f"{v:,.1f}"


def build(s):
    i = {k: v[s] for k, v in INV.items()}
    n = RES[s]["nutrients"]["N"]
    rep = NUT[("total_rejection", "N")][s]
    imta = i["oyster_gain"] > 0
    tidal = s == "SE-IMTA"
    grey = ("#F1EFE8", "#B4B2A9")
    nodes = {
        "feed": (25, 75, "#FAEEDA", "#BA7517", "Fish feed", f"{kg(i['feed'])} kg · {kg(n['feed'])} kg N", 0.0),
        "fry": (25, 200, "#FBEAF0", "#993556", "Fry + oyster spat" if imta else "Fry", f"{kg(i['fish_stocked'] + i['oyster_stocked'])} kg stocked", 0.0),
        "water": (25, 325, "#E6F1FB", "#185FA5", "Seawater", f"{kg(i['seawater_used'])} m³ · {'tidal' if tidal else 'pumped'}", 0.0),
        "energy": (25, 450, "#EEEDFE", "#534AB7", "Energy", "almost none (tides)" if tidal else "pumping + aeration", 0.0),
        "pond": (300, 230, "#E1F5EE", "#0F6E56", "Fish pond" + (" + oysters" if imta else ""), "feed → fish → waste", 0.4),
        "oys": (580, 75, *(("#FAECE7", "#993C1D") if imta else grey), "Oysters", "filter particles" if imta else "none in this system", 0.9),
        "alg": (580, 385, *(("#EAF3DE", "#3B6D11") if imta else grey), "Macroalgae", ("Ulva + Gracilaria" if tidal else "Ulva") + " take up N, P" if imta else "none in this system", 0.9),
        "fish": (860, 230, "#EEEDFE", "#3C3489", "Fish", f"{kg(i['fish_gain'])} kg gained", 0.9),
        "oyout": (860, 75, *(("#FAECE7", "#993C1D") if imta else grey), "Oyster flesh", f"{kg(i['oyster_gain'])} kg" if imta else "–", 1.5),
        "algout": (860, 385, *(("#EAF3DE", "#3B6D11") if imta else grey), "Macroalgae harvest", f"{kg(i['macroalgae_gain'])} kg · {kg(n['macroalgae'])} kg N" if imta else "–", 1.5),
        "sea": (580, 505, "#FCEBEB", "#A32D2D", "Lagoon / estuary",
                (f"net uptake {kg(-rep)} kg N" if rep < 0 else f"{kg(rep)} kg N released"), 1.5 if imta else 0.9),
    }

    def port(k, side):
        x0, y0 = nodes[k][0], nodes[k][1]
        return {"l": (x0, y0 + NH / 2), "r": (x0 + NW, y0 + NH / 2), "t": (x0 + NW / 2, y0), "b": (x0 + NW / 2, y0 + NH)}[side]

    def curve(a, b):
        (x1, y1), (x2, y2) = a, b
        if abs(y1 - y2) < 1 or abs(x1 - x2) < 1:
            return f"M{x1},{y1} L{x2},{y2}"
        if abs(x1 - x2) < 60:
            my = (y1 + y2) / 2
            return f"M{x1},{y1} C{x1},{my} {x2},{my} {x2},{y2}"
        mx = (x1 + x2) / 2
        return f"M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}"

    def wN(v):
        return 3 + 9 * min(abs(v) / max(n["feed"], 1e-9), 1)

    edges = [("feed", "r", "pond", "l", "#BA7517", f"{kg(n['feed'])} kg N", wN(n["feed"]), 0.2),
             ("fry", "r", "pond", "l", "#D4537E", "", 3, 0.2),
             ("water", "r", "pond", "l", "#378ADD", "", 3, 0.2),
             ("energy", "r", "pond", "l", "#7F77DD", "", 2.5, 0.2),
             ("pond", "r", "fish", "l", "#534AB7", "harvest", 5, 0.7)]
    if imta:
        edges += [("pond", "t", "oys", "l", "#D85A30", "particles", 4, 0.7),
                  ("oys", "r", "oyout", "l", "#D85A30", "harvest", 4, 1.3),
                  ("pond", "b", "alg", "l", "#1D9E75", "dissolved N, P", wN(n["macroalgae"]), 0.7),
                  ("alg", "r", "algout", "l", "#1D9E75", f"{kg(n['macroalgae'])} kg N", wN(n["macroalgae"]), 1.3)]
    if rep < 0:
        edges.append(("sea", "t", "alg", "b", "#1D9E75", "natural food + nutrients", 4, 1.3))
    else:
        edges.append(("alg" if imta else "pond", "b", "sea", "t" if imta else "l", "#E24B4A", f"{kg(rep)} kg N", wN(rep), 1.3 if imta else 0.7))

    pid = s.lower()
    title = f"How the fish waste is used: {NAMES[s][0].lower() + NAMES[s][1:]}"
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" font-family="Segoe UI, Arial, sans-serif">',
           f"<title>{title}</title>",
           f"<desc>Flows of feed, water and nitrogen through the {NAMES[s].lower()} in one production cycle (INTEGRATE deliverable PI05#3, Tables 4 and 5).</desc>",
           STYLE, f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
           f'<text x="25" y="30" font-size="18" font-weight="600" fill="#2C2C2A">{title[0].upper() + title[1:]}</text>',
           f'<text x="25" y="52" font-size="12" fill="#5F5E5A">{PLACE[s]} · one production cycle · nitrogen in kg N</text>']
    for j, (a, sa, b, sb, col, lab, w, d) in enumerate(edges):
        p1, p2 = port(a, sa), port(b, sb)
        path = curve(p1, p2)
        eid = f"{pid}-e{j}"
        out.append(f'<path class="base" d="{path}" stroke="{col}" stroke-width="{w + 6:.1f}" style="animation-delay:{d}s"/>')
        out.append(f'<path id="{eid}" class="flow" d="{path}" stroke="{col}" stroke-width="{w:.1f}" style="animation-delay:0s,{d}s"/>')
        out.append(f'<circle r="{w / 2 + 2.5:.1f}" fill="{col}" opacity="0"><set attributeName="opacity" to="1" begin="{d + .4}s"/>'
                   f'<animateMotion dur="2.4s" begin="{d + .4}s" repeatCount="indefinite"><mpath href="#{eid}"/></animateMotion></circle>')
        if lab:
            lx, ly, anc = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 - 10, "middle"
            if a == "feed":
                lx, ly, anc = p1[0] + 12, p1[1] - 10, "start"
            elif sa == "t" or sa == "b":
                lx, ly, anc = p1[0] + 12, (p1[1] + p2[1]) / 2, "start"
                if sa == "b" and a == "pond":
                    lx, ly, anc = p1[0] + 80, (p1[1] + p2[1]) / 2 + 22, "end"
            elif a == "sea":
                lx, ly, anc = p1[0] + 12, (p1[1] + p2[1]) / 2 + 4, "start"
            out.append(f'<text class="lab" x="{lx:.0f}" y="{ly:.0f}" text-anchor="{anc}" style="animation-delay:{d + .3}s">{lab}</text>')
    for k, (x0, y0, fill, stroke, t, sub, d) in nodes.items():
        dash = ' stroke-dasharray="5 4"' if fill == grey[0] else ""
        out.append(f'<g class="node" style="animation-delay:{d}s;transform-origin:{x0 + NW / 2}px {y0 + NH / 2}px">'
                   f'<rect x="{x0}" y="{y0}" width="{NW}" height="{NH}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}/>'
                   f'<text class="t" x="{x0 + NW / 2}" y="{y0 + 29}" text-anchor="middle" fill="{stroke}">{t}</text>'
                   f'<text class="s" x="{x0 + NW / 2}" y="{y0 + 50}" text-anchor="middle" fill="{stroke}">{sub}</text></g>')
    eff = n["use_efficiency"]
    out.append(f'<text x="860" y="520" font-size="13" font-weight="600" fill="#2C2C2A">N in products: {kg(n["extracted"])} kg</text>')
    parts = f'fish + oysters {kg(n["fish_oyster"])} · macroalgae {kg(n["macroalgae"])}' if n["macroalgae"] else f'fish {kg(n["fish_oyster"])}'
    out.append(f'<text x="860" y="540" font-size="12" fill="#5F5E5A">{parts}</text>')
    out.append(f'<text x="860" y="560" font-size="12" fill="#5F5E5A">N use efficiency {eff:.0%}</text>')
    out.append(f'<text x="{W - 25}" y="{H - 10}" text-anchor="end" font-size="11" fill="#888780">Data: INTEGRATE deliverable PI05#3 (IPMA, CTAQUA 2020)</text>')
    out.append("</svg>")
    return "\n".join(out)


(ROOT / "results" / "charts").mkdir(parents=True, exist_ok=True)
svgs = {}
for s in SYSTEMS:
    svgs[s] = build(s)
    (ROOT / "results" / "charts" / FILE[s]).write_text(svgs[s], encoding="utf-8")


def story(s):
    n, i = RES[s]["nutrients"]["N"], {k: v[s] for k, v in INV.items()}
    if s == "SI-POLY":
        return (f"<li>Only fish are farmed. Of the {kg(n['feed'])} kg N in the feed, {kg(n['fish_oyster'])} kg ends up in the fish.</li>"
                f"<li><b style='color:#E24B4A'>{kg(NUT[('total_rejection', 'N')][s])} kg N</b> ({n['released'] / n['feed']:.0%}) leaves with the outflow water – there are no oysters or macroalgae to catch it.</li>")
    out = (f"<li><b style='color:#BA7517'>Feed</b> brings {kg(n['feed'])} kg N into the pond.</li>"
           f"<li><b style='color:#D85A30'>Oysters</b> filter particles (uneaten feed, faeces, plankton); fish and oysters together hold {kg(n['fish_oyster'])} kg N.</li>"
           f"<li><b style='color:#1D9E75'>Macroalgae</b> take up dissolved N and P: {kg(n['macroalgae'])} kg N in {kg(i['macroalgae_gain'])} kg of algae.</li>")
    if n["released"] < 0:
        out += (f"<li>The system takes up more N than the feed brings: a <b style='color:#1D9E75'>net uptake of {kg(-NUT[('total_rejection', 'N')][s])} kg N</b> "
                f"from the estuary water (reported in Table 5). Fish and oysters also eat natural food.</li>")
    else:
        out += f"<li><b style='color:#E24B4A'>{kg(NUT[('total_rejection', 'N')][s])} kg N</b> is still released – {n['use_efficiency']:.0%} of the feed N is recovered in products.</li>"
    return out


tabs = "".join(f'<button role="tab" aria-selected="{"true" if j == 0 else "false"}" data-s="{s}">{NAMES[s]}</button>' for j, s in enumerate(SYSTEMS))
panels = "".join(f'<section data-s="{s}"{" hidden" if j else ""}><div class="wrap">{svgs[s]}</div><ol>{story(s)}</ol></section>'
                 for j, s in enumerate(SYSTEMS))
page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pond IMTA Waste Flows</title>
<style>body{{margin:0;background:#fbfaf7;color:#1f1e1c;font:16px/1.6 system-ui,Segoe UI,Arial,sans-serif}}
main{{max-width:1140px;margin:0 auto;padding:20px 16px 48px}} .wrap{{overflow-x:auto;background:#fff;border-radius:12px;border:1px solid #d3d1c7}}
svg{{display:block;max-width:100%;height:auto}} li{{margin:.3em 0}}
[role=tablist]{{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}} button{{font:inherit;padding:6px 14px;border-radius:20px;border:1px solid #b4b2a9;background:#fff;cursor:pointer}}
button[aria-selected=true]{{background:#0f6e56;color:#fff;border-color:#0f6e56}}</style></head><body><main>
<h1 style="font-size:1.5rem;margin-bottom:0">How the fish waste is used in pond IMTA</h1>
<p style="margin-top:4px;color:#5f5e5a">One production cycle per system. Switch between the three systems of the INTEGRATE study.</p>
<div role="tablist">{tabs}</div>{panels}
<p style="color:#5f5e5a;font-size:.85rem">Data: INTEGRATE deliverable PI05#3, Tables 4 and 5 (IPMA, CTAQUA 2020). Fish and oyster N are reported together.
Part of the repository “Life cycle assessment of fish monoculture and IMTA aquaculture”.</p>
<script>
document.querySelectorAll('[role=tab]').forEach(b=>b.addEventListener('click',()=>{{
 document.querySelectorAll('[role=tab]').forEach(x=>x.setAttribute('aria-selected',x===b));
 document.querySelectorAll('section[data-s]').forEach(p=>{{p.hidden=p.dataset.s!==b.dataset.s; if(!p.hidden){{const sv=p.querySelector('svg'); const c=sv.cloneNode(true); sv.replaceWith(c);}}}});
}}));
</script>
</main></body></html>"""
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs" / "flow.html").write_text(page, encoding="utf-8")
print("written", ", ".join(FILE.values()), "and docs/flow.html")
