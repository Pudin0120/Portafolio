"""
REST API endpoints for Payroll.
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide
import uuid
from app.infrastructure.adapters.repositories.payroll_repository import PostgresPayrollRepository
from sqlalchemy.orm import Session
from datetime import date
from decimal import Decimal
import logging

from app.domain.repositories.payroll_repository import PayrollRepository
from app.domain.repositories.payroll_history_repository import PayrollHistoryRepository
from app.domain.repositories.task_repository import TaskRepository
from app.domain.repositories.payroll_history_task_repository import PayrollHistoryTaskRepository
from app.domain.models.user import User
from app.domain.models.payroll_history import PayrollHistory
from app.domain.value_objects.money import Money
from app.domain.value_objects.contract_type import ContractType, ContractTypeEnum
from app.domain.value_objects.state_payroll import StatePayroll, StatePayrollEnum
from app.infrastructure.adapters.rest.authorization import get_current_user
from app.infrastructure.adapters.db.database import get_db_session
from app.infrastructure.containers import Container

from app.application.mappers.payroll_mapper import PayrollMapper
from app.application.mappers.payroll_history_mapper import PayrollHistoryMapper
from app.application.dto.payroll_dto import (
    PayrollDTO,
    PayrollListDTO,
    PayrollCreateDTO,
    PayrollUpdateDTO,
    PayrollServiceProvisionTasksDTO,
    PayrollTaskSummaryItemDTO
)
from app.application.use_cases.payroll_task_integration import (
    CalculatePayrollFromTasks,
    UpdatePayrollFromTaskCompletion,
    GetPayrollTaskSummary
)

router = APIRouter(prefix="/payrolls", tags=["Payrolls"])
logger = logging.getLogger(__name__)

# ----------------------------
# List, Get and Stats Endpoints
# ----------------------------

@router.get("/", response_model=PayrollListDTO)
def list_payrolls(
    contract_type: Optional[str] = None,
    state: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
) -> PayrollListDTO:
    """List all payrolls with optional filters."""
    from app.infrastructure.adapters.repositories.payroll_history_repository import PostgresPayrollHistoryRepository
    
    payroll_repo = PostgresPayrollRepository(db_session)
    payroll_history_repo = PostgresPayrollHistoryRepository(db_session)
    
    # Get payrolls
    if contract_type:
        payrolls = payroll_repo.get_by_contract_type(ContractTypeEnum(contract_type))
    elif state:
        payrolls = payroll_repo.get_by_state(StatePayrollEnum(state))
    else:
        payrolls = payroll_repo.get_all()
    
    #  Para cada payroll, obtener su identification_number y historial mas reciente
    payrolls_with_history = []
    for payroll in payrolls:
        # Obtener el historial mas reciente
        histories = payroll_history_repo.get_by_payroll_id(payroll.payroll_id)
        latest_history = histories[0] if histories else None
        identification_number = latest_history.identification_number if latest_history else None
        payrolls_with_history.append((payroll, identification_number, latest_history))
    
    return PayrollMapper.to_dto_list(payrolls_with_history)


@router.get("/{payroll_id}", response_model=PayrollDTO)
def get_payroll(
    payroll_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
) -> PayrollDTO:
    """Get a specific payroll by ID."""
    from app.infrastructure.adapters.repositories.payroll_history_repository import PostgresPayrollHistoryRepository
    
    payroll_repo = PostgresPayrollRepository(db_session)
    payroll_history_repo = PostgresPayrollHistoryRepository(db_session)
    
    payroll = payroll_repo.get_by_id(payroll_id)
    if not payroll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payroll with ID {payroll_id} not found"
        )
    
    #  Obtener el historial mas reciente
    histories = payroll_history_repo.get_by_payroll_id(payroll_id)
    latest_history = histories[0] if histories else None
    identification_number = latest_history.identification_number if latest_history else None
    
    return PayrollMapper.to_dto(payroll, identification_number, latest_history)


@router.get("/stats/count", response_model=dict)
@inject
def get_payroll_stats(
    current_user: User = Depends(get_current_user),
    payroll_repo: PayrollRepository = Depends(Provide[Container.payroll_repository]),
) -> dict:
    """Get payroll statistics by state and contract type."""
    total_count = payroll_repo.count()
    return {
        "total_count": total_count,
        "by_state": {
            "liquidated": payroll_repo.count_by_state(StatePayrollEnum.LIQUIDATED),
            "active": payroll_repo.count_by_state(StatePayrollEnum.ACTIVE),
            "paid": payroll_repo.count_by_state(StatePayrollEnum.PAID),
            "cancelled": payroll_repo.count_by_state(StatePayrollEnum.CANCELLED)
        },
        "by_contract_type": {
            "fixed_term": payroll_repo.count_by_contract_type(ContractTypeEnum.FIXED_TERM),
            "indefinite_term": payroll_repo.count_by_contract_type(ContractTypeEnum.INDEFINITE_TERM),
            "service_provision": payroll_repo.count_by_contract_type(ContractTypeEnum.SERVICE_PROVISION)
        }
    }

# ----------------------------
# Create Payroll Endpoint
# ----------------------------

@router.post("/", response_model=PayrollDTO, status_code=status.HTTP_201_CREATED)
@inject
def create_payroll(
    payroll_data: PayrollCreateDTO,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    payroll_repo: PayrollRepository = Depends(Provide[Container.payroll_repository]),
    payroll_history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
    task_repo: TaskRepository = Depends(Provide[Container.task_repository]),
    user_repo = Depends(Provide[Container.user_repo])
) -> PayrollDTO:
    """Create a new payroll with history."""
    try:
        payroll_id = uuid.uuid4()
        start_date = payroll_data.start_date
        end_date = payroll_data.end_date

        # 1 Create payroll
        payroll = PayrollMapper.from_create_dto(payroll_data, payroll_id)
        saved_payroll = payroll_repo.save(payroll)

        # 2 Obtener user
        user = user_repo.get_by_identification_number(payroll_data.identification_number)
        if not user:
            raise HTTPException(status_code=404, detail="User no encontrado")

        # 3 Obtener tasks FINISHED del user
        from datetime import datetime
        tasks = task_repo.get_by_assigned_user(
            user_id=user.firebase_uid,
            start_date=datetime.combine(start_date, datetime.min.time()) if start_date else None,
            end_date=datetime.combine(end_date, datetime.min.time()) if end_date else None
        )
        finished_tasks = [t for t in tasks if t.state.value.value == "FINISHED"]
        total_works_value = sum(
            (Decimal(str(t.labor.amount)) for t in finished_tasks if t.labor and t.labor.amount > 0),
            Decimal('0')
        )

        # 4 Create PayrollHistory
        history_record = PayrollHistory(
            identification_number=payroll_data.identification_number,
            payroll_id=payroll_id,
            security_id=payroll_data.identification_number,
            works_value_amount=Money(amount=total_works_value, currency='COP'),
            init_date=start_date,
            end_date=end_date if end_date else start_date
        )
        payroll_history_repo.save(history_record)

        logger.info(f"OK Payroll {payroll_id} creado con works_value_amount = {total_works_value}")
        
        # 5 Recargar el payroll para obtener la relacion con history actualizada
        refreshed_payroll = payroll_repo.get_by_id(payroll_id)
        if not refreshed_payroll:
            raise HTTPException(status_code=500, detail="Error al recargar la payroll creada")
        
        #  Retornar DTO con identification_number
        return PayrollMapper.to_dto(refreshed_payroll, payroll_data.identification_number)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR Error creating payroll: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al create la payroll: {str(e)}")

# ----------------------------
# Update, Delete Endpoints
# ----------------------------

@router.patch("/{payroll_id}", response_model=PayrollDTO)
@inject
def update_payroll(
    payroll_id: UUID,
    payroll_data: PayrollUpdateDTO,
    current_user: User = Depends(get_current_user),
    payroll_repo: PayrollRepository = Depends(Provide[Container.payroll_repository])
) -> PayrollDTO:
    """Update an existing payroll."""
    payroll = payroll_repo.get_by_id(payroll_id)
    if not payroll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Payroll with ID {payroll_id} not found")
    try:
        updated_payroll = PayrollMapper.update_from_dto(payroll, payroll_data)
        saved_payroll = payroll_repo.save(updated_payroll)
        return PayrollMapper.to_dto(saved_payroll)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{payroll_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_payroll(
    payroll_id: UUID,
    current_user: User = Depends(get_current_user),
    payroll_repo: PayrollRepository = Depends(Provide[Container.payroll_repository])
):
    """Delete a payroll."""
    success = payroll_repo.delete(payroll_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Payroll with ID {payroll_id} not found")

# ----------------------------
# Task-related Endpoints
# ----------------------------

@router.post("/{payroll_id}/calculate-from-tasks", response_model=PayrollDTO)
@inject
def calculate_payroll_from_tasks(
    payroll_id: UUID,
    current_user: User = Depends(get_current_user),
    payroll_repo: PayrollRepository = Depends(Provide[Container.payroll_repository]),
    task_assignment_repo = Depends(Provide[Container.task_assignment_repository]),  # type: ignore
) -> PayrollDTO:
    """Calculate payroll values based on completed tasks."""
    use_case = CalculatePayrollFromTasks(task_assignment_repo, payroll_repo)
    updated_payroll = use_case.execute(payroll_id)
    return PayrollMapper.to_dto(updated_payroll)


@router.get("/{payroll_id}/task-summary")
@inject
def get_payroll_task_summary(
    payroll_id: UUID,
    current_user: User = Depends(get_current_user),
    payroll_repo: PayrollRepository = Depends(Provide[Container.payroll_repository]),
    task_assignment_repo = Depends(Provide[Container.task_assignment_repository]),  # type: ignore
) -> dict:
    """Get payroll task summary."""
    use_case = GetPayrollTaskSummary(task_assignment_repo, payroll_repo)
    return use_case.execute(payroll_id)


@router.post("/{payroll_id}/update-from-task/{task_id}", response_model=PayrollDTO)
@inject
def update_payroll_from_task_completion(
    payroll_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    payroll_repo: PayrollRepository = Depends(Provide[Container.payroll_repository]),
    task_assignment_repo = Depends(Provide[Container.task_assignment_repository]),  # type: ignore
) -> PayrollDTO:
    """Update payroll when a task is completed."""
    use_case = UpdatePayrollFromTaskCompletion(task_assignment_repo, payroll_repo)
    updated_payroll = use_case.execute(task_id)
    return PayrollMapper.to_dto(updated_payroll)


# ----------------------------
# Service Provision Tasks Endpoint
# ----------------------------

@router.get("/{payroll_id}/service-provision-tasks", response_model=PayrollServiceProvisionTasksDTO)
def get_service_provision_tasks(
    payroll_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
) -> PayrollServiceProvisionTasksDTO:
    """
    Get tasks summary for a service provision payroll.
    
    Returns a summary of all tasks completed during the payroll period,
    grouped by task name with count and total labor cost.
    
    Only works for SERVICE_PROVISION contract type payrolls.
    """
    from app.infrastructure.adapters.repositories.payroll_history_repository import PostgresPayrollHistoryRepository
    from app.infrastructure.adapters.repositories.payroll_history_task_repository import PostgresPayrollHistoryTaskRepository
    from app.infrastructure.adapters.repositories.postgres_task_repository import PostgresTaskRepository
    from collections import defaultdict
    
    payroll_repo = PostgresPayrollRepository(db_session)
    payroll_history_repo = PostgresPayrollHistoryRepository(db_session)
    payroll_history_task_repo = PostgresPayrollHistoryTaskRepository(db_session)
    task_repo = PostgresTaskRepository(db_session)
    
    # 1. Get payroll and validate it's SERVICE_PROVISION
    payroll = payroll_repo.get_by_id(payroll_id)
    if not payroll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payroll with ID {payroll_id} not found"
        )
    
    if payroll.contract_type.value != ContractTypeEnum.SERVICE_PROVISION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This endpoint only works for SERVICE_PROVISION payrolls. Current type: {payroll.contract_type.value.value}"
        )
    
    # 2. Get the latest payroll history for this payroll
    histories = payroll_history_repo.get_by_payroll_id(payroll_id)
    if not histories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No payroll history found for payroll {payroll_id}"
        )
    
    latest_history = histories[0]  # Already sorted by date desc
    
    if not latest_history.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payroll history ID is missing"
        )
    
    # 3. Get all task associations for this payroll history
    payroll_tasks_associations = payroll_history_task_repo.get_by_payroll_history_id(latest_history.id)
    
    if not payroll_tasks_associations:
        # No tasks yet, return empty summary
        return PayrollServiceProvisionTasksDTO(
            payroll_id=payroll_id,
            payroll_history_id=latest_history.id,
            identification_number=latest_history.identification_number,
            period_start_date=latest_history.init_date,
            period_end_date=latest_history.end_date,
            contract_type=payroll.contract_type.value.value,
            tasks_summary=[],
            total_tasks_count=0,
            total_labor_cost=Decimal('0'),
            total_labor_cost_formatted="$0 COP"
        )
    
    # 4. Get all tasks and group by name
    task_ids = [assoc.task_id for assoc in payroll_tasks_associations]
    tasks_by_name = defaultdict(list)
    
    for task_id in task_ids:
        task = task_repo.get_by_id(task_id)
        if task:
            tasks_by_name[task.task_name].append(task)
    
    # 5. Calculate summary for each task name
    tasks_summary = []
    total_labor_cost = Decimal('0')
    
    for task_name, tasks in tasks_by_name.items():
        task_count = len(tasks)
        # Get labor cost from first task (they should all be the same for same task name)
        labor_cost_per_task = Decimal(str(tasks[0].labor.amount))
        total_for_this_task = labor_cost_per_task * task_count
        
        tasks_summary.append(PayrollTaskSummaryItemDTO(
            task_name=task_name,
            task_count=task_count,
            labor_cost_per_task=labor_cost_per_task,
            labor_cost_per_task_formatted=f"${labor_cost_per_task:,.0f} COP",
            total_labor_cost=total_for_this_task,
            total_labor_cost_formatted=f"${total_for_this_task:,.0f} COP"
        ))
        
        total_labor_cost += total_for_this_task
    
    # Sort by task name for consistency
    tasks_summary.sort(key=lambda x: x.task_name)
    
    return PayrollServiceProvisionTasksDTO(
        payroll_id=payroll_id,
        payroll_history_id=latest_history.id,
        identification_number=latest_history.identification_number,
        period_start_date=latest_history.init_date,
        period_end_date=latest_history.end_date,
        contract_type=payroll.contract_type.value.value,
        tasks_summary=tasks_summary,
        total_tasks_count=len(task_ids),
        total_labor_cost=total_labor_cost,
        total_labor_cost_formatted=f"${total_labor_cost:,.0f} COP"
    )
