<script lang="ts">
	import { getAppState, updateTemperature, resetToDefaults } from '$lib/stores/appState.svelte';
	import { MIN_THRESHOLD, MAX_THRESHOLD } from '$lib/services/climateData';

	const appState = getAppState();

	// Tooltip state
	let activeTooltip = $state<string | null>(null);

	// Tooltip content
	const tooltips = {
		temperature: 'Set the maximum temperature threshold. The map will show the number of days per year where the maximum daily temperature exceeds this value.',
		period: 'Climate projections are grouped into 30-year periods. Earlier periods have less uncertainty, later periods show more pronounced climate change effects.',
		scenario: 'Shared Socioeconomic Pathways (SSPs) represent different emission scenarios. SSP1-2.6 is low emissions, SSP3-7.0 is medium, and SSP5-8.5 is high emissions.',
		months: 'Select a range of months to focus your analysis on specific seasons or time periods within the year.'
	};

	function toggleTooltip(id: string) {
		activeTooltip = activeTooltip === id ? null : id;
	}

	// Month names for the range slider
	const monthNames = [
		'January', 'February', 'March', 'April', 'May', 'June',
		'July', 'August', 'September', 'October', 'November', 'December'
	];

	// Abbreviated month names for display
	const monthAbbreviations = [
		'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
		'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
	];

	// Ensure end month is always >= start month
	$effect(() => {
		if (appState.temperature.months[1] < appState.temperature.months[0]) {
			updateTemperature({ months: [appState.temperature.months[0], appState.temperature.months[0]] });
		}
	});

	// Clamp threshold on blur (not while typing)
	function clampThreshold() {
		const t = appState.temperature.threshold;
		if (isNaN(t) || t < MIN_THRESHOLD) {
			updateTemperature({ threshold: MIN_THRESHOLD });
		} else if (t > MAX_THRESHOLD) {
			updateTemperature({ threshold: MAX_THRESHOLD });
		}
	}

	// Calculate slider range position and width as percentages
	const rangeLeftPercent = $derived(((appState.temperature.months[0] - 1) / 11) * 100);
	const rangeWidthPercent = $derived(((appState.temperature.months[1] - appState.temperature.months[0]) / 11) * 100);

	// Helper function to check if a tick is in the selected range
	function isTickInRange(index: number): boolean {
		return index >= appState.temperature.months[0] - 1 && index <= appState.temperature.months[1] - 1;
	}

	// Helper function to check if a month label is in the selected range
	function isMonthInRange(index: number): boolean {
		return index >= appState.temperature.months[0] - 1 && index <= appState.temperature.months[1] - 1;
	}

	// Custom dropdown state
	let yearsDropdownOpen = $state(false);
	let scenarioDropdownOpen = $state(false);

	const yearsOptions = [
		{ value: '2036-2065' as const, label: '2036-2065' },
		{ value: '2066-2095' as const, label: '2066-2095' }
	];

	const scenarioOptions = [
		{ value: 'ssp126' as const, label: 'SSP1-2.6', description: 'Low emissions' },
		{ value: 'ssp370' as const, label: 'SSP3-7.0', description: 'Medium emissions' },
		{ value: 'ssp585' as const, label: 'SSP5-8.5', description: 'High emissions' }
	];

	function selectYears(value: typeof appState.temperature.years) {
		updateTemperature({ years: value });
		yearsDropdownOpen = false;
	}

	function selectScenario(value: typeof appState.temperature.scenario) {
		updateTemperature({ scenario: value });
		scenarioDropdownOpen = false;
	}

	// Get current scenario label
	const currentScenarioLabel = $derived(
		scenarioOptions.find(o => o.value === appState.temperature.scenario)?.label || appState.temperature.scenario
	);

	// Close dropdowns when clicking outside
	$effect(() => {
		function handleClickOutside(event: MouseEvent) {
			const target = event.target as HTMLElement;
			if (!target.closest('.custom-select')) {
				yearsDropdownOpen = false;
				scenarioDropdownOpen = false;
			}
		}

		if (yearsDropdownOpen || scenarioDropdownOpen) {
			document.addEventListener('click', handleClickOutside);
			return () => document.removeEventListener('click', handleClickOutside);
		}
	});
</script>

<div class="user-input-container">
	<!-- Header Section -->
	<div class="section-header">
		<h2 class="main-question">How often do maximum temperature thresholds occur?</h2>
		<p class="subtitle">Configure your climate query to analyze maximum temperature patterns</p>
		<button class="reset-btn" onclick={() => resetToDefaults()}>
			<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
				<path d="M3 3v5h5"/>
			</svg>
			Reset to defaults
		</button>
	</div>

	<!-- Sections 1 & 2: Side by side -->
	<div class="sections-row">
		<!-- Section 1: Temperature Threshold (Primary) -->
		<div class="input-section primary">
			<div class="section-header-inline">
				<div class="section-number">1</div>
				<div class="section-content">
					<div class="label-with-tooltip">
						<span class="section-label">Temperature threshold</span>
						<button class="info-link" onclick={() => toggleTooltip('temperature')}>&#9432;</button>
						{#if activeTooltip === 'temperature'}
							<div class="tooltip">{tooltips.temperature}</div>
						{/if}
					</div>
					<p class="section-description">Number of days per year with maximum temperature above</p>
				</div>
			</div>

			<div class="input-row">
				<div class="input-group">
					<label for="threshold">Threshold ({MIN_THRESHOLD}-{MAX_THRESHOLD}°C)</label>
					<input
						id="threshold"
						type="number"
						bind:value={appState.temperature.threshold}
						min={MIN_THRESHOLD}
						max={MAX_THRESHOLD}
						step="1"
						onblur={clampThreshold}
					/>
				</div>
			</div>
		</div>

		<!-- Section 2: Time Period & Scenario -->
		<div class="input-section secondary">
			<div class="section-header-inline">
				<div class="section-number">2</div>
				<div class="section-content">
					<div class="label-with-tooltip">
						<span class="section-label">Future projection</span>
						<button class="info-link" onclick={() => toggleTooltip('period')}>&#9432;</button>
						{#if activeTooltip === 'period'}
							<div class="tooltip">{tooltips.period}</div>
						{/if}
					</div>
					<p class="section-description">Select period and emission scenario</p>
				</div>
			</div>

			<div class="input-row">
				<div class="input-group compact">
					<label for="period-select">Period</label>
					<div class="custom-select" class:open={yearsDropdownOpen}>
						<button
							id="period-select"
							type="button"
							class="select-trigger"
							onclick={() => { yearsDropdownOpen = !yearsDropdownOpen; scenarioDropdownOpen = false; }}
							aria-haspopup="listbox"
							aria-expanded={yearsDropdownOpen}
						>
							<span>{appState.temperature.years}</span>
							<svg class="select-arrow" class:rotated={yearsDropdownOpen} width="10" height="6" viewBox="0 0 12 8" fill="none">
								<path d="M1 1.5L6 6.5L11 1.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
							</svg>
						</button>
						{#if yearsDropdownOpen}
							<div class="select-dropdown">
								{#each yearsOptions as option}
									<button
										type="button"
										class="select-option"
										class:selected={appState.temperature.years === option.value}
										onclick={() => selectYears(option.value)}
									>
										{option.label}
									</button>
								{/each}
							</div>
						{/if}
					</div>
				</div>
				<div class="input-group compact">
					<label>
						Scenario
						<button class="info-link" onclick={() => toggleTooltip('scenario')}>&#9432;</button>
						{#if activeTooltip === 'scenario'}
							<div class="tooltip">{tooltips.scenario}</div>
						{/if}
					</label>
					<div class="custom-select" class:open={scenarioDropdownOpen}>
						<button
							type="button"
							class="select-trigger"
							onclick={() => { scenarioDropdownOpen = !scenarioDropdownOpen; yearsDropdownOpen = false; }}
							aria-haspopup="listbox"
							aria-expanded={scenarioDropdownOpen}
						>
							<span>{currentScenarioLabel}</span>
							<svg class="select-arrow" class:rotated={scenarioDropdownOpen} width="10" height="6" viewBox="0 0 12 8" fill="none">
								<path d="M1 1.5L6 6.5L11 1.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
							</svg>
						</button>
						{#if scenarioDropdownOpen}
							<div class="select-dropdown">
								{#each scenarioOptions as option}
									<button
										type="button"
										class="select-option"
										class:selected={appState.temperature.scenario === option.value}
										onclick={() => selectScenario(option.value)}
									>
										<span>{option.label}</span>
										<span class="option-desc">{option.description}</span>
									</button>
								{/each}
							</div>
						{/if}
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Section 3: Months (Tertiary) -->
	<div class="input-section tertiary">
		<div class="section-header-inline">
			<div class="section-number">3</div>
			<div class="section-content">
				<div class="label-with-tooltip">
					<span class="section-label">Select months</span>
					<button class="info-link" onclick={() => toggleTooltip('months')}>&#9432;</button>
					{#if activeTooltip === 'months'}
						<div class="tooltip">{tooltips.months}</div>
					{/if}
				</div>
				<p class="section-description">Choose which months to include in the analysis</p>
			</div>
		</div>

		<div class="month-slider">
			<div class="slider-track"></div>
			<div class="slider-ticks">
				{#each monthNames as _, i}
					<div class="tick" class:active={isTickInRange(i)} style="left: {(i / 11) * 100}%"></div>
				{/each}
			</div>
			<div class="slider-range" style="left: {rangeLeftPercent}%; width: {rangeWidthPercent}%"></div>
			<input
				type="range"
				min="1"
				max="12"
				bind:value={appState.temperature.months[0]}
				class="slider-input slider-input-min"
				aria-label="Start month"
			/>
			<input
				type="range"
				min="1"
				max="12"
				bind:value={appState.temperature.months[1]}
				class="slider-input slider-input-max"
				aria-label="End month"
			/>
		</div>
		<div class="month-labels">
			{#each monthAbbreviations as month, i}
				<span class="month-label" class:selected={isMonthInRange(i)} style="left: {(i / 11) * 100}%">{month}</span>
			{/each}
		</div>
	</div>
</div>

<style>
	.user-input-container {
		margin-bottom: 2rem;
		padding: 1.5rem;
		background: white;
		border-radius: 10px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
		border: 1px solid #e9ecef;
	}

	/* Header Section */
	.section-header {
		margin-bottom: 1.25rem;
		text-align: center;
		padding-bottom: 1rem;
		border-bottom: 2px solid #f0f4f8;
	}

	.main-question {
		font-size: 1.375rem;
		font-weight: 700;
		color: #1a2332;
		margin: 0 0 0.25rem 0;
		line-height: 1.3;
	}

	.subtitle {
		font-size: 0.8125rem;
		color: #6c757d;
		font-weight: 400;
		margin: 0;
	}

	/* Sections Row - for side by side layout */
	.sections-row {
		display: flex;
		gap: 1rem;
		margin-bottom: 1rem;
		flex-wrap: wrap;
	}

	.sections-row .input-section {
		flex: 1;
		min-width: 300px;
		margin-bottom: 0;
		z-index: 10;
	}

	/* Input Sections with Visual Hierarchy */
	.input-section {
		margin-bottom: 1rem;
		border-radius: 8px;
		transition: all 0.3s ease;
		position: relative;
	}

	.input-section:focus-within {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
	}

	.input-section.primary {
		border: 2px solid #0A565E;
		background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
		padding: 1.25rem;
		box-shadow: 0 2px 8px rgba(10, 86, 94, 0.12);
	}

	.input-section.secondary {
		border: 2px solid #D6DEE8;
		background: white;
		padding: 1.125rem;
		box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
	}

	.input-section.tertiary {
		border: 1px solid #D6DEE8;
		background: white;
		padding: 1.125rem;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
		z-index: 1;
	}

	/* Section Header Inline */
	.section-header-inline {
		display: flex;
		gap: 0.75rem;
		margin-bottom: 0.875rem;
		align-items: flex-start;
	}

	.section-number {
		width: 32px;
		height: 32px;
		border-radius: 50%;
		background: linear-gradient(135deg, #0A565E 0%, #084850 100%);
		color: white;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: 700;
		font-size: 1rem;
		flex-shrink: 0;
		box-shadow: 0 2px 6px rgba(10, 86, 94, 0.3);
	}

	.section-content {
		flex: 1;
	}

	.section-label {
		font-size: 0.9375rem;
		font-weight: 600;
		color: #2c3e50;
		margin: 0 0 0.125rem 0;
		display: block;
	}

	.section-description {
		font-size: 0.75rem;
		color: #6c757d;
		margin: 0;
		font-weight: 400;
	}

	.input-row {
		display: flex;
		gap: 1rem;
		align-items: flex-end;
		flex-wrap: wrap;
		margin-top: 0.5rem;
	}

	.input-group {
		display: flex;
		flex-direction: column;
		gap: 0.375rem;
		flex: 0 0 auto;
		transition: opacity 0.3s, visibility 0.3s;
	}

	.input-group:first-child {
		flex: 1;
		min-width: 260px;
		max-width: 100%;
	}

	.input-group.compact {
		flex: 1;
		min-width: 130px;
		max-width: 100%;
	}

	.option-desc {
		font-size: 0.7rem;
		color: #6c757d;
		margin-left: 0.5rem;
	}

	label {
		font-size: 0.75rem;
		color: #495057;
		font-weight: 600;
		margin: 0;
		letter-spacing: 0.01em;
		display: flex;
		align-items: flex-end;
	}

	input[type='number'] {
		padding: 0.375rem 0.5rem;
		border: 1px solid #D6DEE8;
		border-radius: 6px;
		font-size: 0.875rem;
		line-height: 1.5;
		background: white;
		cursor: text;
		transition: all 0.2s ease;
		font-weight: 500;
		color: #2c3e50;
		max-width: 90px;
		font-family: inherit;
		height: 2.125rem;
	}

	input[type='number']:hover {
		border-color: #B5C4D3;
		background: #FAFBFC;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
	}

	input[type='number']:focus {
		outline: none;
		border-color: #0A565E;
		background: white;
		box-shadow: 0 0 0 3px rgba(10, 86, 94, 0.12), 0 1px 3px rgba(0, 0, 0, 0.05);
	}

	/* Custom Select Styles */
	.custom-select {
		position: relative;
		width: 100%;
	}

	.select-trigger {
		width: 100%;
		padding: 0.375rem 0.5rem;
		padding-right: 2rem;
		border: 1px solid #D6DEE8;
		border-radius: 6px;
		font-size: 0.875rem;
		line-height: 1.5;
		background: white;
		cursor: pointer;
		transition: all 0.2s ease;
		font-weight: 500;
		color: #2c3e50;
		text-align: left;
		display: flex;
		align-items: center;
		justify-content: space-between;
		font-family: inherit;
		height: 2.125rem;
	}

	.select-trigger:hover {
		border-color: #B5C4D3;
		background: #FAFBFC;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
	}

	.custom-select.open .select-trigger {
		border-color: #0A565E;
		box-shadow: 0 0 0 3px rgba(10, 86, 94, 0.12), 0 1px 3px rgba(0, 0, 0, 0.05);
	}

	.select-arrow {
		position: absolute;
		right: 0.625rem;
		color: #084850;
		transition: transform 0.2s ease;
		pointer-events: none;
		width: 10px;
		height: auto;
	}

	.select-arrow.rotated {
		transform: rotate(180deg);
	}

	.select-dropdown {
		position: absolute;
		top: calc(100% + 4px);
		left: 0;
		background: white;
		border: 1px solid #D6DEE8;
		border-radius: 6px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		z-index: 100;
		overflow: hidden;
		animation: dropdownSlide 0.2s ease;
		width: 100%;
	}

	@keyframes dropdownSlide {
		from {
			opacity: 0;
			transform: translateY(-8px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.select-option {
		width: 100%;
		padding: 0.375rem 0.5rem;
		border: none;
		background: white;
		cursor: pointer;
		transition: all 0.15s ease;
		font-weight: 500;
		color: #2c3e50;
		text-align: left;
		font-size: 0.875rem;
		line-height: 1.3;
	}

	.select-option:hover {
		background: rgba(192, 255, 192, 0.5);
		color: #084850;
	}

	.select-option.selected {
		background: rgba(192, 255, 192, 0.6);
		color: #084850;
		font-weight: 600;
	}

	.select-option.selected:hover {
		background: rgba(192, 255, 192, 0.8);
	}

	.month-slider {
		position: relative;
		height: 30px;
		margin: 0.25rem 0;
	}

	.slider-track {
		position: absolute;
		top: 20px;
		transform: translateY(-50%);
		width: 100%;
		height: 4px;
		background: #D6DEE8;
		border-radius: 2px;
	}

	.slider-ticks {
		position: absolute;
		top: 0;
		width: 100%;
		height: 100%;
		pointer-events: none;
		z-index: 1;
	}

	.tick {
		position: absolute;
		top: 20px;
		transform: translate(-50%, -50%);
		width: 8px;
		height: 8px;
		background: #D6DEE8;
		border: 1px solid #B5C4D3;
		border-radius: 50%;
		transition: all 0.2s ease;
	}

	.tick.active {
		background: #0A565E;
		border-color: #084850;
		transform: translate(-50%, -50%) scale(1.2);
	}

	.slider-range {
		position: absolute;
		top: 20px;
		transform: translateY(-50%);
		height: 4px;
		background: #0A565E;
		border-radius: 2px;
		pointer-events: none;
		z-index: 2;
	}

	.slider-input {
		position: absolute;
		top: 20px;
		transform: translateY(-50%);
		width: calc(100% + 20px);
		margin-left: -10px;
		margin-right: -10px;
		padding: 0;
		pointer-events: none;
		-webkit-appearance: none;
		appearance: none;
		background: transparent;
		z-index: 3;
		box-sizing: border-box;
	}

	.slider-input::-webkit-slider-thumb {
		-webkit-appearance: none;
		appearance: none;
		width: 22px;
		height: 22px;
		border-radius: 50%;
		background: white;
		cursor: grab;
		pointer-events: auto;
		border: 3px solid #084850;
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
		margin-top: -9px;
		transition: all 0.15s ease;
	}

	.slider-input::-webkit-slider-thumb:hover {
		border-color: #5A85BE;
		transform: scale(1.15);
		box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
	}

	.slider-input::-webkit-slider-thumb:active {
		cursor: grabbing;
		border-color: #084850;
		transform: scale(1.05);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
	}

	.slider-input::-moz-range-thumb {
		width: 22px;
		height: 22px;
		border-radius: 50%;
		background: white;
		cursor: grab;
		pointer-events: auto;
		border: 3px solid #084850;
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
		transition: all 0.15s ease;
	}

	.slider-input::-moz-range-thumb:hover {
		border-color: #5A85BE;
		transform: scale(1.15);
		box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
	}

	.slider-input::-moz-range-thumb:active {
		cursor: grabbing;
		border-color: #084850;
		transform: scale(1.05);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
	}

	.slider-input::-webkit-slider-runnable-track {
		background: transparent;
		height: 4px;
		border: none;
		width: 100%;
		padding: 0;
		margin: 0;
	}

	.slider-input::-moz-range-track {
		background: transparent;
		height: 4px;
		border: none;
		width: 100%;
		padding: 0;
		margin: 0;
	}

	.slider-input:focus {
		outline: none;
	}

	.slider-input:focus::-webkit-slider-thumb {
		box-shadow: 0 0 0 3px rgba(10, 86, 94, 0.25), 0 2px 6px rgba(0, 0, 0, 0.15);
		outline: none;
	}

	.slider-input:focus::-moz-range-thumb {
		box-shadow: 0 0 0 3px rgba(10, 86, 94, 0.25), 0 2px 6px rgba(0, 0, 0, 0.15);
		outline: none;
	}

	.month-labels {
		position: relative;
		margin-top: 0.375rem;
		font-size: 0.6875rem;
		height: 1rem;
	}

	.month-label {
		position: absolute;
		transform: translateX(-50%);
		color: #9AA6B2;
		white-space: nowrap;
		font-weight: 400;
		letter-spacing: 0.02em;
		transition: all 0.2s ease;
	}

	.month-label.selected {
		color: #084850;
		font-weight: 700;
		font-size: 0.75rem;
	}

	/* Reset Button */
	.reset-btn {
		display: inline-flex;
		align-items: center;
		gap: 0.375rem;
		margin-top: 0.75rem;
		padding: 0.375rem 0.75rem;
		background: transparent;
		border: 1px solid #D6DEE8;
		border-radius: 6px;
		color: #6c757d;
		font-size: 0.75rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.reset-btn:hover {
		background: #f8f9fa;
		border-color: #0A565E;
		color: #0A565E;
	}

	.reset-btn svg {
		flex-shrink: 0;
	}

	/* Label with Tooltip */
	.label-with-tooltip {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		position: relative;
	}

	.info-link {
		padding: 0;
		background: transparent;
		border: none;
		color: #9AA6B2;
		cursor: pointer;
		transition: color 0.2s ease;
		font-size: 0.875rem;
		line-height: 1;
	}

	.info-link:hover {
		color: #0A565E;
	}

	.tooltip {
		position: absolute;
		top: calc(100% + 8px);
		left: 0;
		z-index: 1000;
		width: 280px;
		padding: 0.75rem;
		background: #1a2332;
		color: white;
		font-size: 0.75rem;
		font-weight: 400;
		line-height: 1.5;
		border-radius: 8px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
		animation: tooltipFade 0.2s ease;
	}

	.tooltip::before {
		content: '';
		position: absolute;
		top: -6px;
		left: 16px;
		width: 12px;
		height: 12px;
		background: #1a2332;
		transform: rotate(45deg);
	}

	@keyframes tooltipFade {
		from {
			opacity: 0;
			transform: translateY(-4px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	/* Mobile Responsive Styles */
	@media (max-width: 768px) {
		.user-input-container {
			padding: 1rem;
			margin-bottom: 1rem;
		}

		.section-header {
			margin-bottom: 1rem;
			padding-bottom: 0.75rem;
		}

		.main-question {
			font-size: 1.125rem;
		}

		.subtitle {
			font-size: 0.75rem;
		}

		.sections-row {
			flex-direction: column;
			gap: 0.75rem;
		}

		.sections-row .input-section {
			min-width: 100%;
		}

		.input-section.primary,
		.input-section.secondary,
		.input-section.tertiary {
			padding: 1rem;
		}

		.section-header-inline {
			gap: 0.5rem;
			margin-bottom: 0.75rem;
		}

		.section-number {
			width: 28px;
			height: 28px;
			font-size: 0.875rem;
		}

		.section-label {
			font-size: 0.875rem;
		}

		.section-description {
			font-size: 0.6875rem;
		}

		.input-row {
			flex-direction: column;
			gap: 0.75rem;
		}

		.input-group:first-child {
			min-width: 100%;
		}

		.input-group.compact {
			min-width: 100%;
		}

		input[type='number'] {
			max-width: 100%;
			width: 100%;
		}

		/* Tooltip adjustments for mobile */
		.tooltip {
			width: calc(100vw - 80px);
			max-width: 280px;
			left: -10px;
			font-size: 0.6875rem;
		}

		/* Month slider adjustments */
		.month-labels {
			font-size: 0.5625rem;
		}

		.month-label.selected {
			font-size: 0.625rem;
		}

		.slider-input::-webkit-slider-thumb {
			width: 20px;
			height: 20px;
			margin-top: -8px;
		}

		.slider-input::-moz-range-thumb {
			width: 20px;
			height: 20px;
		}
	}

	@media (max-width: 480px) {
		.user-input-container {
			padding: 0.75rem;
			border-radius: 8px;
		}

		.main-question {
			font-size: 1rem;
		}

		.input-section.primary,
		.input-section.secondary,
		.input-section.tertiary {
			padding: 0.75rem;
			border-radius: 6px;
		}

		.section-number {
			width: 24px;
			height: 24px;
			font-size: 0.75rem;
		}

		.section-label {
			font-size: 0.8125rem;
		}

		label {
			font-size: 0.6875rem;
		}

		.select-trigger,
		input[type='number'] {
			font-size: 0.8125rem;
			height: 2rem;
			padding: 0.25rem 0.375rem;
		}

		.select-option {
			font-size: 0.8125rem;
			padding: 0.25rem 0.375rem;
		}

		.reset-btn {
			font-size: 0.6875rem;
			padding: 0.25rem 0.5rem;
		}

		/* Hide some month labels on very small screens */
		.month-label:nth-child(2),
		.month-label:nth-child(4),
		.month-label:nth-child(6),
		.month-label:nth-child(8),
		.month-label:nth-child(10),
		.month-label:nth-child(12) {
			display: none;
		}

		.tick {
			width: 6px;
			height: 6px;
		}
	}
</style>
