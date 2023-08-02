<script>
	import Toolbar from "$lib/Toolbar.svelte";
	import { browser } from "$app/environment";
	import { isLoggedIn } from "$lib/userDataStore.js";

	let status;
	isLoggedIn.subscribe((val) => { status = val });

</script>

<Toolbar/>

<p>User Account page</p>
<p>{JSON.stringify(status)}</p>
