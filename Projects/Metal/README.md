# ServiPerfiles / Ornamenta — Metal Workspace

This workspace contains a full-stack workshop and workforce management platform. The repository folder is named **Metal**; the application documentation and frontend identify the product as **ServiPerfiles**.

## Architecture at a glance

| Component | Location | Main technologies |
| --- | --- | --- |
| Backend API | **ornamenta_back/** | Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, Firebase Admin |
| Web application | **ornamenta_react_front/** | React 19, TypeScript, Vite, HeroUI, Tailwind CSS 4 |
| Local infrastructure | Backend Docker Compose files | Docker Compose, PostgreSQL, Traefik |
| Secret management | Infisical integration | Infisical CLI |

The backend documentation describes a hexagonal architecture with domain, application, and infrastructure layers. The frontend is a modular React application with Firebase authentication, role-based screens, and PWA support.

## Before you start

- Install Git and Docker with the Docker Compose plugin.
- Install [Task](https://taskfile.dev/) for the backend workflow.
- Install [Infisical CLI](https://infisical.com/docs/cli/overview) and obtain access to the project environment. Do not commit real credentials.
- Install Bun for frontend package management (the frontend README is the source of truth for its scripts).

## Backend quick start

    cd ornamenta_back
    infisical login
    task dev-up
    task dev-logs

The Taskfile starts the development Compose stack and injects environment values through Infisical. To run backend tests in the development container:

    task dev-test

Useful backend references:

- [Backend architecture and conventions](ornamenta_back/README.md)
- [Development workflow](ornamenta_back/docs/DEV_WORKFLOW.md)
- [Authentication](ornamenta_back/docs/AUTHENTICATION_README.md)
- [Database migrations](ornamenta_back/docs/MIGRATIONS_README.md)
- [Deployment with Traefik](ornamenta_back/docs/TRAEFIK_SETUP.md)

## Frontend quick start

    cd ornamenta_react_front
    bun install
    infisical auth login
    bun run dev

The frontend scripts call Infisical before Vite. Ensure the required frontend variables are available in the selected Infisical environment. For a production bundle, use:

    bun run build

Useful frontend references:

- [Frontend setup](ornamenta_react_front/README.md)
- [Architecture](ornamenta_react_front/ARCHITECTURE.md)
- [Development guide](ornamenta_react_front/GUIDE.md)
- [AI agent conventions](ornamenta_react_front/AGENTS.md)

## Engineering notes

- Keep secrets in Infisical or local environment files; never commit service-account JSON files, API keys, passwords, or production credentials.
- Keep domain rules independent of FastAPI, database adapters, and UI frameworks.
- Put new business workflows in backend use cases and expose them through thin API routers.
- Keep frontend API calls in service modules and authentication/role checks in the established auth and routing layers.
- Add or update automated tests whenever behavior changes.

## Scope and verification

This directory contains the source workspace and documentation. A successful local build, a deployed environment, and production readiness are separate claims; verify each with the relevant backend tests, frontend build, and deployment checks before describing a release as production-ready.

Maintained as part of [Joseff Laverde's portfolio](https://github.com/Pudin0120).
