<script lang="ts">
	import { onMount } from 'svelte';
	import { getAppState, updateMapView, setSelectedLocation } from '$lib/stores/appState.svelte';
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
	let isInitialized = false;
	let isProgrammaticUpdate = false;

	// Load Leaflet dynamically (client-side only)
	onMount(() => {
		(async () => {
			// Import Leaflet
			const L = (await import('leaflet')).default;

			// Import Leaflet CSS
			const link = document.createElement('link');
			link.rel = 'stylesheet';
			link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
			document.head.appendChild(link);

			// Initialize map
			map = L.map(mapContainer, {
				zoomControl: true,
				attributionControl: true
			}).setView(
				[appState.mapView.center[0], appState.mapView.center[1]],
				appState.mapView.zoom
			);

			// Add OpenStreetMap tile layer
			L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
				attribution: '© OpenStreetMap contributors',
				maxZoom: 19
			}).addTo(map);

			// Handle map move events
			map.on('moveend', () => {
				if (!map) return;

				// Skip if this is a programmatic update from the other map
				if (isProgrammaticUpdate) {
					console.log(`[${mapId}] Skipping programmatic update`);
					isProgrammaticUpdate = false;
					return;
				}

				const center = map.getCenter();
				const zoom = map.getZoom();

				// Only update if this is a user interaction (not programmatic)
				if (isInitialized) {
					console.log(`[${mapId}] User moved map, updating store:`, { center: [center.lat, center.lng], zoom });
					updateMapView({
						center: [center.lat, center.lng],
						zoom
					});
				}
			});

			// Load GeoJSON data
			await loadGeoJSONData(L);

			isInitialized = true;
		})();

		// Cleanup function
		return () => {
			map?.remove();
		};
	});

	async function loadGeoJSONData(L: any) {
		try {
			// Load kenia.geojson grid
			const gridFile = 'kenia.geojson';

			const response = await fetch(`/data/grids/${gridFile}`);
			const geojsonData = await response.json();

			// Create choropleth layer
			if (geoJsonLayer && map) {
				map.removeLayer(geoJsonLayer);
			}

			geoJsonLayer = L.geoJSON(geojsonData, {
				style: function (feature: any) {
					return getFeatureStyle(feature);
				},
				onEachFeature: function (feature: any, layer: any) {
					// Add click handler
					layer.on('click', function () {
						handleFeatureClick(feature);
					});

					// Add hover tooltip
					const lat_lon = feature.properties?.lat_lon || '';
					const [lat, lon] = lat_lon.split('_').map(parseFloat);

					layer.bindTooltip(
						`<b>Location:</b> ${lat.toFixed(2)}, ${lon.toFixed(2)}<br>` +
						`<b>Current:</b> Sample data<br>` +
						`<b>Future:</b> Sample data`,
						{ sticky: true }
					);
				}
			}).addTo(map!);

		} catch (error) {
			console.error('Error loading GeoJSON:', error);
		}
	}

	function getFeatureStyle(feature: any): any {
		// Sample color based on feature index (replace with actual data later)
		const value = Math.random() * 100;

		// Color scale (blue to red)
		let color = '#ffffcc';
		if (value > 80) color = '#bd0026';
		else if (value > 60) color = '#f03b20';
		else if (value > 40) color = '#fd8d3c';
		else if (value > 20) color = '#fecc5c';

		return {
			fillColor: color,
			weight: 0,
			opacity: 0.7,
			fillOpacity: 0.7
		};
	}

	function handleFeatureClick(feature: any) {
		const lat_lon = feature.properties?.lat_lon || '';
		if (lat_lon) {
			const [lat, lon] = lat_lon.split('_').map(parseFloat);
			setSelectedLocation({ lat, lon });
		}
	}

	// Reactive: Update map view when store changes (from other map)
	$effect(() => {
		// Explicitly track these values for reactivity
		const center = appState.mapView.center;
		const zoom = appState.mapView.zoom;

		if (map && isInitialized) {
			const currentCenter = map.getCenter();
			const currentZoom = map.getZoom();

			const [newLat, newLon] = center;

			console.log(`[${mapId}] $effect triggered, store:`, { center, zoom }, 'current:', { center: [currentCenter.lat, currentCenter.lng], zoom: currentZoom });

			// Only update if different (avoid infinite loop)
			if (
				Math.abs(currentCenter.lat - newLat) > 0.001 ||
				Math.abs(currentCenter.lng - newLon) > 0.001 ||
				currentZoom !== zoom
			) {
				console.log(`[${mapId}] Updating map view from store`);
				// Mark as programmatic update to prevent feedback loop
				isProgrammaticUpdate = true;
				map.setView([newLat, newLon], zoom);
			}
		}
	});
</script>

<div class="map-container">
	<div id={mapId} bind:this={mapContainer} class="map"></div>
	{#if showLegend}
		<div class="legend">
			<div class="legend-title">Days</div>
			<div class="legend-item"><span class="legend-color" style="background: #bd0026"></span> 80-100</div>
			<div class="legend-item"><span class="legend-color" style="background: #f03b20"></span> 60-80</div>
			<div class="legend-item"><span class="legend-color" style="background: #fd8d3c"></span> 40-60</div>
			<div class="legend-item"><span class="legend-color" style="background: #fecc5c"></span> 20-40</div>
			<div class="legend-item"><span class="legend-color" style="background: #ffffcc"></span> 0-20</div>
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
		font-size: 14px;
	}

	.legend-item {
		display: flex;
		align-items: center;
		margin: 4px 0;
		font-size: 12px;
	}

	.legend-color {
		display: inline-block;
		width: 20px;
		height: 15px;
		margin-right: 8px;
		border: 1px solid #ccc;
	}
</style>
