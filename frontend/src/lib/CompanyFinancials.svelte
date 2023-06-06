<script>
	import { onMount } from "svelte";

	let financialPlot;

	const tempData = {
		"2023-01-03": {
			"us-gaap:Assets": {
				"value": 100000,
				"children": {
					"us-gaap:PropertyPlantAndEquipment": {
						"value": 60000,
						"children": {}
					}
				}
			}
		},
		"2022-01-03": {
			"us-gaap:Assets": {
				"value": 105000,
				"children": {
					"us-gaap:PropertyPlantAndEquipment": {
						"value": 65000,
						"children": {}
					}
				}
			}
		},
		"2021-01-03": {
			"us-gaap:Assets": {
				"value": 99000,
				"children": {
					"us-gaap:PropertyPlantAndEquipment": {
						"value": 57000,
						"children": {}
					}
				}
			}
		},
		"2020-01-03": {
			"us-gaap:Assets": {
				"value": 90000,
				"children": {
					"us-gaap:PropertyPlantAndEquipment": {
						"value": 40000,
						"children": {}
					}
				}
			}
		},
	}

	$: flatTempData = recursiveFlattenTop(tempData);
	$: arrayTempData = function() {
		const years = Object.keys(tempData).sort();

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
				console.log(index);
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

		return out;
	}

	function recursiveFlatten(node, date, out) {
		for (const term of Object.keys(node)) {
			if (!out[term])	 {
				out[term] = {};
			}

			out[term][date] = node[term]["value"];

			out = recursiveFlatten(node[term]["children"], date, out);
		}

		return out;
	}

	function updatePlot(fieldName) {
		shouldPlotTable[fieldName] = !shouldPlotTable[fieldName];
		console.log(shouldPlotTable);

		const keys = Object.keys(shouldPlotTable)
			.filter((k) => {
				return shouldPlotTable[k];
			});

		console.log(keys);


		// Should look into using Plotly.react to improve performance
		// Not a concern right now

		let datasets = [];
		for (const k of keys) {
			const data = convertFlattenedToTrace(k, flatTempData[k])
			console.log(data);
			datasets.push(data);
		}

		Plotly.newPlot(financialPlot,
			datasets);
	}

	function convertFlattenedToTrace(name, flattened) {
		const traces = [];
		const x = Object.keys(flattened);
		
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

	onMount(async () => {
		Plotly.newPlot(financialPlot);
	})
</script>

<br>

<div class="card">
	<div bind:this={financialPlot}>
	</div>
</div>

<br>

<table class="table" style="width: 100%">
	<thead>
		<tr>
			<th>Field</th>
			{#each Object.keys(tempData).sort() as key}
				<th>{key}</th>
			{/each}
			<th>Plot</th>
		</tr>
	</thead>

	<tbody>
		{#each arrayTempData as row}
			<tr>
				{#each row as cell, i}
					{#if i === row.length - 1}
						<td>
							<input type="checkbox" 
			  					on:change={updatePlot(cell)} />
						</td>
					{:else}
						<td>{cell}</td>
					{/if}
				{/each}
			</tr>
		{/each}
	</tbody>
</table>
<br>
