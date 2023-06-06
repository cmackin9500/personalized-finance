<script>
	export let selectedCompany = ";"
	let currentCompany = "";
	let currentQuery = "";
</script>

<div class="container">
	<div class="card"> 
		<div id="search-bar" class="">
			<label>Search:</label>
			<input class="input" bind:value={currentQuery}/>
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
