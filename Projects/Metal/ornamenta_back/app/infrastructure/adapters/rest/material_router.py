"""
REST API endpoints for materials.
"""

from typing import Optional, Union
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dto.material_dto import (
    MaterialDTO,
    MaterialListDTO,
    MaterialCreateDTO,
    MaterialUpdateDTO,
    MaterialUpdateResponseDTO,
)
from app.application.mappers.material_mapper import MaterialMapper
from app.application.serializers.property_serializer import (
    PropertyDeserializer,
    PropertySerializer,
)
from app.domain.models.material import Material
from app.domain.value_objects.money import Money
from app.domain.models.user import User
from app.domain.repositories.material_repository import MaterialRepository
from app.infrastructure.adapters.rest.authorization import get_current_user
from app.infrastructure.adapters.db.database import get_db_session
from app.infrastructure.adapters.repositories.postgres_material_repository import (
    PostgresMaterialRepository,
)
from app.infrastructure.adapters.repositories.postgres_material_type_repository import (
    PostgresMaterialTypeRepository,
)
from app.infrastructure.adapters.repositories.postgres_unit_of_measure_repository import (
    PostgresUnitOfMeasureRepository,
)

from app.application.services.inventory_service import InventoryService
from app.infrastructure.dependencies.inventory_dependencies import get_inventory_service
from sqlalchemy.orm import Session
from app.infrastructure.dependencies.material_dependencies import (
    get_create_material_use_case,
    get_update_material_use_case,
    get_material_repository,
)
from app.application.use_cases.create_material import CreateMaterialUseCase
from app.application.use_cases.update_material import UpdateMaterialUseCase

router = APIRouter(
    prefix="/materials", tags=["Materials"], dependencies=[Depends(get_current_user)]
)


# Helper functions for property normalization


@router.get("/", response_model=MaterialListDTO)
def list_materials(
    material_type_id: Optional[UUID] = None,
    strategy: Optional[str] = None,
    include_deleted: bool = False,
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    material_repo: MaterialRepository = Depends(get_material_repository),
    db: Session = Depends(get_db_session),
) -> MaterialListDTO:
    """
    List all materials with pagination.

    Optional filters:
    - material_type_id: Filter by material type
    - strategy: Filter by measurement strategy (sheet, profile, liquid, solid)
    - include_deleted: If true, includes soft-deleted materials
    - limit: Maximum number of materials to return (default: 10)
    - offset: Number of materials to skip (default: 0)
    """

    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have a tenant assigned"
        )

    # TODO: If material_repo doesn't support include_deleted yet, we might need to filter manually
    # or update the repository. Assuming repository handles it if parameter is passed.
    
    if material_type_id:
        materials = material_repo.get_by_material_type(
            material_type_id, tenant_id=current_user.tenant_id, limit=limit, offset=offset
        )
        total = material_repo.count_by_material_type(material_type_id, tenant_id=current_user.tenant_id)
    elif strategy:
        materials = material_repo.get_by_strategy(strategy, tenant_id=current_user.tenant_id, limit=limit, offset=offset)
        total = material_repo.count_by_strategy(strategy, tenant_id=current_user.tenant_id)
    else:
        materials = material_repo.get_all(tenant_id=current_user.tenant_id, limit=limit, offset=offset)
        total = material_repo.count_all(tenant_id=current_user.tenant_id)

    # Filter by is_deleted if include_deleted is False (if repo doesn't do it)
    if not include_deleted:
        materials = [m for m in materials if not m.is_deleted]
        # Note: This messes up pagination if filtered here. 
        # Ideally repo should handle it.

    # Return DTO with materials list and total count
    from app.infrastructure.adapters.repositories.postgres_unit_of_measure_repository import PostgresUnitOfMeasureRepository
    
    # We need a unit_repo to resolve calculated values in the mapper
    unit_repo = PostgresUnitOfMeasureRepository(db)

    dto_list = MaterialMapper.to_dto_list(materials, unit_repo)
    dto_list.total = total
    return dto_list


@router.get("/{material_id}", response_model=MaterialDTO)
def get_material(
    material_id: UUID,
    current_user: User = Depends(get_current_user),
    material_repo: MaterialRepository = Depends(get_material_repository),
    db: Session = Depends(get_db_session),
) -> MaterialDTO:
    """Get a specific material by UUID."""
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have a tenant assigned"
        )

    material = material_repo.get_by_id(material_id, tenant_id=current_user.tenant_id)

    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material with ID {material_id} not found",
        )

    from app.infrastructure.adapters.repositories.postgres_unit_of_measure_repository import PostgresUnitOfMeasureRepository
    unit_repo = PostgresUnitOfMeasureRepository(db)
    return MaterialMapper.to_dto(material, unit_repo)


@router.post("/", response_model=MaterialDTO, status_code=status.HTTP_201_CREATED)
def create_material(
    material_data: MaterialCreateDTO,
    current_user: User = Depends(get_current_user),
    create_use_case: CreateMaterialUseCase = Depends(get_create_material_use_case),
) -> MaterialDTO:
    """
    Create a new material and initialize its inventory.

    This endpoint:
    1. Validates material type and composition.
    2. Validates properties based on the measurement strategy (SHEET, PROFILE, etc.).
    3. Generates a unique SKU.
    4. Generates a dynamic full name UNLESS a custom name is provided in the 'name' field.
    5. **Initializes the inventory level at zero for the current tenant.**
    
    Returns the created material details.
    """
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have a tenant assigned"
        )
    try:
        return create_use_case.execute(material_data, current_user.tenant_id)
    except ValueError as e:
        # Business validation errors
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Fallback for unexpected errors
        error_str = str(e).lower()
        if "unique constraint" in error_str or "duplicate key" in error_str:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=f"Conflict: {str(e)}"
            )
        raise


@router.patch(
    "/{material_id}", response_model=Union[MaterialDTO, MaterialUpdateResponseDTO]
)
def update_material(
    material_id: UUID,
    material_data: MaterialUpdateDTO,
    current_user: User = Depends(get_current_user),
    update_use_case: UpdateMaterialUseCase = Depends(get_update_material_use_case),
) -> Union[MaterialDTO, MaterialUpdateResponseDTO]:
    """
    Update an existing material (Partial Update).

    This endpoint allows partial updates. You only need to send the fields you want to change.

    Updatable fields:
    - name: Changes the custom name of the material
    - description: Changes the visible description/notes
    - price_amount: Triggers automatic price recalculation
    - properties: Updates measurements (supports partial updates of properties)

    Properties Partial Update:
    You can send just the specific property you want to change.
    Example: To change only the gauge of a sheet, send:
    ```json
    {
        "properties": {
            "thickness": {"gauge": 16}
        }
    }
    ```
    The system will keep the existing area/dimensions.

    Returns:
        - MaterialDTO: If only name or description updated
        - MaterialUpdateResponseDTO: If price/properties updated (includes impact information)
    """
    try:
        return update_use_case.execute(material_id, material_data, current_user)
    except ValueError as e:
        # Business logic validation errors
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        # Permission denied (e.g. non-manager trying to update price)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        # Infrastructure/Database errors
        error_str = str(e).lower()
        if (
            "unique constraint" in error_str
            or "duplicate key" in error_str
            or "ix_materials_name" in error_str
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A material with this description already exists. "
                f"Try using a different description.",
            )
        # Re-raise unexpected errors
        raise


@router.post("/{material_id}/restore", response_model=MaterialDTO)
def restore_material(
    material_id: UUID,
    current_user: User = Depends(get_current_user),
    material_repo: MaterialRepository = Depends(get_material_repository),
    db: Session = Depends(get_db_session),
):
    """Restore a soft-deleted material."""
    material = material_repo.get_by_id(material_id, tenant_id=current_user.tenant_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material with ID {material_id} not found",
        )
    
    material.restore()
    material_repo.save(material)
    
    from app.infrastructure.adapters.repositories.postgres_unit_of_measure_repository import PostgresUnitOfMeasureRepository
    unit_repo = PostgresUnitOfMeasureRepository(db)
    return MaterialMapper.to_dto(material, unit_repo)


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(
    material_id: UUID,
    current_user: User = Depends(get_current_user),
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    """
    Delete a material (Soft Delete).
    
    Validation:
    - Material must have zero stock to be deleted.
    """
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have a tenant assigned"
        )
        
    try:
        inventory_service.delete_material(material_id, tenant_id=current_user.tenant_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material with ID {material_id} not found",
        )
