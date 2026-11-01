# Joseff Laverde — Portfolio Website

Sitio profesional desarrollado con Astro, TypeScript y Tailwind CSS, configurado para GitHub Pages dentro de Pudin0120/Portafolio.

## Stack y versiones declaradas

| Tecnología | Versión |
| --- | --- |
| Astro | 7.4.4 |
| TypeScript | 7.0.2 |
| Tailwind CSS | 4.3.3 |
| @tailwindcss/vite | 4.3.3 |
| Node.js en CI | 24 |

## Ejecutar localmente

Desde esta carpeta:

```bash
npm install
npm run dev
```

## Compilar y probar

```bash
npm run build
npm run preview
```

## Funcionalidades

- Portada responsive con identidad azul noche, cian y dorado.
- Terminal interactiva: help, about, stack, projects, contact y clear.
- Catálogo de proyectos con filtros y búsqueda.
- Fichas estáticas de proyectos.
- Buscador global Ctrl + K / Cmd + K.
- Página de contacto.
- Foco visible y respeto a prefers-reduced-motion.

## Publicación en GitHub Pages

1. Abre el repositorio Pudin0120/Portafolio.
2. Ve a Settings → Pages.
3. En Build and deployment → Source, selecciona GitHub Actions.
4. Guarda y revisa Actions → Deploy portfolio website.

Dirección esperada: https://pudin0120.github.io/Portafolio/

El archivo astro.config.mjs ya configura el dominio y la ruta base del repositorio.
