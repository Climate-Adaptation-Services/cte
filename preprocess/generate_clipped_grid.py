"""
Generate a clipped country grid GeoJSON from the climate CSV and the country boundary.

Each grid cell is a 0.5° square centered on the lat/lon from the CSV,
clipped to the country boundary polygon. The `lat_lon` property matches
the CSV format exactly (e.g. "-4.25_33.75").

Usage (defaults to Kenya):
    python generate_clipped_grid.py [CSV_PATH BOUNDARY_PATH OUTPUT_PATH]

Ghana boundary: geoBoundaries gbOpen GHA ADM0
(https://www.geoboundaries.org/api/current/gbOpen/GHA/ADM0/)
"""

import csv
import json
import sys
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union

CSV_PATH = "../static/data/clim_indicators_thresholdTool_medianEnsemble_KEN.csv"
BOUNDARY_PATH = "../static/data/grids/kenya.json"
OUTPUT_PATH = "../static/data/grids/kenia_clipped.geojson"

if len(sys.argv) == 4:
    CSV_PATH, BOUNDARY_PATH, OUTPUT_PATH = sys.argv[1:]

CELL_SIZE = 0.5  # degrees

# 1. Read unique lat/lon from CSV
coords = set()
with open(CSV_PATH) as f:
    for row in csv.DictReader(f):
        coords.add((float(row["lat"]), float(row["lon"])))

print(f"Unique CSV coordinates: {len(coords)}")

# 2. Load Kenya boundary
with open(BOUNDARY_PATH) as f:
    boundary_geojson = json.load(f)

# Combine all features into one shape
boundary_shapes = [shape(feat["geometry"]) for feat in boundary_geojson["features"]]
kenya = unary_union(boundary_shapes)

print(f"Kenya boundary loaded: {kenya.geom_type}")

# 3. Generate clipped grid cells
features = []
half = CELL_SIZE / 2

for lat, lon in sorted(coords):
    # Create 0.5° square centered on (lat, lon)
    cell = box(lon - half, lat - half, lon + half, lat + half)

    # Clip with Kenya boundary
    clipped = cell.intersection(kenya)

    if clipped.is_empty:
        print(f"  WARNING: cell {lat}_{lon} has no overlap with Kenya boundary")
        continue

    feature = {
        "type": "Feature",
        "properties": {
            "lat_lon": f"{lat}_{lon}"
        },
        "geometry": mapping(clipped)
    }
    features.append(feature)

geojson = {
    "type": "FeatureCollection",
    "features": features
}

with open(OUTPUT_PATH, "w") as f:
    json.dump(geojson, f)

print(f"\nOutput: {len(features)} clipped grid cells written to {OUTPUT_PATH}")
print(f"Skipped: {len(coords) - len(features)} cells (no overlap)")
