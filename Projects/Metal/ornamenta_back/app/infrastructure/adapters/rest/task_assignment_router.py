"""
REST API endpoints for TaskAssignment management.
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide

from app.domain.repositories.task_assignment_repository import TaskAssignmentRepository
from app.domain.repositories.task_repository import TaskRepository
from app.domain.models.user import User
from app.infrastructure.adapters.rest.authorization import get_current_user
from app.application.dto.task_assignment_dto import (
    TaskAssignmentDTO,
    TaskAssignmentListDTO,
    TaskAssignmentCreateDTO,
    TaskAssignmentUpdateDTO,
    TaskAssignmentDeliverDTO,
    TaskAssignmentSummaryDTO,
    TaskAssignmentByPayrollDTO
)
from app.application.use_cases.task_assignment_use_cases import (
    CreateTaskAssignment,
    DeliverTaskAssignment,
    GetTaskAssignmentsByPayroll,
    GetTaskAssignmentSummary
)
from app.infrastructure.containers import Container

router = APIRouter(prefix="/task-assignments", tags=["Task Assignments"])


@router.post("/", response_model=TaskAssignmentDTO)
@inject
def create_task_assignment(
    create_dto: TaskAssignmentCreateDTO,
    current_user: User = Depends(get_current_user),
    task_assignment_repo: TaskAssignmentRepository = Depends(Provide[Container.task_assignment_repository]),
    task_repo: TaskRepository = Depends(Provide[Container.task_repository]),
) -> TaskAssignmentDTO:
    """
    Create a new task assignment.
    
    Args:
        create_dto: Task assignment creation data
        current_user: Current authenticated user
        task_assignment_repo: Task assignment repository
        task_repo: Task repository
        
    Returns:
        TaskAssignmentDTO of the created assignment
    """
    use_case = CreateTaskAssignment(task_assignment_repo, task_repo)
    return use_case.execute(create_dto, current_user)


@router.get("/task/{task_id}", response_model=TaskAssignmentDTO)
@inject
def get_task_assignment(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    task_assignment_repo: TaskAssignmentRepository = Depends(Provide[Container.task_assignment_repository]),
) -> TaskAssignmentDTO:
    """
    Get task assignment by task ID.
    
    Args:
        task_id: Task ID
        current_user: Current authenticated user
        task_assignment_repo: Task assignment repository
        
    Returns:
        TaskAssignmentDTO of the assignment
    """
    assignment = task_assignment_repo.get_by_task_id(task_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontro la asignacion de task especificada"
        )
    
    from app.application.mappers.task_assignment_mapper import TaskAssignmentMapper
    return TaskAssignmentMapper.to_dto(assignment)


@router.get("/payroll/{payroll_id}", response_model=list[TaskAssignmentByPayrollDTO])
@inject
def get_task_assignments_by_payroll(
    payroll_id: UUID,
    current_user: User = Depends(get_current_user),
    task_assignment_repo: TaskAssignmentRepository = Depends(Provide[Container.task_assignment_repository]),
) -> list[TaskAssignmentByPayrollDTO]:
    """
    Get task assignments grouped by payroll.
    
    Args:
        payroll_id: Payroll ID
        current_user: Current authenticated user
        task_assignment_repo: Task assignment repository
        
    Returns:
        List of TaskAssignmentByPayrollDTO
    """
    use_case = GetTaskAssignmentsByPayroll(task_assignment_repo)
    return use_case.execute(payroll_id)


@router.get("/employee/{identification_number}/summary", response_model=TaskAssignmentSummaryDTO)
@inject
def get_task_assignment_summary(
    identification_number: str,
    current_user: User = Depends(get_current_user),
    task_assignment_repo: TaskAssignmentRepository = Depends(Provide[Container.task_assignment_repository]),
) -> TaskAssignmentSummaryDTO:
    """
    Get task assignment summary for an employee.
    
    Args:
        identification_number: Employee identification number
        current_user: Current authenticated user
        task_assignment_repo: Task assignment repository
        
    Returns:
        TaskAssignmentSummaryDTO with summary statistics
    """
    use_case = GetTaskAssignmentSummary(task_assignment_repo)
    return use_case.execute(identification_number)


@router.post("/task/{task_id}/deliver", response_model=TaskAssignmentDTO)
@inject
def deliver_task_assignment(
    task_id: UUID,
    deliver_dto: TaskAssignmentDeliverDTO,
    current_user: User = Depends(get_current_user),
    task_assignment_repo: TaskAssignmentRepository = Depends(Provide[Container.task_assignment_repository]),
) -> TaskAssignmentDTO:
    """
    Mark a task assignment as delivered.
    
    Args:
        task_id: Task ID
        deliver_dto: Delivery data
        current_user: Current authenticated user
        task_assignment_repo: Task assignment repository
        
    Returns:
        TaskAssignmentDTO of the updated assignment
    """
    use_case = DeliverTaskAssignment(task_assignment_repo)
    return use_case.execute(task_id, deliver_dto, current_user)


@router.get("/employee/{identification_number}", response_model=TaskAssignmentListDTO)
@inject
def get_task_assignments_by_employee(
    identification_number: str,
    current_user: User = Depends(get_current_user),
    task_assignment_repo: TaskAssignmentRepository = Depends(Provide[Container.task_assignment_repository]),
) -> TaskAssignmentListDTO:
    """
    Get all task assignments for a specific employee.
    
    Args:
        identification_number: Employee identification number
        current_user: Current authenticated user
        task_assignment_repo: Task assignment repository
        
    Returns:
        TaskAssignmentListDTO with list of assignments
    """
    try:
        assignments = task_assignment_repo.get_by_identification_number(identification_number)
        from app.application.mappers.task_assignment_mapper import TaskAssignmentMapper
        return TaskAssignmentMapper.to_dto_list(assignments)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener las asignaciones del empleado"
        )


@router.get("/overdue", response_model=TaskAssignmentListDTO)
@inject
def get_overdue_task_assignments(
    current_user: User = Depends(get_current_user),
    task_assignment_repo: TaskAssignmentRepository = Depends(Provide[Container.task_assignment_repository]),
) -> TaskAssignmentListDTO:
    """
    Get all overdue task assignments.
    
    Args:
        current_user: Current authenticated user
        task_assignment_repo: Task assignment repository
        
    Returns:
        TaskAssignmentListDTO with list of overdue assignments
    """
    try:
        assignments = task_assignment_repo.get_overdue_assignments()
        from app.application.mappers.task_assignment_mapper import TaskAssignmentMapper
        return TaskAssignmentMapper.to_dto_list(assignments)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener las asignaciones vencidas"
        )


@router.put("/task/{task_id}", response_model=TaskAssignmentDTO)
@inject
def update_task_assignment(
    task_id: UUID,
    update_dto: TaskAssignmentUpdateDTO,
    current_user: User = Depends(get_current_user),
    task_assignment_repo: TaskAssignmentRepository = Depends(Provide[Container.task_assignment_repository]),
) -> TaskAssignmentDTO:
    """
    Update a task assignment.
    
    Args:
        task_id: Task ID
        update_dto: Update data
        current_user: Current authenticated user
        task_assignment_repo: Task assignment repository
        
    Returns:
        TaskAssignmentDTO of the updated assignment
    """
    try:
        # Get existing assignment
        assignment = task_assignment_repo.get_by_task_id(task_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontro la asignacion de task especificada"
            )
        
        # Apply updates
        from app.application.mappers.task_assignment_mapper import TaskAssignmentMapper
        updated_assignment = TaskAssignmentMapper.apply_update_dto(assignment, update_dto)
        
        # Save updated assignment
        saved_assignment = task_assignment_repo.save(updated_assignment)
        
        return TaskAssignmentMapper.to_dto(saved_assignment)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al actualizar la asignacion de task"
        )
