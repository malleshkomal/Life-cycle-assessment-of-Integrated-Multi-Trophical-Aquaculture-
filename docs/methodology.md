# Methodology

## 1. From the report to the data files
`make_data.py` holds every number typed from INTEGRATE deliverable PI05#3 and writes:

| File | Content | Report source |
|---|---|---|
| `data/report/systems.csv` | the three systems, sites, species, periods | section 3.1 |
| `data/report/inventory_table4.csv` | inventory per production pond and cycle | Table 4 |
| `data/report/nutrients_table5.csv` | N and P balance per pond and cycle | Table 5 |
| `data/report/lcia_annex1.csv` | 7 categories × 11 processes × 3 systems, amount and share | Annex 1 |
| `data/lci/` | foreground LCI per functional unit, LCIS2024 structure | derived |

## 2. Scaling to the functional unit
Reference flow per pond = fish gain + oyster flesh gain.

scaling factor = 1,000 kg / (fish gain + oyster gain)

Every inventory flow per tonne = flow per pond × scaling factor. Example, semi-intensive IMTA:
feed 1,888 kg × 1,000 / 1,229 = 1,536 kg feed per tonne.

## 3. Nutrient balance
- N in feed = feed × protein content / 6.25; P in feed = feed × P content. This reproduces Table 5 exactly.
- N in products = N in fish + oysters + N in macroalgae (Table 5).
- N released to water = N in feed − N in products. A negative value means the system takes up nutrients from the water
  (semi-extensive IMTA: fish and oysters also eat natural food).

## 4. Impact assessment
The impact results per process are those of the report (Piscentool, Annex 1). The repository does not re-run the LCA;
it checks the results (section 6) and builds KPIs on them. The implied impact per kg of feed
(Feeds process ÷ feed per tonne) is shown in the Excel tab *Comparison* as a plausibility check:
about 1.0–1.3 kg CO2-eq and 6.8–7.8 kg C per kg feed.

## 5. KPI framework

| ID | KPI | Formula | Target |
|---|---|---|---|
| E1–E7 | GW, TCED, NPPU, AP, EP, LC, WD per tonne | Annex 1 total | ≤ polyculture × (1 − 10 %) |
| C1 | Nitrogen use efficiency | N in all products / N in feed | ≥ 35 % |
| C2 | Phosphorus use efficiency | P in all products / P in feed | ≥ 30 % |
| C3 | Net N released to water | N released × scaling factor | ≤ 60 kg N/t |
| C4 | Fish feed conversion ratio | feed / fish gain | ≤ 1.75 |
| C5 | Share of non-fed biomass | (oyster + macroalgae gain) / total harvest | ≥ 50 % |
| C6 | Feed share of global warming | Feeds / total GW | ≤ 60 % |

The improvement target (10 %) and all circularity targets are inputs (yellow cells in Excel). The polyculture is the
baseline for E1–E7, so it is shown as "baseline" there rather than pass/fail.

## 6. Data checks
`imtakpi.checks()` and the Excel tab *Data checks* compare the report's tables with each other:

1. Feed N and P = feed × recipe (Table 4 → Table 5)
2. N rejection = feed N − extracted N (Table 5)
3. Seawater per tonne = *Water consumption* in Annex 1 (confirms the functional unit)
4. FCR = feed / fish gain (Table 4)
5. Farm area allocated to the pond × cycle = *Direct activity* in Land competition (Annex 1)
6. Sum of the 11 processes = reported total, for every category and system

37 of 39 checks pass. The two that do not are explained in [`known_issues.md`](known_issues.md).

## 7. Reproducing everything
```bash
python make_data.py      # report tables -> data/report, data/lci
python run.py            # KPIs, impacts, nutrient balance, data checks -> results/*.csv
python make_excel.py     # offline Excel tool (then open it in Excel, or recalc with LibreOffice)
python make_charts.py    # all figures (PNG)
python make_flow.py      # flow diagrams (SVG) + docs/flow.html
python build_site.py     # docs/index.html
pytest
```
The Excel tool and the Python model give the same KPI values.
