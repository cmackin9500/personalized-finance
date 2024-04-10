<script>
	import { onMount } from "svelte";
	import { companyForms } from "$lib/financialsStore.js";

	export let onSubmitFunc = () => {};


	let eqContent = `k = usgaap:Assets(0) * 0.95`;

	let TICKER = "";
	let LASTVARS = {};
	let LASTWORK = {};

	function keydownHandler(event) {
		if (event.key === "Enter"
			&& event.shiftKey === true) {
			// Parse current contents
			event.preventDefault();
			onSubmitFunc(eqContent);
			//console.log("Parsing equation...");
			//temporaryEvalRun(event.srcElement.value);
			//parseEquation(event.srcElement.value);
		}
	}

</script>


<div id="wrapper" class="container">
	<div class="card">
		<div class="card-content">
		<div class="container">
				<label class="label">Company Ticker</label>
				<input class="input" bind:value={TICKER}/>
			</div>
			<textarea class="textarea" style="width: 100%; height: 20ch;"
		  	  	  	  bind:value={eqContent}
		  	  	  	  on:keydown={keydownHandler}/>
		</div>
	</div>
</div>

<br>

<div class="container">
	<div class="card">
		<header class="card-header">
			<h2 class="title" style="padding: 0.5rem;">Results</h2>
		</header>

		<div class="card-content">
			<table class="table">
				<thead>
					{#if Object.keys(LASTVARS).length > 0} 
						<tr>
							<th>Variable Name</th>
							<th>Value</th>
						</tr>
					{/if}
				</thead>
				<tbody>
					{#each Object.keys(LASTVARS) as v}
						<tr>
							<td>
								{v}
							</td>

							<td>
								{LASTVARS[v]}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>

			<table class="table">
				<thead>
					{#if Object.keys(LASTWORK).length > 0} 
						<tr>
							<th>Tag</th>
							<th>Values</th>
							<th>Sum</th>
						</tr>
					{/if}
				</thead>
				<tbody>
					{#each Object.keys(LASTWORK) as w}
						<tr>
							<td>
								{w}
							</td>

							<td>
								[ {LASTWORK[w].values.join(" | ")} ]
							</td>

							<td>
								{LASTWORK[w].result}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</div>

<style>

	#results-card {
		margin: 0.5rem;
	}
</style>


