export function temporaryEvalRun(text, flatData, years, targetYear) {
	const result = parseAndEval(text, flatData, years, targetYear);
	const LASTVARS = result["vars"];
	const LASTWORK = result["work"];
	const keys = Object.keys(LASTVARS);
	result["res"] = LASTVARS[keys[keys.length - 1]]
	result["name"] = keys[keys.length - 1];
	
	return result
}

function parseAndEval(text, flatData, years, targetYear) {
	let window = undefined;
	let document = undefined;

	const split = text.split(/[ \n\t]+/);
	const tokens = tokenizeText(text);
	console.log("Tokens", tokens);

	let out = "";
	let i = 0;
	let error = null;
	let work = {};
	let vars = {};
	while (i < tokens.length) {
		if (tokens[i].includes(":")) {
			// Check if correct syntex
			if (tokens.length - i < 4) {
				error = { msg: `Invalid syntax near term ${tokens[i]}` }
				break;
			}

			const term = tokens[i].replace("usgaap", "us-gaap");
			const indexOfTarget = years.indexOf(targetYear);
			const eqIndex = parseInt(tokens[i+2]);
			const inner = years[indexOfTarget - eqIndex];

			out += `evalTerm(flatData, work,"${term}", "${inner}")`;
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
		vars[v] = vars[v].toFixed(2);
	}

	let result = {
		work: work,
		vars: vars
	};

	return result;
}

// Inner should be an integer
// The work term is an object containing all the results
// for evaluated terms. This function retrieves all values
// for a given term at a time period and 
function evalTerm(flatData, work, term, inner) {
	const val = flatData[term][inner];
	work[`${term}(${inner})`] = {
		values: val,
		result: val
	};

	return val
}

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

// Evaluates equation over all years provided
export function evalEquationYears(equation, companyDataFlat, years) {
	const out = []
	for (const y of years) {
		const res = temporaryEvalRun(equation, companyDataFlat, years, y);
		out.push(res);
	}

	return out;
}
