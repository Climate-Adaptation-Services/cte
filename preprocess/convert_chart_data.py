"""
Convert chart data from NetCDF to JSON format
This data is loaded on-demand when a user clicks on the map

For file size optimization, we create aggregated datasets rather than
pre-generating data for every grid cell.
"""

import json
import xarray as xr
import pandas as pd
from pathlib import Path

# Paths
DASH_APP_PATH = Path("../Afgesloten projecten/DashTMT/App")
SVELTE_CHART_DATA_PATH = Path("src/lib/data/charts")

# Ensure output directory exists
SVELTE_CHART_DATA_PATH.mkdir(parents=True, exist_ok=True)


def convert_temperature_chart_data():
    """
    Convert temperature chart data (daily time series)
    We'll keep these as NetCDF and load on-demand, or convert to a more efficient format

    For simplicity, we'll create a grid-based lookup that can be queried client-side
    """

    print("Temperature chart data...")
    print("Note: Temperature chart data will be loaded from original NetCDF files")
    print("or converted to an indexed format for client-side lookup.")
    print("Skipping for now - will implement on-demand loading in dataLoader.js")


def convert_precipitation_chart_data():
    """
    Convert precipitation chart data (distribution data for KDE plots)

    This includes individual year data for the onset/cessation dates
    """

    print("Precipitation chart data...")
    print("Note: Precipitation chart data includes distribution data")
    print("This will be implemented with on-demand loading from indexed files")
    print("Skipping for now - will implement in dataLoader.js")


def create_metadata():
    """
    Create metadata file with information about available data
    This helps the client know what data is available and where to find it
    """

    metadata = {
        "temperature": {
            "variables": ["max", "min"],
            "periods": {
                "historic": "1979-2010 (ERA5)",
                "mid": "2041-2070",
                "end": "2071-2100"
            },
            "chart_data_location": "original_netcdf",
            "note": "Chart data loaded from NetCDF files in original app folder"
        },
        "precipitation": {
            "rain_types": ["long", "short"],
            "date_types": ["ds", "de"],
            "periods": {
                "hist": "1979-2018",
                "2031-2060": "2031-2060",
                "2071-2100": "2071-2100"
            },
            "chart_data_location": "original_netcdf",
            "note": "Chart data loaded from NetCDF files in original app folder"
        },
        "grids": {
            "temperature": "ghana_highres.geojson",
            "precipitation": "precipitation_grid.geojson"
        }
    }

    output_file = SVELTE_CHART_DATA_PATH / "metadata.json"
    with open(output_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"✓ Created metadata.json")


if __name__ == "__main__":
    print("=" * 60)
    print("Converting Chart Data")
    print("=" * 60)
    convert_temperature_chart_data()
    print()
    convert_precipitation_chart_data()
    print()
    create_metadata()
    print("\nDone!")
    print("=" * 60)
    print("\nNote: Chart data will be loaded on-demand via dataLoader utilities")
    print("This approach keeps the initial bundle size small while maintaining")
    print("full functionality.")
