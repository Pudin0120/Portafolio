"""Tests para el sistema de auditoria de cambios de estado de users."""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, mock_open
import uuid

from app.domain.models.user import User, RoleEnum
from app.domain.value_objects.document_number import DocumentNumber, DocumentEnum
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateUser, StateEnum
from app.domain.events.user_events import UserStateChanged
from app.application.use_cases.activate_user import ActivateUser
from app.application.use_cases.desactivate_user import DeactivateUser
from app.application.event_handlers import UserStateChangedHandler


@pytest.fixture
def manager_user():
    """User con rol MANAGER para ejecutar acciones."""
    return User(
        identification_number=DocumentNumber(value="87654321", doc_type=DocumentEnum.CC),
        role=RoleEnum.MANAGER,
        first_name="Maria",
        last_name="Garcia",
        email=Email(value="maria.garcia@example.com"),
        state=StateUser(value=StateEnum.ACTIVE),
        firebase_uid="manager_uid_123"
    )


@pytest.fixture
def employee_user():
    """User con rol EMPLOYEE para ser afectado."""
    return User(
        identification_number=DocumentNumber(value="12345678", doc_type=DocumentEnum.CC),
        role=RoleEnum.EMPLOYEE,
        first_name="Juan",
        last_name="Perez",
        email=Email(value="juan.perez@example.com"),
        state=StateUser(value=StateEnum.ACTIVE),
        firebase_uid="employee_uid_456"
    )


@pytest.fixture
def supervisor_user():
    """User con rol SUPERVISOR para ser afectado."""
    return User(
        identification_number=DocumentNumber(value="11223344", doc_type=DocumentEnum.CC),
        role=RoleEnum.SUPERVISOR,
        first_name="Carlos",
        last_name="Lopez",
        email=Email(value="carlos.lopez@example.com"),
        state=StateUser(value=StateEnum.ACTIVE),
        firebase_uid="supervisor_uid_789"
    )


class TestUserStateChanged:
    """Tests para el evento UserStateChanged."""
    
    def test_event_creation(self):
        """Verifica que el evento se crea correctamente."""
        event_id = uuid.uuid4()
        occurred_at = datetime.now()
        aggregate_id = uuid.uuid4()
        
        event = UserStateChanged(
            event_id=event_id,
            occurred_at=occurred_at,
            aggregate_id=aggregate_id,
            user_identification="12345678",
            user_full_name="Juan Perez",
            user_role="EMPLOYEE",
            previous_state="ACTIVE",
            new_state="INACTIVE",
            changed_by_identification="87654321",
            changed_by_full_name="Maria Garcia",
            changed_by_role="MANAGER",
            reason="Vacaciones"
        )
        
        assert event.event_id == event_id
        assert event.get_event_type() == "UserStateChanged"
        assert event.user_identification == "12345678"
        assert event.new_state == "INACTIVE"
    
    def test_event_log_message_format(self):
        """Verifica el formato del mensaje de log."""
        event = UserStateChanged(
            event_id=uuid.uuid4(),
            occurred_at=datetime(2025, 10, 8, 14, 30, 45),
            aggregate_id=uuid.uuid4(),
            user_identification="12345678",
            user_full_name="Juan Perez",
            user_role="EMPLOYEE",
            previous_state="ACTIVE",
            new_state="INACTIVE",
            changed_by_identification="87654321",
            changed_by_full_name="Maria Garcia",
            changed_by_role="MANAGER",
            reason="Vacaciones"
        )
        
        log_message = event.to_log_message()
        
        assert "USUARIO DESACTIVADO" in log_message
        assert "Juan Perez (12345678)" in log_message
        assert "ACTIVE -> INACTIVE" in log_message
        assert "Maria Garcia (87654321)" in log_message
        assert "Razon: Vacaciones" in log_message


class TestUserDomainEvents:
    """Tests para la generacion de eventos en el modelo User."""
    
    def test_user_deactivate_generates_event(self, employee_user, manager_user):
        """Verifica que desactivar un user genera un evento."""
        employee_user.deactivate(changed_by=manager_user, reason="Test")
        
        events = employee_user.clear_domain_events()
        
        assert len(events) == 1
        assert isinstance(events[0], UserStateChanged)
        assert events[0].user_identification == "12345678"
        assert events[0].new_state == "INACTIVE"
        assert events[0].changed_by_identification == "87654321"
    
    def test_user_activate_generates_event(self, employee_user, manager_user):
        """Verifica que activar un user genera un evento."""
        # Primero desactivar
        employee_user.deactivate(changed_by=manager_user)
        employee_user.clear_domain_events()  # Limpiar eventos
        
        # Ahora activar
        employee_user.activate(changed_by=manager_user, reason="Regreso de vacaciones")
        
        events = employee_user.clear_domain_events()
        
        assert len(events) == 1
        assert isinstance(events[0], UserStateChanged)
        assert events[0].new_state == "ACTIVE"
        assert events[0].reason == "Regreso de vacaciones"
    
    def test_clear_domain_events_empties_list(self, employee_user, manager_user):
        """Verifica que clear_domain_events vacia la lista."""
        employee_user.deactivate(changed_by=manager_user)
        
        events = employee_user.clear_domain_events()
        assert len(events) == 1
        
        events_again = employee_user.clear_domain_events()
        assert len(events_again) == 0


class TestDeactivateUserUseCase:
    """Tests para el caso de uso DeactivateUser."""
    
    def test_deactivate_employee_success(self, employee_user, manager_user):
        """Verifica desactivacion exitosa de un empleado."""
        mock_repo = Mock()
        mock_repo.get_by_identification_number.side_effect = [manager_user, employee_user]
        mock_repo.update.return_value = employee_user
        
        use_case = DeactivateUser(mock_repo)
        
        with patch('app.application.event_handlers.DomainEventDispatcher.dispatch_events'):
            result = use_case.execute(
                target_user_identification=employee_user.identification_number,
                admin_user_identification=manager_user.identification_number,
                reason="Test reason"
            )
        
        assert result.state.value == StateEnum.INACTIVE
        mock_repo.update.assert_called_once()
    
    def test_deactivate_supervisor_success(self, supervisor_user, manager_user):
        """Verifica desactivacion exitosa de un supervisor."""
        mock_repo = Mock()
        mock_repo.get_by_identification_number.side_effect = [manager_user, supervisor_user]
        mock_repo.update.return_value = supervisor_user
        
        use_case = DeactivateUser(mock_repo)
        
        with patch('app.application.event_handlers.DomainEventDispatcher.dispatch_events'):
            result = use_case.execute(
                target_user_identification=supervisor_user.identification_number,
                admin_user_identification=manager_user.identification_number
            )
        
        assert result.state.value == StateEnum.INACTIVE
    
    def test_deactivate_fails_without_permissions(self, employee_user):
        """Verifica que un empleado no puede desactivar users."""
        another_employee = User(
            identification_number=DocumentNumber(value="99999999", doc_type=DocumentEnum.CC),
            role=RoleEnum.EMPLOYEE,
            first_name="Pedro",
            last_name="Gomez",
            email=Email(value="pedro.gomez@example.com"),
            state=StateUser(value=StateEnum.ACTIVE),
            firebase_uid="employee_uid_999"
        )
        
        mock_repo = Mock()
        mock_repo.get_by_identification_number.side_effect = [another_employee, employee_user]
        
        use_case = DeactivateUser(mock_repo)
        
        with pytest.raises(Exception) as exc_info:
            use_case.execute(
                target_user_identification=employee_user.identification_number,
                admin_user_identification=another_employee.identification_number
            )
        
        assert "No tiene permisos" in str(exc_info.value.detail)


class TestActivateUserUseCase:
    """Tests para el caso de uso ActivateUser."""
    
    def test_activate_employee_success(self, employee_user, manager_user):
        """Verifica activacion exitosa de un empleado."""
        # Desactivar primero
        employee_user.deactivate(changed_by=manager_user)
        employee_user.clear_domain_events()
        
        mock_repo = Mock()
        mock_repo.get_by_identification_number.side_effect = [manager_user, employee_user]
        mock_repo.update.return_value = employee_user
        
        use_case = ActivateUser(mock_repo)
        
        with patch('app.application.event_handlers.DomainEventDispatcher.dispatch_events'):
            result = use_case.execute(
                target_user_identification=employee_user.identification_number,
                admin_user_identification=manager_user.identification_number,
                reason="Regreso"
            )
        
        assert result.state.value == StateEnum.ACTIVE
        mock_repo.update.assert_called_once()


class TestUserStateChangedHandler:
    """Tests para el handler de eventos."""
    
    @patch('app.application.event_handlers.audit_logger')
    def test_handler_writes_to_audit_log(self, mock_audit_logger):
        """Verifica que el handler escribe en el log de auditoria."""
        event = UserStateChanged(
            event_id=uuid.uuid4(),
            occurred_at=datetime.now(),
            aggregate_id=uuid.uuid4(),
            user_identification="12345678",
            user_full_name="Juan Perez",
            user_role="EMPLOYEE",
            previous_state="ACTIVE",
            new_state="INACTIVE",
            changed_by_identification="87654321",
            changed_by_full_name="Maria Garcia",
            changed_by_role="MANAGER",
            reason="Test"
        )
        
        UserStateChangedHandler.handle(event)
        
        mock_audit_logger.info.assert_called_once()
        call_args = mock_audit_logger.info.call_args[0][0]
        assert "USUARIO DESACTIVADO" in call_args
        assert "Juan Perez" in call_args
