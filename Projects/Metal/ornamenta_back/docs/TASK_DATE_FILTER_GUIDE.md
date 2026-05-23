# Guia: Filtrado de Tasks por Fechas y Campo updated_at

##  Resumen de Cambios

Se ha implementado exitosamente:

1. OK **Campo `updated_at`** en cada task devuelta por los endpoints
2. OK **Filtrado por rango de fechas** en los endpoints de tasks mediante query parameters
3. OK Filtros disponibles en:
   - `GET /tasks/` - Todas las tasks
   - `GET /tasks/me` - Mis tasks asignadas
   - `GET /tasks/user/{user_id}` - Tasks de un user especifico

---

##  Campo `updated_at`

Cada task ahora incluye el campo `updated_at` que indica la ultima vez que fue modificada en la base de datos.

### Ejemplo de Response

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
      "is_assigned": true,
      "updated_at": "2025-11-10T15:30:45.123456+00:00"
    }
  ],
  "total_count": 1
}
```

---

##  Filtrado por Rango de Fechas

### Parametros Query Disponibles

Todos los endpoints de listado de tasks ahora aceptan estos parametros opcionales:

- **`start_date`**: Fecha de inicio del rango (formato ISO: `YYYY-MM-DDTHH:MM:SS`)
  - Filtra tasks con `updated_at >= start_date`
  
- **`end_date`**: Fecha de fin del rango (formato ISO: `YYYY-MM-DDTHH:MM:SS`)
  - Filtra tasks con `updated_at <= end_date`

**Ambos parametros son opcionales y pueden usarse juntos o por separado.**

---

##  Ejemplos de Uso

### 1. Obtener Mis Tasks (Sin Filtros)

**Endpoint:** `GET /tasks/me`

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost/tasks/me
```

**JavaScript:**
```javascript
const response = await fetch('/api/tasks/me', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const data = await response.json();
```

---

### 2. Obtener Mis Tasks Actualizadas Despues de una Fecha

**Endpoint:** `GET /tasks/me?start_date=2025-11-01T00:00:00`

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost/tasks/me?start_date=2025-11-01T00:00:00"
```

**JavaScript:**
```javascript
const startDate = '2025-11-01T00:00:00';
const response = await fetch(`/api/tasks/me?start_date=${startDate}`, {
  headers: { 'Authorization': `Bearer ${token}` }
});
const data = await response.json();
console.log(`Tasks desde ${startDate}:`, data.tasks);
```

---

### 3. Obtener Mis Tasks en un Rango de Fechas Especifico

**Endpoint:** `GET /tasks/me?start_date=2025-11-01T00:00:00&end_date=2025-11-10T23:59:59`

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost/tasks/me?start_date=2025-11-01T00:00:00&end_date=2025-11-10T23:59:59"
```

**JavaScript:**
```javascript
const startDate = '2025-11-01T00:00:00';
const endDate = '2025-11-10T23:59:59';
const response = await fetch(
  `/api/tasks/me?start_date=${startDate}&end_date=${endDate}`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);
const data = await response.json();
console.log('Tasks entre fechas:', data.tasks);
```

---

### 4. Obtener Tasks de un User (Admin/Manager)

**Endpoint:** `GET /tasks/user/{user_id}?start_date=2025-11-01T00:00:00`

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost/tasks/user/firebase_uid_user?start_date=2025-11-01T00:00:00"
```

**JavaScript:**
```javascript
const userId = 'firebase_uid_user';
const startDate = '2025-11-01T00:00:00';
const response = await fetch(
  `/api/tasks/user/${userId}?start_date=${startDate}`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);
const data = await response.json();
```

---

### 5. Obtener Todas las Tasks con Filtros (Admin)

**Endpoint:** `GET /tasks/?start_date=2025-11-01T00:00:00&end_date=2025-11-10T23:59:59`

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost/tasks/?start_date=2025-11-01T00:00:00&end_date=2025-11-10T23:59:59"
```

---

##  Casos de Uso Comunes

### Caso 1: Dashboard con Tasks Recientes (Ultimos 7 dias)

```javascript
async function getRecentTasks(token) {
  const now = new Date();
  const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
  
  const startDate = sevenDaysAgo.toISOString();
  const endDate = now.toISOString();
  
  const response = await fetch(
    `/api/tasks/me?start_date=${startDate}&end_date=${endDate}`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  
  return await response.json();
}

// Uso
const recentTasks = await getRecentTasks(userToken);
console.log(`Tasks de los ultimos 7 dias: ${recentTasks.total_count}`);
```

---

### Caso 2: Filtrar Tasks del Mes Actual

```javascript
async function getCurrentMonthTasks(token) {
  const now = new Date();
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
  const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59);
  
  const response = await fetch(
    `/api/tasks/me?start_date=${startOfMonth.toISOString()}&end_date=${endOfMonth.toISOString()}`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  
  return await response.json();
}
```

---

### Caso 3: Tasks Modificadas Hoy

```javascript
async function getTodaysTasks(token) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const startDate = today.toISOString();
  
  const response = await fetch(
    `/api/tasks/me?start_date=${startDate}`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  
  return await response.json();
}
```

---

### Caso 4: React Component con Date Range Picker

```jsx
import React, { useState, useEffect } from 'react';

function TasksWithDateFilter({ token }) {
  const [tasks, setTasks] = useState([]);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchTasks = async () => {
    setLoading(true);
    try {
      let url = '/api/tasks/me';
      const params = new URLSearchParams();
      
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }
      
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const data = await response.json();
      setTasks(data.tasks);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [startDate, endDate]);

  return (
    <div>
      <h2>Mis Tasks</h2>
      
      <div className="date-filters">
        <label>
          Desde:
          <input 
            type="datetime-local" 
            value={startDate} 
            onChange={(e) => setStartDate(e.target.value)}
          />
        </label>
        
        <label>
          Hasta:
          <input 
            type="datetime-local" 
            value={endDate} 
            onChange={(e) => setEndDate(e.target.value)}
          />
        </label>
        
        <button onClick={() => { setStartDate(''); setEndDate(''); }}>
          Limpiar Filtros
        </button>
      </div>

      {loading ? (
        <p>Cargando...</p>
      ) : (
        <div>
          <p>Total de tasks: {tasks.length}</p>
          <ul>
            {tasks.map(task => (
              <li key={task.task_id}>
                {task.task_name} - 
                Actualizada: {new Date(task.updated_at).toLocaleString()}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

---

##  Formato de Fechas

### Formato ISO 8601

Todas las fechas deben enviarse en formato ISO 8601:

- **Completo**: `2025-11-10T15:30:45`
- **Con zona horaria**: `2025-11-10T15:30:45+00:00`
- **Con milisegundos**: `2025-11-10T15:30:45.123456+00:00`

### Ejemplos Validos

```
2025-11-01T00:00:00
2025-11-10T23:59:59
2025-11-10T15:30:45.123456
2025-11-10T15:30:45+00:00
2025-11-10T15:30:45Z
```

---

##  Python Examples

### Ejemplo 1: Requests con Filtros de Fecha

```python
import requests
from datetime import datetime, timedelta

token = "your_firebase_token"
headers = {"Authorization": f"Bearer {token}"}

# Tasks de los ultimos 30 dias
start_date = (datetime.now() - timedelta(days=30)).isoformat()
end_date = datetime.now().isoformat()

response = requests.get(
    "http://localhost/tasks/me",
    headers=headers,
    params={
        "start_date": start_date,
        "end_date": end_date
    }
)

tasks = response.json()
print(f"Tasks encontradas: {tasks['total_count']}")
for task in tasks['tasks']:
    print(f"- {task['task_name']} (actualizada: {task['updated_at']})")
```

### Ejemplo 2: Solo Tasks Recientes

```python
import requests
from datetime import datetime, timedelta

token = "your_firebase_token"
headers = {"Authorization": f"Bearer {token}"}

# Solo tasks actualizadas en las ultimas 24 horas
yesterday = (datetime.now() - timedelta(days=1)).isoformat()

response = requests.get(
    "http://localhost/tasks/me",
    headers=headers,
    params={"start_date": yesterday}
)

tasks = response.json()
print(f"Tasks actualizadas en las ultimas 24h: {tasks['total_count']}")
```

---

##  Seguridad y Permisos

Los filtros de fecha respetan los mismos permisos que los endpoints originales:

- **`/tasks/me`**: Solo tus tasks (todos los roles)
- **`/tasks/user/{user_id}`**: 
  - SUPER_ADMIN y MANAGER pueden ver cualquier user
  - Otros roles solo pueden ver sus propias tasks
- **`/tasks/`**: Todas las tasks (requiere permisos admin)

---

##  Notas Importantes

1. **Ambos parametros son opcionales**: Puedes usar solo `start_date`, solo `end_date`, ambos, o ninguno.

2. **Zona horaria**: Las fechas se almacenan en UTC en la base de datos. Asegurate de convertir las fechas locales a UTC si es necesario.

3. **Rendimiento**: Los filtros de fecha estan indexados en la base de datos (`updated_at` tiene indice), por lo que las consultas son eficientes.

4. **Compatibilidad**: Los endpoints sin filtros siguen funcionando exactamente igual que antes.

---

##  Endpoints Afectados

| Endpoint | Metodo | Filtros de Fecha | Description |
|----------|--------|------------------|-------------|
| `/tasks/` | GET | OK | Todas las tasks (admin) |
| `/tasks/me` | GET | OK | Mis tasks asignadas |
| `/tasks/user/{user_id}` | GET | OK | Tasks de user especifico |
| `/tasks/work/{work_id}` | GET | ERROR | Tasks de un work |
| `/tasks/{task_id}` | GET | ERROR | Task especifica |

---

## OK Testing

Para probar los cambios en Docker:

```bash
# Iniciar servicios de desarrollo
task dev-up

# Ver logs del backend
task dev-logs-backend

# Probar endpoint sin filtros
curl -H "Authorization: Bearer TOKEN" http://localhost/tasks/me

# Probar con filtros de fecha
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost/tasks/me?start_date=2025-11-01T00:00:00"
```

---

##  Resumen

OK **Campo `updated_at`** incluido en todas las respuestas de tasks  
OK **Filtros por rango de fechas** implementados en todos los endpoints de listado  
OK **Documentacion completa** con ejemplos en JS, Python, React  
OK **Compatibilidad total** con codigo existente  
OK **Sin cambios en base de datos** (el campo ya existia)  

---

**Fecha de Implementacion:** 11 de noviembre de 2025  
**Status:** OK Completed y Listo para Produccion
