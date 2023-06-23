<script>
	import { onMount } from "svelte";
	import { companyForms } from "$lib/financialsStore.js";

	let financialPlot;

	let companyData = {};

	let normalizePlotData = false;

	$: {
		normalizePlotData;
		console.log("ASD");
		updatePlot(null);
	}

	companyForms.subscribe(newData => {
		companyData = newData;
	})

	$: flatTempData = recursiveFlattenTop(companyData);
	$: arrayTempData = function() {
		const years = Object.keys(companyData).sort();

		// Make array
		let arr = new Array(Object.keys(flatTempData).length);
		for (let i = 0; i < arr.length; i++) {
			arr[i] = new Array(years.length + 2);
		}

		for (const [i, term] of Object.keys(flatTempData).entries()) {
			arr[i][0] = term;
			arr[i][years.length + 1] = term;

			for (const year of Object.keys(flatTempData[term])) {
				const index = years.indexOf(year) + 1;
				arr[i][index] = flatTempData[term][year];
			}
		}

		console.log(arr);

		return arr;
	}()

	$: shouldPlotTable = function() {
		let keys = Object.keys(flatTempData);

		let out = {}
		for (const k of keys) {
			out[k] = false;
		}

		return out;
	}();


	function recursiveFlattenTop(data) {
		let out = {}

		for (const year of Object.keys(data)) {
			out = recursiveFlatten(data[year], year, out);
		}
		console.log(out);

		return out;
	}

	function recursiveFlatten(node, date, out) {
		for (const term of Object.keys(node)) {
			if (!out[term])	 {
				out[term] = {};
			}

			out[term][date] = node[term]["val"];

			out = recursiveFlatten(node[term]["child"], date, out);
		}

		return out;
	}

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
			const data = convertFlattenedToTrace(k, flatTempData[k])
			if (normalizePlotData) {
				data.y = data.y.map(y => y / Math.max(...data.y));
			}
			datasets.push(data);
		}

		Plotly.newPlot(financialPlot,
			datasets);
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
		Plotly.newPlot(financialPlot);
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

	<div id="table-wrapper">
		<table class="table" style="width: 100%">
			<thead>
				<tr style="position: sticky; top: 0; z-index: 101; background-color: #e8e8e8">
					<th>Field</th>
					{#each Object.keys(companyData).sort() as key}
						<th>{key}</th>
					{/each}
					<th>Plot</th>
				</tr>
			</thead>

			<tbody>
				{#each arrayTempData as row}
					{#if !row[0].includes("Abstract")}
						<tr>
							{#each row as cell, i}
								{#if i === row.length - 1}
									<td>
										<input type="checkbox" 
			  								on:change={updatePlot(cell)} />
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
		height: 90vh;
	}

	#financial-plot {
		height: 40vh;
	}

	#table-wrapper {
		overflow-x: scroll;
		overflow-y: scroll;
		height: 50vh;
	}

	td:first-child, th:first-child {
		position: sticky;
		position: -webkit-sticky;
		background-color: #c8c8c8;
		left: 0px;
		min-width: 20ch;
	}


</style>
