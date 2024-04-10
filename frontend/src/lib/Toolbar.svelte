<script>
	import { browser } from "$app/environment";

	let isLoggedIn = false;

	if (browser) {
		isLoggedIn = document.cookie.includes("overmacWebDummy");
	}

</script>

<div id="wrapper">
	<div style="flex-grow: 1;">
		<a href="/">Home</a>
		<a href="/company">Company</a>
	</div>
	<h1 style="color: var(--clr-text-light)">overmac</h1>
	<div style="flex-grow: 1;"></div>

	<div style="padding-right: 0.5rem;">
		{#if isLoggedIn}
			<a href="/account" style="font-weight: bold" class="has-text-light">Account</a>
		{:else}
			<a href="/login">Login</a>
			<a href="/register">Register</a>
		{/if}
	</div>
</div>

<style>
	#wrapper {
		display: flex;
		align-items: center;
		background-color: #444444;
		padding: 0.5rem;
	}

	a {
		color: var(--clr-text-light);
		font-weight: bold;
		text-decoration: none;
	}

	i {
		font-size: 1.5rem;
		padding: 0.25rem 0.5rem;
	}

	i:hover {
		opacity: 0.5
	}

	h1 {
		font-size: 1.5rem;	
		font-weight: bold;
	}


</style>
