# Arquitectura del Proyecto

Este proyecto React con TypeScript esta organizado siguiendo una arquitectura escalable y mantenible.

## Estructura de Carpetas

```
src/
 components/          # Componentes atomicos y reutilizables
    Login.tsx       # Componente de login
 pages/              # Vistas completas que representan pantallas
    Dashboard.tsx   # Dashboard principal con renderizado dinamico
    EmpleadoView.tsx # Vista del empleado
    GerenteView.tsx # Vista del gerente
 hooks/              # Logica reutilizable como hooks personalizados
    useAuth.ts      # Hook para autenticacion
 services/           # Logica de negocio y acceso a datos
    firebase.ts     # Configuration de Firebase
    userService.ts  # Servicio para operaciones de user
 config/             # Configuraciones de la aplicacion
    roleViews.tsx   # Mapeo de roles a sus vistas correspondientes
 types/              # Definiciones de tipos e interfaces TypeScript
    auth.ts         # Tipos relacionados con autenticacion
    role.ts         # Tipos relacionados con roles
    user.ts         # Tipos relacionados con users
    index.ts        # Archivo de barril para exportaciones
 utils/              # Funciones puras y helpers
    validation.ts   # Validation utilities
    errorHandling.ts # Utilidades para manejo de errores
    index.ts        # Archivo de barril para exportaciones
 context/            # Contexto global de React
    AuthContext.tsx # Contexto de autenticacion con roles dinamicos
 App.tsx             # Componente raiz de la aplicacion
 main.tsx            # Punto de entrada de la aplicacion
 index.css           # Estilos globales
 App.css             # Estilos del componente App
```

## Alias de Importacion

El proyecto utiliza alias de importacion configurados en `vite.config.ts` y `tsconfig.json`:

- `@/*`  `src/*`
- `@components/*`  `src/components/*`
- `@pages/*`  `src/pages/*`
- `@hooks/*`  `src/hooks/*`
- `@services/*`  `src/services/*`
- `@shared/*`  `src/types/*`
- `@utils/*`  `src/utils/*`
- `@context/*`  `src/context/*`
- `@config/*`  `src/config/*`

## Convenciones de Nomenclatura

- **Componentes**: PascalCase (ej. `GerenteView`, `UserService`)
- **Funciones**: camelCase (ej. `handleSubmit`, `validateEmail`)
- **Archivos**: camelCase para archivos de logica, PascalCase para componentes
- **Tipos/Interfaces**: PascalCase con prefijo `I` para interfaces (ej. `IUserData`)

## Tipado con TypeScript

Todos los tipos e interfaces estan centralizados en la carpeta `types/`:
- `auth.ts`: Tipos relacionados con autenticacion
- `user.ts`: Tipos relacionados con users y formularios
- `role.ts`: Tipos relacionados con roles del sistema

## Servicios

Los servicios encapsulan la logica de negocio y las llamadas a APIs:
- `UserService`: Maneja operaciones CRUD de users
- `firebase.ts`: Configuration y exportacion de servicios de Firebase

## Utilidades

Las utilidades proporcionan funciones puras y helpers:
- `validation.ts`: Funciones de validacion de formularios
- `errorHandling.ts`: Manejo centralizado de errores

## Hooks Personalizados

Los hooks encapsulan logica reutilizable:
- `useAuth`: Hook para manejo de autenticacion

## Sistema de Roles Dinamicos

El proyecto implementa un sistema de roles completamente dinamico que no requiere hardcodear valores:

### Arquitectura de Authentication
- **Firebase**: Solo autenticacion (email/password) y tokens JWT
- **Backend**: Maneja roles, permisos y datos de user
- **Frontend**: Renderiza vistas segun el rol del backend

Ver `docs/ARCHITECTURE_AUTH.md` para el flujo completo de autenticacion.

### Flujo de Roles
1. **User se autentica**: Firebase valida credenciales y genera token JWT
2. **Backend provee rol**: Frontend llama a `/users/me` con el token
3. **AuthContext guarda rol**: El rol viene del backend, no de Firebase
4. **roleViews.tsx mapea**: Cada rol a su componente de vista correspondiente
5. **Dashboard renderiza**: Vista apropiada segun el rol

### Agregar un Nuevo Rol
Para agregar un nuevo rol, solo necesitas:
1. Create el componente de vista en `src/pages/`
2. Registrarlo en `src/config/roleViews.tsx`
3. Asegurar que el rol exista en la base de datos del backend

No es necesario modificar tipos ni logica de autenticacion. Ver `docs/ROLE_VIEWS_SYSTEM.md` para mas detalles.

Esta arquitectura facilita el mantenimiento, la escalabilidad y la colaboracion en equipo.
