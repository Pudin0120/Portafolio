from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

# Remove circular imports by using TYPE_CHECKING and strings for annotations if needed,
# or just ensure imports are correct.

from app.domain.models.user import RoleEnum
from app.domain.value_objects.document_number import DocumentNumber
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateUser

if TYPE_CHECKING:
    from app.domain.models.user import User
from app.infrastructure.adapters.db.models.user_model import User as UserModel # Tu modelo de DB

class UserRepository(ABC):

    @abstractmethod
    def get_by_firebase_uid(self, firebase_uid: str) -> Optional[User]:
        """Obtiene un user por su Firebase UID."""
        pass

    @abstractmethod
    def get_by_email(self, email: Email) -> Optional[User]:
        """Obtiene un user por su email.

        Args:
            email (Email): Direccion de email del user.

        Returns:
            Optional[User]: User encontrado o None si no existe.
        """
        pass

    @abstractmethod #  Debe ser abstracto
    def get_by_role(self, role: RoleEnum) -> List[User]:
        """
        Obtiene todos los users que tienen un rol especifico.
        """
        pass

    @abstractmethod
    def get_all_except_super_admin(self) -> List[User]:
        """
        Obtiene todos los users excepto los SUPER_ADMIN.
        """
        pass

    @abstractmethod
    def create_user(
        self,
        firebase_uid: str,
        email: Email,
        role: RoleEnum,
        document_number: DocumentNumber,
        state: StateUser,
        first_name: str,
        last_name: str,
        tenant_id: Optional[UUID] = None,
        phone: Optional[str] = None,
    ) -> User:
        """Crea un nuevo user con los valores especificados.

        Args:
            firebase_uid (str): Identificador unico del user en Firebase.
            email (Email): Direccion de email del user.
            role (RoleEnum): Rol asignado al user.
            document_number (DocumentNumber): Number de document del user.
            state (StateUser): Estado del user.
            first_name (str): Nombre del user.
            last_name (str): Apellido del user.
            tenant_id (Optional[UUID]): ID del tenant.
            phone (Optional[str]): Telefono del user.

        Returns:
            User: User creado.
        """
        pass

    @abstractmethod
    def get_by_identification_number(self, identification_number: str) -> Optional[User]:
        """Obtiene un user por su number de identificacion."""
        pass

    @abstractmethod
    def update_user_state(self, identification_number: str, new_state: StateUser) -> User:
        """Actualiza el estado de un user."""
        pass

    @abstractmethod
    def update_user(
        self,
        identification_number: str,
        first_name: str,
        last_name: str,
        phone: Optional[str],
        role: RoleEnum,
    ) -> User:
        """Actualiza los datos de un user (excepto email y document)."""
        pass
