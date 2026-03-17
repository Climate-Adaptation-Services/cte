<script lang="ts">
	import { onMount } from 'svelte';
	import UserInput from '$lib/components/UserInput.svelte';
	import Map from '$lib/components/Map.svelte';
	import Chart from '$lib/components/Chart.svelte';
	import { getAppState, updateTemperature, getStateFromURL, getLocationFromURL, updateURLFromState, setDataLoaded, setSelectedLocation } from '$lib/stores/appState.svelte';
	import { loadClimateData } from '$lib/services/climateData';

	const appState = getAppState();

	let dataLoadingError = $state<string | null>(null);

	// Load state from URL and climate data on mount
	onMount(async () => {
		const urlState = getStateFromURL();
		if (urlState) {
			updateTemperature(urlState);
		}

		const urlLocation = getLocationFromURL();
		if (urlLocation) {
			setSelectedLocation(urlLocation);
		}

		// Load climate CSV data
		try {
			await loadClimateData();
			setDataLoaded(true);
		} catch (error) {
			console.error('Failed to load climate data:', error);
			dataLoadingError = 'Failed to load climate data. Please refresh the page.';
		}
	});

	// Update URL when state changes
	$effect(() => {
		const _ = [
			appState.temperature.threshold,
			appState.temperature.years,
			appState.temperature.scenario,
			appState.temperature.months,
			appState.selectedLocation?.lat,
			appState.selectedLocation?.lon
		];
		updateURLFromState();
	});

	// Month names for subtitle
	const monthNames = [
		'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
		'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
	];

	const scenarioLabels: Record<string, string> = {
		ssp126: 'Low emissions',
		ssp585: 'High emissions'
	};

	// Shared title above both maps
	const mapsTitle = $derived(() => {
		const startMonth = monthNames[appState.temperature.months[0] - 1];
		const endMonth = monthNames[appState.temperature.months[1] - 1];
		const monthRange = startMonth === endMonth ? startMonth : `${startMonth} to ${endMonth}`;

		return `Number of days with maximum temperature above ${appState.temperature.threshold}\u00B0C \u2014 ${monthRange}`;
	});

	const yearsLabel = $derived(() => {
		return appState.temperature.years === '2036-2065' ? 'Around 2050' : 'Around 2080';
	});
</script>

<div class="container">
	<UserInput />

	{#if dataLoadingError}
		<div class="error-banner">
			<p>{dataLoadingError}</p>
		</div>
	{/if}

	{#if !appState.dataLoaded}
		<div class="loading-banner">
			<div class="loading-spinner"></div>
			<p>Loading climate data...</p>
		</div>
	{/if}

	<div class="maps-section">
		<h2 class="maps-title">{mapsTitle()}</h2>
		<div class="maps-container">
			<div class="map-wrapper map-left">
				<p class="map-title">Historical (1981-2010)</p>
				<Map mapId="map_left" period="Historic" showLegend={true} />
			</div>
			<div class="map-wrapper map-right">
				<p class="map-title">{yearsLabel()} ({(scenarioLabels[appState.temperature.scenario] || '').toLowerCase()})</p>
				<Map mapId="map_right" period="Projection" showLegend={false} />
			</div>
		</div>
	</div>

	<Chart />
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
		background: #F4FBF4;
	}

	.container {
		margin-left: 30px;
		margin-right: 30px;
		padding: 20px 0;
	}

	.loading-banner {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.75rem;
		padding: 1rem;
		margin-bottom: 1rem;
		background: #f0f9ff;
		border: 1px solid #bae6fd;
		border-radius: 8px;
		color: #0369a1;
		font-size: 0.875rem;
		font-weight: 500;
	}

	.loading-spinner {
		width: 20px;
		height: 20px;
		border: 2px solid #bae6fd;
		border-top-color: #0369a1;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}

	.error-banner {
		padding: 1rem;
		margin-bottom: 1rem;
		background: #fef2f2;
		border: 1px solid #fecaca;
		border-radius: 8px;
		color: #dc2626;
		font-size: 0.875rem;
		text-align: center;
	}

	.error-banner p {
		margin: 0;
	}

	.maps-section {
		margin: 2rem 0;
		background: white;
		border-radius: 10px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
		border: 1px solid #e9ecef;
		padding: 1.5rem;
	}

	.maps-title {
		text-align: center;
		font-size: 1.125rem;
		font-weight: 600;
		color: #1a2332;
		margin: 0 0 1rem 0;
	}

	.maps-container {
		display: flex;
		gap: 20px;
	}

	.map-wrapper {
		position: relative;
		flex: 1;
		background: #fafbfc;
		border-radius: 8px;
		border: 1px solid #e9ecef;
		overflow: hidden;
		padding: 1rem;
	}

	.map-left {
		width: 50%;
	}

	.map-right {
		width: 50%;
	}

	.map-title {
		text-align: center;
		font-size: 0.9375rem;
		font-weight: 600;
		color: #2c3e50;
		margin: 0 0 0.75rem 0;
		padding-bottom: 0.5rem;
		border-bottom: 1px solid #f0f4f8;
	}

	/* Responsive design */
	@media (max-width: 768px) {
		.container {
			margin-left: 12px;
			margin-right: 12px;
			padding: 12px 0;
		}

		.maps-section {
			margin: 1rem 0;
		}

		.maps-title {
			font-size: 0.9375rem;
			margin-bottom: 0.75rem;
		}

		.maps-container {
			flex-direction: column;
			gap: 12px;
		}

		.map-left,
		.map-right {
			width: 100% !important;
			padding: 0.75rem;
		}

		.map-title {
			font-size: 0.875rem;
			margin-bottom: 0.5rem;
			padding-bottom: 0.375rem;
		}
	}

	@media (max-width: 480px) {
		.container {
			margin-left: 8px;
			margin-right: 8px;
			padding: 8px 0;
		}

		.map-wrapper {
			border-radius: 6px;
			padding: 0.5rem;
		}
	}
</style>
