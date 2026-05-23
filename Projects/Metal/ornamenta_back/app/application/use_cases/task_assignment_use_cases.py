"""
Use case for managing task assignments.
"""
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.application.dto.task_assignment_dto import (
    TaskAssignmentCreateDTO, 
    TaskAssignmentDTO, 
    TaskAssignmentDeliverDTO,
    TaskAssignmentListDTO,
    TaskAssignmentSummaryDTO,
    TaskAssignmentByPayrollDTO
)
from app.domain.models.task_assignment import TaskAssignment
from app.domain.models.user import User
from app.domain.repositories.task_assignment_repository import TaskAssignmentRepository
from app.domain.repositories.task_repository import TaskRepository
from app.application.mappers.task_assignment_mapper import TaskAssignmentMapper
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class CreateTaskAssignment:
    """Use case for creating a new task assignment."""
    
    def __init__(self, task_assignment_repository: TaskAssignmentRepository, task_repository: TaskRepository):
        self.task_assignment_repository = task_assignment_repository
        self.task_repository = task_repository
    
    def execute(self, create_dto: TaskAssignmentCreateDTO, current_user: Optional[User] = None) -> TaskAssignmentDTO:
        """
        Create a new task assignment.
        
        Args:
            create_dto: Task assignment creation data
            current_user: User creating the assignment (for audit purposes)
            
        Returns:
            TaskAssignmentDTO of the created assignment
            
        Raises:
            HTTPException: If assignment creation fails
        """
        logger.info(f"Creating task assignment for task {create_dto.task_id} and employee {create_dto.identification_number}")
        
        try:
            # Check if task exists
            task = self.task_repository.get_by_id(create_dto.task_id)
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="La task especificada no existe"
                )
            
            # Check if assignment already exists for this task
            existing_assignment = self.task_assignment_repository.get_by_task_id(create_dto.task_id)
            if existing_assignment:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe una asignacion para esta task"
                )
            
            # Convert DTO to domain entity
            task_assignment = TaskAssignmentMapper.from_create_dto(create_dto)
            
            # Save assignment
            saved_assignment = self.task_assignment_repository.save(task_assignment)
            
            # Assign task to user
            task.assign_to(UUID(create_dto.identification_number))  # Assuming identification_number maps to user_id
            self.task_repository.save(task)
            
            logger.info(f"Task assignment created successfully: {saved_assignment.task_id}")
            
            # Convert to DTO and return
            return TaskAssignmentMapper.to_dto(saved_assignment)
            
        except ValueError as e:
            logger.error(f"Validation error creating task assignment: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating task assignment: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor al create la asignacion de task"
            )


class DeliverTaskAssignment:
    """Use case for marking a task assignment as delivered."""
    
    def __init__(self, task_assignment_repository: TaskAssignmentRepository):
        self.task_assignment_repository = task_assignment_repository
    
    def execute(self, task_id: UUID, deliver_dto: TaskAssignmentDeliverDTO, current_user: Optional[User] = None) -> TaskAssignmentDTO:
        """
        Mark a task assignment as delivered.
        
        Args:
            task_id: ID of the task to deliver
            deliver_dto: Delivery data
            current_user: User delivering the task (for audit purposes)
            
        Returns:
            TaskAssignmentDTO of the updated assignment
            
        Raises:
            HTTPException: If delivery fails
        """
        logger.info(f"Delivering task assignment for task {task_id}")
        
        try:
            # Get assignment
            assignment = self.task_assignment_repository.get_by_task_id(task_id)
            if not assignment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No se encontro la asignacion de task especificada"
                )
            
            # Mark as delivered
            assignment.deliver(deliver_dto.delivery_date)
            
            # Save updated assignment
            saved_assignment = self.task_assignment_repository.save(assignment)
            
            logger.info(f"Task assignment delivered successfully: {saved_assignment.task_id}")
            
            # Convert to DTO and return
            return TaskAssignmentMapper.to_dto(saved_assignment)
            
        except ValueError as e:
            logger.error(f"Validation error delivering task assignment: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error delivering task assignment: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor al entregar la task"
            )


class GetTaskAssignmentsByPayroll:
    """Use case for getting task assignments by payroll."""
    
    def __init__(self, task_assignment_repository: TaskAssignmentRepository):
        self.task_assignment_repository = task_assignment_repository
    
    def execute(self, payroll_id: UUID) -> List[TaskAssignmentByPayrollDTO]:
        """
        Get task assignments grouped by payroll.
        
        Args:
            payroll_id: Payroll ID to filter by
            
        Returns:
            List of TaskAssignmentByPayrollDTO
            
        Raises:
            HTTPException: If retrieval fails
        """
        logger.info(f"Getting task assignments for payroll {payroll_id}")
        
        try:
            # Get assignments by payroll
            assignments = self.task_assignment_repository.get_by_payroll_id(payroll_id)
            
            if not assignments:
                return []
            
            # Group by payroll and employee
            payroll_groups = {}
            for assignment in assignments:
                key = (assignment.payroll_id, assignment.identification_number)
                if key not in payroll_groups:
                    payroll_groups[key] = []
                payroll_groups[key].append(assignment)
            
            # Convert to DTOs
            result = []
            for (payroll_id, identification_number), group_assignments in payroll_groups.items():
                dto = TaskAssignmentMapper.to_by_payroll_dto(group_assignments, payroll_id, identification_number)
                result.append(dto)
            
            logger.info(f"Retrieved {len(result)} payroll groups with task assignments")
            return result
            
        except Exception as e:
            logger.error(f"Error getting task assignments by payroll: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor al obtener las asignaciones de tasks"
            )


class GetTaskAssignmentSummary:
    """Use case for getting task assignment summary for an employee."""
    
    def __init__(self, task_assignment_repository: TaskAssignmentRepository):
        self.task_assignment_repository = task_assignment_repository
    
    def execute(self, identification_number: str) -> TaskAssignmentSummaryDTO:
        """
        Get task assignment summary for an employee.
        
        Args:
            identification_number: Employee identification number
            
        Returns:
            TaskAssignmentSummaryDTO with summary statistics
            
        Raises:
            HTTPException: If retrieval fails
        """
        logger.info(f"Getting task assignment summary for employee {identification_number}")
        
        try:
            # Get assignments by employee
            assignments = self.task_assignment_repository.get_by_identification_number(identification_number)
            
            # Convert to summary DTO
            summary = TaskAssignmentMapper.to_summary_dto(assignments, identification_number)
            
            logger.info(f"Retrieved task assignment summary for employee {identification_number}")
            return summary
            
        except Exception as e:
            logger.error(f"Error getting task assignment summary: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor al obtener el resumen de asignaciones"
            )
