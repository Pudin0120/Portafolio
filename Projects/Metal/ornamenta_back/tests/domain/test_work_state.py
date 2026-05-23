"""
Unit tests for WorkState (State Pattern).

Tests cover:
- State transition validations
- Allowed operations per state
- State-specific behavior
- Invalid transitions
"""
import pytest
from uuid import uuid4

from app.domain.value_objects.work_state import (
    WorkState,
    DraftState,
    QuotedState,
    InProgressState,
    DeliveredState,
    WorkStateEnum,
    create_work_state
)
from app.domain.models.work import Work
from app.domain.models.client import Client
from app.domain.value_objects import DocumentNumber, Email
from app.domain.value_objects.document_number import DocumentEnum


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """Client fixture."""
    return Client(
        identification_number=DocumentNumber(value="12345", doc_type=DocumentEnum.CC),
        first_name="Pedro",
        last_name="Client",
        email=Email(value="client@email.com"),
        phone="555-1234",
        address="Calle 123"
    )


@pytest.fixture
def draft_work(client):
    """Work in DRAFT state."""
    return Work(
        work_id=uuid4(),
        identification_number_client=client.identification_number,
        work_name="Test Work",
        description="Test",
        state=DraftState()
    )


# ============================================================================
# TESTS: DraftState
# ============================================================================

def test_draft_state_name():
    """Test DraftState name."""
    state = DraftState()
    assert state.get_state_name() == WorkStateEnum.DRAFT


def test_draft_state_can_add_products():
    """Test that DRAFT state allows adding products."""
    state = DraftState()
    assert state.can_add_products()


def test_draft_state_can_remove_products():
    """Test that DRAFT state allows removing products."""
    state = DraftState()
    assert state.can_remove_products()


def test_draft_state_can_edit_product_order():
    """Test that DRAFT state allows editing product order."""
    state = DraftState()
    assert state.can_edit_product_order()


def test_draft_state_can_quote():
    """Test that DRAFT state can transition to QUOTED."""
    state = DraftState()
    assert state.can_quote()


def test_draft_state_cannot_start_work():
    """Test that DRAFT state cannot start work."""
    state = DraftState()
    assert not state.can_start_work()


def test_draft_state_cannot_deliver():
    """Test that DRAFT state cannot deliver."""
    state = DraftState()
    assert not state.can_deliver()


def test_draft_state_quote_transition(draft_work):
    """Test transition from DRAFT to QUOTED."""
    state = DraftState()
    new_state = state.quote(draft_work)
    
    assert isinstance(new_state, QuotedState)
    assert new_state.get_state_name() == WorkStateEnum.QUOTED


def test_draft_state_cannot_start_work_directly(draft_work):
    """Test that DRAFT cannot start work directly."""
    state = DraftState()
    
    with pytest.raises(ValueError, match="debe cotizarse"):
        state.start_work(draft_work)


def test_draft_state_cannot_deliver_directly(draft_work):
    """Test that DRAFT cannot deliver directly."""
    state = DraftState()
    
    with pytest.raises(ValueError, match="No se puede entregar"):
        state.deliver(draft_work)


# ============================================================================
# TESTS: QuotedState
# ============================================================================

def test_quoted_state_name():
    """Test QuotedState name."""
    state = QuotedState()
    assert state.get_state_name() == WorkStateEnum.QUOTED


def test_quoted_state_can_add_products():
    """Test that QUOTED state allows adding products."""
    state = QuotedState()
    assert state.can_add_products()


def test_quoted_state_can_remove_products():
    """Test that QUOTED state allows removing products."""
    state = QuotedState()
    assert state.can_remove_products()


def test_quoted_state_can_start_work():
    """Test that QUOTED state can start work."""
    state = QuotedState()
    assert state.can_start_work()


def test_quoted_state_cannot_quote_again():
    """Test that QUOTED state cannot quote again."""
    state = QuotedState()
    assert not state.can_quote()


def test_quoted_state_start_work_transition(draft_work):
    """Test transition from QUOTED to IN_PROGRESS."""
    state = QuotedState()
    new_state = state.start_work(draft_work)
    
    assert isinstance(new_state, InProgressState)
    assert new_state.get_state_name() == WorkStateEnum.IN_PROGRESS


def test_quoted_state_cannot_quote_again_raises_error(draft_work):
    """Test that QUOTED cannot quote again."""
    state = QuotedState()
    
    with pytest.raises(ValueError, match="ya esta cotizado"):
        state.quote(draft_work)


def test_quoted_state_cannot_deliver_directly(draft_work):
    """Test that QUOTED cannot deliver directly."""
    state = QuotedState()
    
    with pytest.raises(ValueError, match="no ha iniciado"):
        state.deliver(draft_work)


# ============================================================================
# TESTS: InProgressState
# ============================================================================

def test_in_progress_state_name():
    """Test InProgressState name."""
    state = InProgressState()
    assert state.get_state_name() == WorkStateEnum.IN_PROGRESS


def test_in_progress_state_cannot_add_products():
    """Test that IN_PROGRESS state cannot add products."""
    state = InProgressState()
    assert not state.can_add_products()


def test_in_progress_state_cannot_remove_products():
    """Test that IN_PROGRESS state cannot remove products."""
    state = InProgressState()
    assert not state.can_remove_products()


def test_in_progress_state_cannot_edit_order():
    """Test that IN_PROGRESS state cannot edit product order."""
    state = InProgressState()
    assert not state.can_edit_product_order()


def test_in_progress_state_can_deliver():
    """Test that IN_PROGRESS state can deliver."""
    state = InProgressState()
    assert state.can_deliver()


def test_in_progress_state_cannot_quote():
    """Test that IN_PROGRESS state cannot quote."""
    state = InProgressState()
    assert not state.can_quote()


def test_in_progress_state_cannot_start_again():
    """Test that IN_PROGRESS state cannot start again."""
    state = InProgressState()
    assert not state.can_start_work()


def test_in_progress_state_deliver_transition(draft_work):
    """Test transition from IN_PROGRESS to DELIVERED."""
    state = InProgressState()
    new_state = state.deliver(draft_work)
    
    assert isinstance(new_state, DeliveredState)
    assert new_state.get_state_name() == WorkStateEnum.DELIVERED


def test_in_progress_state_cannot_quote_raises_error(draft_work):
    """Test that IN_PROGRESS cannot quote."""
    state = InProgressState()
    
    with pytest.raises(ValueError, match="en progreso"):
        state.quote(draft_work)


# ============================================================================
# TESTS: DeliveredState
# ============================================================================

def test_delivered_state_name():
    """Test DeliveredState name."""
    state = DeliveredState()
    assert state.get_state_name() == WorkStateEnum.DELIVERED


def test_delivered_state_cannot_add_products():
    """Test that DELIVERED state cannot add products."""
    state = DeliveredState()
    assert not state.can_add_products()


def test_delivered_state_cannot_remove_products():
    """Test that DELIVERED state cannot remove products."""
    state = DeliveredState()
    assert not state.can_remove_products()


def test_delivered_state_cannot_do_anything():
    """Test that DELIVERED state is immutable."""
    state = DeliveredState()
    
    assert not state.can_add_products()
    assert not state.can_remove_products()
    assert not state.can_edit_product_order()
    assert not state.can_quote()
    assert not state.can_start_work()
    assert not state.can_deliver()


def test_delivered_state_all_transitions_raise_errors(draft_work):
    """Test that DELIVERED state cannot transition to any state."""
    state = DeliveredState()
    
    with pytest.raises(ValueError, match="entregado"):
        state.quote(draft_work)
    
    with pytest.raises(ValueError, match="entregado"):
        state.start_work(draft_work)
    
    with pytest.raises(ValueError, match="entregado"):
        state.deliver(draft_work)


# ============================================================================
# TESTS: State Equality and Hashing
# ============================================================================

def test_state_equality():
    """Test state equality comparison."""
    state1 = DraftState()
    state2 = DraftState()
    
    assert state1 == state2


def test_state_inequality():
    """Test state inequality."""
    draft = DraftState()
    quoted = QuotedState()
    
    assert draft != quoted


def test_state_hash():
    """Test state hashing."""
    state1 = DraftState()
    state2 = DraftState()
    
    assert hash(state1) == hash(state2)


def test_state_set():
    """Test that states can be used in sets."""
    states = {DraftState(), QuotedState(), InProgressState()}
    
    assert len(states) == 3


# ============================================================================
# TESTS: State Factory
# ============================================================================

def test_create_work_state_draft():
    """Test creating DRAFT state via factory."""
    state = create_work_state(WorkStateEnum.DRAFT)
    
    assert isinstance(state, DraftState)


def test_create_work_state_quoted():
    """Test creating QUOTED state via factory."""
    state = create_work_state(WorkStateEnum.QUOTED)
    
    assert isinstance(state, QuotedState)


def test_create_work_state_in_progress():
    """Test creating IN_PROGRESS state via factory."""
    state = create_work_state(WorkStateEnum.IN_PROGRESS)
    
    assert isinstance(state, InProgressState)


def test_create_work_state_delivered():
    """Test creating DELIVERED state via factory."""
    state = create_work_state(WorkStateEnum.DELIVERED)
    
    assert isinstance(state, DeliveredState)


def test_create_work_state_invalid():
    """Test creating invalid state raises error."""
    with pytest.raises(ValueError, match="desconocido"):
        create_work_state("INVALID_STATE")


# ============================================================================
# TESTS: State String Representation
# ============================================================================

def test_state_str_representation():
    """Test state string representation."""
    assert str(DraftState()) == "DRAFT"
    assert str(QuotedState()) == "QUOTED"
    assert str(InProgressState()) == "IN_PROGRESS"
    assert str(DeliveredState()) == "DELIVERED"


# ============================================================================
# TESTS: Complete State Flow
# ============================================================================

def test_complete_state_flow(draft_work):
    """Test complete state transition flow."""
    # DRAFT
    assert isinstance(draft_work.state, DraftState)
    
    # DRAFT  QUOTED
    new_state = draft_work.state.quote(draft_work)
    assert isinstance(new_state, QuotedState)
    
    # QUOTED  IN_PROGRESS
    new_state = new_state.start_work(draft_work)
    assert isinstance(new_state, InProgressState)
    
    # IN_PROGRESS  DELIVERED
    new_state = new_state.deliver(draft_work)
    assert isinstance(new_state, DeliveredState)


# ============================================================================
# TESTS: State Behavior Consistency
# ============================================================================

def test_all_states_implement_interface():
    """Test that all states implement WorkState interface."""
    states = [
        DraftState(),
        QuotedState(),
        InProgressState(),
        DeliveredState()
    ]
    
    for state in states:
        assert isinstance(state, WorkState)
        assert hasattr(state, 'get_state_name')
        assert hasattr(state, 'can_add_products')
        assert hasattr(state, 'can_remove_products')
        assert hasattr(state, 'can_edit_product_order')
        assert hasattr(state, 'can_quote')
        assert hasattr(state, 'can_start_work')
        assert hasattr(state, 'can_deliver')
        assert hasattr(state, 'quote')
        assert hasattr(state, 'start_work')
        assert hasattr(state, 'deliver')

