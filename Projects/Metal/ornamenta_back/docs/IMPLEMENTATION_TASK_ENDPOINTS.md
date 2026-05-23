# Implementacion: Endpoint GET User Tasks

## Resumen

Se han implementado y mejorado los endpoints para obtener tasks asignadas a users en el sistema. El endpoint principal permite que los users vean las tasks que les fueron asignadas, con validacion de permisos y seguridad adecuada.

## Cambios Realizados

### 1. **Nuevo Endpoint: GET /tasks/me** 
**Archivo:** `/app/infrastructure/adapters/rest/task_router.py` (linea 81-115)

**Description:** Endpoint mas seguro y conveniente para que un user obtenga sus propias tasks sin necesidad de pasar un ID de user.

**Caracteristicas:**
- OK No requiere parametros de ruta
- OK Obtiene el user del token autenticado
- OK Retorna todas las tasks asignadas al user actual
- OK Mas seguro que pasar un ID de user

**Response:**
```json
{
  "tasks": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "work_id": "660e8400-e29b-41d4-a716-446655440001",
      "task_name": "Instalacion de puerta",
      "description": "Instalar puerta principal",
      "state": "ASSIGNED",
      "labor_amount": 150000.00,
      "labor_formatted": "COP 150,000.00",
      "estimated_value_amount": 250000.00,
      "estimated_value_formatted": "COP 250,000.00",
      "assigned_user_id": "firebase_uid",
      "is_assigned": true
    }
  ],
  "total_count": 1
}
```

### 2. **Endpoint Mejorado: GET /tasks/user/{user_id}**
**Archivo:** `/app/infrastructure/adapters/rest/task_router.py` (linea 118-161)

**Mejoras implementadas:**

#### a) **Authorization por Rol**
```python
is_admin_or_manager = current_user.role in (RoleEnum.SUPER_ADMIN, RoleEnum.MANAGER)
if user_id != current_user.firebase_uid and not is_admin_or_manager:
    raise HTTPException(status_code=403, detail="No tienes permiso...")
```

**Reglas de acceso:**
- OK **SUPER_ADMIN**: Puede ver tasks de cualquier user
- OK **MANAGER**: Puede ver tasks de cualquier user
- OK **SUPERVISOR**: Solo puede ver sus propias tasks (si `user_id == su_id`)
- OK **EMPLOYEE**: Solo puede ver sus propias tasks (si `user_id == su_id`)

#### b) **Mejor Manejo de Errores**
```python
try:
    # Authorization check
    # Get tasks
except HTTPException:
    raise  # Re-raise authorization errors
except Exception as e:
    raise HTTPException(status_code=500, detail="Error al obtener...")
```

#### c) **Documentacion Mejorada**
Docstring mas detallado explicando permisos y casos de error.

### 3. **Importes Actualizados**
**Archivo:** `/app/infrastructure/adapters/rest/task_router.py` (linea 1-30)

Se agregaron importes necesarios:
```python
from typing import Optional  # Para futuros query parameters
from app.domain.models.user import User, RoleEnum  # Para validacion de roles
```

## Endpoints Disponibles (Resumen)

| Endpoint | Metodo | Description | Requiere Auth |
|----------|--------|-------------|---------------|
| `/tasks/me` | GET | Obtener mis tasks | OK |
| `/tasks/user/{user_id}` | GET | Obtener tasks de user | OK |
| `/tasks/work/{work_id}` | GET | Obtener tasks de work | OK |
| `/tasks/work/{work_id}/summary` | GET | Resumen estadistico | OK |
| `/tasks/{task_id}` | GET | Obtener task especifica | OK |
| `/tasks/` | GET | Obtener todas las tasks | OK |

## Flujo de Funcionamiento

### 1. User solicita sus tasks
```
GET /tasks/me
Authorization: Bearer <token>
           
   [Authentication]
   (verificar token)
           
   [Obtener user]
   (desde token)
           
   [Consultar BD]
   (get_by_assigned_user)
           
   [Mapear a DTO]
   (TaskMapper.to_dto_list)
           
   [Retornar JSON]
   (TaskListDTO)
```

### 2. Admin solicita tasks de otro user
```
GET /tasks/user/{user_id}
Authorization: Bearer <token>
           
   [Authentication]
   (verificar token)
           
   [Verificar Rol]
   (es SUPER_ADMIN o MANAGER?)
           
   [Consultar BD]
   (get_by_assigned_user)
           
   [Mapear y retornar]
```

### 3. Empleado intenta ver tasks de otro user
```
GET /tasks/user/{otro_user_id}
Authorization: Bearer <token>
           
   [Authentication]
   [Verificar Rol]
           
   ERROR DENY (403 Forbidden)
   "No tienes permiso..."
```

## Repositorio (Backend)

La implementacion del repositorio ya estaba lista:
- **Archivo:** `/app/infrastructure/adapters/repositories/postgres_task_repository.py`
- **Metodo:** `get_by_assigned_user(user_id: str) -> List[Task]`

```python
def get_by_assigned_user(self, user_id: str) -> List[Task]:
    """Obtiene todas las tasks asignadas a un user especifico."""
    stmt = select(TaskModel).where(
        TaskModel.assigned_user_id == user_id
    ).order_by(TaskModel.execution_order)
    models = self.db_session.execute(stmt).scalars().all()
    return [self._to_domain(model) for model in models]
```

## Documentacion

Se creo guia completa de uso:
- **Archivo:** `/docs/TASK_ENDPOINTS_GUIDE.md`
- **Contenido:**
  - OK Description de todos los endpoints
  - OK Ejemplos de curl
  - OK Ejemplos de JavaScript/Fetch
  - OK Casos de uso comunes
  - OK Estructura de DTOs
  - OK Manejo de errores
  - OK Mejores practicas
  - OK Matriz de permisos por rol

## Script de Prueba

Se creo script de prueba completo:
- **Archivo:** `/test_task_endpoints.py`
- **Uso:**
```bash
# Probar obtener mis tasks
python test_task_endpoints.py "TOKEN"

# Probar obtener tasks de user especifico
python test_task_endpoints.py "TOKEN" "user123"

# Probar authorization
python test_task_endpoints.py "TOKEN" "user123" "user456"
```

## Validaciones Implementadas

### 1. **Authentication**
- OK Token debe ser valid
- OK Token debe contener Firebase UID
- OK User debe existir en la BD

### 2. **Authorization**
- OK Solo SUPER_ADMIN y MANAGER pueden ver tasks de otros users
- OK Users normales solo ven sus propias tasks
- OK Retorna 403 Forbidden cuando se intenta acceso no autorizado

### 3. **Datos**
- OK Las tasks se devuelven ordenadas por orden de ejecucion
- OK Se mapean correctamente a DTOs
- OK Se incluye total_count en la respuesta

## Codigos de Error Posibles

| Codigo | Description | Ejemplo |
|--------|-------------|---------|
| 200 | OK OK | Tasks devueltas exitosamente |
| 401 | Token invalid o expirado | No incluir token |
| 403 | User no autorizado | Ver tasks de otro como EMPLOYEE |
| 404 | User no encontrado en BD | Aunque el token sea valid |
| 500 | Error interno del servidor | Problema en la BD |

## Como Usar (Ejemplos)

### JavaScript/React
```javascript
// Obtener mis tasks
async function getMyTasks(token) {
  const response = await fetch('/api/tasks/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
}

// Obtener tasks de user (si eres admin)
async function getUserTasks(userId, token) {
  const response = await fetch(`/api/tasks/user/${userId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (response.status === 403) {
    console.error('No autorizado');
    return null;
  }
  
  return await response.json();
}
```

### Python/Requests
```python
import requests

token = "your_firebase_jwt_token"
headers = {"Authorization": f"Bearer {token}"}

# Obtener mis tasks
response = requests.get("http://localhost/tasks/me", headers=headers)
tasks = response.json()

# Obtener tasks de user especifico
response = requests.get(f"http://localhost/tasks/user/{user_id}", headers=headers)
if response.status_code == 200:
    tasks = response.json()
elif response.status_code == 403:
    print("No autorizado")
```

### cURL
```bash
# Obtener mis tasks
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost/tasks/me

# Obtener tasks de user (admin/manager)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost/tasks/user/firebase_uid_user
```

## Testing

Para probar los endpoints:

1. **Obtener un token de prueba:**
   - Usar Firebase Console
   - O ejecutar el script de prueba con un token valid

2. **Ejecutar pruebas:**
   ```bash
   python test_task_endpoints.py "YOUR_TOKEN"
   ```

3. **Comprobar en Postman/Insomnia:**
   - Header: `Authorization: Bearer <token>`
   - GET: `http://localhost/tasks/me`

## Resumen de Archivos Modificados

1. **`/app/infrastructure/adapters/rest/task_router.py`**
   - OK Agregado import de `Optional` y `RoleEnum`
   - OK Agregado nuevo endpoint `GET /tasks/me`
   - OK Mejorado endpoint `GET /tasks/user/{user_id}` con validacion de authorization

2. **`/docs/TASK_ENDPOINTS_GUIDE.md`** (NUEVO)
   - OK Guia completa de uso de endpoints
   - OK Ejemplos de codigo
   - OK Matriz de permisos

3. **`/test_task_endpoints.py`** (NUEVO)
   - OK Script de prueba completo
   - OK Pruebas de authorization

## Status

OK **COMPLETADO**

Todos los endpoints estan funcionales y listos para usar. El user puede obtener sus tasks de dos formas:

1. **`GET /tasks/me`** - Forma segura y recomendada (sin parametros)
2. **`GET /tasks/user/{user_id}`** - Forma alternativa (requiere parametro, con validacion de authorization)
