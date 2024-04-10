<script>
	import { onMount } from "svelte";
	import { companyForms, companyFormsFlat } from "$lib/financialsStore.js";
	import { evalEquationYears } from "$lib/ovmscript.js";

	export let userEquations;

	let companyData;
	let companyDataFlat;

	let evalResults = {

	}

	companyForms.subscribe(newData => {
		companyData = newData;
	})

	companyFormsFlat.subscribe(newData => {
		companyDataFlat = newData;
	})

	// Evaluates all user equations and sets evalResults
	function evalAllEquations() {
		const years = Object.keys(companyData).sort();
		evalResults = {};
		for (const eq of userEquations) {
			const row = evalEquationYears(eq["eq"], companyDataFlat, years);
			if (row.length > 0) {
				evalResults[row[0]["name"]] = row;
			}			
		}
	}

	onMount(() => {
		evalAllEquations();
	})
</script>

<table class="table" style="width: 100%;">
	<tbody>
		{#each Object.keys(evalResults) as field}
			<tr>
				<td>{field}</td>
				{#each evalResults[field] as entry}
					<td>{entry["res"]}</td>
				{/each}
			</tr>
		{/each}
	</tbody>
</table>
