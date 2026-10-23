import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from imtakpi import run_all, load, checks, nutrient_balance, per_tonne, SYSTEMS, CATEGORIES  # noqa: E402

INV, NUT, LC = load()
RES = run_all()


def kpi(s, kid):
    return next(k for k in RES[s]["kpis"] if k["id"] == kid)


def test_report_totals_are_reproduced():
    # Annex 1 / section 4 of the report, per tonne of fish + oyster
    assert RES["SI-IMTA"]["totals"]["GW"] == 2801
    assert RES["SE-IMTA"]["totals"]["GW"] == 1255
    assert RES["SI-POLY"]["totals"]["GW"] == 2836
    assert RES["SI-POLY"]["totals"]["WD"] == 393002


@pytest.mark.parametrize("s", SYSTEMS)
def test_feed_nutrients_match_table5(s):
    nb = nutrient_balance(INV, NUT, s)
    assert nb["N"]["feed"] == pytest.approx(NUT[("feed", "N")][s], abs=0.1)
    assert nb["P"]["feed"] == pytest.approx(NUT[("feed", "P")][s], abs=0.1)


@pytest.mark.parametrize("s", SYSTEMS)
def test_nitrogen_balance_closes(s):
    d = nutrient_balance(INV, NUT, s)["N"]
    assert d["feed"] == pytest.approx(d["fish_oyster"] + d["macroalgae"] + d["released"])


@pytest.mark.parametrize("s", SYSTEMS)
def test_functional_unit_scaling_matches_annex_water(s):
    # seawater per pond cycle scaled to 1 t fish + oyster equals "Water consumption" in Annex 1
    assert INV["seawater_used"][s] * per_tonne(INV, s) == pytest.approx(LC["amount"]["WD"][s]["Water consumption"], rel=0.01)


@pytest.mark.parametrize("s", SYSTEMS)
@pytest.mark.parametrize("c", CATEGORIES)
def test_processes_sum_to_total(s, c):
    parts = sum(v for p, v in LC["amount"][c][s].items() if p != "Total")
    assert parts == pytest.approx(LC["amount"][c][s]["Total"], abs=max(2, 0.005 * LC["amount"][c][s]["Total"]))


def test_semi_extensive_takes_up_nitrogen():
    assert RES["SE-IMTA"]["nutrients"]["N"]["released"] < 0
    assert kpi("SE-IMTA", "C1")["value"] > 1


def test_known_kpis():
    assert kpi("SI-IMTA", "C1")["value"] == pytest.approx(0.470, abs=0.001)
    assert kpi("SI-POLY", "C1")["value"] == pytest.approx(0.202, abs=0.001)
    assert kpi("SI-IMTA", "C4")["value"] == pytest.approx(1.72, abs=0.005)
    assert kpi("SI-POLY", "C4")["value"] == pytest.approx(1.79, abs=0.005)
    assert kpi("SI-IMTA", "C6")["value"] == pytest.approx(0.553, abs=0.001)
    assert {s: sum(k["met"] for k in RES[s]["kpis"]) for s in SYSTEMS} == {"SI-IMTA": 9, "SE-IMTA": 12, "SI-POLY": 0}


def test_baseline_target_is_ten_percent_better():
    assert kpi("SI-IMTA", "E1")["target"] == pytest.approx(2836 * 0.9)


def test_only_known_data_issues_are_flagged():
    # 1) the semi-extensive FCR in Table 4 (0.56) divides feed by fish + oyster gain, not fish gain only
    # 2) the polyculture land use in Annex 1 does not follow the pond-area allocation rule over 26 months
    bad = [(c["check"], c["system"]) for c in checks(INV, NUT, LC) if not c["ok"]]
    assert bad == [("FCR = feed / fish gain (Table 4)", "SE-IMTA"),
                   ("Land: allocated farm area = Direct activity in LC (Annex 1)", "SI-POLY")]
    assert INV["feed"]["SE-IMTA"] / (INV["fish_gain"]["SE-IMTA"] + INV["oyster_gain"]["SE-IMTA"]) == pytest.approx(0.56, abs=0.005)
