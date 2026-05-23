# Sistema de Cotizaciones, Works y Tasks

##  Resumen Ejecutivo

Este document describe la implementacion completa del modulo de gestion de works, cotizaciones y tasks para el sistema de ornamentacion. El sistema utiliza patrones de diseno robustos para manejar el ciclo de vida completo desde la quotation hasta la entrega.

##  Arquitectura General

### Flujo de Estados del Work

```
DRAFT  QUOTED  IN_PROGRESS  DELIVERED
```

1. **DRAFT**: Borrador, se agregan/eliminan products libremente
2. **QUOTED**: Cotizado, precios congelados (snapshot), aun se pueden agregar products
3. **IN_PROGRESS**: En proceso, tasks generadas y asignadas a empleados
4. **DELIVERED**: Entregado al client, inmutable

### Flujo de Estados de Task

```
PENDING  ASSIGNED  READY  IN_PROGRESS  COMPLETED  FINISHED
```

1. **PENDING**: Task no asignada
2. **ASSIGNED**: Asignada pero bloqueada por task anterior (solo en secuencias)
3. **READY**: Asignada y desbloqueada, lista para comenzar
4. **IN_PROGRESS**: Empleado trabajando en ella
5. **COMPLETED**: Empleado completo, pending de validacion (solo EMPLOYEE)
6. **FINISHED**: Completada y validada (o auto-validada)

##  Patrones de Diseno Implementados

### 1. State Pattern (WorkState)

**Ubicacion**: `app/domain/value_objects/work_state.py`

**Proposito**: Manejar transiciones de estados del work con validaciones especificas por estado.

**Estados implementados**:
- `DraftState`: Permite agregar/delete products
- `QuotedState`: Precios congelados, aun permite agregar products
- `InProgressState`: Tasks generadas, no permite modificar products
- `DeliveredState`: Estado final, inmutable

**Ejemplo de uso**:
```python
# Create work en estado DRAFT
work = Work(
    work_id=uuid4(),
    identification_number_client=client_doc,
    work_name="Porton y ventanas",
    description="Work completo de ornamentacion",
    state=DraftState()
)

# Agregar products
work.add_product(porton_composite, quantity=1)
work.add_product(ventana_simple, quantity=3)

# Cotizar (DRAFT  QUOTED)
work.quote(quoted_by=manager, products_registry=products_dict)

# Iniciar work (QUOTED  IN_PROGRESS)
work.start_work(started_by=manager, products_registry=products_dict)

# Entregar (IN_PROGRESS  DELIVERED)
work.deliver(delivered_by=manager)
```

### 2. Strategy Pattern (TaskCompletionStrategy)

**Ubicacion**: `app/domain/strategies/task_completion_strategy.py`

**Proposito**: Manejar la logica de completitud y validacion de tasks segun el rol del user.

**Estrategias implementadas**:
- `EmployeeTaskCompletionStrategy`: Requiere validacion posterior
- `SupervisorTaskCompletionStrategy`: Auto-validada
- `ManagerTaskCompletionStrategy`: Auto-validada

**Ejemplo de uso**:
```python
# EMPLOYEE completa task (requiere validacion)
employee_task.complete(completed_by=employee)
# Status: IN_PROGRESS  COMPLETED

# SUPERVISOR valida
employee_task.validate(validated_by=supervisor)
# Status: COMPLETED  FINISHED

# SUPERVISOR completa task (auto-validada)
supervisor_task.complete(completed_by=supervisor)
# Status: IN_PROGRESS  FINISHED directamente
```

### 3. Factory Pattern (TaskFactory)

**Ubicacion**: `app/domain/factories/task_factory.py`

**Proposito**: Generar tasks automaticamente desde products (simples o compuestos).

**Logica**:
- `SimpleProduct`  1 Task
- `CompositeProduct`  N Tasks (recursivamente)
- Mantiene orden de ejecucion y bloqueos secuenciales

**Ejemplo de uso**:
```python
# Generar tasks desde un product compuesto
tasks, next_order = TaskFactory.create_tasks_from_product(
    product=puerta_composite,
    work_id=work.work_id,
    product_quantity=2,
    base_order=0
)

# Las tasks de un CompositeProduct son secuenciales
# Primera task: estado READY
# Siguientes tasks: estado ASSIGNED (bloqueadas)
```

### 4. Observer Pattern (TaskObserver)

**Ubicacion**: `app/domain/observers/task_observer.py`

**Proposito**: Notificar a empleados cuando sus tasks son desbloqueadas.

**Ejemplo de uso**:
```python
# Configurar observador
from app.domain.observers.task_observer import TaskNotificationObserver, get_task_event_subject

notification_observer = TaskNotificationObserver()
subject = get_task_event_subject()
subject.attach(notification_observer)

# Al completar una task, se desbloquea la siguiente
next_task = work.unblock_next_task(completed_task)

# Procesar eventos
events = work.clear_domain_events()
subject.process_domain_events(events)

# El empleado puede ver sus notificaciones
notifications = notification_observer.get_notifications_for_user(employee_id)
```

### 5. Composite Pattern (Product)

**Ubicacion**: `app/domain/models/product.py` (ya existente)

**Proposito**: Manejar products simples y compuestos (con anidacion).

**Soporte extendido**:
- `CompositeProduct` puede contener otros `CompositeProduct`
- Ejemplo: Puerta-Ventana contiene Puerta (composite) y Ventana (composite)

##  Entidades y Value Objects

### Work (Aggregate Root)

**Ubicacion**: `app/domain/models/work.py`

**Responsabilidades**:
- Gestionar products y sus snapshots
- Controlar transiciones de estados
- Generar tasks desde products
- Calcular valores con tax
- Gestionar desbloqueo de tasks secuenciales

**Atributos principales**:
```python
work_id: UUID
identification_number_client: DocumentNumber
work_name: str
state: WorkState
products: List[ProductWorkItem]
tasks: List[Task]
tax: float  # Ej: 0.15 = 15%
```

**Metodos clave**:
- `add_product()`: Agrega product (con snapshot si esta cotizado)
- `remove_product()`: Elimina product (solo DRAFT/QUOTED)
- `quote()`: Cotiza work, congela precios
- `start_work()`: Inicia work, genera tasks
- `deliver()`: Entrega work (todas las tasks finalizadas)
- `unblock_next_task()`: Desbloquea siguiente task en secuencia

### ProductWorkItem (Value Object)

**Ubicacion**: `app/domain/value_objects/product_work_item.py`

**Proposito**: Representa un product dentro de un work con su snapshot congelado.

**Atributos**:
```python
product_id: UUID
work_id: UUID
quantity: int
execution_order: int
state: ProductItemState  # PENDING, IN_PROGRESS, COMPLETED
snapshot: Optional[ProductSnapshot]
task_ids: List[UUID]
```

### ProductSnapshot (Value Object)

**Ubicacion**: `app/domain/value_objects/product_snapshot.py`

**Proposito**: Snapshot inmutable del price y composicion de un product.

**Atributos**:
```python
product_id: UUID
product_name: str
product_type: str  # "simple" o "composite"
price: Money
composition: Dict[str, Any]  # Estructura completa para auditoria
dimensions: Dict[str, float]
quantity_multiplier: Decimal
```

### Task (Entity)

**Ubicacion**: `app/domain/models/task.py`

**Atributos nuevos**:
```python
product_id: UUID  # Product del cual se genero
execution_order: int
requires_validation: bool
is_blocked: bool
previous_task_id: Optional[UUID]
completed_by_user_id: Optional[UUID]
validated_by_user_id: Optional[UUID]
```

**Metodos clave**:
- `assign_to()`: Asigna a user (solo SUPERVISOR/MANAGER)
- `reassign_to()`: Reasigna a otro user
- `unblock()`: Desbloquea task (genera evento)
- `start()`: Inicia task (READY  IN_PROGRESS)
- `complete()`: Completa segun estrategia del rol
- `validate()`: Valida task (solo SUPERVISOR/MANAGER)

##  Flujo Completo de Negocio

### 1. Creation de Quotation

```python
# 1. MANAGER crea work
work = Work(
    work_id=uuid4(),
    identification_number_client=client.identification_number,
    work_name="Porton y 3 ventanas",
    description="Work completo",
    state=DraftState(),
    tax=0.15  # 15% ganancia
)

# 2. Agregar products (DRAFT)
work.add_product(porton_composite, quantity=1, execution_order=0)
work.add_product(ventana_simple, quantity=3, execution_order=1)

# 3. Cotizar (congela precios)
work.quote(quoted_by=manager, products_registry=products_dict)

# Ahora:
# - work.state = QUOTED
# - Cada product tiene su snapshot congelado
# - products_value = suma de products con snapshots
# - work_value = products_value  (1 + 0.15)
```

### 2. Inicio de Work

```python
# 1. MANAGER inicia work
tasks = work.start_work(
    started_by=manager,
    products_registry=products_dict
)

# Ahora:
# - work.state = IN_PROGRESS
# - Tasks generadas automaticamente desde products
# - Tasks secuenciales estan bloqueadas
# - Primera task de cada product: PENDING

# 2. SUPERVISOR/MANAGER asigna tasks
for task in tasks:
    if task.is_pending:
        # Asignar a empleado
        task.assign_to(user=employee, assigned_by=supervisor)
        # Si no esta bloqueada: PENDING  READY
        # Si esta bloqueada: PENDING  ASSIGNED
```

### 3. Ejecucion de Tasks

```python
# 1. EMPLOYEE inicia task
task.start(started_by=employee)  # READY  IN_PROGRESS

# 2. EMPLOYEE completa task
task.complete(completed_by=employee)  # IN_PROGRESS  COMPLETED

# 3. SUPERVISOR valida task
task.validate(validated_by=supervisor)  # COMPLETED  FINISHED

# 4. Desbloquear siguiente task (automatico en Work)
next_task = work.unblock_next_task(task)
if next_task:
    # ASSIGNED  READY
    # Se genera evento TaskUnblocked
    # Observer notifica al empleado asignado
```

### 4. Entrega del Work

```python
# Verificar que todas las tasks esten finalizadas
if work.completion_percentage == 100:
    work.deliver(delivered_by=manager)
    # work.state = DELIVERED
    # work.end_delivery_date = ahora
```

##  Calculo de Valores

### Products Value (Valor de Products)

```python
products_value = (product.snapshot.price  product.quantity)
```

### Work Value (Valor Total del Work)

```python
work_value = products_value  (1 + tax)

# Ejemplo:
# products_value = $1,000,000
# tax = 0.15 (15%)
# work_value = $1,000,000  1.15 = $1,150,000
```

### Completion Percentage (Porcentaje de Completitud)

```python
completion_percentage = (tareas_finished / total_tareas)  100
```

##  Permisos y Roles

### MANAGER

**Puede**:
- Create works
- Cotizar works
- Iniciar works
- Entregar works
- Asignar tasks
- Reasignar tasks
- Validar tasks
- Completar tasks (auto-validadas)

### SUPERVISOR

**Puede**:
- Asignar tasks
- Reasignar tasks
- Validar tasks
- Completar tasks (auto-validadas)

**No puede**:
- Create works
- Cotizar works
- Iniciar works
- Entregar works

### EMPLOYEE

**Puede**:
- Completar tasks (requiere validacion)

**No puede**:
- Create/cotizar/iniciar/entregar works
- Asignar/reasignar tasks
- Validar tasks

##  Eventos de Dominio

### Work Events

- `WorkCreated`: Work created
- `WorkQuoted`: Work cotizado (precios congelados)
- `WorkStarted`: Work iniciado (tasks generadas)
- `WorkDelivered`: Work entregado
- `ProductAddedToWork`: Product agregado al work
- `ProductRemovedFromWork`: Product eliminado del work

### Task Events

- `TaskAssigned`: Task assigned a user
- `TaskReassigned`: Task reasignada a otro user
- `TaskUnblocked`: Task desbloqueada (lista para ejecutar)
- `TaskCompleted`: Task completada por user
- `TaskValidated`: Task validada por supervisor/manager
- `TaskStateChanged`: Estado de task cambio

##  Ejemplo Completo de Uso

```python
from uuid import uuid4
from datetime import datetime, timedelta
from decimal import Decimal

from app.domain.models.work import Work
from app.domain.models.user import User, RoleEnum
from app.domain.models.client import Client
from app.domain.models.product import SimpleProduct, CompositeProduct
from app.domain.value_objects.work_state import DraftState
from app.domain.value_objects import DocumentNumber, Email, Money

# 1. Setup: Users
manager = User(
    identification_number=DocumentNumber(value="12345"),
    role=RoleEnum.MANAGER,
    first_name="Carlos",
    last_name="Gerente",
    email=Email(value="manager@empresa.com"),
    state=StateUser(value=StateUserEnum.ACTIVE),
    firebase_uid="uid_manager"
)

supervisor = User(
    identification_number=DocumentNumber(value="67890"),
    role=RoleEnum.SUPERVISOR,
    first_name="Ana",
    last_name="Supervisora",
    email=Email(value="supervisor@empresa.com"),
    state=StateUser(value=StateUserEnum.ACTIVE),
    firebase_uid="uid_supervisor"
)

employee = User(
    identification_number=DocumentNumber(value="11111"),
    role=RoleEnum.EMPLOYEE,
    first_name="Juan",
    last_name="Empleado",
    email=Email(value="employee@empresa.com"),
    state=StateUser(value=StateUserEnum.ACTIVE),
    firebase_uid="uid_employee"
)

# 2. Setup: Client
client = Client(
    identification_number=DocumentNumber(value="22222"),
    first_name="Pedro",
    last_name="Client",
    email=Email(value="client@email.com"),
    phone="555-1234",
    address="Calle 123"
)

# 3. Setup: Products
# (Supongamos que ya tenemos products creados)
porton = CompositeProduct(id=uuid4(), name="Porton Galvanizado")
ventana = SimpleProduct(id=uuid4(), name="Ventana Aluminio", material=aluminio_material)

products_dict = {
    porton.id: porton,
    ventana.id: ventana
}

# 4. Create work (DRAFT)
work = Work(
    work_id=uuid4(),
    identification_number_client=client.identification_number,
    work_name="Porton y 3 Ventanas - Casa Sr. Pedro",
    description="Instalacion completa de porton y ventanas",
    state=DraftState(),
    tax=0.15,
    start_date=datetime.utcnow(),
    end_aprox_delivery_date=datetime.utcnow() + timedelta(days=15)
)

# 5. Agregar products
work.add_product(porton, quantity=1, execution_order=0)
work.add_product(ventana, quantity=3, execution_order=1)

# 6. Cotizar (DRAFT  QUOTED)
work.quote(quoted_by=manager, products_registry=products_dict)

print(f"Valor products: {work.products_value}")
print(f"Valor work (con 15% tax): {work.work_value}")

# 7. Client acepta, iniciar work (QUOTED  IN_PROGRESS)
tasks = work.start_work(started_by=manager, products_registry=products_dict)

print(f"Tasks generadas: {len(tasks)}")

# 8. SUPERVISOR asigna tasks
for task in work.get_ready_tasks():
    task.assign_to(user=employee, assigned_by=supervisor)

# 9. EMPLOYEE ejecuta primera task
first_task = work.get_ready_tasks()[0]
first_task.start(started_by=employee)
first_task.complete(completed_by=employee)

# 10. SUPERVISOR valida
supervisor.validate(validated_by=supervisor)

# 11. Desbloquear siguiente task
next_task = work.unblock_next_task(first_task)
if next_task:
    print(f"Task desbloqueada: {next_task.task_name}")
    
    # Observer notifica al empleado
    events = work.clear_domain_events()
    # Procesar eventos para enviar notificaciones...

# 12. Continuar hasta completar todas las tasks...

# 13. Entregar work (IN_PROGRESS  DELIVERED)
if work.completion_percentage == 100:
    work.deliver(delivered_by=manager)
    print(f"Work entregado en: {work.end_delivery_date}")
```

##  Conclusion

El sistema implementado utiliza patrones de diseno robustos para manejar un flujo complejo de negocio:

- **State Pattern**: Maneja transiciones de estados con validaciones
- **Strategy Pattern**: Logica de validacion segun roles
- **Factory Pattern**: Generacion automatica de tasks
- **Observer Pattern**: Notificaciones de desbloqueo
- **Composite Pattern**: Products anidados
- **Aggregate Pattern**: Work como aggregate root

La arquitectura es extensible, testeable y sigue principios SOLID.

