from fastapi import Depends
from sqlalchemy.orm import Session
from app.infrastructure.adapters.db.database import get_db_session
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.material_repository import MaterialRepository
from app.infrastructure.adapters.repositories.postgres_inventory_repository import PostgresInventoryRepository
from app.infrastructure.adapters.repositories.postgres_material_repository import PostgresMaterialRepository
from app.infrastructure.adapters.repositories.postgres_unit_of_measure_repository import PostgresUnitOfMeasureRepository
from app.application.services.inventory_service import InventoryService

def get_unit_repository(
    db_session: Session = Depends(get_db_session),
) -> PostgresUnitOfMeasureRepository:
    """Dependency provider for UnitOfMeasureRepository."""
    return PostgresUnitOfMeasureRepository(db_session)

def get_material_repository(
    db_session: Session = Depends(get_db_session),
    unit_repo: PostgresUnitOfMeasureRepository = Depends(get_unit_repository),
) -> MaterialRepository:
    """Dependency provider for MaterialRepository."""
    return PostgresMaterialRepository(db_session, unit_repo)

def get_inventory_repository(
    db_session: Session = Depends(get_db_session),
) -> InventoryRepository:
    """Dependency provider for InventoryRepository."""
    return PostgresInventoryRepository(db_session)

def get_inventory_service(
    inventory_repo: InventoryRepository = Depends(get_inventory_repository),
    material_repo: MaterialRepository = Depends(get_material_repository),
) -> InventoryService:
    """Dependency provider for InventoryService."""
    return InventoryService(inventory_repo, material_repo)
