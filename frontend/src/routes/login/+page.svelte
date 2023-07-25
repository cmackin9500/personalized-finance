<script>
	import Toolbar from "$lib/Toolbar.svelte";
	import { JSONPostRequest } from "$lib/util.js";

	let username = "";
	let password = "";

	function loginHandler(event) {
		event.preventDefault();
		JSONPostRequest("/api/userLogin", {username, password})
	}
</script>

<Toolbar/>

<br>

<div class="card container">
	<form class="card-content" on:submit={loginHandler}>
		<label>Username</label>
		<input class="input" bind:value={username}/>

		<label>Password</label>
		<input class="input" bind:value={password}/>

		<button>Login</button>
	</form>
</div>
