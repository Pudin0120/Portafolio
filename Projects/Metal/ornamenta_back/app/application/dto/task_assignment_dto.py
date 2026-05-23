"""
DTOs for TaskAssignment API.
"""
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import date
from pydantic import BaseModel, ConfigDict, Field


class TaskAssignmentDTO(BaseModel):
    """DTO for task assignment response."""
    task_id: UUID = Field(..., description="Associated task identifier")
    identification_number: str = Field(..., description="Employee identification number")
    payroll_id: UUID = Field(..., description="Associated payroll identifier")
    assigned_date: date = Field(..., description="Task assignment date")
    date_deliver_aprox: date = Field(..., description="Approximate delivery date")
    date_deliver: Optional[date] = Field(None, description="Actual delivery date")
    labor_amount: Decimal = Field(..., description="Labor value amount in COP")
    labor_formatted: str = Field(..., description="Labor value formatted as string")
    is_delivered: bool = Field(..., description="Whether the task has been delivered")
    is_overdue: bool = Field(..., description="Whether the task is overdue")
    
    model_config = ConfigDict(from_attributes=True)


class TaskAssignmentCreateDTO(BaseModel):
    """DTO for creating a new task assignment."""
    task_id: UUID = Field(..., description="Associated task identifier")
    identification_number: str = Field(..., min_length=1, max_length=20, description="Employee identification number")
    payroll_id: UUID = Field(..., description="Associated payroll identifier")
    assigned_date: date = Field(..., description="Task assignment date")
    date_deliver_aprox: date = Field(..., description="Approximate delivery date")
    labor_amount: Decimal = Field(..., gt=0, description="Labor value amount in COP")


class TaskAssignmentUpdateDTO(BaseModel):
    """DTO for updating an existing task assignment."""
    identification_number: Optional[str] = Field(None, min_length=1, max_length=20, description="Employee identification number")
    payroll_id: Optional[UUID] = Field(None, description="Associated payroll identifier")
    assigned_date: Optional[date] = Field(None, description="Task assignment date")
    date_deliver_aprox: Optional[date] = Field(None, description="Approximate delivery date")
    labor_amount: Optional[Decimal] = Field(None, gt=0, description="Labor value amount in COP")


class TaskAssignmentDeliverDTO(BaseModel):
    """DTO for marking a task assignment as delivered."""
    delivery_date: date = Field(..., description="Actual delivery date")


class TaskAssignmentListDTO(BaseModel):
    """DTO for task assignment list response."""
    task_assignments: List[TaskAssignmentDTO] = Field(..., description="List of task assignments")
    total_count: int = Field(..., description="Total number of task assignments")
    
    model_config = ConfigDict(from_attributes=True)


class TaskAssignmentSummaryDTO(BaseModel):
    """DTO for task assignment summary/statistics."""
    employee_id: str = Field(..., description="Employee identification number")
    total_assignments: int = Field(..., description="Total number of task assignments")
    delivered_assignments: int = Field(..., description="Number of delivered assignments")
    overdue_assignments: int = Field(..., description="Number of overdue assignments")
    pending_assignments: int = Field(..., description="Number of pending assignments")
    total_labor_value: Decimal = Field(..., description="Total labor value of all assignments")
    average_delivery_time_days: Optional[float] = Field(None, description="Average delivery time in days")
    completion_percentage: float = Field(..., description="Assignment completion percentage")
    
    model_config = ConfigDict(from_attributes=True)


class TaskAssignmentByPayrollDTO(BaseModel):
    """DTO for task assignments grouped by payroll."""
    payroll_id: UUID = Field(..., description="Payroll identifier")
    identification_number: str = Field(..., description="Employee identification number")
    total_assignments: int = Field(..., description="Total number of assignments for this payroll")
    delivered_assignments: int = Field(..., description="Number of delivered assignments")
    total_labor_value: Decimal = Field(..., description="Total labor value for this payroll")
    assignments: List[TaskAssignmentDTO] = Field(..., description="List of assignments for this payroll")
    
    model_config = ConfigDict(from_attributes=True)
