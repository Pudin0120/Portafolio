"""
Mapper for converting between Task domain entity and DTOs.
"""
from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from app.domain.models.task import Task
from app.domain.value_objects.state_task import StateTask, StateTaskEnum
from app.domain.value_objects.money import Money
from app.application.dto.task_dto import (
    TaskDTO,
    TaskCreateDTO,
    TaskUpdateDTO,
    TaskListDTO,
    TaskSummaryDTO,
    TaskHierarchyInfoDTO,
    CompositeTaskGroupDTO,
    TaskHierarchyListDTO
)


class TaskMapper:
    """Mapper for Task domain entity to DTOs."""
    
    @staticmethod
    def to_dto(task: Task) -> TaskDTO:
        """
        Convert Task domain entity to TaskDTO.
        
        Args:
            task: Task domain entity
            
        Returns:
            TaskDTO with all task information including hierarchy
        """
        return TaskDTO(
            task_id=task.task_id,
            work_id=task.work_id,
            product_id=task.product_id,
            parent_composite_id=task.parent_composite_id,
            composite_task_slot=task.composite_task_slot,
            composite_total_slots=task.composite_total_slots,
            task_name=task.task_name,
            description=task.description,
            state=task.state.value.value,
            labor_amount=task.labor.amount,
            labor_formatted=str(task.labor),
            estimated_value_amount=task.estimated_value.amount,
            estimated_value_formatted=str(task.estimated_value),
            execution_order=task.execution_order,
            is_blocked=task.is_blocked,
            previous_task_id=task.previous_task_id,
            assigned_user_id=task.assigned_user_id,
            is_assigned=task.is_assigned,
            updated_at=task.updated_at
        )
    
    @staticmethod
    def to_dto_list(tasks: List[Task]) -> TaskListDTO:
        """
        Convert list of Task domain entities to TaskListDTO.
        
        Args:
            tasks: List of Task domain entities
            
        Returns:
            TaskListDTO with list of tasks and total count
        """
        task_dtos = [TaskMapper.to_dto(task) for task in tasks]
        return TaskListDTO(
            tasks=task_dtos,
            total_count=len(task_dtos)
        )
    
    @staticmethod
    def to_summary_dto(tasks: List[Task], work_id: UUID) -> TaskSummaryDTO:
        """
        Convert list of Task domain entities to TaskSummaryDTO.
        
        Args:
            tasks: List of Task domain entities
            work_id: Work identifier
            
        Returns:
            TaskSummaryDTO with task statistics
        """
        total_tasks = len(tasks)
        tasks_sin_iniciar = sum(1 for task in tasks if task.is_sin_iniciar)
        tasks_en_proceso = sum(1 for task in tasks if task.is_en_proceso)
        tasks_finalizadas = sum(1 for task in tasks if task.is_finalizada)
        
        total_labor_value = Decimal(sum(task.labor.amount for task in tasks)) if tasks else Decimal("0")
        total_estimated_value = Decimal(sum(task.estimated_value.amount for task in tasks)) if tasks else Decimal("0")
        
        completion_percentage = (tasks_finalizadas / total_tasks * 100) if total_tasks > 0 else 0.0
        
        return TaskSummaryDTO(
            work_id=work_id,
            total_tasks=total_tasks,
            tasks_sin_iniciar=tasks_sin_iniciar,
            tasks_en_proceso=tasks_en_proceso,
            tasks_finalizadas=tasks_finalizadas,
            total_labor_value=total_labor_value,
            total_estimated_value=total_estimated_value,
            completion_percentage=completion_percentage
        )
    
    @staticmethod
    def from_create_dto(create_dto: TaskCreateDTO, task_id: UUID) -> Task:
        """
        Convert TaskCreateDTO to Task domain entity.
        
        Args:
            create_dto: TaskCreateDTO with creation data
            task_id: UUID for the new task
            
        Returns:
            Task domain entity
            
        Raises:
            ValueError: If state is invalid
        """
        # Create Money objects
        labor = Money(amount=create_dto.labor_amount)
        estimated_value = Money(amount=create_dto.estimated_value_amount)
        
        # Default state is PENDING
        state = StateTask(value=StateTaskEnum.PENDING)
        
        # Note: This creates a task without product_id, which should be provided by the caller
        # This is a legacy method and should probably be deprecated
        return Task(
            task_id=task_id,
            work_id=create_dto.work_id,
            product_id=task_id,  # Placeholder - should be provided by caller
            task_name=create_dto.task_name,
            description=create_dto.description,
            state=state,
            labor=labor,
            estimated_value=estimated_value,
            execution_order=0,  # Default order
            assigned_user_id=None
        )
    
    @staticmethod
    def apply_update_dto(task: Task, update_dto: TaskUpdateDTO) -> Task:
        """
        Apply TaskUpdateDTO changes to existing Task domain entity.
        
        Args:
            task: Existing Task domain entity
            update_dto: TaskUpdateDTO with update data
            
        Returns:
            Updated Task domain entity
        """
        # Update task name if provided
        if update_dto.task_name is not None:
            task.task_name = update_dto.task_name
        
        # Update description if provided
        if update_dto.description is not None:
            task.description = update_dto.description
        
        # Update labor value if provided
        if update_dto.labor_amount is not None:
            task.labor = Money(amount=update_dto.labor_amount)
        
        # Update estimated value if provided
        if update_dto.estimated_value_amount is not None:
            task.estimated_value = Money(amount=update_dto.estimated_value_amount)
        
        return task
    
    @staticmethod
    def to_hierarchy_info_dto(hierarchy_info: dict, task_dto: TaskDTO) -> TaskHierarchyInfoDTO:
        """
        Convert task hierarchy information to DTO.
        
        Args:
            hierarchy_info: Dictionary with hierarchy information from Work.get_task_hierarchy_info()
            task_dto: TaskDTO of the task
            
        Returns:
            TaskHierarchyInfoDTO with complete hierarchy information
        """
        sibling_task_ids = [t.task_id for t in hierarchy_info.get('sibling_tasks', [])]
        
        return TaskHierarchyInfoDTO(
            task=task_dto,
            parent_composite_id=hierarchy_info.get('parent_composite_id'),
            current_slot=hierarchy_info.get('current_slot'),
            total_slots=hierarchy_info.get('total_slots'),
            valid_execution_orders=hierarchy_info.get('valid_execution_orders', []),
            can_be_reordered=hierarchy_info.get('can_be_reordered', False),
            sibling_task_ids=sibling_task_ids
        )
    
    @staticmethod
    def to_hierarchy_list_dto(
        work_id: UUID,
        composite_groups: dict,
        products_registry: Optional[dict] = None
    ) -> TaskHierarchyListDTO:
        """
        Convert composite task groups to hierarchical list DTO.
        
        Args:
            work_id: Work identifier
            composite_groups: Dictionary from Work.get_composite_task_groups()
            products_registry: Optional dictionary of products for getting names
            
        Returns:
            TaskHierarchyListDTO with grouped tasks
        """
        import re
        
        group_dtos = []
        total_tasks = 0
        
        for composite_id, tasks in composite_groups.items():
            if not tasks:
                continue
            
            total_tasks += len(tasks)
            task_dtos = [TaskMapper.to_dto(task) for task in tasks]
            
            # Get composite product name if available
            composite_name = None
            if composite_id and products_registry:
                product = products_registry.get(composite_id)
                if product:
                    composite_name = product.name
            
            # Extract multiplier from the first task's name
            # Task names are like "Vidrio (x20)" or "Puerta (x1)"
            # We want to extract the (xN) part
            multiplier_str = None
            if tasks:
                first_task_name = tasks[0].task_name
                match = re.search(r'\(x(\d+)\)', first_task_name)
                if match:
                    multiplier_str = f"(x{match.group(1)})"
            
            # Append multiplier to composite name if available
            if composite_name and multiplier_str:
                composite_name = f"{composite_name} {multiplier_str}"
            
            # Calculate execution order range
            start_order = min(task.execution_order for task in tasks)
            end_order = max(task.execution_order for task in tasks)
            
            group_dto = CompositeTaskGroupDTO(
                composite_id=composite_id,
                composite_name=composite_name,
                tasks=task_dtos,
                start_execution_order=start_order,
                end_execution_order=end_order
            )
            group_dtos.append(group_dto)
        
        # Sort groups by start execution order
        group_dtos.sort(key=lambda g: g.start_execution_order)
        
        return TaskHierarchyListDTO(
            work_id=work_id,
            total_tasks=total_tasks,
            composite_groups=group_dtos
        )
    
    @staticmethod
    def parse_state(state_str: str) -> StateTask:
        """
        Parse state string to StateTask value object.
        
        Args:
            state_str: State string (S, P, F)
            
        Returns:
            StateTask value object
            
        Raises:
            ValueError: If state string is invalid
        """
        try:
            state_enum = StateTaskEnum(state_str)
            return StateTask(value=state_enum)
        except ValueError:
            raise ValueError(f"Invalid task state: {state_str}. Valid states are: S (SIN_INICIAR), P (EN_PROCESO), F (FINALIZADA)")
