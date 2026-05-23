from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
import uuid

from app.domain.models.task import Task
from app.domain.value_objects.state_task import StateTask


class TaskRepository(ABC):
    """Repositorio abstracto para la entidad Task."""

    @abstractmethod
    def save(self, task: Task) -> Task:
        """Guarda una task en el repositorio."""
        pass

    @abstractmethod
    def get_by_id(self, task_id: uuid.UUID) -> Optional[Task]:
        """Obtiene una task por su ID."""
        pass

    @abstractmethod
    def get_by_work_id(self, work_id: uuid.UUID) -> List[Task]:
        """Obtiene todas las tasks de un work especifico."""
        pass

    @abstractmethod
    def get_by_assigned_user(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Task]:
        """Obtiene todas las tasks asignadas a un user especifico, opcionalmente filtradas por rango de fechas."""
        pass

    @abstractmethod
    def get_by_state(self, state: StateTask) -> List[Task]:
        """Obtiene todas las tasks con un estado especifico."""
        pass

    @abstractmethod
    def get_all(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Task]:
        """Obtiene todas las tasks, opcionalmente filtradas por rango de fechas."""
        pass

    @abstractmethod
    def delete(self, task_id: uuid.UUID) -> bool:
        """Deletes a task por su ID."""
        pass

    @abstractmethod
    def exists(self, task_id: uuid.UUID) -> bool:
        """Verifica si existe una task con el ID dado."""
        pass
