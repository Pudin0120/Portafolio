# ServiPerfiles Backend — Architecture and Development

The backend is a Python API built with FastAPI. Its documentation describes a **hexagonal architecture (ports and adapters)** that keeps domain rules independent from frameworks, persistence, and external services.

## Stack recorded in this repository

- Python
- FastAPI and Uvicorn
- Pydantic and pydantic-settings
- SQLAlchemy and PostgreSQL
- Alembic for database migrations
- Firebase Admin
- dependency-injector
- pytest and HTTPX
- Docker Compose, Task, Infisical, and Traefik

The exact installed versions are resolved from the dependency constraints and project environment. The requirements file currently uses minimum-version constraints rather than a fully pinned lock file.

## Prerequisites

1. Docker Engine and Docker Compose.
2. [Task](https://taskfile.dev/) for repeatable development commands.
3. [Infisical CLI](https://infisical.com/docs/cli/overview) and access to the project secrets.
4. Git.

Authenticate with Infisical before running tasks that inject secrets:

    infisical login
    infisical init

## Quick start

From this directory:

    task dev-up
    task dev-watch

To check service status or view logs:

    task dev-ps
    task dev-logs

Run the automated tests in the development backend container:

    task dev-test

To pass pytest arguments:

    task dev-test -- tests/domain

The Taskfile is the authoritative list of available tasks. Check it before using commands from older notes.

## Local service addresses

The current development documentation describes these local endpoints:

| Service | Address |
| --- | --- |
| API | http://localhost |
| API documentation | http://localhost/docs |
| Scalar documentation | http://localhost/scalar |
| Traefik dashboard | http://localhost:8080 |
| PostgreSQL | localhost:5432 |

Actual availability depends on the selected Compose file, environment, and container health.

## Architecture

The codebase is organized around three layers:

### Domain — app/domain

Contains business concepts, entities, value objects, builders, and repository abstractions. It should not import application or infrastructure modules.

### Application — app/application

Contains use cases, DTOs, and mappers. Use cases coordinate business operations and depend on domain abstractions rather than concrete database or web implementations.

### Infrastructure — app/infrastructure

Contains FastAPI routers, persistence adapters, external integrations, and dependency wiring. This is where framework-specific and infrastructure-specific implementations belong.

### Request flow

1. A FastAPI router validates incoming data and creates a DTO.
2. The router delegates the operation to an application use case.
3. The use case applies domain rules and uses repository interfaces.
4. Infrastructure adapters implement persistence and external integrations.
5. The result is mapped to a response DTO and serialized by FastAPI.

## Development conventions

- Keep HTTP routing and serialization concerns out of domain entities.
- Do not make domain or application modules depend on infrastructure implementations.
- Use DTOs at application boundaries; do not expose persistence entities as API contracts.
- Register concrete dependencies in the composition root/container.
- Add domain unit tests, use-case tests, and API/integration tests for new behavior.
- Keep migrations reviewable and backward-compatible where possible.
- Never commit secret values. Use Infisical or local-only environment files.

## Database and deployment references

- [Development workflow](docs/DEV_WORKFLOW.md)
- [Database seed and configuration](docs/DATABASE_SEED.md)
- [Migrations](docs/MIGRATIONS_README.md)
- [Authentication](docs/AUTHENTICATION_README.md)
- [Traefik deployment](docs/TRAEFIK_SETUP.md)
- [Cloudflare configuration](docs/CLOUDFLARE_SETUP.md)
- [Tests guide](tests/domain/README_TESTS.md)

## Production caution

The presence of a production Compose file or deployment guide does not by itself prove that a deployment is secure or healthy. Before deploying, run the documented verification task, review all injected secrets and exposed routes, apply database migrations, and verify service health after startup.
