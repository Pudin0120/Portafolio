"""
Use case for calculating payroll values based on task assignments.
"""
from typing import List
from uuid import UUID
from decimal import Decimal

from app.domain.models.Payroll import Payroll
from app.domain.models.task_assignment import TaskAssignment
from app.domain.repositories.task_assignment_repository import TaskAssignmentRepository
from app.domain.repositories.payroll_repository import PayrollRepository
from app.domain.value_objects.money import Money
from app.domain.value_objects.contract_type import ContractTypeEnum
import logging

logger = logging.getLogger(__name__)


class CalculatePayrollFromTasks:
    """Use case for calculating payroll values based on completed task assignments."""
    
    def __init__(self, task_assignment_repo: TaskAssignmentRepository, payroll_repo: PayrollRepository):
        self.task_assignment_repo = task_assignment_repo
        self.payroll_repo = payroll_repo
    
    def execute(self, payroll_id: UUID) -> Payroll:
        """
        Calculate payroll values based on completed task assignments.
        
        Args:
            payroll_id: Payroll ID to calculate
            
        Returns:
            Updated Payroll with calculated task values
            
        Raises:
            ValueError: If payroll not found or calculation fails
        """
        logger.info(f"Calculating payroll values for payroll {payroll_id}")
        
        try:
            # Get payroll
            payroll = self.payroll_repo.get_by_id(payroll_id)
            if not payroll:
                raise ValueError(f"Payroll {payroll_id} not found")
            
            # Get all task assignments for this payroll
            task_assignments = self.task_assignment_repo.get_by_payroll_id(payroll_id)
            
            # Calculate total labor value from completed tasks
            total_labor_value = Decimal('0')
            completed_task_ids = []
            
            for assignment in task_assignments:
                if assignment.is_delivered:
                    total_labor_value += assignment.labor.amount
                    completed_task_ids.append(assignment.task_id)
            
            # Update payroll with calculated values
            payroll.total_tasks_value = Money(amount=total_labor_value)
            payroll.completed_tasks = completed_task_ids
            
            # Save updated payroll
            updated_payroll = self.payroll_repo.save(payroll)
            
            logger.info(f"Payroll calculated successfully: total_tasks_value={total_labor_value}, completed_tasks={len(completed_task_ids)}")
            
            return updated_payroll
            
        except Exception as e:
            logger.error(f"Error calculating payroll from tasks: {e}")
            raise ValueError(f"Error calculating payroll from tasks: {e}")


class UpdatePayrollFromTaskCompletion:
    """Use case for updating payroll when a task is completed."""
    
    def __init__(self, task_assignment_repo: TaskAssignmentRepository, payroll_repo: PayrollRepository):
        self.task_assignment_repo = task_assignment_repo
        self.payroll_repo = payroll_repo
    
    def execute(self, task_id: UUID) -> Payroll:
        """
        Update payroll when a task is completed and delivered.
        
        Args:
            task_id: Task ID that was completed
            
        Returns:
            Updated Payroll
            
        Raises:
            ValueError: If task assignment or payroll not found
        """
        logger.info(f"Updating payroll for completed task {task_id}")
        
        try:
            # Get task assignment
            assignment = self.task_assignment_repo.get_by_task_id(task_id)
            if not assignment:
                raise ValueError(f"Task assignment for task {task_id} not found")
            
            if not assignment.is_delivered:
                raise ValueError(f"Task {task_id} is not delivered yet")
            
            # Get payroll
            payroll = self.payroll_repo.get_by_id(assignment.payroll_id)
            if not payroll:
                raise ValueError(f"Payroll {assignment.payroll_id} not found")
            
            # Add task to completed tasks if not already there
            if task_id not in payroll.completed_tasks:
                payroll.add_completed_task(task_id)
            
            # Recalculate total tasks value
            task_assignments = self.task_assignment_repo.get_by_payroll_id(assignment.payroll_id)
            total_labor_value = Decimal('0')
            
            for task_assignment in task_assignments:
                if task_assignment.is_delivered:
                    total_labor_value += task_assignment.labor.amount
            
            payroll.update_total_tasks_value(Money(amount=total_labor_value))
            
            # Save updated payroll
            updated_payroll = self.payroll_repo.save(payroll)
            
            logger.info(f"Payroll updated successfully for task {task_id}: total_tasks_value={total_labor_value}")
            
            return updated_payroll
            
        except Exception as e:
            logger.error(f"Error updating payroll from task completion: {e}")
            raise ValueError(f"Error updating payroll from task completion: {e}")


class GetPayrollTaskSummary:
    """Use case for getting payroll task summary."""
    
    def __init__(self, task_assignment_repo: TaskAssignmentRepository, payroll_repo: PayrollRepository):
        self.task_assignment_repo = task_assignment_repo
        self.payroll_repo = payroll_repo
    
    def execute(self, payroll_id: UUID) -> dict:
        """
        Get payroll task summary.
        
        Args:
            payroll_id: Payroll ID
            
        Returns:
            Dictionary with task summary information
            
        Raises:
            ValueError: If payroll not found
        """
        logger.info(f"Getting payroll task summary for payroll {payroll_id}")
        
        try:
            # Get payroll
            payroll = self.payroll_repo.get_by_id(payroll_id)
            if not payroll:
                raise ValueError(f"Payroll {payroll_id} not found")
            
            # Get task assignments
            task_assignments = self.task_assignment_repo.get_by_payroll_id(payroll_id)
            
            # Calculate summary
            total_assignments = len(task_assignments)
            delivered_assignments = sum(1 for assignment in task_assignments if assignment.is_delivered)
            pending_assignments = total_assignments - delivered_assignments
            overdue_assignments = sum(1 for assignment in task_assignments if assignment.is_overdue)
            
            total_labor_value = sum(assignment.labor.amount for assignment in task_assignments)
            delivered_labor_value = sum(assignment.labor.amount for assignment in task_assignments if assignment.is_delivered)
            
            completion_percentage = (delivered_assignments / total_assignments * 100) if total_assignments > 0 else 0.0
            
            summary = {
                "payroll_id": payroll_id,
                "total_assignments": total_assignments,
                "delivered_assignments": delivered_assignments,
                "pending_assignments": pending_assignments,
                "overdue_assignments": overdue_assignments,
                "total_labor_value": total_labor_value,
                "delivered_labor_value": delivered_labor_value,
                "pending_labor_value": total_labor_value - delivered_labor_value,
                "completion_percentage": completion_percentage,
                "payroll_total": payroll.total_payroll.amount,
                "contract_type": payroll.contract_type.value.value,
                "is_service_provision": payroll.contract_type.is_service_provision
            }
            
            logger.info(f"Payroll task summary calculated: {summary}")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting payroll task summary: {e}")
            raise ValueError(f"Error getting payroll task summary: {e}")
