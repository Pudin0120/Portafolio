# Endpoints de Tasks - Mapa Rapido

##  Lo Que Necesitas Saber

### El Endpoint Principal: `/tasks/me`

```
GET /api/tasks/me
 Header: Authorization: Bearer TOKEN
 Response:
    {
      "tasks": [...],
      "total_count": 1
    }
```

---

##  Otros Endpoints

| Endpoint | Metodo | Para Que | Requiere |
|----------|--------|----------|----------|
| `/tasks/me` | GET | Ver mis tasks | Token |
| `/tasks/user/{id}` | GET | Ver tasks de otro (admin) | Token + Permisos |
| `/tasks/work/{id}` | GET | Ver tasks de un work | Token |
| `/tasks/work/{id}/summary` | GET | Resumen de tasks | Token |
| `/tasks/{id}` | GET | Ver detalle de task | Token |

---

##  Claves para Usar

1. **Obten un token de Firebase**
   ```
   Login en tu app  obten JWT token
   ```

2. **Usa el token en el header**
   ```
   Authorization: Bearer eyJhbGc...
   ```

3. **Llama al endpoint**
   ```bash
   curl -H "Authorization: Bearer TOKEN" \
     http://localhost/tasks/me
   ```

---

##  Ejemplos de Codigo

### cURL
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost/tasks/me
```

### JavaScript
```javascript
const response = await fetch('/api/tasks/me', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const data = await response.json();
```

### Python
```python
import requests
requests.get('/api/tasks/me', 
  headers={'Authorization': f'Bearer {token}'})
```

---

##  Seguridad

- OK Se valida que seas un user autenticado
- OK Solo ves tus propias tasks (a menos que seas admin)
- OK Si no tienes permisos: 403 Forbidden
- OK Si token es invalid: 401 Unauthorized

---

##  Response Ejemplo

```json
{
  "tasks": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "task_name": "Instalacion de puerta",
      "description": "Instalar puerta principal",
      "state": "ASSIGNED",
      "labor_formatted": "COP 150,000.00",
      "estimated_value_formatted": "COP 250,000.00",
      "assigned_user_id": "tu_firebase_uid",
      "is_assigned": true
    }
  ],
  "total_count": 1
}
```

---

##  Probar

```bash
python test_task_endpoints.py "YOUR_FIREBASE_TOKEN"
```

---

##  Documentacion

- **Quick Reference**  `TASK_ENDPOINTS_QUICK_REF.md`
- **Guia Completa**  `docs/TASK_ENDPOINTS_GUIDE.md`
- **Frontend**  `FRONTEND_INTEGRATION_GUIDE.md`
- **Tecnico**  `IMPLEMENTATION_TASK_ENDPOINTS.md`

---

## OK Status: COMPLETADO

**Listo para usar en produccion hoy mismo.** 
