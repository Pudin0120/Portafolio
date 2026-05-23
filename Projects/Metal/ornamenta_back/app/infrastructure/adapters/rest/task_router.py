"""
REST API endpoints for Task management.
"""
from uuid import UUID
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from dependency_injector.wiring import inject, Provide
from app.application.use_cases.update_payroll_task import (
    UpdatePayrollHistoryOnTaskCompletionV2
)
from app.application.use_cases.update_payroll_task import (
    UpdatePayrollHistoryOnTaskCompletionV2
)
from app.domain.repositories.task_repository import TaskRepository
from app.domain.models.user import User, RoleEnum
from app.infrastructure.adapters.rest.authorization import get_current_user
from app.application.dto.task_dto import (
    TaskDTO,
    TaskListDTO,
    TaskCreateDTO,
    TaskUpdateDTO,
    TaskAssignDTO,
    TaskStateChangeDTO,
    TaskSummaryDTO
)
from app.application.use_cases.create_task import CreateTask
from app.application.use_cases.task_use_cases import (
    GetTask,
    GetTasksByWork,
    GetTaskSummary,
    UpdateTask,
    AssignTask,
    ChangeTaskState,
    FinishTask,
    CompleteTask,
    ValidateTask
)
from app.infrastructure.containers import Container
from app.domain.repositories.payroll_history_repository import PayrollHistoryRepository
from app.domain.repositories.payroll_repository import PayrollRepository
from app.domain.repositories.payroll_history_task_repository import PayrollHistoryTaskRepository

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/", response_model=TaskListDTO)
@inject
def get_all_tasks(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio del rango (formato ISO: YYYY-MM-DDTHH:MM:SS)"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin del rango (formato ISO: YYYY-MM-DDTHH:MM:SS)"),
    current_user: User = Depends(get_current_user),
    task_repo: TaskRepository = Depends(Provide[Container.task_repository]),
) -> TaskListDTO:
    """
    Get all tasks in the system.
    
    Args:
        start_date: Optional start date for filtering (filters by updated_at >= start_date)
        end_date: Optional end date for filtering (filters by updated_at <= end_date)
        current_user: Current authenticated user
        task_repo: Task repository
        
    Returns:
        TaskListDTO with list of all tasks
    """
    try:
        tasks = task_repo.get_all(start_date=start_date, end_date=end_date)
        from app.application.mappers.task_mapper import TaskMapper
        return TaskMapper.to_dto_list(tasks)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener las tasks"
        )


@router.post("/", response_model=TaskDTO)
@inject
def create_task(
    create_dto: TaskCreateDTO,
    current_user: User = Depends(get_current_user),
    task_repo: TaskRepository = Depends(Provide[Container.task_repository]),
) -> TaskDTO:
    """
    Create a new task.
    
    Args:
        create_dto: Task creation data
        current_user: Current authenticated user
        task_repo: Task repository
        
    Returns:
        TaskDTO of the created task
    """
    use_case = CreateTask(task_repo)
    return use_case.execute(create_dto, current_user)


@router.get("/me", response_model=TaskListDTO)
@inject
def get_my_tasks(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio del rango (formato ISO: YYYY-MM-DDTHH:MM:SS)"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin del rango (formato ISO: YYYY-MM-DDTHH:MM:SS)"),
    current_user: User = Depends(get_current_user),
    task_repo: TaskRepository = Depends(Provide[Container.task_repository]),
) -> TaskListDTO:
    """
    Get all tasks assigned to the current authenticated user.
    
    This endpoint returns tasks that have been explicitly assigned to the user.
    Useful for employees to see their assigned work.
    
    Args:
        start_date: Optional start date for filtering (filters by updated_at >= start_date)
        end_date: Optional end date for filtering (filters by updated_at <= end_date)
        current_user: Current authenticated user
        task_repo: Task repository
        
    Returns:
        TaskListDTO with list of tasks assigned to the current user
        
    Raises:
        HTTPException: If there's an error retrieving the tasks
    """
    try:
        # Get tasks assigned to the current user
        tasks = task_repo.get_by_assigned_user(current_user.firebase_uid, start_date=start_date, end_date=end_date)
        from app.application.mappers.task_mapper import TaskMapper
        return TaskMapper.to_dto_list(tasks)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener tus tasks asignadas"
        )


@router.get("/user/{user_id}", response_model=TaskListDTO)
@inject
def get_tasks_by_user(
    user_id: str,  # Firebase UID or UUID string
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio del rango (formato ISO: YYYY-MM-DDTHH:MM:SS)"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin del rango (formato ISO: YYYY-MM-DDTHH:MM:SS)"),
    current_user: User = Depends(get_current_user),
    task_repo: TaskRepository = Depends(Provide[Container.task_repository]),
) -> TaskListDTO:
    """
    Get all tasks assigned to a specific user.
    
    Admin users can view tasks for any user. Regular users can only view their own tasks.
    
    Args:
        user_id: User ID (Firebase UID or UUID string)
        start_date: Optional start date for filtering (filters by updated_at >= start_date)
        end_date: Optional end date for filtering (filters by updated_at <= end_date)
        current_user: Current authenticated user
        task_repo: Task repository
        
    Returns:
        TaskListDTO with list of tasks assigned to the specified user
        
    Raises:
        HTTPException 403: If user doesn't have permission to view this user's tasks
        HTTPException 500: If there's an error retrieving the tasks
    """
    try:
        # Check authorization: Users can only see their own tasks unless they're admin/manager
        is_admin_or_manager = current_user.role in (RoleEnum.SUPER_ADMIN, RoleEnum.MANAGER)
        if user_id != current_user.firebase_uid and not is_admin_or_manager:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver las tasks de otro user"
            )
        
        # Get tasks assigned to the user
        tasks = task_repo.get_by_assigned_user(user_id, start_date=start_date, end_date=end_date)  # type: ignore
        from app.application.mappers.task_mapper import TaskMapper
        return TaskMapper.to_dto_list(tasks)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener las tasks del user"
        )


@router.get("/work/{work_id}", response_model=TaskListDTO)
@inject
def get_tasks_by_work(
    work_id: UUID,
    current_user: User = Depends(get_current_user),
    task_repo: TaskRepository = Depends(Provide[Container.task_repository]),
) -> TaskListDTO:
    """
    Get all tasks for a specific work.
    
    Args:
        work_id: Work ID
        current_user: Current authenticated user
        task_repo: Task repository
        
    Returns:
        TaskListDTO with list of tasks
    """
    use_case = GetTasksByWork(task_repo)
    return use_case.execute(work_id)


@router.get("/work/{work_id}/summary", response_model=TaskSummaryDTO)
@inject
def get_task_summary(
    work_id: UUID,
    current_user: User = Depends(get_current_user),
    task_repo: TaskRepository = Depends(Provide[Container.task_repository]),
) -> TaskSummaryDTO:
    """
    Get task summary for a work.
    
    Args:
        work_id: Work ID
        current_user: Current authenticated user
        task_repo: Task repository
        
    Returns:
        TaskSummaryDTO with task statistics
    """
    use_case = GetTaskSummary(task_repo)
    return use_case.execute(work_id)


@router.get("/{task_id}", response_model=TaskDTO)
@inject
def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    task_repo: TaskRepository = Depends(Provide[Container.task_repository]),
) -> TaskDTO:
    """
    Get a task by ID.
    
    Args:
        task_id: Task ID
        current_user: Current authenticated user
        task_repo: Task repository
        
    Returns:
        TaskDTO of the task
    """
    use_case = GetTask(task_repo)
    return use_case.execute(task_id)


@router.put("/{task_id}", response_model=TaskDTO)
@inject
def update_task(
    task_id: UUID,
    update_dto: TaskUpdateDTO,
    current_user: User = Depends(get_current_user),
    task_repo: TaskRepository = Depends(Provide[Container.task_repository]),
) -> TaskDTO:
    """
    Update a task.
    
    Args:
        task_id: Task ID to update
        update_dto: Update data
        current_user: Current authenticated user
        task_repo: Task repository
        
    Returns:
        TaskDTO of the updated task
    """
    use_case = UpdateTask(task_repo)
    return use_case.execute(task_id, update_dto, current_user)


@router.post("/{task_id}/assign", response_model=TaskDTO)
@inject
def assign_task(
    task_id: UUID,
    assign_dto: TaskAssignDTO,
    current_user: User = Depends(get_current_user),
    task_repo: TaskRepository = Depends(Provide[Container.task_repository]),
    user_repo = Depends(Provide[Container.user_repo]),
) -> TaskDTO:
    """
    Assign a task to a user.
    
    Args:
        task_id: Task ID to assign
        assign_dto: Assignment data
        current_user: Current authenticated user
        task_repo: Task repository
        user_repo: User repository
        
    Returns:
        TaskDTO of the updated task
    """
    use_case = AssignTask(task_repo, user_repo)
    return use_case.execute(task_id, assign_dto, current_user)


@router.post("/{task_id}/finish", response_model=TaskDTO)
@inject
def finish_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    task_repo: TaskRepository = Depends(Provide[Container.task_repository]),
    work_repo = Depends(Provide[Container.work_repository]),
    payroll_history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
    payroll_repo: PayrollRepository = Depends(Provide[Container.payroll_repository]),
    user_repo = Depends(Provide[Container.user_repo]),  # type: ignore
    payroll_history_task_repo: PayrollHistoryTaskRepository = Depends(Provide[Container.payroll_history_task_repository]),
) -> TaskDTO:
    """
    Finish a task and automatically unlock the next blocked task in the sequence.
    
    When a task is marked as finished, any task that was blocked by it 
    (waiting for this one to complete) is automatically unlocked and 
    transitioned from ASSIGNED to READY state.
    
    **NUEVO**: Tambien actualiza el PayrollHistory para empleados con contract
    de prestacion de servicios, sumando el valor de mano de obra al works_value_amount.
    
    Args:
        task_id: Task ID to finish
        current_user: Current authenticated user
        task_repo: Task repository
        work_repo: Work repository
        payroll_history_repo: PayrollHistory repository
        payroll_repo: Payroll repository
        user_repo: User repository
        payroll_history_task_repo: PayrollHistoryTask repository
        
    Returns:
        TaskDTO of the updated task
    """
    # 1. Ejecutar el caso de uso original de FinishTask
    use_case = FinishTask(task_repo, work_repo)
    finished_task_dto = use_case.execute(task_id, current_user)
    
    # 2. Actualizar PayrollHistory si aplica
    try:
        payroll_update_case = UpdatePayrollHistoryOnTaskCompletionV2(
            task_repo,
            payroll_history_repo,
            payroll_repo,
            user_repo,
            payroll_history_task_repo
        )
        update_result = payroll_update_case.execute(task_id)
        
        if update_result:
            print(f"OK PayrollHistory actualizado: {update_result}")
    except Exception as e:
        print(f" Error actualizando PayrollHistory para task {task_id}: {e}")
    
    return finished_task_dto


@router.post("/{task_id}/complete", response_model=TaskDTO)
@inject
def complete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    task_repo: TaskRepository = Depends(Provide[Container.task_repository]),
    work_repo = Depends(Provide[Container.work_repository]),
    payroll_history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
    payroll_repo: PayrollRepository = Depends(Provide[Container.payroll_repository]),
    user_repo = Depends(Provide[Container.user_repo]),  # type: ignore
    payroll_history_task_repo: PayrollHistoryTaskRepository = Depends(Provide[Container.payroll_history_task_repository]),
) -> TaskDTO:
    """
    Complete a task (IN_PROGRESS  COMPLETED or FINISHED).
    
    - EMPLOYEE: Task goes to COMPLETED (requires validation), next task unlocked
    - SUPERVISOR/MANAGER: Task auto-validated to FINISHED, next task unlocked
    
    The next blocked task in the sequence is automatically unlocked regardless
    of whether the current task needs validation (COMPLETED) or is finished.
    This allows work to continue without waiting for validation.
    
    **NUEVO**: Si la task va directamente a FINISHED (supervisor/manager),
    actualiza el PayrollHistory para empleados con contract de prestacion de servicios.
    
    Args:
        task_id: Task ID to complete
        current_user: Current authenticated user
        task_repo: Task repository
        work_repo: Work repository
        payroll_history_repo: PayrollHistory repository
        payroll_repo: Payroll repository
        user_repo: User repository
        payroll_history_task_repo: PayrollHistoryTask repository
        
    Returns:
        TaskDTO of the updated task
    """
    # 1. Ejecutar el caso de uso original
    use_case = CompleteTask(task_repo, work_repo)
    completed_task_dto = use_case.execute(task_id, current_user)
    
    # 2. Si la task fue directamente a FINISHED (supervisor/manager), actualizar payroll
    if completed_task_dto.state == "FINISHED":  # Comparar con string del DTO
        try:
            payroll_update_case = UpdatePayrollHistoryOnTaskCompletionV2(
                task_repo,
                payroll_history_repo,
                payroll_repo,
                user_repo,
                payroll_history_task_repo
            )
            update_result = payroll_update_case.execute(task_id)
            
            if update_result:
                print(f"OK PayrollHistory actualizado: {update_result}")
        except Exception as e:
            print(f" Error actualizando PayrollHistory para task {task_id}: {e}")
    
    return completed_task_dto


@router.post("/{task_id}/validate", response_model=TaskDTO)
@inject
def validate_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    task_repo: TaskRepository = Depends(Provide[Container.task_repository]),
    work_repo = Depends(Provide[Container.work_repository]),
    payroll_history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
    payroll_repo: PayrollRepository = Depends(Provide[Container.payroll_repository]),
    user_repo = Depends(Provide[Container.user_repo]),  # type: ignore
    payroll_history_task_repo: PayrollHistoryTaskRepository = Depends(Provide[Container.payroll_history_task_repository]),
) -> TaskDTO:
    """
    Validate a completed task (COMPLETED  FINISHED).
    
    Only SUPERVISOR or MANAGER can validate.
    Automatically unlocks the next blocked task in the sequence.
    
    **NUEVO**: Al validar la task (COMPLETED  FINISHED), actualiza el PayrollHistory
    para empleados con contract de prestacion de servicios.
    
    Args:
        task_id: Task ID to validate
        current_user: Current authenticated user (must be SUPERVISOR/MANAGER)
        task_repo: Task repository
        work_repo: Work repository
        payroll_history_repo: PayrollHistory repository
        payroll_repo: Payroll repository
        user_repo: User repository
        payroll_history_task_repo: PayrollHistoryTask repository
        
    Returns:
        TaskDTO of the updated task
    """
    # 1. Ejecutar el caso de uso original
    use_case = ValidateTask(task_repo, work_repo)
    validated_task_dto = use_case.execute(task_id, current_user)
    
    # 2. Actualizar PayrollHistory ya que la task ahora esta FINISHED
    try:
        payroll_update_case = UpdatePayrollHistoryOnTaskCompletionV2(
            task_repo,
            payroll_history_repo,
            payroll_repo,
            user_repo,
            payroll_history_task_repo
        )
        update_result = payroll_update_case.execute(task_id)
        
        if update_result:
            print(f"OK PayrollHistory actualizado: {update_result}")
    except Exception as e:
        print(f" Error actualizando PayrollHistory para task {task_id}: {e}")
    
    return validated_task_dto


@router.post("/{task_id}/change-state", response_model=TaskDTO)
@inject
def change_task_state(
    task_id: UUID,
    state_change_dto: TaskStateChangeDTO,
    current_user: User = Depends(get_current_user),
    task_repo: TaskRepository = Depends(Provide[Container.task_repository]),
    work_repo = Depends(Provide[Container.work_repository]),
    payroll_history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
    payroll_repo: PayrollRepository = Depends(Provide[Container.payroll_repository]),
    user_repo = Depends(Provide[Container.user_repo]),  # type: ignore
    payroll_history_task_repo: PayrollHistoryTaskRepository = Depends(Provide[Container.payroll_history_task_repository]),
) -> TaskDTO:
    """
    Change task state.
    
    When a task transitions to COMPLETED or FINISHED, the next blocked task 
    (if exists) is automatically unlocked.
    
    **NUEVO**: Si la task cambia a FINISHED, actualiza el PayrollHistory
    para empleados con contract de prestacion de servicios.
    
    Args:
        task_id: Task ID to update
        state_change_dto: State change data
        current_user: Current authenticated user
        task_repo: Task repository
        work_repo: Work repository
        payroll_history_repo: PayrollHistory repository
        payroll_repo: Payroll repository
        user_repo: User repository
        payroll_history_task_repo: PayrollHistoryTask repository
        
    Returns:
        TaskDTO of the updated task
    """
    # 1. Ejecutar el caso de uso original
    use_case = ChangeTaskState(task_repo, work_repo)
    updated_task_dto = use_case.execute(task_id, state_change_dto, current_user)
    
    # 2. Si el nuevo estado es FINISHED, actualizar payroll
    if updated_task_dto.state == "FINISHED":  # Comparar con string del DTO
        try:
            payroll_update_case = UpdatePayrollHistoryOnTaskCompletionV2(
                task_repo,
                payroll_history_repo,
                payroll_repo,
                user_repo,
                payroll_history_task_repo
            )
            update_result = payroll_update_case.execute(task_id)
            
            if update_result:
                print(f"OK PayrollHistory actualizado: {update_result}")
        except Exception as e:
            print(f" Error actualizando PayrollHistory para task {task_id}: {e}")
    
    return updated_task_dto
    