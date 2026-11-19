# Zenodo deposit metadata — draft

**Title**

Data and code for: Evaluating an Astronomy-Inspired Colour–Colour Diagram Approach for River Turbidity Assessment: Implications for Arsenic Contamination Screening in the Kok and Sai Rivers, Thailand

**Resource type:** Dataset (includes analysis software). Alternatively use Software only if choosing the GitHub automated software archive route. Do not create two records for the same identical release.

**Creator:** Surina, Farung

**ORCID:** 0000-0002-9717-9806

**Affiliation:** Chiang Rai Rajabhat University, Thailand

**Version:** 1.0.0 (publish after final author review)

**Publication date:** Actual date of public deposit, not an assumed article publication date.

**Description**

This research compendium supports an exploratory evaluation of an astronomy-inspired optical approach to river turbidity assessment and indirect arsenic exceedance screening in northern Thailand. It contains a subset of the publicly reported water-quality data compilation (PCD monitoring rounds 1–22, March 2025–August 2026), prepared station and date audits, Sentinel-2 aperture-derived surface reflectance exports, Earth Engine and Python code, analysis tables, cross-validation predictions, bootstrap intervals, and manuscript figures. It includes 300 ground-based arsenic observations (296 paired with turbidity) and 45 exploratory Kok River satellite–ground observations in the D4/50 m scenario. No observation satisfies both strict same-day and verified-location requirements, and no usable Sai River satellite observations were obtained. The archived results do not establish reliable satellite-based arsenic screening. Contains modified Copernicus Sentinel data 2025–2026. Third-party data retain their original attribution and applicable terms; see DATA_ATTRIBUTION.md. The original OpenStreetMap geometry cache (OSM database timestamp 1 June 2026) is included under `03_code/map/`; Figure 1 was independently regenerated from this cache.

**Keywords:** astronomical photometry; optical physics; colour–colour diagram; Sentinel-2; remote sensing; turbidity; arsenic; water quality monitoring; Thailand

**Licence(s):** Choose only after author approval and source rights verification. Proposed MIT for project code; CC BY 4.0 for author-owned documentation/derived outputs; source data and map attribution as described in DATA_ATTRIBUTION.md. Zenodo supports multiple/custom rights statements.

**Related works:** Link the actual GitHub repository/release when available. Cite source compilation DOI above; add the article DOI as a supplement relationship only after it exists.

**Funding:** No external funding.

**DOI:** Reserve in a manual draft or let Zenodo mint it when archiving a GitHub release. No DOI has been created by this package.

## Ready-to-paste LaTeX (after publishing)

```latex
\dataavailability{Ground-based monitoring data were obtained from the Pollution Control Department of Thailand \cite{pcd25,pcd26} and the machine-readable compilation by Sinwisitsophon \cite{sin26}. Sentinel-2 data were accessed through Google Earth Engine \cite{goo26}. The analysis scripts, prepared datasets, archived satellite-derived reflectance tables, and results supporting this study are available at \url{GITHUB_URL} and are archived in Zenodo at \url{https://doi.org/VERSION_DOI}.}
```

Replace the placeholders with real verified links; use the numerical version DOI for the exact files used in the paper.
