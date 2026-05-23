"""
Validador para el reordenamiento de tasks.
"""
from typing import List
from uuid import UUID

from app.domain.models.task import Task
from app.domain.value_objects.product_work_item import ProductWorkItem


class TaskReorderValidator:
    """Validador de reglas de negocio para reordenamiento de tasks."""

    @staticmethod
    def validate_reorder(
        task: Task,
        new_execution_order: int,
        all_tasks: List[Task],
        products: List[ProductWorkItem]
    ) -> None:
        """
        Valida que el reordenamiento de una task sea valid.

        Args:
            task: La task a reordenar
            new_execution_order: El nuevo orden de ejecucion
            all_tasks: Lista de todas las tasks del work
            products: Lista de products del work

        Raises:
            ValueError: Si el reordenamiento no es valid
        """
        # Validar rango basico
        if new_execution_order < 0:
            raise ValueError(
                f"No se puede reordenar task: "
                f"El nuevo orden debe ser >= 0, recibido: {new_execution_order}"
            )

        max_order = len(all_tasks) - 1
        if new_execution_order > max_order:
            raise ValueError(
                f"No se puede reordenar task: "
                f"El nuevo orden debe ser <= {max_order}, recibido: {new_execution_order}"
            )

        # Si es una task de compuesto, validar que no salga del rango del compuesto
        if task.parent_composite_id is not None:
            TaskReorderValidator._validate_composite_task_range(
                task, new_execution_order, all_tasks
            )

    @staticmethod
    def _validate_composite_task_range(
        task: Task,
        new_execution_order: int,
        all_tasks: List[Task]
    ) -> None:
        """
        Valida que una task de compuesto no salga del rango de su compuesto.

        Args:
            task: La task a reordenar (debe ser de un compuesto)
            new_execution_order: El nuevo orden de ejecucion
            all_tasks: Lista de todas las tasks del work

        Raises:
            ValueError: Si el reordenamiento saca la task del rango del compuesto
        """
        # Obtener todas las tasks del mismo compuesto
        composite_tasks = [
            t for t in all_tasks
            if t.parent_composite_id == task.parent_composite_id
        ]

        if not composite_tasks:
            return

        # Obtener el rango del compuesto
        min_order = min(t.execution_order for t in composite_tasks)
        max_order = max(t.execution_order for t in composite_tasks)

        # Validar que el nuevo orden este dentro del rango
        if new_execution_order < min_order or new_execution_order > max_order:
            raise ValueError(
                f"No se puede reordenar task: "
                f"La task pertenece a un compuesto y no puede salir "
                f"fuera del rango del compuesto [{min_order}, {max_order}]. "
                f"Nuevo orden solicitado: {new_execution_order}"
            )
