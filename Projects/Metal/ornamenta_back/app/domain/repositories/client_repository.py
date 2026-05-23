"""
Repositorio abstracto para la entidad Client.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.models.client import Client
from app.domain.value_objects.document_number import DocumentNumber
from app.domain.value_objects.email import Email


class ClientRepository(ABC):
    """Repositorio abstracto para la entidad Client."""

    @abstractmethod
    def save(self, client: Client) -> Client:
        """
        Guarda o actualiza un client en el repositorio.
        
        Args:
            client: Client a save
            
        Returns:
            Client guardado con datos actualizados
        """
        pass

    @abstractmethod
    def get_by_identification(self, identification: DocumentNumber, tenant_id: UUID) -> Optional[Client]:
        """
        Obtiene un client por su number de identificacion.
        
        Args:
            identification: Number de identificacion del client
            
        Returns:
            Client encontrado o None si no existe
        """
        pass

    @abstractmethod
    def get_by_email(self, email: Email, tenant_id: UUID) -> Optional[Client]:
        """
        Obtiene un client por su email.
        
        Args:
            email: Email del client
            
        Returns:
            Client encontrado o None si no existe
        """
        pass

    @abstractmethod
    def get_all(self, tenant_id: UUID) -> List[Client]:
        """
        Obtiene todos los clients.
        
        Returns:
            Lista de todos los clients
        """
        pass

    @abstractmethod
    def delete(self, identification: DocumentNumber, tenant_id: UUID) -> bool:
        """
        Elimina un client por su number de identificacion.
        
        Args:
            identification: Number de identificacion del client
            
        Returns:
            True si se elimino correctamente, False si no existia
        """
        pass
