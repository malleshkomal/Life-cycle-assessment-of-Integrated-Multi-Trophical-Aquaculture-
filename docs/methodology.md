# Methodology

## 1. Life cycle inventory (LCI)
For each scenario, one foreground process lists all inputs and outputs per year
(`data/lci/dataset/imta-cirkpi-lci.csv`, LCIS2024 column prefixes `ap_` = activity property, `fp_` = flow property).

Direct emissions come from simple balances:

- CO2 from boats = diesel [kg] × 3.16
- N to sea = N in feed − N in fish − N in seaweed (incl. collected residues) − N in mussels
- P to sea = same logic for phosphorus

## 2. Impact assessment (LCIA)
Impact = Σ (amount of each flow × impact factor of that flow).

- **In openLCA** the impact factor of each input is calculated from its whole ecoinvent supply chain
  (matrix inversion: scaling vector s = A⁻¹ f, inventory g = B s, impacts h = C g).
- **In the KPI tool** (`src/imtakpi/model.py`, Excel) the per-unit factors are read from a table.
  The shipped table is **illustrative**. Real per-unit factors are obtained by calculating 1 unit of
  each input in openLCA.

Avoided products (scenario C) enter with a negative sign (system expansion).

## 3. Allocation
Scenario C produces three products. The farm's total impact is split by **economic value**:

share_fish = revenue_fish / (revenue_fish + revenue_seaweed + revenue_mussels) = 280,000 / 417,500 = 0.671

Result per functional unit = farm impact × share_fish / 40,000 kg.
Mass allocation (fish 34.8 %) is reported as a sensitivity in the Excel tool.

## 4. KPI framework
Every KPI = question → formula → data source → target → pass/fail.

| ID | Dimension | KPI | Formula | Target |
|---|---|---|---|---|
| E1 | Environment | Carbon footprint of fish | farm CO2-eq × share_fish / kg fish | ≤ 2.0 kg CO2-eq/kg |
| E2 | Environment | Marine eutrophication of fish | farm N-eq × share_fish / kg fish | ≤ 0.08 kg N-eq/kg |
| E3 | Environment | Energy demand of fish (Excel only) | farm MJ × share_fish / kg fish | ≤ 40 MJ/kg |
| E4 | Environment | Feed share of climate impact | feed CO2-eq / total CO2-eq | ≤ 75 % |
| C1 | Circularity | Nitrogen recovery rate | N in seaweed + mussels / (N feed − N fish) | ≥ 15 % |
| C2 | Circularity | Phosphorus recovery rate | P in seaweed + mussels / (P feed − P fish) | ≥ 10 % |
| C3 | Circularity | Nitrogen use efficiency | N in all products / N in feed | ≥ 35 % |
| C4 | Circularity | Feed conversion ratio | kg feed / kg fish | ≤ 1.7 |
| C5 | Circularity | Share of non-fed biomass | (seaweed + mussels) / total harvest | ≥ 50 % |
| C6 | Circularity | By-product valorisation rate | (residues collected + shells valorised) / (residues generated + shells) | ≥ 50 % |
| B1 | Economy | Eco-efficiency | revenue / t CO2-eq (farm) | ≥ 3,000 EUR/t |
| B2 | Economy | Revenue share of extractive species | (revenue seaweed + mussels) / total revenue | ≥ 25 % |

Targets are placeholders; in practice they would be agreed with the company (e.g. in a workshop).
Circularity KPIs come from the mass balance and do not depend on the LCA database; environmental
KPIs do. Reading both together reveals trade-offs that a single score would hide.

## 5. Verification
- `run.py`, the Excel tool (`excel/`) and `openlca/IMTA_example_runnable_openLCA.zip` use the same
  illustrative factors and give identical results (scenario C: 2.125 kg CO2-eq/kg, 0.0725 kg N-eq/kg).
- The ecoinvent run (`data/openlca_results/`) was compared with literature (2.27 kg CO2-eq/kg for Greek
  gilthead sea bream) – see `docs/known_issues.md` for why the current run is not yet final.
