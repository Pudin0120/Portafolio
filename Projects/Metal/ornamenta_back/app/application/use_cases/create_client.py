"""
Use case para create un client.
"""
from fastapi import HTTPException, status
from uuid import UUID

from app.domain.models.client import Client
from app.domain.repositories.client_repository import ClientRepository
from app.application.dto.client_dto import ClientCreateDTO
from app.application.mappers.client_mapper import ClientMapper


class CreateClient:
    """Use case para create un nuevo client."""

    def __init__(self, client_repository: ClientRepository):
        self.client_repository = client_repository

    def execute(self, request: ClientCreateDTO, tenant_id: UUID) -> Client:
        """
        Crea un nuevo client en el sistema.
        
        Args:
            request: DTO con datos del client a create
            
        Returns:
            Client creado
            
        Raises:
            HTTPException: Si el client ya existe (409 Conflict)
        """
        # Check if client already exists by identification
        client_domain = ClientMapper.to_domain(request)
        client_domain.tenant_id = tenant_id
        
        existing_by_identification = self.client_repository.get_by_identification(
            client_domain.identification_number,
            tenant_id
        )
        if existing_by_identification:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un client con identificacion {request.identification_number}"
            )
        
        # Check if email already exists
        existing_by_email = self.client_repository.get_by_email(client_domain.email, tenant_id)
        if existing_by_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un client con el email {request.email}"
            )
        
        # Save client
        saved_client = self.client_repository.save(client_domain)
        return saved_client
