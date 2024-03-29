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
