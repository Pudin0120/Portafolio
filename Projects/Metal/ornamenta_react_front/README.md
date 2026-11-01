# ServiPerfiles — React Frontend

The frontend is a React single-page application built with TypeScript and Vite. Its repository configuration also includes a PWA service worker and Firebase-based authentication.

## Technology stack

| Area | Technology |
| --- | --- |
| UI | React 19, HeroUI, Tailwind CSS 4 |
| Language | TypeScript |
| Development server and bundler | Vite |
| Authentication | Firebase |
| Client routing | React Router |
| PWA | vite-plugin-pwa with a custom service worker |
| E2E testing | Playwright |
| Secrets | Infisical CLI |
| Package manager | Bun |

Declared dependency ranges are in package.json; use the repository's Bun lock file to reproduce the resolved dependency set.

## Prerequisites

- Bun (use the version expected by the project lock file).
- Infisical CLI.
- Access to the ServiPerfiles Infisical project and its required frontend variables.

Authenticate before running the scripts:

    infisical auth login

## Installation and development

    bun install
    bun run dev

The dev, build, and preview scripts run through Infisical. Make sure the correct project and environment are selected.

## Production build and preview

    bun run build
    bun run preview

## Browser tests

The project declares Playwright scripts:

    bun run test
    bun run test:ui
    bun run test:headed
    bun run test:report

Some named test scripts target specific existing test IDs. Check the current test directory before relying on an individual test alias.

Install the Playwright browsers when running the suite on a fresh machine:

    bunx playwright install --with-deps

## Configuration

The checked-in .env.example documents the public Firebase web configuration and VITE_API_URL. Copy it to a local environment file only when using a local workflow, and keep real values out of commits.

Firebase web configuration values are delivered to the browser; they are not server secrets. Protect Firebase resources with Authentication, Security Rules, authorized domains, and appropriate API restrictions. Never place Firebase service-account credentials or private server keys in frontend variables.

The Vite configuration reads VITE_API_URL to configure the development /api proxy. Set it to the backend origin for local development.

## Project structure and conventions

- Read [ARCHITECTURE.md](./ARCHITECTURE.md) before changing feature boundaries.
- Follow [GUIDE.md](./GUIDE.md) for the repository's Git workflow.
- Follow [AGENTS.md](./AGENTS.md) for coding conventions used by the project.
- Keep API access in service modules and reuse the existing authentication and role-management hooks.
- Add or update Playwright coverage for user-visible flows.

## Scope note

The project documentation describes a role-based workforce/workshop management application. Confirm available API endpoints and permissions in the current source before integrating a new screen or assuming an endpoint exists.
