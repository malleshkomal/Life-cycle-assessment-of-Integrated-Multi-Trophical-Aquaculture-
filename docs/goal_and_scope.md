# Life cycle assessment of fish monoculture and IMTA aquaculture
## Goal and scope definition (ISO 14040/44)

The study re-uses the inventory and impact results of the INTEGRATE project, deliverable PI05#3
(*LCA of aquaculture systems: comparison between semi-intensive/extensive pond IMTA and semi-intensive traditional fishpond production*,
IPMA and CTAQUA, 2020). This repository adds a KPI framework, a nutrient-balance re-calculation and data checks.

## 1. Goal

**Intended application.** Compare the potential environmental impacts of two pond IMTA systems with a conventional fish-only pond,
identify hotspots, and turn the results into KPIs that support a farm design decision.

| Code | System | Site | Species |
|---|---|---|---|
| **SI-IMTA** | Semi-intensive pond IMTA | IPMA Aquaculture Research Station (EPPO), Olhão, Portugal | meagre, white seabream, flathead mullet + Pacific oyster (triploid) + macroalgae (*Ulva* spp.) |
| **SE-IMTA** | Semi-extensive pond IMTA | Estero Natural, Cádiz, Spain | gilthead seabream + Pacific oyster; macroalgae (*Ulva*, *Gracilaria*) in a second pond fed by the fishpond outflow |
| **SI-POLY** | Semi-intensive fishpond polyculture (**baseline**) | IPMA, Olhão, Portugal | meagre + gilthead seabream (fish only, no extractive species; labelled "MONO" in Annex 1) |

**Reasons for the study.** IMTA is promoted as a circular aquaculture design: oysters filter particles and macroalgae take up
dissolved nutrients released by the fed fish. The study tests whether this also lowers life cycle impacts.

**Methodological basis.** LCA of IMTA is difficult because the system delivers several products (functional unit, allocation)
and harmonised data are scarce (Hala, Chougule et al., 2024). These choices are made explicit below.

**Intended audience.** Project partners, researchers and practitioners in aquaculture sustainability assessment.

## 2. Scope

### 2.1 Functional unit and reference flow
- **Functional unit:** **1 tonne of aquatic product (fish + oyster flesh weight gain) at the farm gate, one production cycle.**
- **Reference flows** (per pond and cycle, Table 4): SI-IMTA 1,229 kg (1,099 fish + 130 oyster flesh), SE-IMTA 159 kg (65 + 94), SI-POLY 6,137 kg fish.
- Macroalgae are an *associated downstream production* and are **not** part of the functional unit; they carry no burden.
- Check: seawater per pond × (1,000 / reference flow) reproduces the *Water consumption* of Annex 1 within 0.2 %, which confirms this functional unit.

### 2.2 System boundary
Farm operation and the production of its inputs (Fig. 3 of the report):

| Included | Excluded |
|---|---|
| Fish fry and oyster spat (carp-fry LCA profile as proxy) | Packaging |
| Feeds: ingredient production and processing | Transport to the retailer, retail, consumption |
| Energy on the farm (electricity for pumping and aeration, gasoline) | |
| Water use, equipment, buildings, vehicles, chemicals | |
| All transport (sea and land) to the farm | |
| Direct farm activity (land and water occupation) | |
| N and P emissions from uneaten feed and excretion ("Rejects fish") | |

### 2.3 Multifunctionality and allocation
- No allocation between fish and oysters: they are summed by mass in the functional unit.
- Macroalgae: outside the functional unit (no allocation, no credit).
- Shared infrastructure, vehicles and electricity of the station are allocated to the studied pond by
  **production-pond area / total farm pond area**.

### 2.4 Life cycle inventory
- Primary data from daily farm records: water flow and renewal, aeration time, feed, mortality, treatments.
- Feed ingredients and amounts from the feed manufacturer.
- N, P and solid emissions from a nutrient balance (Cho & Kaushik, 1990): nutrients in feed minus nutrients retained in harvested biomass.
- The foreground inventory per functional unit is shared in the LCIS2024 structure in [`data/lci/`](../data/lci/) (Nair, Chougule et al., 2025).

### 2.5 Impact assessment
Software: **Piscentool** (Excel interface developed in project Piscenlit; Wilfart et al., 2012) with SimaPro background data.

| Code | Category | Unit |
|---|---|---|
| GW | Global warming (GWP100) | kg CO2-eq |
| TCED | Total cumulative energy demand | MJ-eq |
| NPPU | Net primary production use | kg C |
| AP | Acidification | kg SO2-eq |
| EP | Eutrophication | kg PO4-eq |
| LC | Land competition | m²·a |
| WD | Water dependence | m³ |

Results are reported per process (11 processes: building, energy, water, vehicle, rejects fish, chemicals, equipment, fry,
feeds, transports, direct activity). No normalisation or weighting.

### 2.6 KPI layer (added in this repository)
13 KPIs: 7 environmental (one per category; target = at least 10 % better than the polyculture) and 6 circularity KPIs
(N and P use efficiency, net N released, feed conversion ratio, share of non-fed biomass, feed share of global warming).
Targets are placeholders to be agreed with stakeholders. See [`methodology.md`](methodology.md).

### 2.7 Limitations
- Experimental ponds (665–1,700 m²) and single production cycles of different length (5.3, 8.5 and 26 months);
  short cycles raise the share of equipment and buildings.
- Fry modelled with a carp-fry proxy.
- Fish and oyster nitrogen are reported together, so their separate contributions cannot be shown.
- Impact amounts in Annex 1 are rounded to whole units, which matters for small values (semi-extensive acidification and eutrophication).
- Two inconsistencies between the report tables are documented in [`known_issues.md`](known_issues.md).
