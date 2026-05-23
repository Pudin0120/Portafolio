"""
Use case para obtener clients.
"""
from typing import List
from fastapi import HTTPException, status
from uuid import UUID

from app.domain.models.client import Client
from app.domain.repositories.client_repository import ClientRepository
from app.domain.value_objects.document_number import DocumentNumber, DocumentEnum


class GetClient:
    """Use case para obtener clients."""

    def __init__(self, client_repository: ClientRepository):
        self.client_repository = client_repository

    def execute_by_identification(self, identification: str, tenant_id: UUID) -> Client:
        """
        Obtiene un client por su number de identificacion.
        
        Args:
            identification: Number de identificacion del client
            
        Returns:
            Client encontrado
            
        Raises:
            HTTPException: Si el client no existe (404)
        """
        client = self.client_repository.get_by_identification(
            DocumentNumber(value=identification, doc_type=DocumentEnum.CC),
            tenant_id
        )
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client con identificacion {identification} no encontrado"
            )
        
        return client

    def execute_all(self, tenant_id: UUID) -> List[Client]:
        """
        Obtiene todos los clients.
        
        Returns:
            Lista de todos los clients
        """
        return self.client_repository.get_all(tenant_id)
