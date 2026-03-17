<script lang="ts">
	import { onMount } from 'svelte';
	import { getAppState, updateMapView, setSelectedLocation } from '$lib/stores/appState.svelte';
	import {
		getGridData,
		getLocationData,
		snapToGrid,
		sumMonthRange,
		type Scenario,
		type Period,
		type MonthlyData
	} from '$lib/services/climateData';
	import * as d3 from 'd3';
	import type L from 'leaflet';

	interface MapProps {
		mapId: string;
		period: 'Historic' | 'Projection';
		showLegend: boolean;
	}

	let { mapId, period, showLegend }: MapProps = $props();

	const appState = getAppState();

	let mapContainer: HTMLDivElement;
	let map: L.Map | null = null;
	let geoJsonLayer: L.GeoJSON | null = null;
	let leafletModule: any = null;
	let geojsonData: any = null;
	let isInitialized = false;
	let isProgrammaticUpdate = false;
	let isLoading = $state(true);
	let showTouchHint = $state(false);
	let touchHintTimeout: ReturnType<typeof setTimeout> | null = null;

	// Pre-computed snap cache: feature index → snapped "lat_lon" key
	let snapCache: Map<number, string> = new Map();
	// Pre-computed parsed coords: feature index → [lat, lon]
	let coordCache: Map<number, [number, number]> = new Map();

	// Dynamic tooltip element
	let tooltipLayer: any = null;

	// Determine scenario and period for this map
	function getMapScenario(): Scenario {
		return period === 'Historic' ? 'historical' : appState.temperature.scenario;
	}

	function getMapPeriod(): Period {
		return period === 'Historic' ? '1981-2010' : appState.temperature.years;
	}

	// Legend state
	let legendMin = $state(0);
	let legendMax = $state(100);

	const scenarioLabels: Record<string, string> = {
		ssp126: 'Low emissions',
		ssp585: 'High emissions'
	};

	function getColor(value: number, minVal: number, maxVal: number): string {
		if (maxVal <= minVal) return '#ffffcc';
		const ratio = Math.max(0, Math.min(1, (value - minVal) / (maxVal - minVal)));
		return d3.interpolateYlOrRd(ratio * 0.85 + 0.1) as string;
	}

	// Build the snap cache once from geojsonData
	function buildSnapCache() {
		if (!geojsonData) return;
		snapCache = new Map();
		coordCache = new Map();
		for (let i = 0; i < geojsonData.features.length; i++) {
			const feature = geojsonData.features[i];
			const lat_lon = feature.properties?.lat_lon || '';
			const [lat, lon] = lat_lon.split('_').map(parseFloat);
			const snappedKey = `${snapToGrid(lat)}_${snapToGrid(lon)}`;
			snapCache.set(i, snappedKey);
			coordCache.set(i, [lat, lon]);
		}
	}

	onMount(() => {
		(async () => {
			const L = (await import('leaflet')).default;
			leafletModule = L;

			const link = document.createElement('link');
			link.rel = 'stylesheet';
			link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
			document.head.appendChild(link);

			const isMobile = window.matchMedia('(max-width: 768px)').matches || 'ontouchstart' in window;

			map = L.map(mapContainer, {
				zoomControl: true,
				attributionControl: true,
				scrollWheelZoom: false,
				dragging: !isMobile
			}).setView(
				[appState.mapView.center[0], appState.mapView.center[1]],
				appState.mapView.zoom
			);

			L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
				attribution: '&copy; OpenStreetMap contributors',
				maxZoom: 19
			}).addTo(map);

			map.on('moveend', () => {
				if (!map) return;
				if (isProgrammaticUpdate) {
					isProgrammaticUpdate = false;
					return;
				}
				const center = map.getCenter();
				const zoom = map.getZoom();
				if (isInitialized) {
					updateMapView({ center: [center.lat, center.lng], zoom });
				}
			});

			if (isMobile) {
				mapContainer.addEventListener('touchstart', (e) => {
					if (e.touches.length === 1) {
						showTouchHint = true;
						if (touchHintTimeout) clearTimeout(touchHintTimeout);
						touchHintTimeout = setTimeout(() => { showTouchHint = false; }, 2000);
					}
				});
				mapContainer.addEventListener('touchmove', (e) => {
					if (e.touches.length >= 2) {
						showTouchHint = false;
						map!.dragging.enable();
					}
				});
				mapContainer.addEventListener('touchend', () => {
					if (isMobile) map!.dragging.disable();
				});
			}

			await loadGeoJSONData(L);
			isInitialized = true;
		})();

		return () => { map?.remove(); };
	});

	async function loadGeoJSONData(L: any) {
		try {
			const response = await fetch(`/data/grids/kenia.geojson`);
			geojsonData = await response.json();

			// Pre-compute snap cache (once, never changes)
			buildSnapCache();

			// Create the GeoJSON layer ONCE
			createGeoJSONLayer(L);

			isLoading = false;
		} catch (error) {
			console.error('Error loading GeoJSON:', error);
			isLoading = false;
		}
	}

	/**
	 * Create the GeoJSON layer once with click handlers and dynamic tooltip.
	 * Styling is done separately via updateStyles().
	 */
	function createGeoJSONLayer(L: any) {
		if (!map || !geojsonData) return;

		// Create a single tooltip to reuse
		tooltipLayer = L.tooltip({ sticky: true });

		geoJsonLayer = L.geoJSON(geojsonData, {
			// Initial style: gray (will be updated immediately)
			style: () => ({ fillColor: '#e0e0e0', weight: 0, opacity: 0.3, fillOpacity: 0.3 }),
			onEachFeature: function (feature: any, layer: any) {
				// Store feature index on the layer for fast lookups
				const idx = geojsonData.features.indexOf(feature);
				(layer as any)._featureIdx = idx;

				layer.on('click', () => handleFeatureClick(feature));

				// Dynamic tooltip: compute content on hover
				layer.on('mouseover', function (e: any) {
					const content = getTooltipContent(idx);
					if (content) {
						tooltipLayer.setContent(content);
						tooltipLayer.setLatLng(e.latlng);
						if (map) map.openTooltip(tooltipLayer);
					}
				});

				layer.on('mousemove', function (e: any) {
					tooltipLayer.setLatLng(e.latlng);
				});

				layer.on('mouseout', function () {
					if (map) map.closeTooltip(tooltipLayer);
				});
			}
		}).addTo(map);

		// Apply initial styles
		updateStyles();
	}

	/**
	 * Generate tooltip HTML for a feature. Called on hover only (not pre-computed).
	 */
	function getTooltipContent(featureIdx: number): string | null {
		const coords = coordCache.get(featureIdx);
		if (!coords) return null;
		const [lat, lon] = coords;

		const threshold = appState.temperature.threshold;
		const monthStart = appState.temperature.months[0];
		const monthEnd = appState.temperature.months[1];

		const histData = getLocationData('historical', '1981-2010', threshold, lat, lon);
		const futureData = getLocationData(appState.temperature.scenario, appState.temperature.years, threshold, lat, lon);

		if (!histData && !futureData) {
			return `<div style="font-size:12px;line-height:1.6">
				<div style="color:#6b7280;font-size:11px">${lat.toFixed(2)}°, ${lon.toFixed(2)}°</div>
				<div>No data available</div>
			</div>`;
		}

		const histVal = histData ? Math.round(sumMonthRange(histData, monthStart, monthEnd)) : null;
		const futVal = futureData ? Math.round(sumMonthRange(futureData, monthStart, monthEnd)) : null;

		const scenarioLabel = scenarioLabels[appState.temperature.scenario] || appState.temperature.scenario;
		const periodLabel = appState.temperature.years === '2036-2065' ? 'Around 2050' : 'Around 2080';

		let changeHtml = '';
		if (histVal !== null && futVal !== null) {
			const delta = futVal - histVal;
			const sign = delta > 0 ? '+' : '';
			const color = delta > 0 ? '#dc2626' : delta < 0 ? '#16a34a' : '#6b7280';
			changeHtml = `<div style="border-top:1px solid #e5e7eb;margin-top:6px;padding-top:6px;color:${color};font-weight:600">${sign}${delta} days</div>`;
		}

		return `<div style="font-size:12px;line-height:1.6">
			<div style="color:#6b7280;font-size:11px;margin-bottom:4px">${lat.toFixed(2)}°, ${lon.toFixed(2)}°</div>
			<div style="display:flex;justify-content:space-between;gap:12px">
				<span style="color:#6b7280">Historical</span>
				<span style="font-weight:600">${histVal !== null ? histVal + ' days' : 'N/A'}</span>
			</div>
			<div style="display:flex;justify-content:space-between;gap:12px">
				<span style="color:#6b7280">${periodLabel} (${scenarioLabel.toLowerCase()})</span>
				<span style="font-weight:600">${futVal !== null ? futVal + ' days' : 'N/A'}</span>
			</div>
			${changeHtml}
		</div>`;
	}

	/**
	 * Fast style update - only recomputes colors, doesn't recreate the layer.
	 */
	function updateStyles() {
		if (!geoJsonLayer) return;

		const scenario = getMapScenario();
		const mapPeriod = getMapPeriod();
		const threshold = appState.temperature.threshold;
		const monthStart = appState.temperature.months[0];
		const monthEnd = appState.temperature.months[1];

		// O(1) lookup for the grid data
		const gridData = getGridData(scenario, mapPeriod, threshold);

		// Compute min/max from the ~323 grid cells (fast)
		let minVal = Infinity;
		let maxVal = -Infinity;
		for (const data of gridData.values()) {
			const value = sumMonthRange(data, monthStart, monthEnd);
			if (value < minVal) minVal = value;
			if (value > maxVal) maxVal = value;
		}
		if (minVal === Infinity) { minVal = 0; maxVal = 0; }

		legendMin = Math.round(minVal);
		legendMax = Math.round(maxVal);

		// Update each feature's style (Leaflet setStyle is much faster than recreating)
		geoJsonLayer.eachLayer((layer: any) => {
			const idx: number = layer._featureIdx;
			const snappedKey = snapCache.get(idx);
			if (snappedKey === undefined) return;

			const data = gridData.get(snappedKey);
			if (!data) {
				layer.setStyle({ fillColor: '#e0e0e0', weight: 0, opacity: 0.3, fillOpacity: 0.3 });
				return;
			}

			const value = sumMonthRange(data, monthStart, monthEnd);
			const color = getColor(value, minVal, maxVal);
			layer.setStyle({ fillColor: color, weight: 0, opacity: 0.7, fillOpacity: 0.7 });
		});
	}

	function handleFeatureClick(feature: any) {
		const lat_lon = feature.properties?.lat_lon || '';
		if (lat_lon) {
			const [lat, lon] = lat_lon.split('_').map(parseFloat);
			setSelectedLocation({ lat, lon });
		}
	}

	// Re-style when climate parameters change (fast - no layer recreation)
	$effect(() => {
		const _ = [
			appState.temperature.threshold,
			appState.temperature.years,
			appState.temperature.scenario,
			appState.temperature.months[0],
			appState.temperature.months[1],
			appState.dataLoaded
		];

		if (geoJsonLayer && appState.dataLoaded) {
			updateStyles();
		}
	});

	// Sync map view from other map
	$effect(() => {
		const center = appState.mapView.center;
		const zoom = appState.mapView.zoom;

		if (map && isInitialized) {
			const currentCenter = map.getCenter();
			const currentZoom = map.getZoom();
			const [newLat, newLon] = center;

			if (
				Math.abs(currentCenter.lat - newLat) > 0.001 ||
				Math.abs(currentCenter.lng - newLon) > 0.001 ||
				currentZoom !== zoom
			) {
				isProgrammaticUpdate = true;
				map.setView([newLat, newLon], zoom);
			}
		}
	});
</script>

<div class="map-container">
	{#if isLoading}
		<div class="loading-overlay">
			<div class="spinner"></div>
			<p>Loading map data...</p>
		</div>
	{/if}
	{#if showTouchHint}
		<div class="touch-hint">
			<span>Use two fingers to move the map</span>
		</div>
	{/if}
	<div id={mapId} bind:this={mapContainer} class="map"></div>
	{#if showLegend}
		<div class="legend">
			<div class="legend-title">Days above {appState.temperature.threshold}°C</div>
			<div class="legend-gradient">
				<div class="gradient-bar"></div>
				<div class="gradient-labels">
					<span>{legendMin}</span>
					<span>{Math.round((legendMin + legendMax) / 2)}</span>
					<span>{legendMax}</span>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	.map-container {
		position: relative;
		width: 100%;
		height: 60vh;
		min-height: 400px;
	}

	.map {
		width: 100%;
		height: 100%;
		border-radius: 6px;
		overflow: hidden;
	}

	.legend {
		position: absolute;
		bottom: 20px;
		right: 20px;
		background: white;
		padding: 10px;
		border-radius: 4px;
		box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
		z-index: 1000;
	}

	.legend-title {
		font-weight: bold;
		margin-bottom: 8px;
		font-size: 13px;
	}

	.legend-gradient {
		width: 100%;
	}

	.gradient-bar {
		width: 100%;
		height: 14px;
		border-radius: 3px;
		border: 1px solid #ccc;
		background: linear-gradient(to right,
			#ffffcc 0%,
			#fed976 15%,
			#feb24c 30%,
			#fd8d3c 45%,
			#f03b20 65%,
			#bd0026 85%,
			#800026 100%
		);
	}

	.gradient-labels {
		display: flex;
		justify-content: space-between;
		margin-top: 4px;
		font-size: 11px;
		color: #555;
	}

	/* Touch hint overlay */
	.touch-hint {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 999;
		pointer-events: none;
		border-radius: 6px;
	}

	.touch-hint span {
		background: white;
		padding: 12px 20px;
		border-radius: 8px;
		font-size: 14px;
		font-weight: 500;
		color: #333;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
	}

	/* Loading Overlay */
	.loading-overlay {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(255, 255, 255, 0.9);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		border-radius: 6px;
	}

	.loading-overlay p {
		margin-top: 1rem;
		color: #0A565E;
		font-size: 0.875rem;
		font-weight: 500;
	}

	.spinner {
		width: 40px;
		height: 40px;
		border: 3px solid #e9ecef;
		border-top-color: #0A565E;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	/* Mobile Responsive Styles */
	@media (max-width: 768px) {
		.map-container {
			height: 50vh;
			min-height: 300px;
		}

		.legend {
			bottom: 10px;
			right: 10px;
			padding: 8px;
		}

		.legend-title {
			font-size: 12px;
			margin-bottom: 6px;
		}

		.gradient-labels {
			font-size: 10px;
		}

		.loading-overlay p {
			font-size: 0.8125rem;
		}

		.spinner {
			width: 32px;
			height: 32px;
		}
	}

	@media (max-width: 480px) {
		.map-container {
			height: 45vh;
			min-height: 250px;
		}

		.legend {
			bottom: 8px;
			right: 8px;
			padding: 6px;
			border-radius: 3px;
		}

		.legend-title {
			font-size: 11px;
			margin-bottom: 4px;
		}

		.gradient-labels {
			font-size: 9px;
		}
	}
</style>
