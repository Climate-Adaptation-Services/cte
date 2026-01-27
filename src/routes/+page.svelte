<script lang="ts">
	import UserInput from '$lib/components/UserInput.svelte';
	import Map from '$lib/components/Map.svelte';
	import Chart from '$lib/components/Chart.svelte';
	import { getAppState } from '$lib/stores/appState.svelte';

	const appState = getAppState();

	// Month names for subtitle
	const monthNames = [
		'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
		'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
	];

	// Generate dynamic subtitle with current selection
	const querySubtitle = $derived(() => {
		let queryText = '';
		if (appState.temperature.variable === 'Maximum temperature above') {
			queryText = `Days with max temp above ${appState.temperature.threshold}°C`;
		} else if (appState.temperature.variable === 'Minimum temperature below') {
			queryText = `Days with min temp below ${appState.temperature.threshold}°C`;
		} else {
			queryText = `Days with avg temp between ${appState.temperature.threshold}°C - ${appState.temperature.threshold2}°C`;
		}

		const startMonth = monthNames[appState.temperature.months[0] - 1];
		const endMonth = monthNames[appState.temperature.months[1] - 1];
		const monthRange = startMonth === endMonth ? startMonth : `${startMonth} - ${endMonth}`;

		return `${queryText} | ${appState.temperature.years} | ${monthRange}`;
	});
</script>

<div class="container">
	<UserInput />

	<div class="maps-section">
		<div class="maps-header">
			<h2 class="maps-main-title">Climate Comparison</h2>
			<p class="maps-subtitle">{querySubtitle()}</p>
		</div>

		<div class="maps-container">
			<div class="map-wrapper map-left">
				<p class="map-title">Current climate</p>
				<Map mapId="map_left" period="Historic" showLegend={true} />
			</div>
			<div class="map-wrapper map-right">
				<p class="map-title">Future climate</p>
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
		background: #f8f9fa;
	}

	.container {
		margin-left: 30px;
		margin-right: 30px;
		padding: 20px 0;
	}

	.maps-section {
		margin: 2rem 0;
	}

	.maps-header {
		text-align: center;
		margin-bottom: 1.5rem;
		padding: 1.5rem;
		background: white;
		border-radius: 10px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
		border: 1px solid #e9ecef;
	}

	.maps-main-title {
		font-size: 1.375rem;
		font-weight: 700;
		color: #1a2332;
		margin: 0 0 0.25rem 0;
		line-height: 1.3;
	}

	.maps-subtitle {
		font-size: 0.8125rem;
		color: #6c757d;
		font-weight: 400;
		margin: 0;
	}

	.maps-container {
		display: flex;
		gap: 20px;
	}

	.map-wrapper {
		position: relative;
		flex: 1;
		background: white;
		border-radius: 8px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
		.maps-container {
			flex-direction: column;
		}

		.map-left,
		.map-right {
			width: 100% !important;
			padding-right: 0;
		}
	}
</style>
