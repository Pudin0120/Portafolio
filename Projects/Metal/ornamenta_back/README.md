# Project Architecture - ServiPerfiles

This document describes the project architecture, following the principles of **Hexagonal Architecture** (also known as Ports and Adapters). The goal is to separate business logic (domain) from infrastructure concerns (frameworks, databases, etc.), allowing the application core to be independent and easily testable.

## Y"s Documentation

- **[Architecture](#layer-structure)** - This document
- **[Development Workflow](docs/DEV_WORKFLOW.md)** - a **Complete development guide with hot reload**
- **[Deployment Guide with Traefik](docs/TRAEFIK_SETUP.md)** - Development and production deployment
- **[Cloudflare Configuration](docs/CLOUDFLARE_SETUP.md)** - SSL/TLS with Cloudflare
- **[Authentication](docs/AUTHENTICATION_README.md)** - Authentication system
- **[Database](docs/DATABASE_SEED.md)** - DB Seed and configuration
- **[Quick Reference](docs/QUICK_DEV_REFERENCE.md)** - Quick command reference

## Y" Prerequisites

Before you begin, ensure you have the following installed:

1.  **Docker & Docker Compose**: The entire environment runs in containers.
2.  **[Task](https://taskfile.dev/)**: Our command runner (replaces `make`).
3.  **[Infisical CLI](https://infisical.com/docs/cli/usage)**: Used for managing environment variables and secrets safely.
    *   `infisical login`
    *   `infisical init` (select the appropriate project)
4.  **Git**: For version control.

## Ys Quick Start

### Local Development with Hot Reload Y"

```bash
# Using Task (cross-platform, mandatory)
task dev-up

# Watch logs in real-time (to see hot reload in action)
task dev-watch
```

### Yi Installation of Task
If you don't have `task` installed:
```bash
# Linux/macOS
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b ~/.local/bin

# Windows (PowerShell)
# iwr -useb https://taskfile.dev/install.ps1 | iex
# or download from https://github.com/go-task/task/releases
```

**Available URLs:**

- API: <http://localhost>
- Docs: <http://localhost/docs>
- Scalar Docs: <http://localhost/scalar>
- Traefik Dashboard: <http://localhost:8080>
- PostgreSQL: localhost:5432

**a Hot Reload Enabled:**

- Edit any `.py` file in your editor
- Save the file
- FastAPI reloads automatically
- No need to restart containers

Y"- **Read [docs/DEV_WORKFLOW.md](docs/DEV_WORKFLOW.md) for the full development guide**

### Production

```bash
# Verify configuration
task prod-verify

# Deploy
task prod-up
```

For more details, check **[docs/TRAEFIK_SETUP.md](docs/TRAEFIK_SETUP.md)**.

## Y Branching Strategy (Simplified GitFlow)

Our branch structure is divided into:

### 1. Main Branches (Permanent)

- **`main`**: Production code. Only contains stable code tagged with versions (`v0.9.0`, `v1.0.0`, etc.). **Never** push directly here.
- **`dev`**: Integration branch. This is where daily development lives. It is the "draft" for the next stable version.

### 2. Task Branches (Temporary)

We use prefixes to identify what we are doing:

- **`feature/task-name`**: For new features (e.g., `feature/login-refactor`). Branch out from `dev` and merge back into `dev`.
- **`fix/bug-description`**: To fix bugs found in `dev`.
- **`hotfix/urgency`**: Only for critical bugs in `main` that must be fixed IMMEDIATELY without going through the normal `dev` cycle.

---

## Yi Versions and Tags (Semantic Versioning)

We use the `vMAJOR.MINOR.PATCH` format (e.g., `v1.2.3`):

1. **MAJOR (1)**: Breaking changes.
2. **MINOR (2)**: New features that are backward compatible.
3. **PATCH (3)**: Minor bug fixes.

### How to create a Release?

When `dev` is ready to become a version (e.g., `0.9.0`):

1. `git checkout main`
2. `git merge dev`
3. `git tag -a v0.9.0 -m "Descriptive message"`
4. `git push origin main --tags`

---

## Y Repository Cleanup

To keep the house clean, we delete branches that have already been merged.

### Delete remote branches

If you see old branches on the server that are no longer needed:

```bash
git push origin --delete branch-name
```

### Delete local branches

```bash
git branch -d branch-name
```

---

## Yi Daily Useful Commands

### Start a new task

```bash
git checkout dev
git pull origin dev
git checkout -b feature/my-great-improvement
```

### Upload your changes (always to your branch)

**CRITICAL: All commit messages MUST be in English.**

```bash
git add .
git commit -m "feat: clear description of what you did"
git push origin feature/my-great-improvement
```

---

## Layer Structure

The project is organized into three main layers:

1. **`app/domain`**: The heart of the application.
2. **`app/application`**: The orchestration layer.
3. **`app/infrastructure`**: The infrastructure layer and implementation details.

Below is the purpose of each layer and how they relate to each other.

---

### 1. Domain Layer (`app/domain`)

This layer contains pure business logic and does not depend on any other layer. It is the core of the software and defines the rules and data structures that are fundamental to the problem being solved.

- **`models`**: Contains the main entities and business objects.
  - `product.py`: Represents a basic product or a component.
  - `composition.py`: Manages the relationship between composite products and their parts.
  - `material.py`: Defines raw materials used in products.
- **`value_objects`**: Contains immutable objects representing domain attributes, such as `Dimensions`, `Money`, etc.
- **`repositories`**: Defines the **abstractions** (interfaces) for data storage and retrieval. For example, `ProductRepository` defines how products should be accessed, but not how it is implemented.
- **`builders`**: Responsible for creating complex domain objects.
  - `product_builder.py`: Builds product instances from raw data or components.

**Key Rule**: Code in `app/domain` **must not import** anything from `app/application` or `app/infrastructure`.

---

### 2. Application Layer (`app/application`)

This layer acts as an orchestrator. It contains the application **use cases**, which coordinate domain logic to perform specific tasks.

- **`use_cases`**: Each file represents an action the user can perform.
  - `quote_work.py`: Orchestrates a work quotation, calculating totals.
  - `create_material.py`: Adds a new material to the system.
- **`dto` (Data Transfer Objects)**: Simple objects used to transfer data between the infrastructure layer and the application layer. They contain no business logic.
- **`mappers`**: Responsible for converting domain objects to DTOs and vice-versa.

**Key Rule**: The application layer depends on the domain, but **must not depend** on infrastructure. It uses interfaces (repositories) defined in the domain to interact with data.

---

### 3. Infrastructure Layer (`app/infrastructure`)

This layer contains the **concrete implementations** of the abstractions defined in the domain and application. It is the outermost and most volatile layer, as it depends on specific technologies and frameworks.

- **`adapters`**:
  - `repositories`: Contains the **implementations** of the repositories. For example, `postgres_user_repository.py` implements the domain interface for PostgreSQL.
  - `rest`: Contains the API _routers_ or _controllers_ (using FastAPI).
- **`containers.py`**: The **Composition Root** of the application. Uses `dependency-injector` to "wire" all dependencies. This is where the concrete implementation for each interface is decided.
- **`main.py`**: Application entry point. Configures and starts the web server.

**Key Rule**: This layer depends on both the domain and application, but neither depends on infrastructure.

---

## Request Flow: Generic Example

To illustrate how layers interact, let's look at a generic flow:

1. **API (Infrastructure)**: A client sends an HTTP request to an endpoint.
    - The FastAPI router receives the request.
    - Validates and converts the request body into a DTO.
2. **Use Case (Application)**: The router calls the corresponding use case.
    - `containers.py` injects the necessary dependencies into the use case.
    - The use case executes business logic.
3. **Domain**:
    - The use case uses domain entities and value objects.
    - Entities contain business logic and domain rules.
4. **Repositories (Infrastructure)**:
    - When persistent data access is needed, domain repository abstractions are used.
    - The dependency container ensures these calls are directed to concrete implementations in `app/infrastructure/adapters/repositories`.
5. **Response (Application -> Infrastructure)**:
    - The use case converts domain objects into response DTOs using _mappers_.
    - The FastAPI router serializes the DTOs to JSON and sends them as a response to the client.

## Best Practices Guide and Next Steps

To continue developing the project consistently with Hexagonal Architecture, keep the following in mind:

### What to **DO** Y'

1. **Start with the Domain**: When adding a new feature, first define the models, `value_objects`, and repository interfaces in `app/domain`.
2. **Add Use Cases**: Create a new use case in `app/application` that orchestrates domain logic.
3. **Implement in Infrastructure**: Finally, implement the details:
    - Create or modify API _routers_.
    - Implement repositories (e.g., connecting to a real database like PostgreSQL).
    - Update `containers.py` to register new dependencies.
4. **Use DTOs**: Always communicate between infrastructure and application layers via DTOs.
5. **Dependency Injection**: Let the container handle building and injecting dependencies. Use cases and domain services should receive their dependencies in the constructor.

### What **NOT** to DO Y'Z

1. **No business logic in routers**: Routers should only handle HTTP communication and delegate work to use cases.
2. **No domain dependency on infrastructure**: Never import an `infrastructure` or `application` module from `domain`. For example, the domain should not know if data comes from JSON, a SQL database, or an external API.
3. **No direct use of implementations**: Application and domain layers must depend on **abstractions** (repository interfaces), not concrete implementations.
4. **No mixing DTOs with domain models**: Domain models have business logic; DTOs are only for transporting data.

### Suggested Next Steps

1. **Add More Tests**:
    - **Unit tests for the domain**: Easiest to write, as they have no external dependencies.
    - **Integration tests for use cases**: Use mocks or stubs for repositories and test orchestration logic.
    - **E2E (End-to-End) tests**: Test the full API with a real database.
2. **Refine Domain Logic**: Further isolate business rules from application flow.

---

