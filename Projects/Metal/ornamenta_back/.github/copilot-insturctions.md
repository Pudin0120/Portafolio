# GitHub Copilot Chat Instructions

Este proyecto **no se ejecuta en local**, sino dentro de **contenedores Docker**.

---

## Entorno de ejecucion
- Antes de sugerir o ejecutar cualquier comando de Python, **verifica que se esta usando el contenedor correcto**.
- Examina el entorno con `docker ps` y utiliza el contenedor configurado en el archivo `docker-compose.dev.yml`.
- El contenedor tiene **hot reload activado**, por lo que no es necesario reiniciarlo manualmente tras cambios en el codigo.
- No ejecutes comandos fuera del entorno Docker.

---

## Taskfile (Task)
- El archivo `Taskfile.yml` contiene scripts automatizados esenciales y reemplaza al antiguo Makefile.
- Antes de proponer cualquier comando, **revisa las tasks disponibles en el Taskfile**.
- Ejemplos:
  - `task dev-test`  ejecuta los tests del proyecto.
  - `task dev-up`  levanta la aplicacion en su entorno.
- Si el flujo de work requiere otra accion (como migraciones, cargas o limpieza), **busca primero un target en el Taskfile** en lugar de create nuevos scripts.

---

## Reglas generales
- **No generes ni propongas archivos Markdown.** No se utiliza documentacion en ese formato en este proyecto.
- **No uses archivos `.sql`.** Toda interaccion con PostgreSQL debe hacerse mediante **SQLAlchemy ORM**.
- Evita cualquier referencia a documentacion Markdown, README u otros ficheros similares.

---

## Documentacion y docstrings
- La documentacion de la API se maneja con **Scalar**.
- Cada endpoint importante debe tener su **docstring correcto y actualizado**.
- Si Copilot modifica una function o endpoint:
  - Revisa que el docstring exista.
  - Actualiza los ejemplos, descripciones y tipos de retorno.
  - Manten consistencia entre los docstrings y la documentacion de Scalar.

---

## Buenas practicas de desarrollo
- Prioriza la **claridad y consistencia** sobre la brevedad.
- Evita errores de linting o formato (usa convenciones PEP 8).
- No ejecutes acciones que dependan del entorno local.
- No asumas que existen rutas absolutas en el host; todo ocurre dentro del contenedor.

---

## Contexto adicional
- El archivo `docker-compose.dev.yml` define el entorno y dependencias de desarrollo.
- El proyecto ya esta levantado con `task dev-up`.
- No generes configuraciones duplicadas ni modifiques la estructura base de los contenedores.
