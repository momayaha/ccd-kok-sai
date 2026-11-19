# Arsenic, lead, manganese and turbidity in the Kok, Sai, Ruak and Mekong rivers, northern Thailand: station-level monitoring data, rounds 1–22 (March 2025 – August 2026)

Compiled by Jetnipit Sinwisitsophon, Department of Chemical Engineering, Faculty of Engineering, Mahidol University. Version 1.0, October 2026.

## What this is

A machine-readable compilation of surface-water and sediment monitoring results published by Thailand's Pollution Control Department (PCD, กรมควบคุมมลพิษ) for the Kok River, four Thai tributaries, the Sai and Ruak rivers, and the Mekong in Chiang Mai and Chiang Rai provinces. PCD began this monitoring in March 2025 after abnormal turbidity and arsenic were reported in rivers flowing from Myanmar's Shan State.

PCD publishes these results as PDF reports. This dataset converts the tables to CSV, one file per parameter, without changing any value.

## Source

- Surface water, rounds 1–22: PCD Environment and Pollution Control Office 1 (Chiang Mai), "Surface water quality of the Kok River, Kok tributaries, Sai, Ruak and Mekong rivers, round 22 (sampling 3–7 August 2026)", data as of 27 August 2026, posted 20 September 2026. Cumulative appendix tables, pages 21–24. https://epo01.pcd.go.th/th/information/list/2682
- Sediment, rounds 1–7: PCD, "Situation of environmental quality in the Kok River and tributaries, Sai, Ruak and Mekong rivers", data as of 15 October 2025. https://www.pcd.go.th/wp-content/uploads/2025/10/pcdnew-2025-10-30_09-47-27_653322.pdf

All measurements were made by PCD. The compiler collected no samples. Please cite PCD as the data originator when using these data.

## Files

| File | Content | Unit |
| --- | --- | --- |
| arsenic_water_mgL_r01-r22.csv | Total arsenic in surface water | mg/L |
| lead_water_mgL_r01-r22.csv | Lead in surface water | mg/L |
| manganese_water_mgL_r01-r22.csv | Manganese in surface water | mg/L |
| turbidity_NTU_r01-r22.csv | Turbidity | NTU |
| arsenic_sediment_mgkg_r01-r07.csv | Arsenic in river sediment, dry weight | mg/kg |
| stations.csv | Station code, river, group, location (Thai, as given by PCD), province | – |
| sampling_rounds.csv | Sampling dates of each surface-water round | – |
| news_vs_pcd_check.csv | 41 station values reported in Thai news compared with PCD's tables | mg/L |
| Kok_Arsenic_Dashboard.html | Interactive dashboard (Thai) built from these files; one self-contained file, opens offline in any modern browser | – |
| Kok_Arsenic_Dashboard_source_v1.0.zip | Source code of the dashboard (React + Vite) | – |

Each data file has one row per station and one column per round (r1 … r22).

## How values are recorded

- Values are copied exactly as printed by PCD, including the number of decimal places.
- `<0.010` (or `<0.10`, `<0.100`, `<5.0`) means below PCD's reporting limit. These are kept as text, not replaced by numbers.
- An empty cell means the station was not sampled in that round (printed as "–" by PCD) or the cell was blank in the source. Turbidity at KK07 in round 22 is blank in the source although arsenic was reported.
- Stations KK03, KK04, KK06, KK08, KK13, KK14 and SU01 stop after round 12 or 15; NK04 starts in round 18 and NK09 has two rounds. This reflects PCD's sampling plan, not missing data in this compilation.
- From October 2025 PCD reduced sampling from twice to once a month.

## Interactive dashboard

`Kok_Arsenic_Dashboard.html` presents the same data as an interactive, Thai-language explainer: a schematic station map that plays through all 22 rounds, time series, sediment and turbidity charts, a cause-and-mechanism walkthrough, and the reference list. Download it and open it in a browser; no installation or internet connection is needed. Add `?skip` to the address to go straight past the intro.

The dashboard is an analysis layer on top of the data files, not part of the data. For its statistics it substitutes half the reporting limit for censored values (for example `<0.010` → 0.005 mg/L); the CSV files keep the censored text unchanged. The station map is a schematic, not to scale.

To rebuild from source: unzip `Kok_Arsenic_Dashboard_source_v1.0.zip`, then run `npm ci` and `npm run build:single` (Node 18 or later). The pre-computed data file `src/data/kok.json` is included, so the build does not need the analysis scripts.

## Standards (from the PCD reports)

| Parameter | Thai surface-water standard |
| --- | --- |
| Arsenic | ≤ 0.01 mg/L |
| Lead | ≤ 0.05 mg/L |
| Manganese | ≤ 1.0 mg/L |
| Arsenic in sediment | 10 mg/kg (protects benthic organisms); 33 mg/kg (food-chain risk level) |

## Sediment round dates (2025)

r1: 19–24 Mar and 9 Apr · r2: 21–24 Apr and 29 Apr–2 May · r3: 26–30 May · r4: 23–27 Jun · r5: 21–25 Jul · r6: 18–22 Aug · r7: 22–26 Sep.

## Quality control

- The text layer of the PCD PDF was extracted and parsed; every row was checked to contain exactly 22 values.
- Arsenic values for rounds 1–10 were compared with an independent transcription from a separate PCD report (data as of 12 September 2025): 270 of 270 values agree.
- Where the PDF text layer split a number (for example "20 4" for 204), the value was rejoined and checked against the same value printed in the report's main text tables.

## Known issues in public reporting

`news_vs_pcd_check.csv` compares 41 station-specific arsenic values published in five Thai news reports with PCD's own tables. Five differ, including a tenfold error at the PWA raw-water intake (RU01, round 22: reported as 0.17 mg/L; PCD table 0.017 mg/L).

## Licence

This compilation is released under CC BY 4.0. The dashboard source code is released under the MIT licence; the bundled fonts (IBM Plex, Noto Serif Thai) are under the SIL Open Font License. The underlying measurements are PCD's; credit PCD as the data originator and this dataset as the compilation.
