<script>
	import { companyForms, companyFormsFlat } from "$lib/financialsStore.js";
	import { JSONGetRequest } from "$lib/util.js";

	export let selectedCompany = "";
	let currentCompany = "";
	let currentQuery = "";
	let searchError = null;

	function getCompanyData() {
		selectedCompany = "";
		JSONGetRequest(`/api/financials/allForms/${currentCompany}`)
			.then(data => {
				searchError = null;
				companyForms.update(prev => {});
				companyForms.update(prev => data);
				const flat = recursiveFlattenTop(data);
				companyFormsFlat.update(prev => {});
				companyFormsFlat.update(prev => flat);
				console.log(flat);
				selectedCompany = currentCompany;
			})
			.catch(async err => {
				selectedCompany = "";
				console.log(err.cause);
				searchError = err.cause;
			}) 
	}

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

			out[term][date] = node[term]["val"];

			out = recursiveFlatten(node[term]["children"], date, out);
		}

		return out;
	}
</script>

<div class="container">
	<div class="card"> 
		<div id="search-bar" class="">
			<form on:submit={getCompanyData}>
				<label>Search:</label>
				<input class="input" bind:value={currentCompany}/>
				<button style="display: none;"></button>
			</form>
		</div>


		<div class="content">
			{#if currentQuery.length > 0}
				<ul>
					<li>This</li>
					<li>Will</li>
					<li>Show</li>
					<li>Results</li>
				</ul>
			{/if}
		</div>
	</div>
	<div>
		{#if searchError}
			<p>{searchError.msg}</p>
		{/if}
	</div>
</div>

<style>
	#search-bar {
		display: flex;
		align-items: center;
		padding:0.5rem;
	}

	#search-bar > label {
		display: flex;
		align-items: center;
		font-weight: bold;
		margin: 0.5rem;
	}
</style>
