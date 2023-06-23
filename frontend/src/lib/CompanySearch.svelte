<script>
	import { companyForms } from "$lib/financialsStore.js";
	import { JSONGetRequest } from "$lib/util.js";

	export let selectedCompany = "";
	let currentCompany = "";
	let currentQuery = "";
	let searchError = null;

	function getCompanyData() {
		JSONGetRequest(`/api/financials/allForms/${currentCompany}`)
			.then(data => {
				companyForms.update(prev => data);
				selectedCompany = currentCompany;
			})
			.catch(async err => {
				selectedCompany = "";
				console.log("ASD");
				console.log(err.cause);
				searchError = err;
			}) 
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
			<p>{JSON.stringify(searchError)}</p>
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
