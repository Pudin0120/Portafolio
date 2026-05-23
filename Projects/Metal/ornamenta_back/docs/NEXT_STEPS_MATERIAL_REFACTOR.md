# Proximos Pasos: Refactor de Materials y Estrategias

Este document detalla las tasks pendientes tras la estabilizacion del backend y la correccion de las regresiones iniciales en los tests de materials.

## 1. Correccion de Tests de Infraestructura
- [ ] **Archivo**: `tests/infrastructure/test_material_repository.py`
- [ ] **Problema**: Error `fixture 'mock_unit_repo' not found`.
- [ ] **Accion**: 
    - Verificar si `mock_unit_repo` debe estar en `tests/conftest.py`.
    - Asegurar que el repositorio use un `unit_repo` valid (real o mock) durante las pruebas de integracion.
    - Habilitar la extension `citext` automaticamente en el setup de la DB de tests si no existe.

## 2. Limpieza de Codigo Obsoleto (Tests de Aplicacion)
- [ ] **Archivo**: `tests/application/test_material_name_services.py`
- [ ] **Problema**: Estos tests prueban servicios que ya no existen (borrados durante el refactor).
- [ ] **Accion**: 
    - Delete este archivo.
    - Create `tests/domain/test_measurement_strategies.py` para probar directamente que `SHEET`, `TUBE`, `LIQUID`, etc., generen las descripciones y cantidades correctas sin depender de la capa de aplicacion.

## 3. Validacion de Estrategias Especificas
- [ ] **Estrategia TUBE**: Verificar que el calculo de peso por metro lineal y la description incluyan diametro y espesor correctamente.
- [ ] **Estrategia LIQUID/SOLID**: Asegurar que la densidad se use correctamente para convertir unidades de volumen a masa si es necesario.
- [ ] **Estrategia LABOR**: Validar que el calculo de tiempo y costo de mano de obra siga la logica de `labor_measurement_strategy.py`.

## 4. Auditoria de Factory y Persistencia
- [ ] **MaterialFactory**: Asegurar que la reconstruccion de objetos desde la DB (JSONB `properties`) sea 100% robusta para todos los tipos de materials historicos.
- [ ] **PropertySerializer**: Verificar que no haya perdida de precision al serializar `Decimal` a JSON.

---
**Nota**: El backend esta corriendo en Docker y la base de datos de test `serviperfiles_test_db` ya esta creada con la extension `citext` habilitada manualmente.
