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
