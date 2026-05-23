"""
REST API endpoints for products (Composite Pattern).
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependency_injector.wiring import inject, Provide
import uuid
from decimal import Decimal

from app.application.dto.product_dto import (
    ProductDTO,
    ProductListDTO,
    SimpleProductCreateDTO,
    CompositeProductCreateDTO,
    ProductUpdateDTO,
    ProductInstantiationDTO,
    TemplateRequirementDTO,
    MoneyDTO,
    ProductSimulationResultDTO,
    ProductCreateResponseDTO
)
from app.application.dto.product_composition_dto import ProductCompositionDTO
from app.application.mappers.product_mapper import ProductMapper, to_product_composition_dto
from app.domain.models.product import SimpleProduct, CompositeProduct
from app.domain.value_objects.money import Money
from app.application.services.product_creation_service import ProductCreationService
from app.application.services.composite_product_service import CompositeProductService
from app.application.use_cases.simulate_simple_product import SimulateSimpleProductUseCase
from app.application.use_cases.create_simple_product import CreateSimpleProductUseCase
from app.application.use_cases.create_composite_product import CreateCompositeProductUseCase
from app.application.use_cases.update_product import UpdateProductUseCase
from app.infrastructure.dependencies.material_dependencies import (
    get_product_creation_service,
    get_product_repository,
    get_composite_product_service,
    get_material_repository,
    get_create_composite_product_use_case,
    get_update_product_use_case,
    get_template_requirements_use_case,
    get_instantiate_product_use_case,
)
from app.application.use_cases.template_use_cases import (
    GetTemplateRequirementsUseCase,
    InstantiateProductUseCase
)
from app.domain.models.user import User
from app.infrastructure.adapters.rest.authorization import get_current_user
from app.infrastructure.containers import Container
from app.domain.repositories.product_repository import ProductRepository
from app.domain.repositories.material_repository import MaterialRepository
from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=ProductListDTO)
def list_products(
    product_type: Optional[str] = None,
    include_deleted: bool = False,
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    product_repo: ProductRepository = Depends(get_product_repository),
) -> ProductListDTO:
    """
    List all products with pagination.
    
    Optional filters:
    - product_type: Filter by type ('simple' or 'composite')
    - include_deleted: If true, includes soft-deleted products
    - limit: Maximum number of products to return (default: 10)
    - offset: Number of products to skip (default: 0)
    """
    # Get paginated products AND total count
    if product_type == 'simple':
        products = product_repo.get_all_simple(limit=limit, offset=offset, include_deleted=include_deleted)
        total = product_repo.count_simple(include_deleted=include_deleted)
    elif product_type == 'composite':
        products = product_repo.get_all_composite(limit=limit, offset=offset, include_deleted=include_deleted)
        total = product_repo.count_composite(include_deleted=include_deleted)
    else:
        products = product_repo.get_all(limit=limit, offset=offset, include_deleted=include_deleted)
        total = product_repo.count_all(include_deleted=include_deleted)
    
    # Return DTO with products list and total count
    dto_list = ProductMapper.to_dto_list(products)
    dto_list.total = total
    return dto_list


@router.post("/{product_id}/restore", response_model=ProductDTO)
def restore_product(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    product_repo: ProductRepository = Depends(get_product_repository),
) -> ProductDTO:
    """Restore a soft-deleted product."""
    product = product_repo.get_by_id(product_id, include_deleted=True)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    product.restore()
    product_repo.save(product)
    return ProductMapper.to_dto(product)


@router.get("/{product_id}", response_model=ProductDTO)
def get_product_by_id(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    product_repo: ProductRepository = Depends(get_product_repository),
) -> ProductDTO:
    """Get a product by its ID."""
    product = product_repo.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return ProductMapper.to_dto(product)


@router.post("/simple/simulate", response_model=ProductSimulationResultDTO)
def simulate_simple_product(
    product_data: SimpleProductCreateDTO,
    current_user: User = Depends(get_current_user),
    material_repo: MaterialRepository = Depends(get_material_repository),
) -> ProductSimulationResultDTO:
    """
    Simula la creation de un product simple para obtener calculos en tiempo real.
    Util para el frontend cuando el user esta ajustando medidas y materials.
    """
    try:
        use_case = SimulateSimpleProductUseCase(material_repo)
        result = use_case.execute(product_data, current_user)
        return ProductSimulationResultDTO(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        import traceback
        print(f"Error en simulacion: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno en la simulacion")


@router.post("/simple", response_model=ProductCreateResponseDTO, status_code=status.HTTP_201_CREATED)
def create_simple_product(
    product_data: SimpleProductCreateDTO,
    current_user: User = Depends(get_current_user),
    product_creation_service: ProductCreationService = Depends(get_product_creation_service),
) -> ProductCreateResponseDTO:
    """
    Crea un product simple con una receta de materials.
    
    **PRICING LOGIC**:
    - El price se AUTO-CALCULA basado en los materials y dimensiones.
    - No se permiten overrides si hay materials presentes.
    
    **EXAMPLE REQUEST**:
    ```json
    {
      "name": "Puerta Entamborada",
      "materials": [
        {
          "material_id": "UUID-LAMINA",
          "quantity": 1.0
        },
        {
          "material_id": "UUID-MANO-DE-OBRA",
          "quantity": 1.5
        }
      ],
      "dimensions": {
        "width": {"value": 0.9, "unit": "m"},
        "height": {"value": 2.1, "unit": "m"}
      }
    }
    ```
    """
    try:
        use_case = CreateSimpleProductUseCase(product_creation_service)
        return use_case.execute(product_data, current_user)
        
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de validacion: {str(e)}")
    except Exception as e:
        # Log del error para debugging
        import traceback
        print(f"Error creando product: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor.")


@router.post("/composite", response_model=ProductCreateResponseDTO, status_code=status.HTTP_201_CREATED)
def create_composite_product(
    product_data: CompositeProductCreateDTO,
    current_user: User = Depends(get_current_user),
    use_case: CreateCompositeProductUseCase = Depends(get_create_composite_product_use_case),
) -> ProductCreateResponseDTO:
    """
    Create a new composite product.
    
    A composite product is composed of other products (simple or composite).
    Examples: Porton completo, Ventana con marco, Sistema de pintura
    
    Requires:
    - name: Unique product name
    - components: List of {product_id, quantity}
    
    Components will be ordered by the order they appear in the list.
    """
    try:
        return use_case.execute(product_data, current_user)
        
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
        # Importar SQLAlchemy IntegrityError para manejo especifico  
        from sqlalchemy.exc import IntegrityError
        
        # Manejar error de nombre duplicado
        if isinstance(e, IntegrityError) and "duplicate key value violates unique constraint" in str(e):
            if "ix_products_name" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un product con el nombre '{product_data.name}'. Please, usa un nombre diferente."
                )
        
        # Log del error para debugging
        import traceback
        print(f"Error creando product compuesto: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al create el product compuesto."
        )


@router.patch("/{product_id}", response_model=ProductDTO)
def update_product(
    product_id: UUID,
    product_data: ProductUpdateDTO,
    current_user: User = Depends(get_current_user),
    use_case: UpdateProductUseCase = Depends(get_update_product_use_case),
) -> ProductDTO:
    """
    Update an existing product.
    
    **UPDATABLE FIELDS**:
    - `name`: Product name (must be unique)
    - `description`: Product description
    - `dimensions`: Updated dimensions (only for simple products)
    - `components`: Updated components (only for composite products)
    
    Validates measurement strategy and recalculates price automatically.
    """
    try:
        return use_case.execute(product_id, product_data, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Importar SQLAlchemy IntegrityError para manejo especifico  
        from sqlalchemy.exc import IntegrityError
        
        # Manejar error de nombre duplicado
        if isinstance(e, IntegrityError) and "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un product con ese nombre. Please, usa un nombre diferente."
            )
        
        # Log del error para debugging
        import traceback
        print(f"Error actualizando product: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al actualizar el product."
        )



@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    product_repo: ProductRepository = Depends(get_product_repository),
):
    """
    Delete a product.
    
    Note: If this product is used as a component in other products,
    those references will be deleted (CASCADE).
    """
    try:
        success = product_repo.delete(product_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
    except ValueError as e:
        # Handle the case where product is being used in works/quotations
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/templates/{product_id}/requirements", response_model=List[TemplateRequirementDTO])
def get_template_requirements(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    use_case: GetTemplateRequirementsUseCase = Depends(get_template_requirements_use_case),
) -> List[TemplateRequirementDTO]:
    """Get what materials are needed to instantiate this template."""
    try:
        return use_case.execute(product_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/templates/{product_id}/instantiate", response_model=ProductDTO)
def instantiate_product(
    product_id: UUID,
    data: ProductInstantiationDTO,
    current_user: User = Depends(get_current_user),
    use_case: InstantiateProductUseCase = Depends(get_instantiate_product_use_case),
) -> ProductDTO:
    """Create a concrete product from a template by providing material assignments."""
    try:
        new_product = use_case.execute(
            template_id=product_id,
            material_assignments=data.material_assignments,
            custom_name=data.name
        )
        return ProductMapper.to_dto(new_product)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{product_id}/components", response_model=ProductListDTO)
def get_product_components(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    product_repo: ProductRepository = Depends(get_product_repository),
) -> ProductListDTO:
    """
    Get all components of a composite product.
    
    Returns empty list for simple products.
    """
    product = product_repo.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    if not product.is_composite():
        return ProductListDTO(products=[], total=0)
    
    components = product_repo.get_components(product_id)
    component_products = [comp[0] for comp in components]  # Extract ProductComponent from tuple
    
    return ProductMapper.to_dto_list(component_products)


@router.get("/{product_id}/composition", response_model=ProductCompositionDTO)
def get_product_composition(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    product_repo: ProductRepository = Depends(get_product_repository),
) -> ProductCompositionDTO:
    """
    Get the full material composition breakdown of a product.
    
    This includes:
    - All sub-components (if composite)
    - Detailed material usage (multiplier, types, names)
    - Total price calculation breakdown
    - Product properties
    """
    product = product_repo.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    return to_product_composition_dto(product)
