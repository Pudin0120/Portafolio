# Delta Spec: offline-materials-sync

## Goal

Habilitar la creation offline de materials e insumos de forma integra garantizando la disponibilidad offline de catalogos maestros y corrigiendo el bloqueo reactivo en la reconexion de red del client HTTP.

---

## 1. REQUISITOS DEL SISTEMA

### R1. Disponibilidad Offline de Catalogos Maestros (Tipos y Composiciones)
El Service Worker DEBE interceptar y cachear de forma persistente los endpoints de datos maestros necesarios para el formulario de creation.
* **Endpoints a Interceptar**:
  * `GET /api/material-types` (o endpoint equivalente de tipos de materials)
  * `GET /api/compositions` (o endpoint equivalente de composiciones de materials)
* **Estrategia de SW**: **Network-First**. Si hay conexion, realiza la peticion HTTP directamente contra el backend para garantizar frescura absoluta. Si el fetch falla (offline o problemas de red), sirve el recurso desde el cache persistente sin disparar error de cara a la UI.

### R2. Preservacion y Tipado de Payloads en IndexedDB
El payload de creation en IndexedDB DEBE ser una replica exacta e inmutable de lo que recibiria la API en produccion.
* **Esquema de Almacenamiento**: La tabla `pending_operations` debe persistir el payload completo de creation del material.
* **Sanitizacion Pre-Encolado**:
  * Los IDs temporales de recursos locales (como URIs de `localMediaStore` para imagenes de materials) DEBEN mapearse con prefijos univocos (ej. `local-media://`) para evitar que el backend los confunda con URLs reales de Firebase en la sincronizacion diferida.
  * No se permite omitir campos requeridos (SKU, nombre, price, tipo, composicion) al serializar para la cola.

### R3. Destrabe Reactivo de Conectividad (Resolucion de Bucle Offline)
El `ConnectivityProvider` y el `apiClient` DEBEN sincronizar su estado de red de manera instantanea y reactiva ante el cambio a `online`.
* **Mecanismo de Desbloqueo**:
  * Al dispararse el evento `online` en el navegador, se DEBE invocar una function centralizadora `resumeHttpQueue()`.
  * Esta function limpiara explicitamente cualquier flag estatico de "offline" en el `apiClient` e invalidara la supresion de llamadas GET y POST.
  * El `ConnectivityProvider` DEBE emitir un evento global `connection-restored` que obligue a los contexts activos a re-suscribirse o refrescar su estado de inmediato en lugar de depender de la interaccion del user.

---

## 2. HISTORIAS DE USUARIO Y ESCENARIOS GHERKIN

### Historia de User 1: Creation de Insumo Offline con Formulario Completo
**COMO** Operario de Inventario en el galpon (sin senal de internet)  
**QUIERO** abrir la pantalla de "Creation de Materials", ver los selectores de tipos y composiciones con datos, y save el nuevo insumo  
**PARA QUE** el sistema lo guarde localmente y no pierda mi work de registro.

#### Escenario: Renderizado y guardado exitoso sin red
* **Dado** que el dispositivo del operario no tiene conexion a internet (`navigator.onLine = false`)
* **Y** que los datos de "Material Types" y "Composiciones" fueron previamente cacheados por el Service Worker en una sesion online anterior
* **Cuando** el operario accede al formulario de "Creation de Materials"
* **Entonces** la aplicacion DEBE cargar los datos maestros desde la cache de forma instantanea
* **Y** permitir al user seleccionar el "Tipo de Material" y "Composicion"
* **Cuando** el operario hace clic en "Create Material"
* **Entonces** la aplicacion DEBE generar un UUID temporal para el material
* **Y** encolar la operacion de creation (`CREATE_MATERIAL`) con el payload estructurado e intacto en el IndexedDB (`pending_operations`)
* **Y** mostrar un aviso de exito local: "Material guardado localmente (Offline)".

---

### Historia de User 2: Destrabe Reactivo y Sincronizacion Automatica
**COMO** Administrador del Sistema  
**QUIERO** que cuando el operario recupere la conexion de red, la PWA reactive de forma inmediata y automatica las peticiones HTTP y vacie la cola offline  
**PARA** evitar que el sistema quede trabado asumiendo un estado sin conexion inexistente.

#### Escenario: Recuperacion automatica del flujo HTTP y vaciado de cola sin recarga manual
* **Dado** que el user tiene 1 operacion de creation de material pending en la cola de IndexedDB
* **Y** que la aplicacion quedo en estado "offline" (con las llamadas HTTP GET y POST suprimidas)
* **Cuando** el navegador emite el evento `online` (transicion offline -> online)
* **Entonces** la aplicacion DEBE disparar reactivamente el evento global `connection-restored`
* **Y** el `apiClient` DEBE limpiar de forma inmediata e incondicional cualquier flag de bloqueo offline
* **Y** DEBE iniciar automaticamente la ejecucion de `syncPendingOperations()`
* **Cuando** la sincronizacion del material finalice exitosamente en el backend
* **Entonces** la cola de IndexedDB de esa operacion DEBE quedar vacia
* **Y** el listado de materials DEBE actualizarse reactivamente con el material guardado persistido en el backend sin requerir que el user recargue manualmente la pestana (F5).
