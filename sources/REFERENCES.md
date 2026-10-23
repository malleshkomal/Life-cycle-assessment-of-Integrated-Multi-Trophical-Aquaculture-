# References

## LCI schema used in this repository
- Nair, R. R., Chougule, K. M., Gomez, J. C., & Brand-Daniels, U. (2025). A generalized schema to publish and share
  life cycle inventories (LCI): Exemplary case of an aviation fuel supply chain. *Journal of Cleaner Production*, 520, 146120.
  https://doi.org/10.1016/j.jclepro.2025.146120 (open access, CC BY 4.0)
- Nair, R. R. (2024). DLR Tool for Life Cycle Inventory Schema (LCIS). Zenodo. https://doi.org/10.5281/zenodo.12200857

## IMTA and aquaculture LCA
- Hala, A. F., Chougule, K., Cunha, M. E., Caria Mendes, M., Oliveira, I., Bradley, T., Forbes, J., & Galileu Speranza, L. (2024).
  Life cycle assessment of integrated multi-trophic aquaculture: A review on methodology and challenges for its
  sustainability evaluation. *Aquaculture*, 590, 741035. https://doi.org/10.1016/j.aquaculture.2024.741035
  – used for: multi-product functional unit and methodological challenges of IMTA LCA.
- García García, B., Rosique Jiménez, C., Aguado-Giménez, F., & García García, J. (2016). Life Cycle Assessment of
  Gilthead Seabream (*Sparus aurata*) Production in Offshore Fish Farms. *Sustainability*, 8(12), 1228.
  https://doi.org/10.3390/su8121228 – used for: FCR about 2 (1.7 tested); feed and vessel fuel as hotspots.
- Kallitsis, E., & Avramidis, P. (2025). Life cycle assessment of aquaculture production in Greece.
  *Cleaner Environmental Systems*. Summary: https://www.mispeces.com/en/news/Greek-Aquaculture-Life-Cycle-Assessment-Highlights-Key-Areas-for-Improvement-and-Opportunities/
  – used for: 2.27 kg CO2-eq/kg gilthead sea bream; feed up to 79 % of GHG.
- Zoli, M., Rossi, L., Costantini, M., Bibbiani, C., Fronte, B., Brambilla, F., & Bacenetti, J. (2023). Quantification and
  characterization of the environmental impact of sea bream and sea bass production in Italy.
  *Cleaner Environmental Systems*, 9, 100118. https://doaj.org/article/0c047700b22741bdb3ae6e5e47b07298
  – used for: feed ≥ 60 % of most impacts; marine eutrophication driven by nutrient emissions.
- Nederlof, M. A. J., Verdegem, M. C. J., Smaal, A. C., & Jansen, H. M. (2021). Nutrient retention efficiencies in integrated
  multi-trophic aquaculture. *Reviews in Aquaculture*. Summary (Global Seafood Alliance, 2022):
  https://www.globalseafood.org/advocate/nutrient-retention-efficiencies-in-integrated-multi-trophic-aquaculture/
  – used for: nutrient retention in fish; extractive species recover ~7 % N in open-water IMTA.
- Azizi, G. et al. (2020). Growth weight and reproductive cycle in the mussel (*Mytilus galloprovincialis*) from Cala Iris.
  EasyChair Preprint 2857. https://easychair.org/publications/preprint/P5vQ/open – rough check of mussel shell share.

## Data and methods
- ecoinvent 3.7 cut-off database (licensed). https://ecoinvent.org
- Environmental Footprint (EF) 3.1 method, European Commission JRC; implemented in openLCA LCIA methods package.
- openLCA. GreenDelta. https://www.openlca.org

## What is and is not from literature
Most activity data, nutrient contents, prices and all values in `data/factors_illustrative.csv` are **assumptions**.
Only the values explicitly marked "checked" in `data/lci/dataset/parameters.csv` were compared with the sources above,
and several differ from them (see `docs/known_issues.md`).
