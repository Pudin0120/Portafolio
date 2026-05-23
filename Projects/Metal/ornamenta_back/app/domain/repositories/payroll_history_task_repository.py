"""
Repository interface for PayrollHistoryTask entity.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.domain.models.payroll_history_task import PayrollHistoryTask


class PayrollHistoryTaskRepository(ABC):
    """
    Abstract repository for managing PayrollHistoryTask persistence.
    """
    
    @abstractmethod
    def get_by_id(self, association_id: UUID) -> Optional[PayrollHistoryTask]:
        """Get association by ID."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[PayrollHistoryTask]:
        """Get all associations."""
        pass
    
    @abstractmethod
    def get_by_payroll_history_id(self, payroll_history_id: UUID) -> List[PayrollHistoryTask]:
        """
        Get all task associations for a specific payroll history.
        
        Use this to get all tasks that contribute to a payroll period.
        """
        pass
    
    @abstractmethod
    def get_by_task_id(self, task_id: UUID) -> Optional[PayrollHistoryTask]:
        """
        Get the payroll history association for a specific task.
        
        Returns None if the task is not yet associated with any payroll history.
        """
        pass
    
    @abstractmethod
    def exists_by_task_id(self, task_id: UUID) -> bool:
        """
        Check if a task is already associated with a payroll history.
        
        Use this to prevent duplicate associations.
        """
        pass
    
    @abstractmethod
    def get_by_added_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[PayrollHistoryTask]:
        """Get associations added within a date range."""
        pass
    
    @abstractmethod
    def count_by_payroll_history_id(self, payroll_history_id: UUID) -> int:
        """Count how many tasks are associated with a payroll history."""
        pass
    
    @abstractmethod
    def save(self, payroll_history_task: PayrollHistoryTask) -> PayrollHistoryTask:
        """
        Save or update a payroll history task association.
        
        Raises:
            ValueError: If task is already associated with another payroll history.
        """
        pass
    
    @abstractmethod
    def delete(self, association_id: UUID) -> bool:
        """
        Delete a specific association.
        
        Returns:
            True if deleted, False if not found.
        """
        pass
    
    @abstractmethod
    def delete_by_payroll_history_id(self, payroll_history_id: UUID) -> int:
        """
        Delete all task associations for a specific payroll history.
        
        Useful when cancelling a payroll history to free up tasks
        for reassociation.
        
        Returns:
            Number of associations deleted.
        """
        pass
    
    @abstractmethod
    def delete_by_task_id(self, task_id: UUID) -> bool:
        """
        Delete the association for a specific task.
        
        Useful for removing a task from a payroll history before it's paid.
        
        Returns:
            True if deleted, False if not found.
        """
        pass
