#  Estructura del Proyecto - ServiPerfiles

Este document describe la nueva estructura organizada del proyecto despues de la limpieza.

##  Estructura de Directorios

```
serviperfiles_back/

 docs/                           #  Documentacion del proyecto
    README.md                   # Indice de documentacion
    AUTHENTICATION_README.md    # Sistema de autenticacion
    CLOUDFLARE_SETUP.md        # Configuration SSL/TLS
    DATABASE_SEED.md           # Configuration y seed de BD
    DEV_WORKFLOW.md            #  Guia de desarrollo
    PRE_DEPLOY_CHECKLIST.md    # Checklist pre-despliegue
    QUICK_DEV_REFERENCE.md     # Referencia rapida
    PROJECT_STRUCTURE.md       # Este document
    TRAEFIK_SETUP.md           # Configuration de Traefik

 scripts/                        #  Scripts de automatizacion
    backup_db.sh               # Backups de BD
    restore_db.sh              # Restaurar backups
    verify_setup.sh            # Verificar configuration
    setup-basic-auth.sh        # Configurar auth basica Traefik
    generate_traefik_password.sh # Generar password Traefik
    fix_and_seed_prod.sh       # Fix y seed en produccion
    migrate_task_hierarchy.py  # Migracion de jerarquia de tasks
    setup_auto_backup.sh       # Configurar backups automaticos
    setup_systemd_backup.sh    # Configurar servicio systemd para backups
    test_products_integration.sh # Tests de integracion de products
    verify_test_fix.sh         # Verificar fix de tests
    entrypoint.sh              #  Script de inicio del contenedor

 app/                            #  Codigo fuente (Arquitectura Hexagonal)
    domain/                    # Capa de dominio
       models/               # Modelos de negocio
       value_objects/        # Value objects
       repositories/         # Interfaces de repositorios
       builders/             # Builders
       factories/            # Factories
   
    application/               # Capa de aplicacion
       dto/                  # Data Transfer Objects
       mappers/              # Mappers
       services/             # Servicios de aplicacion
       use_cases/            # Casos de uso
   
    infrastructure/            # Capa de infraestructura
        adapters/             # Adaptadores (API, BD, etc.)
        builders/             # Builders de infraestructura
        containers.py         # Contenedor de inyeccion de dependencias

 database/                       #  Archivos de base de datos
    migrations/               # Migraciones (legacy, no usar)

 tests/                          #  Tests
    domain/                    # Tests de dominio
    application/               # Tests de aplicacion
    api/                       # Tests de API
    infraestructure/           # Tests de infraestructura

 traefik/                        #  Configuration de Traefik
    traefik.dev.yml            # Config desarrollo
    traefik.prod.yml           # Config produccion
    dynamic_conf.yml           # Config dinamica

 __pycache__/                    # Cache de Python (ignorado)

 main.py                         #  Entry point de la aplicacion
 conftest.py                     #  Configuration de pytest
 seed.py                         #  Script de seed de BD
 create_tables.py                #  Script de creation de tablas

 requirements.txt                #  Dependencias Python
 firebase-credentials.json       #  Credenciales Firebase

 .env                            #  Variables de entorno (no en repo)
 .dockerignore                   #  Archivos ignorados por Docker
 .gitignore                      #  Archivos ignorados por Git

 Dockerfile                      #  Definicion de imagen Docker
 docker-compose.yml              #  Compose por defecto (dev)
 docker-compose.dev.yml          #  Compose desarrollo
 docker-compose.test-local.yml   #  Compose para probar produccion localmente
 docker-compose.prod.yml         #  Compose produccion

 Taskfile.yml                        #  Comandos utiles
 README.md                       #  README principal
```

##  Description de Directorios Principales

### `docs/` - Documentacion
Toda la documentacion del proyecto organizada por tema:
- Configuraciones (Cloudflare, Traefik)
- Guias de desarrollo y despliegue
- Referencias rapidas

### `scripts/` - Scripts de Automatizacion
Scripts shell para automatizar tasks comunes:
- **`entrypoint.sh`**:  **CRITICO** - Usado por Docker para iniciar contenedores
- **`start-*.sh`**: Scripts para iniciar entornos
- **`verify-*.sh`**: Scripts de verificacion
- **`*-ssl.sh`**: Utilidades para SSL

### `app/` - Codigo Fuente
Arquitectura Hexagonal (Puertos y Adaptadores):
- **`domain/`**: Logica de negocio pura (independiente)
- **`application/`**: Casos de uso y orquestacion
- **`infrastructure/`**: Adaptadores externos (API, BD, etc.)

### `traefik/` - Reverse Proxy
Configuration de Traefik para desarrollo y produccion.

### `tests/` - Tests
Tests organizados por capa de arquitectura.

##  Archivos Importantes

### Archivos en el Root

| Archivo | Description | En Docker? |
|---------|-------------|-------------|
| `main.py` | Entry point de la aplicacion | OK Si |
| `conftest.py` | Config de pytest | OK Si |
| `seed.py` | Seedear base de datos | OK Si |
| `create_tables.py` | Create tablas de BD | OK Si |
| `requirements.txt` | Dependencias Python | OK Si |
| `firebase-credentials.json` | Credenciales Firebase | OK Si (solo archivo) |
| `*.json` | Datos de configuration | OK Si |
| `Dockerfile` | Definicion de imagen | ERROR No |
| `docker-compose*.yml` | Orquestacion Docker | ERROR No |
| `Taskfile.yml` | Comandos utiles | ERROR No |
| `.env` | Variables de entorno | ERROR No |
| `README.md` | Documentacion principal | ERROR No |

##  Que va en la Imagen Docker?

Segun `.dockerignore`, **NO se incluyen**:
- `docs/` - Documentacion (no necesaria en runtime)
- `scripts/*.sh` - Scripts (excepto `entrypoint.sh` )
- `tests/` - Tests
- `Taskfile.yml` - Comandos de desarrollo
- Archivos temporales (`.pyc`, `__pycache__`, etc.)

**SI se incluyen**:
- `app/` - Todo el codigo fuente
- `scripts/entrypoint.sh` - Script critico de inicio
- Archivos Python del root (`main.py`, `seed.py`, etc.)
- Archivos de configuration (`.json`, `requirements.txt`)

##  Flujo de Work

### Desarrollo Local
```bash
# Iniciar entorno
task dev-up

# Ver logs en tiempo real (hot reload)
task dev-watch

# Detener servicios
task dev-down

# Ejecutar tests
task dev-test
```

### Produccion
```bash
# Verificar setup
task prod-verify

# Desplegar (con confirmacion)
task prod-up

# Ver logs
task prod-logs
```

##  Probar Produccion Localmente

Antes de desplegar a produccion, puedes probar la configuration de produccion en tu maquina local:

```bash
task test-deploy-local
```

Este comando usa `docker-compose.test-local.yml` que esta configurado para:
- OK Usar **localhost** en lugar de tu dominio (api.serviperfilesayc.com)
- OK **Sin SSL/TLS** (no intenta obtener certificados Let's Encrypt)
- OK Base de datos **separada** (no afecta desarrollo ni produccion real)
- OK Construye las imagenes con el **Dockerfile de produccion**
- OK Puerto diferente para la BD (5433 vs 5432) para evitar conflictos

** Ventajas:**
-  **Seguro**: No afecta tu servidor de produccion real
-  **Limpio**: Base de datos separada que puedes delete facilmente
-  **Detecta errores**: Prueba el build de produccion antes de desplegar
-  **Verifica configuration**: Asegura que las variables de entorno funcionen

** Diferencias con produccion real:**
- Usa `localhost` en lugar de `api.serviperfilesayc.com`
- No tiene certificados SSL (solo HTTP, no HTTPS)
- Base de datos local temporal

##  Documentacion Relacionada

- **[README.md](../README.md)** - Informacion general y guia rapida
- **[docs/DEV_WORKFLOW.md](DEV_WORKFLOW.md)** - Flujo de desarrollo detallado
- **[docs/TRAEFIK_SETUP.md](TRAEFIK_SETUP.md)** - Configuration de Traefik
- **[docs/README.md](README.md)** - Indice completo de documentacion

## OK Beneficios de Esta Estructura

1. ** Organizacion Clara**: Documentacion y scripts separados del codigo
2. ** Facil Navegacion**: Es claro donde search cada cosa
3. ** Imagen Docker Ligera**: Solo incluye lo necesario
4. ** Arquitectura Limpia**: Separacion clara de capas hexagonales
5. ** Comandos Rapidos**: Taskfile.yml y scripts para tasks comunes
