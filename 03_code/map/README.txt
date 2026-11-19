FIGURE 1 — Kok and Sai Rivers monitoring stations

1. Install Python 3.11 or 3.12 on Windows, then open Command Prompt in this folder.
   py -m pip install -r requirements.txt
2. Run with the supplied raw JSON cache (no network fetch needed). If the cache is absent, Internet access is required:
   py make_figure1.py
3. If downloaded named Kok and Sai river geometry is present, the script writes:
   fig1-study-area.pdf (vector PDF)
   fig1-study-area.png (600 dpi)
   osm_waterways_raw.json (cached raw Overpass response)
   osm_waterways.geojson (extracted lines with OSM way IDs)
4. Check that river names and continuity agree with GIS and that labels are readable.
   The script does not snap station positions to rivers or connect stations with artificial lines.
   Name matching uses OSM tags and waterway relation membership; incomplete or incorrect tags
   may require manual review. Borders are generalized WDBII/GMT linework, not survey-grade boundaries.
5. If Internet access fails or both named rivers are not found, the script outputs a PREVIEW only.
   Do not use the preview as the final river map. For an offline preview:
   py make_figure1.py --offline

Sources:
* PCD: reference station coordinate campaign 22–26 September 2025; supplied CSV.
* River lines: OpenStreetMap contributors, ODbL, https://www.openstreetmap.org/copyright
* Boundaries: WDBII / GMT, through Basemap; generalized cartographic dataset.
* Coastlines for the inset: GSHHG through Basemap.

Keep the OSM JSON with the reproducibility archive if the final figure is made.
The original cache was supplied by the author and the complete map was regenerated without a new download. The corrected map separates Ruak from Mekong and uses manually positioned labels. The regenerated PNG and PDF matched the corrected manuscript figure at 600 dpi and 100 dpi, respectively. The regenerated GeoJSON contains 304 way IDs. The --offline flag is for a preview without rivers, not for cached map regeneration. See OSM_ATTRIBUTION.md and REPRODUCIBILITY_CHECK.md.
