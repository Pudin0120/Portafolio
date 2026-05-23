from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List
from uuid import UUID

from app.domain.permissions import ROLE_PERMISSIONS, Permission
from app.domain.value_objects.document_number import DocumentNumber
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateUser
from app.domain.domain_event import DomainEvent


class RoleEnum(str, Enum):
    """Roles disponibles"""

    SUPER_ADMIN = "SUPER_ADMIN"
    MANAGER = "MANAGER"
    SUPERVISOR = "SUPERVISOR"
    EMPLOYEE = "EMPLOYEE"


@dataclass
class User:
    """Modelo de dominio para user."""

    identification_number: DocumentNumber
    role: RoleEnum
    first_name: str
    last_name: str
    email: Email
    state: StateUser
    firebase_uid: str
    id: Optional[UUID] = None
    tenant_id: Optional[UUID] = None
    phone: Optional[str] = None
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False, repr=False)

    @property
    def full_name(self) -> str:
        """Retorna el nombre completo del user."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_active(self) -> bool:
        """Verifica si el user esta active."""
        return self.state.is_active

    def change_role(self, new_role: RoleEnum) -> None:
        """Cambia el rol del user."""

        self.role = new_role

    def activate(self, changed_by: 'User', reason: str = "") -> None:
        """
        Activa el user y registra el evento de dominio.
        
        Args:
            changed_by: User que ejecuta la activacion (debe ser MANAGER o SUPER_ADMIN)
            reason: Razon opcional del cambio
        """
        from datetime import datetime
        import uuid
        from app.domain.events.user_events import UserStateChanged
        
        previous_state = self.state.value.name  # Obtiene "ACTIVE" o "INACTIVE"
        self.state = self.state.activate()
        
        # Generar evento de dominio
        event = UserStateChanged(
            event_id=uuid.uuid4(),
            occurred_at=datetime.now(),
            aggregate_id=uuid.uuid4(),  # Podrias usar hash del identification_number
            user_identification=str(self.identification_number),
            user_full_name=self.full_name,
            user_role=self.role.value,
            previous_state=previous_state,
            new_state=self.state.value.name,  # Obtiene "ACTIVE" o "INACTIVE"
            changed_by_identification=str(changed_by.identification_number),
            changed_by_full_name=changed_by.full_name,
            changed_by_role=changed_by.role.value,
            reason=reason
        )
        self._domain_events.append(event)

    def deactivate(self, changed_by: 'User', reason: str = "") -> None:
        """
        Desactiva el user y registra el evento de dominio.
        
        Args:
            changed_by: User que ejecuta la desactivacion (debe ser MANAGER o SUPER_ADMIN)
            reason: Razon opcional del cambio
        """
        from datetime import datetime
        import uuid
        from app.domain.events.user_events import UserStateChanged
        
        previous_state = self.state.value.name  # Obtiene "ACTIVE" o "INACTIVE"
        self.state = self.state.deactivate()
        
        # Generar evento de dominio
        event = UserStateChanged(
            event_id=uuid.uuid4(),
            occurred_at=datetime.now(),
            aggregate_id=uuid.uuid4(),
            user_identification=str(self.identification_number),
            user_full_name=self.full_name,
            user_role=self.role.value,
            previous_state=previous_state,
            new_state=self.state.value.name,  # Obtiene "ACTIVE" o "INACTIVE"
            changed_by_identification=str(changed_by.identification_number),
            changed_by_full_name=changed_by.full_name,
            changed_by_role=changed_by.role.value,
            reason=reason
        )
        self._domain_events.append(event)

    def clear_domain_events(self) -> List[DomainEvent]:
        """Retorna y limpia los eventos de dominio acumulados."""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

    def has_permission(self, permission: Permission) -> bool:
        """Verifica si el user tiene un permiso especifico."""
        role_permissions = ROLE_PERMISSIONS.get(self.role.value, [])
        return permission in role_permissions

    def can_create_user_with_role(self, target_role: RoleEnum) -> bool:
        """
        Verifica si el user puede create otro user con el rol especificado.
        
        Reglas de negocio:
        - SUPER_ADMIN: puede create MANAGER, SUPERVISOR y EMPLOYEE (NO puede create otro SUPER_ADMIN)
        - MANAGER: puede create MANAGER, SUPERVISOR y EMPLOYEE (NO puede create SUPER_ADMIN)
        - SUPERVISOR y EMPLOYEE: NO pueden create users
        
        Args:
            target_role: Rol del user que se desea create
            
        Returns:
            bool: True si tiene permiso, False en caso contrario
        """
        # SUPER_ADMIN puede create MANAGER, SUPERVISOR y EMPLOYEE
        if self.role == RoleEnum.SUPER_ADMIN:
            return target_role in [RoleEnum.MANAGER, RoleEnum.SUPERVISOR, RoleEnum.EMPLOYEE]
        
        # MANAGER puede create MANAGER, SUPERVISOR y EMPLOYEE
        if self.role == RoleEnum.MANAGER:
            return target_role in [RoleEnum.MANAGER, RoleEnum.SUPERVISOR, RoleEnum.EMPLOYEE]
        
        # SUPERVISOR y EMPLOYEE no pueden create users
        return False
