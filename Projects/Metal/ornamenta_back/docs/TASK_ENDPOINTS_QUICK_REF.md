#  Quick Reference: Task Endpoints

## En 30 Segundos

### Obtener mis tasks (LO MAS FACIL)
```bash
curl -H "Authorization: Bearer TOKEN" http://localhost/tasks/me
```

### JavaScript
```javascript
const tasks = await fetch('/tasks/me', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());
```

### Python
```python
import requests
tasks = requests.get('http://localhost/tasks/me', 
  headers={'Authorization': f'Bearer {token}'}).json()
```

---

## Endpoints Clave

| Endpoint | Description |
|----------|-------------|
| `GET /tasks/me` | **Mis tasks** (recomendado) |
| `GET /tasks/user/{id}` | Tasks de user (admin/manager) |
| `GET /tasks/work/{id}` | Tasks de un work |
| `GET /tasks/{id}` | Detalle de una task |

---

## Response

```json
{
  "tasks": [
    {
      "task_id": "123e4567-e89b-12d3-a456-426614174000",
      "work_id": "123e4567-e89b-12d3-a456-426614174001",
      "task_name": "Instalacion de puerta",
      "description": "Instalar puerta principal",
      "state": "ASSIGNED",
      "labor_amount": 150000.0,
      "labor_formatted": "COP 150,000.00",
      "estimated_value_amount": 250000.0,
      "estimated_value_formatted": "COP 250,000.00",
      "assigned_user_id": "firebase_uid_user",
      "is_assigned": true
    }
  ],
  "total_count": 1
}
```

---

## Permisos

| Rol | /tasks/me | /tasks/user/{id} |
|-----|-----------|------------------|
| SUPER_ADMIN | OK | OK (cualquier user) |
| MANAGER | OK | OK (cualquier user) |
| SUPERVISOR | OK | OK (solo propio) |
| EMPLOYEE | OK | OK (solo propio) |

---

## Errores Comunes

```
401 Unauthorized      Token invalid o expirado
403 Forbidden         Intenta ver tasks de otro user
404 Not Found         User no existe
500 Server Error      Error en la BD
```

---

## Documentacion Completa

- **Guia de uso:** `/docs/TASK_ENDPOINTS_GUIDE.md`
- **Detalles tecnicos:** `/IMPLEMENTATION_TASK_ENDPOINTS.md`
- **Testing:** `python test_task_endpoints.py TOKEN`

---

## Implementacion: 7 de noviembre de 2025 OK
