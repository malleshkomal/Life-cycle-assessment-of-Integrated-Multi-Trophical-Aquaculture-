# openLCA results (ecoinvent 3.7 cut-off, EF 3.1)

These runs model **IMTA without waste valorisation** (fish + seaweed + mussels). The valorisation loops of scenario C
change climate change by less than 0.1 % in the illustrative model, so the runs are a close proxy for C.

Aggregated results only. Raw openLCA exports (process-level inventories and contribution matrices)
contain licensed ecoinvent data and are **not** included.

| Run | Model | Allocation | Climate change, per kg sea bream | Status |
|---|---|---|---|---|
| run1 | IMTA (no valorisation), providers by auto-link | economic | 1.83 kg CO2-eq | electricity provider/amount not verified |
| run2 | IMTA (no valorisation) "KOMAL imta" | **none** | 3.94 kg CO2-eq | superseded (wrong allocation) |
| run3 | IMTA (no valorisation) "KOMAL imta" | economic | 4.95 kg CO2-eq | **electricity provider is lignite-dominated – known issue** |

Literature for comparison: 2.27 kg CO2-eq/kg for gilthead sea bream, cradle-to-gate (Kallitsis & Avramidis 2025).

Files:
- `results_summary.csv` – all EF 3.1 impact categories per run, total (40,000 kg fish) and per kg fish.
- `contributions_grouped.csv` – direct process contributions grouped by type (land use change, crop farming,
  electricity, fuels and heat, transport, farm direct, ...) for climate change and marine eutrophication.

![run 3 contributions](../../results/charts/05_openlca_run3_contributions.png)

See `../../docs/known_issues.md` before using these numbers.
