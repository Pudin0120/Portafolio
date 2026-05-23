"""
Unit tests for advanced Task functionality.

Tests cover:
- Task assignment (only SUPERVISOR/MANAGER)
- Task reassignment
- Task blocking and unblocking
- Task completion by role (EMPLOYEE vs SUPERVISOR/MANAGER)
- Task validation
- State transitions
- Domain events generation
"""
import pytest
from decimal import Decimal
from uuid import uuid4

from app.domain.models.task import Task
from app.domain.models.user import User, RoleEnum
from app.domain.value_objects import DocumentNumber, Email, Money
from app.domain.value_objects.document_number import DocumentEnum
from app.domain.value_objects.state_task import StateTask, StateTaskEnum
from app.domain.value_objects.state_user import StateUser, StateEnum as StateUserEnum
from app.domain.events.task_events import (
    TaskAssigned,
    TaskReassigned,
    TaskUnblocked,
    TaskCompleted,
    TaskValidated
)


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
        firebase_uid="uid_manager"
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
        firebase_uid="uid_supervisor"
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
        firebase_uid="uid_employee"
    )


@pytest.fixture
def inactive_employee():
    """Inactive employee fixture."""
    return User(
        identification_number=DocumentNumber(value="99999", doc_type=DocumentEnum.CC),
        role=RoleEnum.EMPLOYEE,
        first_name="Pedro",
        last_name="Inactive",
        email=Email(value="inactive@empresa.com"),
        state=StateUser(value=StateUserEnum.INACTIVE),
        firebase_uid="uid_inactive"
    )


@pytest.fixture
def pending_task():
    """Task in PENDING state."""
    return Task(
        task_id=uuid4(),
        work_id=uuid4(),
        product_id=uuid4(),
        task_name="Soldar marco",
        description="Soldar marco de la puerta",
        state=StateTask(value=StateTaskEnum.PENDING),
        labor=Money(amount=Decimal("50000")),
        estimated_value=Money(amount=Decimal("50000")),
        execution_order=0
    )


@pytest.fixture
def blocked_pending_task():
    """Task in PENDING state that will be blocked."""
    return Task(
        task_id=uuid4(),
        work_id=uuid4(),
        product_id=uuid4(),
        task_name="Instalar chapa",
        description="Instalar chapa en la puerta",
        state=StateTask(value=StateTaskEnum.PENDING),
        labor=Money(amount=Decimal("30000")),
        estimated_value=Money(amount=Decimal("30000")),
        execution_order=1,
        is_blocked=True,
        previous_task_id=uuid4()
    )


# ============================================================================
# TESTS: Task Assignment
# ============================================================================

def test_supervisor_can_assign_task(pending_task, supervisor, employee):
    """Test that supervisor can assign task to employee."""
    pending_task.assign_to(user=employee, assigned_by=supervisor)
    
    assert pending_task.is_assigned
    assert pending_task.assigned_user_id == employee.firebase_uid
    assert pending_task.is_ready  # Not blocked, so goes to READY
    
    # Check event
    events = pending_task.clear_domain_events()
    assert any(isinstance(e, TaskAssigned) for e in events)


def test_manager_can_assign_task(pending_task, manager, employee):
    """Test that manager can assign task to employee."""
    pending_task.assign_to(user=employee, assigned_by=manager)
    
    assert pending_task.is_assigned
    assert pending_task.is_ready


def test_employee_cannot_assign_task(pending_task, employee):
    """Test that employee cannot assign tasks."""
    another_employee = User(
        identification_number=DocumentNumber(value="22222", doc_type=DocumentEnum.CC),
        role=RoleEnum.EMPLOYEE,
        first_name="Maria",
        last_name="Empleada",
        email=Email(value="maria@empresa.com"),
        state=StateUser(value=StateUserEnum.ACTIVE),
        firebase_uid="uid_maria"
    )
    
    with pytest.raises(ValueError, match="Solo SUPERVISOR o MANAGER"):
        pending_task.assign_to(user=another_employee, assigned_by=employee)


def test_assign_blocked_task_goes_to_assigned_state(blocked_pending_task, supervisor, employee):
    """Test that assigning a blocked task goes to ASSIGNED (not READY)."""
    blocked_pending_task.assign_to(user=employee, assigned_by=supervisor)
    
    assert blocked_pending_task.is_assigned
    assert blocked_pending_task.is_assigned_state  # State ASSIGNED (blocked)
    assert not blocked_pending_task.is_ready


def test_cannot_assign_to_inactive_user(pending_task, supervisor, inactive_employee):
    """Test that task cannot be assigned to inactive user."""
    with pytest.raises(ValueError, match="activos"):
        pending_task.assign_to(user=inactive_employee, assigned_by=supervisor)


def test_inactive_supervisor_cannot_assign(pending_task, employee):
    """Test that inactive supervisor cannot assign tasks."""
    inactive_supervisor = User(
        identification_number=DocumentNumber(value="88888", doc_type=DocumentEnum.CC),
        role=RoleEnum.SUPERVISOR,
        first_name="Supervisor",
        last_name="Inactive",
        email=Email(value="supervisor_inactive@empresa.com"),
        state=StateUser(value=StateUserEnum.INACTIVE),
        firebase_uid="uid_inactive_sup"
    )
    
    with pytest.raises(ValueError, match="active"):
        pending_task.assign_to(user=employee, assigned_by=inactive_supervisor)


# ============================================================================
# TESTS: Task Reassignment
# ============================================================================

def test_reassign_task_to_another_employee(pending_task, supervisor, employee):
    """Test reassigning task to another employee."""
    # First assign
    pending_task.assign_to(user=employee, assigned_by=supervisor)
    previous_user = pending_task.assigned_user_id
    
    # Reassign
    another_employee = User(
        identification_number=DocumentNumber(value="33333", doc_type=DocumentEnum.CC),
        role=RoleEnum.EMPLOYEE,
        first_name="Carlos",
        last_name="Otro",
        email=Email(value="carlos@empresa.com"),
        state=StateUser(value=StateUserEnum.ACTIVE),
        firebase_uid="uid_carlos"
    )
    
    pending_task.reassign_to(user=another_employee, reassigned_by=supervisor, reason="Cambio de asignacion")
    
    assert pending_task.assigned_user_id == another_employee.identification_number.value
    assert pending_task.assigned_user_id != previous_user
    
    # Check event
    events = pending_task.clear_domain_events()
    reassign_events = [e for e in events if isinstance(e, TaskReassigned)]
    assert len(reassign_events) > 0


def test_employee_cannot_reassign_task(pending_task, supervisor, employee):
    """Test that employee cannot reassign tasks."""
    pending_task.assign_to(user=employee, assigned_by=supervisor)
    
    another_employee = User(
        identification_number=DocumentNumber(value="44444", doc_type=DocumentEnum.CC),
        role=RoleEnum.EMPLOYEE,
        first_name="Pedro",
        last_name="Empleado",
        email=Email(value="pedro@empresa.com"),
        state=StateUser(value=StateUserEnum.ACTIVE),
        firebase_uid="uid_pedro"
    )
    
    with pytest.raises(ValueError, match="Solo SUPERVISOR o MANAGER"):
        pending_task.reassign_to(user=another_employee, reassigned_by=employee, reason="Test")


def test_cannot_reassign_unassigned_task(pending_task, supervisor, employee):
    """Test that unassigned task cannot be reassigned."""
    with pytest.raises(ValueError, match="ya asignadas"):
        pending_task.reassign_to(user=employee, reassigned_by=supervisor, reason="Test")


# ============================================================================
# TESTS: Task Unblocking
# ============================================================================

def test_unblock_assigned_task(supervisor, employee):
    """Test unblocking a blocked task."""
    task = Task(
        task_id=uuid4(),
        work_id=uuid4(),
        product_id=uuid4(),
        task_name="Task 2",
        description="Second task",
        state=StateTask(value=StateTaskEnum.ASSIGNED),
        labor=Money(amount=Decimal("50000")),
        estimated_value=Money(amount=Decimal("50000")),
        execution_order=1,
        is_blocked=True,
        previous_task_id=uuid4(),
        assigned_user_id="11111"
    )
    
    event = task.unblock()
    
    assert not task.is_blocked
    assert task.is_ready
    assert isinstance(event, TaskUnblocked)


def test_cannot_unblock_non_blocked_task(pending_task, supervisor, employee):
    """Test that non-blocked task cannot be unblocked."""
    pending_task.assign_to(user=employee, assigned_by=supervisor)
    
    # Task is READY, not blocked
    with pytest.raises(ValueError, match="no esta bloqueada"):
        pending_task.unblock()


# ============================================================================
# TESTS: Task Completion by EMPLOYEE
# ============================================================================

def test_employee_starts_and_completes_task(pending_task, supervisor, employee):
    """Test employee starts and completes task (requires validation)."""
    # Assign
    pending_task.assign_to(user=employee, assigned_by=supervisor)
    
    # Start
    pending_task.start(started_by=employee)
    assert pending_task.is_in_progress
    
    # Complete
    pending_task.complete(completed_by=employee)
    assert pending_task.is_completed  # Not FINISHED yet
    assert not pending_task.is_finished
    
    # Check event
    events = pending_task.clear_domain_events()
    assert any(isinstance(e, TaskCompleted) for e in events)


def test_only_assigned_user_can_start_task(pending_task, supervisor, employee):
    """Test that only assigned user can start task."""
    pending_task.assign_to(user=employee, assigned_by=supervisor)
    
    another_employee = User(
        identification_number=DocumentNumber(value="55555", doc_type=DocumentEnum.CC),
        role=RoleEnum.EMPLOYEE,
        first_name="Otro",
        last_name="Empleado",
        email=Email(value="otro@empresa.com"),
        state=StateUser(value=StateUserEnum.ACTIVE),
        firebase_uid="uid_otro"
    )
    
    with pytest.raises(ValueError, match="asignado puede iniciar"):
        pending_task.start(started_by=another_employee)


def test_cannot_start_non_ready_task(blocked_pending_task, supervisor, employee):
    """Test that blocked task (ASSIGNED) cannot be started."""
    blocked_pending_task.assign_to(user=employee, assigned_by=supervisor)
    
    # Task is ASSIGNED (blocked), not READY
    with pytest.raises(ValueError, match="READY"):
        blocked_pending_task.start(started_by=employee)


# ============================================================================
# TESTS: Task Completion by SUPERVISOR/MANAGER
# ============================================================================

def test_supervisor_completes_task_auto_validated(pending_task, supervisor):
    """Test supervisor completes task (auto-validated, no validation needed)."""
    # Assign to supervisor
    pending_task.assign_to(user=supervisor, assigned_by=supervisor)
    
    # Start and complete
    pending_task.start(started_by=supervisor)
    pending_task.complete(completed_by=supervisor)
    
    # Should be FINISHED directly (auto-validated)
    assert pending_task.is_finished
    assert pending_task.validated_by_user_id is not None


def test_manager_completes_task_auto_validated(pending_task, manager):
    """Test manager completes task (auto-validated)."""
    pending_task.assign_to(user=manager, assigned_by=manager)
    
    pending_task.start(started_by=manager)
    pending_task.complete(completed_by=manager)
    
    assert pending_task.is_finished


# ============================================================================
# TESTS: Task Validation
# ============================================================================

def test_supervisor_validates_employee_task(pending_task, supervisor, employee):
    """Test supervisor validates task completed by employee."""
    # Employee completes
    pending_task.assign_to(user=employee, assigned_by=supervisor)
    pending_task.start(started_by=employee)
    pending_task.complete(completed_by=employee)
    
    assert pending_task.is_completed
    
    # Supervisor validates
    pending_task.validate(validated_by=supervisor)
    
    assert pending_task.is_finished
    assert pending_task.validated_by_user_id == supervisor.identification_number.value
    
    # Check event
    events = pending_task.clear_domain_events()
    assert any(isinstance(e, TaskValidated) for e in events)


def test_manager_validates_employee_task(pending_task, manager, employee, supervisor):
    """Test manager validates task completed by employee."""
    pending_task.assign_to(user=employee, assigned_by=supervisor)
    pending_task.start(started_by=employee)
    pending_task.complete(completed_by=employee)
    
    pending_task.validate(validated_by=manager)
    
    assert pending_task.is_finished


def test_employee_cannot_validate_task(pending_task, supervisor, employee):
    """Test that employee cannot validate tasks."""
    pending_task.assign_to(user=employee, assigned_by=supervisor)
    pending_task.start(started_by=employee)
    pending_task.complete(completed_by=employee)
    
    with pytest.raises(ValueError, match="no puede validar"):
        pending_task.validate(validated_by=employee)


def test_cannot_validate_non_completed_task(pending_task, supervisor, employee):
    """Test that non-COMPLETED task cannot be validated."""
    pending_task.assign_to(user=employee, assigned_by=supervisor)
    pending_task.start(started_by=employee)
    
    # Task is IN_PROGRESS, not COMPLETED
    with pytest.raises(ValueError, match="COMPLETED"):
        pending_task.validate(validated_by=supervisor)


# ============================================================================
# TESTS: Domain Events
# ============================================================================

def test_task_generates_assigned_event(pending_task, supervisor, employee):
    """Test that assigning task generates TaskAssigned event."""
    pending_task.assign_to(user=employee, assigned_by=supervisor)
    
    events = pending_task.clear_domain_events()
    assigned_events = [e for e in events if isinstance(e, TaskAssigned)]
    
    assert len(assigned_events) == 1
    assert assigned_events[0].task_id == pending_task.task_id
    assert assigned_events[0].assigned_user_id == pending_task.assigned_user_id


def test_task_generates_completed_event(pending_task, supervisor, employee):
    """Test that completing task generates TaskCompleted event."""
    pending_task.assign_to(user=employee, assigned_by=supervisor)
    pending_task.start(started_by=employee)
    pending_task.complete(completed_by=employee)
    
    events = pending_task.clear_domain_events()
    completed_events = [e for e in events if isinstance(e, TaskCompleted)]
    
    assert len(completed_events) >= 1


def test_task_generates_validated_event(pending_task, supervisor, employee):
    """Test that validating task generates TaskValidated event."""
    pending_task.assign_to(user=employee, assigned_by=supervisor)
    pending_task.start(started_by=employee)
    pending_task.complete(completed_by=employee)
    pending_task.clear_domain_events()  # Clear previous events
    
    pending_task.validate(validated_by=supervisor)
    
    events = pending_task.clear_domain_events()
    validated_events = [e for e in events if isinstance(e, TaskValidated)]
    
    assert len(validated_events) == 1


# ============================================================================
# TESTS: State Transitions
# ============================================================================

def test_complete_task_flow_employee(pending_task, supervisor, employee):
    """Test complete task flow for employee."""
    # PENDING  READY (via assign)
    pending_task.assign_to(user=employee, assigned_by=supervisor)
    assert pending_task.state.value == StateTaskEnum.READY
    
    # READY  IN_PROGRESS (via start)
    pending_task.start(started_by=employee)
    assert pending_task.state.value == StateTaskEnum.IN_PROGRESS
    
    # IN_PROGRESS  COMPLETED (via complete)
    pending_task.complete(completed_by=employee)
    assert pending_task.state.value == StateTaskEnum.COMPLETED
    
    # COMPLETED  FINISHED (via validate)
    pending_task.validate(validated_by=supervisor)
    assert pending_task.state.value == StateTaskEnum.FINISHED


def test_complete_task_flow_supervisor(pending_task, supervisor):
    """Test complete task flow for supervisor (auto-validated)."""
    # PENDING  READY
    pending_task.assign_to(user=supervisor, assigned_by=supervisor)
    assert pending_task.state.value == StateTaskEnum.READY
    
    # READY  IN_PROGRESS
    pending_task.start(started_by=supervisor)
    assert pending_task.state.value == StateTaskEnum.IN_PROGRESS
    
    # IN_PROGRESS  FINISHED (auto-validated)
    pending_task.complete(completed_by=supervisor)
    assert pending_task.state.value == StateTaskEnum.FINISHED


def test_blocked_task_flow(supervisor, employee):
    """Test blocked task flow (PENDING  ASSIGNED  READY)."""
    task = Task(
        task_id=uuid4(),
        work_id=uuid4(),
        product_id=uuid4(),
        task_name="Blocked task",
        description="Test",
        state=StateTask(value=StateTaskEnum.PENDING),
        labor=Money(amount=Decimal("50000")),
        estimated_value=Money(amount=Decimal("50000")),
        execution_order=1,
        is_blocked=True,
        previous_task_id=uuid4()
    )
    
    # PENDING  ASSIGNED (blocked)
    task.assign_to(user=employee, assigned_by=supervisor)
    assert task.state.value == StateTaskEnum.ASSIGNED
    assert task.is_blocked
    
    # ASSIGNED  READY (unblock)
    task.unblock()
    assert task.state.value == StateTaskEnum.READY
    assert not task.is_blocked


# ============================================================================
# TESTS: Edge Cases
# ============================================================================

def test_cannot_assign_already_assigned_task(pending_task, supervisor, employee):
    """Test that already assigned task cannot be assigned again."""
    pending_task.assign_to(user=employee, assigned_by=supervisor)
    
    # Try to assign again
    another_employee = User(
        identification_number=DocumentNumber(value="66666", doc_type=DocumentEnum.CC),
        role=RoleEnum.EMPLOYEE,
        first_name="Ana",
        last_name="Empleada",
        email=Email(value="ana@empresa.com"),
        state=StateUser(value=StateUserEnum.ACTIVE),
        firebase_uid="uid_ana"
    )
    
    with pytest.raises(ValueError, match="PENDING"):
        pending_task.assign_to(user=another_employee, assigned_by=supervisor)


def test_cannot_complete_unassigned_task():
    """Test that unassigned task cannot be completed."""
    task = Task(
        task_id=uuid4(),
        work_id=uuid4(),
        product_id=uuid4(),
        task_name="Test",
        description="Test",
        state=StateTask(value=StateTaskEnum.IN_PROGRESS),
        labor=Money(amount=Decimal("50000")),
        estimated_value=Money(amount=Decimal("50000")),
        execution_order=0
    )
    
    employee = User(
        identification_number=DocumentNumber(value="77777", doc_type=DocumentEnum.CC),
        role=RoleEnum.EMPLOYEE,
        first_name="Test",
        last_name="User",
        email=Email(value="test@empresa.com"),
        state=StateUser(value=StateUserEnum.ACTIVE),
        firebase_uid="uid_test"
    )
    
    with pytest.raises(ValueError, match="asignada"):
        task.complete(completed_by=employee)


def test_cannot_reassign_finished_task(pending_task, supervisor, employee):
    """Test that finished task cannot be reassigned."""
    pending_task.assign_to(user=supervisor, assigned_by=supervisor)
    pending_task.start(started_by=supervisor)
    pending_task.complete(completed_by=supervisor)
    
    # Task is FINISHED
    another_employee = User(
        identification_number=DocumentNumber(value="88888", doc_type=DocumentEnum.CC),
        role=RoleEnum.EMPLOYEE,
        first_name="Test",
        last_name="User",
        email=Email(value="test@empresa.com"),
        state=StateUser(value=StateUserEnum.ACTIVE),
        firebase_uid="uid_test2"
    )
    
    with pytest.raises(ValueError, match="finalizada"):
        pending_task.reassign_to(user=another_employee, reassigned_by=supervisor, reason="Test")

