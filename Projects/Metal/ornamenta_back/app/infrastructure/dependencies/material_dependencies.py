"""
Dependency injection configuration for Material module.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.services.composite_product_service import CompositeProductService
from app.application.services.material_price_service import MaterialPriceUpdateService
from app.application.services.product_creation_service import ProductCreationService
from app.application.use_cases.create_material import CreateMaterialUseCase
from app.application.use_cases.update_material import UpdateMaterialUseCase
from app.application.use_cases.create_composite_product import CreateCompositeProductUseCase
from app.application.use_cases.update_composite_dimensions import UpdateCompositeProductDimensionsUseCase
from app.application.use_cases.create_composite_snapshot import CreateCompositeSnapshotUseCase
from app.application.use_cases.clear_composite_snapshot import ClearCompositeSnapshotUseCase
from app.application.use_cases.update_product import UpdateProductUseCase
from app.application.use_cases.template_use_cases import (
    GetTemplateRequirementsUseCase,
    InstantiateProductUseCase,
)
from app.application.services.inventory_service import InventoryService
from app.domain.repositories.composition_repository import CompositionRepository
from app.domain.repositories.material_repository import MaterialRepository
from app.domain.repositories.material_type_repository import MaterialTypeRepository
from app.domain.repositories.product_repository import ProductRepository
from app.domain.repositories.price_calculation_audit_repository import PriceCalculationAuditRepository
from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository
from app.infrastructure.adapters.db.database import get_db_session
from app.infrastructure.adapters.db.repositories.postgresql_composition_repository import (
    PostgreSQLCompositionRepository,
)
from app.infrastructure.adapters.repositories.postgres_material_repository import (
    PostgresMaterialRepository,
)
from app.infrastructure.adapters.repositories.postgres_material_type_repository import (
    PostgresMaterialTypeRepository,
)
from app.infrastructure.adapters.repositories.postgres_product_repository import (
    PostgresProductRepository,
)
from app.infrastructure.adapters.repositories.postgres_unit_of_measure_repository import (
    PostgresUnitOfMeasureRepository,
)
from app.infrastructure.adapters.repositories.postgres_audit_repository import (
    PostgresPriceCalculationAuditRepository,
)
from app.infrastructure.dependencies.inventory_dependencies import get_inventory_service

def get_unit_repository(
    db_session: Session = Depends(get_db_session),
) -> UnitOfMeasureRepository:
    """Dependency provider for UnitOfMeasureRepository."""
    return PostgresUnitOfMeasureRepository(db_session)


def get_material_repository(
    db_session: Session = Depends(get_db_session),
    unit_repo: UnitOfMeasureRepository = Depends(get_unit_repository),
) -> MaterialRepository:
    """Dependency provider for MaterialRepository."""
    return PostgresMaterialRepository(db_session, unit_repo)


def get_product_repository(
    db_session: Session = Depends(get_db_session),
    unit_repo: UnitOfMeasureRepository = Depends(get_unit_repository),
) -> ProductRepository:
    """Dependency provider for ProductRepository."""
    return PostgresProductRepository(db_session, unit_repo)


def get_audit_repository(
    db_session: Session = Depends(get_db_session),
) -> PriceCalculationAuditRepository:
    """Dependency provider for PriceCalculationAuditRepository."""
    return PostgresPriceCalculationAuditRepository(db_session)


def get_product_creation_service(
    material_repo: MaterialRepository = Depends(get_material_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
    unit_repo: UnitOfMeasureRepository = Depends(get_unit_repository),
    audit_repo: PriceCalculationAuditRepository = Depends(get_audit_repository),
) -> ProductCreationService:
    """Dependency provider for ProductCreationService."""
    return ProductCreationService(
        material_repository=material_repo,
        product_repository=product_repo,
        unit_repository=unit_repo,
        audit_repository=audit_repo,
    )


def get_material_type_repository(
    db_session: Session = Depends(get_db_session),
) -> MaterialTypeRepository:
    """Dependency provider for MaterialTypeRepository."""
    return PostgresMaterialTypeRepository(db_session)


def get_composition_repository(
    db_session: Session = Depends(get_db_session),
) -> CompositionRepository:
    """Dependency provider for CompositionRepository."""
    return PostgreSQLCompositionRepository(db_session)


def get_material_price_update_service(
    material_repo: MaterialRepository = Depends(get_material_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
) -> MaterialPriceUpdateService:
    """Dependency provider for MaterialPriceUpdateService."""
    return MaterialPriceUpdateService(
        material_repository=material_repo, product_repository=product_repo
    )


def get_create_material_use_case(
    material_repo: MaterialRepository = Depends(get_material_repository),
    material_type_repo: MaterialTypeRepository = Depends(get_material_type_repository),
    composition_repo: CompositionRepository = Depends(get_composition_repository),
    unit_repo: UnitOfMeasureRepository = Depends(get_unit_repository),
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> CreateMaterialUseCase:
    """Dependency provider for CreateMaterialUseCase."""
    return CreateMaterialUseCase(
        material_repository=material_repo,
        material_type_repository=material_type_repo,
        composition_repository=composition_repo,
        unit_repository=unit_repo,
        inventory_service=inventory_service,
    )


def get_update_material_use_case(
    material_repo: MaterialRepository = Depends(get_material_repository),
    composition_repo: CompositionRepository = Depends(get_composition_repository),
    unit_repo: UnitOfMeasureRepository = Depends(get_unit_repository),
    price_service: MaterialPriceUpdateService = Depends(
        get_material_price_update_service
    ),
) -> UpdateMaterialUseCase:
    """Dependency provider for UpdateMaterialUseCase."""
    return UpdateMaterialUseCase(
        material_repository=material_repo,
        composition_repository=composition_repo,
        unit_repository=unit_repo,
        price_update_service=price_service,
    )


def get_composite_product_service(
    product_repo: ProductRepository = Depends(get_product_repository),
) -> CompositeProductService:
    """Dependency provider for CompositeProductService."""
    return CompositeProductService(
        product_repository=product_repo,
    )


def get_create_composite_product_use_case(
    composite_service: CompositeProductService = Depends(get_composite_product_service),
) -> CreateCompositeProductUseCase:
    """Dependency provider for CreateCompositeProductUseCase."""
    return CreateCompositeProductUseCase(composite_service=composite_service)


def get_update_composite_dimensions_use_case(
    product_repo: ProductRepository = Depends(get_product_repository),
) -> UpdateCompositeProductDimensionsUseCase:
    """Dependency provider for UpdateCompositeProductDimensionsUseCase."""
    return UpdateCompositeProductDimensionsUseCase(product_repository=product_repo)


def get_create_composite_snapshot_use_case(
    product_repo: ProductRepository = Depends(get_product_repository),
) -> CreateCompositeSnapshotUseCase:
    """Dependency provider for CreateCompositeSnapshotUseCase."""
    return CreateCompositeSnapshotUseCase(product_repository=product_repo)


def get_clear_composite_snapshot_use_case(
    product_repo: ProductRepository = Depends(get_product_repository),
) -> ClearCompositeSnapshotUseCase:
    """Dependency provider for ClearCompositeSnapshotUseCase."""
    return ClearCompositeSnapshotUseCase(product_repository=product_repo)


def get_update_product_use_case(
    product_repo: ProductRepository = Depends(get_product_repository),
) -> UpdateProductUseCase:
    """Dependency provider for UpdateProductUseCase."""
    return UpdateProductUseCase(product_repo=product_repo)


def get_template_requirements_use_case(
    product_repo: ProductRepository = Depends(get_product_repository),
) -> GetTemplateRequirementsUseCase:
    """Dependency provider for GetTemplateRequirementsUseCase."""
    return GetTemplateRequirementsUseCase(product_repo=product_repo)


def get_instantiate_product_use_case(
    product_repo: ProductRepository = Depends(get_product_repository),
    material_repo: MaterialRepository = Depends(get_material_repository),
) -> InstantiateProductUseCase:
    """Dependency provider for InstantiateProductUseCase."""
    return InstantiateProductUseCase(
        product_repo=product_repo, material_repo=material_repo
    )
