# OpenStreetMap river geometry

© OpenStreetMap contributors. The two files `osm_waterways_raw.json` and `osm_waterways.geojson` contain OpenStreetMap data and are available under the Open Data Commons Open Database License (ODbL) 1.0: https://opendatacommons.org/licenses/odbl/1-0/. Attribution: https://www.openstreetmap.org/copyright.

The raw file is the original Overpass API response supplied by the author, with OSM database timestamp 2026-06-01T08:52:28Z. The GeoJSON was derived from that response by the map script, retaining way IDs and coordinate sequences and adding river-group classifications. These two files retain ODbL terms and are excluded from any MIT or CC BY licence applied to project-authored material.

To reproduce the archived map using the original cache, run `python make_figure1.py` in this directory. Do not use `--offline`, which intentionally generates a preview without river geometry. The revised map script separates Ruak from Mekong, and the revised GeoJSON contains 304 ways. The raw cache is unchanged. Successful regeneration is not a complete geographic validation; similar names and relation membership may include additional waterways.
