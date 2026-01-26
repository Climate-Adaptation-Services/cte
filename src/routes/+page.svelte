<script lang="ts">
	import UserInput from '$lib/components/UserInput.svelte';
	import Map from '$lib/components/Map.svelte';
	import Chart from '$lib/components/Chart.svelte';
</script>

<div class="container">
	<UserInput />

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

	.maps-container {
		display: flex;
		gap: 20px;
		margin: 2rem 0;
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
		font-size: 20px;
		font-weight: 600;
		color: #333;
		margin-bottom: 12px;
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
