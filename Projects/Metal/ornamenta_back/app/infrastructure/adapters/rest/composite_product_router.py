"""
FastAPI router for composite product operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide
from uuid import UUID

from app.application.services.composite_product_service import CompositeProductService
from app.application.dto.composite_product_dto import (
    CompositeDynamicCreateRequest,
    CompositeDimensionsUpdateRequest,
    AddComponentRequest,
    CompositeProductResponse,
    PriceBreakdownResponse
)
from app.application.use_cases.update_composite_dimensions import (
    UpdateCompositeProductDimensionsUseCase,
    UpdateCompositeDimensionsDTO,
)
from app.application.use_cases.create_composite_snapshot import (
    CreateCompositeSnapshotUseCase,
    CreateCompositeSnapshotDTO,
)
from app.application.use_cases.clear_composite_snapshot import (
    ClearCompositeSnapshotUseCase,
    ClearCompositeSnapshotDTO,
)
from app.infrastructure.dependencies.material_dependencies import get_composite_product_service
from app.infrastructure.dependencies.material_dependencies import (
    get_update_composite_dimensions_use_case,
    get_create_composite_snapshot_use_case,
    get_clear_composite_snapshot_use_case,
)
from app.infrastructure.adapters.rest.authorization import get_current_user
from app.domain.models.user import User
from app.domain.value_objects.money import Money


router = APIRouter(
    prefix="/api/products/composite",
    tags=["Composite Products"]
)


@router.post(
    "/",
    response_model=CompositeProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create product compuesto",
    description="""
    Crea un product compuesto a partir de otros products (simples o compuestos).
    
    **Requiere rol MANAGER o SUPER_ADMIN.**
    
    El price total se calcula automaticamente como la suma de los precios
    de todos los componentes (a menos que se especifique price_override).
    
    ## Ejemplo de Request
    
    ```json
    {
        "name": "Caja metalica simple",
        "description": "Caja hecha con 4 laminas 1x1",
        "components": [
            {
                "product_id": "prod-std-1m2",
                "quantity": 4
            }
        ]
    }
    ```
    """
)
async def create_composite_product(
    request: CompositeDynamicCreateRequest,
    current_user: User = Depends(get_current_user),
    service: CompositeProductService = Depends(get_composite_product_service)
):
    """
    Create product compuesto (solo MANAGER/SUPER_ADMIN).
    """
    try:
        # Convertir componentes a formato dict
        price_override = None
        if request.price_override:
            price_override = Money(
                amount=request.price_override.amount,
                currency=request.price_override.currency,
            )

        components = [
            {
                "product_id": comp.product_id,
                "quantity": comp.quantity,
                "relationship": comp.relationship.model_dump() if comp.relationship else None,
            }
            for comp in request.components
        ]
        
        result = service.create_composite_product(
            name=request.name,
            components=components,
            user=current_user,
            description=request.description,
            price_override=price_override,
            properties={"dimensions": request.dimensions},
        )
        return CompositeProductResponse(**result)
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

@router.patch(
    "/{composite_id}/dimensions",
    response_model=CompositeProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar dimensiones de product compuesto",
)
async def update_composite_dimensions(
    composite_id: UUID,
    request: CompositeDimensionsUpdateRequest,
    current_user: User = Depends(get_current_user),
    use_case: UpdateCompositeProductDimensionsUseCase = Depends(get_update_composite_dimensions_use_case),
):
    """Updates parent dimensions and recalculates component values."""
    try:
        updated = use_case.execute(
            UpdateCompositeDimensionsDTO(product_id=composite_id, new_dimensions=request.dimensions),
            current_user,
        )
        return CompositeProductResponse(success=True, product={
            "id": str(updated.id),
            "name": updated.name,
            "dimensions": updated.dimensions,
            "is_snapshot_mode": updated.is_snapshot_mode,
            "components": updated.get_material_composition().get("components", []),
        })
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno: {str(e)}")


@router.post(
    "/{composite_id}/snapshot",
    response_model=CompositeProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Create snapshot de composicion",
)
async def create_composite_snapshot(
    composite_id: UUID,
    current_user: User = Depends(get_current_user),
    use_case: CreateCompositeSnapshotUseCase = Depends(get_create_composite_snapshot_use_case),
):
    """Freezes composite composition for quotation/order consistency."""
    try:
        updated = use_case.execute(CreateCompositeSnapshotDTO(product_id=composite_id), current_user)
        return CompositeProductResponse(success=True, product={
            "id": str(updated.id),
            "name": updated.name,
            "is_snapshot_mode": updated.is_snapshot_mode,
            "composition_snapshot_created_at": updated.composition_snapshot_created_at.isoformat() if updated.composition_snapshot_created_at else None,
        })
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno: {str(e)}")


@router.delete(
    "/{composite_id}/snapshot",
    response_model=CompositeProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete snapshot de composicion",
)
async def clear_composite_snapshot(
    composite_id: UUID,
    current_user: User = Depends(get_current_user),
    use_case: ClearCompositeSnapshotUseCase = Depends(get_clear_composite_snapshot_use_case),
):
    """Returns composite product to dynamic mode."""
    try:
        updated = use_case.execute(ClearCompositeSnapshotDTO(product_id=composite_id), current_user)
        return CompositeProductResponse(success=True, product={
            "id": str(updated.id),
            "name": updated.name,
            "is_snapshot_mode": updated.is_snapshot_mode,
        })
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno: {str(e)}")


@router.post(
    "/{composite_id}/components",
    response_model=CompositeProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Agregar componente a product compuesto",
    description="""
    Agrega un componente a un product compuesto existente.
    
    **Requiere rol MANAGER o SUPER_ADMIN.**
    
    El price total se recalcula automaticamente.
    
    ## Ejemplo de Request
    
    ```json
    {
        "component_product_id": "prod-chapa",
        "quantity": 1
    }
    ```
    """
)
async def add_component(
    composite_id: UUID,
    request: AddComponentRequest,
    current_user: User = Depends(get_current_user),
    service: CompositeProductService = Depends(get_composite_product_service)
):
    """
    Agregar componente a product compuesto (solo MANAGER/SUPER_ADMIN).
    """
    try:
        result = service.add_component_to_composite(
            composite_id=composite_id,
            component_product_id=request.component_product_id,
            quantity=request.quantity,
            user=current_user
        )
        return CompositeProductResponse(**result)
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


@router.delete(
    "/{composite_id}/components/{component_id}",
    response_model=CompositeProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete componente de product compuesto",
    description="""
    Elimina un componente de un product compuesto.
    
    **Requiere rol MANAGER o SUPER_ADMIN.**
    
    El price total se recalcula automaticamente.
    """
)
async def remove_component(
    composite_id: UUID,
    component_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompositeProductService = Depends(get_composite_product_service)
):
    """
    Delete componente de product compuesto (solo MANAGER/SUPER_ADMIN).
    """
    try:
        result = service.remove_component_from_composite(
            composite_id=composite_id,
            component_product_id=component_id,
            user=current_user
        )
        return CompositeProductResponse(**result)
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


@router.get(
    "/{composite_id}/breakdown",
    response_model=PriceBreakdownResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener desglose de precios",
    description="""
    Obtiene el desglose detallado de precios de un product compuesto.
    
    Muestra el price unitario, quantity y subtotal de cada componente,
    ademas del porcentaje que representa del total.
    """
)
async def get_price_breakdown(
    composite_id: UUID,
    service: CompositeProductService = Depends(get_composite_product_service)
):
    """
    Obtener desglose detallado de precios de product compuesto.
    """
    try:
        result = service.get_price_breakdown(composite_id=composite_id)
        return PriceBreakdownResponse(**result)
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
