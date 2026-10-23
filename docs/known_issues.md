# Known issues and open questions

These came out of the data checks (`results/data_checks.csv`, Excel tab *Data checks*). They do not change the
report's conclusions, but they should be clarified before the numbers are reused.

## 1. Feed conversion ratio of the semi-extensive IMTA (Table 4)
Table 4 gives an FCR of **0.56**. Feed / fish gain = 89 / 65 = **1.37**. The 0.56 equals feed / (fish + oyster gain) = 89 / 159.
The other two systems use feed / fish gain (1,888 / 1,099 = 1.72; 10,975 / 6,137 = 1.79).
**In this repository:** KPI C4 uses feed / fish gain for all three systems (1.37 for the semi-extensive IMTA).

## 2. Land competition of the polyculture (Annex 1)
For both IMTA systems, *Direct activity* in Land competition matches the report's allocation rule
(farm area × production-pond area / total pond area × cycle length): 959 vs 941 m²a/t and 4,222 vs 4,194 m²a/t.
For the polyculture the same rule over 26 months gives 2,289 m²a/t, but Annex 1 reports **460** m²a/t
(this would correspond to about 5 months, or to a one-year basis with a different area). To clarify with the authors.
**In this repository:** the Annex 1 value is used unchanged.

## 3. Table 5 caption
The caption says "calculated for 1 tonne of fish and oyster produced per cycle", but the values are **per pond and cycle**:
N in feed = feed of the pond × 42 % / 6.25 (1,888 × 0.0672 = 126.9 kg). The last row ("by weight of produced fish") is per kg
of fish + oyster. **In this repository:** Table 5 is read per pond and scaled to the functional unit.

## 4. Text vs Annex 1
- Section 4.3 quotes 10,423 kg C for the semi-intensive IMTA; that is the *Feeds* contribution. The total is 10,478 kg C.
- Section 4.5 quotes 3 kg PO4-eq for the semi-extensive IMTA; Annex 1 gives a total of 2 kg PO4-eq.
**In this repository:** Annex 1 totals are used.

## 5. Rounding and missing shares
Annex 1 amounts are rounded to whole units, so small values lose precision (semi-extensive acidification 6 kg SO2-eq,
eutrophication 2 kg PO4-eq). Three shares are printed as `###` (overflow) and are left empty in `lcia_annex1.csv`.
Process sums match the totals within ±2 units.

## 6. Macroalgae nitrogen
Implied N content of the harvested macroalgae: 30.6 / 1,224 = 2.5 % (semi-intensive) vs 1.8 / 35,400 = 0.005 % (semi-extensive).
The basis (fresh vs dry weight, harvested vs grown) is probably different. Worth checking against the raw data.

## 7. Scope differences between the systems
Cycle lengths differ (5.3, 8.5, 26 months) and the ponds are experimental. Short cycles raise the share of equipment
and buildings (section 5 of the report). Comparisons are per functional unit, not per year.
