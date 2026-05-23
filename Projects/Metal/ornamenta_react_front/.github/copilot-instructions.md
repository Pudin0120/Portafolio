# GitHub Copilot Chat Instructions - Frontend

Este proyecto **no utiliza NPM**.  
**Nunca ejecutes ni sugieras comandos con NPM o Yarn.**  
El proyecto utiliza **Bun** como gestor de paquetes y entorno de ejecucion.

---

##  Entorno y ejecucion
- Todas las pruebas, builds o ejecuciones deben hacerse con **Bun**, no con NPM ni Yarn.
- Ejemplos valids:  
  - `bun run dev`  
  - `bun test`  
  - `bun install`
- **Nunca uses `npm run`, `npm start` ni `yarn`.**
- **No uses referencias directas a localhost.**  
  Siempre usa las **variables de entorno** definidas para apuntar al backend u otros servicios.
- El empaquetador del proyecto es **Vite**.  
  Antes de ejecutar o sugerir un comando de desarrollo, **verifica que se esta corriendo con Vite y el entorno WAN**.
- Si necesitas levantar el entorno localmente, usa el flujo correcto con **Bun + Vite**, **nunca con NPM**.

---

##  Estilo visual
- Los **colores corporativos** son **naranja** y **blanco**.
- Evita sugerir o generar componentes con tonos azules u otros distintos al esquema corporativo.
- Los botones y paneles deben mantener el **estilo base en naranja**, siguiendo la guia visual existente.
- Antes de proponer nuevos estilos o componentes, **revisa los paneles y componentes ya implementados**.

---

##  Desarrollo con TypeScript y TFX
- El proyecto usa **TypeScript estricto** (`"strict": true` en `tsconfig.json`).
- **No relajes las reglas de tipado.** Manten el codigo fuertemente tipado.
- Se utiliza **TFX** para la arquitectura de componentes.
- Antes de create un componente grande o con demasiadas lineas:
  - **Dividelo** en subcomponentes reutilizables y legibles.
- No generes **codigo duplicado**, **componentes monoliticos** ni **logica mezclada**.

---

##  Calidad del codigo
- **No quiero errores del linter.**  
  Verifica y corrige cualquier problema antes de marcar una task como completa.
- El codigo debe ser limpio, modular y consistente.
- **No generes ni propongas archivos Markdown.**  
  La documentacion en ese formato **no se utiliza** en este proyecto.
- **Evita el uso de `any`** o la supresion de tipos salvo casos completamente justificados.

---

##  Depuracion
- Puedes usar `console.log` durante el desarrollo.
- Una vez que una task este aprobada, **elimina todos los `console.log`** para mantener el codigo limpio.
- No uses `alert` o `prompt`; usa logs o herramientas de depuracion.

---

##  Conexion con el backend
- Nunca uses `localhost` en peticiones HTTP o WebSocket.
- Usa siempre las **variables de entorno** (`import.meta.env`) definidas por **Vite** para las URLs del backend.
- Asegurate de que las llamadas cumplan con los contratos y endpoints del backend.
- Verifica los tipos de respuesta y los datos antes de modificar cualquier request.

---

##  Restricciones finales
- **Nunca uses NPM ni Yarn.**
- **Nunca apuntes a localhost.**
- **Nunca generes archivos Markdown.**
- Usa **Bun + Vite + TypeScript estricto (TFX)**.
- Prioriza componentes pequenos, reutilizables y coherentes con el estilo naranja-blanco de la marca.
- Verifica siempre los errores del linter antes de completar una task.
