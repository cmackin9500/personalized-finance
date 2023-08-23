<script>
	import Toolbar from "$lib/Toolbar.svelte";
	import CompanySearch from "$lib/CompanySearch.svelte";
	import CompanyFinancials from "$lib/CompanyFinancials.svelte";
	import CompanyHome from "$lib/CompanyHome.svelte";
	import { companyForms, companyFormsFlat } from "$lib/financialsStore.js";

	export let data;

	let dataNormal;
	let dataFlat;


	let currentPage = "home";
	let selectedCompany = ""

	$: {
		dataNormal = data.finances;
		dataFlat = recursiveFlattenTop(dataNormal);

		companyForms.update(old => dataNormal);
		companyFormsFlat.update(old => dataFlat);
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

<Toolbar/>

<div id="search-banner">
	<CompanySearch/>
</div>
<div>
	<h1 style="font-size: 10rem; font-weight: bold;">{data.ticker}</h1>
</div>
<br>

<div id="wrapper">

	<button class="button"
		class:has-background-link,has-background-selected={currentPage === "home"} 
		on:click={() => {currentPage = "home"}}>Overview</button>


	<button class="button"
		class:has-background-link,has-background-selected={currentPage === "financials"} 
		on:click={() => {currentPage = "financials"}}>Financials</button>


	<button class="button"
		class:has-background-link,has-background-selected={currentPage === "derived"} 
		on:click={() => {currentPage = "derived"}}>Derived</button>

</div>


<div class="container">
			{#if currentPage === "home"} 
				<CompanyHome bind:selectedCompany={selectedCompany}/>	
				
			{:else if currentPage === "financials"}
				<CompanyFinancials/>

			{:else if currentPage === "derived"}
			{/if}

</div>

<style>
	button {
		border-radius: 0;
		padding: 1rem 4rem;
		margin: 2px;
	}

	#wrapper {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		width: 100%;
		flex-direction: row;
	}

	#wrapper > div {
		background-color: black;
		width: 1px;
		height: 100%;
	}

	#search-banner {
		display: flex;
		align-items: center;
		padding: 1rem;
		height: 6rem;
		background-image: linear-gradient(to bottom right, blue, cyan);
	}

	.has-background-selected {
		background-color: var(--clr-primary-light);
	}
</style>
