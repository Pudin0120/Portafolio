#  AGENT GUIDELINES - SERVIPERFILES FRONTEND

This document provides the standard operating procedures and technical requirements for autonomous agents and developers working on the Serviperfiles Frontend repository. Adherence to these guidelines is mandatory to ensure architectural consistency and scalability as we transition towards a SaaS-ready modular architecture.

##  Execution Environment & Tooling (BUN ONLY)

This project exclusively uses **Bun** as its package manager and runtime. Do not use NPM, Yarn, or Pnpm.

- **Package Manager:** Bun
- **Bundler:** Vite
- **Language:** TypeScript (Strict Mode)
- **Framework:** React 19
- **UI Framework:** HeroUI (formerly NextUI) + Tailwind CSS + Framer Motion
- **Icons:** Lucide-React
- **Testing:** Playwright (End-to-End)

###  Core Commands

- `bun install` - Install dependencies.
- `bun run dev` - Start the development server with **Infisical** secret injection.
- `bun run build` - Generate production bundle with **Infisical** secrets.
- `bun test` - Run all Playwright tests.
- `bun playwright test <path-to-test>` - Execute a specific test file.
- `bun playwright test --ui` - Open Playwright interactive UI.
- `bun x eslint .` - Run linting checks.

---

##  Secret Management (Infisical)

We no longer use local `.env` files for development secrets.

- **Requirement:** You MUST have the [Infisical CLI](https://infisical.com/docs/cli/overview) installed and configured.
- **Workflow:** The `dev` and `build` scripts are prefixed with `infisical run --`. This ensures secrets are injected directly into the process environment without touching the disk.
- **Setup:** Run `infisical auth login` if you haven't already, and ensure you have access to the project workspace.

---

##  SaaS-Ready Modular Architecture

The goal is to decouple the core logic from specific branding or business rules to allow the application to scale as a SaaS.

- **Feature-Based Modularization:** Logic must reside in isolated feature directories under `src/components/<feature>/`.
- **Agnostic Common Components:** `src/components/common/` must contain theme-agnostic, reusable primitives. Avoid hardcoding specific brand colors (like Orange) directly; use Tailwind theme variables instead.
- **Logic Decoupling:** Components must be thin. Delegate business logic to custom hooks (`src/hooks/`) and API interactions to services (`src/services/`).
- **State Management:** Use Context API for module-level state and avoid prop drilling. Ensure providers are scoped as tightly as possible.

---

##  Design System & Generic UI

Transitioning from a fixed "Orange & White" scheme to a themeable, generic system.

- **Themeable Tailwind:** Prioritize Tailwind's semantic classes (e.g., `primary`, `secondary`, `success`) over specific hex codes or hardcoded color names.
- **Component Library:** Utilize HeroUI's built-in theming capabilities. Custom UI components should be built as generic wrappers.
- **Modals:** Always use `@components/common/CenteredModal.tsx` for any modal implementation. This ensures consistent centering relative to the sidebar and proper mobile responsiveness.
- **Responsiveness:** Adopt a mobile-first approach. Use the `useIsMobile` hook for conditional rendering when Tailwind classes are insufficient.
- **Animations:** Use Framer Motion for subtle transitions (FadeIn, Slide). Maintain professional motion curves.

---

##  Code Style & TypeScript Guidelines

### 1. Imports & Path Aliases

Always use the path aliases defined in `tsconfig.json`.

- `@/*`: `src/*`
- `@components/*`: `src/components/*`
- `@hooks/*`: `src/hooks/*`
- `@services/*`: `src/services/*`
- `@shared/*`: `src/types/*`
- `@utils/*`: `src/utils/*`
- `@context/*`: `src/context/*`

### 2. TypeScript (Strict Mode)

- **Zero Tolerance for `any`:** Use `unknown` or define proper interfaces.
- **Interfaces vs. Types:** Use `interface` for object structures and `type` for unions or primitives.
- **Component Props:** Every component must have an explicitly defined `Props` interface.

### 3. Error Handling

- Use the centralized `apiClient.ts` which implements `ApiError` logic.
- Always provide user feedback for failed operations using `UndoToast` or error-state components.
- **Never** use empty `catch (e) {}` blocks.

### 4. Code Quality & Cleanup

- **No Localhost:** Never hardcode URLs. Use `import.meta.env.VITE_API_URL`.
- **Debugging:** Remove all `console.log`, `alert`, and `debugger` statements before submitting a PR.
- **Linting:** Resolve all ESLint warnings and errors.

---

##  Critical Restrictions

1. **No NPM/Yarn:** Only Bun is permitted.
2. **No New Markdown:** Do not create new `.md` files unless specifically requested.
3. **No Inline Styles:** Use Tailwind CSS for all styling.
4. **No Direct Firebase in Components:** All Firebase logic must reside in `src/services/firebase.ts` or feature-specific services.
5. **No Proactive Commits:** NEVER execute `git commit` or `git push` unless the user explicitly requests it. Analyze, suggest, and edit code, but leave the version control actions to the user.

###  Reasoning & Professional Conduct

As an AI agent, you are expected to act as a Senior Architect.

- **Use Skills Proactively:** Always utilize specialized agent skills (e.g., `typescript`, `react-19`, `heroui-react`, `systematic-debugging`) whenever relevant to the task to ensure best practices and project standards are met.

###  Branching Strategy

Before starting any new requirement or refactor:

1. **Always start from the `dev` branch.**
2. **Create a dedicated feature branch** using the naming convention: `feature/short-description` or `fix/short-description`.
3. **Never work directly on `main` or `dev`.**
4. All logic must be modular and SaaS-oriented. If you encounter hardcoded branding or tightly coupled logic, proactively suggest and implement refactors.
