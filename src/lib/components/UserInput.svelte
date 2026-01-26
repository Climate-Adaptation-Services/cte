<script lang="ts">
	import { getAppState, updateTemperature } from '$lib/stores/appState.svelte';

	const appState = getAppState();

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

	// Show/hide second threshold based on variable
	let showThreshold2 = $derived(
		appState.temperature.variable === 'Average temperature between'
	);

	// Ensure end month is always >= start month
	$effect(() => {
		if (appState.temperature.months[1] < appState.temperature.months[0]) {
			updateTemperature({ months: [appState.temperature.months[0], appState.temperature.months[0]] });
		}
	});

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
	let variableDropdownOpen = $state(false);
	let yearsDropdownOpen = $state(false);

	// Dropdown options
	const variableOptions = [
		{ value: 'Maximum temperature above' as const, label: 'Maximum temperature above' },
		{ value: 'Minimum temperature below' as const, label: 'Minimum temperature below' },
		{ value: 'Average temperature between' as const, label: 'Average temperature between' }
	];

	const yearsOptions = [
		{ value: '2011-2040' as const, label: '2011-2040' },
		{ value: '2041-2070' as const, label: '2041-2070' },
		{ value: '2071-2100' as const, label: '2071-2100' }
	];

	function selectVariable(value: typeof appState.temperature.variable) {
		updateTemperature({ variable: value });
		variableDropdownOpen = false;
	}

	function selectYears(value: typeof appState.temperature.years) {
		updateTemperature({ years: value });
		yearsDropdownOpen = false;
	}

	// Close dropdowns when clicking outside
	$effect(() => {
		function handleClickOutside(event: MouseEvent) {
			const target = event.target as HTMLElement;
			if (!target.closest('.custom-select')) {
				variableDropdownOpen = false;
				yearsDropdownOpen = false;
			}
		}

		if (variableDropdownOpen || yearsDropdownOpen) {
			document.addEventListener('click', handleClickOutside);
			return () => document.removeEventListener('click', handleClickOutside);
		}
	});
</script>

<div class="user-input-container">
	<div class="input-row">
		<div class="input-group">
			<label for="variable">Number of days per year with:</label>
			<div class="custom-select" class:open={variableDropdownOpen}>
				<button
					type="button"
					class="select-trigger"
					onclick={() => variableDropdownOpen = !variableDropdownOpen}
					aria-haspopup="listbox"
					aria-expanded={variableDropdownOpen}
				>
					<span>{appState.temperature.variable}</span>
					<svg class="select-arrow" class:rotated={variableDropdownOpen} width="10" height="6" viewBox="0 0 12 8" fill="none">
						<path d="M1 1.5L6 6.5L11 1.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					</svg>
				</button>
				{#if variableDropdownOpen}
					<div class="select-dropdown">
						{#each variableOptions as option}
							<button
								type="button"
								class="select-option"
								class:selected={appState.temperature.variable === option.value}
								onclick={() => selectVariable(option.value)}
							>
								{option.label}
							</button>
						{/each}
					</div>
				{/if}
			</div>
		</div>

		<div class="input-group">
			<label for="threshold">Degrees °C</label>
			<input
				id="threshold"
				type="number"
				bind:value={appState.temperature.threshold}
				min="-50"
				max="60"
				step="1"
			/>
		</div>

		<div class="input-group" class:hidden={!showThreshold2}>
			<label for="threshold2">Degrees °C</label>
			<input
				id="threshold2"
				type="number"
				bind:value={appState.temperature.threshold2}
				min="-50"
				max="60"
				step="1"
				disabled={!showThreshold2}
			/>
		</div>

		<div class="input-group compact">
			<label for="years">Future time period</label>
			<div class="custom-select" class:open={yearsDropdownOpen}>
				<button
					type="button"
					class="select-trigger"
					onclick={() => yearsDropdownOpen = !yearsDropdownOpen}
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
	</div>

	<div class="slider-section">
		<p class="slider-label">Select months:</p>
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
		border-radius: 8px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
		border: 1px solid #e9ecef;
	}

	.input-row {
		display: flex;
		gap: 1.25rem;
		align-items: flex-end;
		flex-wrap: wrap;
	}

	.input-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		flex: 0 0 auto;
		transition: opacity 0.3s, visibility 0.3s;
	}

	.input-group:first-child {
		max-width: 320px;
	}

	.input-group.compact {
		max-width: 180px;
	}

	.input-group.hidden {
		display: none;
	}

	label {
		font-size: 0.8125rem;
		color: #495057;
		font-weight: 500;
		margin: 0;
		letter-spacing: 0.01em;
		min-height: 2.5rem;
		display: flex;
		align-items: flex-end;
	}

	input[type='number'] {
		padding: 0.5rem 0.625rem;
		border: 1px solid #D6DEE8;
		border-radius: 6px;
		font-size: 0.875rem;
		line-height: 1.5;
		background: white;
		cursor: text;
		transition: all 0.2s ease;
		font-weight: 500;
		color: #2c3e50;
		max-width: 100px;
		font-family: inherit;
		height: 2.375rem;
	}

	input[type='number']:hover {
		border-color: #B5C4D3;
		background: #FAFBFC;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
	}

	input[type='number']:disabled {
		background: #F5F7FA;
		border-color: #E5E9EF;
		cursor: not-allowed;
		opacity: 0.6;
		color: #9AA6B2;
	}

	input[type='number']:focus {
		outline: none;
		border-color: #4A6FA5;
		background: white;
		box-shadow: 0 0 0 3px rgba(74, 111, 165, 0.12), 0 1px 3px rgba(0, 0, 0, 0.05);
	}

	/* Custom Select Styles */
	.custom-select {
		position: relative;
		width: 100%;
	}

	.select-trigger {
		width: 100%;
		padding: 0.5rem 0.625rem;
		padding-right: 2.25rem;
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
		height: 2.375rem;
	}

	.select-trigger:hover {
		border-color: #B5C4D3;
		background: #FAFBFC;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
	}

	.custom-select.open .select-trigger {
		border-color: #4A6FA5;
		box-shadow: 0 0 0 3px rgba(74, 111, 165, 0.12), 0 1px 3px rgba(0, 0, 0, 0.05);
	}

	.select-arrow {
		position: absolute;
		right: 0.625rem;
		color: #3F5E8C;
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
		padding: 0.45rem 0.625rem;
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
		background: #F0F4F8;
		color: #3F5E8C;
	}

	.select-option.selected {
		background: #E8EEF5;
		color: #3F5E8C;
		font-weight: 600;
	}

	.select-option.selected:hover {
		background: #DDE6F3;
	}

	.slider-section {
		margin-top: 1.5rem;
		padding-top: 0;
	}

	.slider-label {
		display: block;
		margin-bottom: 0.5rem;
		font-size: 0.875rem;
		color: #495057;
		font-weight: 600;
		letter-spacing: 0.02em;
	}

	.month-slider {
		position: relative;
		height: 35px;
		margin: 0.25rem 0;
	}

	.slider-track {
		position: absolute;
		top: 25px;
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
		top: 25px;
		transform: translate(-50%, -50%);
		width: 8px;
		height: 8px;
		background: #D6DEE8;
		border: 1px solid #B5C4D3;
		border-radius: 50%;
		transition: all 0.2s ease;
	}

	.tick.active {
		background: #4A6FA5;
		border-color: #3F5E8C;
		transform: translate(-50%, -50%) scale(1.2);
	}

	.slider-range {
		position: absolute;
		top: 25px;
		transform: translateY(-50%);
		height: 4px;
		background: #4A6FA5;
		border-radius: 2px;
		pointer-events: none;
		z-index: 2;
	}

	.slider-input {
		position: absolute;
		top: 25px;
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
		border: 3px solid #3F5E8C;
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
		border-color: #3F5E8C;
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
		border: 3px solid #3F5E8C;
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
		border-color: #3F5E8C;
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
		box-shadow: 0 0 0 3px rgba(74, 111, 165, 0.25), 0 2px 6px rgba(0, 0, 0, 0.15);
		outline: none;
	}

	.slider-input:focus::-moz-range-thumb {
		box-shadow: 0 0 0 3px rgba(74, 111, 165, 0.25), 0 2px 6px rgba(0, 0, 0, 0.15);
		outline: none;
	}

	.month-labels {
		position: relative;
		margin-top: 0.5rem;
		font-size: 0.75rem;
		height: 1.2rem;
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
		color: #3F5E8C;
		font-weight: 700;
		font-size: 0.85rem;
	}
</style>
