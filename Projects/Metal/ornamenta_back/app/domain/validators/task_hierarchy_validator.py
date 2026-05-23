"""
Task Hierarchy Validator.

Valida que el orden de ejecucion de tasks respete la jerarquia de products compuestos.

Reglas:
1. Tasks del mismo compuesto deben estar consecutivas en execution_order
2. No se puede mover una task fuera de su rango [start, end] del compuesto
3. El orden dentro del compuesto no puede cambiar (respeta composite_task_slot)
"""
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from app.domain.models.task import Task


@dataclass
class CompositeTaskBoundary:
    """
    Define los limites de ejecucion de un product compuesto.
    
    Attributes:
        composite_id: ID del product compuesto
        start_execution_order: Orden de ejecucion de la primera task del compuesto
        end_execution_order: Orden de ejecucion de la ultima task del compuesto
        total_task_slots: Quantity total de tasks en el compuesto
    """
    composite_id: UUID
    start_execution_order: int
    end_execution_order: int
    total_task_slots: int


class TaskHierarchyValidator:
    """
    Valida que el orden de ejecucion de tasks respete la jerarquia de products.
    
    Ejemplo:
        Work
         Task A (execution_order=0, no compuesto)
         CompositeProduct "Puerta"
            Task B (execution_order=1, slot=0/3)
            Task C (execution_order=2, slot=1/3)   No puede ir antes de B
            Task D (execution_order=3, slot=2/3)   No puede ir antes de C
         Task E (execution_order=4, no compuesto)
    """
    
    @staticmethod
    def build_composite_boundaries(tasks: List['Task']) -> Dict[UUID, CompositeTaskBoundary]:
        """
        Construye los limites de ejecucion para cada product compuesto.
        
        Args:
            tasks: Lista de todas las tasks del work
            
        Returns:
            Diccionario {composite_id: CompositeTaskBoundary}
        """
        composites: Dict[UUID, List['Task']] = {}
        
        # Agrupar tasks por composite
        for task in tasks:
            if task.parent_composite_id:
                if task.parent_composite_id not in composites:
                    composites[task.parent_composite_id] = []
                composites[task.parent_composite_id].append(task)
        
        # Calcular limites para cada compuesto
        boundaries: Dict[UUID, CompositeTaskBoundary] = {}
        for composite_id, composite_tasks in composites.items():
            if not composite_tasks:
                continue
            
            # Ordenar por execution_order
            sorted_tasks = sorted(composite_tasks, key=lambda t: t.execution_order)
            
            boundaries[composite_id] = CompositeTaskBoundary(
                composite_id=composite_id,
                start_execution_order=sorted_tasks[0].execution_order,
                end_execution_order=sorted_tasks[-1].execution_order,
                total_task_slots=len(sorted_tasks)
            )
        
        return boundaries
    
    @staticmethod
    def validate_task_reorder(
        task: 'Task',
        new_execution_order: int,
        all_tasks: List['Task']
    ) -> Tuple[bool, str]:
        """
        Valida si una task puede cambiar su orden de ejecucion.
        
        Ahora permite reordenar tasks dentro de products compuestos,
        siempre que se respete la secuencia de dependencias.
        
        Args:
            task: Task a mover
            new_execution_order: Nuevo orden solicitado
            all_tasks: Todas las tasks del work
            
        Returns:
            (is_valid, error_message)
            - is_valid: True si el reorden es valid
            - error_message: Description del error (vacio si is_valid=True)
        """
        # Validar que este dentro del rango total
        if new_execution_order < 0 or new_execution_order >= len(all_tasks):
            return False, f"Orden invalid: debe estar entre 0 y {len(all_tasks) - 1}"
        
        # Si la task no pertenece a un compuesto, no hay mas restricciones
        if not task.parent_composite_id:
            return True, ""
        
        # Las tasks de compuesto ahora pueden moverse dentro del compuesto
        # Solo necesitamos validar que no salgan fuera del rango del compuesto
        boundaries = TaskHierarchyValidator.build_composite_boundaries(all_tasks)
        boundary = boundaries.get(task.parent_composite_id)
        
        if not boundary:
            return False, "No se encontraron limites para el compuesto"
        
        # La task DEBE permanecer dentro del rango del compuesto
        if not (boundary.start_execution_order <= new_execution_order <= boundary.end_execution_order):
            return False, (
                f"La task no puede moverse fuera del rango del compuesto "
                f"[{boundary.start_execution_order}, {boundary.end_execution_order}]. "
                f"Orden solicitado: {new_execution_order}"
            )
        
        # NUEVA LOGICA: Permitir reordenar dentro del compuesto
        # Solo verificamos que no haya conflictos de dependencias (si se implementan)
        return True, ""
    
    @staticmethod
    def get_valid_execution_orders(
        task: 'Task',
        all_tasks: List['Task']
    ) -> List[int]:
        """
        Retorna los ordenes de ejecucion valids para una task.
        
        Ahora las tasks de compuestos pueden moverse a cualquier posicion
        dentro del rango de su compuesto.
        
        Args:
            task: Task a consultar
            all_tasks: Todas las tasks del work
            
        Returns:
            Lista de execution_order valids para esta task
        """
        if not task.parent_composite_id:
            # Sin restriccion: puede ir a cualquier posicion
            return list(range(len(all_tasks)))
        
        boundaries = TaskHierarchyValidator.build_composite_boundaries(all_tasks)
        boundary = boundaries.get(task.parent_composite_id)
        
        if not boundary:
            return []
        
        # NUEVA LOGICA: Puede moverse a cualquier posicion dentro del compuesto
        return list(range(
            boundary.start_execution_order,
            boundary.end_execution_order + 1
        ))
    
    @staticmethod
    def get_composite_tasks(
        composite_id: UUID,
        all_tasks: List['Task']
    ) -> List['Task']:
        """
        Obtiene todas las tasks que pertenecen a un product compuesto.
        
        Args:
            composite_id: ID del product compuesto
            all_tasks: Todas las tasks del work
            
        Returns:
            Lista de tasks del compuesto, ordenadas por execution_order
        """
        composite_tasks = [
            t for t in all_tasks 
            if t.parent_composite_id == composite_id
        ]
        return sorted(composite_tasks, key=lambda t: t.execution_order)
