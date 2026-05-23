# Tasks: offline-materials-sync

- [ ] **Fase 1: Cache de Datos Maestros**
  - [ ] Actualizar `public/sw.ts` para registrar rutas de Workbox para `/api/material-types` y `/api/compositions` usando `StaleWhileRevalidate`.
  - [ ] Implementar plugins de cacheabilidad (statuses 200) y expiracion de cache (7 dias).

- [ ] **Fase 2: Robustez de Payloads en IndexedDB**
  - [ ] Actualizar el hook de envio del formulario de materials en `src/components/products/CreateMaterial.tsx` para generar un payload estructurado compatible con `pwaSyncContracts.ts`.
  - [ ] Integrar el mapeo de URIs locales de imagenes (`local-media://`) si se asocia una imagen tomada offline en `ImageUpload.tsx`.

- [ ] **Fase 3: Implementacion del Connectivity Bus y Correccion del Bug**
  - [ ] Create el bus de eventos de bajo nivel `src/services/pwa/connectivityBus.ts`.
  - [ ] Integrar el bus en `src/providers/ConnectivityProvider.tsx` para emitir `connection-restored` al detectar la transicion de `isOnline` a true.
  - [ ] Modificar `src/services/apiClient.ts` para suscribirse al bus y desbloquear inmediatamente cualquier flag de bloqueo offline persistente.
  - [ ] Asegurar que el cambio fuerce el disparo automatico de `syncPendingOperations()` en la reconexion de forma reactiva.

- [ ] **Fase 4: Pruebas y Validacion**
  - [ ] Create test de integracion para validar que la reconexion vacia la cola de IndexedDB y no entra en bucle offline.
  - [ ] Correr `bun run test` para asegurar regresion cero en la suite de pruebas del proyecto.
