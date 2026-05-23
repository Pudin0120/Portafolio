"""
PostgreSQL implementation of WorkRepository.
"""
from typing import List, Optional, Dict
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, delete as sql_delete

from app.domain.models.work import Work
from app.domain.models.product import ProductComponent
from app.domain.repositories.work_repository import WorkRepository
from app.domain.repositories.product_repository import ProductRepository
from app.domain.value_objects.document_number import DocumentNumber, DocumentEnum
from app.domain.value_objects.work_state import WorkStateEnum, create_work_state
from app.domain.value_objects.money import Money
from app.domain.value_objects.product_work_item import ProductWorkItem, ProductItemState
from app.domain.value_objects.product_snapshot import ProductSnapshot
from app.infrastructure.adapters.db.models.work_model import WorkModel
from app.infrastructure.adapters.db.models.product_work_item_model import ProductWorkItemModel
from app.infrastructure.adapters.db.models.task_model import TaskModel
from app.infrastructure.adapters.repositories.postgres_task_repository import PostgresTaskRepository


class PostgresWorkRepository(WorkRepository):
    """Implementacion PostgreSQL del repositorio de works."""

    def __init__(self, db_session: Session, product_repo: ProductRepository):
        self.db_session = db_session
        self.product_repo = product_repo
        self.task_repo = PostgresTaskRepository(db_session)

    def save(self, work: Work) -> Work:
        """
        Guarda o actualiza un work en la base de datos.
        
        Persiste el work junto con sus products y tasks asociadas.
        
        NOTE: Does NOT commit or flush - relies on get_db_session() to commit at end of request.
        This avoids "Session is already flushing" errors when saving nested entities.
        
        Args:
            work: Work a save
            
        Returns:
            Work guardado
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Check if work already exists
        stmt = select(WorkModel).where(WorkModel.id == work.work_id)
        existing = self.db_session.execute(stmt).scalar_one_or_none()
        
        if existing:
            # Update existing work
            logger.info(f"Updating existing work {work.work_id}")
            self._update_model_from_domain(existing, work)
            model = existing
        else:
            # Create new work
            logger.info(f"Creating new work {work.work_id}")
            model = self._to_model(work)
            self.db_session.add(model)
        
        # IMPORTANT: Flush here to assign IDs and make work visible for product_items and tasks
        # This is safe because we're the top-level entity
        self.db_session.flush()
        logger.info(f"Work {work.work_id} flushed, ID assigned")
        
        # Save product work items
        self._save_product_items(work, model)
        
        # Save tasks only if they exist (IN_PROGRESS state)
        if work.tasks:
            logger.info(f"Saving {len(work.tasks)} tasks for work {work.work_id}")
            self._save_tasks(work)
        else:
            logger.info(f"No tasks to save for work {work.work_id} (state: {work.state.get_state_name()})")
        
        # No flush here - SQLAlchemy will handle the order automatically
        # get_db_session() will commit everything at once
        logger.info(f"Work {work.work_id} and related entities queued for commit")
        
        # Refresh model to get latest state
        self.db_session.refresh(model)
        # Return fresh domain object from ORM model
        return self._to_domain(model)

    def get_by_id(self, work_id: UUID) -> Optional[Work]:
        """
        Obtiene un work por su ID.
        
        Carga el work completo con products, tasks y snapshots.
        
        Args:
            work_id: ID del work
            
        Returns:
            Work encontrado o None
        """
        stmt = select(WorkModel).where(WorkModel.id == work_id).options(
            joinedload(WorkModel.client),
            joinedload(WorkModel.products),
            joinedload(WorkModel.tasks)
        )
        model = self.db_session.execute(stmt).unique().scalar_one_or_none()
        return self._to_domain(model) if model else None

    def get_all(self) -> List[Work]:
        """
        Gets all works.
        
        Returns:
            Lista de todos los works
        """
        stmt = select(WorkModel).options(
            joinedload(WorkModel.client),
            joinedload(WorkModel.products),
            joinedload(WorkModel.tasks)
        ).order_by(WorkModel.created_at.desc())
        models = self.db_session.execute(stmt).unique().scalars().all()
        return [self._to_domain(model) for model in models]

    def get_by_state(self, state: WorkStateEnum) -> List[Work]:
        """
        Gets all works en un estado especifico.
        
        Args:
            state: Estado del work
            
        Returns:
            Lista de works en el estado especificado
        """
        stmt = select(WorkModel).where(
            WorkModel.state == state.value
        ).options(
            joinedload(WorkModel.client),
            joinedload(WorkModel.products),
            joinedload(WorkModel.tasks)
        ).order_by(WorkModel.created_at.desc())
        models = self.db_session.execute(stmt).unique().scalars().all()
        return [self._to_domain(model) for model in models]

    def get_by_client(self, client_identification: DocumentNumber) -> List[Work]:
        """
        Gets all works de un client especifico.
        
        Args:
            client_identification: Number de identificacion del client
            
        Returns:
            Lista de works del client
        """
        stmt = select(WorkModel).where(
            WorkModel.client_identification == client_identification.value
        ).options(
            joinedload(WorkModel.client),
            joinedload(WorkModel.products),
            joinedload(WorkModel.tasks)
        ).order_by(WorkModel.created_at.desc())
        models = self.db_session.execute(stmt).unique().scalars().all()
        return [self._to_domain(model) for model in models]

    def delete(self, work_id: UUID) -> bool:
        """
        Elimina un work por su ID.
        
        Args:
            work_id: ID del work
            
        Returns:
            True si se elimino correctamente, False si no existia
        """
        stmt = select(WorkModel).where(WorkModel.id == work_id)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        
        if not model:
            return False
        
        self.db_session.delete(model)
        # Don't flush or commit - let get_db_session() handle it
        return True

    def _to_domain(self, model: WorkModel) -> Work:
        """
        Convierte un modelo de base de datos a entidad de dominio.
        
        Args:
            model: Modelo de base de datos
            
        Returns:
            Entidad de dominio Work
        """
        # Create state
        state_enum = WorkStateEnum(model.state)
        state = create_work_state(state_enum)
        
        # Create work
        # Note: Using CC as default doc_type since we only have the identification_number from DB
        work = Work(
            work_id=model.id,  # type: ignore
            identification_number_client=DocumentNumber(value=model.client_identification, doc_type=DocumentEnum.CC),  # type: ignore
            work_name=model.work_name,  # type: ignore
            description=model.description or "",  # type: ignore
            state=state,
            products=[],
            tasks=[],
            tax=float(model.tax),  # type: ignore
            start_date=model.start_date,  # type: ignore
            end_aprox_delivery_date=model.end_aprox_delivery_date,  # type: ignore
            end_delivery_date=model.end_delivery_date,  # type: ignore
            deposit=Money(amount=Decimal(str(model.deposit_amount)), currency=model.deposit_currency),  # type: ignore
            tenant_id=model.tenant_id
        )
        
        # Load products
        for product_model in sorted(model.products, key=lambda p: p.execution_order):
            product_item = self._product_item_to_domain(product_model)
            work.products.append(product_item)
        
        # Load tasks
        for task_model in sorted(model.tasks, key=lambda t: t.execution_order):
            task = self.task_repo._to_domain(task_model)
            work.tasks.append(task)
        
        return work

    def _to_model(self, work: Work) -> WorkModel:
        """
        Convierte una entidad de dominio a modelo de base de datos.
        
        Args:
            work: Entidad de dominio
            
        Returns:
            Modelo de base de datos WorkModel
        """
        return WorkModel(
            id=work.work_id,
            client_identification=work.identification_number_client.value,
            work_name=work.work_name,
            description=work.description,
            state=work.state.get_state_name().value,
            tax=Decimal(str(work.tax)),
            deposit_amount=work.deposit.amount,
            deposit_currency=work.deposit.currency,
            start_date=work.start_date,
            end_aprox_delivery_date=work.end_aprox_delivery_date,
            end_delivery_date=work.end_delivery_date,
            tenant_id=work.tenant_id
        )

    def _update_model_from_domain(self, model: WorkModel, work: Work) -> None:
        """
        Actualiza un modelo existente con datos de la entidad de dominio.
        
        Args:
            model: Modelo a actualizar
            work: Entidad de dominio con datos actualizados
        """
        model.work_name = work.work_name  # type: ignore
        model.description = work.description  # type: ignore
        model.state = work.state.get_state_name().value  # type: ignore
        model.tax = Decimal(str(work.tax))  # type: ignore
        model.deposit_amount = work.deposit.amount  # type: ignore
        model.deposit_currency = work.deposit.currency  # type: ignore
        model.start_date = work.start_date  # type: ignore
        model.end_aprox_delivery_date = work.end_aprox_delivery_date  # type: ignore
        model.end_delivery_date = work.end_delivery_date  # type: ignore

    def _save_product_items(self, work: Work, work_model: WorkModel) -> None:
        """
        Guarda los ProductWorkItems del work.
        
        Args:
            work: Entidad de dominio Work
            work_model: Modelo de base de datos WorkModel
        """
        # Get existing product items
        stmt = select(ProductWorkItemModel).where(
            ProductWorkItemModel.work_id == work.work_id
        )
        existing_items = self.db_session.execute(stmt).scalars().all()
        
        # Create a map of existing items by product_id
        existing_map: Dict[UUID, ProductWorkItemModel] = {item.product_id: item for item in existing_items}  # type: ignore
        
        # Track which products are in the new state
        current_product_ids = {item.product_id for item in work.products}
        
        # Delete items that are no longer in the work
        for product_id, existing_item in existing_map.items():
            if product_id not in current_product_ids:
                self.db_session.delete(existing_item)
        
        # Update or create product items
        for product_item in work.products:
            if product_item.product_id in existing_map:
                # Update existing
                existing = existing_map[product_item.product_id]
                existing.quantity = product_item.quantity  # type: ignore
                existing.execution_order = product_item.execution_order  # type: ignore
                existing.state = product_item.state.value  # type: ignore
                
                # Update snapshot if present
                if product_item.snapshot:
                    existing.snapshot_product_id = product_item.snapshot.product_id  # type: ignore
                    existing.snapshot_product_name = product_item.snapshot.product_name  # type: ignore
                    existing.snapshot_product_type = product_item.snapshot.product_type  # type: ignore
                    existing.snapshot_purchase_price_amount = product_item.snapshot.purchase_price.amount  # type: ignore
                    existing.snapshot_purchase_price_currency = product_item.snapshot.purchase_price.currency  # type: ignore
                    existing.snapshot_sale_price_amount = product_item.snapshot.sale_price.amount  # type: ignore
                    existing.snapshot_sale_price_currency = product_item.snapshot.sale_price.currency  # type: ignore
                    existing.snapshot_price_amount = product_item.snapshot.sale_price.amount  # type: ignore
                    existing.snapshot_price_currency = product_item.snapshot.sale_price.currency  # type: ignore
                    existing.snapshot_composition = product_item.snapshot.composition  # type: ignore
                    existing.snapshot_dimensions = product_item.snapshot.dimensions  # type: ignore
                    existing.snapshot_quantity_multiplier = product_item.snapshot.quantity_multiplier  # type: ignore
            else:
                # Create new
                model = self._product_item_to_model(product_item, work.work_id)
                self.db_session.add(model)

    def _save_tasks(self, work: Work) -> None:
        """
        Guarda las tasks del work en la misma transaccion.
        
        Este metodo persiste las tasks sin hacer commit, permitiendo que
        el work_repository maneje la transaccion completa.
        
        Args:
            work: Entidad de dominio Work con las tasks a save
        """
        for task in work.tasks:
            # Check if task already exists
            stmt = select(TaskModel).where(TaskModel.id == task.task_id)
            existing = self.db_session.execute(stmt).scalar_one_or_none()
            
            if existing:
                # Update existing task
                self.task_repo._update_model_from_domain(existing, task)
            else:
                # Create new task
                task_model = self.task_repo._to_model(task)
                self.db_session.add(task_model)

    def _product_item_to_domain(self, model: ProductWorkItemModel) -> ProductWorkItem:
        """
        Convierte un ProductWorkItemModel a ProductWorkItem de dominio.
        
        Args:
            model: Modelo de base de datos
            
        Returns:
            ProductWorkItem de dominio
        """
        # Create snapshot if present
        snapshot = None
        if model.snapshot_product_id:  # type: ignore
            # Handle migration of old data where sale/purchase columns might be null
            sale_amount = model.snapshot_sale_price_amount or model.snapshot_price_amount
            sale_currency = model.snapshot_sale_price_currency or model.snapshot_price_currency or "COP"
            
            purchase_amount = model.snapshot_purchase_price_amount or sale_amount
            purchase_currency = model.snapshot_purchase_price_currency or sale_currency
            
            snapshot = ProductSnapshot(
                product_id=model.snapshot_product_id,  # type: ignore
                product_name=model.snapshot_product_name,  # type: ignore
                product_type=model.snapshot_product_type,  # type: ignore
                purchase_price=Money(
                    amount=Decimal(str(purchase_amount)),
                    currency=str(purchase_currency)
                ),
                sale_price=Money(
                    amount=Decimal(str(sale_amount)),
                    currency=str(sale_currency)
                ),
                composition=model.snapshot_composition or {},  # type: ignore
                dimensions=model.snapshot_dimensions or {},  # type: ignore
                quantity_multiplier=Decimal(str(model.snapshot_quantity_multiplier or "1.0"))  # type: ignore
            )
        
        # Map state
        state = ProductItemState(model.state)  # type: ignore
        
        return ProductWorkItem(
            product_id=model.product_id,  # type: ignore
            work_id=model.work_id,  # type: ignore
            quantity=model.quantity,  # type: ignore
            execution_order=model.execution_order,  # type: ignore
            state=state,
            snapshot=snapshot,
            task_ids=[]  # Task IDs loaded separately
        )

    def _product_item_to_model(self, item: ProductWorkItem, work_id: UUID) -> ProductWorkItemModel:
        """
        Convierte un ProductWorkItem de dominio a ProductWorkItemModel.
        
        Args:
            item: ProductWorkItem de dominio
            work_id: ID del work
            
        Returns:
            Modelo de base de datos ProductWorkItemModel
        """
        model = ProductWorkItemModel(
            work_id=work_id,
            product_id=item.product_id,
            quantity=item.quantity,
            execution_order=item.execution_order,
            state=item.state.value
        )
        
        # Add snapshot if present
        if item.snapshot:
            model.snapshot_product_id = item.snapshot.product_id  # type: ignore
            model.snapshot_product_name = item.snapshot.product_name  # type: ignore
            model.snapshot_product_type = item.snapshot.product_type  # type: ignore
            model.snapshot_purchase_price_amount = item.snapshot.purchase_price.amount  # type: ignore
            model.snapshot_purchase_price_currency = item.snapshot.purchase_price.currency  # type: ignore
            model.snapshot_sale_price_amount = item.snapshot.sale_price.amount  # type: ignore
            model.snapshot_sale_price_currency = item.snapshot.sale_price.currency  # type: ignore
            model.snapshot_price_amount = item.snapshot.sale_price.amount  # type: ignore
            model.snapshot_price_currency = item.snapshot.sale_price.currency  # type: ignore
            model.snapshot_composition = item.snapshot.composition  # type: ignore
            model.snapshot_dimensions = item.snapshot.dimensions  # type: ignore
            model.snapshot_quantity_multiplier = item.snapshot.quantity_multiplier  # type: ignore
        
        return model

