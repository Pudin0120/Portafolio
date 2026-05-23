# Sistema de Roles - Resumen

##  Los 4 Roles del Sistema

El sistema maneja exactamente 4 roles que vienen del backend:

| Rol Backend | Rol Frontend | Vista | Description |
|-------------|--------------|-------|-------------|
| `SUPER_ADMIN` | `super_admin` | `SuperAdminView` | Administrador con acceso completo |
| `MANAGER` | `manager` | `GerenteView` | Gerente que puede create users |
| `SUPERVISOR` | `supervisor` | `SupervisorView` | Supervisor de equipos |
| `EMPLOYEE` | `employee` | `EmpleadoView` | Empleado regular |

##  Vistas Implementadas

### OK SuperAdminView (`src/pages/SuperAdminView.tsx`)
- Carga perfil desde `/user/perfil`
- Muestra information completa del user
- Lista de funcionalidades del administrador

### OK GerenteView (`src/pages/GerenteView.tsx`)
- **Vista especial**: Formulario para create users
- Carga roles dinamicamente desde `/roles`
- Validaciones completas
- Gestion de estado del formulario

### OK SupervisorView (`src/pages/SupervisorView.tsx`)
- Carga perfil desde `/user/perfil`
- Muestra information completa del user
- Lista de funcionalidades del supervisor

### OK EmpleadoView (`src/pages/EmpleadoView.tsx`)
- Carga perfil desde `/user/perfil`
- Muestra information completa del user
- Lista de funcionalidades del empleado

##  Flujo de Authentication

```
1. User se loguea
   
2. Firebase Auth devuelve token con custom claims
   
3. AuthContext extrae el rol (ej: "SUPER_ADMIN")
   
4. Dashboard normaliza el rol a lowercase (ej: "super_admin")
   
5. roleViewsConfig busca la vista correspondiente
   
6. Se renderiza la vista apropiada (ej: SuperAdminView)
```

##  Archivos Clave

### Configuration de Vistas
**`src/config/roleViews.tsx`**
```typescript
export const roleViewsConfig: Record<string, React.FC> = {
  super_admin: SuperAdminView,
  manager: GerenteView,
  supervisor: SupervisorView,
  employee: EmpleadoView,
};
```

### Servicio de User
**`src/services/userService.ts`**
- `getUserProfile(token)` - Obtiene perfil del user actual
- `getRoles()` - Obtiene lista de roles del sistema
- `createUser(userData, token)` - Crea nuevo user (solo MANAGER)

### Contexto de Authentication
**`src/context/AuthContext.tsx`**
- Lee custom claims de Firebase
- Normaliza roles automaticamente
- Acepta cualquier rol dinamicamente

##  Caracteristicas de las Vistas

Todas las vistas (excepto GerenteView) incluyen:

1. **Carga de Perfil**
   - Nombre completo
   - Email
   - Document de identidad
   - Telefono
   - Rol
   - Estado (Active/Inactive)

2. **Estados de UI**
   - Loading state mientras carga
   - Error state si falla la peticion
   - Vista completa cuando carga exitosamente

3. **Estilo Consistente**
   - Card con information del perfil
   - Card con funcionalidades del rol
   - Colores diferenciados por rol:
     - Super Admin: Azul (`#2196f3`)
     - Supervisor: Naranja (`#ff9800`)
     - Empleado: Verde (`#4caf50`)

##  Permisos por Rol

### SUPER_ADMIN
- Acceso completo al sistema
- Configuration global
- Reportes y auditoria

### MANAGER
- Create y gestionar users
- Asignar roles
- Ver information de empleados

### SUPERVISOR
- Gestionar equipos
- Aprobar solicitudes
- Ver reportes de equipo

### EMPLOYEE
- Ver perfil propio
- Ver payroll
- Solicitar permisos

##  Agregar un Nuevo Rol (Futuro)

Si necesitas agregar un 5to rol:

1. **Create vista** en `src/pages/NuevoRolView.tsx`
2. **Importar y registrar** en `src/config/roleViews.tsx`
3. **Backend**: Asignar custom claim con el nuevo rol
4. **Listo!** No necesitas cambiar tipos ni logica

Ver `docs/EXAMPLE_ADD_ROLE.md` para detalles.

##  Endpoints Utilizados

- `GET /roles` - Lista de roles disponibles en el sistema
- `GET /users/me` - Informacion del user actual (incluyendo rol)
- `POST /admin/users` - Create nuevo user (solo MANAGER)

**Nota:** El endpoint `/users/me` es el que provee el rol del user. Este se llama automaticamente al iniciar sesion para obtener el rol desde el backend.

##  Ventajas del Sistema

- OK **Dinamico**: Los roles vienen del backend
- OK **Escalable**: Agregar roles es trivial
- OK **Mantenible**: Configuration centralizada
- OK **Type-safe**: TypeScript valida todo
- OK **Robusto**: Maneja errores apropiadamente
- OK **Consistente**: UI uniforme en todas las vistas
