import process from "node:process";
import { fileURLToPath, URL } from "node:url";
import react from "@vitejs/plugin-react-swc";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";
import { VitePWA } from "vite-plugin-pwa";

const API_URL = process.env.VITE_API_URL;

export default defineConfig({
	plugins: [
		react(),
		tailwindcss(),
		VitePWA({
			registerType: "prompt",
			injectRegister: null,

			// SW personalizado en /public/sw.ts
			srcDir: "public",
			filename: "sw.ts",
			strategies: "injectManifest",

			injectManifest: {
				globPatterns: ["**/*.{js,css,html,ico,png,svg,woff2}"],
				maximumFileSizeToCacheInBytes: 5000000,
			},

			manifest: {
				name: "ServiPerfiles A Y C",
				short_name: "ServiPerfiles",
				description: "Workshop management system for profiles and metal carpentry",
				theme_color: "#ffffff",
				background_color: "#ffffff",
				display: "standalone",
				start_url: "/",
				icons: [
					{
						src: "/Logo-192.png",
						sizes: "192x192",
						type: "image/png",
						purpose: "any",
					},
					{
						src: "/Logo-512.png",
						sizes: "512x512",
						type: "image/png",
						purpose: "any",
					},
					{
						src: "/Logo-512.png",
						sizes: "512x512",
						type: "image/png",
						purpose: "maskable",
					},
				],
			},

			devOptions: {
				enabled: true,
				type: "module",
				navigateFallback: "/index.html",
			},
		}),
	],

	resolve: {
		alias: {
			"@": fileURLToPath(new URL("./src", import.meta.url)),
			"@components": fileURLToPath(
				new URL("./src/components", import.meta.url),
			),
			"@pages": fileURLToPath(new URL("./src/pages", import.meta.url)),
			"@hooks": fileURLToPath(new URL("./src/hooks", import.meta.url)),
			"@services": fileURLToPath(new URL("./src/services", import.meta.url)),
			"@providers": fileURLToPath(new URL("./src/providers", import.meta.url)),
			"@shared": fileURLToPath(new URL("./src/types", import.meta.url)),
			"@utils": fileURLToPath(new URL("./src/utils", import.meta.url)),
			"@context": fileURLToPath(new URL("./src/context", import.meta.url)),
			"@config": fileURLToPath(new URL("./src/config", import.meta.url)),
		},
		extensions: [".mjs", ".js", ".ts", ".jsx", ".tsx", ".json"],
	},

	server: {
		proxy: {
			"/api": {
				target: API_URL,
				changeOrigin: true,
				rewrite: (path) => path.replace(/^\/api/, ""),
			},
		},
	},
});
