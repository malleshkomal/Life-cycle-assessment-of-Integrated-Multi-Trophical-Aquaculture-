# Life cycle assessment of fish monoculture and IMTA aquaculture
## Goal and scope definition (ISO 14040/44)

## 1. Goal

**Intended application.** To compare the environmental, circularity and economic performance of a gilthead
sea bream (*Sparus aurata*) farm operated as

- **A – fish monoculture**, and
- **C – integrated multi-trophic aquaculture (IMTA)**: sea bream co-cultured with seaweed and mussels, including the
  valorisation of seaweed residues (composting) and mussel shells (lime substitute),

and to identify environmental hotspots and trade-offs that support a circular farm design decision.

**Reasons for the study.** IMTA is promoted as a circular aquaculture system: nutrients released by the fed species
(fish) are taken up by extractive species (seaweed, mussels). The study tests whether this circularity also reduces
life cycle impacts, and demonstrates how LCA results and circularity indicators can be combined in a KPI framework.

**Methodological basis.** LCA of IMTA is challenging because the system delivers several products, which complicates
the definition of the functional unit and the choice of allocation, and because harmonised data are scarce
(Hala, Chougule et al., 2024). These choices are therefore made explicit below and tested by sensitivity analysis.

**Intended audience.** Researchers and practitioners in sustainability assessment and circular decision support.

**Comparative assertion.** Yes (A vs C), for internal and demonstration use only. Activity data are illustrative;
the study is not intended for public disclosure about a real farm.

## 2. Scope

### 2.1 Product system and function
- **Product system:** coastal sea-cage farm in Portugal, one year of steady-state operation.
- **Function:** production of fresh fish for human consumption.

### 2.2 Functional unit and reference flow
- **Functional unit:** **1 kg of fresh gilthead sea bream (live weight) at the farm gate, including transport to market.**
- **Reference flow:** 40,000 kg sea bream per year, identical in A and C, so that both designs deliver the same function.

### 2.3 System boundary (cradle-to-gate + transport to market)

| Included | Excluded (cut-off) |
|---|---|
| Feed ingredients: fishmeal, fish oil, soybean meal, wheat, rapeseed oil | Fish juveniles (hatchery) – no suitable dataset |
| Electricity for pumps and aeration | Mussel seed – collected from the wild |
| Boat diesel: production and combustion (CO2) | Feed milling and feed transport |
| Polypropylene ropes and nets | Infrastructure (cages, vessels, buildings) |
| Transport to market (300 km, lorry) | Processing, retail, consumption, end of life |
| Direct N and P emissions to sea (nutrient mass balance) | Medicines, antifoulants, fish escapes, biodiversity |
| C only: composting of seaweed residues, crushing and transport of mussel shells, avoided products | Mussel biodeposits (would require a deposit-feeding species) |

### 2.4 Multifunctionality and allocation
- **C** delivers three co-products (sea bream 40 t, seaweed 50 t, mussels 25 t per year).
- **Default: economic allocation** by farm-gate revenue: sea bream 67.1 %, seaweed 18.0 %, mussels 15.0 %
  (prices 7 / 1.5 / 2.5 EUR/kg). Rationale: sea bream is the determining product.
- **Sensitivity: mass allocation** (sea bream 34.8 %).
- **Waste valorisation in C:** system expansion – avoided ground limestone (10 t shells, 1:1) and avoided mineral
  N fertiliser (25 kg N from compost) are credited before allocation.

### 2.5 Life cycle impact assessment
- **Method:** Environmental Footprint EF 3.1 (openLCA implementation "EF 3.1 Method (adapted)").
- **Focus categories:** climate change, marine eutrophication; all EF categories are reported.
- No normalisation or weighting for the comparison.

### 2.6 Data and data quality
- **Foreground:** activity data assumed and checked against literature ranges (no measured farm data).
- **Background:** ecoinvent 3.7, cut-off system model.
- **Data quality:** documented per flow (source, data type, pedigree scores) in the Excel tool, tab *Metadata*.
- **LCI documentation:** the inventory is shared in the **LCIS2024** structure – dataset, dataset properties,
  metadata, dependencies, network and environment (Nair, Chougule, Gomez & Brand-Daniels, 2025).

### 2.7 Key assumptions
1. Feed 60 t/yr (feed conversion ratio 1.5; literature for sea bream about 1.7–2.0 – optimistic).
2. Proxy feed recipe: 25 % fishmeal, 10 % fish oil, 30 % soybean meal, 25 % wheat, 10 % rapeseed oil.
3. N/P emissions = N/P in feed − N/P in all harvested biomass (contents in `data/lci/dataset/parameters.csv`).
4. Diesel 4,000 L × 0.84 kg/L = 3,360 kg; combustion 3.16 kg CO2/kg diesel.
5. Electricity: Portuguese low-voltage grid mix.
6. Steady-state operation, no stock changes.

### 2.8 Limitations
Illustrative activity data; exclusion of juveniles underestimates the footprint; nutrient recovery is an upper
estimate; EF does not capture IMTA ecosystem services. Open issues in the ecoinvent runs are listed in
[`known_issues.md`](known_issues.md).

### 2.9 Critical review
None – internal demonstration study.

## References
- Hala, A. F., Chougule, K., Cunha, M. E., Caria Mendes, M., Oliveira, I., Bradley, T., Forbes, J., & Galileu Speranza, L. (2024).
  Life cycle assessment of integrated multi-trophic aquaculture: A review on methodology and challenges for its
  sustainability evaluation. *Aquaculture*, 590, 741035.
- Nair, R. R., Chougule, K. M., Gomez, J. C., & Brand-Daniels, U. (2025). A generalized schema to publish and share
  life cycle inventories (LCI): Exemplary case of an aviation fuel supply chain. *Journal of Cleaner Production*, 520, 146120.
  https://doi.org/10.1016/j.jclepro.2025.146120
- Further sources: [`../sources/REFERENCES.md`](../sources/REFERENCES.md)
