import pytest
from pydantic import ValidationError

from app.domain.value_objects.state_user import StateEnum, StateUser


def test_state_user_creation_active():
    """Test create StateUser con estado active."""
    state = StateUser(value=StateEnum.ACTIVE)
    assert state.value == StateEnum.ACTIVE
    assert str(state) == "A"
    assert state.is_active is True


def test_state_user_creation_inactive():
    """Test create StateUser con estado inactive."""
    state = StateUser(value=StateEnum.INACTIVE)
    assert state.value == StateEnum.INACTIVE
    assert str(state) == "I"
    assert state.is_active is False


def test_state_user_equality():
    """Test igualdad entre StateUser."""
    state1 = StateUser(value=StateEnum.ACTIVE)
    state2 = StateUser(value=StateEnum.ACTIVE)
    state3 = StateUser(value=StateEnum.INACTIVE)

    assert state1 == state2
    assert state1 != state3
    assert state2 != state3


def test_state_user_hash():
    """Test que StateUser es hasheable."""
    state1 = StateUser(value=StateEnum.ACTIVE)
    state2 = StateUser(value=StateEnum.ACTIVE)
    state3 = StateUser(value=StateEnum.INACTIVE)

    # Objetos iguales tienen el mismo hash
    assert hash(state1) == hash(state2)
    # Objetos diferentes pueden tener hash diferentes
    assert hash(state1) != hash(state3)

    # Se puede usar en un set
    states = {state1, state2, state3}
    assert len(states) == 2  # Solo 2 unicos (ACTIVE y INACTIVE)


def test_state_user_activate():
    """Test activar un estado."""
    inactive_state = StateUser(value=StateEnum.INACTIVE)
    assert not inactive_state.is_active

    active_state = inactive_state.activate()
    assert active_state.is_active
    assert active_state.value == StateEnum.ACTIVE

    # El estado original no cambia (inmutable)
    assert not inactive_state.is_active


def test_state_user_deactivate():
    """Test desactivar un estado."""
    active_state = StateUser(value=StateEnum.ACTIVE)
    assert active_state.is_active

    inactive_state = active_state.deactivate()
    assert not inactive_state.is_active
    assert inactive_state.value == StateEnum.INACTIVE

    # El estado original no cambia (inmutable)
    assert active_state.is_active


def test_state_user_validation_error():
    """Test que se lanza ValidationError con valores invalids."""
    with pytest.raises(ValidationError):
        StateUser(value="INVALID_STATE")

    with pytest.raises(ValidationError):
        StateUser(value=None)


def test_state_enum_values():
    """Test los valores del enum StateEnum."""
    assert StateEnum.ACTIVE.value == "A"
    assert StateEnum.INACTIVE.value == "I"

    # Test que los valores son strings
    assert isinstance(StateEnum.ACTIVE, str)
    assert isinstance(StateEnum.INACTIVE, str)


def test_state_user_str_representation():
    """Test la representacion en string de StateUser."""
    active_state = StateUser(value=StateEnum.ACTIVE)
    inactive_state = StateUser(value=StateEnum.INACTIVE)

    assert str(active_state) == "A"
    assert str(inactive_state) == "I"


def test_state_user_equality_with_different_types():
    """Test igualdad con objetos de diferentes tipos."""
    state = StateUser(value=StateEnum.ACTIVE)

    # No debe ser igual a otros tipos
    assert state != "A"
    assert state != StateEnum.ACTIVE
    assert state != None
    assert state != 1

