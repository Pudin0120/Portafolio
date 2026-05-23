"""
DTOs for Task API.
"""
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class TaskDTO(BaseModel):
    """DTO for task response with hierarchy information."""
    task_id: UUID = Field(..., description="Unique task identifier")
    work_id: UUID = Field(..., description="Associated work identifier")
    product_id: UUID = Field(..., description="Product identifier that generated this task")
    parent_composite_id: Optional[UUID] = Field(None, description="Parent composite product ID (if task belongs to a composite)")
    composite_task_slot: Optional[int] = Field(None, description="Position within the composite product (0, 1, 2...)")
    composite_total_slots: Optional[int] = Field(None, description="Total tasks in the composite product")
    task_name: str = Field(..., description="Task name")
    description: str = Field(..., description="Task description")
    state: str = Field(..., description="Task state (S=SIN_INICIAR, P=EN_PROCESO, F=FINALIZADA)")
    labor_amount: Decimal = Field(..., description="Labor value amount in COP")
    labor_formatted: str = Field(..., description="Labor value formatted as string")
    estimated_value_amount: Decimal = Field(..., description="Estimated value amount in COP")
    estimated_value_formatted: str = Field(..., description="Estimated value formatted as string")
    execution_order: int = Field(..., description="Execution order within the work")
    is_blocked: bool = Field(..., description="Whether the task is blocked by a previous task")
    previous_task_id: Optional[UUID] = Field(None, description="ID of the task that blocks this one")
    assigned_user_id: Optional[str] = Field(None, description="Assigned user identifier (firebase_uid)")
    is_assigned: bool = Field(..., description="Whether the task is assigned to a user")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class TaskHierarchyInfoDTO(BaseModel):
    """DTO for task hierarchy information."""
    task: TaskDTO = Field(..., description="The task itself")
    parent_composite_id: Optional[UUID] = Field(None, description="Parent composite product ID")
    current_slot: Optional[int] = Field(None, description="Current slot position within composite")
    total_slots: Optional[int] = Field(None, description="Total slots in composite")
    valid_execution_orders: List[int] = Field(..., description="Valid execution orders for this task")
    can_be_reordered: bool = Field(..., description="Whether the task can be reordered")
    sibling_task_ids: List[UUID] = Field(..., description="IDs of sibling tasks (same composite)")
    
    model_config = ConfigDict(from_attributes=True)


class TaskCreateDTO(BaseModel):
    """DTO for creating a new task."""
    work_id: UUID = Field(..., description="Associated work identifier")
    task_name: str = Field(..., min_length=1, max_length=255, description="Task name")
    description: str = Field(..., min_length=1, max_length=1000, description="Task description")
    labor_amount: Decimal = Field(..., gt=0, description="Labor value amount in COP")
    estimated_value_amount: Decimal = Field(..., gt=0, description="Estimated value amount in COP")


class TaskUpdateDTO(BaseModel):
    """DTO for updating an existing task."""
    task_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Task name")
    description: Optional[str] = Field(None, min_length=1, max_length=1000, description="Task description")
    labor_amount: Optional[Decimal] = Field(None, gt=0, description="Labor value amount in COP")
    estimated_value_amount: Optional[Decimal] = Field(None, gt=0, description="Estimated value amount in COP")


class TaskAssignDTO(BaseModel):
    """DTO for assigning a task to a user."""
    user_id: str = Field(..., description="User identifier to assign the task to (UUID or string)")


class TaskStateChangeDTO(BaseModel):
    """DTO for changing task state."""
    new_state: str = Field(..., description="New task state (S=SIN_INICIAR, P=EN_PROCESO, F=FINALIZADA)")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for state change")


class TaskListDTO(BaseModel):
    """DTO for task list response."""
    tasks: List[TaskDTO] = Field(..., description="List of tasks")
    total_count: int = Field(..., description="Total number of tasks")
    
    model_config = ConfigDict(from_attributes=True)


class TaskSummaryDTO(BaseModel):
    """DTO for task summary/statistics."""
    work_id: UUID = Field(..., description="Work identifier")
    total_tasks: int = Field(..., description="Total number of tasks")
    tasks_sin_iniciar: int = Field(..., description="Number of tasks not started")
    tasks_en_proceso: int = Field(..., description="Number of tasks in progress")
    tasks_finalizadas: int = Field(..., description="Number of completed tasks")
    total_labor_value: Decimal = Field(..., description="Total labor value of all tasks")
    total_estimated_value: Decimal = Field(..., description="Total estimated value of all tasks")
    completion_percentage: float = Field(..., description="Task completion percentage")
    
    model_config = ConfigDict(from_attributes=True)


class TaskReorderDTO(BaseModel):
    """DTO for reordering a task."""
    new_execution_order: int = Field(..., ge=0, description="New execution order for the task")


class CompositeTaskGroupDTO(BaseModel):
    """DTO for a group of tasks belonging to a composite product."""
    composite_id: Optional[UUID] = Field(None, description="Composite product ID (None for standalone tasks)")
    composite_name: Optional[str] = Field(None, description="Composite product name with multiplier (e.g., 'Ventana (x2)')")
    tasks: List[TaskDTO] = Field(..., description="Tasks in this composite")
    start_execution_order: int = Field(..., description="First execution order in the group")
    end_execution_order: int = Field(..., description="Last execution order in the group")
    
    model_config = ConfigDict(from_attributes=True)


class TaskHierarchyListDTO(BaseModel):
    """DTO for hierarchical task list response."""
    work_id: UUID = Field(..., description="Work identifier")
    total_tasks: int = Field(..., description="Total number of tasks")
    composite_groups: List[CompositeTaskGroupDTO] = Field(..., description="Tasks grouped by composite product")
    
    model_config = ConfigDict(from_attributes=True)
