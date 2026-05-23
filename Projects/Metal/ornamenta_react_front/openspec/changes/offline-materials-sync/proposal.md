# Proposal: GestiAn de Estado Offline y SincronizaciAn para CreaciAn de Materials

**Creado**: 2026-05-22  
**Author:** Joseff Antonio Laverde Avendano
**Estado**: Bajo RevisiAn  
**Contexto**: Serviperfiles React Frontend (PWA)

---

## 1. DIAGNA"STICO Y DEUDA TACNICA

A pesar de contar con una arquitectura de sincronizaciAn offline robusta basada en IndexedDB, la experiencia de creaciAn de materials offline presenta tres fallas crAticas que bloquean su viabilidad en producciAn:

### A. Falla en CachA(c) de Datos Maestros (Selects Rotos)
* **El Problema**: Para renderizar el formulario de creaciAn de materials (`CreateMaterial.tsx`), el frontend realiza llamadas HTTP GET a los endpoints `/api/material-types` y `/api/compositions` para poblar los componentes de selecciAn. 
* **Impacto**: Estando offline, estas llamadas fallan inmediatamente devolviendo un error de API. El formulario se renderiza sin dropdowns utilizables, imposibilitando fAsicamente que el operario complete el formulario de creaciAn de materials.
* **Deuda TA(c)cnica**: No hay una estrategia de almacenamiento persistente en cachA(c) para lecturas rApidas de catAlogos de solo lectura.

### B. PA(c)rdida de Integridad en Offline (Payloads Mutilados)
* **El Problema**: Los materials creados offline a menudo pierden relaciones o atributos requeridos (como los IDs locales de imagen de `localMediaStore` o los tipos de unidad) antes de ser encolados en IndexedDB.
* **Impacto**: Al recuperar la conexiAn, la operaciAn encolada se despacha con un payload corrupto o incompleto, haciendo que el backend rebote el request con errores 400 (Bad Request) y dejando al client en un limbo de sincronizaciAn fallida.
* **Deuda TA(c)cnica**: Falta de tipado estricto e inmutabilidad en el almacenamiento serializado de operaciones pendientes dentro de IndexedDB.

### C. Bug CrAtico de DesincronizaciAn de Estado (Bucle Offline en ReconexiAn)
* **El Problema**: Al transicionar de `offline` a `online` (evento de red recuperado), ciertos mAdulos internos y contextos de React (ej. `MaterialsContext`) quedan atrapados en estado offline. Siguen asumiendo que no hay conexiAn de red y omiten/suprimen las llamadas HTTP normales del `apiClient`.
* **Impacto**: La PWA no reactiva la comunicaciAn en tiempo real. El user ve que el navegador reporta estar conectado, pero el dashboard no carga datos frescos y las acciones quedan bloqueadas "en espera de conexiAn".
* **Deuda TA(c)cnica**: Falta de un mecanismo pub/sub reactivo central que garantice la propagaciAn inmediata e irrevocable del cambio de estado de red a todos los intermediarios e interceptores HTTP.

---

## 2. OBJETIVOS

1. **Formularios Disponibles Siempre**: Garantizar el renderizado completo y correcto de los formularios de materials y products en situaciones de nula o baja conectividad.
2. **Integridad del Modelo de Datos**: Asegurar que cualquier payload de creaciAn/mutaciAn encolado en IndexedDB conserve el 100% de su estructura y tipos.
3. **Destrabe de Red Irrevocable**: Asegurar que la transiciAn al estado `online` reactive de forma instantAnea el envAo de peticiones HTTP en todos los clients, contextos y mAdulos del sistema.

---

## 3. NON-GOALS

* Implementar ediciAn offline compleja con resoluciAn de conflictos de versiones en backend (se usa la polAtica de "Altimo en llegar escribe").
* Soportar la sincronizaciAn offline de archivos pesados de medios sin compresiAn previa.

