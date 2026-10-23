# References

## Primary data source
- INTEGRATE project (2020). *LCA of aquaculture systems: comparison between semi-intensive/extensive pond IMTA and
  semi-intensive traditional fishpond production.* Deliverable PI05#3, Interreg Atlantic Area 2014–2020, project EAPA_232/2016.
  Lead partner IPMA; contributing partners IPMA and CTAQUA. Submitted 23/07/2020. https://www.integrate-imta.eu
  – used for: all inventory data (Table 4), nutrient balance (Table 5) and impact results (Annex 1).
- Cunha, M. E., Malta, E., Partida, B., Agraso, M. M., & Ribeiro, L. (2021). Comparative life cycle assessment of semi-intensive
  and extensive pond IMTA and semi-intensive conventional fishpond production. *Aquaculture Europe 2021*, Funchal.
  https://aquaeas.org/Program/PaperDetail/38885 – conference version of the same comparison.

## Methods used in the report
- Cho, C. Y., & Kaushik, S. J. (1990). Nutritional energetics in fish: energy and protein utilization in rainbow trout (*Salmo gairdneri*).
  *World Review of Nutrition and Dietetics*, 61, 132–172. – nutrient-balance model for N, P and solids emissions.
- Wilfart, A., Aubin, J., et al. (2012). Piscentool: a tool to assess sustainability in aquaculture systems.
  8th International Conference on LCA in the Agri-Food Sector, Saint-Malo. – LCA software used.
- Aubin, J., Papatryphon, E., van der Werf, H. M. G., & Chatzifotis, S. (2009). Assessment of the environmental impact of carnivorous
  finfish production systems using life cycle assessment. *Journal of Cleaner Production*, 17, 354–361.
  https://doi.org/10.1016/j.jclepro.2008.08.008 – impact categories incl. NPPU and water dependence.
- Papatryphon, E., Petit, J., Kaushik, S. J., & van der Werf, H. M. G. (2004). Environmental impact assessment of salmonid feeds using
  life cycle assessment. *Ambio*, 33(6), 316–323. – net primary production use.
- European Commission JRC (2010). ILCD Handbook – General guide for life cycle assessment – Detailed guidance. EUR 24708 EN.

## IMTA LCA background and LCI schema
- Hala, A. F., Chougule, K., Cunha, M. E., Caria Mendes, M., Oliveira, I., Bradley, T., Forbes, J., & Galileu Speranza, L. (2024).
  Life cycle assessment of integrated multi-trophic aquaculture: A review on methodology and challenges for its sustainability
  evaluation. *Aquaculture*, 590, 741035. https://doi.org/10.1016/j.aquaculture.2024.741035
  – used for: multi-product functional unit and allocation challenges of IMTA LCA.
- Bohnes, F. A., Hauschild, M. Z., Schlundt, J., & Laurent, A. (2019). Life cycle assessments of aquaculture systems: a critical review
  of reported findings with recommendations for policy and system development. *Reviews in Aquaculture*, 11, 1061–1079.
  https://doi.org/10.1111/raq.12280
- Nair, R. R., Chougule, K. M., Gomez Trillos, J. C., & Brand-Daniels, U. (2025). A generalized schema to publish and share life cycle
  inventories (LCI): Exemplary case of an aviation fuel supply chain. *Journal of Cleaner Production*, 520, 146120.
  https://doi.org/10.1016/j.jclepro.2025.146120 – LCIS2024 structure of `data/lci/`.

## What comes from where
- **From the report:** every number in `data/report/` (page, table and annex in the `source` column) and therefore all
  impact results, inventory flows and nutrient balances.
- **Added in this repository:** the scaling to the functional unit, the recalculated feed N and P, the KPI definitions
  and targets (placeholders), and the data checks.
