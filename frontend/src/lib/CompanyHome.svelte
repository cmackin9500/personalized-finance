<script>
	import { onMount } from "svelte";
	import { Chart } from "chart.js/auto";

	export let selectedCompany = "";
	let marketPricePlot = undefined;

	let chartInstance;

	const marketTimes = [
		0, 1, 2, 3, 4, 5, 6, 7, 8, 9
	];
	
	const marketPrices = [
		10, 13, 12, 14, 17, 16, 19, 23, 27, 31
	];


	onMount(async () => {
		console.log(marketPricePlot);
		chartInstance =  new Chart(document.getElementById("plotdiv"), {
			type: "line",
			data: {
				labels: marketTimes,
				datasets: [
					{
						label: "Market Price",
						data: marketPrices
					}
				]
			}
		});
	})
</script>

<br>
<div class="card">
	<div class="columns">
		<div class="column" style="padding: 1rem;"> 
			<canvas id="plotdiv" bind:this={marketPricePlot} style="width: 100%;"></canvas>
		</div>
	</div>
</div>
<br>

<section class="hero is-link">
	<div class="hero-body">
		<p class="title">Additional Information</p>
	</div>
</section>

<br>

<div class="content card" style="padding: 1rem;">
	<p>We can add more information for each company down here such as times of latest filings, maybe links to various financial forms.</p>
</div>

<style>
	td:nth-child(odd) {
		font-weight: bold;
	}
</style>
