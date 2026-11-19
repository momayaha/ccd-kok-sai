# Astronomy-inspired colour–colour diagrams for river turbidity assessment

**Research compendium | v1.0.0 release candidate | 19 November 2026**

**GitHub:** https://github.com/momayaha/ccd-kok-sai (private during preparation).

**Reserved Zenodo version DOI:** 10.5281/zenodo.24372650 — https://doi.org/10.5281/zenodo.24372650 (draft; not yet registered or publicly accessible).

**Author:** Farung Surina — Faculty of Science and Technology, Chiang Rai Rajabhat University, Chiang Rai, Thailand. ORCID: https://orcid.org/0000-0002-9717-9806

**Associated manuscript (in preparation):** Evaluating an Astronomy-Inspired Colour–Colour Diagram Approach for River Turbidity Assessment: Implications for Arsenic Contamination Screening in the Kok and Sai Rivers, Thailand

## Overview

This research compendium supports an exploratory evaluation of an astronomy-inspired optical approach to river turbidity assessment and indirect arsenic exceedance screening in northern Thailand. It contains a subset of the publicly reported water-quality data compilation (PCD monitoring rounds 1–22, March 2025–August 2026), prepared station and date audits, Sentinel-2 aperture-derived surface reflectance exports, Earth Engine and Python code, analysis tables, cross-validation predictions, bootstrap intervals, and manuscript figures. It includes 300 ground-based arsenic observations (296 paired with turbidity) and 45 exploratory Kok River satellite–ground observations in the D4/50 m scenario. No observation satisfies both strict same-day and verified-location requirements, and no usable Sai River satellite observations were obtained. The archived results do not establish reliable satellite-based arsenic screening. Contains modified Copernicus Sentinel data 2025–2026. Third-party data retain their original attribution and applicable terms; see DATA_ATTRIBUTION.md. The original OpenStreetMap geometry cache (OSM database timestamp 1 June 2026) is included under `03_code/map/`; The corrected Figure 1 (separate Ruak and Mekong groups and labels) was independently regenerated from this cache.

## Directory structure

| Location | Contents |
|---|---|
| `01_source_data/` | Unmodified third-party CSV subset, original README and attribution |
| `02_input_and_raw_data/` | Prepared master table, station reference, date audit, GEE input, archived aperture extraction |
| `03_code/` | Earth Engine extraction, Python analysis, bootstrap, sensitivity, figure generation and map script |
| `04_results/` | Archived results, predictions, fold choices, coverage, ROC coordinates and uncertainty summaries |
| `05_figures/` | Figures 1–5 in PDF and PNG |
| `CITATION.cff` | Citation metadata for GitHub |
| `ZENODO_METADATA.md` | Ready-to-paste deposit metadata and version information |
| `DATA_ATTRIBUTION.md` | Provenance and rights by data source |
| `MANIFEST.csv` | File sizes and SHA-256 checksums (excludes itself) |
| `REPRODUCIBILITY_CHECK.md` | Tested result comparison and scope |

## Scientific scope

- PCD rounds 1–22 only; 17 reference stations, 14 Kok and 3 Sai; 300 arsenic observations, 296 paired with turbidity.
- B2/B3/B4/B8 at native 10 m; six pseudo-colour indices, 15 candidate CCD pairs; 20/30/50 m radius; at least three common positive water pixels (SCL class 6).
- D0, D2, D3 and D4 denote the maximum possible date mismatch, not an assertion of unchanged river conditions. The primary strict same-day/location criterion has zero verified matches.
- D4/50 m exploratory sample: 45 observations, 9 Kok stations, 14 rounds; 10 arsenic exceedances. No usable Sai River satellite matches.
- Nested LOSO CCD RMSE = 0.270827 on log10(NTU); four-band RMSE = 0.307348; training-mean RMSE = 0.337384. The CCD advantage was not consistently maintained in LORO. Measured-turbidity Kok AUC = 0.735043; CCD-estimated-turbidity AUC = 0.494286 in the D4 subset. No operational risk map or drinking-water safety classification is supported.

## Reproduce locally

Tested in Python 3.13.5. From the repository root (Windows Command Prompt):

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r 03_code/requirements.txt
python 03_code/run_analysis.py
python 03_code/verify_archived_predictions.py
```

On Linux/macOS, use `python3 -m venv .venv` and `source .venv/bin/activate`. Run the same Python commands thereafter. The runner writes new outputs under `reproduced/`, preserving the archived data. Tables can be generated with `--skip-figures`. It recalculates the aperture analysis, ground analyses, sensitivity, bootstrap intervals, and Figures 2–5. The archived D4 predictions and fold labels are used for the original ROC/figure workflow; the companion verification script independently refits each archived choice and checks predictions. Equivalent CCD bases may tie at floating-point precision. Figure 1 is copied from its archived PDF by the main runner; its independent map-generation script uses the supplied cache. To regenerate the map without fetching new OSM data, install `03_code/map/requirements.txt` and run `python 03_code/map/make_figure1.py` (do not use `--offline`, which creates a preview without rivers).

The upstream GEE export is already provided, so no GEE account is needed for local analyses. To regenerate the extraction, see `03_code/README.md`. The exact raw OSM geometry cache is supplied; the full automated upstream master/coordinate preparation workflow is not supplied. The figures and tables are not a validated arsenic detection product.

## Cite and reuse

After publication, cite Farung Surina (2026), version 1.0.0, https://doi.org/10.5281/zenodo.24372650, and the underlying data sources as indicated in `DATA_ATTRIBUTION.md`. The DOI identifies the research compendium, not the journal article. The journal article is in preparation and no article DOI is asserted here. Licence choices must be confirmed by the author before public release; no blanket licence is granted over third-party material. See `RELEASE_CHECKLIST.md`.
