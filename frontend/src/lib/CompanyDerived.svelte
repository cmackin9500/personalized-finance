<script>
	import { companyForms, companyFormsFlat } from "$lib/financialsStore.js";
	import { temporaryEvalRun } from "$lib/ovmscript.js";
	import EqEditor from "$lib/EqEditor.svelte";
	import EquationTable from "$lib/EquationTable.svelte";

	let equations = [
		{
			"name": "Adjusted Assets",
			"eq": "AdjAssets = usgaap:Assets(0) * 1.0"
		},
		{
			"name": "Adjusted Assets",
			"eq": "AdjAssets1 = usgaap:Assets(0) * 0.9"
		},
		{
			"name": "Adjusted Assets",
			"eq": "AdjAssets2 = usgaap:Assets(0) * 0.8"
		},
		{
			"name": "Adjusted Assets",
			"eq": "AdjAssets3 = usgaap:Assets(0) * 0.7"
		},
	];

</script>



<section class="hero is-link">
	<div class="hero-body">
		<p class="title">Derived values</p>
	</div>
</section>

<EquationTable
	userEquations={equations}/>

<EqEditor
	onSubmitFunc={() => {}}/>

<br>



<div>
</div>

<section class="hero is-primary">
	<div class="hero-body">
		<p class="title">Models</p>
	</div>
</section>



