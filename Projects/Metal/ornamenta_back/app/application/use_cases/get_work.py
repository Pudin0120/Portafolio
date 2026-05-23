"""
Use case para obtener works.
"""
from typing import List
from uuid import UUID
from fastapi import HTTPException, status

from app.domain.models.work import Work
from app.domain.repositories.work_repository import WorkRepository
from app.domain.value_objects.document_number import DocumentNumber
from app.domain.value_objects.work_state import WorkStateEnum


class GetWork:
    """Use case para obtener works."""

    def __init__(self, work_repository: WorkRepository):
        self.work_repository = work_repository

    def execute_by_id(self, work_id: UUID) -> Work:
        """
        Obtiene un work por su ID.
        
        Args:
            work_id: ID del work
            
        Returns:
            Work encontrado
            
        Raises:
            HTTPException: Si el work no existe (404)
        """
        work = self.work_repository.get_by_id(work_id)
        
        if not work:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Work {work_id} no encontrado"
            )
        
        return work

    def execute_all(self) -> List[Work]:
        """
        Gets all works.
        
        Returns:
            Lista de todos los works
        """
        return self.work_repository.get_all()

    def execute_by_state(self, state: WorkStateEnum) -> List[Work]:
        """
        Gets all works en un estado especifico.
        
        Args:
            state: Estado del work
            
        Returns:
            Lista de works en el estado especificado
        """
        return self.work_repository.get_by_state(state)

    def execute_by_client(self, client_identification: str) -> List[Work]:
        """
        Gets all works de un client especifico.
        
        Args:
            client_identification: Number de identificacion del client
            
        Returns:
            Lista de works del client
        """
        return self.work_repository.get_by_client(
            DocumentNumber(value=client_identification)
        )

