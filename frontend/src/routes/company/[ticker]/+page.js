import { JSONGetRequest } from "$lib/util.js";

export async function load({ params, fetch }) {
	return fetch(`/api/financials/allForms/${params.ticker}`).
		then(async res => {
			let rawData = await res.json();
			return {
				ticker: params.ticker,
				finances: rawData
			};
		});
	//return JSONGetRequest(`/api/financials/allForms/${params.ticker}`)
}
