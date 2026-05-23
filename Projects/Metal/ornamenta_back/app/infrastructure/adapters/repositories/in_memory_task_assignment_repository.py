"""
In-memory implementation of TaskAssignmentRepository.

This is a simple in-memory implementation useful for:
- Development and testing
- Temporary storage
"""
from typing import List, Optional, Dict
from datetime import date
import uuid

from app.domain.models.task_assignment import TaskAssignment
from app.domain.repositories.task_assignment_repository import TaskAssignmentRepository


class InMemoryTaskAssignmentRepository(TaskAssignmentRepository):
    """
    In-memory implementation of task assignment repository.
    
    This implementation stores task assignments in memory (lost on restart).
    Suitable for development and testing.
    
    Features:
    - Fast lookups by task_id, payroll_id
    - Support for filtering by date ranges
    
    Limitations:
    - Data lost on restart
    - Memory usage grows with assignment count
    - Not suitable for production
    """
    
    def __init__(self):
        """Initialize the in-memory repository."""
        self._assignments: Dict[uuid.UUID, TaskAssignment] = {}  # task_id -> assignment
        self._by_payroll: Dict[uuid.UUID, List[uuid.UUID]] = {}  # payroll_id -> [task_ids]
        self._by_identification: Dict[str, List[uuid.UUID]] = {}  # identification_number -> [task_ids]
    
    def save(self, task_assignment: TaskAssignment) -> TaskAssignment:
        """
        Save a task assignment.
        
        Args:
            task_assignment: TaskAssignment to save
            
        Returns:
            The saved TaskAssignment
        """
        self._assignments[task_assignment.task_id] = task_assignment
        
        # Index by payroll_id
        if task_assignment.payroll_id not in self._by_payroll:
            self._by_payroll[task_assignment.payroll_id] = []
        if task_assignment.task_id not in self._by_payroll[task_assignment.payroll_id]:
            self._by_payroll[task_assignment.payroll_id].append(task_assignment.task_id)
        
        # Index by identification_number
        if task_assignment.identification_number not in self._by_identification:
            self._by_identification[task_assignment.identification_number] = []
        if task_assignment.task_id not in self._by_identification[task_assignment.identification_number]:
            self._by_identification[task_assignment.identification_number].append(task_assignment.task_id)
        
        return task_assignment
    
    def get_by_task_id(self, task_id: uuid.UUID) -> Optional[TaskAssignment]:
        """
        Get a task assignment by task ID.
        
        Args:
            task_id: Task ID to search for
            
        Returns:
            TaskAssignment if found, None otherwise
        """
        return self._assignments.get(task_id)
    
    def get_by_payroll_id(self, payroll_id: uuid.UUID) -> List[TaskAssignment]:
        """
        Get all task assignments for a specific payroll.
        
        Args:
            payroll_id: Payroll ID to search for
            
        Returns:
            List of TaskAssignments
        """
        task_ids = self._by_payroll.get(payroll_id, [])
        return [self._assignments[task_id] for task_id in task_ids if task_id in self._assignments]
    
    def get_by_identification_number(self, identification_number: str) -> List[TaskAssignment]:
        """
        Get all task assignments for a specific employee.
        
        Args:
            identification_number: Employee identification number
            
        Returns:
            List of TaskAssignments
        """
        task_ids = self._by_identification.get(identification_number, [])
        return [self._assignments[task_id] for task_id in task_ids if task_id in self._assignments]
    
    def get_by_assigned_date_range(self, start_date: date, end_date: date) -> List[TaskAssignment]:
        """
        Get task assignments within an assigned date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of TaskAssignments
        """
        return [
            assignment for assignment in self._assignments.values()
            if start_date <= assignment.assigned_date <= end_date
        ]
    
    def get_by_delivery_date_range(self, start_date: date, end_date: date) -> List[TaskAssignment]:
        """
        Get task assignments within a delivery date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of TaskAssignments
        """
        return [
            assignment for assignment in self._assignments.values()
            if assignment.date_deliver and start_date <= assignment.date_deliver <= end_date
        ]
    
    def get_overdue_assignments(self) -> List[TaskAssignment]:
        """
        Get all overdue task assignments.
        
        Returns:
            List of overdue TaskAssignments
        """
        today = date.today()
        return [
            assignment for assignment in self._assignments.values()
            if not assignment.is_delivered and assignment.date_deliver_aprox < today
        ]
    
    def get_all(self) -> List[TaskAssignment]:
        """
        Get all task assignments.
        
        Returns:
            List of all TaskAssignments
        """
        return list(self._assignments.values())
    
    def delete(self, task_id: uuid.UUID) -> bool:
        """
        Delete a task assignment.
        
        Args:
            task_id: Task ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        if task_id not in self._assignments:
            return False
        
        assignment = self._assignments.pop(task_id)
        
        # Clean up indexes
        if assignment.payroll_id in self._by_payroll:
            self._by_payroll[assignment.payroll_id] = [
                tid for tid in self._by_payroll[assignment.payroll_id] if tid != task_id
            ]
            if not self._by_payroll[assignment.payroll_id]:
                del self._by_payroll[assignment.payroll_id]
        
        if assignment.identification_number in self._by_identification:
            self._by_identification[assignment.identification_number] = [
                tid for tid in self._by_identification[assignment.identification_number] if tid != task_id
            ]
            if not self._by_identification[assignment.identification_number]:
                del self._by_identification[assignment.identification_number]
        
        return True
