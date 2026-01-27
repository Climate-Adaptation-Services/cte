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
	let isLoading = $state(true);
	let showTouchHint = $state(false);
	let touchHintTimeout: ReturnType<typeof setTimeout> | null = null;

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

			// Check if mobile device
			const isMobile = window.matchMedia('(max-width: 768px)').matches || 'ontouchstart' in window;

			// Initialize map
			map = L.map(mapContainer, {
				zoomControl: true,
				attributionControl: true,
				scrollWheelZoom: false,
				dragging: !isMobile, // Disable dragging on mobile (requires 2 fingers)
				tap: false // Disable tap handler on mobile
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

			// Add touch hint for mobile users
			if (isMobile) {
				mapContainer.addEventListener('touchstart', (e) => {
					if (e.touches.length === 1) {
						// Single finger touch - show hint
						showTouchHint = true;
						if (touchHintTimeout) clearTimeout(touchHintTimeout);
						touchHintTimeout = setTimeout(() => {
							showTouchHint = false;
						}, 2000);
					}
				});

				mapContainer.addEventListener('touchmove', (e) => {
					if (e.touches.length >= 2) {
						// Two finger gesture - enable dragging temporarily and hide hint
						showTouchHint = false;
						map!.dragging.enable();
					}
				});

				mapContainer.addEventListener('touchend', () => {
					// Re-disable dragging after gesture ends
					if (isMobile) {
						map!.dragging.disable();
					}
				});
			}

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

			isLoading = false;
		} catch (error) {
			console.error('Error loading GeoJSON:', error);
			isLoading = false;
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

		.legend-item {
			font-size: 11px;
			margin: 3px 0;
		}

		.legend-color {
			width: 16px;
			height: 12px;
			margin-right: 6px;
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

		.legend-item {
			font-size: 10px;
			margin: 2px 0;
		}

		.legend-color {
			width: 14px;
			height: 10px;
			margin-right: 4px;
		}
	}
</style>
