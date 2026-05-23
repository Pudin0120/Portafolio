"""
Unit tests for TaskCompletionStrategy (Strategy Pattern).

Tests cover:
- EmployeeTaskCompletionStrategy (requires validation)
- SupervisorTaskCompletionStrategy (auto-validated)
- ManagerTaskCompletionStrategy (auto-validated)
- Strategy factory
- Validation permissions by role
"""
import pytest
from decimal import Decimal
from uuid import uuid4

from app.domain.strategies.task_completion_strategy import (
    TaskCompletionStrategy,
    EmployeeTaskCompletionStrategy,
    SupervisorTaskCompletionStrategy,
    ManagerTaskCompletionStrategy,
    TaskCompletionStrategyFactory
)
from app.domain.models.task import Task
from app.domain.models.user import User, RoleEnum
from app.domain.value_objects import DocumentNumber, Email, Money
from app.domain.value_objects.state_task import StateTask, StateTaskEnum
from app.domain.value_objects.state_user import StateUser, StateEnum as StateUserEnum


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def manager():
    """Manager user fixture."""
    return User(
        identification_number=DocumentNumber(value="12345"),
        role=RoleEnum.MANAGER,
        first_name="Carlos",
        last_name="Gerente",
        email=Email(value="manager@empresa.com"),
        state=StateUser(value=StateUserEnum.ACTIVE),
        firebase_uid="uid_manager"
    )


@pytest.fixture
def supervisor():
    """Supervisor user fixture."""
    return User(
        identification_number=DocumentNumber(value="67890"),
        role=RoleEnum.SUPERVISOR,
        first_name="Ana",
        last_name="Supervisora",
        email=Email(value="supervisor@empresa.com"),
        state=StateUser(value=StateUserEnum.ACTIVE),
        firebase_uid="uid_supervisor"
    )


@pytest.fixture
def employee():
    """Employee user fixture."""
    return User(
        identification_number=DocumentNumber(value="11111"),
        role=RoleEnum.EMPLOYEE,
        first_name="Juan",
        last_name="Empleado",
        email=Email(value="employee@empresa.com"),
        state=StateUser(value=StateUserEnum.ACTIVE),
        firebase_uid="uid_employee"
    )


@pytest.fixture
def task_in_progress():
    """Task in IN_PROGRESS state."""
    return Task(
        task_id=uuid4(),
        work_id=uuid4(),
        product_id=uuid4(),
        task_name="Test Task",
        description="Test description",
        state=StateTask(value=StateTaskEnum.IN_PROGRESS),
        labor=Money(amount=Decimal("50000")),
        estimated_value=Money(amount=Decimal("50000")),
        execution_order=0,
        assigned_user_id="11111"
    )


@pytest.fixture
def task_completed():
    """Task in COMPLETED state."""
    return Task(
        task_id=uuid4(),
        work_id=uuid4(),
        product_id=uuid4(),
        task_name="Test Task",
        description="Test description",
        state=StateTask(value=StateTaskEnum.COMPLETED),
        labor=Money(amount=Decimal("50000")),
        estimated_value=Money(amount=Decimal("50000")),
        execution_order=0,
        assigned_user_id="11111",
        completed_by_user_id="11111"
    )


# ============================================================================
# TESTS: EmployeeTaskCompletionStrategy
# ============================================================================

def test_employee_strategy_requires_validation():
    """Test that employee strategy requires validation."""
    strategy = EmployeeTaskCompletionStrategy()
    
    assert strategy.requires_validation()
    assert not strategy.can_validate_tasks()


def test_employee_completes_task_to_completed_state(task_in_progress, employee):
    """Test that employee completes task to COMPLETED (not FINISHED)."""
    strategy = EmployeeTaskCompletionStrategy()
    
    new_state = strategy.complete_task(task_in_progress, employee)
    
    assert new_state.is_completed()
    assert not new_state.is_finished()


def test_employee_cannot_complete_non_in_progress_task(employee):
    """Test that employee cannot complete task not in IN_PROGRESS."""
    strategy = EmployeeTaskCompletionStrategy()
    
    task = Task(
        task_id=uuid4(),
        work_id=uuid4(),
        product_id=uuid4(),
        task_name="Test",
        description="Test",
        state=StateTask(value=StateTaskEnum.READY),  # Not IN_PROGRESS
        labor=Money(amount=Decimal("50000")),
        estimated_value=Money(amount=Decimal("50000")),
        execution_order=0
    )
    
    with pytest.raises(ValueError, match="IN_PROGRESS"):
        strategy.complete_task(task, employee)


def test_employee_strategy_with_wrong_role_raises_error(task_in_progress, supervisor):
    """Test that employee strategy validates role."""
    strategy = EmployeeTaskCompletionStrategy()
    
    with pytest.raises(ValueError, match="solo es valid para EMPLOYEE"):
        strategy.complete_task(task_in_progress, supervisor)


def test_employee_cannot_validate_tasks(task_completed, employee):
    """Test that employee cannot validate tasks."""
    strategy = EmployeeTaskCompletionStrategy()
    
    with pytest.raises(ValueError, match="no puede validar"):
        strategy.validate_task(task_completed, employee)


# ============================================================================
# TESTS: SupervisorTaskCompletionStrategy
# ============================================================================

def test_supervisor_strategy_does_not_require_validation():
    """Test that supervisor strategy does not require validation."""
    strategy = SupervisorTaskCompletionStrategy()
    
    assert not strategy.requires_validation()
    assert strategy.can_validate_tasks()


def test_supervisor_completes_task_to_finished_state(task_in_progress, supervisor):
    """Test that supervisor completes task directly to FINISHED (auto-validated)."""
    strategy = SupervisorTaskCompletionStrategy()
    
    new_state = strategy.complete_task(task_in_progress, supervisor)
    
    assert new_state.is_finished()


def test_supervisor_can_validate_tasks(task_completed, supervisor):
    """Test that supervisor can validate tasks."""
    strategy = SupervisorTaskCompletionStrategy()
    
    new_state = strategy.validate_task(task_completed, supervisor)
    
    assert new_state.is_finished()


def test_supervisor_cannot_validate_non_completed_task(task_in_progress, supervisor):
    """Test that supervisor cannot validate task not in COMPLETED."""
    strategy = SupervisorTaskCompletionStrategy()
    
    with pytest.raises(ValueError, match="COMPLETED"):
        strategy.validate_task(task_in_progress, supervisor)


# ============================================================================
# TESTS: ManagerTaskCompletionStrategy
# ============================================================================

def test_manager_strategy_does_not_require_validation():
    """Test that manager strategy does not require validation."""
    strategy = ManagerTaskCompletionStrategy()
    
    assert not strategy.requires_validation()
    assert strategy.can_validate_tasks()


def test_manager_completes_task_to_finished_state(task_in_progress, manager):
    """Test that manager completes task directly to FINISHED (auto-validated)."""
    strategy = ManagerTaskCompletionStrategy()
    
    new_state = strategy.complete_task(task_in_progress, manager)
    
    assert new_state.is_finished()


def test_manager_can_validate_tasks(task_completed, manager):
    """Test that manager can validate tasks."""
    strategy = ManagerTaskCompletionStrategy()
    
    new_state = strategy.validate_task(task_completed, manager)
    
    assert new_state.is_finished()


# ============================================================================
# TESTS: TaskCompletionStrategyFactory
# ============================================================================

def test_factory_returns_employee_strategy():
    """Test factory returns correct strategy for EMPLOYEE."""
    strategy = TaskCompletionStrategyFactory.get_strategy(RoleEnum.EMPLOYEE)
    
    assert isinstance(strategy, EmployeeTaskCompletionStrategy)


def test_factory_returns_supervisor_strategy():
    """Test factory returns correct strategy for SUPERVISOR."""
    strategy = TaskCompletionStrategyFactory.get_strategy(RoleEnum.SUPERVISOR)
    
    assert isinstance(strategy, SupervisorTaskCompletionStrategy)


def test_factory_returns_manager_strategy():
    """Test factory returns correct strategy for MANAGER."""
    strategy = TaskCompletionStrategyFactory.get_strategy(RoleEnum.MANAGER)
    
    assert isinstance(strategy, ManagerTaskCompletionStrategy)


def test_factory_can_role_validate():
    """Test factory method for checking validation permissions."""
    assert not TaskCompletionStrategyFactory.can_role_validate(RoleEnum.EMPLOYEE)
    assert TaskCompletionStrategyFactory.can_role_validate(RoleEnum.SUPERVISOR)
    assert TaskCompletionStrategyFactory.can_role_validate(RoleEnum.MANAGER)


# ============================================================================
# TESTS: Strategy Comparison
# ============================================================================

def test_employee_vs_supervisor_completion_behavior(task_in_progress, employee, supervisor):
    """Test different completion behavior between employee and supervisor."""
    # Employee completes
    employee_task = Task(
        task_id=uuid4(),
        work_id=task_in_progress.work_id,
        product_id=task_in_progress.product_id,
        task_name="Task 1",
        description="Test",
        state=StateTask(value=StateTaskEnum.IN_PROGRESS),
        labor=Money(amount=Decimal("50000")),
        estimated_value=Money(amount=Decimal("50000")),
        execution_order=0,
        assigned_user_id="11111"
    )
    
    employee_strategy = TaskCompletionStrategyFactory.get_strategy(RoleEnum.EMPLOYEE)
    employee_new_state = employee_strategy.complete_task(employee_task, employee)
    
    # Supervisor completes
    supervisor_task = Task(
        task_id=uuid4(),
        work_id=task_in_progress.work_id,
        product_id=task_in_progress.product_id,
        task_name="Task 2",
        description="Test",
        state=StateTask(value=StateTaskEnum.IN_PROGRESS),
        labor=Money(amount=Decimal("50000")),
        estimated_value=Money(amount=Decimal("50000")),
        execution_order=1,
        assigned_user_id="67890"
    )
    
    supervisor_strategy = TaskCompletionStrategyFactory.get_strategy(RoleEnum.SUPERVISOR)
    supervisor_new_state = supervisor_strategy.complete_task(supervisor_task, supervisor)
    
    # Employee: COMPLETED (needs validation)
    assert employee_new_state.is_completed()
    assert not employee_new_state.is_finished()
    
    # Supervisor: FINISHED (auto-validated)
    assert supervisor_new_state.is_finished()


# ============================================================================
# TESTS: Edge Cases
# ============================================================================

def test_strategy_validates_task_state_before_completion(employee):
    """Test that strategies validate task state."""
    # Try to complete a PENDING task
    task = Task(
        task_id=uuid4(),
        work_id=uuid4(),
        product_id=uuid4(),
        task_name="Test",
        description="Test",
        state=StateTask(value=StateTaskEnum.PENDING),
        labor=Money(amount=Decimal("50000")),
        estimated_value=Money(amount=Decimal("50000")),
        execution_order=0
    )
    
    strategy = EmployeeTaskCompletionStrategy()
    
    with pytest.raises(ValueError, match="IN_PROGRESS"):
        strategy.complete_task(task, employee)


def test_all_strategies_implement_interface():
    """Test that all strategies implement the interface correctly."""
    strategies = [
        EmployeeTaskCompletionStrategy(),
        SupervisorTaskCompletionStrategy(),
        ManagerTaskCompletionStrategy()
    ]
    
    for strategy in strategies:
        assert isinstance(strategy, TaskCompletionStrategy)
        assert hasattr(strategy, 'complete_task')
        assert hasattr(strategy, 'requires_validation')
        assert hasattr(strategy, 'can_validate_tasks')
        assert hasattr(strategy, 'validate_task')

