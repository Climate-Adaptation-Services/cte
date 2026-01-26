"""
Convert temperature NetCDF data to JSON format for the Svelte app
Generates base files with all thresholds and months, which can be filtered client-side
"""

import json
import xarray as xr
import pandas as pd
from pathlib import Path

# Paths
DASH_APP_PATH = Path("../Afgesloten projecten/DashTMT/App")
SVELTE_DATA_PATH = Path("src/lib/data/temperature")

# Ensure output directory exists
SVELTE_DATA_PATH.mkdir(parents=True, exist_ok=True)

# Variables and scenarios
VARIABLES = {
    'max': 'Maximum temperature',
    'min': 'Minimum temperature'
}

PERIODS = {
    'mid': '2041-2070',
    'end': '2071-2100'
}

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


def convert_dataset_to_json(dataset, output_file):
    """
    Convert xarray dataset to JSON format
    Format: {lat_lon: {threshold: {month: days}}}
    """
    df = dataset.to_dataframe()
    df = df.reset_index()

    # Create lat_lon identifier
    df['lat_lon'] = df['lat'].round(2).astype(str) + '_' + df['lon'].round(2).astype(str)

    # Reorganize data structure
    result = {}

    for _, row in df.iterrows():
        lat_lon = row['lat_lon']
        threshold = int(row['threshold'])
        month = row['month']
        value = float(row['tas']) if pd.notna(row['tas']) else None

        if lat_lon not in result:
            result[lat_lon] = {}
        if threshold not in result[lat_lon]:
            result[lat_lon][threshold] = {}

        result[lat_lon][threshold][month] = value

    # Write to JSON
    print(f"Writing {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(result, f, separators=(',', ':'))  # Compact format

    print(f"[OK] Created {output_file.name} ({output_file.stat().st_size / 1024:.1f} KB)")


def convert_temperature_data():
    """Convert all temperature datasets"""

    print("Converting temperature data...")

    # Process historic data (ERA5)
    for var_short, var_long in VARIABLES.items():
        print(f"\nProcessing historic {var_long}...")
        dataset_path = DASH_APP_PATH / f"Data/preprocessed/era5_T{var_short}_numberofdays_permonth_perthreshold.nc"

        if dataset_path.exists():
            dataset = xr.open_dataset(dataset_path)
            output_file = SVELTE_DATA_PATH / f"historic_{var_short}.json"
            convert_dataset_to_json(dataset, output_file)
        else:
            print(f"[WARN] Warning: {dataset_path} not found")

    # Process projection data (CMIP5 mid and end century)
    for period_short, period_long in PERIODS.items():
        for var_short, var_long in VARIABLES.items():
            print(f"\nProcessing {period_long} {var_long}...")
            dataset_path = DASH_APP_PATH / f"Data/preprocessed/cmip5_{period_short}_T{var_short}_numberofdays_permonth_perthreshold.nc"

            if dataset_path.exists():
                dataset = xr.open_dataset(dataset_path)
                output_file = SVELTE_DATA_PATH / f"{period_short}_{var_short}.json"
                convert_dataset_to_json(dataset, output_file)
            else:
                print(f"[WARN] Warning: {dataset_path} not found")


if __name__ == "__main__":
    print("=" * 60)
    print("Converting Temperature Data (NetCDF → JSON)")
    print("=" * 60)
    convert_temperature_data()
    print("\nDone!")
    print("=" * 60)
