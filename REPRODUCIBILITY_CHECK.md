# Reproducibility check

Tested 19 November 2026 with Python 3.13.5 and pinned numerical dependencies. The runner completed. All 25 corresponding result CSVs have matching dimensions and numerical columns (rtol=1e-8, atol=1e-10). Four D4 original CSVs were copied to preserve original fold labels; their numerical predictions were separately verified by refitting archived per-fold predictors. This is not a byte-for-byte comparison or complete upstream re-extraction. The GEE online process was not rerun. Subsequently, the original OSM cache was received and the map script rerun using that cache without a new network fetch.

| CSV | Rows | Check |
|---|---:|---|
| CCD_aperture_D4_SigmaPlot.csv | 99 | PASS |
| CCD_aperture_D4_correlations.csv | 30 | PASS |
| CCD_aperture_D4_fixed_models.csv | 78 | PASS |
| CCD_aperture_D4_nested_models.csv | 15 | PASS |
| CCD_aperture_audit_all.csv | 3312 | PASS |
| CCD_aperture_best_per_radius.csv | 135 | PASS |
| CCD_auc_cluster_bootstrap.csv | 33 | PASS |
| CCD_sensitivity_RMSE.csv | 120 | PASS |
| CCD_sensitivity_SigmaPlot.csv | 24 | PASS |
| CCD_sensitivity_coverage.csv | 12 | PASS |
| CCD_sensitivity_predictions.csv | 2900 | PASS |
| D4_50m_RMSE.csv | 5 | PASS |
| D4_50m_SigmaPlot.csv | 45 | PASS |
| D4_50m_fold_choices.csv | 45 | PASS |
| D4_50m_predictions.csv | 45 | PASS |
| D4_arsenic_proxy_ROC_coordinates.csv | 227 | PASS |
| D4_arsenic_proxy_auc.csv | 5 | PASS |
| D4_arsenic_proxy_predictions.csv | 45 | PASS |
| ground_ROC_coordinates.csv | 1521 | PASS |
| ground_all_300.csv | 300 | PASS |
| ground_auc.csv | 13 | PASS |
| ground_grouped_predictions.csv | 1064 | PASS |
| ground_paired_296.csv | 296 | PASS |
| ground_stratified_auc.csv | 98 | PASS |
| ground_summary.csv | 6 | PASS |

All five model-family archived D4 predictions independently matched upon refitting. Figures 2–5 regenerated successfully; the main runner copies Figure 1. The separate map script regenerated Figure 1 from the supplied OSM cache. For the corrected Figure 1, the Ruak group was added before Mekong in the name-matching rules, and the four river labels were placed manually. The revised GeoJSON contains 304 distinct way IDs: all 297 previous ways are retained with unchanged coordinate sequences, five previous Mekong ways and one previous other way are now Ruak, and seven additional Ruak-relation ways are included. The corrected map script was rerun from the supplied raw cache. Its PNG was pixel-identical to the corrected manuscript image at 600 dpi (5465 × 4266 pixels), and the PDF render was pixel-identical at 100 dpi. This is a reproduction check, not a complete geographic validation: automated name matching may still include similarly named tributaries or old river channels. Reference station coordinates and numerical analysis outputs were not changed.
