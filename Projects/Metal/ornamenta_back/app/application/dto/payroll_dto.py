"""
DTOs for Payroll API.
"""
from datetime import date
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class PayrollDTO(BaseModel):
    """DTO for payroll response."""
    payroll_id: UUID = Field(..., description="Unique identifier for the payroll")
    identification_number: Optional[str] = Field(None, description="Employee identification number (from history)")
    contract_type: str = Field(..., description="Type of contract (FIXED_TERM, INDEFINITE_TERM, SERVICE_PROVISION)")
    state: str = Field(..., description="Current state of the payroll (LIQUIDATED, ACTIVE, PAID, CANCELLED)")
    base_salary_amount: Decimal = Field(..., description="Base salary amount in COP")
    base_salary_formatted: str = Field(..., description="Base salary formatted as string")
    
    # Current period calculated salary (from latest PayrollHistory)
    current_period_salary: Optional[Decimal] = Field(None, description="Calculated salary from current period (from latest PayrollHistory)")
    current_period_salary_formatted: Optional[str] = Field(None, description="Formatted calculated salary from current period")
    current_period_start_date: Optional[date] = Field(None, description="Start date of current period")
    current_period_end_date: Optional[date] = Field(None, description="End date of current period")
    
    # State properties for convenience
    is_liquidated: bool = Field(..., description="Whether the payroll is liquidated")
    is_active: bool = Field(..., description="Whether the payroll is active")
    is_paid: bool = Field(..., description="Whether the payroll is paid")
    is_cancelled: bool = Field(..., description="Whether the payroll is cancelled")
    
    # Contract type properties for convenience
    is_fixed_term: bool = Field(..., description="Whether the contract is fixed term")
    is_indefinite_term: bool = Field(..., description="Whether the contract is indefinite term")
    is_service_provision: bool = Field(..., description="Whether the contract is service provision")
    
    model_config = ConfigDict(from_attributes=True)


class PayrollCreateDTO(BaseModel):
    """DTO for creating a new payroll."""
    contract_type: str = Field(..., description="Type of contract")
    state: str = Field(default="ACTIVE", description="Initial state of the payroll")
    base_salary_amount: Decimal = Field(..., description="Base salary amount in COP")
    identification_number: str = Field(..., description="Employee identification number")
    start_date: date = Field(..., description="Start date of the payroll period (Required)")
    end_date: Optional[date] = Field(None, description="End date of the payroll period (Optional)")


class PayrollUpdateDTO(BaseModel):
    """DTO for updating an existing payroll."""
    contract_type: Optional[str] = Field(None, description="Type of contract")
    state: Optional[str] = Field(None, description="State of the payroll")
    base_salary_amount: Optional[Decimal] = Field(None, description="Base salary amount in COP")


class PayrollListDTO(BaseModel):
    """DTO for payroll list response."""
    payrolls: List[PayrollDTO] = Field(..., description="List of payrolls")
    total_count: int = Field(..., description="Total number of payrolls")
    
    model_config = ConfigDict(from_attributes=True)


class PayrollTaskSummaryItemDTO(BaseModel):
    """DTO for a single task type summary in a payroll."""
    task_name: str = Field(..., description="Name of the task")
    task_count: int = Field(..., description="Number of times this task appears")
    labor_cost_per_task: Decimal = Field(..., description="Labor cost per single task instance")
    labor_cost_per_task_formatted: str = Field(..., description="Labor cost per task formatted")
    total_labor_cost: Decimal = Field(..., description="Total labor cost (task_count * labor_cost_per_task)")
    total_labor_cost_formatted: str = Field(..., description="Total labor cost formatted")
    
    model_config = ConfigDict(from_attributes=True)


class PayrollServiceProvisionTasksDTO(BaseModel):
    """DTO for service provision payroll tasks summary."""
    payroll_id: UUID = Field(..., description="Unique identifier for the payroll")
    payroll_history_id: UUID = Field(..., description="Payroll history ID for this period")
    identification_number: str = Field(..., description="Employee identification number")
    period_start_date: date = Field(..., description="Start date of the payroll period")
    period_end_date: date = Field(..., description="End date of the payroll period")
    contract_type: str = Field(..., description="Contract type (should be SERVICE_PROVISION)")
    
    # Task summary
    tasks_summary: List[PayrollTaskSummaryItemDTO] = Field(..., description="Summary of tasks grouped by name")
    total_tasks_count: int = Field(..., description="Total number of tasks completed")
    total_labor_cost: Decimal = Field(..., description="Sum of all labor costs")
    total_labor_cost_formatted: str = Field(..., description="Total labor cost formatted")
    
    model_config = ConfigDict(from_attributes=True)
