from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
import uuid

from app.domain.models.task_assignment import TaskAssignment


class TaskAssignmentRepository(ABC):
    """Repositorio abstracto para la entidad TaskAssignment."""

    @abstractmethod
    def save(self, task_assignment: TaskAssignment) -> TaskAssignment:
        """Guarda una asignacion de task en el repositorio."""
        pass

    @abstractmethod
    def get_by_task_id(self, task_id: uuid.UUID) -> Optional[TaskAssignment]:
        """Obtiene la asignacion de una task especifica."""
        pass

    @abstractmethod
    def get_by_payroll_id(self, payroll_id: uuid.UUID) -> List[TaskAssignment]:
        """Obtiene todas las asignaciones de tasks de una payroll especifica."""
        pass

    @abstractmethod
    def get_by_identification_number(self, identification_number: str) -> List[TaskAssignment]:
        """Obtiene todas las asignaciones de tasks de un empleado especifico."""
        pass

    @abstractmethod
    def get_by_assigned_date_range(self, start_date: date, end_date: date) -> List[TaskAssignment]:
        """Obtiene todas las asignaciones en un rango de fechas de asignacion."""
        pass

    @abstractmethod
    def get_by_delivery_date_range(self, start_date: date, end_date: date) -> List[TaskAssignment]:
        """Obtiene todas las asignaciones entregadas en un rango de fechas de entrega."""
        pass

    @abstractmethod
    def get_overdue_assignments(self) -> List[TaskAssignment]:
        """Obtiene todas las asignaciones vencidas."""
        pass

    @abstractmethod
    def get_all(self) -> List[TaskAssignment]:
        """Obtiene todas las asignaciones de tasks."""
        pass

    @abstractmethod
    def delete(self, task_id: uuid.UUID) -> bool:
        """Elimina una asignacion de task por el ID de la task."""
        pass

    @abstractmethod
    def exists(self, task_id: uuid.UUID) -> bool:
        """Verifica si existe una asignacion para la task con el ID dado."""
        pass
