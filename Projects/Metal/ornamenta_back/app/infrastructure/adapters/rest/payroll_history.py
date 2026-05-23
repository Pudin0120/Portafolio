"""
REST API endpoints for PayrollHistory.
"""
from typing import Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide
from sqlalchemy.orm import Session

from app.domain.repositories.payroll_history_repository import PayrollHistoryRepository
from app.domain.models.user import User
from app.infrastructure.adapters.rest.authorization import get_current_user
from app.application.dto.payroll_history_dto import (
    PayrollHistoryDTO,
    PayrollHistoryListDTO,
    PayrollHistoryCreateDTO,
    PayrollHistoryUpdateDTO,
    PayrollHistorySummaryDTO
)
from app.application.mappers.payroll_history_mapper import PayrollHistoryMapper
from app.infrastructure.containers import Container
from app.infrastructure.adapters.db.database import get_db_session

router = APIRouter(prefix="/payroll-histories", tags=["Payroll Histories"])


@router.get("/", response_model=PayrollHistoryListDTO)
@inject
def list_payroll_histories(
    identification_number: Optional[str] = None,
    payroll_id: Optional[UUID] = None,
    security_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
) -> PayrollHistoryListDTO:
    """
    List all payroll histories.
    
    Optional filters:
    - identification_number: Filter by employee identification number
    - payroll_id: Filter by payroll ID
    - security_id: Filter by security ID
    """
    if identification_number:
        histories = history_repo.get_by_identification_number(identification_number)
    elif payroll_id:
        histories = history_repo.get_by_payroll_id(payroll_id)
    elif security_id:
        histories = history_repo.get_by_security_id(security_id)
    else:
        histories = history_repo.get_all()
    
    return PayrollHistoryMapper.to_dto_list(histories)


@router.get("/{history_id}", response_model=PayrollHistoryDTO)
@inject
def get_payroll_history(
    history_id: UUID,
    current_user: User = Depends(get_current_user),
    history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
) -> PayrollHistoryDTO:
    """Get a specific payroll history by UUID."""
    history = history_repo.get_by_id(history_id)
    
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payroll history with ID {history_id} not found"
        )
    
    return PayrollHistoryMapper.to_dto(history)


@router.post("/", response_model=PayrollHistoryDTO, status_code=status.HTTP_201_CREATED)
@inject
def create_payroll_history(
    history_data: PayrollHistoryCreateDTO,
    current_user: User = Depends(get_current_user),
    history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
    db: Session = Depends(get_db_session),
) -> PayrollHistoryDTO:
    """
    Create a new payroll history record.
    
    Requires:
    - identification_number: Employee identification number
    - payroll_id: Associated payroll ID
    - security_id: Security/social security ID
    - works_value_amount: Works value amount in COP
    - init_date: Period start date
    - end_date: Period end date
    """
    try:
        history = PayrollHistoryMapper.from_create_dto(history_data)
        saved_history = history_repo.save(history)
        return PayrollHistoryMapper.to_dto(saved_history)
    
    except Exception as e:
        #  ESTO DEBE ACTIVARSE SI HAY UN ERROR DE DB
        print(f" ERROR CRITICO DE DB EN PAYROLL_HISTORY: {type(e).__name__}: {e}")
        # Asegurate de importar IntegrityError si es necesario
        from sqlalchemy.exc import IntegrityError
        
        # El frontend recibira un 500 en lugar del 201, pero podremos ver el log.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during payroll history creation: {type(e).__name__}"
        )
    


@router.patch("/{history_id}", response_model=PayrollHistoryDTO)
@inject
def update_payroll_history(
    history_id: UUID,
    history_data: PayrollHistoryUpdateDTO,
    current_user: User = Depends(get_current_user),
    history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
) -> PayrollHistoryDTO:
    """
    Update an existing payroll history record.
    
    Updatable fields:
    - identification_number
    - payroll_id
    - security_id
    - works_value_amount
    - init_date
    - end_date
    """
    history = history_repo.get_by_id(history_id)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payroll history with ID {history_id} not found"
        )
    
    updated_history = PayrollHistoryMapper.apply_update_dto(history, history_data)
    saved_history = history_repo.save(updated_history)
    return PayrollHistoryMapper.to_dto(saved_history)


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_payroll_history(
    history_id: UUID,
    current_user: User = Depends(get_current_user),
    history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
):
    """Delete a payroll history record."""
    success = history_repo.delete(history_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payroll history with ID {history_id} not found"
        )


@router.get("/employee/{identification_number}", response_model=PayrollHistoryListDTO)
@inject
def get_employee_histories(
    identification_number: str,
    current_user: User = Depends(get_current_user),
    history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
) -> PayrollHistoryListDTO:
    """Get all payroll histories for a specific employee."""
    histories = history_repo.get_by_identification_number(identification_number)
    return PayrollHistoryMapper.to_dto_list(histories)


@router.get("/employee/{identification_number}/latest", response_model=PayrollHistoryDTO)
@inject
def get_employee_latest_history(
    identification_number: str,
    current_user: User = Depends(get_current_user),
    history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
) -> PayrollHistoryDTO:
    """Get the latest payroll history for a specific employee."""
    history = history_repo.get_latest_by_employee(identification_number)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No payroll history found for employee {identification_number}"
        )
    return PayrollHistoryMapper.to_dto(history)


@router.get("/employee/{identification_number}/earliest", response_model=PayrollHistoryDTO)
@inject
def get_employee_earliest_history(
    identification_number: str,
    current_user: User = Depends(get_current_user),
    history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
) -> PayrollHistoryDTO:
    """Get the earliest payroll history for a specific employee."""
    history = history_repo.get_earliest_by_employee(identification_number)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No payroll history found for employee {identification_number}"
        )
    return PayrollHistoryMapper.to_dto(history)


@router.get("/employee/{identification_number}/summary", response_model=PayrollHistorySummaryDTO)
@inject
def get_employee_summary(
    identification_number: str,
    current_user: User = Depends(get_current_user),
    history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
) -> PayrollHistorySummaryDTO:
    """Get summary statistics for an employee's payroll history."""
    summary_data = history_repo.get_employee_summary(identification_number)
    
    if summary_data['total_records'] == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No payroll history found for employee {identification_number}"
        )
    
    return PayrollHistorySummaryDTO(**summary_data)


@router.get("/payroll/{payroll_id}", response_model=PayrollHistoryListDTO)
@inject
def get_payroll_histories(
    payroll_id: UUID,
    current_user: User = Depends(get_current_user),
    history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
) -> PayrollHistoryListDTO:
    """Get all payroll histories for a specific payroll."""
    
    histories = history_repo.get_by_payroll_id(payroll_id)
    dto_list = PayrollHistoryMapper.to_dto_list(histories)

    return PayrollHistoryListDTO(
        payroll_histories=dto_list,
        total_count=len(dto_list)
    )



@router.get("/date-range/", response_model=PayrollHistoryListDTO)
@inject
def get_histories_by_date_range(
    start_date: date,
    end_date: date,
    identification_number: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
) -> PayrollHistoryListDTO:
    """
    Get payroll histories within a date range.
    
    Optional filter:
    - identification_number: Filter by specific employee
    """
    if identification_number:
        histories = history_repo.get_by_employee_and_date_range(
            identification_number, start_date, end_date
        )
    else:
        histories = history_repo.get_by_date_range(start_date, end_date)
    
    return PayrollHistoryMapper.to_dto_list(histories)


@router.get("/value/minimum-works", response_model=PayrollHistoryListDTO)
@inject
def get_histories_by_minimum_works_value(
    min_value: float,
    current_user: User = Depends(get_current_user),
    history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
) -> PayrollHistoryListDTO:
    """Get payroll histories with works value greater than or equal to minimum."""
    histories = history_repo.get_by_minimum_works_value(min_value)
    return PayrollHistoryMapper.to_dto_list(histories)


@router.get("/value/minimum-labor", response_model=PayrollHistoryListDTO)
@inject
def get_histories_by_minimum_labor_cost(
    min_cost: float,
    current_user: User = Depends(get_current_user),
    history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
) -> PayrollHistoryListDTO:
    """Get payroll histories with labor cost greater than or equal to minimum."""
    histories = history_repo.get_by_minimum_labor_cost(min_cost)
    return PayrollHistoryMapper.to_dto_list(histories)


@router.get("/value/minimum-total", response_model=PayrollHistoryListDTO)
@inject
def get_histories_by_minimum_total_value(
    min_value: float,
    current_user: User = Depends(get_current_user),
    history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
) -> PayrollHistoryListDTO:
    """Get payroll histories with total value greater than or equal to minimum."""
    histories = history_repo.get_by_minimum_total_value(min_value)
    return PayrollHistoryMapper.to_dto_list(histories)


@router.delete("/payroll/{payroll_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_payroll_histories(
    payroll_id: UUID,
    current_user: User = Depends(get_current_user),
    history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
):
    """Delete all payroll histories for a specific payroll."""
    deleted_count = history_repo.delete_by_payroll_id(payroll_id)
    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No payroll histories found for payroll {payroll_id}"
        )


@router.delete("/employee/{identification_number}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_employee_histories(
    identification_number: str,
    current_user: User = Depends(get_current_user),
    history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
):
    """Delete all payroll histories for a specific employee."""
    deleted_count = history_repo.delete_by_employee(identification_number)
    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No payroll histories found for employee {identification_number}"
        )


@router.get("/stats/count", response_model=dict)
@inject
def get_payroll_history_stats(
    current_user: User = Depends(get_current_user),
    history_repo: PayrollHistoryRepository = Depends(Provide[Container.payroll_history_repository]),
) -> dict:
    """Get payroll history statistics."""
    total_count = history_repo.count()
    
    return {
        "total_count": total_count
    }