export function JSONGetRequest(url) {
	return fetch(url)
		.then(res => {
			if (res.status < 200 || res.status >= 400) {
				throw new Error(res);
			}
			return res.json();
		})
}
