<script>
	import Toolbar from "$lib/Toolbar.svelte";
	import {JSONPostRequest} from "$lib/util.js";
	import { goto } from "$app/navigation";

	let username;
	let password;
	let confirmPassword;
	let email;

	let errorMessage = "";

	function registerUser() {
		errorMessage = "";
		if (password !== confirmPassword) {
			alert("Passwords do not match");
			return;
		}

		JSONPostRequest("/api/registerUser", {
			username,
			password,
			email
		})	
			.then(data => {
				goto("/emailConfirmation");
			})
			.catch(err => {
				errorMessage = err.cause;
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

	{#if errorMessage.length > 0}
		<div class="content">{errorMessage}</div>
	{/if}

	<button class="button">Register</button>
</form>
