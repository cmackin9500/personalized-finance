<script>
	import { companyForms, companyFormsFlat } from "$lib/financialsStore.js";
	import { JSONGetRequest } from "$lib/util.js";

	export let selectedCompany = "";
	let currentCompany = "";
	let currentQuery = "";
	let searchError = null;

	function getCompanyData() {
		window.location.href = `/company/${currentCompany}`;
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

<div id="search-container">
	<div class="card"> 
		<div id="search-bar" class="">
			<form on:submit={getCompanyData} style="width: 100%">
				<input id="search-input" class="input" bind:value={currentCompany} 
					placeholder="Search"/>
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

	#search-input {
		max-width: 200ch;
		min-width: 20ch;
		width: 100%;
	}

	#search-container {
		width: 100%;
		display: flex;
		justify-content: center;
	}
</style>
