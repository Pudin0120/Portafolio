# Guia de Filtrado de Tasks por Fechas

##  Nuevas Funcionalidades Implementadas

Se han agregado dos mejoras importantes a los endpoints de tasks:

1. **Filtrado por rango de fechas** usando el campo `updated_at`
2. **Campo `updated_at`** incluido en la respuesta de cada task

---

##  Filtrado por Rango de Fechas

Los siguientes endpoints ahora soportan filtrado opcional por rango de fechas:

### Endpoints que Soportan Filtrado

| Endpoint | Description |
|----------|-------------|
| `GET /tasks/` | Todas las tasks (con filtros opcionales) |
| `GET /tasks/me` | Mis tasks asignadas (con filtros opcionales) |
| `GET /tasks/user/{user_id}` | Tasks de user especifico (con filtros opcionales) |

### Parametros de Query

- **`start_date`** (opcional): Fecha de inicio del rango
  - Formato: ISO 8601 (`YYYY-MM-DDTHH:MM:SS`)
  - Filtra: `updated_at >= start_date`
  
- **`end_date`** (opcional): Fecha de fin del rango
  - Formato: ISO 8601 (`YYYY-MM-DDTHH:MM:SS`)
  - Filtra: `updated_at <= end_date`

---

##  Ejemplos de Uso

### 1. Obtener Mis Tasks (Sin Filtros)

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost/tasks/me
```

**Response:**
```json
{
  "tasks": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "task_name": "Instalacion de puerta principal",
      "state": "ASSIGNED",
      "updated_at": "2025-11-10T15:30:00Z",
      ...
    }
  ],
  "total_count": 1
}
```

---

### 2. Obtener Mis Tasks Actualizadas Hoy

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost/tasks/me?start_date=2025-11-11T00:00:00"
```

---

### 3. Obtener Mis Tasks en un Rango de Fechas

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost/tasks/me?start_date=2025-11-01T00:00:00&end_date=2025-11-10T23:59:59"
```

---

### 4. Obtener Tasks de un User en una Fecha Especifica

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost/tasks/user/firebase_uid?start_date=2025-11-11T00:00:00&end_date=2025-11-11T23:59:59"
```

---

### 5. Obtener Todas las Tasks de la Ultima Semana

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost/tasks/?start_date=2025-11-04T00:00:00"
```

---

##  Ejemplos con JavaScript/Fetch

### Sin Filtros

```javascript
const response = await fetch('/api/tasks/me', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const data = await response.json();
console.log(`Tienes ${data.total_count} tasks`);
```

### Con Filtro de Fecha de Inicio

```javascript
const startDate = '2025-11-11T00:00:00';
const response = await fetch(
  `/api/tasks/me?start_date=${encodeURIComponent(startDate)}`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);
const data = await response.json();
console.log(`Tasks desde ${startDate}: ${data.total_count}`);
```

### Con Rango de Fechas Completo

```javascript
const startDate = '2025-11-01T00:00:00';
const endDate = '2025-11-10T23:59:59';
const url = `/api/tasks/me?start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`;

const response = await fetch(url, {
  headers: { 'Authorization': `Bearer ${token}` }
});
const data = await response.json();
console.log(`Tasks entre ${startDate} y ${endDate}: ${data.total_count}`);
```

### Construir Fechas Dinamicamente

```javascript
// Tasks de hoy
const today = new Date();
today.setHours(0, 0, 0, 0);
const startDate = today.toISOString();

const response = await fetch(
  `/api/tasks/me?start_date=${encodeURIComponent(startDate)}`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);

// Tasks de los ultimos 7 dias
const sevenDaysAgo = new Date();
sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
const startDate7d = sevenDaysAgo.toISOString();

const response7d = await fetch(
  `/api/tasks/me?start_date=${encodeURIComponent(startDate7d)}`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);
```

---

##  Ejemplos con Python

### Sin Filtros

```python
import requests

token = "your_firebase_token"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get("http://localhost/tasks/me", headers=headers)
tasks = response.json()
print(f"Total de tasks: {tasks['total_count']}")
```

### Con Rango de Fechas

```python
import requests
from datetime import datetime, timedelta

token = "your_firebase_token"
headers = {"Authorization": f"Bearer {token}"}

# Tasks de los ultimos 7 dias
start_date = (datetime.now() - timedelta(days=7)).isoformat()
end_date = datetime.now().isoformat()

params = {
    "start_date": start_date,
    "end_date": end_date
}

response = requests.get(
    "http://localhost/tasks/me", 
    headers=headers,
    params=params
)

tasks = response.json()
print(f"Tasks en los ultimos 7 dias: {tasks['total_count']}")

for task in tasks['tasks']:
    print(f"- {task['task_name']} (actualizada: {task['updated_at']})")
```

### Con Fecha Especifica (Un Solo Dia)

```python
import requests
from datetime import datetime

token = "your_firebase_token"
headers = {"Authorization": f"Bearer {token}"}

# Tasks actualizadas hoy
today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
tomorrow = today + timedelta(days=1)

params = {
    "start_date": today.isoformat(),
    "end_date": tomorrow.isoformat()
}

response = requests.get(
    "http://localhost/tasks/me", 
    headers=headers,
    params=params
)

tasks = response.json()
print(f"Tasks actualizadas hoy: {tasks['total_count']}")
```

---

##  Estructura de Response con `updated_at`

Cada task en la respuesta ahora incluye el campo `updated_at`:

```json
{
  "tasks": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "work_id": "660e8400-e29b-41d4-a716-446655440001",
      "product_id": "770e8400-e29b-41d4-a716-446655440002",
      "task_name": "Instalacion de puerta principal",
      "description": "Instalar la puerta principal de acceso",
      "state": "ASSIGNED",
      "labor_amount": 150000.00,
      "labor_formatted": "COP 150,000.00",
      "estimated_value_amount": 250000.00,
      "estimated_value_formatted": "COP 250,000.00",
      "execution_order": 1,
      "is_blocked": false,
      "previous_task_id": null,
      "assigned_user_id": "firebase_uid_user",
      "is_assigned": true,
      "updated_at": "2025-11-10T15:30:00.123456Z"  //  NUEVO CAMPO
    }
  ],
  "total_count": 1
}
```

---

##  Componente React con Filtrado por Fechas

```javascript
import React, { useState, useEffect } from 'react';

export function TaskDashboard({ token }) {
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
        headers: { 'Authorization': `Bearer ${token}` },
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
  }, [token]);

  const handleFilterChange = () => {
    fetchTasks();
  };

  // Filtros rapidos
  const setToday = () => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    setStartDate(today.toISOString().slice(0, 16));
    setEndDate(new Date().toISOString().slice(0, 16));
  };

  const setLastWeek = () => {
    const today = new Date();
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    setStartDate(weekAgo.toISOString().slice(0, 16));
    setEndDate(today.toISOString().slice(0, 16));
  };

  const clearFilters = () => {
    setStartDate('');
    setEndDate('');
  };

  return (
    <div>
      <h2>Mis Tasks</h2>
      
      <div className="filters">
        <div>
          <label>Desde:</label>
          <input 
            type="datetime-local" 
            value={startDate} 
            onChange={(e) => setStartDate(e.target.value)}
          />
        </div>
        
        <div>
          <label>Hasta:</label>
          <input 
            type="datetime-local" 
            value={endDate} 
            onChange={(e) => setEndDate(e.target.value)}
          />
        </div>
        
        <button onClick={handleFilterChange}>Filtrar</button>
        <button onClick={setToday}>Hoy</button>
        <button onClick={setLastWeek}>Ultima Semana</button>
        <button onClick={clearFilters}>Limpiar</button>
      </div>

      {loading ? (
        <p>Cargando...</p>
      ) : (
        <div>
          <p>Total: {tasks.length} tasks</p>
          <ul>
            {tasks.map(task => (
              <li key={task.task_id}>
                <strong>{task.task_name}</strong> 
                - Status: {task.state}
                - Actualizada: {new Date(task.updated_at).toLocaleString()}
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

##  Casos de Uso Comunes

### 1. Dashboard de Tasks del Dia

```javascript
async function getTodaysTasks(token) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const startDate = today.toISOString();
  
  const response = await fetch(
    `/api/tasks/me?start_date=${encodeURIComponent(startDate)}`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  
  return await response.json();
}
```

### 2. Reporte Semanal

```javascript
async function getWeeklyReport(token) {
  const today = new Date();
  const weekAgo = new Date();
  weekAgo.setDate(weekAgo.getDate() - 7);
  
  const startDate = weekAgo.toISOString();
  const endDate = today.toISOString();
  
  const response = await fetch(
    `/api/tasks/me?start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  
  return await response.json();
}
```

### 3. Reporte Mensual

```javascript
async function getMonthlyReport(token, year, month) {
  const startDate = new Date(year, month - 1, 1).toISOString();
  const endDate = new Date(year, month, 0, 23, 59, 59).toISOString();
  
  const response = await fetch(
    `/api/tasks/me?start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  
  return await response.json();
}

// Uso:
const novemberTasks = await getMonthlyReport(token, 2025, 11);
```

---

##  Notas Importantes

1. **Formato de Fecha**: Usar formato ISO 8601 (`YYYY-MM-DDTHH:MM:SS`)
2. **Zona Horaria**: Las fechas se almacenan en UTC en la base de datos
3. **Filtros Opcionales**: Ambos parametros son opcionales. Se pueden usar:
   - Solo `start_date` (desde una fecha en adelante)
   - Solo `end_date` (hasta una fecha)
   - Ambos (rango completo)
   - Ninguno (todas las tasks sin filtrar)
4. **Campo `updated_at`**: Siempre se incluye en la respuesta, incluso si no se usan filtros
5. **Compatibilidad**: Los endpoints siguen funcionando sin parametros (retrocompatibles)

---

## OK Resumen de Cambios

### Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `app/domain/models/task.py` | Agregado campo `updated_at: Optional[datetime]` |
| `app/application/dto/task_dto.py` | Agregado campo `updated_at: Optional[datetime]` al TaskDTO |
| `app/application/mappers/task_mapper.py` | Incluye `updated_at` en el mapeo a DTO |
| `app/domain/repositories/task_repository.py` | Agregados parametros `start_date` y `end_date` |
| `app/infrastructure/adapters/repositories/postgres_task_repository.py` | Implementado filtrado por fechas |
| `app/infrastructure/adapters/rest/task_router.py` | Agregados query parameters para filtrado |

### Endpoints Actualizados

- OK `GET /tasks/` - Todas las tasks (con filtros opcionales)
- OK `GET /tasks/me` - Mis tasks (con filtros opcionales)
- OK `GET /tasks/user/{user_id}` - Tasks de user (con filtros opcionales)

### Nuevo Campo en Response

- OK `updated_at` - Timestamp de la ultima actualizacion de cada task

---

##  Listo para Usar

Todos los cambios estan implementados y listos para usar en produccion. Los endpoints son retrocompatibles, por lo que el codigo existente seguira funcionando sin cambios.

**Fecha de Implementacion:** 11 de noviembre de 2025
