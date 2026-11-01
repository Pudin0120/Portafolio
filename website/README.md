# Joseff Laverde — Portfolio Website

Professional portfolio built with Astro, TypeScript, and Tailwind CSS, configured for GitHub Pages in the Pudin0120/Portafolio repository.

## Stack and declared versions

| Technology | Version |
| --- | --- |
| Astro | 7.4.4 |
| TypeScript | 7.0.2 |
| Tailwind CSS | 4.3.3 |
| @tailwindcss/vite | 4.3.3 |
| Node.js in CI | 24 |

## Run locally

From this directory:

```bash
npm install
npm run dev
```

## Build and preview

```bash
npm run build
npm run preview
```

## Features

- Responsive homepage with a midnight-blue, cyan, and gold visual identity.
- Curated homepage featuring selected engineering projects rather than the entire archive.
- Interactive terminal: help, about, stack, projects, contact, and clear.
- Complete project archive with category filters and search.
- Static project detail pages.
- Global search with Ctrl + K / Cmd + K.
- English-language contact page and navigation.
- Visible keyboard focus and support for prefers-reduced-motion.

## GitHub Pages deployment

1. Open the Pudin0120/Portafolio repository.
2. Go to Settings → Pages.
3. Under Build and deployment → Source, select GitHub Actions.
4. Save and check Actions → Deploy portfolio website.

Expected URL: https://pudin0120.github.io/Portafolio/

The astro.config.mjs file already sets the site domain and repository base path.