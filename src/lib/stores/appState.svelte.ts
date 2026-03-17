/**
 * Central application state management for Climate Atlas
 * Uses Svelte 5 runes for reactivity
 */

import type { Scenario, FuturePeriod } from '$lib/services/climateData';

type Tab = "temperature";

interface TemperatureState {
  threshold: number;
  years: FuturePeriod;
  scenario: Scenario;
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
  dataLoaded: boolean;
}

// Create reactive state - export directly for better reactivity
export const appState = $state<AppState>({
  activeTab: "temperature",
  temperature: {
    threshold: 35,
    years: "2036-2065",
    scenario: "ssp585",
    months: [1, 12],
  },
  mapView: {
    center: [0.242001, 37.717031],
    zoom: 5.5,
  },
  selectedLocation: null,
  dataLoaded: false,
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

export function setDataLoaded(loaded: boolean) {
  appState.dataLoaded = loaded;
}

// Default values for reset
const defaultTemperature: TemperatureState = {
  threshold: 35,
  years: "2036-2065",
  scenario: "ssp370",
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

  const threshold = params.get('t1');
  if (threshold) {
    const t = parseInt(threshold);
    if (t >= 15 && t <= 40) state.threshold = t;
  }

  const years = params.get('years');
  if (years === '2036-2065' || years === '2066-2095') {
    state.years = years;
  }

  const scenario = params.get('scenario');
  if (scenario === 'ssp126' || scenario === 'ssp370' || scenario === 'ssp585') {
    state.scenario = scenario;
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

export function getLocationFromURL(): Location | null {
  if (typeof window === 'undefined') return null;

  const params = new URLSearchParams(window.location.search);
  const lat = params.get('lat');
  const lon = params.get('lon');

  if (lat && lon) {
    const latNum = parseFloat(lat);
    const lonNum = parseFloat(lon);
    if (!isNaN(latNum) && !isNaN(lonNum)) {
      return { lat: latNum, lon: lonNum };
    }
  }
  return null;
}

export function updateURLFromState() {
  if (typeof window === 'undefined') return;

  const params = new URLSearchParams();

  params.set('t1', appState.temperature.threshold.toString());
  params.set('years', appState.temperature.years);
  params.set('scenario', appState.temperature.scenario);
  params.set('months', `${appState.temperature.months[0]}-${appState.temperature.months[1]}`);

  if (appState.selectedLocation) {
    params.set('lat', appState.selectedLocation.lat.toFixed(4));
    params.set('lon', appState.selectedLocation.lon.toFixed(4));
  }

  const newURL = `${window.location.pathname}?${params.toString()}`;
  window.history.replaceState({}, '', newURL);
}
