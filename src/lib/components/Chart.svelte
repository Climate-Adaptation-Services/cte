<script lang="ts">
	import { onMount } from 'svelte';
	import { getAppState } from '$lib/stores/appState.svelte';
	import * as d3 from 'd3';

	const appState = getAppState();

	let svgContainer: HTMLDivElement;
	let svg: d3.Selection<SVGGElement, unknown, null, undefined> | null = null;
	let tooltip: d3.Selection<HTMLDivElement, unknown, null, undefined> | null = null;

	let margin = { top: 70, right: 30, bottom: 50, left: 65 };
	let width = 0;
	let height = 400;
	let svgWidth = 0; // Store full SVG width for centering titles

	// Responsive margin calculation
	function getResponsiveMargin() {
		const containerWidth = svgContainer?.clientWidth || 600;
		if (containerWidth < 480) {
			// Extra bottom margin for horizontal legend below chart
			return { top: 50, right: 15, bottom: 55, left: 45 };
		} else if (containerWidth < 768) {
			// Extra bottom margin for horizontal legend below chart
			return { top: 60, right: 20, bottom: 60, left: 55 };
		}
		return { top: 70, right: 30, bottom: 50, left: 65 };
	}

	// Responsive font sizes and positions
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

	// Calculate center x position for titles (centered in the white container/SVG)
	function getTitleCenterX() {
		// On mobile, center over the full SVG width (not just plot area)
		// Since the g element is translated by margin.left, we need to offset
		const containerWidth = svgContainer?.clientWidth || 600;
		if (containerWidth < 768) {
			// Center over full container: (svgWidth / 2) - margin.left
			return (svgWidth / 2) - margin.left;
		}
		// Desktop: center over the plot area
		return width / 2;
	}

	// Climate-themed color palette (cool to warm = past to future warming)
	const colors = {
		era5: '#64748b',      // Slate gray for historical baseline
		upcoming: '#f59e0b',  // Amber for near future (slight warming)
		mid: '#ea580c',       // Orange for mid-century (moderate warming)
		end: '#b91c1c'        // Deep red for end-century (significant warming)
	};

	const legendLabels = {
		era5: 'Historical (ERA5)',
		upcoming: '2011-2040',
		mid: '2041-2070',
		end: '2071-2100'
	};

	// Month names for title
	const monthNames = [
		'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
		'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
	];

	onMount(() => {
		// Create SVG with responsive margins
		margin = getResponsiveMargin();
		// Get container padding to calculate available SVG width
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

		// Create tooltip
		tooltip = d3
			.select(svgContainer)
			.append('div')
			.attr('class', 'chart-tooltip')
			.style('opacity', 0);

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

		const sizes = getResponsiveSizes();
		const centerX = getTitleCenterX();

		// Add placeholder title
		svg
			.append('text')
			.attr('x', centerX)
			.attr('y', sizes.titleY)
			.attr('text-anchor', 'middle')
			.style('font-size', sizes.titleFontSize)
			.style('font-weight', '600')
			.style('fill', '#111827')
			.text('Temperature Seasonality');

		svg
			.append('text')
			.attr('x', centerX)
			.attr('y', sizes.subtitleY)
			.attr('text-anchor', 'middle')
			.style('font-size', sizes.subtitleFontSize)
			.style('font-weight', '400')
			.style('fill', '#6b7280')
			.text('Select a location on the map to view data');

		// Professional chart icon using accent colors
		const iconGroup = svg
			.append('g')
			.attr('transform', `translate(${centerX}, ${height / 2 - 15})`);

		// Icon background circle
		iconGroup
			.append('circle')
			.attr('cx', 0)
			.attr('cy', 0)
			.attr('r', sizes.iconRadius)
			.attr('fill', '#f8fafc')
			.attr('stroke', '#e2e8f0')
			.attr('stroke-width', 2);

		// Mini chart lines (simplified line chart icon)
		const iconColors = [colors.era5, colors.upcoming, colors.mid, colors.end];
		const lineData = [
			[{ x: -25, y: 8 }, { x: -10, y: 5 }, { x: 5, y: 12 }, { x: 20, y: 2 }],
			[{ x: -25, y: 12 }, { x: -10, y: 8 }, { x: 5, y: 15 }, { x: 20, y: 6 }],
			[{ x: -25, y: 16 }, { x: -10, y: 12 }, { x: 5, y: 18 }, { x: 20, y: 10 }],
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

		// Small dots at the end of each line
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
			.style('fill', '#6b7280')
			.text('Click on the map to select a location');
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

		const yMin = d3.min(sampleData, d => Math.min(d.era5, d.upcoming, d.mid, d.end))! - 2;
		const yMax = d3.max(sampleData, d => Math.max(d.era5, d.upcoming, d.mid, d.end))! + 2;

		const yScale = d3
			.scaleLinear()
			.domain([yMin, yMax])
			.range([height, 0]);

		// Add horizontal grid lines
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

		// Get responsive sizes for axis
		const sizes = getResponsiveSizes();

		// Add X axis
		const xAxis = svg!
			.append('g')
			.attr('class', 'x-axis')
			.attr('transform', `translate(0,${height})`)
			.call(
				d3
					.axisBottom(xScale)
					.tickFormat((d, i) => {
						// On small screens, show only odd months (Jan, Mar, May, etc.)
						if (!sizes.showAllMonths && i % 2 === 1) return '';
						return sampleData.find(sd => sd.month === d)?.monthName || '';
					})
					.tickSize(0)
			);

		xAxis.select('.domain').attr('stroke', '#d1d5db');
		xAxis.selectAll('text')
			.attr('dy', '1em')
			.style('font-size', sizes.axisFontSize)
			.style('fill', '#6b7280');

		// Add Y axis
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
			.style('fill', '#6b7280');
		yAxis.selectAll('line').attr('stroke', '#d1d5db');

		// Add Y axis label
		const yAxisLabel = 'Max Temp (°C)';

		svg!
			.append('text')
			.attr('transform', 'rotate(-90)')
			.attr('y', 0 - margin.left + 15)
			.attr('x', 0 - height / 2)
			.style('text-anchor', 'middle')
			.style('font-size', sizes.yAxisLabelSize)
			.style('fill', '#374151')
			.style('font-weight', '500')
			.text(yAxisLabel);

		// Line generators with smooth curves
		const lineGenerators = {
			era5: d3
				.line<any>()
				.x(d => xScale(d.month)!)
				.y(d => yScale(d.era5))
				.curve(d3.curveMonotoneX),
			upcoming: d3
				.line<any>()
				.x(d => xScale(d.month)!)
				.y(d => yScale(d.upcoming))
				.curve(d3.curveMonotoneX),
			mid: d3
				.line<any>()
				.x(d => xScale(d.month)!)
				.y(d => yScale(d.mid))
				.curve(d3.curveMonotoneX),
			end: d3
				.line<any>()
				.x(d => xScale(d.month)!)
				.y(d => yScale(d.end))
				.curve(d3.curveMonotoneX)
		};

		// Draw lines with animation
		const lineKeys = ['era5', 'upcoming', 'mid', 'end'] as const;

		lineKeys.forEach((key) => {
			const lineGen = lineGenerators[key];
			const path = svg!
				.append('path')
				.datum(sampleData)
				.attr('fill', 'none')
				.attr('stroke', colors[key])
				.attr('stroke-width', 2.5)
				.attr('stroke-linecap', 'round')
				.attr('stroke-linejoin', 'round')
				.attr('d', lineGen);

			// Animate line drawing
			const totalLength = path.node()?.getTotalLength() || 0;
			path
				.attr('stroke-dasharray', `${totalLength} ${totalLength}`)
				.attr('stroke-dashoffset', totalLength)
				.transition()
				.duration(1000)
				.ease(d3.easeQuadOut)
				.attr('stroke-dashoffset', 0);
		});

		// Add static data points (small, no individual hover)
		lineKeys.forEach((key) => {
			const yKey = key as keyof typeof sampleData[0];

			svg!
				.selectAll(`.dot-${key}`)
				.data(sampleData)
				.enter()
				.append('circle')
				.attr('class', `dot-${key}`)
				.attr('cx', d => xScale(d.month)!)
				.attr('cy', d => yScale(d[yKey] as number))
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

		// Hover dots (larger, shown on hover)
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

		// Invisible overlay for mouse tracking
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

				// Find closest month
				const monthPositions = sampleData.map(d => ({
					month: d.month,
					x: xScale(d.month)!,
					data: d
				}));

				const closest = monthPositions.reduce((prev, curr) =>
					Math.abs(curr.x - mouseX) < Math.abs(prev.x - mouseX) ? curr : prev
				);

				// Update hover line position
				hoverLine.attr('x1', closest.x).attr('x2', closest.x);

				// Update hover dots positions
				lineKeys.forEach((key) => {
					const yKey = key as keyof typeof closest.data;
					hoverDots
						.select(`.hover-dot-${key}`)
						.attr('cx', closest.x)
						.attr('cy', yScale(closest.data[yKey] as number));
				});

				// Update tooltip
				if (tooltip) {
					const tooltipHtml = `
						<div style="font-weight: 600; margin-bottom: 8px; font-size: 13px; border-bottom: 1px solid #e5e7eb; padding-bottom: 6px;">${closest.data.monthName}</div>
						<div style="display: flex; flex-direction: column; gap: 4px;">
							<div style="display: flex; align-items: center; gap: 8px;">
								<span style="width: 10px; height: 10px; border-radius: 50%; background: ${colors.era5};"></span>
								<span style="color: #6b7280; flex: 1;">${legendLabels.era5}</span>
								<span style="font-weight: 600;">${closest.data.era5.toFixed(1)}°C</span>
							</div>
							<div style="display: flex; align-items: center; gap: 8px;">
								<span style="width: 10px; height: 10px; border-radius: 50%; background: ${colors.upcoming};"></span>
								<span style="color: #6b7280; flex: 1;">${legendLabels.upcoming}</span>
								<span style="font-weight: 600;">${closest.data.upcoming.toFixed(1)}°C</span>
							</div>
							<div style="display: flex; align-items: center; gap: 8px;">
								<span style="width: 10px; height: 10px; border-radius: 50%; background: ${colors.mid};"></span>
								<span style="color: #6b7280; flex: 1;">${legendLabels.mid}</span>
								<span style="font-weight: 600;">${closest.data.mid.toFixed(1)}°C</span>
							</div>
							<div style="display: flex; align-items: center; gap: 8px;">
								<span style="width: 10px; height: 10px; border-radius: 50%; background: ${colors.end};"></span>
								<span style="color: #6b7280; flex: 1;">${legendLabels.end}</span>
								<span style="font-weight: 600;">${closest.data.end.toFixed(1)}°C</span>
							</div>
						</div>
					`;

					// Calculate tooltip dimensions
					const tooltipWidth = 180;
					const tooltipHeight = 140;

					// Get container bounds
					const containerRect = svgContainer.getBoundingClientRect();
					const containerWidth = svgContainer.clientWidth;
					const containerStyles = getComputedStyle(svgContainer);
					const paddingLeft = parseFloat(containerStyles.paddingLeft) || 0;
					const paddingTop = parseFloat(containerStyles.paddingTop) || 0;

					// Get Y positions of all data points (in SVG coordinates)
					const dataYPositions = [
						yScale(closest.data.era5),
						yScale(closest.data.upcoming),
						yScale(closest.data.mid),
						yScale(closest.data.end)
					];
					const minDataY = Math.min(...dataYPositions); // Highest point (smallest Y)
					const maxDataY = Math.max(...dataYPositions); // Lowest point (largest Y)

					// Horizontal position: center tooltip on the hover line
					const lineX = paddingLeft + closest.x + margin.left;
					let leftPos = lineX - tooltipWidth / 2;
					// Clamp to container edges
					leftPos = Math.max(4, Math.min(leftPos, containerWidth - tooltipWidth - 4));

					// Vertical position: place tooltip above all data points
					const dotRadius = 8; // hover dot radius + some padding
					let topPos = paddingTop + margin.top + minDataY - tooltipHeight - dotRadius;

					// If tooltip would go above container, place it below the data points instead
					if (topPos < 4) {
						topPos = paddingTop + margin.top + maxDataY + dotRadius;
					}

					// Final clamp
					const maxTop = containerRect.height - tooltipHeight - 4;
					topPos = Math.max(4, Math.min(topPos, maxTop));

					tooltip
						.html(tooltipHtml)
						.style('left', `${leftPos}px`)
						.style('top', `${topPos}px`);
				}
			});

		// Chart title
		const titleText = 'Average Monthly Maximum Temperature';

		// Format location coordinates
		const lat = appState.selectedLocation?.lat;
		const lon = appState.selectedLocation?.lon;
		const locationText = lat && lon
			? `${Math.abs(lat).toFixed(2)}°${lat >= 0 ? 'N' : 'S'}, ${Math.abs(lon).toFixed(2)}°${lon >= 0 ? 'E' : 'W'}`
			: 'Selected Location';

		// Use sizes from earlier (already declared for axis)
		const centerX = getTitleCenterX();

		// Add main title
		svg!
			.append('text')
			.attr('x', centerX)
			.attr('y', sizes.titleY)
			.attr('text-anchor', 'middle')
			.style('font-size', sizes.titleFontSize)
			.style('font-weight', '600')
			.style('fill', '#111827')
			.text(titleText);

		// Add subtitle with location
		svg!
			.append('text')
			.attr('x', centerX)
			.attr('y', sizes.subtitleY)
			.attr('text-anchor', 'middle')
			.style('font-size', sizes.subtitleFontSize)
			.style('font-weight', '400')
			.style('fill', '#6b7280')
			.text(`Location: ${locationText}`);

		// Add legend (position depends on screen size)
		const legendData = [
			{ key: 'era5', label: legendLabels.era5 },
			{ key: 'upcoming', label: legendLabels.upcoming },
			{ key: 'mid', label: legendLabels.mid },
			{ key: 'end', label: legendLabels.end }
		];

		if (sizes.legendBelow) {
			// 2x2 grid legend below chart for mobile
			const legend = svg!
				.append('g')
				.attr('class', 'legend')
				.attr('transform', `translate(${centerX}, ${height + 30})`);

			const colWidth = Math.min(90, width / 2.2);
			const rowHeight = 16;

			legendData.forEach((item, i) => {
				const col = i % 2; // 0 or 1
				const row = Math.floor(i / 2); // 0 or 1
				const x = (col - 0.5) * colWidth; // Center the 2 columns
				const y = row * rowHeight;

				const legendItem = legend
					.append('g')
					.attr('transform', `translate(${x}, ${y})`)
					.style('cursor', 'pointer');

				legendItem
					.append('circle')
					.attr('cx', 0)
					.attr('cy', 0)
					.attr('r', 4)
					.attr('fill', colors[item.key as keyof typeof colors]);

				legendItem
					.append('text')
					.attr('x', 8)
					.attr('y', 0)
					.attr('dy', '0.35em')
					.style('font-size', '10px')
					.style('fill', '#4b5563')
					.style('font-weight', '500')
					.text(item.label.replace('Historical (ERA5)', 'Historic'));
			});
		} else {
			// Vertical legend at top right for desktop
			const legend = svg!
				.append('g')
				.attr('class', 'legend')
				.attr('transform', `translate(${width - 120}, 5)`);

			// Legend background (semi-transparent)
			legend
				.append('rect')
				.attr('x', -10)
				.attr('y', -10)
				.attr('width', 130)
				.attr('height', legendData.length * 24 + 12)
				.attr('rx', 6)
				.attr('fill', 'rgba(255, 255, 255, 0.92)')
				.attr('stroke', '#e5e7eb')
				.attr('stroke-width', 1);

			legendData.forEach((item, i) => {
				const legendItem = legend
					.append('g')
					.attr('transform', `translate(0, ${i * 24})`)
					.style('cursor', 'pointer');

				legendItem
					.append('line')
					.attr('x1', 0)
					.attr('x2', 20)
					.attr('y1', 6)
					.attr('y2', 6)
					.attr('stroke', colors[item.key as keyof typeof colors])
					.attr('stroke-width', 2.5)
					.attr('stroke-linecap', 'round');

				legendItem
					.append('circle')
					.attr('cx', 10)
					.attr('cy', 6)
					.attr('r', 3.5)
					.attr('fill', colors[item.key as keyof typeof colors])
					.attr('stroke', 'white')
					.attr('stroke-width', 1.5);

				legendItem
					.append('text')
					.attr('x', 28)
					.attr('y', 6)
					.attr('dy', '0.35em')
					.style('font-size', '11px')
					.style('fill', '#4b5563')
					.style('font-weight', '500')
					.text(item.label);
			});
		}
	}

	// Re-render when selectedLocation or temperature parameters change
	$effect(() => {
		// Watch all relevant state changes
		// For selectedLocation, we need to watch the actual lat/lon values, not just the object
		const locationLat = appState.selectedLocation?.lat;
		const locationLon = appState.selectedLocation?.lon;
		const threshold = appState.temperature.threshold;
		// For arrays, watch the individual elements
		const monthStart = appState.temperature.months[0];
		const monthEnd = appState.temperature.months[1];
		const years = appState.temperature.years;

		console.log('Chart $effect triggered', { locationLat, locationLon, threshold, monthStart, monthEnd, years });

		// Re-render chart whenever any of these change
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
		min-width: 180px;
	}

	.chart-container :global(.x-axis text),
	.chart-container :global(.y-axis text) {
		font-family: system-ui, -apple-system, sans-serif;
	}

	/* Mobile Responsive Styles */
	@media (max-width: 768px) {
		.chart-container {
			padding: 16px;
			min-height: 350px;
			border-radius: 10px;
		}

		.chart-container :global(.chart-tooltip) {
			padding: 10px 12px;
			min-width: 160px;
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
			min-width: 140px;
			font-size: 10px;
		}
	}
</style>
