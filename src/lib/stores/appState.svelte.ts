/**
 * Central application state management for Climate Atlas
 * Uses Svelte 5 runes for reactivity
 */

type Tab = "temperature";

interface TemperatureState {
  variable:
    | "Maximum temperature above"
    | "Minimum temperature below"
    | "Average temperature between";
  threshold: number;
  threshold2: number;
  years: "2011-2040" | "2041-2070" | "2071-2100";
  months: [number, number]; // [start, end] month (1-12)
}

interface MapView {
  center: [number, number]; // [lat, lon]
  zoom: number;
}

interface Location {
  lat: number;
  lon: number;
}

interface AppState {
  activeTab: Tab;
  temperature: TemperatureState;
  mapView: MapView;
  selectedLocation: Location | null;
}

// Create reactive state - export directly for better reactivity
export const appState = $state<AppState>({
  activeTab: "temperature",
  temperature: {
    variable: "Maximum temperature above",
    threshold: 25,
    threshold2: 35,
    years: "2041-2070",
    months: [1, 12],
  },
  mapView: {
    center: [0.242001, 37.717031],
    zoom: 5.5,
  },
  selectedLocation: null,
});

// Determine which grid to use - always use kenia.geojson for temperature
export const currentGrid = "kenia";

// Legacy function for backwards compatibility
export function getAppState() {
  return appState;
}

// Convenience functions for updating state
export function updateTemperature(updates: Partial<TemperatureState>) {
  appState.temperature = { ...appState.temperature, ...updates };
}

export function updateMapView(updates: Partial<MapView>) {
  appState.mapView = { ...appState.mapView, ...updates };
}

export function setSelectedLocation(location: Location | null) {
  appState.selectedLocation = location;
}

// Default values for reset
const defaultTemperature: TemperatureState = {
  variable: "Maximum temperature above",
  threshold: 25,
  threshold2: 35,
  years: "2041-2070",
  months: [1, 12],
};

export function resetToDefaults() {
  appState.temperature = { ...defaultTemperature };
}

// URL parameter helpers
export function getStateFromURL(): Partial<TemperatureState> | null {
  if (typeof window === 'undefined') return null;

  const params = new URLSearchParams(window.location.search);
  const state: Partial<TemperatureState> = {};

  const variable = params.get('var');
  if (variable === 'max' || variable === 'min' || variable === 'avg') {
    state.variable = variable === 'max' ? 'Maximum temperature above'
      : variable === 'min' ? 'Minimum temperature below'
      : 'Average temperature between';
  }

  const threshold = params.get('t1');
  if (threshold) state.threshold = parseInt(threshold);

  const threshold2 = params.get('t2');
  if (threshold2) state.threshold2 = parseInt(threshold2);

  const years = params.get('years');
  if (years === '2011-2040' || years === '2041-2070' || years === '2071-2100') {
    state.years = years;
  }

  const months = params.get('months');
  if (months) {
    const [start, end] = months.split('-').map(Number);
    if (start >= 1 && start <= 12 && end >= 1 && end <= 12) {
      state.months = [start, end];
    }
  }

  return Object.keys(state).length > 0 ? state : null;
}

export function updateURLFromState() {
  if (typeof window === 'undefined') return;

  const params = new URLSearchParams();

  const varMap = {
    'Maximum temperature above': 'max',
    'Minimum temperature below': 'min',
    'Average temperature between': 'avg'
  };
  params.set('var', varMap[appState.temperature.variable]);
  params.set('t1', appState.temperature.threshold.toString());
  if (appState.temperature.variable === 'Average temperature between') {
    params.set('t2', appState.temperature.threshold2.toString());
  }
  params.set('years', appState.temperature.years);
  params.set('months', `${appState.temperature.months[0]}-${appState.temperature.months[1]}`);

  const newURL = `${window.location.pathname}?${params.toString()}`;
  window.history.replaceState({}, '', newURL);
}
