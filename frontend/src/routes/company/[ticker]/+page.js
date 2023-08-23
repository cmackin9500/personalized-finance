import { JSONGetRequest } from "$lib/util.js";

export function load({ params, fetch }) {
	return fetch(`/api/financials/allForms/${params.ticker}`).
		then(res => {
			return res.json()
		});
	//return JSONGetRequest(`/api/financials/allForms/${params.ticker}`)
}
