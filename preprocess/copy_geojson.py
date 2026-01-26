"""
Copy GeoJSON grid files from the original Dash app to the Svelte app data folder
"""

import shutil
from pathlib import Path

# Paths
DASH_APP_PATH = Path("../Afgesloten projecten/tmt-climate-atlas")
SVELTE_DATA_PATH = Path("src/lib/data/grids")

# GeoJSON files to copy
GEOJSON_FILES = [
    "Data/kenia.geojson",
    "Data/temperature_grid.geojson",
    "Data/precipitation_grid.geojson"
]

def copy_geojson_files():
    """Copy GeoJSON grid files"""

    # Ensure destination directory exists
    SVELTE_DATA_PATH.mkdir(parents=True, exist_ok=True)

    for geojson_file in GEOJSON_FILES:
        source = DASH_APP_PATH / geojson_file
        dest = SVELTE_DATA_PATH / Path(geojson_file).name

        if source.exists():
            print(f"Copying {source} to {dest}")
            shutil.copy(source, dest)
            print(f"[OK] Copied {dest.name}")
        else:
            print(f"[WARN] Warning: {source} not found")

if __name__ == "__main__":
    print("Copying GeoJSON grid files...")
    copy_geojson_files()
    print("Done!")
