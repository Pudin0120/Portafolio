"""
Unit tests for TaskFactory (Factory Pattern).

Tests cover:
- Task generation from SimpleProduct
- Task generation from CompositeProduct (recursively)
- Task generation from nested CompositeProducts
- Sequential task blocking within CompositeProduct
- Parallel execution between different products
- Task ordering and execution_order assignment
"""
import pytest
from decimal import Decimal
from uuid import uuid4

from app.domain.factories.task_factory import TaskFactory
from app.domain.models.product import SimpleProduct, CompositeProduct
from app.domain.models.material import Material
from app.domain.models.material_type import MaterialType
from app.domain.models.unit_of_measure import UnitOfMeasure
from app.domain.strategies.sheet_measurement_strategy import SheetMeasurementStrategy
from app.domain.value_objects.money import Money
from app.domain.value_objects.state_task import StateTaskEnum


# ============================================================================
# FIXTURES
# ============================================================================

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
        measurement_strategy="SHEET"
    )


@pytest.fixture
def steel_material(steel_material_type, square_meter_unit):
    """Steel material fixture."""
    return Material(
        id=uuid4(),
        sku="TEST-SKU-1",
        description="Acero galvanizado",
        material_type=steel_material_type,
        purchase_price=Money(amount=Decimal("30000")),
        properties={
            "gauge": "20",
            "thickness_mm": 0.85,
            "area": 4.0
        }
    )


@pytest.fixture
def simple_product(steel_material):
    """Simple product: Chapa."""
    return SimpleProduct(
        id=uuid4(),
        name="Chapa Yale",
        description="Chapa para puerta",
        material=steel_material,
        dimensions={"width": 0.1, "height": 0.2},
        quantity_multiplier=Decimal("0.5")
    )


@pytest.fixture
def another_simple_product(steel_material):
    """Another simple product: Marco."""
    return SimpleProduct(
        id=uuid4(),
        name="Marco de ventana",
        description="Marco de aluminio",
        material=steel_material,
        dimensions={"width": 1.0, "height": 2.0},
        quantity_multiplier=Decimal("2.0")
    )


@pytest.fixture
def composite_product(simple_product, another_simple_product):
    """Composite product: Ventana."""
    composite = CompositeProduct(
        id=uuid4(),
        name="Ventana Completa"
    )
    
    composite.add_component(another_simple_product, quantity=1)  # Marco
    composite.add_component(simple_product, quantity=1)  # Chapa
    
    return composite


@pytest.fixture
def nested_composite_product(composite_product, simple_product):
    """Nested composite: Puerta-Ventana."""
    nested = CompositeProduct(
        id=uuid4(),
        name="Puerta-Ventana"
    )
    
    # Agregar un composite (ventana) y un simple (chapa adicional)
    nested.add_component(composite_product, quantity=1)
    nested.add_component(simple_product, quantity=1)
    
    return nested


# ============================================================================
# TESTS: Task Generation from SimpleProduct
# ============================================================================

def test_create_task_from_simple_product(simple_product):
    """Test creating task from a simple product."""
    work_id = uuid4()
    tasks, next_order = TaskFactory.create_tasks_from_product(
        product=simple_product,
        work_id=work_id,
        product_quantity=1,
        base_order=0,
        tax=0.6
    )
    
    # SimpleProduct  1 task
    assert len(tasks) == 1
    assert tasks[0].product_id == simple_product.id
    assert tasks[0].work_id == work_id
    assert tasks[0].execution_order == 0
    assert not tasks[0].is_blocked
    assert tasks[0].previous_task_id is None
    assert next_order == 1


def test_create_task_from_simple_product_with_quantity(simple_product):
    """Test creating task with quantity > 1."""
    work_id = uuid4()
    tasks, next_order = TaskFactory.create_tasks_from_product(
        product=simple_product,
        work_id=work_id,
        product_quantity=3,
        base_order=0
    )
    
    # Still 1 task, but description includes quantity
    assert len(tasks) == 1
    assert "x3" in tasks[0].task_name


def test_create_task_with_custom_base_order(simple_product):
    """Test creating task with custom base order."""
    work_id = uuid4()
    tasks, next_order = TaskFactory.create_tasks_from_product(
        product=simple_product,
        work_id=work_id,
        product_quantity=1,
        base_order=10
    )
    
    assert tasks[0].execution_order == 10
    assert next_order == 11


# ============================================================================
# TESTS: Task Generation from CompositeProduct
# ============================================================================

def test_create_tasks_from_composite_product(composite_product):
    """Test creating tasks from composite product."""
    work_id = uuid4()
    tasks, next_order = TaskFactory.create_tasks_from_product(
        product=composite_product,
        work_id=work_id,
        product_quantity=1,
        base_order=0
    )
    
    # Composite with 2 components  2 tasks
    assert len(tasks) == 2
    assert tasks[0].execution_order == 0
    assert tasks[1].execution_order == 1


def test_tasks_from_composite_are_sequential(composite_product):
    """Test that tasks from composite are sequential (blocked)."""
    work_id = uuid4()
    tasks, next_order = TaskFactory.create_tasks_from_product(
        product=composite_product,
        work_id=work_id,
        product_quantity=1,
        base_order=0
    )
    
    # First task: not blocked
    assert not tasks[0].is_blocked
    assert tasks[0].previous_task_id is None
    
    # Second task: blocked by first
    assert tasks[1].is_blocked
    assert tasks[1].previous_task_id == tasks[0].task_id


def test_tasks_from_composite_with_quantity(composite_product):
    """Test creating tasks from composite with quantity > 1."""
    work_id = uuid4()
    tasks, next_order = TaskFactory.create_tasks_from_product(
        product=composite_product,
        work_id=work_id,
        product_quantity=2,
        base_order=0
    )
    
    # Still 2 tasks (one per component), but quantities are multiplied
    assert len(tasks) == 2


# ============================================================================
# TESTS: Task Generation from Nested CompositeProduct
# ============================================================================

def test_create_tasks_from_nested_composite(nested_composite_product):
    """Test creating tasks from nested composite product."""
    work_id = uuid4()
    tasks, next_order = TaskFactory.create_tasks_from_product(
        product=nested_composite_product,
        work_id=work_id,
        product_quantity=1,
        base_order=0
    )
    
    # Nested composite:
    # - Ventana (composite with 2 components)  2 tasks
    # - Chapa (simple)  1 task
    # Total: 3 tasks
    assert len(tasks) == 3


def test_nested_composite_tasks_are_sequential(nested_composite_product):
    """Test that nested composite tasks maintain sequential order."""
    work_id = uuid4()
    tasks, next_order = TaskFactory.create_tasks_from_product(
        product=nested_composite_product,
        work_id=work_id,
        product_quantity=1,
        base_order=0
    )
    
    # Task 0: not blocked
    assert not tasks[0].is_blocked
    
    # Task 1: blocked by task 0
    assert tasks[1].is_blocked
    assert tasks[1].previous_task_id == tasks[0].task_id
    
    # Task 2: blocked by task 1
    assert tasks[2].is_blocked
    assert tasks[2].previous_task_id == tasks[1].task_id


def test_nested_composite_execution_order(nested_composite_product):
    """Test execution order in nested composite."""
    work_id = uuid4()
    tasks, next_order = TaskFactory.create_tasks_from_product(
        product=nested_composite_product,
        work_id=work_id,
        product_quantity=1,
        base_order=5
    )
    
    assert tasks[0].execution_order == 5
    assert tasks[1].execution_order == 6
    assert tasks[2].execution_order == 7
    assert next_order == 8


# ============================================================================
# TESTS: Multiple Products (Parallel Execution)
# ============================================================================

def test_multiple_products_can_execute_in_parallel(simple_product, composite_product):
    """Test that tasks from different products can execute in parallel."""
    work_id = uuid4()
    
    # Generate tasks for first product
    tasks1, next_order = TaskFactory.create_tasks_from_product(
        product=simple_product,
        work_id=work_id,
        product_quantity=1,
        base_order=0
    )
    
    # Generate tasks for second product
    tasks2, next_order = TaskFactory.create_tasks_from_product(
        product=composite_product,
        work_id=work_id,
        product_quantity=1,
        base_order=next_order
    )
    
    # Tasks from different products are not blocked by each other
    # First task of product 1: not blocked
    assert not tasks1[0].is_blocked
    
    # First task of product 2: not blocked (parallel execution)
    assert not tasks2[0].is_blocked
    
    # But second task of product 2 is blocked by first task of product 2
    assert tasks2[1].is_blocked
    assert tasks2[1].previous_task_id == tasks2[0].task_id


# ============================================================================
# TESTS: Task Properties
# ============================================================================

def test_generated_task_has_correct_properties(simple_product):
    """Test that generated task has all required properties."""
    work_id = uuid4()
    tasks, _ = TaskFactory.create_tasks_from_product(
        product=simple_product,
        work_id=work_id,
        product_quantity=1,
        base_order=0
    )
    
    task = tasks[0]
    
    assert task.task_id is not None
    assert task.work_id == work_id
    assert task.product_id == simple_product.id
    assert task.task_name is not None
    assert task.description is not None
    assert task.state.value == StateTaskEnum.PENDING
    assert task.labor is not None
    assert task.estimated_value is not None
    assert task.execution_order == 0
    assert task.assigned_user_id is None


def test_generated_task_has_pending_state(simple_product):
    """Test that generated tasks start in PENDING state."""
    work_id = uuid4()
    tasks, _ = TaskFactory.create_tasks_from_product(
        product=simple_product,
        work_id=work_id,
        product_quantity=1,
        base_order=0
    )
    
    assert all(t.state.is_pending for t in tasks)


# ============================================================================
# TESTS: Calculate Total Tasks
# ============================================================================

def test_calculate_total_tasks_for_simple_product(simple_product):
    """Test calculating total tasks for simple product."""
    total = TaskFactory.calculate_total_tasks(simple_product, quantity=1)
    assert total == 1
    
    total = TaskFactory.calculate_total_tasks(simple_product, quantity=5)
    assert total == 1  # Quantity doesn't affect count (just task description)


def test_calculate_total_tasks_for_composite_product(composite_product):
    """Test calculating total tasks for composite product."""
    total = TaskFactory.calculate_total_tasks(composite_product, quantity=1)
    # Composite with 2 components  2 tasks
    assert total == 2


def test_calculate_total_tasks_for_nested_composite(nested_composite_product):
    """Test calculating total tasks for nested composite."""
    total = TaskFactory.calculate_total_tasks(nested_composite_product, quantity=1)
    # Nested: 2 (from inner composite) + 1 (simple) = 3
    assert total == 3


# ============================================================================
# TESTS: Edge Cases
# ============================================================================

def test_empty_composite_product():
    """Test generating tasks from empty composite product."""
    empty_composite = CompositeProduct(
        id=uuid4(),
        name="Empty Composite"
    )
    
    work_id = uuid4()
    tasks, next_order = TaskFactory.create_tasks_from_product(
        product=empty_composite,
        work_id=work_id,
        product_quantity=1,
        base_order=0
    )
    
    # Empty composite  no tasks
    assert len(tasks) == 0
    assert next_order == 0


def test_deeply_nested_composite():
    """Test generating tasks from deeply nested composite."""
    # Create a 3-level nested structure
    level1 = SimpleProduct(
        id=uuid4(),
        name="Level 1",
        purchase_price=Money(amount=Decimal("100")),
        sale_price=Money(amount=Decimal("150"))
    )
    
    level2 = CompositeProduct(id=uuid4(), name="Level 2")
    level2.add_component(level1, quantity=1)
    
    level3 = CompositeProduct(id=uuid4(), name="Level 3")
    level3.add_component(level2, quantity=1)
    
    work_id = uuid4()
    tasks, next_order = TaskFactory.create_tasks_from_product(
        product=level3,
        work_id=work_id,
        product_quantity=1,
        base_order=0
    )
    
    # Should recursively generate tasks
    assert len(tasks) == 1  # Only 1 SimpleProduct at the bottom


def test_task_factory_preserves_product_relationships(composite_product):
    """Test that task factory preserves product relationships."""
    work_id = uuid4()
    tasks, _ = TaskFactory.create_tasks_from_product(
        product=composite_product,
        work_id=work_id,
        product_quantity=1,
        base_order=0
    )
    
    # All tasks should belong to components of the composite
    component_ids = [c.component.id for c in composite_product.get_components()]
    
    for task in tasks:
        assert task.product_id in component_ids

