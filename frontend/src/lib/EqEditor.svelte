<script>
	let eqContent = `k = usgaap:PropertyPlantAndEquipmentNet(0) * 0.95
myval = k / usgaap:Assets(0)`;

	let TICKER = "";
	let LASTVARS = {};
	let LASTWORK = {};

	function keydownHandler(event) {
		if (event.key === "Enter"
			&& event.shiftKey === true) {
			// Parse current contents
			event.preventDefault();
			console.log("Parsing equation...");
			temporaryEvalRun(event.srcElement.value);
			//parseEquation(event.srcElement.value);
		}
	}

	function temporaryEvalRun(text) {
		const result = parseAndEval(TICKER, text);
		LASTVARS = result["vars"];
		LASTWORK = result["work"];
		console.log(result);
	}

	function parseAndEval(ticker, text) {
		let window = undefined;
		let document = undefined;

		const split = text.split(/[ \n\t]+/);
		const tokens = tokenizeText(text);

		let out = "";
		let i = 0;
		let error = null;
		let work = {};
		let vars = {};
		while (i < tokens.length) {
			if (tokens[i].includes(":")) {
				// Check if correct syntex
				if (tokens.length - i < 4) {
					error = { msg: ```Invalid syntax near term ${tokens[i]}` }
					break;
				}
				const term = tokens[i];
				const inner = parseInt(tokens[i+2]);

				out += `evalTerm("${ticker}", work, "${term}", ${inner})`;
				i += 4;
				continue;
			} else if (tokens[i] == "\n") {
				out += ";";
				i += 1;
				continue;
			} else if (tokens.length - i >= 2 && tokens[i+1] === "=") {
				//vars[tokens[i]]	= undefined;
				out += `const ${tokens[i]} = vars["${tokens[i]}"]` + " ";
				//out += `const ${tokens[i]}` + " ";
				i += 1;
				continue;
			}

			out += tokens[i] + " ";
			i += 1;
		}
		

		console.log("Evaluating: ", out);
		eval(out);

		// round values
		for (const v of Object.keys(vars)) {
			console.log("V", v);
			vars[v] = vars[v].toFixed(2);
			console.log(vars[v].toFixed);
		}

		let result = {
			work: work,
			vars: vars
		};
		console.log(work);
		console.log(vars);

		return result;
	}

	// Inner should be an integer
	// The work term is an object containing all the results
	// for evaluated terms. This function retrieves all values
	// for a given term at a time period and 
	function evalTerm(ticker, work, term, inner) {
		work[`${term}(${inner})`] = {
			values: [1, 2, 3],
			result: 6
		};

		return 6
	}

	//function parseEquation(text) {
	//	const tokens = tokenizeText(text);
	//	console.log(tokens);

	//	const ast = {
	//		type: "equation",
	//		children: []
	//	}

	//	for (const t of tokens) {
	//			
	//	}
	//}

	function tokenizeText(text) {
		const special = "()=+-*/^\n";
		const skip = " \t";

		let tokens = [];
		let buffer = "";

		for (const char of text) {
			if (skip.includes(char)) { 
				if (buffer.length > 0) {
					tokens.push(buffer);
				}
				buffer = "";
				continue;
			}

			if (special.includes(char)) {
				if (buffer.length > 0) {
					tokens.push(buffer);
				}
				buffer = "";
				tokens.push(char)
				continue;
			}

			if (skip.includes(char)) { continue }
			buffer += char;
		}

		if (buffer.length > 0) {
			tokens.push(buffer);
		}

		return tokens;
	}
</script>


<div id="wrapper" class="container">
	<div class="card">
		<div class="card-content">
		<div class="container">
				<label class="label">Company Ticker</label>
				<input class="input" bind:value={TICKER}/>
			</div>
			<textarea style="width: 100%; height: 20ch;"
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


