import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from imtakpi import run_all, load, impacts  # noqa: E402

RES = run_all()


def kpi(code, kid):
    return next(k["value"] for k in RES[code]["kpis"] if k["id"] == kid)


@pytest.mark.parametrize("code", ["imta-A", "imta-C"])
@pytest.mark.parametrize("el", ["N", "P"])
def test_nutrient_balance_closes(code, el):
    d = RES[code]["nutrients"][el]
    assert d["fish"] + d["seaweed"] + d["mussels"] + d["to_sea"] == pytest.approx(d["feed"])


def test_lci_nitrogen_matches_mass_balance():
    inv, _, _ = load()
    assert inv["imta-A"]["Nitrogen"][1] == pytest.approx(RES["imta-A"]["nutrients"]["N"]["to_sea"])
    # scenario C: 2,450 kg to sea + 5 kg lost from compost use
    assert inv["imta-C"]["Nitrogen"][1] == pytest.approx(RES["imta-C"]["nutrients"]["N"]["to_sea"] + 5)


def test_monoculture_recovers_nothing():
    assert kpi("imta-A", "C1") == 0
    assert RES["imta-A"]["share_fish"] == 1


def test_known_values_match_excel():
    assert kpi("imta-A", "E1") == pytest.approx(2.8954, abs=1e-4)
    assert kpi("imta-C", "E1") == pytest.approx(2.1249, abs=1e-4)
    assert kpi("imta-C", "E2") == pytest.approx(0.0725, abs=1e-4)
    assert kpi("imta-C", "C1") == pytest.approx(0.1833, abs=1e-4)
    assert RES["imta-C"]["climate_total"] == pytest.approx(126733.6, abs=0.5)


def test_economic_share():
    assert RES["imta-C"]["share_fish"] == pytest.approx(280000 / 417500)


def test_linearity():
    inv, _, fac = load()
    x = inv["imta-C"]
    doubled = {f: (t, 2 * v) for f, (t, v) in x.items()}
    assert impacts(doubled, fac)[0] == pytest.approx(2 * impacts(x, fac)[0])


def test_avoided_products_are_credits():
    c = RES["imta-C"]["contrib"]
    assert c["ground limestone (avoided)"][0] < 0
    assert c["mineral N fertiliser (avoided)"][0] < 0
