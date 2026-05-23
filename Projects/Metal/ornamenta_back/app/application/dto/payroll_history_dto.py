"""
DTOs for PayrollHistory API.
"""
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import date
from pydantic import BaseModel, ConfigDict, Field, ConfigDict


class PayrollHistoryDTO(BaseModel):
    """DTO for payroll history response."""
    identification_number: str = Field(..., description="Employee identification number")
    payroll_id: UUID = Field(..., description="Associated payroll ID")
    security_id: str = Field(..., description="Security/social security ID")
    works_value_amount: Decimal = Field(..., description="Works value amount in COP")
    works_value_formatted: str = Field(..., description="Works value formatted as string")
    init_date: date = Field(..., description="Period start date")
    end_date: date = Field(..., description="Period end date")
    
    model_config = ConfigDict(from_attributes=True)


class PayrollHistoryCreateDTO(BaseModel):
    """DTO for creating a new payroll history record."""
    identification_number: str = Field(..., description="Employee identification number")
    payroll_id: UUID = Field(..., description="Associated payroll ID")
    security_id: str = Field(..., description="Security/social security ID")
    works_value_amount: Decimal = Field(..., description="Works value amount in COP")
    init_date: date = Field(..., description="Period start date")
    end_date: date = Field(..., description="Period end date")


class PayrollHistoryUpdateDTO(BaseModel):
    """DTO for updating an existing payroll history record."""
    identification_number: Optional[str] = Field(None, description="Employee identification number")
    payroll_id: Optional[UUID] = Field(None, description="Associated payroll ID")
    security_id: Optional[str] = Field(None, description="Security/social security ID")
    works_value_amount: Optional[Decimal] = Field(None, description="Works value amount in COP")
    init_date: Optional[date] = Field(None, description="Period start date")
    end_date: Optional[date] = Field(None, description="Period end date")


class PayrollHistoryListDTO(BaseModel):
    """DTO for payroll history list response."""
    payroll_histories: List[PayrollHistoryDTO] = Field(..., description="List of payroll history records")
    total_count: int = Field(..., description="Total number of payroll history records")
    
    model_config = ConfigDict(from_attributes=True)


class PayrollHistorySummaryDTO(BaseModel):
    """DTO for payroll history summary/statistics."""
    employee_id: str = Field(..., description="Employee identification number")
    total_records: int = Field(..., description="Total number of payroll history records")
    total_works_value: Decimal = Field(..., description="Total works value across all records")
    model_config = ConfigDict(from_attributes=True)
