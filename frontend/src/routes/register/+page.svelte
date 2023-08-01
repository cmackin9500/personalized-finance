<script>
	import Toolbar from "$lib/Toolbar.svelte";
	import {JSONPostRequest} from "$lib/util.js";

	let username;
	let password;
	let confirmPassword;
	let email;

	function registerUser() {
		if (password !== confirmPassword) {
			alert("Passwords do not match");
			return;
		}

		JSONPostRequest("/api/registerUser", {

		})	
	}

</script>

<Toolbar/>

<h1>Register</h1>

<form class="form" on:submit={registerUser}>
	<label>Username</label>
	<input class="input" bind:value={username}/>

	<label>Password</label>
	<input class="input" bind:value={password}/>

	<label>Confirm password</label>
	<input class="input" bind:value={confirmPassword}/>

	<label>Email address</label>
	<input class="input" bind:value={email}/>

	<button class="button">Register</button>
</form>
