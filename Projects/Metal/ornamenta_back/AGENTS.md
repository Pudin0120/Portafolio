# AGENT GUIDELINES - SERVIPERFILES ERP (SaaS READY)

##  Execution Environment
- **Docker Only**: No local execution. Use `docker compose -f docker-compose.dev.yml`.
- **Secret Management**: We use **Infisical** for environment variables in development. 
  - If `.env` is missing, commands MUST be prefixed with `infisical run --` (handled automatically by the `Taskfile`).
  - Ensure you are logged in (`infisical login`) and the project is initialized.
- **Taskfile (Mandatory)**: Cross-platform runner. Use `task dev-up`, `task dev-test`, `task dev-watch`.
- **Setup Task**: If not installed, run `sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b ~/.local/bin`.
- **Running Tests**: ALWAYS use `task dev-test` for all tests, or `docker exec -it fastapi-backend-dev pytest tests/path/to/test.py` for a single test.
- **LSP & DX**: We use a stubbing strategy to avoid local `.venv`.
  - Stubs are located in `.docker-stubs/site-packages` (synced from container).
  - Configuration is managed via `pyrightconfig.json`.
  - To update stubs after adding dependencies: `docker cp fastapi-backend-dev:/usr/local/lib/python3.14/site-packages/ .docker-stubs/`.

##  Modular Architecture (ERP Scale)
The system is moving towards a **Modular Monolith** (SaaS ready). Every agent MUST respect these boundaries:
1. **Bounded Contexts**: Keep modules (Inventory, Payroll, CRM, Accounting) isolated. 
   - Cross-module communication ONLY via **Domain Events** or Service Interfaces.
   - NO direct database joins between tables of different modules.
2. **Layered DDD**:
   - **Domain**: Pure logic, no framework leaks. Use Value Objects for everything (Money, Email, DocumentNumber).
   - **Application**: Use Cases orchestrating domain logic.
   - **Infrastructure**: Implementation details (SQLAlchemy, Firebase, External APIs).

##  SaaS & Multitenancy
This is a SaaS system. Data isolation is non-negotiable:
- **Tenant Isolation**: Every database table MUST have a `tenant_id` (UUID).
- **Filtering**: All queries MUST include a `.where(Model.tenant_id == current_tenant_id)` filter.
- **Context Propagation**: Use the `current_user` dependency to extract the `tenant_id`.

##  Python & Code Style
- **Naming**: `PascalCase` (Classes), `snake_case` (Functions/Vars). DTOs MUST end in `DTO`.
- **Typing**: 100% mandatory type hints. Use `Optional`, `List`, `Dict` and custom types.
- **Mappers**: Use static mappers in `app/application/mappers/`. Never return Domain Entities in Routers.

##  Event-Driven Data Flow
For ERP consistency, use events:
- **Domain Events**: Raised inside entities when something important happens (e.g., `StockFinished`, `InvoiceGenerated`).
- **Transactionality**: Use the `TransactionMiddleware`. Automatic commit on success, rollback on error.
- **Audit**: Every write operation must be traceable. Do not delete data; use **Soft Deletes** (`is_deleted` flag).

##  Database (SQLAlchemy 2.0)
- **Style**: Use the new `select()` and `scalars()` syntax.
- **Migrations**: Alembic only. Every migration must be reversible.
- **NO RAW SQL**: Unless performance requires it (must be approved and documented).

##  Security & Permissions
- **Firebase Auth**: Authentication only.
- **RBAC**: Permissions are managed in `app/domain/permissions.py`. Check roles/permissions in every Use Case or Router.

##  Branching Strategy (Simplified GitFlow)

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

##  Versions and Tags (Semantic Versioning)

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

##  Repository Cleanup

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

##  Daily Useful Commands

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

##  Prohibitions
- **NO Framework Leaks**: Domain layer must not import `fastapi`, `pydantic`, or `sqlalchemy`.
- **NO logic in Routers**: Routers are just entry points.
- **NO Markdown**: Don't create generic `.md` files. Use code comments and docstrings.
- **NO local python commands**: Everything runs inside Docker.
- **NO Spanish in Commits**: All commits must be in English.
