#  Arquitectura del Proyecto - ServiPerfiles

This project follows a **modular SaaS-oriented architecture**, designed to be scalable, maintainable, and decoupled from specific business rules or rigid branding.

##  Estructura de Directorios

```text
src/
 components/          # Componentes de la interfaz
    common/         # Agnostic primitives (buttons, modals, inputs)
    <feature>/      # Componentes aislados por funcionalidad (Login, Payroll, etc.)
 context/            # Proveedores de estado global (Auth, Theme)
 hooks/              # Reusable React logic
 services/           # Communication with APIs and external services (Firebase, backend API)
 types/              # Definiciones de interfaces y tipos TypeScript
 utils/              # Funciones de ayuda puras
```

##  Design Principles

### 1. Desacoplamiento (Logic vs. UI)

Components should be presentational whenever possible. Heavy logic belongs in **custom hooks**, and server communication belongs in **services**.

### 2. Agnostic Common Components

Los componentes en `src/components/common/` no deben conocer el contexto del negocio. Se basan en el sistema de temas de **HeroUI** y **Tailwind CSS**.

### 3. Secret Management

No se utilizan archivos `.env`. Se integra **Infisical** para inyectar secretos directamente en el proceso de `bun run dev` o `build`.

### 4. Flujo de Datos

- **Authentication**: Firebase Auth manages the JWT token.
- **Authorization**: El backend valida el token y provee el rol del user.
- **Estado**: Context API para estados que permean varios niveles; estado local para UI.

##  Core Technologies

- **React 19**: Aprovechando las nuevas APIs y el compilador.
- **HeroUI**: Biblioteca de componentes base.
- **Tailwind CSS 4**: Styled with semantic classes.
- **Bun**: Single runtime and package manager.
