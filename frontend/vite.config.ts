import { sveltekit } from '@sveltejs/kit/vite';
import { multicssclass } from 'svelte-multicssclass';
import { defineConfig } from 'vite';

export default defineConfig({
    server: {
    	proxy: {
        	"/api": {
            	target: "http://localhost:8080",
            	changeOrigin: true,
            	//rewrite: (path) => path.replace(/^\/api/, '')
        	}
    	}
	},
	plugins: [multicssclass(), sveltekit()]
});
