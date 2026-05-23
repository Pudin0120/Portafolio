"""
FastAPI router for material price operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide
from uuid import UUID

from app.application.services.material_price_service import MaterialPriceUpdateService
from app.application.dto.material_price_dto import (
    MaterialPriceUpdateRequest,
    MaterialPriceUpdateResponse
)
from app.infrastructure.containers import Container
from app.infrastructure.adapters.rest.dependencies import get_current_user
from app.domain.models.user import User


router = APIRouter(
    prefix="/api/materials",
    tags=["Material Price Management"]
)


@router.post(
    "/{material_id}/price",
    response_model=MaterialPriceUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar price de material",
    description="""
    Actualiza el price de un material y propaga el cambio automaticamente
    a todos los products que usan ese material.
    
    **Requiere rol MANAGER o SUPER_ADMIN.**
    
    El sistema:
    1. Actualiza el price del material
    2. Busca todos los products que usan este material
    3. Recalcula automaticamente el price de cada product
    4. Genera eventos de auditoria
    5. Persiste los cambios
    
    ## Ejemplo de Request
    
    ```json
    {
        "new_price_amount": 105000.0,
        "currency": "COP",
        "reason": "Ajuste por inflacion trimestral Q4 2025"
    }
    ```
    
    ## Ejemplo de Response
    
    ```json
    {
        "success": true,
        "material": {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Lamina acero cal 14",
            "old_price": 100000.0,
            "new_price": 105000.0,
            "currency": "COP",
            "price_change_percent": 5.0
        },
        "impact": {
            "products_affected": 15,
            "total_price_change": 750000.0,
            "events_generated": 16
        },
        "event_id": "550e8400-e29b-41d4-a716-446655440000"
    }
    ```
    """
)
@inject
async def update_material_price(
    material_id: UUID,
    request: MaterialPriceUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: MaterialPriceUpdateService = Depends(Provide[Container.material_price_service])
):
    """
    Actualizar price de material (solo MANAGER/SUPER_ADMIN).
    
    Propaga automaticamente los cambios a products dependientes.
    """
    try:
        result = service.update_material_price(
            material_id=material_id,
            new_price_amount=request.new_price_amount,
            user=current_user,
            currency=request.currency,
            reason=request.reason
        )
        return MaterialPriceUpdateResponse(**result)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

