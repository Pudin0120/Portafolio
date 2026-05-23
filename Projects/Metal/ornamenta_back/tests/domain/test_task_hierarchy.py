"""
Tests for Task Hierarchy Validator.

Tests that validate the hierarchical constraints of tasks generated from composite products.
"""
import pytest
from uuid import uuid4
from decimal import Decimal

from app.domain.models.task import Task
from app.domain.models.product import CompositeProduct, SimpleProduct
from app.domain.models.material import Material
from app.domain.models.material_type import MaterialType
from app.domain.factories.task_factory import TaskFactory
from app.domain.validators.task_hierarchy_validator import (
    TaskHierarchyValidator,
    CompositeTaskBoundary
)
from app.domain.value_objects.money import Money
from app.domain.value_objects.state_task import StateTask, StateTaskEnum


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def simple_product_marco():
    """Simple product: Marco de acero."""
    material_type = MaterialType(
        id=uuid4(),
        name="Tubo",
        description="Material tipo tubo",
        measurement_strategy="TUBE"
    )
    material = Material(
        id=uuid4(),
        material_type=material_type,
        description="Marco de acero",
        price=Money(amount=Decimal("50000"))
    )
    
    return SimpleProduct(
        id=uuid4(),
        name="Marco de Acero",
        description="Marco para puerta metalica",
        material=material,
        dimensions={"width": 2.0, "height": 0.8},
        quantity_multiplier=Decimal("1.0")
    )


@pytest.fixture
def simple_product_lamina():
    """Simple product: Lamina de acero."""
    material_type = MaterialType(
        id=uuid4(),
        name="Lamina",
        description="Material tipo lamina",
        measurement_strategy="SHEET"
    )
    material = Material(
        id=uuid4(),
        material_type=material_type,
        description="Lamina de acero",
        price=Money(amount=Decimal("80000"))
    )
    
    return SimpleProduct(
        id=uuid4(),
        name="Lamina de Acero",
        description="Lamina para puerta",
        material=material,
        dimensions={"width": 2.0, "height": 0.8},
        quantity_multiplier=Decimal("1.0")
    )


@pytest.fixture
def simple_product_bisagras():
    """Simple product: Bisagras."""
    material_type = MaterialType(
        id=uuid4(),
        name="Bisagra",
        description="Material tipo bisagra",
        measurement_strategy="UNIT"
    )
    material = Material(
        id=uuid4(),
        material_type=material_type,
        description="Bisagras para puerta",
        price=Money(amount=Decimal("25000"))
    )
    
    return SimpleProduct(
        id=uuid4(),
        name="Bisagras",
        description="Bisagras para puerta",
        material=material,
        dimensions={},
        quantity_multiplier=Decimal("1.0")
    )


@pytest.fixture
def composite_product_puerta(simple_product_marco, simple_product_lamina, simple_product_bisagras):
    """Composite product: Puerta Metalica."""
    puerta = CompositeProduct(
        id=uuid4(),
        name="Puerta Metalica",
        description="Puerta completa con marco, lamina y bisagras"
    )
    
    puerta.add_component(simple_product_marco, quantity=1)
    puerta.add_component(simple_product_lamina, quantity=1)
    puerta.add_component(simple_product_bisagras, quantity=2)
    
    return puerta


@pytest.fixture
def work_id():
    """Work ID for tests."""
    return uuid4()


# ============================================================================
# TESTS: TaskFactory with Hierarchy
# ============================================================================

def test_create_tasks_from_simple_product_no_hierarchy(simple_product_marco, work_id):
    """
    Test: Simple product generates task WITHOUT hierarchy info.
    """
    # Act
    tasks, next_order = TaskFactory.create_tasks_from_product(
        product=simple_product_marco,
        work_id=work_id,
        product_quantity=1,
        base_order=0
    )
    
    # Assert
    assert len(tasks) == 1
    task = tasks[0]
    
    # No hierarchy (standalone task)
    assert task.parent_composite_id is None
    assert task.composite_task_slot is None
    assert task.composite_total_slots is None
    
    # Basic fields
    assert task.work_id == work_id
    assert task.product_id == simple_product_marco.id
    assert task.execution_order == 0
    assert next_order == 1


def test_create_tasks_from_composite_product_with_hierarchy(composite_product_puerta, work_id):
    """
    Test: Composite product generates tasks WITH hierarchy info.
    """
    # Act
    tasks, next_order = TaskFactory.create_tasks_from_product(
        product=composite_product_puerta,
        work_id=work_id,
        product_quantity=1,
        base_order=0
    )
    
    # Assert
    assert len(tasks) == 3  # Marco, Lamina, Bisagras
    
    # Task 0: Marco (slot 0/3)
    assert tasks[0].parent_composite_id == composite_product_puerta.id
    assert tasks[0].composite_task_slot == 0
    assert tasks[0].composite_total_slots == 3
    assert tasks[0].execution_order == 0
    
    # Task 1: Lamina (slot 1/3)
    assert tasks[1].parent_composite_id == composite_product_puerta.id
    assert tasks[1].composite_task_slot == 1
    assert tasks[1].composite_total_slots == 3
    assert tasks[1].execution_order == 1
    
    # Task 2: Bisagras (slot 2/3)
    assert tasks[2].parent_composite_id == composite_product_puerta.id
    assert tasks[2].composite_task_slot == 2
    assert tasks[2].composite_total_slots == 3
    assert tasks[2].execution_order == 2
    
    assert next_order == 3


# ============================================================================
# TESTS: TaskHierarchyValidator
# ============================================================================

def test_build_composite_boundaries(composite_product_puerta, work_id):
    """
    Test: Build boundaries for composite products.
    """
    # Arrange
    tasks, _ = TaskFactory.create_tasks_from_product(
        composite_product_puerta, work_id, product_quantity=1, base_order=0
    )
    
    # Act
    boundaries = TaskHierarchyValidator.build_composite_boundaries(tasks)
    
    # Assert
    assert len(boundaries) == 1
    boundary = boundaries[composite_product_puerta.id]
    
    assert boundary.composite_id == composite_product_puerta.id
    assert boundary.start_execution_order == 0
    assert boundary.end_execution_order == 2
    assert boundary.total_task_slots == 3


def test_validate_reorder_standalone_task_success(simple_product_marco, work_id):
    """
    Test: Standalone task can be reordered to any position.
    """
    # Arrange
    tasks, _ = TaskFactory.create_tasks_from_product(
        simple_product_marco, work_id, product_quantity=1, base_order=0
    )
    task = tasks[0]
    all_tasks = tasks + [
        Task(
            task_id=uuid4(),
            work_id=work_id,
            product_id=uuid4(),
            task_name="Other",
            description="Other task",
            state=StateTask(value=StateTaskEnum.PENDING),
            labor=Money(amount=Decimal("10000")),
            estimated_value=Money(amount=Decimal("10000")),
            execution_order=1
        )
    ]
    
    # Act
    is_valid, error = TaskHierarchyValidator.validate_task_reorder(
        task, new_execution_order=1, all_tasks=all_tasks
    )
    
    # Assert
    assert is_valid is True
    assert error == ""


def test_validate_reorder_composite_task_within_range_success(composite_product_puerta, work_id):
    """
    Test: Composite task can stay within its composite range.
    """
    # Arrange
    tasks, _ = TaskFactory.create_tasks_from_product(
        composite_product_puerta, work_id, product_quantity=1, base_order=0
    )
    task = tasks[1]  # Lamina (slot 1, order 1)
    
    # Act - Try to keep it at order 1 (its current position)
    is_valid, error = TaskHierarchyValidator.validate_task_reorder(
        task, new_execution_order=1, all_tasks=tasks
    )
    
    # Assert
    assert is_valid is True
    assert error == ""


def test_validate_reorder_composite_task_outside_range_failure(composite_product_puerta, work_id):
    """
    Test: Composite task CANNOT move outside its composite range.
    """
    # Arrange
    tasks, _ = TaskFactory.create_tasks_from_product(
        composite_product_puerta, work_id, product_quantity=1, base_order=5  # Start at 5
    )
    task = tasks[1]  # Lamina (slot 1, order 6, range [5, 7])
    
    # Act - Try to move to order 3 (outside range)
    is_valid, error = TaskHierarchyValidator.validate_task_reorder(
        task, new_execution_order=3, all_tasks=tasks
    )
    
    # Assert
    assert is_valid is False
    assert "fuera del rango del compuesto" in error
    assert "[5, 7]" in error


def test_validate_reorder_composite_task_wrong_slot_failure(composite_product_puerta, work_id):
    """
    Test: Composite task CANNOT change its relative slot position.
    """
    # Arrange
    tasks, _ = TaskFactory.create_tasks_from_product(
        composite_product_puerta, work_id, product_quantity=1, base_order=0
    )
    task = tasks[1]  # Lamina (slot 1, order 1, range [0, 2])
    
    # Act - Try to move to order 0 (would change slot from 1 to 0)
    is_valid, error = TaskHierarchyValidator.validate_task_reorder(
        task, new_execution_order=0, all_tasks=tasks
    )
    
    # Assert
    assert is_valid is False
    assert "orden interno" in error or "orden relativo" in error


def test_get_valid_execution_orders_standalone(simple_product_marco, work_id):
    """
    Test: Standalone task has all positions as valid.
    """
    # Arrange
    tasks, _ = TaskFactory.create_tasks_from_product(
        simple_product_marco, work_id, product_quantity=1, base_order=0
    )
    task = tasks[0]
    
    # Create a work with 5 total tasks
    all_tasks = tasks + [
        Task(
            task_id=uuid4(),
            work_id=work_id,
            product_id=uuid4(),
            task_name=f"Task {i}",
            description="",
            state=StateTask(value=StateTaskEnum.PENDING),
            labor=Money(amount=Decimal("10000")),
            estimated_value=Money(amount=Decimal("10000")),
            execution_order=i
        )
        for i in range(1, 5)
    ]
    
    # Act
    valid_orders = TaskHierarchyValidator.get_valid_execution_orders(task, all_tasks)
    
    # Assert
    assert len(valid_orders) == 5  # Can go to any of 5 positions
    assert valid_orders == [0, 1, 2, 3, 4]


def test_get_valid_execution_orders_composite(composite_product_puerta, work_id):
    """
    Test: Composite task has only its slot position as valid.
    """
    # Arrange
    tasks, _ = TaskFactory.create_tasks_from_product(
        composite_product_puerta, work_id, product_quantity=1, base_order=2  # Start at 2
    )
    task = tasks[1]  # Lamina (slot 1, order 3)
    
    # Act
    valid_orders = TaskHierarchyValidator.get_valid_execution_orders(task, tasks)
    
    # Assert
    assert len(valid_orders) == 1
    assert valid_orders == [3]  # Only can be at order 3 (its current position)


def test_get_composite_tasks(composite_product_puerta, work_id):
    """
    Test: Get all tasks belonging to a composite product.
    """
    # Arrange
    tasks, _ = TaskFactory.create_tasks_from_product(
        composite_product_puerta, work_id, product_quantity=1, base_order=0
    )
    
    # Add a standalone task
    standalone = Task(
        task_id=uuid4(),
        work_id=work_id,
        product_id=uuid4(),
        task_name="Standalone",
        description="",
        state=StateTask(value=StateTaskEnum.PENDING),
        labor=Money(amount=Decimal("10000")),
        estimated_value=Money(amount=Decimal("10000")),
        execution_order=3
    )
    all_tasks = tasks + [standalone]
    
    # Act
    composite_tasks = TaskHierarchyValidator.get_composite_tasks(
        composite_product_puerta.id, all_tasks
    )
    
    # Assert
    assert len(composite_tasks) == 3  # Only composite tasks, not standalone
    assert all(t.parent_composite_id == composite_product_puerta.id for t in composite_tasks)
    assert composite_tasks[0].execution_order == 0
    assert composite_tasks[1].execution_order == 1
    assert composite_tasks[2].execution_order == 2


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_mixed_tasks_hierarchy(
    simple_product_marco,
    composite_product_puerta,
    work_id
):
    """
    Test: Work with mix of standalone and composite tasks.
    
    Structure:
      0. Standalone task (Marco)
      1-3. Composite tasks (Puerta: Marco, Lamina, Bisagras)
      4. Standalone task (Acabado)
    """
    # Arrange - Create standalone task
    standalone1, next_order = TaskFactory.create_tasks_from_product(
        simple_product_marco, work_id, product_quantity=1, base_order=0
    )
    
    # Create composite tasks
    composite_tasks, next_order = TaskFactory.create_tasks_from_product(
        composite_product_puerta, work_id, product_quantity=1, base_order=next_order
    )
    
    # Create another standalone
    standalone2, _ = TaskFactory.create_tasks_from_product(
        simple_product_marco, work_id, product_quantity=1, base_order=next_order
    )
    
    all_tasks = standalone1 + composite_tasks + standalone2
    
    # Assert structure
    assert len(all_tasks) == 5
    
    # Task 0: Standalone
    assert all_tasks[0].parent_composite_id is None
    assert all_tasks[0].execution_order == 0
    
    # Tasks 1-3: Composite
    assert all_tasks[1].parent_composite_id == composite_product_puerta.id
    assert all_tasks[1].composite_task_slot == 0
    assert all_tasks[1].execution_order == 1
    
    assert all_tasks[2].parent_composite_id == composite_product_puerta.id
    assert all_tasks[2].composite_task_slot == 1
    assert all_tasks[2].execution_order == 2
    
    assert all_tasks[3].parent_composite_id == composite_product_puerta.id
    assert all_tasks[3].composite_task_slot == 2
    assert all_tasks[3].execution_order == 3
    
    # Task 4: Standalone
    assert all_tasks[4].parent_composite_id is None
    assert all_tasks[4].execution_order == 4
    
    # Test: Can reorder first standalone to position 4
    is_valid, _ = TaskHierarchyValidator.validate_task_reorder(
        all_tasks[0], new_execution_order=4, all_tasks=all_tasks
    )
    assert is_valid is True
    
    # Test: Cannot move composite task outside range [1, 3]
    is_valid, error = TaskHierarchyValidator.validate_task_reorder(
        all_tasks[2], new_execution_order=0, all_tasks=all_tasks
    )
    assert is_valid is False
    assert "fuera del rango" in error


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
