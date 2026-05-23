# Guia de Endpoints de Tasks (Tasks)

## Description General

Los endpoints de tasks permiten a los users obtener, create, asignar y gestionar tasks en el sistema. Las tasks se generan automaticamente a partir de products en works y pueden ser asignadas a empleados.

## Authentication

Todos los endpoints requieren un token Bearer valid en el header `Authorization`:

```bash
Authorization: Bearer <token>
```

## Endpoints de Obtencion de Tasks

### 1. **Obtener mis tasks asignadas** (Lo mas seguro y conveniente)

**Endpoint:** `GET /tasks/me`

**Description:** Obtiene todas las tasks asignadas al user autenticado. No requiere parametros adicionales.

**Authentication:** Requerida (token Bearer)

**Response:**
```json
{
  "tasks": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "work_id": "660e8400-e29b-41d4-a716-446655440001",
      "task_name": "Instalacion de puerta principal",
      "description": "Instalar la puerta principal de acceso",
      "state": "ASSIGNED",
      "labor_amount": 150000.00,
      "labor_formatted": "COP 150,000.00",
      "estimated_value_amount": 250000.00,
      "estimated_value_formatted": "COP 250,000.00",
      "assigned_user_id": "firebase_uid_user",
      "is_assigned": true
    }
  ],
  "total_count": 1
}
```

**Ejemplo curl:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost/tasks/me
```

**Ejemplo JavaScript/Fetch:**
```javascript
const response = await fetch('/api/tasks/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const data = await response.json();
console.log('Mis tasks:', data.tasks);
```

---

### 2. **Obtener tasks de un user especifico**

**Endpoint:** `GET /tasks/user/{user_id}`

**Description:** Obtiene todas las tasks asignadas a un user especifico.

**Parametros:**
- `user_id` (path): Firebase UID o UUID del user

**Permisos:**
- OK Los users SUPER_ADMIN y MANAGER pueden ver tasks de cualquier user
- OK Los users normales solo pueden ver sus propias tasks
- ERROR Un user no puede ver tasks de otro user regular (403 Forbidden)

**Response:** (Mismo formato que `/tasks/me`)

**Ejemplo curl:**
```bash
# Ver tasks de un user especifico (solo si eres admin/manager)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost/tasks/user/firebase_uid_empleado
```

**Posibles respuestas de error:**
```json
{
  "detail": "No tienes permiso para ver las tasks de otro user"
}
// Status: 403 Forbidden
```

---

### 3. **Obtener todas las tasks** (Admin only)

**Endpoint:** `GET /tasks/`

**Description:** Obtiene todas las tasks en el sistema.

**Authentication:** Requerida

**Response:** (Mismo formato que `/tasks/me`)

---

### 4. **Obtener tasks de un work especifico**

**Endpoint:** `GET /tasks/work/{work_id}`

**Description:** Obtiene todas las tasks asociadas a un work especifico.

**Parametros:**
- `work_id` (path): UUID del work

**Response:** (Mismo formato que `/tasks/me`)

**Ejemplo curl:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost/tasks/work/660e8400-e29b-41d4-a716-446655440001
```

---

### 5. **Obtener tasks de un work (resumen estadistico)**

**Endpoint:** `GET /tasks/work/{work_id}/summary`

**Description:** Obtiene un resumen estadistico de las tasks de un work.

**Parametros:**
- `work_id` (path): UUID del work

**Response:**
```json
{
  "work_id": "660e8400-e29b-41d4-a716-446655440001",
  "total_tasks": 5,
  "tasks_sin_iniciar": 2,
  "tasks_en_proceso": 2,
  "tasks_finalizadas": 1,
  "total_labor_value": 750000.00,
  "total_estimated_value": 1250000.00,
  "completion_percentage": 20.0
}
```

---

### 6. **Obtener una task especifica**

**Endpoint:** `GET /tasks/{task_id}`

**Description:** Obtiene los detalles de una task especifica.

**Parametros:**
- `task_id` (path): UUID de la task

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "work_id": "660e8400-e29b-41d4-a716-446655440001",
  "task_name": "Instalacion de puerta principal",
  "description": "Instalar la puerta principal de acceso",
  "state": "ASSIGNED",
  "labor_amount": 150000.00,
  "labor_formatted": "COP 150,000.00",
  "estimated_value_amount": 250000.00,
  "estimated_value_formatted": "COP 250,000.00",
  "assigned_user_id": "firebase_uid_user",
  "is_assigned": true
}
```

---

## Casos de Uso Comunes

### Caso 1: Empleado obtiene sus tasks asignadas

```javascript
async function getMyTasks(token) {
  const response = await fetch('/api/tasks/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (!response.ok) {
    throw new Error('Error al obtener tasks');
  }
  
  return await response.json();
}

// Uso:
const tasks = await getMyTasks(userToken);
console.log(`Tienes ${tasks.total_count} tasks asignadas`);
```

### Caso 2: Supervisor verifica tasks de su equipo

```javascript
async function getTeamTasks(userId, token) {
  const response = await fetch(`/api/tasks/user/${userId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (response.status === 403) {
    console.error('No tienes permiso para ver estas tasks');
    return null;
  }
  
  return await response.json();
}
```

### Caso 3: Gerente monitorea progreso del work

```javascript
async function getWorkProgress(workId, token) {
  const response = await fetch(`/api/tasks/work/${workId}/summary`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const summary = await response.json();
  console.log(`Progreso: ${summary.completion_percentage}%`);
  console.log(`Tasks completadas: ${summary.tasks_finalizadas}/${summary.total_tasks}`);
}
```

---

## Estados de Tasks

Las tasks pueden tener los siguientes estados:

- **PENDING**: Task recien creada, no asignada
- **ASSIGNED**: Task assigned a un user
- **READY**: Task desbloqueada, lista para comenzar
- **IN_PROGRESS**: Empleado esta trabajando en ella
- **COMPLETED**: Empleado completo (requiere validacion)
- **FINISHED**: Completada y validada

---

## Estructura del DTO TaskListDTO

```json
{
  "tasks": [
    {
      "task_id": "uuid",
      "work_id": "uuid",
      "task_name": "string",
      "description": "string",
      "state": "string",
      "labor_amount": "number",
      "labor_formatted": "string",
      "estimated_value_amount": "number",
      "estimated_value_formatted": "string",
      "assigned_user_id": "string|null",
      "is_assigned": "boolean"
    }
  ],
  "total_count": "integer"
}
```

---

## Manejo de Errores

### 400 Bad Request
```json
{ "detail": "Solicitud invalid" }
```

### 401 Unauthorized
```json
{ "detail": "Token invalid o expirado" }
```

### 403 Forbidden
```json
{ "detail": "No tienes permiso para acceder a este recurso" }
```

### 404 Not Found
```json
{ "detail": "Task, work o user no encontrado" }
```

### 500 Internal Server Error
```json
{ "detail": "Error al obtener las tasks del user" }
```

---

## Mejores Practicas

1. **Usa `/tasks/me` para obtener tus propias tasks** - Es mas seguro y no requiere pasar un ID de user.

2. **Caching en el client** - Implementa caching en el client para reducir llamadas a la API:
   ```javascript
   const cache = new Map();
   
   async function getMyTasksCached(token) {
     if (cache.has('myTasks')) {
       return cache.get('myTasks');
    }
     const tasks = await getMyTasks(token);
     cache.set('myTasks', tasks);
     return tasks;
   }
   ```

3. **Polling para actualizaciones** - Para aplicaciones en tiempo real, polling cada 30 segundos es suficiente:
   ```javascript
   setInterval(() => {
     getMyTasks(token).then(tasks => updateUI(tasks));
   }, 30000);
   ```

4. **Manejo de errores** - Siempre maneja los errores de authorization adecuadamente:
   ```javascript
   try {
     const tasks = await getMyTasks(token);
   } catch (error) {
     if (error.status === 401) {
       // Redirigir a login
     }
   }
   ```

---

## Permisos por Rol

| Endpoint | SUPER_ADMIN | MANAGER | SUPERVISOR | EMPLOYEE |
|----------|-------------|---------|------------|----------|
| GET / | OK | OK | OK | OK |
| GET /me | OK | OK | OK | OK |
| GET /user/{id} | OK (any) | OK (any) | OK (any) | OK (self only) |
| GET /work/{id} | OK | OK | OK | OK |
| GET /work/{id}/summary | OK | OK | OK | OK |
| GET /{id} | OK | OK | OK | OK |
| POST / | OK | OK | ERROR | ERROR |
| PUT /{id} | OK | OK | OK | ERROR |
| POST /{id}/assign | OK | OK | OK | ERROR |

---

## Notas de Implementacion

- **Authentication**: Los endpoints usan Firebase Authentication + JWT tokens
- **Base de datos**: PostgreSQL con SQLAlchemy ORM
- **Framework**: FastAPI
- **Dependency Injection**: dependency-injector
- **Patron**: Arquitectura hexagonal con separacion de capas (Domain, Application, Infrastructure)
