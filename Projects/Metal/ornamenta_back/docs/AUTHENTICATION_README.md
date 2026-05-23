# Sistema de Authentication - ServiPerfiles Backend

##  Arquitectura de Authentication

Este proyecto utiliza una **arquitectura hibrida** que combina:

- **Firebase Authentication**: Para el manejo de passwords, tokens y autenticacion
- **PostgreSQL**: Para almacenar information adicional del user (roles, permisos, datos de perfil)

##  Componentes del Sistema

### 1. Firebase Service (`app/application/services/firebase_service.py`)

```python
class FirebaseService:
    def verify_token(self, token: str)  # Verifica tokens JWT de Firebase
    def create_user(self, email, password)  # Crea user en Firebase
```

**Funciones principales:**
- OK **Verificacion de tokens**: Valida tokens JWT enviados desde el frontend
- OK **Creation de users**: Crea users en Firebase Authentication
- OK **Manejo de passwords**: Firebase se encarga completamente de las passwords

### 2. Dependencies (`app/infrastructure/adapters/rest/dependencies.py`)

```python
@inject
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    firebase_service: FirebaseService = ...,
    user_repo: UserRepository = ...
) -> User:
```

**Flujo de autenticacion:**
1.  Recibe token Bearer del header `Authorization`
2.  Verifica el token con Firebase
3.  Busca al user en PostgreSQL usando `firebase_uid`
4. OK Retorna el user completo con roles y permisos

### 3. Create User Use Case (`app/application/use_cases/create_user.py`)

**Flujo de creation de user:**
1.  **Verificar duplicados**: Checa Firebase y PostgreSQL
2.  **Create en Firebase**: `auth.create_user(email, password)`
3.  **Create en PostgreSQL**: Guarda datos adicionales (rol, estado, etc.)

```python
# Firebase maneja la password
new_firebase_user = auth.create_user(
    email=str(request.email),
    password=request.password,  #  Firebase se encarga de esto
    email_verified=True
)

# PostgreSQL almacena datos de negocio
new_db_user = self.user_repository.create_user(
    firebase_uid=new_firebase_user.uid,
    role=role_enum,
    # ... otros datos
)
```

##  Flujos de Authentication

###  **Registro de User**

```mermaid
sequenceDiagram
    participant C as Client/Frontend
    participant API as FastAPI Backend
    participant FB as Firebase Auth
    participant DB as PostgreSQL

    C->>API: POST /users (email, password, role)
    API->>FB: create_user(email, password)
    FB-->>API: firebase_uid
    API->>DB: save_user(firebase_uid, role, ...)
    DB-->>API: user_created
    API-->>C: user_response
```

###  **Login de User** (Frontend maneja esto)

```mermaid
sequenceDiagram
    participant C as Client/Frontend
    participant FB as Firebase Auth
    participant API as FastAPI Backend
    participant DB as PostgreSQL

    C->>FB: signInWithEmailAndPassword()
    FB-->>C: ID Token (JWT)
    C->>API: GET /users/me (Bearer: token)
    API->>FB: verify_id_token(token)
    FB-->>API: decoded_token {uid, email}
    API->>DB: get_user_by_firebase_uid(uid)
    DB-->>API: user_data
    API-->>C: user_profile
```

###  **Acceso a Recursos Protegidos**

```mermaid
sequenceDiagram
    participant C as Client/Frontend
    participant API as FastAPI Backend
    participant FB as Firebase Auth
    participant DB as PostgreSQL

    C->>API: GET /protected-endpoint (Bearer: token)
    API->>FB: verify_id_token(token)
    FB-->>API: {uid: "...", email: "..."}
    API->>DB: get_user_by_firebase_uid(uid)
    DB-->>API: User{role, permissions, ...}
    API->>API: check_permissions(user, endpoint)
    API-->>C: protected_data OR 403_forbidden
```

##  Configuration

### Variables de Entorno (`.env`)

```bash
# Firebase
FIREBASE_SERVICE_ACCOUNT_KEY_PATH=path/to/firebase-admin-sdk.json

# Base de datos
DATABASE_URL=postgresql://user:pass@localhost/db
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database
```

### Dependencias de Firebase

```txt
firebase_admin==7.1.0    # SDK de administracion de Firebase
```

##  Endpoints de Authentication

### `GET /users/me`
- **Proposito**: Obtener perfil del user actual
- **Headers**: `Authorization: Bearer <firebase_token>`
- **Response**: Datos completos del user (rol, permisos, etc.)

### `POST /users` (Create User)
```json
{
    "email": "user@ejemplo.com",
    "password": "mi_password_segura",
    "role": "EMPLOYEE"
}
```

##  Seguridad

### OK **Lo que Firebase maneja:**
-  Hashing y almacenamiento seguro de passwords
-  Generacion y validacion de tokens JWT
-  Verificacion de emails
-  Recuperacion de passwords
-  Authentication de users

### OK **Lo que PostgreSQL maneja:**
-  Roles y permisos de negocio
-  Estados de user (active/inactive)
-  Informacion de perfil (nombre, document, telefono)
-  Datos especificos del dominio de negocio

###  **Validaciones de Seguridad:**
- Token expirado  401 Unauthorized
- Token invalid  401 Unauthorized
- User no encontrado  404 Not Found
- Sin permisos  403 Forbidden

##  Integracion con Frontend

### 1. **Registro** (Frontend debe llamar a la API)
```javascript
// Llamar directamente a la API del backend
const response = await fetch('/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        email: 'user@example.com',
        password: 'securePassword123',
        role: 'EMPLOYEE'
    })
});
```

### 2. **Login** (Frontend usa Firebase SDK)
```javascript
import { signInWithEmailAndPassword } from 'firebase/auth';

// Login con Firebase
const userCredential = await signInWithEmailAndPassword(auth, email, password);
const idToken = await userCredential.user.getIdToken();

// Usar token para llamadas a la API
const response = await fetch('/users/me', {
    headers: { 'Authorization': `Bearer ${idToken}` }
});
```

### 3. **Llamadas Autenticadas**
```javascript
// En cada peticion protegida
const token = await firebase.auth().currentUser.getIdToken();
const response = await fetch('/protected-endpoint', {
    headers: { 'Authorization': `Bearer ${token}` }
});
```

##  Roles y Permisos

El sistema maneja los siguientes roles:

```python
class RoleEnum(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"    # Acceso total
    MANAGER = "MANAGER"            # Gestion y supervision
    SUPERVISOR = "SUPERVISOR"      # Supervision de tasks
    EMPLOYEE = "EMPLOYEE"          # Acceso basico
```

**Los permisos se definen en** `app/domain/permissions.py`

##  Troubleshooting

### Token Invalid (401)
- OK Verificar que el token no haya expirado
- OK Asegurar formato correcto: `Bearer <token>`
- OK Validar configuration de Firebase

### User No Encontrado (404)
- OK User existe en Firebase pero no en PostgreSQL
- OK Verificar que el `firebase_uid` coincida

### Errores de Configuration
- OK Verificar `FIREBASE_SERVICE_ACCOUNT_KEY_PATH`
- OK Validar que el archivo JSON de Firebase sea valid
- OK Confirmar permisos del archivo de credenciales

##  Archivos Importantes

```
app/
 application/
    services/firebase_service.py       #  Servicios de Firebase
    use_cases/create_user.py          #  Creation de users
    dto/create_user_request_dto.py    #  DTO de creation
 infrastructure/
    adapters/rest/dependencies.py     #  Dependencias de auth
    adapters/rest/user_router.py      #  Rutas de user
    containers.py                     #  Inyeccion de dependencias
 domain/
    models/user.py                    #  Modelo de user
    permissions.py                    #  Definicion de permisos
 config.py                             #  Configuration general
```

---

##  Resumen Ejecutivo

**Firebase se encarga de:**
- OK Manejo seguro de passwords
- OK Authentication de users
- OK Generacion de tokens JWT

**Tu API se encarga de:**
- OK Authorization (roles y permisos)
- OK Datos de negocio del user
- OK Logica de dominio especifica

**Frontend debe:**
- OK Usar Firebase SDK para login
- OK Obtener tokens de Firebase
- OK Enviar tokens a tu API para acceso a recursos

