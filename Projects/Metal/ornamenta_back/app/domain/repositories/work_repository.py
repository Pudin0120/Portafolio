"""
Repositorio abstracto para la entidad Work.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.models.work import Work
from app.domain.value_objects.document_number import DocumentNumber
from app.domain.value_objects.work_state import WorkStateEnum


class WorkRepository(ABC):
    """Repositorio abstracto para la entidad Work (Aggregate Root)."""

    @abstractmethod
    def save(self, work: Work) -> Work:
        """
        Guarda o actualiza un work en el repositorio.
        
        Persiste el work junto con sus products y tasks asociadas.
        
        Args:
            work: Work a save
            
        Returns:
            Work guardado con datos actualizados
        """
        pass

    @abstractmethod
    def get_by_id(self, work_id: UUID) -> Optional[Work]:
        """
        Obtiene un work por su ID.
        
        Carga el work completo con products, tasks y snapshots.
        
        Args:
            work_id: ID del work
            
        Returns:
            Work encontrado o None si no existe
        """
        pass

    @abstractmethod
    def get_all(self) -> List[Work]:
        """
        Gets all works.
        
        Returns:
            Lista de todos los works
        """
        pass

    @abstractmethod
    def get_by_state(self, state: WorkStateEnum) -> List[Work]:
        """
        Gets all works en un estado especifico.
        
        Args:
            state: Estado del work (DRAFT, QUOTED, IN_PROGRESS, DELIVERED)
            
        Returns:
            Lista de works en el estado especificado
        """
        pass

    @abstractmethod
    def get_by_client(self, client_identification: DocumentNumber) -> List[Work]:
        """
        Gets all works de un client especifico.
        
        Args:
            client_identification: Number de identificacion del client
            
        Returns:
            Lista de works del client
        """
        pass

    @abstractmethod
    def delete(self, work_id: UUID) -> bool:
        """
        Elimina un work por su ID.
        
        Elimina el work y todos sus datos asociados (products, tasks) en cascada.
        
        Args:
            work_id: ID del work
            
        Returns:
            True si se elimino correctamente, False si no existia
        """
        pass

