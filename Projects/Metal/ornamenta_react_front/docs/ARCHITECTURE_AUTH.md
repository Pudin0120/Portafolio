# Arquitectura de Authentication y Roles

Este document explica como funciona la arquitectura completa del sistema.

##  Separacion de Responsabilidades

### Firebase
- **Responsabilidad**: Authentication unicamente
- **Maneja**: Email/password, tokens JWT
- **NO maneja**: Roles, permisos, datos de user

### Backend (FastAPI)
- **Responsabilidad**: Logica de negocio
- **Maneja**: Roles, permisos, datos de user, validaciones
- **Endpoints clave**:
  - `GET /users/me` - Informacion del user actual (incluye rol)
  - `GET /roles` - Lista de roles del sistema
  - `POST /admin/users` - Create users

### Frontend (React)
- **Responsabilidad**: Presentacion
- **Maneja**: Renderizado de vistas segun rol, UI/UX
- **NO maneja**: Logica de negocio, asignacion de roles

##  Flujo de Authentication Completo

```

 1. USUARIO INICIA SESION                                        
    Input: email + password                                      

                          

 2. FIREBASE AUTHENTICATION                                      
    - Valida credenciales                                        
    - Genera token JWT                                           
    Output: Firebase User + JWT Token                            

                          

 3. AUTHCONTEXT RECIBE EL USUARIO                               
    - onAuthStateChanged() detecta el cambio                     
    - Obtiene el token JWT del user                           

                          

 4. LLAMADA AL BACKEND                                           
    GET /users/me                                                
    Headers: { Authorization: "Bearer <token>" }                 

                          

 5. BACKEND PROCESA LA PETICION                                 
    - Valida el token JWT con Firebase                           
    - Extrae el firebase_uid del token                           
    - Busca el user en la BD por firebase_uid                 
    - Devuelve UserResponseDTO (incluye rol)                     
    Output: {                                                    
      email: "user@example.com",                                 
      role: "SUPER_ADMIN",                                       
      first_name: "John",                                        
      ...                                                        
    }                                                            

                          

 6. AUTHCONTEXT GUARDA EL ROL                                   
    - setUserRole("SUPER_ADMIN")                                 
    - setUser(firebaseUser)                                      
    - setLoading(false)                                          

                          

 7. DASHBOARD SE RENDERIZA                                      
    - Lee userRole del context                                   
    - Normaliza "SUPER_ADMIN"  "super_admin"                    

                          

 8. BUSCA LA VISTA EN roleViewsConfig                           
    roleViewsConfig["super_admin"]  SuperAdminView              

                          

 9. RENDERIZA SuperAdminView                                     
    - Componente se monta                                        
    - useEffect() se ejecuta                                     

                          

 10. VISTA CARGA DATOS DEL USUARIO                              
     GET /users/me (nuevamente)                                  
     - Muestra information completa del perfil                   
     - Muestra funcionalidades segun el rol                      

                          
                     USUARIO VE SU PANEL 
```

##  Validacion de Token en el Backend

```python
from firebase_admin import auth
from fastapi import Depends, HTTPException, Header

async def get_current_user(authorization: str = Header(None)) -> User:
    """
    Valida el token JWT de Firebase y retorna el user.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No autenticado")
    
    token = authorization.split("Bearer ")[1]
    
    try:
        # Firebase valida el token
        decoded_token = auth.verify_id_token(token)
        firebase_uid = decoded_token['uid']
        
        # Search user en BD por firebase_uid
        user = user_repository.get_by_firebase_uid(firebase_uid)
        
        if not user:
            raise HTTPException(status_code=404, detail="User no encontrado")
            
        return user
        
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token invalid")
```

##  Modelo de Datos

### En Firebase
```json
{
  "uid": "abc123...",
  "email": "user@example.com",
  "emailVerified": true
}
```
**Nota:** Firebase NO almacena el rol

### En Backend (Base de Datos)
```json
{
  "identification_number": "123456789",
  "document_type": "CC",
  "first_name": "John",
  "last_name": "Doe",
  "email": "user@example.com",
  "state": "A",
  "firebase_uid": "abc123...",
  "phone": "+573001234567",
  "role": "SUPER_ADMIN"   ROL AQUI
}
```

### En Frontend (Context)
```typescript
{
  user: FirebaseUser,  // De Firebase
  userRole: "SUPER_ADMIN",  // Del backend
  loading: false,
  login: Function,
  logout: Function
}
```

##  Por Que Esta Arquitectura

### OK Ventajas

1. **Separacion de responsabilidades**
   - Firebase hace lo que mejor hace: autenticacion
   - Backend maneja toda la logica de negocio
   - Frontend solo presenta information

2. **Flexibilidad**
   - Puedes cambiar roles sin tocar Firebase
   - Puedes agregar permisos complejos en el backend
   - Frontend se adapta automaticamente

3. **Seguridad**
   - Los roles se validan en el backend
   - No se puede manipular el rol desde el frontend
   - Firebase solo valida que el token sea legitimo

4. **Escalabilidad**
   - Agregar nuevos roles es trivial
   - Agregar permisos granulares es facil
   - No hay limites de Firebase custom claims

5. **Single Source of Truth**
   - El backend es la unica fuente de verdad para roles
   - No hay sincronizacion entre Firebase y BD

###  Consideraciones

- Se hace una llamada extra a `/users/me` al iniciar sesion
- El token debe enviarse en cada peticion al backend
- Si el backend esta caido, no se puede obtener el rol

##  Flujo de Actualizacion de Rol

Si se actualiza el rol de un user:

```
1. Admin cambia rol en BD (backend)
2. User debe cerrar sesion y volver a iniciar
3. Al iniciar sesion, /users/me devuelve el nuevo rol
4. Frontend renderiza la nueva vista
```

**Nota:** Para actualizacion en tiempo real, considera implementar WebSockets o polling.

##  Endpoints del Backend

### `/users/me`
```python
@router.get("/users/me", response_model=UserResponseDTO)
def read_users_me(current_user: User = Depends(get_current_user)):
    return UserMapper.to_response_dto(current_user)
```
**Proposito:** Obtener information del user actual (incluye rol)

### `/roles`
```python
@router.get("/roles", response_model=RolesResponseDTO)
def get_available_roles(
    get_roles_use_case: GetAvailableRoles = Depends(...)
):
    return get_roles_use_case.execute()
```
**Proposito:** Listar todos los roles disponibles en el sistema

### `/admin/users`
```python
@router.post("/admin/users", response_model=UserResponseDTO)
def create_user(
    user_data: CreateUserDTO,
    current_user: User = Depends(require_manager_role)
):
    return create_user_use_case.execute(user_data)
```
**Proposito:** Create nuevos users (solo MANAGER)
