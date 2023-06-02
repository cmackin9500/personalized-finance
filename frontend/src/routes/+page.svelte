<script>
	import EqEditor from "$lib/EqEditor.svelte";
	import Toolbar from "$lib/Toolbar.svelte";
</script>

<Toolbar/>
<div id="page-content" class="has-background-light">
	<br>

	<div class="container">
		<div class="card">
			<header class="card-header">
				<h1 class="title card-title" style="padding:0.5rem;">Equation Editor Demo</h1>
			</header>
			<div class="card-content content">
				<p>The overmac equation editor allow users to input their own arbitrary expressions to evaluate company financial data. All intermediate and computed values are saved and shown to the user at the end of the calculation. This enables users to directly debug written expressions and derive many values from a single calculation run. This approach runs all user code client-side, which avoids many of the issues associated with running arbitrary user code. For future releases, the current implementation would have to be hardened to effectively sandbox some of the functionality within the edit, as only a rudimentary parser is used to santize the input.</p>

				<p>The current implementation just uses some hard-coded values when evaluating the corresponding functions for various gap terms, but this can easily be replaced with some form of API call/cached call lookup for the correct value. Because all intermediate values are stored, we can alert users if values are missing or likely to be incorrect.</p>

				<h3>Usage</h3>
				<p>Right now the ticker box does not perform anything meaningful. Pressing shift-enter while in the text editor part runs the current code content. The output from the calculation is shown at the bottom.</p>

				<h3>Future work</h3>
				<ul>
					<li>Create and API layer for retrieving values</li>
					<ul>
						<li>For best performance, we should retrieve all forms relevant to the calculation and cache them. This can be done using the output of the tokenizer.</li>
						<li>Add corresponding text from the financial document to the intermediate step (trivial).</li>
						<li>Create backend server to interface with the editor. It would be nice to have a stable data format before starting this.</li>
					</ul>
					<li>Use a nicer looking editor such as Quill</li>
				</ul>
			</div>
		</div>
	</div>

	<br>

	<EqEditor/>
	<br>


</div>

<style>
	#page-content > * {
		margin-top:0.5rem;
	}
</style>
