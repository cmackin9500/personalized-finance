
<script>
	import EqEditor from "$lib/EqEditor.svelte";
	import Toolbar from "$lib/Toolbar.svelte";
	import CompanySearch from "$lib/CompanySearch.svelte";
	import CompanyHome from "$lib/CompanyHome.svelte";
	import CompanyFinancials from "$lib/CompanyFinancials.svelte";
	import CompanyDerived from "$lib/CompanyDerived.svelte";

	let currentPage = "home";
	let selectedCompany = "";

</script>


<Toolbar/>
<br>
<CompanySearch bind:selectedCompany={selectedCompany}/>
<br>

{#if selectedCompany.length > 0}
	<div class="container">
		<div class="hero is-link is-small">
			<div class="hero-body">
				<p class="title">{selectedCompany}</p>
				<p class="subtitle">{selectedCompany}</p>
			</div>
		</div>
	</div>

	<br>

	<div id="wrapper" class="has-background-white-ter container">
		<div class="card">
			<div class="card-header">
				<button class="button" on:click={() => {currentPage = "home"}}>Overview</button>
				<button class="button" on:click={() => {currentPage = "financials"}}>Financials</button>
				<button class="button" on:click={() => {currentPage = "derived"}}>Derived</button>
			</div>

			
		</div>
	</div>
	<div class="container">
				{#if currentPage === "home"} 
					<CompanyHome bind:selectedCompany={selectedCompany}/>	
					
				{:else if currentPage === "financials"}
					<CompanyFinancials/>

				{:else if currentPage === "derived"}
					<CompanyDerived/>
					<EqEditor/>
				{/if}

	</div>
{/if}

<style> 
</style>
