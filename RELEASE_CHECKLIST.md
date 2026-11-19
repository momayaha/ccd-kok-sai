# Release checklist

1. Private GitHub repository created and GIS update committed, as reported by the author: https://github.com/momayaha/ccd-kok-sai. Apply the RC4 Figure 1 update and verify all changed file paths before release.
2. Original OSM JSON cache supplied by the author; updated GeoJSON regenerated in `03_code/map/`. Ruak/Mekong correction and reproduction of the revised Figure 1 tested. The author has reported updating the manuscript. Other automatic name matches and generalized boundaries remain cartographic limitations.
3. The author confirmed that the original Zenodo record lists CC BY 4.0. Verify underlying PCD redistribution rights for both unmodified and derived data. If verification fails, omit restricted files and provide permitted links/retrieval instructions, updating the runner/manifest accordingly.
4. Confirm institutional/author rights and choose scoped licences; proposed MIT code + CC BY 4.0 author-controlled documentation/outputs, preserving all source terms.
5. Verify the PCD September campaign draft reference (`pcd25`) already added to `references.bib`; review all manuscript references. No manuscript PDF is included in this deposit.
6. Run the analysis and verification commands; inspect the outputs. Update manifest after any change.
7. Publish a GitHub release tagged `v1.0.0` once ready. For a manual Zenodo Dataset deposit, upload a ZIP from this exact release; use `ZENODO_METADATA.md`. Choose multiple licences/rights statements if appropriate. Use the existing manual Zenodo draft with reserved DOI 10.5281/zenodo.24372650. Do NOT enable automatic GitHub-to-Zenodo archiving for this identical release. Review metadata and rights before public access.
8. After rights and map review, publish the existing Zenodo draft and verify https://doi.org/10.5281/zenodo.24372650 resolves; confirm the public GitHub link and then update manuscript Data Availability.
