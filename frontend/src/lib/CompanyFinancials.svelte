<script>
	import { onMount } from "svelte";
	import { companyForms, companyFormsFlat } from "$lib/financialsStore.js";
	import { Chart } from "chart.js/auto";

	let financialPlot;
	let chartInstance;

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
		for (const [i, k] of keys.entries()) {
			if (k === "us-gaap:Assets") {
				out[k] = true;
			} else {
				out[k] = false;
			}
		}


		updatePlot();
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
				let max = 1;
				for (const elem of data.data) {
					if (elem.y > max) max = elem.y;
				}

				data.data = data.data.map(elem => {
					return {
						x: elem.x,
						y: elem.y / max,
					}
				})
			}
			datasets.push(data);
		}

		// Clear prior data
		chartInstance.destroy();

		chartInstance = new Chart(financialPlot, {
			type: "line",
			data: {
				datasets: datasets,	
			}
		})
	}

	function convertFlattenedToTrace(name, flattened) {
		const traces = [];
		const x = Object.keys(flattened).sort();

		let data = [];
		
		for (const k of x) {
			data.push({x: k, y: flattened[k]})
		}

		return {
			label: name,
			data: data
		};
	}

	function simplifyTag(tag) {
		const content = tag.split(":")[1];
		return content.match(/[A-Z][a-z]+|[0-9]+/g).join(" ")
	}

	onMount(async () => {
		chartInstance = new Chart(financialPlot, {
			type: "line"
		});

		updatePlot();
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

	<div id="financial-plot">
		<canvas bind:this={financialPlot} style="width: 100%;">
		</canvas>
	</div>

	<br>

	<div bind:this={tableWrapperElem} style="display: flex; flex-direction: row; width: 100%; flex-wrap: wrap; padding: 1rem;">
		<div style="width: 100%; height: 40vh; overflow-x: auto; min-width: 40ch;">
			<table style="width: 100%;">
				<thead>
					<tr style="position: sticky; top: 0; left:0 ; z-index: 101; background-color: #ffffff; border-bottom: solid black 2px;">
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
											<div style="flex-grow: 1; max-width: 20ch;">
												{simplifyTag(cell)}
											</div>

											<div style="min-width: 10ch; text-align: center;">
												{#if cell === "us-gaap:Assets"}
													<input type="checkbox"
			  											on:change={updatePlot(cell)} checked="true"/>
												{:else}
													<input type="checkbox"
			  											on:change={updatePlot(cell)} />
												{/if}
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
</div>

<br>

<style>
	#wrapper {
		height: 95vh;
	}

	#financial-plot {
		display: flex;
		justify-content: center;
		height: 50vh;
		width: 100%;
	}

	table {
		border-collapse: collapse;
	}

	tbody > tr {
		border-bottom: solid grey 1px;
		line-height: 1.5rem;
	}

	td {
		text-align: right;
		padding-right: 0.5rem;
	}

	th {
		text-align: right;
		padding-right: 0.5rem;
	}

	td:first-child, th:first-child {
		text-align: left;
		display: flex;
		position: sticky;
		position: -webkit-sticky;
		min-width: 20ch;
		left: 0px;
		z-index:100;
	}


</style>
