export function JSONGetRequest(url) {
	return fetch(url)
		.then(async res => {
			if (res.status < 200 || res.status >= 400) {
				const content = await res.json();
				throw new Error(res, { cause: content } );
			}

			return res.json();
		})
}

export function JSONPostRequest(url, body) {
	return fetch(url, {
		method: "POST",
		headers: {
			"Content-Type": "application/json"
		},
		body: JSON.stringify(body)
	})
		.then(async res => {
			if (res.status < 200 || res.status >= 400) {
				const content = await res.json();
				throw new Error(res, { cause: content } );
			}

			return res.json();
		})
}
