# Known issues and limitations

This repository is shared openly, including what is not yet right.

## Open issues in the ecoinvent / openLCA runs

| # | Issue | Effect | Status |
|---|---|---|---|
| 1 | **Electricity provider**: auto-linking selected a lignite-dominated mix (Kosovo/Serbia) instead of `market for electricity, low voltage \| PT` | Electricity ≈ 66 % of climate change in run 3; result (4.95 kg CO2-eq/kg) far above literature (2.27) | Open – provider must be set to PT and the product system recreated with "only default providers" |
| 2 | **Nitrogen not characterised**: the farm's N emission (to ocean or surface water) has no factor in openLCA's "EF 3.1 Method (adapted)" for marine eutrophication | Marine eutrophication strongly underestimated; the farm (the expected hotspot) does not appear | Open – check which N flows carry a factor (e.g. nitrate, ammonium) and convert |
| 3 | Other auto-linked providers (e.g. Swiss rapeseed oil, small refrigerated lorry in run 1) | Minor | Open – set explicitly for a final study |
| 4 | Run 2 used allocation "none" | All burden on fish | Superseded by run 3; kept for transparency |

## Limitations of the model
- Activity data are assumptions (no measured farm data); FCR 1.5 is optimistic versus literature (1.7–2.0).
- Fish juveniles, feed milling, infrastructure excluded; including juveniles would raise the footprint.
- Nutrient recovery is an upper estimate: mussels also feed on natural plankton, biodeposits are not modelled;
  open-water IMTA in the literature recovers about 7 % of fed N.
- Illustrative factors (`data/factors_illustrative.csv`) exclude land use change; ecoinvent shows it is significant for soy.
- EF does not capture IMTA ecosystem services (water quality) or biodiversity effects.

## Next steps
1. Fix issues 1 and 2, re-run, update `data/openlca_results/`.
2. Replace illustrative factors with per-unit openLCA results.
3. Sensitivity analysis: FCR, soy origin, allocation method, electricity mix.
4. Add uncertainty (pedigree matrix → Monte Carlo).
