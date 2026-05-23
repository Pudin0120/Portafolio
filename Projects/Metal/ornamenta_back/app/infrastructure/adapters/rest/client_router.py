"""
REST API endpoints for clients.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.domain.models.user import User
from app.application.dto.client_dto import (
    ClientDTO,
    ClientCreateDTO,
    ClientUpdateDTO,
    ClientListDTO
)
from app.application.mappers.client_mapper import ClientMapper
from app.application.use_cases.create_client import CreateClient
from app.application.use_cases.update_client import UpdateClient
from app.application.use_cases.get_client import GetClient
from app.infrastructure.adapters.rest.dependencies import get_current_user
from app.infrastructure.adapters.db.database import get_db_session
from app.infrastructure.adapters.repositories.postgres_client_repository import PostgresClientRepository
from app.domain.value_objects.document_number import DocumentNumber, DocumentEnum


router = APIRouter(
    prefix="/clients",
    tags=["Clients"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/", response_model=ClientDTO, status_code=status.HTTP_201_CREATED)
def create_client(
    client_data: ClientCreateDTO,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Crea un nuevo client.
    
    Requiere autenticacion.
    
    Args:
        client_data: Datos del client a create
        
    Returns:
        Client creado
    """
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have a tenant assigned"
        )

    client_repo = PostgresClientRepository(db_session)
    
    use_case = CreateClient(client_repository=client_repo)
    client = use_case.execute(client_data, current_user.tenant_id)
    return ClientMapper.to_dto(client)


@router.get("/", response_model=ClientListDTO)
def list_clients(
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Lista todos los clients.
    
    Returns:
        Lista de clients
    """
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have a tenant assigned"
        )

    client_repo = PostgresClientRepository(db_session)
    
    use_case = GetClient(client_repository=client_repo)
    clients = use_case.execute_all(current_user.tenant_id)
    return ClientMapper.to_dto_list(clients)


@router.get("/{identification}", response_model=ClientDTO)
def get_client(
    identification: str,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Obtiene un client por su number de identificacion.
    
    Args:
        identification: Number de identificacion del client
        
    Returns:
        Client encontrado
    """
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have a tenant assigned"
        )

    client_repo = PostgresClientRepository(db_session)
    
    use_case = GetClient(client_repository=client_repo)
    client = use_case.execute_by_identification(identification, current_user.tenant_id)
    return ClientMapper.to_dto(client)


@router.patch("/{identification}", response_model=ClientDTO)
def update_client(
    identification: str,
    client_data: ClientUpdateDTO,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Actualiza un client existente.
    
    Args:
        identification: Number de identificacion del client
        client_data: Datos a actualizar (campos opcionales)
        
    Returns:
        Client actualizado
    """
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have a tenant assigned"
        )

    client_repo = PostgresClientRepository(db_session)
    
    use_case = UpdateClient(client_repository=client_repo)
    client = use_case.execute(identification, client_data, current_user.tenant_id)
    return ClientMapper.to_dto(client)


@router.delete("/{identification}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    identification: str,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Elimina un client.
    
    Solo MANAGER puede delete clients.
    
    Args:
        identification: Number de identificacion del client
    """
    from app.domain.models.user import RoleEnum
    
    # Validate permissions
    if current_user.role != RoleEnum.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo MANAGER puede delete clients"
        )

    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have a tenant assigned"
        )
    
    # Create repository with the same session
    client_repo = PostgresClientRepository(db_session)
    
    # Delete client
    success = client_repo.delete(
        DocumentNumber(value=identification, doc_type=DocumentEnum.CC),
        current_user.tenant_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client con identificacion {identification} no encontrado"
        )
