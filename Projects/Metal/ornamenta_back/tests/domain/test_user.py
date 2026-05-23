import uuid

from app.domain.models.user import RoleEnum, User
from app.domain.permissions import Permission
from app.domain.value_objects.document_number import DocumentEnum, DocumentNumber
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateEnum, StateUser


def make_user(role=RoleEnum.EMPLOYEE, state=StateEnum.INACTIVE) -> User:
    """Factory helper para create un user de prueba."""
    return User(
        identification_number=DocumentNumber(
            value="1234567890", doc_type=DocumentEnum.CC
        ),
        role=role,
        first_name="Ana",
        last_name="Lopez",
        email=Email(value="ana@example.com"),
        state=StateUser(value=state),
        firebase_uid=uuid.uuid4(),
    )


def test_full_name():
    user = make_user()
    assert user.full_name == "Ana Lopez"


def test_user_activation():
    user = make_user(state=StateEnum.INACTIVE)
    manager = make_user(role=RoleEnum.MANAGER, state=StateEnum.ACTIVE)
    assert not user.is_active

    user.activate(changed_by=manager, reason="Test activation")
    assert user.is_active
    
    # Verificar que se genero el evento
    events = user.clear_domain_events()
    assert len(events) == 1


def test_employee_permissions():
    user = make_user(role=RoleEnum.EMPLOYEE)
    assert user.has_permission(Permission.VIEW_TASKS)
    assert not user.has_permission(Permission.MANAGE_USERS)


def test_user_change_role():
    user = make_user(role=RoleEnum.EMPLOYEE)
    assert user.role == RoleEnum.EMPLOYEE

    user.change_role(RoleEnum.MANAGER)
    assert user.role == RoleEnum.MANAGER


def test_manager_permissions():
    user = make_user(role=RoleEnum.MANAGER)
    assert user.has_permission(Permission.APPROVE_TASKS)
    assert not user.has_permission(Permission.MANAGE_USERS)


def test_user_can_create_roles():
    """Test que verifica quien puede create users con diferentes roles."""
    # SUPER_ADMIN puede create MANAGER, SUPERVISOR y EMPLOYEE
    super_admin = make_user(role=RoleEnum.SUPER_ADMIN)
    assert super_admin.can_create_user_with_role(RoleEnum.MANAGER)
    assert super_admin.can_create_user_with_role(RoleEnum.SUPERVISOR)
    assert super_admin.can_create_user_with_role(RoleEnum.EMPLOYEE)
    assert not super_admin.can_create_user_with_role(RoleEnum.SUPER_ADMIN)
    
    # MANAGER puede create MANAGER, SUPERVISOR y EMPLOYEE
    manager = make_user(role=RoleEnum.MANAGER)
    assert manager.can_create_user_with_role(RoleEnum.MANAGER)
    assert manager.can_create_user_with_role(RoleEnum.SUPERVISOR)
    assert manager.can_create_user_with_role(RoleEnum.EMPLOYEE)
    assert not manager.can_create_user_with_role(RoleEnum.SUPER_ADMIN)
    
    # SUPERVISOR no puede create users
    supervisor = make_user(role=RoleEnum.SUPERVISOR)
    assert not supervisor.can_create_user_with_role(RoleEnum.MANAGER)
    assert not supervisor.can_create_user_with_role(RoleEnum.SUPERVISOR)
    assert not supervisor.can_create_user_with_role(RoleEnum.EMPLOYEE)
    assert not supervisor.can_create_user_with_role(RoleEnum.SUPER_ADMIN)
    
    # EMPLOYEE no puede create users
    employee = make_user(role=RoleEnum.EMPLOYEE)
    assert not employee.can_create_user_with_role(RoleEnum.MANAGER)
    assert not employee.can_create_user_with_role(RoleEnum.SUPERVISOR)
    assert not employee.can_create_user_with_role(RoleEnum.EMPLOYEE)
    assert not employee.can_create_user_with_role(RoleEnum.SUPER_ADMIN)
