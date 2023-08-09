<script>
	import { browser } from "$app/environment";

	let isLoggedIn = false;

	if (browser) {
		isLoggedIn = document.cookie.includes("overmacWebDummy");
	}

</script>

<div id="wrapper">
	<div style="flex-grow: 1;">
		<a href="/"><i class="fa-solid fa-house has-text-light icon-is-large"/></a>
		<a href="/company" class="has-text-light"
			style="font-weight: bold;">Company</a>
	</div>
	<h1 class="has-text-light" style="text-align: center;">overmac</h1>
	<div style="flex-grow: 1;"></div>

	<div style="padding-right: 0.5rem;">
		{#if isLoggedIn}
			<a href="/account" style="font-weight: bold" class="has-text-light">Account</a>
		{:else}
			<a href="/login" class="has-text-light"
				   	   style="font-weight: bold;">Login</a>
			<a href="/register" class="has-text-light"
				style="font-weight: bold">Register</a>
		{/if}
	</div>
</div>

<style>
	#wrapper {
		display: flex;
		align-items: center;
		background-color: #444444;
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
