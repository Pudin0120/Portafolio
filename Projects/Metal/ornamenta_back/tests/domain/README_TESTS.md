# Tests del Sistema de Cotizaciones, Works y Tasks

##  Resumen

Este directorio contiene tests unitarios completos para el modulo de gestion de works, cotizaciones y tasks. Los tests cubren toda la logica de negocio implementada con patrones de diseno.

##  Cobertura de Tests

### 1. test_work.py (Work Domain Model)

**Cobertura**: ~45 tests

**Tests principales**:
- OK Creation y validacion de works
- OK Properties de estado (is_draft, is_quoted, etc.)
- OK Gestion de products (add, remove, reorder)
- OK Transiciones de estado (DRAFT  QUOTED  IN_PROGRESS  DELIVERED)
- OK Creation de snapshots y congelamiento de precios
- OK Generacion de tasks desde products
- OK Desbloqueo de tasks secuenciales
- OK Calculos de valores (products_value, work_value, completion_percentage)
- OK Validaciones de permisos (solo MANAGER puede create/cotizar/iniciar/entregar)
- OK Generacion de eventos de dominio
- OK Casos edge (no agregar products en IN_PROGRESS, etc.)

**Ejemplo de ejecucion**:
```bash
pytest tests/domain/test_work.py -v
```

### 2. test_task_factory.py (TaskFactory - Factory Pattern)

**Cobertura**: ~20 tests

**Tests principales**:
- OK Generacion de tasks desde SimpleProduct
- OK Generacion de tasks desde CompositeProduct (recursivamente)
- OK Generacion desde CompositeProducts anidados
- OK Bloqueo secuencial de tasks dentro de CompositeProduct
- OK Ejecucion paralela entre products diferentes
- OK Asignacion de execution_order
- OK Properties de tasks generadas
- OK Calculo de total de tasks
- OK Casos edge (composite vacio, anidacion profunda)

**Ejemplo de ejecucion**:
```bash
pytest tests/domain/test_task_factory.py -v
```

### 3. test_task_completion_strategy.py (Strategy Pattern)

**Cobertura**: ~20 tests

**Tests principales**:
- OK EmployeeTaskCompletionStrategy (requiere validacion)
- OK SupervisorTaskCompletionStrategy (auto-validada)
- OK ManagerTaskCompletionStrategy (auto-validada)
- OK TaskCompletionStrategyFactory
- OK Validacion de permisos por rol
- OK Comparacion de comportamiento entre roles
- OK Validacion de estados
- OK Implementacion correcta de interface

**Ejemplo de ejecucion**:
```bash
pytest tests/domain/test_task_completion_strategy.py -v
```

### 4. test_task_advanced.py (Task Advanced Features)

**Cobertura**: ~35 tests

**Tests principales**:
- OK Asignacion de tasks (solo SUPERVISOR/MANAGER)
- OK Reasignacion de tasks
- OK Bloqueo y desbloqueo de tasks
- OK Inicio de tasks
- OK Completitud por EMPLOYEE (requiere validacion)
- OK Completitud por SUPERVISOR/MANAGER (auto-validada)
- OK Validacion de tasks por SUPERVISOR/MANAGER
- OK Transiciones de estado completas
- OK Generacion de eventos de dominio
- OK Validaciones de permisos
- OK Casos edge (no reasignar tasks finalizadas, etc.)

**Ejemplo de ejecucion**:
```bash
pytest tests/domain/test_task_advanced.py -v
```

### 5. test_work_state.py (WorkState - State Pattern)

**Cobertura**: ~40 tests

**Tests principales**:
- OK Properties de cada estado (DraftState, QuotedState, etc.)
- OK Operaciones permitidas por estado
- OK Transiciones valid entre estados
- OK Validacion de transiciones invalid
- OK Igualdad y hashing de estados
- OK Factory function para create estados
- OK Representacion en string
- OK Flujo completo de estados
- OK Implementacion correcta de interface

**Ejemplo de ejecucion**:
```bash
pytest tests/domain/test_work_state.py -v
```

### 6. test_task_observer.py (Observer Pattern)

**Cobertura**: ~30 tests

**Tests principales**:
- OK TaskNotificationObserver funcionalidad
- OK Creation y gestion de notificaciones
- OK TaskEventSubject suscripcion
- OK Notificacion de multiples observadores
- OK Procesamiento de eventos de dominio
- OK Singleton global del subject
- OK Flujo completo del patron Observer
- OK Independencia de notificaciones por user
- OK Contenido correcto de notificaciones
- OK Casos edge (detach inexistente, notify sin observers)

**Ejemplo de ejecucion**:
```bash
pytest tests/domain/test_task_observer.py -v
```

##  Ejecutar Todos los Tests

### Ejecutar todos los tests del modulo:
```bash
pytest tests/domain/test_work.py tests/domain/test_task_factory.py tests/domain/test_task_completion_strategy.py tests/domain/test_task_advanced.py tests/domain/test_work_state.py tests/domain/test_task_observer.py -v
```

### Ejecutar con cobertura:
```bash
pytest tests/domain/test_work.py tests/domain/test_task_factory.py tests/domain/test_task_completion_strategy.py tests/domain/test_task_advanced.py tests/domain/test_work_state.py tests/domain/test_task_observer.py --cov=app/domain --cov-report=html
```

### Ejecutar tests especificos:
```bash
# Solo tests de Work
pytest tests/domain/test_work.py -v

# Solo tests de asignacion
pytest tests/domain/test_task_advanced.py::test_supervisor_can_assign_task -v

# Solo tests de estrategias
pytest tests/domain/test_task_completion_strategy.py -k "strategy" -v
```

##  Estadisticas de Cobertura

| Modulo | Tests | Cobertura Estimada |
|--------|-------|-------------------|
| Work | 45 | ~95% |
| TaskFactory | 20 | ~100% |
| TaskCompletionStrategy | 20 | ~100% |
| Task (advanced) | 35 | ~90% |
| WorkState | 40 | ~100% |
| TaskObserver | 30 | ~95% |
| **TOTAL** | **~190** | **~95%** |

##  Estructura de Tests

Todos los tests siguen el patron AAA (Arrange-Act-Assert):

```python
def test_something():
    """Test description."""
    # ARRANGE: Setup fixtures
    work = create_work()
    product = create_product()
    
    # ACT: Execute operation
    work.add_product(product, quantity=1)
    
    # ASSERT: Verify results
    assert len(work.products) == 1
```

##  Fixtures Comunes

Todos los archivos de test usan fixtures comunes:

- `manager`: User con rol MANAGER
- `supervisor`: User con rol SUPERVISOR
- `employee`: User con rol EMPLOYEE
- `client`: Client para works
- `simple_product`: Product simple con material
- `composite_product`: Product compuesto
- `pending_task`: Task en estado PENDING

##  Convenciones de Nombres

- `test_<feature>_success`: Test del caso exitoso
- `test_<feature>_raises_error`: Test que verifica excepciones
- `test_cannot_<action>`: Test de restricciones
- `test_<role>_can_<action>`: Test de permisos por rol

##  Debugging Tests

### Ver output detallado:
```bash
pytest tests/domain/test_work.py -v -s
```

### Ver solo failures:
```bash
pytest tests/domain/test_work.py --tb=short
```

### Ejecutar ultimo test fallido:
```bash
pytest --lf
```

### Modo interactivo (pdb):
```bash
pytest tests/domain/test_work.py --pdb
```

## OK Verificacion de Tests

Antes de hacer commit, ejecutar:

```bash
# 1. Linter
pytest tests/domain/test_*.py --flake8

# 2. Type checking
mypy tests/domain/test_*.py

# 3. Tests completos
pytest tests/domain/ -v --cov=app/domain

# 4. Verificar que no hay tests skippeados
pytest tests/domain/ --strict-markers
```

##  Proximos Tests a Implementar

Para completar la cobertura al 100%:

1. **Integration Tests**: Tests de integracion Work-Task-Product
2. **Repository Tests**: Tests de persistencia (SQLAlchemy)
3. **Use Case Tests**: Tests de casos de uso (QuoteWorkUseCase, etc.)
4. **API Tests**: Tests de endpoints REST
5. **Performance Tests**: Tests de rendimiento con muchos products/tasks

##  Troubleshooting

### Tests fallan con ImportError:
```bash
# Asegurate de que estas en el virtualenv
source venv/bin/activate

# Instala dependencias
pip install -r requirements.txt
```

### Tests fallan con DatabaseError:
```bash
# Los tests de dominio NO requieren base de datos
# Si ves errores de DB, verifica que no estes usando repositorios reales
```

### Fixtures no encontradas:
```bash
# Verifica que las fixtures esten definidas en el mismo archivo
# o en conftest.py
```

##  Referencias

- [Pytest Documentation](https://docs.pytest.org/)
- [WORK_QUOTATION_TASK_SYSTEM.md](../../docs/WORK_QUOTATION_TASK_SYSTEM.md)
- [Design Patterns Used](../../docs/WORK_QUOTATION_TASK_SYSTEM.md#patrones-de-diseno-aplicados)

