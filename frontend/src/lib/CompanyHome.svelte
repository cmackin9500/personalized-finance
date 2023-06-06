<script>
	import { onMount } from "svelte";

	export let selectedCompany = "";
	let marketPricePlot = undefined;

	const bsValues = [
		["Market price", 234],
		["Market price", 234],
		["Market price", 234],
		["Market price", 234],
		["Market price", 234],
		["Market price", 234],
		["Market price", 2340],
		["Market price", -234],
		["Market price", 2304],
		["Market price", 2304],
		["Market price", 2034],
		["Market price", 20034],
	]

	const marketTimes = [
		0, 1, 2, 3, 4, 5, 6, 7, 8, 9
	];
	
	const marketPrices = [
		10, 13, 12, 14, 17, 16, 19, 23, 27, 31
	];


	onMount(async () => {
		Plotly.newPlot(marketPricePlot, [{
			x: marketTimes,
			y: marketPrices,
		}], {
			title: "Market Prices",
			xaxis: {
				title: "Time (some units)"
			},
			yaxis: {
				title: "Price ($/share)"
			},
		}, {
			responsive: true
		})
	})
</script>

<div class="columns">
	<div class="column" style="padding: 1rem;
		display:flex; justify-content: center;">
		<table class="table">
			<tbody>
				{#each bsValues as val, i}
					{#if i % 2 === 0}
						<tr>
							<td>{val[0]}</td>
							<td>{val[1]}</td>
							<td>{bsValues[i+1][0]}</td>
							<td>{bsValues[i+1][1]}</td>
						</tr>
					{/if}
				{/each}

				<tr>
					<td>Market Value</td>
					<td>230</td>
					<td>Some</td>
					<td>123</td>
				</tr>

				<tr>
					<td>Market Value</td>
					<td>230</td>
					<td>Some</td>
					<td>123,000</td>
				<tr>
			</tbody>
		</table>
	</div>

	<div class="column" style="padding: 1rem;"> 
		<div bind:this={marketPricePlot} style="width: 100%;"></div>
	</div>
</div>

<section class="hero is-link">
	<div class="hero-body">
		<p class="title">Additional Information</p>
	</div>
</section>

<div class="content" style="padding: 1rem;">
	<p>We can add more information for each company down here such as times of latest filings, maybe links to various financial forms.</p>
</div>

<style>
	td:nth-child(odd) {
		font-weight: bold;
	}
</style>
