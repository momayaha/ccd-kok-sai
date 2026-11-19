# Code
Install requirements and run `python 03_code/run_analysis.py` from root. Outputs go to `reproduced/`. Numerical tables are recalculated; exact archived D4 prediction and fold CSVs are used for the original ROC and plots. Sensitivity script independently recalculates nested predictions and uses a tolerance for equivalent colour bases.
For upstream extraction, upload `02_input_and_raw_data/CCD_GEE_observations.csv` to Earth Engine as point asset using longitude/latitude, edit placeholder asset ID in `CCD_GEE_aperture_v2.js`, run in GEE Code Editor and export. GEE project/account required.
Map script is in `map/`; final OSM JSON/GeoJSON not supplied. Main runner copies archived Figure 1, regenerates Figures 2–5.
