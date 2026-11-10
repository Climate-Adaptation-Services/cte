# How many hot days can we expect?

An interactive web tool that shows how often the daily maximum temperature exceeds a chosen threshold, now and in the future, for **Kenya**, **Zimbabwe** and **Ghana**.

Pick a temperature threshold (15–40 °C), a range of months, a future period and an emissions scenario. The tool then shows:

- two maps side by side: the historical period (1981–2010) and the selected future period;
- a chart per month for a location you click on the map, comparing the historical period with a low and a high emissions scenario.

Presets for crops and livestock (for example maize, coffee, poultry and cattle) set a relevant threshold with one click. The current view can be shared as a link.

The tool was developed by [Climate Adaptation Services](https://climateadaptationservices.com/en/) together with the [Potsdam Institute for Climate Impact Research (PIK)](https://www.pik-potsdam.de/en) as part of the [SAFE4ALL Africa](https://safe4allafrica.eu/) project.

## Data

The climate data are based on bias-adjusted and statistically downscaled CMIP6 climate models from [ISIMIP3b](https://www.isimip.org/), at a spatial resolution of 0.5°. Values are the ensemble median of the average number of days per month above each threshold, for:

| | |
|---|---|
| Periods | 1981–2010 (historical), 2036–2065 ("around 2050"), 2066–2095 ("around 2080") |
| Scenarios | SSP1-2.6 (low emissions), SSP5-8.5 (high emissions) |
| Thresholds | 15 to 40 °C, in steps of 1 °C |

The method, limitations and references are described in the tool itself under *About this tool & data*.

Files in this repository:

- `static/data/clim_indicators_thresholdTool_medianEnsemble_<ISO>.csv` – one file per country, provided by PIK.
- `static/data/grids/<country>_clipped.geojson` – the 0.5° grid cells, clipped to the country border.

## Development

The tool is built with [SvelteKit](https://svelte.dev/docs/kit), [Leaflet](https://leafletjs.com/) and [D3](https://d3js.org/). You need [Node.js](https://nodejs.org/).

```sh
npm install
npm run dev       # start a development server
npm run check     # type checks
npm run build     # production build
npm run preview   # preview the production build
```

The project is configured for deployment on [Vercel](https://vercel.com/) (`@sveltejs/adapter-vercel`).

### Project structure

```
src/routes/+page.svelte           page layout and "about" text
src/lib/components/               UserInput, Map and Chart
src/lib/services/climateData.ts   loads and indexes the CSV data
src/lib/stores/appState.svelte.ts app state, country settings and URL parameters
static/data/                      climate data and grids
preprocess/                       Python scripts to prepare data for a new country
```

### URL parameters

A view is fully described by its URL, for example
`?country=ghana&t1=35&years=2036-2065&scenario=ssp585&months=1-12&lat=7.25&lon=-1.25`.

## Adding a country

1. Put the CSV from PIK in `static/data/`.
2. Create the clipped grid from the CSV and a GeoJSON file of the country border (requires `shapely`):

   ```sh
   cd preprocess
   python generate_clipped_grid.py CSV_PATH BOUNDARY_PATH OUTPUT_PATH
   ```

3. Check the data and the grid:

   ```sh
   python check_country_data.py GHA ghana_clipped.geojson
   ```

4. Add the country to `COUNTRY_CONFIG` in `src/lib/stores/appState.svelte.ts`.

## License

© Climate Adaptation Services. The code in this repository is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International license](LICENSE) (CC BY-NC 4.0): you may reuse and adapt it for non-commercial purposes, as long as you give appropriate credit.

This license does not cover the logos in `static/logos/`, which remain the property of their respective owners, or the climate data in `static/data/`, which were provided by PIK and are based on ISIMIP3b.
