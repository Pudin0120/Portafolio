"""
Use case para actualizar un client.
"""
from fastapi import HTTPException, status
from uuid import UUID

from app.domain.models.client import Client
from app.domain.repositories.client_repository import ClientRepository
from app.domain.value_objects.document_number import DocumentNumber, DocumentEnum
from app.domain.value_objects.email import Email
from app.application.dto.client_dto import ClientUpdateDTO


class UpdateClient:
    """Use case para actualizar un client existente."""

    def __init__(self, client_repository: ClientRepository):
        self.client_repository = client_repository

    def execute(self, identification: str, request: ClientUpdateDTO, tenant_id: UUID) -> Client:
        """
        Actualiza un client existente.
        
        Args:
            identification: Number de identificacion del client
            request: DTO con datos a actualizar (campos opcionales)
            
        Returns:
            Client actualizado
            
        Raises:
            HTTPException: Si el client no existe (404) o el email ya esta en uso (409)
        """
        # Get existing client
        client = self.client_repository.get_by_identification(
            DocumentNumber(value=identification, doc_type=DocumentEnum.CC),
            tenant_id
        )
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client con identificacion {identification} no encontrado"
            )
        
        # Update fields if provided
        if request.first_name is not None:
            client.first_name = request.first_name
        
        if request.last_name is not None:
            client.last_name = request.last_name
        
        if request.email is not None:
            # Check if new email is already in use by another client
            new_email = Email(value=request.email)
            existing_with_email = self.client_repository.get_by_email(new_email, tenant_id)
            if existing_with_email and existing_with_email.identification_number.value != identification:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"El email {request.email} ya esta en uso por otro client"
                )
            client.email = new_email
        
        if request.phone is not None:
            client.phone = request.phone
        
        if request.address is not None:
            client.address = request.address
        
        # Save updated client
        updated_client = self.client_repository.save(client)
        return updated_client
