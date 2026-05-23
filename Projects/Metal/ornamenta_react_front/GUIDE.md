#  Guia de Flujo de Work - Serviperfiles Frontend

Bienvenido al equipo! Para mantener el codigo limpio, escalable y profesional, seguimos este flujo de work basado en estandares de la industria.

##  Estrategia de Ramas (GitFlow Simplificado)

Nuestra estructura de ramas se divide en:

### 1. Ramas Principales (Permanentes)

- **`main`**: Es el codigo en produccion. Solo contiene codigo estable y tagueado con versiones (`v0.9.0`, `v1.0.0`, etc.). **Nunca** se pushea directamente aca.
- **`dev`**: Rama de integracion. Aca vive el desarrollo del dia a dia. Es el "borrador" de la proxima version estable.

### 2. Ramas de Tasks (Temporales)

Usamos prefijos para identificar que estamos haciendo:

- **`feature/nombre-task`**: Para nuevas funcionalidades (ej: `feature/login-refactor`). Salen de `dev` y vuelven a `dev`.
- **`fix/description-bug`**: Para arreglar errores encontrados en `dev`.
- **`hotfix/urgencia`**: Solo para errores criticos que estan en `main` y deben arreglarse YA sin pasar por el ciclo normal de `dev`.

---

##  Versiones y Tags (Semantic Versioning)

Usamos el formato `vMAJOR.MINOR.PATCH` (ej: `v1.2.3`):

1. **MAJOR (1)**: Cambios grandes que rompen compatibilidad.
2. **MINOR (2)**: Nuevas funcionalidades que no rompen lo anterior.
3. **PATCH (3)**: Arreglos de bugs menores.

### Como create una Release?

Cuando `dev` esta listo para ser una version (ej: `0.9.0`):

1. `git checkout main`
2. `git merge dev`
3. `git tag -a v0.9.0 -m "Mensaje descriptivo"`
4. `git push origin main --tags`

---

##  Limpieza del Repositorio

Para mantener la casa limpia, borramos las ramas que ya fueron mergeadas.

### Borrar ramas remotas

Si ves ramas viejas en el servidor que ya no sirven:

```bash
git push origin --delete nombre-de-la-rama
```

### Borrar ramas locales

```bash
git branch -d nombre-de-la-rama
```

---

##  Comandos Utiles para el Dia a Dia

### Empezar una nueva task:

```bash
git checkout dev
git pull origin dev
git checkout -b feature/mi-gran-mejora
```

### Subir tus cambios (siempre a tu rama):

```bash
git add .
git commit -m "feat: description clara de lo que hiciste"
git push origin feature/mi-gran-mejora
```

---

**Nota:** Este proyecto usa **Bun**. No uses `npm` ni `yarn`.
A darle con todo, loco! 
