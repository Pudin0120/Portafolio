"""
Repository interface for PayrollHistory entity.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.domain.models.payroll_history import PayrollHistory


class PayrollHistoryRepository(ABC):
    """
    Abstract repository for managing PayrollHistory persistence.
    """
    
    @abstractmethod
    def get_by_id(self, history_id: UUID) -> Optional[PayrollHistory]:
        """Get payroll history by UUID (if we add an ID field later)."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[PayrollHistory]:
        """Get all payroll history records."""
        pass
    
    @abstractmethod
    def get_by_identification_number(self, identification_number: str) -> List[PayrollHistory]:
        """Get payroll history records by employee identification number."""
        pass
    
    @abstractmethod
    def get_by_payroll_id(self, payroll_id: UUID) -> List[PayrollHistory]:
        """Get payroll history records by payroll ID."""
        pass
    
    @abstractmethod
    def get_by_security_id(self, security_id: str) -> List[PayrollHistory]:
        """Get payroll history records by security ID."""
        pass
    
    @abstractmethod
    def get_by_date_range(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[PayrollHistory]:
        """Get payroll history records within a date range."""
        pass
    
    @abstractmethod
    def get_by_employee_and_date_range(
        self, 
        identification_number: str, 
        start_date: date, 
        end_date: date
    ) -> List[PayrollHistory]:
        """Get payroll history records for a specific employee within a date range."""
        pass
    
    @abstractmethod
    def get_by_init_date(self, init_date: date) -> List[PayrollHistory]:
        """Get payroll history records by initial date."""
        pass
    
    @abstractmethod
    def get_by_end_date(self, end_date: date) -> List[PayrollHistory]:
        """Get payroll history records by end date."""
        pass
    
    @abstractmethod
    def get_latest_by_employee(self, identification_number: str) -> Optional[PayrollHistory]:
        """Get the latest payroll history record for an employee."""
        pass
    
    @abstractmethod
    def get_latest_service_provision_history_by_employee(self, identification_number: str) -> Optional[PayrollHistory]:
        """
        Get the latest active SERVICE_PROVISION payroll history record for an employee.
        Only returns histories where the payroll is SERVICE_PROVISION and ACTIVE.
        """
        pass
    
    @abstractmethod
    def get_earliest_by_employee(self, identification_number: str) -> Optional[PayrollHistory]:
        """Get the earliest payroll history record for an employee."""
        pass
    
    @abstractmethod
    def get_by_minimum_works_value(self, min_value: float) -> List[PayrollHistory]:
        """Get payroll history records with works value greater than or equal to minimum."""
        pass
    
    @abstractmethod
    def save(self, payroll_history: PayrollHistory) -> PayrollHistory:
        """Save or update a payroll history record."""
        pass
    
    @abstractmethod
    def delete(self, history_id: UUID) -> bool:
        """Delete a payroll history record by ID (if we add an ID field later)."""
        pass
    
    @abstractmethod
    def delete_by_payroll_id(self, payroll_id: UUID) -> int:
        """Delete all payroll history records for a specific payroll ID."""
        pass
    
    @abstractmethod
    def delete_by_employee(self, identification_number: str) -> int:
        """Delete all payroll history records for a specific employee."""
        pass
    
    @abstractmethod
    def exists_by_payroll_id(self, payroll_id: UUID) -> bool:
        """Check if payroll history records exist for a specific payroll ID."""
        pass
    
    @abstractmethod
    def exists_by_employee(self, identification_number: str) -> bool:
        """Check if payroll history records exist for a specific employee."""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Get total count of payroll history records."""
        pass
    
    @abstractmethod
    def count_by_employee(self, identification_number: str) -> int:
        """Get count of payroll history records for a specific employee."""
        pass
    
    @abstractmethod
    def count_by_payroll_id(self, payroll_id: UUID) -> int:
        """Get count of payroll history records for a specific payroll ID."""
        pass
    
    @abstractmethod
    def count_by_date_range(self, start_date: date, end_date: date) -> int:
        """Get count of payroll history records within a date range."""
        pass
    
    @abstractmethod
    def get_employee_summary(self, identification_number: str) -> dict:
        """
        Get summary statistics for an employee's payroll history.
        
        Returns:
            dict: {
                'total_records': int,
                'total_works_value': float,
                'earliest_date': date,
                'latest_date': date,
                'total_days': int
            }
        """
        pass

