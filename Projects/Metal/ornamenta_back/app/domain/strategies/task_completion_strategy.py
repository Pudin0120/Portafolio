"""
Task Completion Strategy Pattern.

Implementa el patron Strategy para manejar la logica de completitud
y validacion de tasks segun el rol del user que la ejecuta.

Estrategias:
- EmployeeTaskCompletionStrategy: Requiere validacion posterior
- SupervisorTaskCompletionStrategy: Auto-validada
- ManagerTaskCompletionStrategy: Auto-validada
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import uuid

from app.domain.models.user import RoleEnum
from app.domain.value_objects.state_task import StateTask, StateTaskEnum

if TYPE_CHECKING:
    from app.domain.models.task import Task
    from app.domain.models.user import User


class TaskCompletionStrategy(ABC):
    """
    Estrategia abstracta para completar tasks.
    
    Define la interfaz que todas las estrategias concretas deben implementar
    para manejar la logica de completitud de tasks segun el rol del user.
    """
    
    @abstractmethod
    def complete_task(self, task: 'Task', completed_by: 'User') -> StateTask:
        """
        Completa una task segun la estrategia especifica del rol.
        
        Args:
            task: Task a completar
            completed_by: User que completa la task
            
        Returns:
            Nuevo estado de la task
            
        Raises:
            ValueError: Si la task no puede completarse
        """
        pass
    
    @abstractmethod
    def requires_validation(self) -> bool:
        """Indica si esta estrategia requiere validacion posterior."""
        pass
    
    @abstractmethod
    def can_validate_tasks(self) -> bool:
        """Indica si este rol puede validar tasks de otros."""
        pass
    
    def validate_task(self, task: 'Task', validated_by: 'User') -> StateTask:
        """
        Valida una task completada (solo para roles que pueden validar).
        
        Args:
            task: Task a validar
            validated_by: User que valida la task
            
        Returns:
            Nuevo estado de la task (FINISHED)
            
        Raises:
            ValueError: Si este rol no puede validar o la task no esta en estado COMPLETED
        """
        if not self.can_validate_tasks():
            raise ValueError(f"El rol {validated_by.role.value} no puede validar tasks")
        
        if not task.state.is_completed:
            raise ValueError("Solo se pueden validar tasks en estado COMPLETED")
        
        return task.state.to_finished()


class EmployeeTaskCompletionStrategy(TaskCompletionStrategy):
    """
    Estrategia de completitud para EMPLOYEE.
    
    Cuando un empleado completa una task:
    - La task pasa a estado COMPLETED (no FINISHED)
    - Requiere validacion posterior de SUPERVISOR o MANAGER
    - No puede validar tasks
    """
    
    def complete_task(self, task: 'Task', completed_by: 'User') -> StateTask:
        """
        Completa una task como EMPLOYEE.
        
        La task pasa de IN_PROGRESS  COMPLETED (pending de validacion).
        """
        if not task.state.is_in_progress:
            raise ValueError("Solo se puede completar una task en estado IN_PROGRESS")
        
        if completed_by.role != RoleEnum.EMPLOYEE:
            raise ValueError("Esta estrategia solo es valid para EMPLOYEE")
        
        # EMPLOYEE completa pero requiere validacion
        return task.state.to_completed()
    
    def requires_validation(self) -> bool:
        return True
    
    def can_validate_tasks(self) -> bool:
        return False


class SupervisorTaskCompletionStrategy(TaskCompletionStrategy):
    """
    Estrategia de completitud para SUPERVISOR.
    
    Cuando un supervisor completa una task:
    - La task pasa directamente a estado FINISHED (auto-validada)
    - No requiere validacion posterior
    - Puede validar tasks de empleados
    """
    
    def complete_task(self, task: 'Task', completed_by: 'User') -> StateTask:
        """
        Completa una task como SUPERVISOR.
        
        La task pasa de IN_PROGRESS  FINISHED (auto-validada).
        """
        if not task.state.is_in_progress:
            raise ValueError("Solo se puede completar una task en estado IN_PROGRESS")
        
        if completed_by.role != RoleEnum.SUPERVISOR:
            raise ValueError("Esta estrategia solo es valid para SUPERVISOR")
        
        # SUPERVISOR auto-valida
        return task.state.to_finished()
    
    def requires_validation(self) -> bool:
        return False
    
    def can_validate_tasks(self) -> bool:
        return True


class ManagerTaskCompletionStrategy(TaskCompletionStrategy):
    """
    Estrategia de completitud para MANAGER.
    
    Cuando un manager completa una task:
    - La task pasa directamente a estado FINISHED (auto-validada)
    - No requiere validacion posterior
    - Puede validar tasks de empleados
    """
    
    def complete_task(self, task: 'Task', completed_by: 'User') -> StateTask:
        """
        Completa una task como MANAGER.
        
        La task pasa de IN_PROGRESS  FINISHED (auto-validada).
        """
        if not task.state.is_in_progress:
            raise ValueError("Solo se puede completar una task en estado IN_PROGRESS")
        
        if completed_by.role != RoleEnum.MANAGER:
            raise ValueError("Esta estrategia solo es valid para MANAGER")
        
        # MANAGER auto-valida
        return task.state.to_finished()
    
    def requires_validation(self) -> bool:
        return False
    
    def can_validate_tasks(self) -> bool:
        return True


class TaskCompletionStrategyFactory:
    """
    Factory para create estrategias de completitud segun el rol.
    """
    
    _strategies = {
        RoleEnum.EMPLOYEE: EmployeeTaskCompletionStrategy(),
        RoleEnum.SUPERVISOR: SupervisorTaskCompletionStrategy(),
        RoleEnum.MANAGER: ManagerTaskCompletionStrategy(),
    }
    
    @classmethod
    def get_strategy(cls, role: RoleEnum) -> TaskCompletionStrategy:
        """
        Obtiene la estrategia de completitud correspondiente al rol.
        
        Args:
            role: Rol del user
            
        Returns:
            Estrategia de completitud correspondiente
            
        Raises:
            ValueError: Si el rol no tiene una estrategia definida
        """
        strategy = cls._strategies.get(role)
        if strategy is None:
            raise ValueError(f"No existe estrategia de completitud para el rol {role.value}")
        return strategy
    
    @classmethod
    def can_role_validate(cls, role: RoleEnum) -> bool:
        """
        Verifica si un rol puede validar tasks.
        
        Args:
            role: Rol a verificar
            
        Returns:
            True si el rol puede validar tasks
        """
        strategy = cls.get_strategy(role)
        return strategy.can_validate_tasks()

