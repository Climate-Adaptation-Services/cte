"""
Convert precipitation NetCDF data to JSON format for the Svelte app
"""

import json
import xarray as xr
import pandas as pd
import numpy as np
from pathlib import Path

# Paths
DASH_APP_PATH = Path("../Afgesloten projecten/DashTMT/App")
SVELTE_DATA_PATH = Path("src/lib/data/precipitation")

# Ensure output directory exists
SVELTE_DATA_PATH.mkdir(parents=True, exist_ok=True)

# Rain types and parameters
RAIN_TYPES = {
    'long': 'Long rains',
    'short': 'Short rains'
}

DATE_TYPES = {
    'ds': 'Start day',
    'de': 'End day'
}

PERIODS = {
    'hist': '1979-2018',
    '2031-2060': '2031-2060',
    '2071-2100': '2071-2100'
}


def convert_map_data(rain_type, date_type, period_years):
    """
    Convert precipitation map data (for choropleth maps)
    Format: {lat_lon: day_value}
    """
    root = DASH_APP_PATH / "Data/precipitation"

    if period_years == '1979-2018':
        # Historic data
        file_path = root / f'total_precipitation_1979-2018_merged_HRES_daysum_season_{rain_type}rains_Kenya.nc'
        hist = xr.open_dataset(file_path)

        df = hist.to_dataframe().reset_index()
        df['lat_lon'] = df['lat'].round(2).astype(str) + '_' + df['lon'].round(2).astype(str)
        df = df.loc[df['bnds'] == 0]  # Filter for specific bound
        df = df[['lat_lon', date_type]].dropna()

        result = {row['lat_lon']: float(row[date_type]) for _, row in df.iterrows()}

    else:
        # Future projection data (delta change)
        file_path = root / f'deltachange_{date_type}_avg_{period_years}_{rain_type}.nc'
        proj = xr.open_dataset(file_path)

        # Also load historic for alignment
        hist_file = root / f'total_precipitation_1979-2018_merged_HRES_daysum_season_{rain_type}rains_Kenya.nc'
        hist = xr.open_dataset(hist_file)

        # Reindex projection to match historic grid
        proj = proj.reindex(lat=hist['lat'].values, lon=hist['lon'].values, method='nearest')

        df_proj = proj.to_dataframe().reset_index()
        df_proj['lat_lon'] = df_proj['lat'].round(2).astype(str) + '_' + df_proj['lon'].round(2).astype(str)
        df_proj = df_proj[['lat_lon', date_type]].dropna()

        df_hist = hist.to_dataframe().reset_index()
        df_hist = df_hist.loc[df_hist['bnds'] == 0]
        df_hist['lat_lon'] = df_hist['lat'].round(2).astype(str) + '_' + df_hist['lon'].round(2).astype(str)
        df_hist = df_hist[['lat_lon', date_type]].dropna()

        # Combine historic + projection delta
        result = {}
        for lat_lon in df_hist['lat_lon'].unique():
            hist_val = df_hist[df_hist['lat_lon'] == lat_lon][date_type].values
            proj_row = df_proj[df_proj['lat_lon'] == lat_lon]

            if len(hist_val) > 0:
                if len(proj_row) > 0:
                    proj_val = proj_row[date_type].values[0]
                    result[lat_lon] = float(hist_val[0] + proj_val)
                else:
                    result[lat_lon] = float(hist_val[0])

    return result


def convert_precipitation_data():
    """Convert all precipitation datasets for maps"""

    print("Converting precipitation map data...")

    for rain_type_short, rain_type_long in RAIN_TYPES.items():
        for date_type_short, date_type_long in DATE_TYPES.items():
            for period_key, period_display in PERIODS.items():
                print(f"\nProcessing {rain_type_long}, {date_type_long}, {period_display}...")

                try:
                    result = convert_map_data(rain_type_short, date_type_short, period_key)

                    period_safe = period_key.replace('/', '-')
                    output_file = SVELTE_DATA_PATH / f"map_{rain_type_short}_{date_type_short}_{period_safe}.json"

                    with open(output_file, 'w') as f:
                        json.dump(result, f, separators=(',', ':'))

                    print(f"[OK] Created {output_file.name} ({output_file.stat().st_size / 1024:.1f} KB)")

                except FileNotFoundError as e:
                    print(f"[WARN] Warning: File not found - {e}")
                except Exception as e:
                    print(f"[ERROR] Error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Converting Precipitation Data (NetCDF → JSON)")
    print("=" * 60)
    convert_precipitation_data()
    print("\nDone!")
    print("=" * 60)
