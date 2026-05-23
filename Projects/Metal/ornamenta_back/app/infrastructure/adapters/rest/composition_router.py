"""API router for Composition endpoints."""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.adapters.db.database import get_db_session
from app.infrastructure.adapters.db.repositories.postgresql_composition_repository import PostgreSQLCompositionRepository
from app.application.services.composition_service import CompositionService
from app.application.dto.composition_dto import (
    CompositionCreateDTO,
    CompositionUpdateDTO,
    CompositionDTO,
    CompositionListDTO
)


from app.infrastructure.adapters.rest.authorization import get_current_user
from app.domain.models.user import User


router = APIRouter(
    prefix="/compositions",
    tags=["compositions"]
)


def get_composition_service(db: Session = Depends(get_db_session)) -> CompositionService:
    """
    Dependency to get CompositionService.
    
    NOTE: Now uses get_db_session() for automatic commit/rollback at end of request.
    This ensures atomicity across all operations in the same request.
    """
    repository = PostgreSQLCompositionRepository(db)
    return CompositionService(repository)


@router.post(
    "/",
    response_model=CompositionDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new composition",
    description="Create a new material composition metadata (e.g., Acero galvanizado, Aluminio 6061). Pricing is NOT stored here - it belongs to Material."
)
def create_composition(
    dto: CompositionCreateDTO,
    service: CompositionService = Depends(get_composition_service),
    current_user: User = Depends(get_current_user)
) -> CompositionDTO:
    """
    Create a new material composition (metadata only).
    
    **Important:** Compositions are REUSABLE metadata. Pricing is stored in Materials, not here.
    
    **Examples:**
    
    Steel composition (reusable across laminas, tubos, varillas):
    ```json
    {
      "name": "Acero cold rolled",
      "description": "Acero laminado en frio, superficie lisa grado comercial"
    }
    ```
    
    Non-sheet material:
    ```json
    {
      "name": "Pintura epoxica",
      "description": "Pintura de dos componentes, acabado brillante"
    }
    ```
    """
    try:
        if not current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has no tenant assigned"
            )
        return service.create_composition(dto, current_user.tenant_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=List[CompositionListDTO],
    summary="List all compositions",
    description="Get a list of all material composition metadata (no pricing - that's in Materials)"
)
def list_compositions(
    service: CompositionService = Depends(get_composition_service),
    current_user: User = Depends(get_current_user)
) -> List[CompositionListDTO]:
    """
    Get all compositions.
    
    Returns a list with id, name and description.
    For pricing, check the Materials that use these compositions.
    """
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no tenant assigned"
        )
    return service.get_all_compositions(current_user.tenant_id)


@router.get(
    "/search",
    response_model=List[CompositionListDTO],
    summary="Search compositions by name",
    description="Search for compositions by name pattern (case-insensitive)"
)
def search_compositions(
    q: str,
    service: CompositionService = Depends(get_composition_service),
    current_user: User = Depends(get_current_user)
) -> List[CompositionListDTO]:
    """
    Search compositions by name pattern.
    
    Args:
        q: Search query (case-insensitive)
    
    Example: `/compositions/search?q=acero` will find "Acero galvanizado", "Acero inoxidable 304", etc.
    """
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no tenant assigned"
        )
    return service.search_compositions(q, current_user.tenant_id)


@router.get(
    "/{composition_id}",
    response_model=CompositionDTO,
    summary="Get composition by ID",
    description="Retrieve detailed information about a specific composition"
)
def get_composition(
    composition_id: UUID,
    service: CompositionService = Depends(get_composition_service),
    current_user: User = Depends(get_current_user)
) -> CompositionDTO:
    """
    Get composition by ID.
    
    Returns full composition details.
    For pricing and material-specific metadata, check the Materials that use this composition.
    """
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no tenant assigned"
        )
    composition = service.get_composition(composition_id, current_user.tenant_id)
    if not composition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Composition with id {composition_id} not found"
        )
    return composition


@router.put(
    "/{composition_id}",
    response_model=CompositionDTO,
    summary="Update composition",
    description="Update an existing composition metadata"
)
def update_composition(
    composition_id: UUID,
    dto: CompositionUpdateDTO,
    service: CompositionService = Depends(get_composition_service),
    current_user: User = Depends(get_current_user)
) -> CompositionDTO:
    """
    Update composition metadata.
    
    Only provided fields will be updated.
    Remember: Pricing is NOT in Composition, it's in Material.
    
    Example request:
    ```json
    {
      "description": "Acero galvanizado grado G90 - calidad premium con acabado spangled"
    }
    ```
    """
    try:
        if not current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has no tenant assigned"
            )
        return service.update_composition(composition_id, dto, current_user.tenant_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete(
    "/{composition_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete composition",
    description="Delete a composition (only if not in use by materials)"
)
def delete_composition(
    composition_id: UUID,
    service: CompositionService = Depends(get_composition_service),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Delete composition.
    
    Will fail if the composition is in use by any materials.
    """
    try:
        if not current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has no tenant assigned"
            )
        service.delete_composition(composition_id, current_user.tenant_id)
        return {"message": "Composition deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
