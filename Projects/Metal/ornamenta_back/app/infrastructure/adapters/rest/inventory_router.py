"""
REST API endpoints for Inventory management.
"""

from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.models.user import User, RoleEnum
from app.infrastructure.adapters.rest.authorization import get_current_user
from app.application.dto.inventory_dto import InventoryMovementCreateDTO, InventoryMovementDTO, InventoryLevelDTO
from app.application.services.inventory_service import InventoryService
from app.infrastructure.dependencies.inventory_dependencies import get_inventory_service
from app.domain.repositories.inventory_repository import InventoryRepository
from app.infrastructure.dependencies.inventory_dependencies import get_inventory_repository

from app.application.mappers.inventory_mapper import InventoryMapper

router = APIRouter(
    prefix="/inventory", 
    tags=["Inventory"], 
    dependencies=[Depends(get_current_user)]
)

@router.post("/movements", response_model=InventoryMovementDTO, status_code=status.HTTP_201_CREATED)
def register_movement(
    movement_data: InventoryMovementCreateDTO,
    current_user: User = Depends(get_current_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
) -> InventoryMovementDTO:
    """
    Register a new inventory movement (PURCHASE, SALE, etc.).
    
    This operation is atomic: it creates the movement record (Kardex) 
    and updates the current stock level for the material.
    """
    if current_user.tenant_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User must belong to a tenant")
    if current_user.role not in [RoleEnum.MANAGER, RoleEnum.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only MANAGER or SUPERVISOR can register inventory movements"
        )

    try:
        movement = inventory_service.register_movement(
            material_id=movement_data.material_id,
            quantity=movement_data.quantity,
            movement_type=movement_data.type,
            tenant_id=current_user.tenant_id,
            reference_id=movement_data.reference_id,
            batch_number=movement_data.batch_number,
            reason=movement_data.reason,
            warehouse_id=movement_data.warehouse_id,
            user_id=current_user.id,
            created_at=movement_data.created_at
        )
        return InventoryMapper.to_movement_dto(movement)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/levels/{material_id}", response_model=InventoryLevelDTO)
def get_inventory_level(
    material_id: UUID,
    current_user: User = Depends(get_current_user),
    inventory_repo: InventoryRepository = Depends(get_inventory_repository)
) -> InventoryLevelDTO:
    """
    Get the current inventory level for a specific material.
    """
    if current_user.tenant_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User must belong to a tenant")

    level = inventory_repo.get_level(material_id, tenant_id=current_user.tenant_id)
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Inventory level not found for this material"
        )
    return InventoryMapper.to_level_dto(level)

@router.get("/levels", response_model=List[InventoryLevelDTO])
def get_all_inventory_levels(
    current_user: User = Depends(get_current_user),
    inventory_repo: InventoryRepository = Depends(get_inventory_repository)
) -> List[InventoryLevelDTO]:
    """
    Get all current inventory levels for the tenant.
    Useful for the main Stock/Inventory view.
    """
    if current_user.tenant_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User must belong to a tenant")

    levels = inventory_repo.get_all_levels(tenant_id=current_user.tenant_id)
    return [InventoryMapper.to_level_dto(level) for level in levels]

@router.get("/movements/{material_id}", response_model=List[InventoryMovementDTO])
def get_material_history(
    material_id: UUID,
    current_user: User = Depends(get_current_user),
    inventory_repo: InventoryRepository = Depends(get_inventory_repository)
) -> List[InventoryMovementDTO]:
    """
    Get the movement history (Kardex) for a specific material.
    """
    if current_user.tenant_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User must belong to a tenant")

    movements = inventory_repo.get_movements_by_material(material_id, tenant_id=current_user.tenant_id)
    return [InventoryMapper.to_movement_dto(m) for m in movements]
