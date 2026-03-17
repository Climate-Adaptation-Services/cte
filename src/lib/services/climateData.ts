/**
 * Climate data service - loads and provides access to climate indicator data
 * Data source: clim_indicators_thresholdTool_medianEnsemble_KEN.csv
 *
 * Uses a nested index for O(1) grid lookups instead of linear scans.
 */
import * as d3 from 'd3';

export interface MonthlyData {
	jan: number;
	feb: number;
	mar: number;
	apr: number;
	may: number;
	jun: number;
	jul: number;
	aug: number;
	sep: number;
	oct: number;
	nov: number;
	dec: number;
}

export const MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'] as const;

export type Scenario = 'historical' | 'ssp126' | 'ssp370' | 'ssp585';
export type Period = '1981-2010' | '2036-2065' | '2066-2095';
export type FuturePeriod = '2036-2065' | '2066-2095';

export const MIN_THRESHOLD = 15;
export const MAX_THRESHOLD = 40;

// Nested index: groupKey → Map<"lat_lon", MonthlyData>
// groupKey = "scenario|period|indicator"
type GridMap = Map<string, MonthlyData>;
type DataIndex = Map<string, GridMap>;

// Flat index for single-cell lookups: "scenario|period|indicator|lat|lon" → MonthlyData
type FlatMap = Map<string, MonthlyData>;

let dataIndex: DataIndex | null = null;
let flatMap: FlatMap | null = null;
let loadingPromise: Promise<void> | null = null;

/**
 * Snap a coordinate to the nearest 0.5° grid center (X.25 or X.75)
 */
export function snapToGrid(value: number): number {
	return Math.round((value - 0.25) / 0.5) * 0.5 + 0.25;
}

/**
 * Load and parse the climate CSV data.
 */
export async function loadClimateData(): Promise<void> {
	if (dataIndex) return;
	if (loadingPromise) return loadingPromise;

	loadingPromise = fetch('/data/clim_indicators_thresholdTool_medianEnsemble_KEN.csv')
		.then((res) => res.text())
		.then((text) => {
			const rows = d3.csvParse(text);
			const index: DataIndex = new Map();
			const flat: FlatMap = new Map();

			for (const row of rows) {
				const scenario = row.sceno;
				const period = row.period_mean;
				const indicator = row.name;
				const lat = +row.lat;
				const lon = +row.lon;

				const monthly: MonthlyData = {
					jan: +row.jan, feb: +row.feb, mar: +row.mar, apr: +row.apr,
					may: +row.may, jun: +row.jun, jul: +row.jul, aug: +row.aug,
					sep: +row.sep, oct: +row.oct, nov: +row.nov, dec: +row.dec
				};

				// Nested index for grid lookups
				const groupKey = `${scenario}|${period}|${indicator}`;
				let grid = index.get(groupKey);
				if (!grid) {
					grid = new Map();
					index.set(groupKey, grid);
				}
				grid.set(`${lat}_${lon}`, monthly);

				// Flat index for single-cell lookups
				flat.set(`${groupKey}|${lat}|${lon}`, monthly);
			}

			dataIndex = index;
			flatMap = flat;
		});

	return loadingPromise;
}

export function isDataLoaded(): boolean {
	return dataIndex !== null;
}

/**
 * Get monthly data for a specific location. O(1) lookup.
 */
export function getLocationData(
	scenario: Scenario,
	period: Period,
	threshold: number,
	lat: number,
	lon: number
): MonthlyData | null {
	if (!flatMap) return null;
	const indicator = `tasmax_a${threshold}`;
	const snappedLat = snapToGrid(lat);
	const snappedLon = snapToGrid(lon);
	return flatMap.get(`${scenario}|${period}|${indicator}|${snappedLat}|${snappedLon}`) || null;
}

/**
 * Get pre-indexed grid data for a given scenario/period/threshold. O(1) lookup.
 * Returns a Map keyed by "lat_lon" string.
 */
export function getGridData(
	scenario: Scenario,
	period: Period,
	threshold: number
): Map<string, MonthlyData> {
	if (!dataIndex) return new Map();
	const indicator = `tasmax_a${threshold}`;
	return dataIndex.get(`${scenario}|${period}|${indicator}`) || new Map();
}

/**
 * Sum monthly values for a given month range (1-indexed, inclusive).
 */
export function sumMonthRange(data: MonthlyData, monthStart: number, monthEnd: number): number {
	let sum = 0;
	for (let m = monthStart; m <= monthEnd; m++) {
		sum += data[MONTHS[m - 1]];
	}
	return sum;
}

/**
 * Get the monthly values as an array [jan, feb, ..., dec]
 */
export function monthlyToArray(data: MonthlyData): number[] {
	return MONTHS.map((m) => data[m]);
}
