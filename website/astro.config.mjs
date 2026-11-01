import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://pudin0120.github.io',
  base: '/Portafolio',
  vite: { plugins: [tailwindcss()] },
});