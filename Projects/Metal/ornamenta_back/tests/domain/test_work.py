"""
Unit tests for Work domain model (Aggregate Root).

Tests cover:
- Work creation and validation
- State transitions (DRAFT  QUOTED  IN_PROGRESS  DELIVERED)
- Product management (add, remove, reorder)
- Snapshot creation and price freezing
- Task generation from products
- Task unblocking mechanism
- Value calculations (products_value, work_value, completion_percentage)
- Permission validations (only MANAGER can create/quote/start/deliver)
"""
import pytest
from decimal import Decimal
from uuid import uuid4
from datetime import datetime, timedelta

from app.domain.models.work import Work
from app.domain.models.product import SimpleProduct, CompositeProduct
from app.domain.models.material import Material
from app.domain.models.material_type import MaterialType
from app.domain.models.unit_of_measure import UnitOfMeasure
from app.domain.models.user import User, RoleEnum
from app.domain.models.client import Client
from app.domain.value_objects import DocumentNumber, Email, Money
from app.domain.value_objects.document_number import DocumentEnum
from app.domain.value_objects.state_user import StateUser, StateEnum as StateUserEnum
from app.domain.value_objects.work_state import DraftState, QuotedState, InProgressState, DeliveredState, WorkStateEnum
from app.domain.value_objects.product_work_item import ProductWorkItem, ProductItemState
from app.domain.strategies.sheet_measurement_strategy import SheetMeasurementStrategy
from app.domain.events.work_events import WorkQuoted, WorkStarted, WorkDelivered, ProductAddedToWork


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def manager():
    """Manager user fixture."""
    return User(
        identification_number=DocumentNumber(value="12345", doc_type=DocumentEnum.CC),
        role=RoleEnum.MANAGER,
        first_name="Carlos",
        last_name="Gerente",
        email=Email(value="manager@empresa.com"),
        state=StateUser(value=StateUserEnum.ACTIVE),
        firebase_uid=str(uuid4())  # UUID valid para firebase_uid
    )


@pytest.fixture
def supervisor():
    """Supervisor user fixture."""
    return User(
        identification_number=DocumentNumber(value="67890", doc_type=DocumentEnum.CC),
        role=RoleEnum.SUPERVISOR,
        first_name="Ana",
        last_name="Supervisora",
        email=Email(value="supervisor@empresa.com"),
        state=StateUser(value=StateUserEnum.ACTIVE),
        firebase_uid=str(uuid4())  # UUID valid para firebase_uid
    )


@pytest.fixture
def employee():
    """Employee user fixture."""
    return User(
        identification_number=DocumentNumber(value="11111", doc_type=DocumentEnum.CC),
        role=RoleEnum.EMPLOYEE,
        first_name="Juan",
        last_name="Empleado",
        email=Email(value="employee@empresa.com"),
        state=StateUser(value=StateUserEnum.ACTIVE),
        firebase_uid=str(uuid4())  # UUID valid para firebase_uid
    )


@pytest.fixture
def client():
    """Client fixture."""
    return Client(
        identification_number=DocumentNumber(value="22222", doc_type=DocumentEnum.CC),
        first_name="Pedro",
        last_name="Client",
        email=Email(value="client@email.com"),
        phone="555-1234",
        address="Calle 123"
    )


@pytest.fixture
def square_meter_unit():
    """Unit for square meters."""
    return UnitOfMeasure(
        id=uuid4(),
        name="Metro cuadrado",
        symbol="m",
        pint_unit_text="meter ** 2",
        dimension="area"
    )


@pytest.fixture
def steel_material_type(square_meter_unit):
    """Material type for steel sheets."""
    return MaterialType(
        id=uuid4(),
        name="Acero",
        description="Material tipo lamina de acero",
        measurement_strategy="SHEET"  # Use string identifier instead of strategy object
    )


@pytest.fixture
def steel_material(steel_material_type, square_meter_unit):
    """Steel material fixture."""
    return Material(
        id=uuid4(),
        description="Acero galvanizado calibre 20",
        material_type=steel_material_type,
        price=Money(amount=Decimal("30000")),  # $30,000 por m
        properties={
            "gauge": "20",
            "thickness_mm": 0.9,
            "area": 4.0  # 4 m por lamina
        }
    )


@pytest.fixture
def simple_product(steel_material):
    """Simple product fixture (chapa)."""
    return SimpleProduct(
        id=uuid4(),
        name="Chapa Yale",
        material=steel_material,
        dimensions={"width": 0.1, "height": 0.2},
        quantity_multiplier=Decimal("0.5")
    )


@pytest.fixture
def composite_product(simple_product):
    """Composite product fixture (puerta)."""
    composite = CompositeProduct(
        id=uuid4(),
        name="Puerta Galvanizada"
    )
    
    # Agregar componentes
    marco = SimpleProduct(
        id=uuid4(),
        name="Marco de puerta",
        material=simple_product.material,
        dimensions={"width": 1.0, "height": 2.0},
        quantity_multiplier=Decimal("2.0")
    )
    
    composite.add_component(marco, quantity=1)
    composite.add_component(simple_product, quantity=1)
    
    return composite


@pytest.fixture
def draft_work(client):
    """Work in DRAFT state."""
    return Work(
        work_id=uuid4(),
        identification_number_client=client.identification_number,
        work_name="Work de prueba",
        description="Description del work",
        state=DraftState(),
        tax=0.15
    )


# ============================================================================
# TESTS: Work Creation and Validation
# ============================================================================

def test_work_creation_valid(client):
    """Test creating a valid work."""
    work = Work(
        work_id=uuid4(),
        identification_number_client=client.identification_number,
        work_name="Porton y ventanas",
        description="Work completo",
        state=DraftState(),
        tax=0.15
    )
    
    assert work.work_id is not None
    assert work.work_name == "Porton y ventanas"
    assert work.is_draft
    assert work.tax == 0.15
    assert len(work.products) == 0
    assert len(work.tasks) == 0


def test_work_creation_invalid_negative_tax(client):
    """Test that negative tax raises error."""
    with pytest.raises(ValueError, match="tax no puede ser negativo"):
        Work(
            work_id=uuid4(),
            identification_number_client=client.identification_number,
            work_name="Test",
            description="Test",
            state=DraftState(),
            tax=-0.1  # Invalid
        )


# ============================================================================
# TESTS: State Properties
# ============================================================================

def test_work_state_properties(client):
    """Test state property checks."""
    # DRAFT
    work_draft = Work(
        work_id=uuid4(),
        identification_number_client=client.identification_number,
        work_name="Test",
        description="Test",
        state=DraftState()
    )
    assert work_draft.is_draft
    assert not work_draft.is_quoted
    assert not work_draft.is_in_progress
    assert not work_draft.is_delivered
    
    # QUOTED
    work_quoted = Work(
        work_id=uuid4(),
        identification_number_client=client.identification_number,
        work_name="Test",
        description="Test",
        state=QuotedState()
    )
    assert not work_quoted.is_draft
    assert work_quoted.is_quoted
    
    # IN_PROGRESS
    work_in_progress = Work(
        work_id=uuid4(),
        identification_number_client=client.identification_number,
        work_name="Test",
        description="Test",
        state=InProgressState()
    )
    assert work_in_progress.is_in_progress
    
    # DELIVERED
    work_delivered = Work(
        work_id=uuid4(),
        identification_number_client=client.identification_number,
        work_name="Test",
        description="Test",
        state=DeliveredState()
    )
    assert work_delivered.is_delivered


# ============================================================================
# TESTS: Product Management
# ============================================================================

def test_add_product_to_draft_work(draft_work, simple_product):
    """Test adding product to DRAFT work."""
    product_item = draft_work.add_product(simple_product, quantity=2)
    
    assert len(draft_work.products) == 1
    assert product_item.product_id == simple_product.id
    assert product_item.quantity == 2
    assert product_item.execution_order == 0
    assert not product_item.has_snapshot()  # No snapshot in DRAFT


def test_add_product_with_custom_order(draft_work, simple_product):
    """Test adding product with custom execution order."""
    product_item = draft_work.add_product(simple_product, quantity=1, execution_order=5)
    
    assert product_item.execution_order == 5


def test_add_multiple_products(draft_work, simple_product, composite_product):
    """Test adding multiple products."""
    draft_work.add_product(simple_product, quantity=2)
    draft_work.add_product(composite_product, quantity=1)
    
    assert len(draft_work.products) == 2


def test_remove_product_from_draft_work(draft_work, simple_product):
    """Test removing product from DRAFT work."""
    draft_work.add_product(simple_product, quantity=1)
    assert len(draft_work.products) == 1
    
    draft_work.remove_product(simple_product.id)
    assert len(draft_work.products) == 0


def test_remove_nonexistent_product_raises_error(draft_work):
    """Test removing non-existent product raises error."""
    with pytest.raises(ValueError, match="no encontrado"):
        draft_work.remove_product(uuid4())


def test_reorder_product(draft_work, simple_product, composite_product):
    """Test reordering products."""
    draft_work.add_product(simple_product, quantity=1)  # order 0
    draft_work.add_product(composite_product, quantity=1)  # order 1
    
    draft_work.reorder_product(simple_product.id, new_order=10)
    
    # Find product
    product_item = next(p for p in draft_work.products if p.product_id == simple_product.id)
    assert product_item.execution_order == 10


# ============================================================================
# TESTS: State Transition - Quote
# ============================================================================

def test_quote_work_success(draft_work, manager, simple_product):
    """Test quoting work successfully."""
    draft_work.add_product(simple_product, quantity=2)
    
    products_registry = {simple_product.id: simple_product}
    draft_work.quote(quoted_by=manager, products_registry=products_registry)
    
    assert draft_work.is_quoted
    assert draft_work.products[0].has_snapshot()
    
    # Check events
    events = draft_work.clear_domain_events()
    assert any(isinstance(e, WorkQuoted) for e in events)


def test_quote_work_creates_snapshots(draft_work, manager, simple_product):
    """Test that quoting creates snapshots for all products."""
    draft_work.add_product(simple_product, quantity=1)
    
    products_registry = {simple_product.id: simple_product}
    draft_work.quote(quoted_by=manager, products_registry=products_registry)
    
    product_item = draft_work.products[0]
    assert product_item.has_snapshot()
    assert product_item.snapshot.product_id == simple_product.id
    assert product_item.snapshot.price == simple_product.get_total_price()


def test_quote_work_supervisor_can_quote(draft_work, supervisor, simple_product):
    """Test that SUPERVISOR can quote."""
    draft_work.add_product(simple_product, quantity=1)
    
    products_registry = {simple_product.id: simple_product}
    draft_work.quote(quoted_by=supervisor, products_registry=products_registry)
    
    assert draft_work.is_quoted


def test_quote_work_employee_can_quote(draft_work, employee, simple_product):
    """Test that EMPLOYEE can quote."""
    draft_work.add_product(simple_product, quantity=1)
    
    products_registry = {simple_product.id: simple_product}
    draft_work.quote(quoted_by=employee, products_registry=products_registry)
    
    assert draft_work.is_quoted


def test_quote_work_unauthorized_roles_cannot_quote(draft_work, client, simple_product):
    """Test that unauthorized roles cannot quote."""
    draft_work.add_product(simple_product, quantity=1)
    
    products_registry = {simple_product.id: simple_product}
    
    # CLIENT no puede cotizar
    with pytest.raises(ValueError, match="Solo EMPLOYEE, SUPERVISOR o MANAGER pueden cotizar"):
        draft_work.quote(quoted_by=client, products_registry=products_registry)


def test_quote_work_without_products_raises_error(draft_work, manager):
    """Test quoting work without products raises error."""
    with pytest.raises(ValueError, match="sin products"):
        draft_work.quote(quoted_by=manager, products_registry={})


def test_add_product_to_quoted_work_creates_snapshot_immediately(
    draft_work, manager, simple_product, composite_product
):
    """Test that adding product to QUOTED work creates snapshot immediately."""
    # Quote with first product
    draft_work.add_product(simple_product, quantity=1)
    products_registry = {simple_product.id: simple_product}
    draft_work.quote(quoted_by=manager, products_registry=products_registry)
    
    # Add second product after quoting
    products_registry[composite_product.id] = composite_product
    product_item = draft_work.add_product(composite_product, quantity=1)
    
    # Should have snapshot immediately
    assert product_item.has_snapshot()


# ============================================================================
# TESTS: State Transition - Start Work
# ============================================================================

def test_start_work_success(draft_work, manager, simple_product):
    """Test starting work successfully."""
    draft_work.add_product(simple_product, quantity=1)
    
    products_registry = {simple_product.id: simple_product}
    draft_work.quote(quoted_by=manager, products_registry=products_registry)
    
    tasks = draft_work.start_work(started_by=manager, products_registry=products_registry)
    
    assert draft_work.is_in_progress
    assert len(tasks) > 0
    assert len(draft_work.tasks) > 0
    
    # Check events
    events = draft_work.clear_domain_events()
    assert any(isinstance(e, WorkStarted) for e in events)


def test_start_work_generates_tasks_for_simple_product(draft_work, manager, simple_product):
    """Test that starting work generates tasks for simple products."""
    draft_work.add_product(simple_product, quantity=1)
    
    products_registry = {simple_product.id: simple_product}
    draft_work.quote(quoted_by=manager, products_registry=products_registry)
    tasks = draft_work.start_work(started_by=manager, products_registry=products_registry)
    
    # SimpleProduct  1 task
    assert len(tasks) == 1
    assert tasks[0].product_id == simple_product.id


def test_start_work_generates_tasks_for_composite_product(draft_work, manager, composite_product):
    """Test that starting work generates tasks for composite products."""
    draft_work.add_product(composite_product, quantity=1)
    
    products_registry = {composite_product.id: composite_product}
    draft_work.quote(quoted_by=manager, products_registry=products_registry)
    tasks = draft_work.start_work(started_by=manager, products_registry=products_registry)
    
    # CompositeProduct with 2 components  2 tasks
    assert len(tasks) == 2


def test_start_work_only_manager_can_start(draft_work, supervisor, simple_product):
    """Test that only MANAGER can start work."""
    draft_work.add_product(simple_product, quantity=1)
    
    products_registry = {simple_product.id: simple_product}
    
    # Can't start from DRAFT
    with pytest.raises(ValueError):
        draft_work.start_work(started_by=supervisor, products_registry=products_registry)


# ============================================================================
# TESTS: State Transition - Deliver
# ============================================================================

def test_deliver_work_success(draft_work, manager, simple_product, supervisor, employee):
    """Test delivering work successfully."""
    # Setup: Create, quote, start, complete all tasks
    draft_work.add_product(simple_product, quantity=1)
    
    products_registry = {simple_product.id: simple_product}
    draft_work.quote(quoted_by=manager, products_registry=products_registry)
    draft_work.start_work(started_by=manager, products_registry=products_registry)
    
    # Complete all tasks
    for task in draft_work.tasks:
        task.assign_to(user=employee, assigned_by=supervisor)
        if task.is_ready:
            task.start(started_by=employee)
            task.complete(completed_by=employee)
            task.validate(validated_by=supervisor)
    
    # Now deliver
    draft_work.deliver(delivered_by=manager)
    
    assert draft_work.is_delivered
    assert draft_work.end_delivery_date is not None
    
    # Check events
    events = draft_work.clear_domain_events()
    assert any(isinstance(e, WorkDelivered) for e in events)


def test_deliver_work_with_unfinished_tasks_raises_error(draft_work, manager, simple_product):
    """Test that delivering with unfinished tasks raises error."""
    draft_work.add_product(simple_product, quantity=1)
    
    products_registry = {simple_product.id: simple_product}
    draft_work.quote(quoted_by=manager, products_registry=products_registry)
    draft_work.start_work(started_by=manager, products_registry=products_registry)
    
    # Tasks are not finished
    with pytest.raises(ValueError, match="sin finalizar"):
        draft_work.deliver(delivered_by=manager)


def test_deliver_work_only_manager_can_deliver(draft_work, supervisor, simple_product):
    """Test that only MANAGER can deliver."""
    draft_work.add_product(simple_product, quantity=1)
    
    # Even if work is ready, supervisor can't deliver
    with pytest.raises(ValueError, match="Solo MANAGER puede entregar"):
        draft_work.deliver(delivered_by=supervisor)


# ============================================================================
# TESTS: Value Calculations
# ============================================================================

def test_products_value_calculation(draft_work, manager, simple_product):
    """Test products_value calculation with snapshots."""
    draft_work.add_product(simple_product, quantity=2)
    
    products_registry = {simple_product.id: simple_product}
    draft_work.quote(quoted_by=manager, products_registry=products_registry)
    
    # products_value = price  quantity
    expected = simple_product.get_total_price().multiply(Decimal("2"))
    assert draft_work.products_value == expected


def test_work_value_calculation_with_tax(draft_work, manager, simple_product):
    """Test work_value calculation with tax."""
    draft_work.tax = 0.15  # 15%
    draft_work.add_product(simple_product, quantity=1)
    
    products_registry = {simple_product.id: simple_product}
    draft_work.quote(quoted_by=manager, products_registry=products_registry)
    
    products_val = draft_work.products_value
    work_val = draft_work.work_value
    
    # work_value = products_value  1.15
    expected = products_val.multiply(Decimal("1.15"))
    assert work_val == expected


def test_completion_percentage_empty_tasks(draft_work):
    """Test completion percentage with no tasks."""
    assert draft_work.completion_percentage == 0.0


def test_completion_percentage_with_tasks(draft_work, manager, simple_product, supervisor, employee):
    """Test completion percentage calculation."""
    draft_work.add_product(simple_product, quantity=1)
    
    products_registry = {simple_product.id: simple_product}
    draft_work.quote(quoted_by=manager, products_registry=products_registry)
    draft_work.start_work(started_by=manager, products_registry=products_registry)
    
    # 0% initially
    assert draft_work.completion_percentage == 0.0
    
    # Complete first task
    task = draft_work.tasks[0]
    task.assign_to(user=employee, assigned_by=supervisor)
    task.start(started_by=employee)
    task.complete(completed_by=employee)
    task.validate(validated_by=supervisor)
    
    # 100% (only 1 task)
    assert draft_work.completion_percentage == 100.0


# ============================================================================
# TESTS: Task Management
# ============================================================================

def test_get_task_by_id(draft_work, manager, simple_product):
    """Test getting task by ID."""
    draft_work.add_product(simple_product, quantity=1)
    
    products_registry = {simple_product.id: simple_product}
    draft_work.quote(quoted_by=manager, products_registry=products_registry)
    draft_work.start_work(started_by=manager, products_registry=products_registry)
    
    task = draft_work.tasks[0]
    found = draft_work.get_task(task.task_id)
    
    assert found is not None
    assert found.task_id == task.task_id


def test_get_tasks_by_product(draft_work, manager, simple_product):
    """Test getting tasks by product ID."""
    draft_work.add_product(simple_product, quantity=1)
    
    products_registry = {simple_product.id: simple_product}
    draft_work.quote(quoted_by=manager, products_registry=products_registry)
    draft_work.start_work(started_by=manager, products_registry=products_registry)
    
    tasks = draft_work.get_tasks_by_product(simple_product.id)
    
    assert len(tasks) > 0
    assert all(t.product_id == simple_product.id for t in tasks)


def test_get_ready_tasks(draft_work, manager, simple_product, supervisor, employee):
    """Test getting ready tasks."""
    draft_work.add_product(simple_product, quantity=1)
    
    products_registry = {simple_product.id: simple_product}
    draft_work.quote(quoted_by=manager, products_registry=products_registry)
    draft_work.start_work(started_by=manager, products_registry=products_registry)
    
    # Assign task
    task = draft_work.tasks[0]
    task.assign_to(user=employee, assigned_by=supervisor)
    
    ready_tasks = draft_work.get_ready_tasks()
    assert len(ready_tasks) == 1


def test_unblock_next_task(draft_work, manager, composite_product, supervisor, employee):
    """Test unblocking next task in sequence."""
    draft_work.add_product(composite_product, quantity=1)
    
    products_registry = {composite_product.id: composite_product}
    draft_work.quote(quoted_by=manager, products_registry=products_registry)
    draft_work.start_work(started_by=manager, products_registry=products_registry)
    
    # Assign all tasks
    for task in draft_work.tasks:
        task.assign_to(user=employee, assigned_by=supervisor)
    
    # Complete first task
    first_task = draft_work.tasks[0]
    first_task.start(started_by=employee)
    first_task.complete(completed_by=employee)
    first_task.validate(validated_by=supervisor)
    
    # Unblock next
    next_task = draft_work.unblock_next_task(first_task)
    
    assert next_task is not None
    assert next_task.is_ready
    assert not next_task.is_blocked


def test_unblock_next_task_with_completed_state(draft_work, manager, composite_product, supervisor, employee):
    """Test unblocking next task when previous task is COMPLETED (not yet validated)."""
    draft_work.add_product(composite_product, quantity=1)
    
    products_registry = {composite_product.id: composite_product}
    draft_work.quote(quoted_by=manager, products_registry=products_registry)
    draft_work.start_work(started_by=manager, products_registry=products_registry)
    
    # Assign all tasks
    for task in draft_work.tasks:
        task.assign_to(user=employee, assigned_by=supervisor)
    
    # Complete first task but don't validate yet
    first_task = draft_work.tasks[0]
    first_task.start(started_by=employee)
    first_task.complete(completed_by=employee)
    
    # Task should be in COMPLETED state (pending validation)
    assert first_task.is_completed
    assert not first_task.is_finished
    
    # Unblock next task even though first task is not validated yet
    next_task = draft_work.unblock_next_task(first_task)
    
    # Next task should be unblocked
    assert next_task is not None
    assert next_task.is_ready
    assert not next_task.is_blocked


# ============================================================================
# TESTS: Domain Events
# ============================================================================

def test_work_generates_domain_events(draft_work, manager, simple_product):
    """Test that work generates appropriate domain events."""
    # Add product  ProductAddedToWork
    draft_work.add_product(simple_product, quantity=1)
    events = draft_work.clear_domain_events()
    assert any(isinstance(e, ProductAddedToWork) for e in events)
    
    # Quote  WorkQuoted
    products_registry = {simple_product.id: simple_product}
    draft_work.quote(quoted_by=manager, products_registry=products_registry)
    events = draft_work.clear_domain_events()
    assert any(isinstance(e, WorkQuoted) for e in events)
    
    # Start  WorkStarted
    draft_work.start_work(started_by=manager, products_registry=products_registry)
    events = draft_work.clear_domain_events()
    assert any(isinstance(e, WorkStarted) for e in events)


# ============================================================================
# TESTS: Edge Cases
# ============================================================================

def test_cannot_add_products_to_in_progress_work(draft_work, manager, simple_product):
    """Test that products cannot be added to IN_PROGRESS work."""
    draft_work.add_product(simple_product, quantity=1)
    
    products_registry = {simple_product.id: simple_product}
    draft_work.quote(quoted_by=manager, products_registry=products_registry)
    draft_work.start_work(started_by=manager, products_registry=products_registry)
    
    # Try to add another product
    new_product = SimpleProduct(
        id=uuid4(),
        name="New product",
        material=simple_product.material,
        dimensions={"width": 1, "height": 1}
    )
    
    with pytest.raises(ValueError, match="No se pueden agregar products"):
        draft_work.add_product(new_product, quantity=1)


def test_work_value_calculation_in_draft_state(draft_work, simple_product):
    """Test work_value calculation in DRAFT state (without snapshots)."""
    draft_work.tax = 0.10  # 10%
    draft_work.add_product(simple_product, quantity=1)
    
    products_registry = {simple_product.id: simple_product}
    
    # Calculate work_value in DRAFT (usando el metodo privado con parametro)
    work_val = draft_work._calculate_work_value(products_registry)
    
    # Expected value = product_price * 1.10
    expected_price = simple_product.get_total_price().multiply(Decimal("1.10"))
    
    assert work_val == expected_price


def test_cannot_remove_products_from_in_progress_work(draft_work, manager, simple_product):
    """Test that products cannot be removed from IN_PROGRESS work."""
    draft_work.add_product(simple_product, quantity=1)
    
    products_registry = {simple_product.id: simple_product}
    draft_work.quote(quoted_by=manager, products_registry=products_registry)
    draft_work.start_work(started_by=manager, products_registry=products_registry)
    
    with pytest.raises(ValueError, match="No se pueden delete products"):
        draft_work.remove_product(simple_product.id)

