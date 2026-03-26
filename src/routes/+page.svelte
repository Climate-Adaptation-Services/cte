<script lang="ts">
	import { onMount } from 'svelte';
	import UserInput from '$lib/components/UserInput.svelte';
	import Map from '$lib/components/Map.svelte';
	import Chart from '$lib/components/Chart.svelte';
	import { getAppState, updateTemperature, getStateFromURL, getLocationFromURL, getCountryFromURL, updateURLFromState, setDataLoaded, setSelectedLocation, setCountry, COUNTRY_CONFIG } from '$lib/stores/appState.svelte';
	import { loadClimateData } from '$lib/services/climateData';

	const appState = getAppState();

	let dataLoadingError = $state<string | null>(null);

	// Load state from URL and climate data on mount
	onMount(async () => {
		// Read country from URL first
		const country = getCountryFromURL();
		setCountry(country);

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
			await loadClimateData(COUNTRY_CONFIG[appState.country].csvFile);
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

		return `Number of days with maximum temperatures above ${appState.temperature.threshold}\u00B0C \u2014 ${monthRange}`;
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

	<details class="about-data">
		<summary class="about-data-toggle">About this tool & data</summary>
		<div class="about-data-content">
			<div class="about-grid">
				<div class="about-item">
					<h4>Data source</h4>
					<p>Climate projections are based on <strong>10 bias-adjusted and statistically downscaled CMIP6 global climate models</strong> provided by phase 3b of the Intersectoral Impact Model Intercomparison Project (see <strong><a href="https://www.isimip.org/" target="_blank" rel="noopener noreferrer">ISIMIP3b</a></strong>). The ensemble includes GFDL-ESM4, IPSL-CM6A-LR, MPI-ESM1-2-HR, MRI-ESM2-0, UKESM1-0-LL, CanESM5, CNRM-CM6-1, CNRM-ESM2-1, EC-Earth3, and MIROC6. Results are based on the ensemble median to provide a robust central estimate. The data were processed as part of the <a href="https://safe4allafrica.eu/" target="_blank" rel="noopener noreferrer">SAFE4ALL Africa</a> project.</p>
				</div>
				<div class="about-item">
					<h4>Methodology</h4>
					<p>Threshold exceedance days are calculated from daily maximum temperature data. Values represent the average number (or percentage) of days per month exceeding the selected threshold over each 30-year period. The median across all ensemble members is used to reduce individual model uncertainty.</p>
				</div>
				<div class="about-item">
					<h4>Time periods and spatial resolution</h4>
					<p>The <strong>historical period (1981–2010)</strong> serves as the baseline reference. The <strong>periods 2036–2065 ("around 2050")</strong> and <strong>2066–2095 ("around 2080")</strong> represent mid-term and long-term future projections. The data are provided at a <strong>spatial resolution of 0.5°</strong> (~50 km × 50 km at the equator).</p>
				</div>
				<div class="about-item">
					<h4>Scenarios</h4>
					<p><strong>Low emissions (SSP1-2.6)</strong> assumes rapid global action to limit warming, reaching net-zero emissions around 2050. <strong>High emissions (SSP5-8.5)</strong> represents continued growth in fossil fuel use with minimal climate policy.</p>
				</div>
				<div class="about-item">
					<h4>Limitations</h4>
					<p>Climate projections are not predictions but plausible futures based on emission scenarios. Local conditions such as urban heat effects or elevation differences within a grid cell are not fully captured. Results should be interpreted as indicative of trends rather than exact values for specific locations.</p>
				</div>
				<div class="about-item references">
					<h4>References</h4>
					<p>Cucchi, M., Weedon, G. P., Amici, A., Bellouin, N., Lange, S., Müller Schmied, H., Hersbach, H., and Buontempo, C.: WFDE5: bias-adjusted ERA5 reanalysis data for impact studies, Earth System Science Data, 12, 2097–2120, <a href="https://doi.org/10.5194/essd-12-2097-2020" target="_blank" rel="noopener noreferrer">https://doi.org/10.5194/essd-12-2097-2020</a>, 2020</p>
					<p>Frieler, K., Volkholz, J., Lange, S., et al.: Scenario setup and forcing data for impact model evaluation and impact attribution within the third round of the Inter-Sectoral Impact Model Intercomparison Project (ISIMIP3a), Geosci. Model Dev., 17, 1–51, <a href="https://doi.org/10.5194/gmd-17-1-2024" target="_blank" rel="noopener noreferrer">https://doi.org/10.5194/gmd-17-1-2024</a>, 2024.</p>
					<p>Lange, S.: ISIMIP3BASD v2.5.0, <a href="https://doi.org/10.5281/zenodo.4686991" target="_blank" rel="noopener noreferrer">https://doi.org/10.5281/zenodo.4686991</a>, 2021.</p>
					<p>Lange, S. and Büchner, M.: ISIMIP3b bias-adjusted atmospheric climate input data (v1.1). ISIMIP Repository. 2021. <a href="https://doi.org/10.48364/ISIMIP.842396.1" target="_blank" rel="noopener noreferrer">https://doi.org/10.48364/ISIMIP.842396.1</a></p>
				</div>
			</div>
		</div>
	</details>
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
		font-size: 1.0625rem;
		font-weight: 600;
		color: #0A565E;
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
		font-size: 0.875rem;
		font-weight: 400;
		color: #6c757d;
		margin: 0 0 0.75rem 0;
		padding-bottom: 0.5rem;
		border-bottom: 1px solid #f0f4f8;
	}

	.about-data {
		margin: 2rem 0;
		background: white;
		border-radius: 10px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
		border: 1px solid #e9ecef;
	}

	.about-data-toggle {
		padding: 1.25rem 1.5rem;
		font-size: 1rem;
		font-weight: 600;
		color: #0A565E;
		cursor: pointer;
		list-style: none;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.about-data-toggle::-webkit-details-marker {
		display: none;
	}

	.about-data-toggle::before {
		content: '▶';
		font-size: 0.625rem;
		transition: transform 0.2s ease;
		color: #6c757d;
	}

	.about-data[open] .about-data-toggle::before {
		transform: rotate(90deg);
	}

	.about-data-content {
		padding: 0 1.5rem 1.5rem;
	}

	.about-grid {
		columns: 2;
		column-gap: 1.5rem;
	}

	.about-item {
		break-inside: avoid;
		margin-bottom: 1.25rem;
	}

	.about-item.references p {
		font-size: 0.6875rem;
	}

	.about-item.references p + p {
		margin-top: 0.5rem;
	}

	.about-item h4 {
		font-size: 0.875rem;
		font-weight: 600;
		color: #0A565E;
		margin: 0 0 0.375rem 0;
	}

	.about-item a {
		color: #0A565E;
		text-decoration: underline;
	}

	.about-item a:hover {
		color: #084850;
	}

	.about-item p {
		font-size: 0.8125rem;
		color: #2c3e50;
		line-height: 1.6;
		margin: 0;
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
			padding: 0.75rem;
		}

		.maps-title {
			font-size: 0.75rem;
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

		.about-grid {
			columns: 1;
		}
	}

	@media (max-width: 480px) {
		.container {
			margin-left: 8px;
			margin-right: 8px;
			padding: 8px 0;
		}

		.maps-section {
			padding: 0.5rem;
		}

		.map-wrapper {
			border-radius: 6px;
			padding: 0.375rem;
		}

		.about-data-toggle {
			padding: 1rem;
			font-size: 0.875rem;
		}

		.about-data-content {
			padding: 0 1rem 1rem;
		}
	}
</style>
