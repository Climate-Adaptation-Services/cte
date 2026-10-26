"""
Sanity checks for a country's threshold CSV and clipped grid before adding it to the app.

Usage (from the preprocess folder):
    python check_country_data.py GHA ghana_clipped.geojson

Checks:
  - CSV is identical to the file on the PIK server (ignoring line endings)
  - header, scenarios/periods and thresholds (tasmax_a15..a40) are complete
  - every scenario/period/threshold has the same set of cells, no empty values
  - values are between 0 and the number of days in the month
  - days above T never increase as T increases
  - every grid cell has data in the CSV
  - warming: future >= historical, and ssp126 <= ssp370 <= ssp585 (2066-2095)
"""

import csv
import io
import json
import sys
import urllib.request

PIK_URL = "https://www.pik-potsdam.de/~laudien/threshold_tool/clim_indicators_thresholdTool_medianEnsemble_{}.csv"
CSV_PATH = "../static/data/clim_indicators_thresholdTool_medianEnsemble_{}.csv"
GRID_PATH = "../static/data/grids/{}"

HEADER = ["sceno", "period_mean", "name", "lat", "lon",
          "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
MONTHS = HEADER[5:]
DAYS = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
GROUPS = [("historical", "1981-2010")] + [(s, p) for s in ("ssp126", "ssp370", "ssp585")
                                          for p in ("2036-2065", "2066-2095")]
THRESHOLDS = range(15, 41)

code, grid_file = sys.argv[1], sys.argv[2]
errors = []


def check(ok, msg):
    print(("  OK    " if ok else "  FAIL  ") + msg)
    if not ok:
        errors.append(msg)


with open(CSV_PATH.format(code), newline="") as f:
    local = f.read()

# 1. Same as PIK
try:
    with urllib.request.urlopen(PIK_URL.format(code)) as r:
        remote = r.read().decode()
    check(remote.replace("\r", "") == local.replace("\r", ""), "CSV identical to PIK server")
except Exception as e:
    print(f"  SKIP  PIK comparison ({e})")

# 2. Structure
reader = csv.DictReader(io.StringIO(local))
check(reader.fieldnames == HEADER, "header matches KEN/ZWE format")

data = {}
for row in reader:
    vals = [row[m] for m in MONTHS]
    if "" in vals:
        errors.append(f"empty value: {row}")
        continue
    data[(row["sceno"], row["period_mean"], int(row["name"].removeprefix("tasmax_a")),
          row["lat"], row["lon"])] = [float(v) for v in vals]

groups = {(k[0], k[1]) for k in data}
thresholds = {k[2] for k in data}
cells = {(k[3], k[4]) for k in data}
check(groups == set(GROUPS), f"scenarios/periods complete ({len(groups)})")
check(thresholds == set(THRESHOLDS), f"thresholds 15-40 complete ({len(thresholds)})")
check(len(data) == len(GROUPS) * len(THRESHOLDS) * len(cells),
      f"every group has all {len(cells)} cells, no empty values")

# 3. Value ranges
check(all(0 <= v <= d for vals in data.values() for v, d in zip(vals, DAYS)),
      "values between 0 and days in month")
check(all(all(b <= a + 1e-6 for a, b in zip(vals, data[(s, p, t + 1, la, lo)]))
          for (s, p, t, la, lo), vals in data.items() if t < 40),
      "days above T never increase with T")

# 4. Grid
with open(GRID_PATH.format(grid_file)) as f:
    grid = {tuple(ft["properties"]["lat_lon"].split("_")) for ft in json.load(f)["features"]}
check(grid <= cells, f"all {len(grid)} grid cells have data ({len(cells - grid)} CSV cells outside border)")

# 5. Plausibility (35 degrees C, full year)
def year(s, p, la, lo):
    return sum(data[(s, p, 35, la, lo)])

check(all(year(s, p, la, lo) >= year("historical", "1981-2010", la, lo) - 1
          for s, p in GROUPS[1:] for la, lo in cells),
      "no cell gets cooler than historical (>35C)")
mean = {s: sum(year(s, "2066-2095", la, lo) for la, lo in cells) / len(cells)
        for s in ("ssp126", "ssp370", "ssp585")}
check(mean["ssp126"] <= mean["ssp370"] <= mean["ssp585"],
      "ssp126 <= ssp370 <= ssp585 in 2066-2095 (>35C)")

print(f"\n{code}: {'all checks passed' if not errors else f'{len(errors)} problem(s)'}")
sys.exit(1 if errors else 0)
