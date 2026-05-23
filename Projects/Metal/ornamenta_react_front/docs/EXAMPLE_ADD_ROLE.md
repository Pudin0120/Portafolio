# Sistema de Roles

El sistema maneja 4 roles predefinidos que vienen del backend:

## Roles del Sistema

```json
{
  "roles": [
    {
      "value": "SUPER_ADMIN",
      "display_name": "Administrador"
    },
    {
      "value": "MANAGER",
      "display_name": "Gerente"
    },
    {
      "value": "SUPERVISOR",
      "display_name": "Supervisor"
    },
    {
      "value": "EMPLOYEE",
      "display_name": "Empleado"
    }
  ]
}
```

## Mapeo de Roles en el Frontend

Los roles se mapean en `src/config/roleViews.tsx`:

- `SUPER_ADMIN`  `SuperAdminView` - Acceso completo al sistema
- `MANAGER`  `GerenteView` - Create y gestionar users
- `SUPERVISOR`  `SupervisorView` - Gestionar equipo y aprobar solicitudes
- `EMPLOYEE`  `EmpleadoView` - Ver perfil y payroll

## Ejemplo: Agregar un Nuevo Rol (Si fuera necesario)

Si en el futuro necesitas agregar un rol adicional, sigue estos pasos:

### Paso 1: Create la Vista

Crea un archivo siguiendo este patron:

```typescript
import React from 'react';

export const SupervisorView: React.FC = () => {
  return (
    <div>
      <h2>Panel de Supervisor</h2>
      {/* Tu contenido aqui */}
    </div>
  );
};
```

## Paso 2: Registrar la Vista en la Configuration

Edita `src/config/roleViews.tsx`:

```typescript
import React from 'react';
import { GerenteView } from '@pages/GerenteView';
import { EmpleadoView } from '@pages/EmpleadoView';
import { SuperAdminView } from '@pages/SuperAdminView';
import { SupervisorView } from '@pages/SupervisorView';
import { NuevoRolView } from '@pages/NuevoRolView'; //  Importar

export const roleViewsConfig: Record<string, React.FC> = {
  super_admin: SuperAdminView,
  manager: GerenteView,
  supervisor: SupervisorView,
  employee: EmpleadoView,
  nuevo_rol: NuevoRolView, //  Agregar aqui (en lowercase y snake_case)
};
```

## Paso 3: Configurar el Backend

En tu backend (FastAPI/Python), asegurate de que:

1. El rol este guardado en la base de datos para el user
2. El endpoint `/users/me` devuelva el rol correctamente

```python
# En tu backend FastAPI
@router.get("/users/me", response_model=UserResponseDTO)
def read_users_me(current_user: User = Depends(get_current_user)):
    return UserMapper.to_response_dto(current_user)
    # UserResponseDTO debe incluir el campo "role"
```

**Importante:** 
- El backend envia roles en MAYUSCULAS (ej: `SUPER_ADMIN`)
- El frontend los normaliza automaticamente a lowercase con snake_case (ej: `super_admin`) para search en `roleViewsConfig`
- Firebase solo maneja autenticacion, NO almacena roles

## Paso 4: Probar

1. Crea un user en el backend con rol "supervisor"
2. Inicia sesion con ese user
3. El Dashboard automaticamente mostrara `SupervisorView`

## Roles Actuales del Sistema

Los 4 roles del sistema estan completamente implementados:

| Backend (Custom Claim) | Frontend (roleViewsConfig) | Vista | Permisos |
|------------------------|----------------------------|-------|----------|
| `SUPER_ADMIN` | `super_admin` | `SuperAdminView` | Acceso completo |
| `MANAGER` | `manager` | `GerenteView` | Create users |
| `SUPERVISOR` | `supervisor` | `SupervisorView` | Gestionar equipo |
| `EMPLOYEE` | `employee` | `EmpleadoView` | Ver perfil |

## Notas Importantes

- **Normalizacion**: El backend envia roles en MAYUSCULAS (ej: `SUPER_ADMIN`), el frontend los convierte automaticamente a lowercase con snake_case (ej: `super_admin`)
- **Sin hardcoding**: Los datos vienen dinamicamente del endpoint `/roles`
- **Type-safe**: TypeScript valida todo correctamente
- **Escalable**: Agregar nuevos roles solo requiere create la vista y registrarla

## Todas las vistas cargan el perfil

Todas las vistas (excepto `GerenteView` que tiene funcionalidades especiales) cargan el perfil del user desde el endpoint `/user/perfil` y muestran:
- Nombre completo
- Email
- Document de identidad
- Telefono
- Rol
- Estado (Active/Inactive)
