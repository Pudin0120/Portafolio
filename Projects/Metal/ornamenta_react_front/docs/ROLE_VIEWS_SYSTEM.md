# Sistema de Vistas Dinamicas por Rol

Este document explica como funciona el sistema de vistas dinamicas basado en roles.

## Arquitectura

### 1. Tipos Dinamicos (`src/types/user.ts`)
```typescript
export type Role = string | null;
```
El tipo `Role` ahora acepta cualquier string, no esta limitado a valores especificos.

### 2. Configuration de Vistas (`src/config/roleViews.tsx`)

Este archivo centraliza la configuration de que vista corresponde a cada rol:

```typescript
export const roleViewsConfig: Record<string, React.FC> = {
  gerente: GerenteView,
  empleado: EmpleadoView,
  // Agrega mas roles aqui
};
```

**Funciones disponibles:**
- `getRoleView(role)`: Obtiene el componente de vista para un rol
- `hasRoleView(role)`: Verifica si un rol tiene una vista configurada

### 3. AuthContext con Backend (`src/context/AuthContext.tsx`)

El contexto de autenticacion:
- Se autentica con Firebase (solo email/password)
- Obtiene el token de Firebase
- Llama al backend (`/users/me`) con el token para obtener el rol
- Almacena el rol que viene del backend
- No usa Firebase custom claims

### 4. Dashboard Adaptativo (`src/pages/Dashboard.tsx`)

El dashboard renderiza dinamicamente la vista correcta basandose en el rol:

```typescript
const RoleView = userRole ? getRoleView(userRole) : null;
```

Si el rol no tiene una vista configurada, muestra un mensaje apropiado.

## Como Agregar un Nuevo Rol

### Paso 1: Create la Vista del Rol

Crea un nuevo archivo en `src/pages/`, por ejemplo `AdminView.tsx`:

```typescript
import React from 'react';

export const AdminView: React.FC = () => {
  return (
    <div>
      <h2>Panel de Administrador</h2>
      <p>Funcionalidades de administrador aqui</p>
    </div>
  );
};
```

### Paso 2: Registrar la Vista

Edita `src/config/roleViews.tsx` y agrega el nuevo rol:

```typescript
import { AdminView } from '@pages/AdminView';

export const roleViewsConfig: Record<string, React.FC> = {
  gerente: GerenteView,
  empleado: EmpleadoView,
  admin: AdminView,  //  Nuevo rol
};
```

### Paso 3: Asegurar el Rol en el Backend

Asegurate de que tu backend:
1. Tenga el rol asignado en la base de datos para el user
2. El endpoint `/users/me` devuelva el rol correctamente

```python
# En tu backend FastAPI
@router.get("/users/me", response_model=UserResponseDTO)
def read_users_me(current_user: User = Depends(get_current_user)):
    return UserMapper.to_response_dto(current_user)
```

Eso es todo! El sistema automaticamente:
1. Obtendra el rol desde el backend
2. Renderizara la vista correcta

## Ventajas de Este Sistema

1. **Escalable**: Agregar nuevos roles es trivial
2. **Mantenible**: Toda la configuration esta en un solo lugar
3. **Flexible**: Los roles vienen del backend, no estan hardcodeados
4. **Robusto**: Maneja roles desconocidos con mensajes apropiados
5. **Type-safe**: TypeScript valida los tipos correctamente

## Flujo de Authentication

1. User se autentica en Firebase (solo email/password)
2. Firebase devuelve un token JWT
3. `AuthContext` usa ese token para llamar a `/users/me` en el backend
4. El backend valida el token y devuelve la information del user (incluyendo el rol)
5. `AuthContext` guarda el rol en el estado
6. `Dashboard` busca la vista correspondiente en `roleViewsConfig`
7. Se renderiza la vista apropiada o un mensaje de error

## Manejo de Errores

- **Sin rol asignado**: Muestra mensaje pidiendo contactar al administrador
- **Rol sin vista**: Muestra el rol y pide configuration
- **Error al obtener user del backend**: Se loguea en consola y continua con rol null
- **Backend no disponible**: El user vera que no tiene rol asignado

## Separacion de Responsabilidades

- **Firebase**: Solo autenticacion (email/password) y generacion de tokens JWT
- **Backend**: Maneja roles, permisos y toda la logica de negocio
- **Frontend**: Renderiza vistas segun el rol que viene del backend
