<script lang="ts">
	import { onMount } from 'svelte';
	import { getAppState } from '$lib/stores/appState.svelte';
	import { getLocationData, snapToGrid, monthlyToArray } from '$lib/services/climateData';
	import * as d3 from 'd3';

	const appState = getAppState();

	let svgContainer: HTMLDivElement;
	let svg: d3.Selection<SVGGElement, unknown, null, undefined> | null = null;
	let tooltip: d3.Selection<HTMLDivElement, unknown, null, undefined> | null = null;

	let margin = { top: 70, right: 30, bottom: 50, left: 65 };
	let width = 0;
	let height = 400;
	let svgWidth = 0;

	function getResponsiveMargin() {
		const containerWidth = svgContainer?.clientWidth || 600;
		if (containerWidth < 480) {
			return { top: 50, right: 15, bottom: 55, left: 45 };
		} else if (containerWidth < 768) {
			return { top: 60, right: 20, bottom: 60, left: 55 };
		}
		return { top: 70, right: 30, bottom: 50, left: 65 };
	}

	function getResponsiveSizes() {
		const containerWidth = svgContainer?.clientWidth || 600;
		if (containerWidth < 480) {
			return {
				titleY: -35,
				subtitleY: -18,
				titleFontSize: '14px',
				subtitleFontSize: '11px',
				iconRadius: 35,
				axisFontSize: '9px',
				yAxisLabelSize: '10px',
				showAllMonths: false,
				legendBelow: true
			};
		} else if (containerWidth < 768) {
			return {
				titleY: -40,
				subtitleY: -20,
				titleFontSize: '15px',
				subtitleFontSize: '12px',
				iconRadius: 40,
				axisFontSize: '11px',
				yAxisLabelSize: '11px',
				showAllMonths: true,
				legendBelow: true
			};
		}
		return {
			titleY: -45,
			subtitleY: -22,
			titleFontSize: '17px',
			subtitleFontSize: '13px',
			iconRadius: 45,
			axisFontSize: '13px',
			yAxisLabelSize: '13px',
			showAllMonths: true,
			legendBelow: false
		};
	}

	function getTitleCenterX() {
		const containerWidth = svgContainer?.clientWidth || 600;
		if (containerWidth < 768) {
			return (svgWidth / 2) - margin.left;
		}
		return width / 2;
	}

	// Climate-themed color palette
	const colors = {
		historical: '#64748b',   // Slate gray for historical baseline
		ssp126: '#f59e0b',       // Amber for low emissions
		ssp585: '#b91c1c'        // Deep red for high emissions
	};

	const legendLabels = {
		historical: 'Historical (1981-2010)',
		ssp126: 'Low emissions',
		ssp585: 'High emissions'
	};

	const monthNames = [
		'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
		'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
	];

	const daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

	onMount(() => {
		margin = getResponsiveMargin();
		const containerStyles = getComputedStyle(svgContainer);
		const paddingLeft = parseFloat(containerStyles.paddingLeft) || 0;
		const paddingRight = parseFloat(containerStyles.paddingRight) || 0;
		svgWidth = svgContainer.clientWidth - paddingLeft - paddingRight;
		const containerHeight = svgWidth < 480 ? 320 : svgWidth < 768 ? 360 : 400;
		width = svgWidth - margin.left - margin.right;
		height = containerHeight - margin.top - margin.bottom;

		svg = d3
			.select(svgContainer)
			.append('svg')
			.attr('width', svgWidth)
			.attr('height', containerHeight)
			.append('g')
			.attr('transform', `translate(${margin.left},${margin.top})`);

		tooltip = d3
			.select(svgContainer)
			.append('div')
			.attr('class', 'chart-tooltip')
			.style('opacity', 0);

		renderChart();
	});

	function renderChart() {
		if (!svg) return;
		svg.selectAll('*').remove();

		if (!appState.selectedLocation) {
			renderPlaceholder();
		} else {
			renderTemperatureChart();
		}
	}

	function renderPlaceholder() {
		if (!svg) return;

		const sizes = getResponsiveSizes();
		const centerX = getTitleCenterX();

		svg
			.append('text')
			.attr('x', centerX)
			.attr('y', sizes.titleY)
			.attr('text-anchor', 'middle')
			.style('font-size', sizes.titleFontSize)
			.style('font-weight', '600')
			.style('fill', '#0A565E')
			.text('Temperature Seasonality');

		svg
			.append('text')
			.attr('x', centerX)
			.attr('y', sizes.subtitleY)
			.attr('text-anchor', 'middle')
			.style('font-size', sizes.subtitleFontSize)
			.style('font-weight', '400')
			.style('fill', '#6c757d')
			.text('Select a location on the map to view data');

		const iconGroup = svg
			.append('g')
			.attr('transform', `translate(${centerX}, ${height / 2 - 15})`);

		iconGroup
			.append('circle')
			.attr('cx', 0)
			.attr('cy', 0)
			.attr('r', sizes.iconRadius)
			.attr('fill', '#f8fafc')
			.attr('stroke', '#e2e8f0')
			.attr('stroke-width', 2);

		const iconColors = [colors.historical, colors.ssp126, colors.ssp585];
		const lineData = [
			[{ x: -25, y: 8 }, { x: -10, y: 5 }, { x: 5, y: 12 }, { x: 20, y: 2 }],
			[{ x: -25, y: 14 }, { x: -10, y: 10 }, { x: 5, y: 16 }, { x: 20, y: 8 }],
			[{ x: -25, y: 20 }, { x: -10, y: 16 }, { x: 5, y: 22 }, { x: 20, y: 14 }]
		];

		const iconLine = d3.line<{ x: number; y: number }>()
			.x(d => d.x)
			.y(d => d.y)
			.curve(d3.curveMonotoneX);

		lineData.forEach((data, i) => {
			iconGroup
				.append('path')
				.datum(data)
				.attr('fill', 'none')
				.attr('stroke', iconColors[i])
				.attr('stroke-width', 2.5)
				.attr('stroke-linecap', 'round')
				.attr('d', iconLine)
				.attr('opacity', 0.85);
		});

		lineData.forEach((data, i) => {
			iconGroup
				.append('circle')
				.attr('cx', data[3].x)
				.attr('cy', data[3].y)
				.attr('r', 3)
				.attr('fill', iconColors[i]);
		});

		svg
			.append('text')
			.attr('x', centerX)
			.attr('y', height / 2 + 50)
			.attr('text-anchor', 'middle')
			.style('font-size', '14px')
			.style('fill', '#6c757d')
			.text('Click on the map to select a location');
	}

	function renderTemperatureChart() {
		if (!svg || !appState.selectedLocation) return;

		const lat = appState.selectedLocation.lat;
		const lon = appState.selectedLocation.lon;
		const threshold = appState.temperature.threshold;
		const selectedPeriod = appState.temperature.years;

		// Get data for all series: historical + low & high emissions
		const historicalData = getLocationData('historical', '1981-2010', threshold, lat, lon);
		const ssp126Data = getLocationData('ssp126', selectedPeriod, threshold, lat, lon);
		const ssp585Data = getLocationData('ssp585', selectedPeriod, threshold, lat, lon);

		const historicalArr = historicalData ? monthlyToArray(historicalData) : null;
		const ssp126Arr = ssp126Data ? monthlyToArray(ssp126Data) : null;
		const ssp585Arr = ssp585Data ? monthlyToArray(ssp585Data) : null;

		// Check if we have any data
		if (!historicalArr && !ssp126Arr && !ssp585Arr) {
			renderNoData();
			return;
		}

		// Build chart data — convert days to percentage of month
		const toPercent = (val: number | null, monthIndex: number) =>
			val !== null ? (val / daysInMonth[monthIndex]) * 100 : null;

		const chartData = monthNames.map((month, i) => ({
			month: i + 1,
			monthName: month,
			historical: toPercent(historicalArr ? historicalArr[i] : null, i),
			ssp126: toPercent(ssp126Arr ? ssp126Arr[i] : null, i),
			ssp585: toPercent(ssp585Arr ? ssp585Arr[i] : null, i)
		}));

		// Scales
		const xScale = d3
			.scalePoint<number>()
			.domain(chartData.map(d => d.month))
			.range([0, width])
			.padding(0.5);

		const allValues = chartData.flatMap(d =>
			[d.historical, d.ssp126, d.ssp585].filter((v): v is number => v !== null)
		);

		const yMin = 0;
		const yMax = Math.min(100, (d3.max(allValues) || 100) + 5);

		const yScale = d3
			.scaleLinear()
			.domain([yMin, yMax])
			.range([height, 0]);

		// Grid lines
		svg!
			.append('g')
			.attr('class', 'grid')
			.selectAll('line')
			.data(yScale.ticks(6))
			.enter()
			.append('line')
			.attr('x1', 0)
			.attr('x2', width)
			.attr('y1', d => yScale(d))
			.attr('y2', d => yScale(d))
			.attr('stroke', '#e5e7eb')
			.attr('stroke-dasharray', '3,3');

		const sizes = getResponsiveSizes();

		// X axis
		const xAxis = svg!
			.append('g')
			.attr('class', 'x-axis')
			.attr('transform', `translate(0,${height})`)
			.call(
				d3
					.axisBottom(xScale)
					.tickFormat((d, i) => {
						if (!sizes.showAllMonths && i % 2 === 1) return '';
						return chartData.find(sd => sd.month === d)?.monthName || '';
					})
					.tickSize(0)
			);

		xAxis.select('.domain').attr('stroke', '#d1d5db');
		xAxis.selectAll('text')
			.attr('dy', '1em')
			.style('font-size', sizes.axisFontSize)
			.style('fill', '#6c757d');

		// Y axis
		const yAxis = svg!
			.append('g')
			.attr('class', 'y-axis')
			.call(
				d3.axisLeft(yScale)
					.ticks(6)
					.tickSize(-5)
			);

		yAxis.select('.domain').attr('stroke', '#d1d5db');
		yAxis.selectAll('text')
			.style('font-size', sizes.axisFontSize)
			.style('fill', '#6c757d');
		yAxis.selectAll('line').attr('stroke', '#d1d5db');

		// Y axis label
		svg!
			.append('text')
			.attr('transform', 'rotate(-90)')
			.attr('y', 0 - margin.left + 15)
			.attr('x', 0 - height / 2)
			.style('text-anchor', 'middle')
			.style('font-size', sizes.yAxisLabelSize)
			.style('fill', '#2c3e50')
			.style('font-weight', '500')
			.text(`% of days above ${threshold}°C`);

		// Line generators
		const lineKeys = ['historical', 'ssp126', 'ssp585'] as const;

		const lineGenerators: Record<string, d3.Line<any>> = {};
		for (const key of lineKeys) {
			lineGenerators[key] = d3
				.line<any>()
				.defined(d => d[key] !== null)
				.x(d => xScale(d.month)!)
				.y(d => yScale(d[key]))
				.curve(d3.curveMonotoneX);
		}

		// Dash patterns per line so overlapping lines stay distinguishable
		const dashPatterns: Record<string, string> = {
			historical: '',          // solid
			ssp126: '8,4',           // dashed
			ssp585: '3,3'            // dotted
		};

		const lineWidths: Record<string, number> = {
			historical: 3,
			ssp126: 2.5,
			ssp585: 2.5
		};

		// Draw lines
		lineKeys.forEach((key) => {
			const hasData = chartData.some(d => d[key] !== null);
			if (!hasData) return;

			svg!
				.append('path')
				.datum(chartData)
				.attr('fill', 'none')
				.attr('stroke', colors[key])
				.attr('stroke-width', lineWidths[key])
				.attr('stroke-linecap', 'round')
				.attr('stroke-linejoin', 'round')
				.attr('stroke-dasharray', dashPatterns[key])
				.attr('d', lineGenerators[key])
				.attr('opacity', 0)
				.transition()
				.duration(800)
				.ease(d3.easeQuadOut)
				.attr('opacity', 1);
		});

		// Data points
		lineKeys.forEach((key) => {
			svg!
				.selectAll(`.dot-${key}`)
				.data(chartData.filter(d => d[key] !== null))
				.enter()
				.append('circle')
				.attr('class', `dot-${key}`)
				.attr('cx', d => xScale(d.month)!)
				.attr('cy', d => yScale(d[key] as number))
				.attr('r', 0)
				.attr('fill', colors[key])
				.attr('stroke', 'white')
				.attr('stroke-width', 2)
				.transition()
				.delay(1000)
				.duration(300)
				.attr('r', 4);
		});

		// Vertical hover line
		const hoverLine = svg!
			.append('line')
			.attr('class', 'hover-line')
			.attr('y1', 0)
			.attr('y2', height)
			.attr('stroke', '#94a3b8')
			.attr('stroke-width', 1)
			.attr('stroke-dasharray', '4,4')
			.style('opacity', 0);

		// Hover dots
		const hoverDots = svg!
			.append('g')
			.attr('class', 'hover-dots')
			.style('opacity', 0);

		lineKeys.forEach((key) => {
			hoverDots
				.append('circle')
				.attr('class', `hover-dot-${key}`)
				.attr('r', 6)
				.attr('fill', colors[key])
				.attr('stroke', 'white')
				.attr('stroke-width', 2);
		});

		// Mouse overlay
		svg!
			.append('rect')
			.attr('class', 'overlay')
			.attr('width', width)
			.attr('height', height)
			.attr('fill', 'transparent')
			.style('cursor', 'crosshair')
			.on('mouseenter', () => {
				hoverLine.style('opacity', 1);
				hoverDots.style('opacity', 1);
				if (tooltip) tooltip.style('opacity', 1);
			})
			.on('mouseleave', () => {
				hoverLine.style('opacity', 0);
				hoverDots.style('opacity', 0);
				if (tooltip) tooltip.style('opacity', 0);
			})
			.on('mousemove', function(event) {
				const [mouseX] = d3.pointer(event);

				const monthPositions = chartData.map(d => ({
					month: d.month,
					x: xScale(d.month)!,
					data: d
				}));

				const closest = monthPositions.reduce((prev, curr) =>
					Math.abs(curr.x - mouseX) < Math.abs(prev.x - mouseX) ? curr : prev
				);

				hoverLine.attr('x1', closest.x).attr('x2', closest.x);

				lineKeys.forEach((key) => {
					const val = closest.data[key];
					if (val !== null) {
						hoverDots
							.select(`.hover-dot-${key}`)
							.attr('cx', closest.x)
							.attr('cy', yScale(val as number))
							.style('display', 'block');
					} else {
						hoverDots.select(`.hover-dot-${key}`).style('display', 'none');
					}
				});

				if (tooltip) {
					const rows = lineKeys
						.filter(key => closest.data[key] !== null)
						.map(key => `
							<div style="display: flex; align-items: center; gap: 8px;">
								<span style="width: 10px; height: 10px; border-radius: 50%; background: ${colors[key]};"></span>
								<span style="color: #6c757d; flex: 1;">${legendLabels[key]}</span>
								<span style="font-weight: 600;">${Math.round(closest.data[key] as number)}%</span>
							</div>
						`).join('');

					const tooltipHtml = `
						<div style="font-weight: 600; margin-bottom: 8px; font-size: 13px; border-bottom: 1px solid #e5e7eb; padding-bottom: 6px;">${closest.data.monthName}</div>
						<div style="display: flex; flex-direction: column; gap: 4px;">
							${rows}
						</div>
					`;

					const tooltipWidth = 200;
					const tooltipHeight = 140;
					const containerWidth = svgContainer.clientWidth;
					const containerStyles = getComputedStyle(svgContainer);
					const paddingLeft = parseFloat(containerStyles.paddingLeft) || 0;
					const paddingTop = parseFloat(containerStyles.paddingTop) || 0;

					const dataYPositions = lineKeys
						.filter(key => closest.data[key] !== null)
						.map(key => yScale(closest.data[key] as number));

					const minDataY = Math.min(...dataYPositions);
					const maxDataY = Math.max(...dataYPositions);

					const lineX = paddingLeft + closest.x + margin.left;
					let leftPos = lineX - tooltipWidth / 2;
					leftPos = Math.max(4, Math.min(leftPos, containerWidth - tooltipWidth - 4));

					const dotRadius = 8;
					let topPos = paddingTop + margin.top + minDataY - tooltipHeight - dotRadius;

					if (topPos < 4) {
						topPos = paddingTop + margin.top + maxDataY + dotRadius;
					}

					const containerRect = svgContainer.getBoundingClientRect();
					const maxTop = containerRect.height - tooltipHeight - 4;
					topPos = Math.max(4, Math.min(topPos, maxTop));

					tooltip
						.html(tooltipHtml)
						.style('left', `${leftPos}px`)
						.style('top', `${topPos}px`);
				}
			});

		// Chart title
		const centerX = getTitleCenterX();

		svg!
			.append('text')
			.attr('x', centerX)
			.attr('y', sizes.titleY)
			.attr('text-anchor', 'middle')
			.style('font-size', sizes.titleFontSize)
			.style('font-weight', '600')
			.style('fill', '#0A565E')
			.text(`% of days with maximum temperatures above ${threshold}°C per month`);

		const locationText = `${Math.abs(lat).toFixed(2)}\u00B0${lat >= 0 ? 'N' : 'S'}, ${Math.abs(lon).toFixed(2)}\u00B0${lon >= 0 ? 'E' : 'W'}`;

		svg!
			.append('text')
			.attr('x', centerX)
			.attr('y', sizes.subtitleY)
			.attr('text-anchor', 'middle')
			.style('font-size', sizes.subtitleFontSize)
			.style('font-weight', '400')
			.style('fill', '#6c757d')
			.text(`Location: ${locationText} | Period: ${appState.temperature.years}`);

		// Legend
		const legendData = [
			{ key: 'historical', label: legendLabels.historical },
			{ key: 'ssp126', label: legendLabels.ssp126 },
			{ key: 'ssp585', label: legendLabels.ssp585 }
		];

		if (sizes.legendBelow) {
			const legend = svg!
				.append('g')
				.attr('class', 'legend')
				.attr('transform', `translate(${centerX}, ${height + 30})`);

			const colWidth = Math.min(100, width / 2.2);
			const rowHeight = 16;

			legendData.forEach((item, i) => {
				const col = i % 2;
				const row = Math.floor(i / 2);
				const x = (col - 0.5) * colWidth;
				const y = row * rowHeight;

				const legendItem = legend
					.append('g')
					.attr('transform', `translate(${x}, ${y})`);

				legendItem
					.append('line')
					.attr('x1', -8)
					.attr('x2', 8)
					.attr('y1', 0)
					.attr('y2', 0)
					.attr('stroke', colors[item.key as keyof typeof colors])
					.attr('stroke-width', 2.5)
					.attr('stroke-linecap', 'round')
					.attr('stroke-dasharray', dashPatterns[item.key]);

				legendItem
					.append('text')
					.attr('x', 12)
					.attr('y', 0)
					.attr('dy', '0.35em')
					.style('font-size', '10px')
					.style('fill', '#2c3e50')
					.style('font-weight', '500')
					.text(item.label.replace('Historical (1981-2010)', 'Historic'));
			});
		} else {
			const legend = svg!
				.append('g')
				.attr('class', 'legend')
				.attr('transform', `translate(${width - 140}, 5)`);

			legend
				.append('rect')
				.attr('x', -10)
				.attr('y', -10)
				.attr('width', 160)
				.attr('height', legendData.length * 24 + 12)
				.attr('rx', 6)
				.attr('fill', 'rgba(255, 255, 255, 0.92)')
				.attr('stroke', '#e5e7eb')
				.attr('stroke-width', 1);

			legendData.forEach((item, i) => {
				const legendItem = legend
					.append('g')
					.attr('transform', `translate(0, ${i * 24})`);

				legendItem
					.append('line')
					.attr('x1', 0)
					.attr('x2', 20)
					.attr('y1', 6)
					.attr('y2', 6)
					.attr('stroke', colors[item.key as keyof typeof colors])
					.attr('stroke-width', 2.5)
					.attr('stroke-linecap', 'round')
					.attr('stroke-dasharray', dashPatterns[item.key]);

				legendItem
					.append('text')
					.attr('x', 28)
					.attr('y', 6)
					.attr('dy', '0.35em')
					.style('font-size', '11px')
					.style('fill', '#2c3e50')
					.style('font-weight', '500')
					.text(item.label);
			});
		}
	}

	function renderNoData() {
		if (!svg) return;
		const sizes = getResponsiveSizes();
		const centerX = getTitleCenterX();

		svg
			.append('text')
			.attr('x', centerX)
			.attr('y', sizes.titleY)
			.attr('text-anchor', 'middle')
			.style('font-size', sizes.titleFontSize)
			.style('font-weight', '600')
			.style('fill', '#0A565E')
			.text('No data available');

		svg
			.append('text')
			.attr('x', centerX)
			.attr('y', height / 2)
			.attr('text-anchor', 'middle')
			.style('font-size', '14px')
			.style('fill', '#6c757d')
			.text('No climate data found for this location. Try selecting a different grid cell.');
	}

	// Re-render when state changes
	$effect(() => {
		const locationLat = appState.selectedLocation?.lat;
		const locationLon = appState.selectedLocation?.lon;
		const threshold = appState.temperature.threshold;
		const monthStart = appState.temperature.months[0];
		const monthEnd = appState.temperature.months[1];
		const years = appState.temperature.years;
		const scenario = appState.temperature.scenario;
		const dataLoaded = appState.dataLoaded;

		if (svg) {
			renderChart();
		}
	});
</script>

<div class="chart-container" bind:this={svgContainer}></div>

<style>
	.chart-container {
		width: 100%;
		min-height: 400px;
		background: linear-gradient(180deg, #ffffff 0%, #fafafa 100%);
		padding: 24px;
		border-radius: 12px;
		box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
		border: 1px solid #e5e7eb;
		position: relative;
		box-sizing: border-box;
		overflow: hidden;
	}

	.chart-container :global(.chart-tooltip) {
		position: absolute;
		background: white;
		padding: 12px 16px;
		border-radius: 10px;
		box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
		border: 1px solid #e5e7eb;
		font-size: 12px;
		pointer-events: none;
		z-index: 100;
		transition: opacity 0.1s ease;
		min-width: 200px;
	}

	.chart-container :global(.x-axis text),
	.chart-container :global(.y-axis text) {
		font-family: system-ui, -apple-system, sans-serif;
	}

	@media (max-width: 768px) {
		.chart-container {
			padding: 16px;
			min-height: 350px;
			border-radius: 10px;
		}

		.chart-container :global(.chart-tooltip) {
			padding: 10px 12px;
			min-width: 170px;
			font-size: 11px;
		}
	}

	@media (max-width: 480px) {
		.chart-container {
			padding: 12px;
			min-height: 300px;
			border-radius: 8px;
		}

		.chart-container :global(.chart-tooltip) {
			padding: 8px 10px;
			min-width: 150px;
			font-size: 10px;
		}
	}
</style>
