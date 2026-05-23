"""
PostgreSQL implementation of TaskRepository.
"""
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.domain.models.task import Task
from app.domain.repositories.task_repository import TaskRepository
from app.domain.value_objects.state_task import StateTask, StateTaskEnum
from app.domain.value_objects.money import Money
from app.infrastructure.adapters.db.models.task_model import TaskModel


class PostgresTaskRepository(TaskRepository):
    """Implementacion PostgreSQL del repositorio de tasks."""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def save(self, task: Task) -> Task:
        """
        Guarda o actualiza una task en la base de datos.
        
        NOTE: COMMITS immediately to ensure data persistence.
        This is necessary because get_db_session() auto-commit is not reliable in all contexts.
        
        Args:
            task: Task a save
            
        Returns:
            Task guardada
        """
        # Check if task already exists
        stmt = select(TaskModel).where(TaskModel.id == task.task_id)
        existing = self.db_session.execute(stmt).scalar_one_or_none()
        
        if existing:
            # Update existing task
            self._update_model_from_domain(existing, task)
            model = existing
        else:
            # Create new task
            model = self._to_model(task)
            self.db_session.add(model)
        
        # Commit to persist changes immediately
        self.db_session.commit()
        # Refresh to get updated values from DB
        self.db_session.refresh(model)
        # Return fresh domain object
        return self._to_domain(model)

    def get_by_id(self, task_id: UUID) -> Optional[Task]:
        """
        Obtiene una task por su ID.
        
        Args:
            task_id: ID de la task
            
        Returns:
            Task encontrada o None
        """
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None

    def get_by_work_id(self, work_id: UUID) -> List[Task]:
        """
        Obtiene todas las tasks de un work especifico.
        
        Args:
            work_id: ID del work
            
        Returns:
            Lista de tasks del work
        """
        stmt = select(TaskModel).where(
            TaskModel.work_id == work_id
        ).order_by(TaskModel.execution_order)
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]

    def get_by_assigned_user(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Task]:
        """
        Obtiene todas las tasks asignadas a un user especifico.
        
        Args:
            user_id: ID del user (Firebase UID o UUID string)
            start_date: Fecha de inicio del rango (opcional, filtra por updated_at >= start_date)
            end_date: Fecha de fin del rango (opcional, filtra por updated_at <= end_date)
            
        Returns:
            Lista de tasks asignadas al user
        """
        stmt = select(TaskModel).where(
            TaskModel.assigned_user_id == user_id
        )
        
        # Aplicar filtros de fecha si se proporcionan
        if start_date:
            stmt = stmt.where(TaskModel.updated_at >= start_date)
        if end_date:
            stmt = stmt.where(TaskModel.updated_at <= end_date)
            
        stmt = stmt.order_by(TaskModel.execution_order)
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]

    def get_by_state(self, state: StateTask) -> List[Task]:
        """
        Obtiene todas las tasks con un estado especifico.
        
        Args:
            state: Estado de la task
            
        Returns:
            Lista de tasks en el estado especificado
        """
        state_value = state.value.value
        stmt = select(TaskModel).where(
            TaskModel.state == state_value
        ).order_by(TaskModel.execution_order)
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]

    def get_all(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Task]:
        """
        Obtiene todas las tasks.
        
        Args:
            start_date: Fecha de inicio del rango (opcional, filtra por updated_at >= start_date)
            end_date: Fecha de fin del rango (opcional, filtra por updated_at <= end_date)
        
        Returns:
            Lista de todas las tasks
        """
        stmt = select(TaskModel)
        
        # Aplicar filtros de fecha si se proporcionan
        if start_date:
            stmt = stmt.where(TaskModel.updated_at >= start_date)
        if end_date:
            stmt = stmt.where(TaskModel.updated_at <= end_date)
            
        stmt = stmt.order_by(TaskModel.created_at)
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]

    def delete(self, task_id: UUID) -> bool:
        """
        Deletes a task por su ID.
        
        NOTE: Does NOT commit - relies on get_db_session() to commit at end of request.
        This ensures atomicity across multiple operations in the same request.
        
        Args:
            task_id: ID de la task
            
        Returns:
            True si se elimino correctamente, False si no existia
        """
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        
        if not model:
            return False
        
        self.db_session.delete(model)
        self.db_session.flush()  # Flush to validate constraints
        return True

    def exists(self, task_id: UUID) -> bool:
        """
        Verifica si existe una task con el ID dado.
        
        Args:
            task_id: ID de la task
            
        Returns:
            True si existe, False en caso contrario
        """
        stmt = select(TaskModel.id).where(TaskModel.id == task_id)
        result = self.db_session.execute(stmt).scalar_one_or_none()
        return result is not None

    def _to_domain(self, model: TaskModel) -> Task:
        """
        Convierte un modelo de base de datos a entidad de dominio.
        
        Args:
            model: Modelo de base de datos
            
        Returns:
            Entidad de dominio Task
        """
        # Map state string to StateTask
        state_enum = StateTaskEnum(model.state)
        state = StateTask(value=state_enum)
        
        return Task(
            task_id=model.id,  # type: ignore
            work_id=model.work_id,  # type: ignore
            product_id=model.product_id,  # type: ignore
            parent_composite_id=model.parent_composite_id,  # type: ignore
            composite_task_slot=model.composite_task_slot,  # type: ignore
            composite_total_slots=model.composite_total_slots,  # type: ignore
            task_name=model.task_name,  # type: ignore
            description=model.description or "",  # type: ignore
            state=state,
            labor=Money(amount=Decimal(str(model.labor_amount)), currency=model.labor_currency),  # type: ignore
            estimated_value=Money(amount=Decimal(str(model.estimated_value_amount)), currency=model.estimated_value_currency),  # type: ignore
            execution_order=model.execution_order,  # type: ignore
            requires_validation=model.requires_validation,  # type: ignore
            is_blocked=model.is_blocked,  # type: ignore
            previous_task_id=model.previous_task_id,  # type: ignore
            assigned_user_id=model.assigned_user_id,  # type: ignore
            completed_by_user_id=model.completed_by_user_id,  # type: ignore
            validated_by_user_id=model.validated_by_user_id,  # type: ignore
            updated_at=model.updated_at  # type: ignore
        )

    def _to_model(self, task: Task) -> TaskModel:
        """
        Convierte una entidad de dominio a modelo de base de datos.
        
        Args:
            task: Entidad de dominio
            
        Returns:
            Modelo de base de datos TaskModel
        """
        return TaskModel(
            id=task.task_id,
            work_id=task.work_id,
            product_id=task.product_id,
            parent_composite_id=task.parent_composite_id,
            composite_task_slot=task.composite_task_slot,
            composite_total_slots=task.composite_total_slots,
            task_name=task.task_name,
            description=task.description,
            state=task.state.value.value,
            labor_amount=task.labor.amount,
            labor_currency=task.labor.currency,
            estimated_value_amount=task.estimated_value.amount,
            estimated_value_currency=task.estimated_value.currency,
            execution_order=task.execution_order,
            requires_validation=task.requires_validation,
            is_blocked=task.is_blocked,
            previous_task_id=task.previous_task_id,
            assigned_user_id=task.assigned_user_id,
            completed_by_user_id=task.completed_by_user_id,
            validated_by_user_id=task.validated_by_user_id
        )

    def _update_model_from_domain(self, model: TaskModel, task: Task) -> None:
        """
        Actualiza un modelo existente con datos de la entidad de dominio.
        
        Args:
            model: Modelo a actualizar
            task: Entidad de dominio con datos actualizados
        """
        model.task_name = task.task_name  # type: ignore
        model.description = task.description  # type: ignore
        model.state = task.state.value.value  # type: ignore
        model.labor_amount = task.labor.amount  # type: ignore
        model.labor_currency = task.labor.currency  # type: ignore
        model.estimated_value_amount = task.estimated_value.amount  # type: ignore
        model.estimated_value_currency = task.estimated_value.currency  # type: ignore
        model.execution_order = task.execution_order  # type: ignore
        model.requires_validation = task.requires_validation  # type: ignore
        model.is_blocked = task.is_blocked  # type: ignore
        model.previous_task_id = task.previous_task_id  # type: ignore
        model.assigned_user_id = task.assigned_user_id  # type: ignore
        model.completed_by_user_id = task.completed_by_user_id  # type: ignore
        model.validated_by_user_id = task.validated_by_user_id  # type: ignore
        model.parent_composite_id = task.parent_composite_id  # type: ignore
        model.composite_task_slot = task.composite_task_slot  # type: ignore
        model.composite_total_slots = task.composite_total_slots  # type: ignore

