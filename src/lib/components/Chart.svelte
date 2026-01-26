<script lang="ts">
	import { onMount } from 'svelte';
	import { getAppState } from '$lib/stores/appState.svelte';
	import * as d3 from 'd3';

	const appState = getAppState();

	let svgContainer: HTMLDivElement;
	let svg: d3.Selection<SVGGElement, unknown, null, undefined> | null = null;

	const margin = { top: 20, right: 30, bottom: 50, left: 60 };
	let width = 0;
	let height = 400;

	onMount(() => {
		// Create SVG
		const containerWidth = svgContainer.clientWidth;
		width = containerWidth - margin.left - margin.right;
		height = 400 - margin.top - margin.bottom;

		svg = d3
			.select(svgContainer)
			.append('svg')
			.attr('width', containerWidth)
			.attr('height', 400)
			.append('g')
			.attr('transform', `translate(${margin.left},${margin.top})`);

		// Initial render
		renderChart();
	});

	function renderChart() {
		if (!svg) return;

		// Clear previous content
		svg.selectAll('*').remove();

		if (!appState.selectedLocation) {
			// Show placeholder
			renderPlaceholder();
		} else {
			renderTemperatureChart();
		}
	}

	function renderPlaceholder() {
		if (!svg) return;

		svg
			.append('text')
			.attr('x', width / 2)
			.attr('y', height / 2)
			.attr('text-anchor', 'middle')
			.style('font-size', '16px')
			.style('fill', '#666')
			.text('Click on the left map to select a location');
	}

	function renderTemperatureChart() {
		if (!svg) return;

		// Sample data for temperature seasonality
		const months = [
			'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
			'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
		];

		const sampleData = months.map((month, i) => ({
			month: i + 1,
			monthName: month,
			era5: 20 + Math.sin(i * 0.5) * 5,
			upcoming: 21 + Math.sin(i * 0.5) * 5,
			mid: 22 + Math.sin(i * 0.5) * 5,
			end: 23 + Math.sin(i * 0.5) * 5
		}));

		// Scales
		const xScale = d3
			.scalePoint<number>()
			.domain(sampleData.map(d => d.month))
			.range([0, width])
			.padding(0.5);

		const yScale = d3
			.scaleLinear()
			.domain([
				d3.min(sampleData, d => Math.min(d.era5, d.upcoming, d.mid, d.end))! - 2,
				d3.max(sampleData, d => Math.max(d.era5, d.upcoming, d.mid, d.end))! + 2
			])
			.range([height, 0]);

		// Add axes
		svg!
			.append('g')
			.attr('transform', `translate(0,${height})`)
			.call(
				d3
					.axisBottom(xScale)
					.tickFormat((d) => sampleData.find(sd => sd.month === d)?.monthName || '')
			);

		svg!
			.append('g')
			.call(d3.axisLeft(yScale));

		// Add Y axis label
		svg!
			.append('text')
			.attr('transform', 'rotate(-90)')
			.attr('y', 0 - margin.left)
			.attr('x', 0 - height / 2)
			.attr('dy', '1em')
			.style('text-anchor', 'middle')
			.text('Temperature (°C)');

		// Line generators
		const lineGenerators = {
			era5: d3
				.line<any>()
				.x(d => xScale(d.month)!)
				.y(d => yScale(d.era5)),
			upcoming: d3
				.line<any>()
				.x(d => xScale(d.month)!)
				.y(d => yScale(d.upcoming)),
			mid: d3
				.line<any>()
				.x(d => xScale(d.month)!)
				.y(d => yScale(d.mid)),
			end: d3
				.line<any>()
				.x(d => xScale(d.month)!)
				.y(d => yScale(d.end))
		};

		// Line colors
		const colors = {
			era5: 'maroon',
			upcoming: 'red',
			mid: 'orange',
			end: 'yellow'
		};

		// Draw lines
		Object.entries(lineGenerators).forEach(([key, lineGen]) => {
			svg!
				.append('path')
				.datum(sampleData)
				.attr('fill', 'none')
				.attr('stroke', colors[key as keyof typeof colors])
				.attr('stroke-width', 2)
				.attr('d', lineGen);
		});

		// Add legend
		const legend = svg!
			.append('g')
			.attr('transform', `translate(${width - 150}, 10)`);

		const legendData = [
			{ name: 'Historical (ERA5)', color: 'maroon' },
			{ name: 'Upcoming period (2011-2040)', color: 'red' },
			{ name: 'Mid century (2041-2070)', color: 'orange' },
			{ name: 'End century (2071-2100)', color: 'yellow' }
		];

		legendData.forEach((item, i) => {
			const legendRow = legend
				.append('g')
				.attr('transform', `translate(0, ${i * 20})`);

			legendRow
				.append('line')
				.attr('x1', 0)
				.attr('x2', 20)
				.attr('y1', 10)
				.attr('y2', 10)
				.attr('stroke', item.color)
				.attr('stroke-width', 2);

			legendRow
				.append('text')
				.attr('x', 25)
				.attr('y', 10)
				.attr('dy', '0.35em')
				.style('font-size', '11px')
				.text(item.name);
		});

		// Add title
		svg!
			.append('text')
			.attr('x', width / 2)
			.attr('y', -5)
			.attr('text-anchor', 'middle')
			.style('font-size', '14px')
			.style('font-weight', 'bold')
			.text('Seasonality of temperature for selected location');
	}

	// Re-render when selectedLocation changes
	$effect(() => {
		if (appState.selectedLocation !== undefined) {
			renderChart();
		}
	});
</script>

<div class="chart-container" bind:this={svgContainer}></div>

<style>
	.chart-container {
		width: 100%;
		height: 50vh;
		min-height: 400px;
		background: white;
		padding: 20px;
		border-radius: 4px;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
	}
</style>
