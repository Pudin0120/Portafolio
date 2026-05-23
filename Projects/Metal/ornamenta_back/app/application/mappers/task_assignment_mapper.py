"""
Mapper for converting between TaskAssignment domain entity and DTOs.
"""
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.domain.models.task_assignment import TaskAssignment
from app.domain.value_objects.money import Money
from app.application.dto.task_assignment_dto import (
    TaskAssignmentDTO,
    TaskAssignmentCreateDTO,
    TaskAssignmentUpdateDTO,
    TaskAssignmentListDTO,
    TaskAssignmentSummaryDTO,
    TaskAssignmentByPayrollDTO
)


class TaskAssignmentMapper:
    """Mapper for TaskAssignment domain entity to DTOs."""
    
    @staticmethod
    def to_dto(task_assignment: TaskAssignment) -> TaskAssignmentDTO:
        """
        Convert TaskAssignment domain entity to TaskAssignmentDTO.
        
        Args:
            task_assignment: TaskAssignment domain entity
            
        Returns:
            TaskAssignmentDTO with all task assignment information
        """
        return TaskAssignmentDTO(
            task_id=task_assignment.task_id,
            identification_number=task_assignment.identification_number,
            payroll_id=task_assignment.payroll_id,
            assigned_date=task_assignment.assigned_date,
            date_deliver_aprox=task_assignment.date_deliver_aprox,
            date_deliver=task_assignment.date_deliver,
            labor_amount=task_assignment.labor.amount,
            labor_formatted=str(task_assignment.labor),
            is_delivered=task_assignment.is_delivered,
            is_overdue=task_assignment.is_overdue
        )
    
    @staticmethod
    def to_dto_list(task_assignments: List[TaskAssignment]) -> TaskAssignmentListDTO:
        """
        Convert list of TaskAssignment domain entities to TaskAssignmentListDTO.
        
        Args:
            task_assignments: List of TaskAssignment domain entities
            
        Returns:
            TaskAssignmentListDTO with list of task assignments and total count
        """
        assignment_dtos = [TaskAssignmentMapper.to_dto(assignment) for assignment in task_assignments]
        return TaskAssignmentListDTO(
            task_assignments=assignment_dtos,
            total_count=len(assignment_dtos)
        )
    
    @staticmethod
    def to_summary_dto(task_assignments: List[TaskAssignment], employee_id: str) -> TaskAssignmentSummaryDTO:
        """
        Convert list of TaskAssignment domain entities to TaskAssignmentSummaryDTO.
        
        Args:
            task_assignments: List of TaskAssignment domain entities
            employee_id: Employee identification number
            
        Returns:
            TaskAssignmentSummaryDTO with assignment statistics
        """
        total_assignments = len(task_assignments)
        delivered_assignments = sum(1 for assignment in task_assignments if assignment.is_delivered)
        overdue_assignments = sum(1 for assignment in task_assignments if assignment.is_overdue)
        pending_assignments = total_assignments - delivered_assignments
        
        total_labor_value = sum(assignment.labor.amount for assignment in task_assignments)
        
        # Calculate average delivery time for delivered assignments
        delivered_with_dates = [
            assignment for assignment in task_assignments 
            if assignment.is_delivered and assignment.date_deliver
        ]
        
        if delivered_with_dates:
            delivery_times = [
                (assignment.date_deliver - assignment.assigned_date).days 
                for assignment in delivered_with_dates
            ]
            average_delivery_time_days = sum(delivery_times) / len(delivery_times)
        else:
            average_delivery_time_days = None
        
        completion_percentage = (delivered_assignments / total_assignments * 100) if total_assignments > 0 else 0.0
        
        return TaskAssignmentSummaryDTO(
            employee_id=employee_id,
            total_assignments=total_assignments,
            delivered_assignments=delivered_assignments,
            overdue_assignments=overdue_assignments,
            pending_assignments=pending_assignments,
            total_labor_value=total_labor_value,
            average_delivery_time_days=average_delivery_time_days,
            completion_percentage=completion_percentage
        )
    
    @staticmethod
    def to_by_payroll_dto(task_assignments: List[TaskAssignment], payroll_id: UUID, identification_number: str) -> TaskAssignmentByPayrollDTO:
        """
        Convert list of TaskAssignment domain entities to TaskAssignmentByPayrollDTO.
        
        Args:
            task_assignments: List of TaskAssignment domain entities for a specific payroll
            payroll_id: Payroll identifier
            identification_number: Employee identification number
            
        Returns:
            TaskAssignmentByPayrollDTO with payroll-specific assignment information
        """
        total_assignments = len(task_assignments)
        delivered_assignments = sum(1 for assignment in task_assignments if assignment.is_delivered)
        total_labor_value = sum(assignment.labor.amount for assignment in task_assignments)
        
        assignment_dtos = [TaskAssignmentMapper.to_dto(assignment) for assignment in task_assignments]
        
        return TaskAssignmentByPayrollDTO(
            payroll_id=payroll_id,
            identification_number=identification_number,
            total_assignments=total_assignments,
            delivered_assignments=delivered_assignments,
            total_labor_value=total_labor_value,
            assignments=assignment_dtos
        )
    
    @staticmethod
    def from_create_dto(create_dto: TaskAssignmentCreateDTO) -> TaskAssignment:
        """
        Convert TaskAssignmentCreateDTO to TaskAssignment domain entity.
        
        Args:
            create_dto: TaskAssignmentCreateDTO with creation data
            
        Returns:
            TaskAssignment domain entity
        """
        # Create Money object
        labor = Money(amount=create_dto.labor_amount)
        
        return TaskAssignment(
            task_id=create_dto.task_id,
            identification_number=create_dto.identification_number,
            payroll_id=create_dto.payroll_id,
            assigned_date=create_dto.assigned_date,
            date_deliver_aprox=create_dto.date_deliver_aprox,
            date_deliver=None,
            labor=labor
        )
    
    @staticmethod
    def apply_update_dto(task_assignment: TaskAssignment, update_dto: TaskAssignmentUpdateDTO) -> TaskAssignment:
        """
        Apply TaskAssignmentUpdateDTO changes to existing TaskAssignment domain entity.
        
        Args:
            task_assignment: Existing TaskAssignment domain entity
            update_dto: TaskAssignmentUpdateDTO with update data
            
        Returns:
            Updated TaskAssignment domain entity
        """
        # Update identification number if provided
        if update_dto.identification_number is not None:
            task_assignment.identification_number = update_dto.identification_number
        
        # Update payroll ID if provided
        if update_dto.payroll_id is not None:
            task_assignment.payroll_id = update_dto.payroll_id
        
        # Update assigned date if provided
        if update_dto.assigned_date is not None:
            task_assignment.assigned_date = update_dto.assigned_date
        
        # Update approximate delivery date if provided
        if update_dto.date_deliver_aprox is not None:
            task_assignment.update_delivery_date(update_dto.date_deliver_aprox)
        
        # Update labor value if provided
        if update_dto.labor_amount is not None:
            task_assignment.labor = Money(amount=update_dto.labor_amount)
        
        return task_assignment
