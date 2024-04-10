<script>
	import Toolbar from "$lib/Toolbar.svelte";
	import { JSONPostRequest } from "$lib/util.js";

	let tempLink;

	function sendEmailVerification() {
		JSONPostRequest("/api/sendEmailVerification")
			.then(data => {
				console.log(data);
				tempLink = data.link;
			})
	}
</script>

<Toolbar/>

<div class="container card">
	<button on:click={sendEmailVerification}>Send Email Verification</button>
	<div class="content">
		<p>We've sent a verification link to your email. Your account will be fully enabled once verified.</p>
	</div>
	<h1>Temporary Button For Debug Verification</h1>
	<a href={tempLink}>DEBUG VERIFY</a>
</div>
