<script>
	import { onMount } from "svelte";
	import { companyForms, companyFormsFlat } from "$lib/financialsStore.js";

	let financialPlot;

	let companyData = {};
	let companyDataFlat = {};

	companyForms.subscribe(newData => {
		companyData = newData;
	})

	companyFormsFlat.subscribe(newData => {
		companyDataFlat = newData;
	})

	let normalizePlotData = false;

	let tableWrapperElem;

	$: {
		normalizePlotData;
		updatePlot(null);
	}

	$: arrayTempData = function() {
		const years = Object.keys(companyData).sort().reverse();

		// Make array
		let arr = new Array(Object.keys(companyDataFlat).length);
		for (let i = 0; i < arr.length; i++) {
			arr[i] = new Array(years.length + 1);
		}

		for (const [i, term] of Object.keys(companyDataFlat).entries()) {
			arr[i][0] = term;

			for (const year of Object.keys(companyDataFlat[term])) {
				const index = years.indexOf(year) + 1;
				arr[i][index] = companyDataFlat[term][year];
			}
		}


		return arr;
	}()

	$: shouldPlotTable = function() {
		let keys = Object.keys(companyDataFlat);

		let out = {}
		for (const k of keys) {
			out[k] = false;
		}

		return out;
	}();


	function updatePlot(fieldName) {
		if (fieldName) {
			shouldPlotTable[fieldName] = !shouldPlotTable[fieldName];
		}

		// TODO: Fix weird bug that requires this
		if (!shouldPlotTable) { return }

		const keys = Object.keys(shouldPlotTable)
			.filter((k) => {
				return shouldPlotTable[k];
			});

		// Should look into using Plotly.react to improve performance
		// Not a concern right now

		let datasets = [];
		for (const k of keys) {
			const data = convertFlattenedToTrace(k, companyDataFlat[k])
			if (normalizePlotData) {
				data.y = data.y.map(y => y / Math.max(...data.y));
			}
			datasets.push(data);
		}

		const layout = {
			autosize: true
		};

		Plotly.newPlot(financialPlot,
			datasets, layout);
	}

	function convertFlattenedToTrace(name, flattened) {
		const traces = [];
		const x = Object.keys(flattened).sort();
		
		let y = [];
		for (const k of x) {
			y.push(flattened[k]);
		}

		console.log(y);

		return {
			x: x,
			y: y,
			name: name
		};
	}

	function simplifyTag(tag) {
		const content = tag.split(":")[1];
		return content.match(/[A-Z][a-z]+|[0-9]+/g).join(" ")
	}

	onMount(async () => {
		const layout = {
			autosize: true
		};
		Plotly.newPlot(financialPlot, {}, layout);
	})
</script>

<br>

<div id="wrapper" class="card">
	<div style="display: flex; align-items: center; padding: 0.5rem; 
	justify-content: right;">
		<input type="checkbox" style="margin-right: 0.5rem;"
			bind:checked={normalizePlotData}/>
		<p class="subtitle-5" style="padding-right: 0.5rem;">Normalize</p>
	</div>

	<div id="financial-plot" bind:this={financialPlot}>
	</div>

	<br>

	<div id="table-wrapper" bind:this={tableWrapperElem}>
		<table class="table" style="width: 100%">
			<thead>
				<tr style="position: sticky; top: 0; z-index: 101; background-color: #e8e8e8">
					<th style="flex-grow: 1;">
						<div style="flex-grow: 1;">
							Field
						</div>

						<div style="min-width: 10ch; text-align: center; text-align: center;">Plot</div>
					</th>
					{#each Object.keys(companyData).sort().reverse() as key}
						<th>{key}</th>
					{/each}
				</tr>
			</thead>

			<tbody>
				{#each arrayTempData as row}
					{#if !row[0].includes("Abstract")}
						<tr>
							{#each row as cell, i}
								{#if i === 0}
									<td>
										<div style="flex-grow: 1;">
											{simplifyTag(cell)}
										</div>

										<div style="min-width: 10ch; text-align: center;">
											<input type="checkbox"
			  									on:change={updatePlot(cell)} />
										</div>
									</td>
								{:else}
									{#if cell === undefined || cell === null}
										<td>-</td>
									{:else if i === 0}
										<td>{simplifyTag(cell)}</td>
									{:else}
										<td>{cell.toLocaleString()}</td>
									{/if}
								{/if}
							{/each}
						</tr>
					{/if}
				{/each}
			</tbody>
		</table>
	</div>
</div>

<br>

<style>
	#wrapper {
		height: 95vh;
	}

	#financial-plot {
		height: 30vh;
		width: 100%;
	}

	#table-wrapper {
		overflow-x: scroll;
		overflow-y: scroll;
		height: 60vh;
	}

	td:first-child, th:first-child {
		display: flex;
		position: sticky;
		position: -webkit-sticky;
		background-color: #c8c8c8;
		min-width: 20ch;
		left: 0px;
		z-index:100;
	}


</style>
