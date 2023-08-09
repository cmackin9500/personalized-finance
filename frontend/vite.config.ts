import { sveltekit } from '@sveltejs/kit/vite';
import { multicssclass } from 'svelte-multicssclass';
import { defineConfig } from 'vite';

export default defineConfig({
    server: {
    	proxy: {
        	"/api": {
            	target: "http://127.0.0.1:8080",
            	changeOrigin: true,
            	//rewrite: (path) => path.replace(/^\/api/, '')
        	}
    	},
    	host: true
	},
	plugins: [multicssclass(), sveltekit()]
});
