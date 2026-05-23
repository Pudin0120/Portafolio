"""
Mapper for converting between PayrollHistory domain entity and DTOs.
"""
from typing import List
from uuid import UUID
from decimal import Decimal
from datetime import date

from app.domain.models.payroll_history import PayrollHistory
from app.domain.value_objects.money import Money
from app.application.dto.payroll_history_dto import (
    PayrollHistoryDTO,
    PayrollHistoryCreateDTO,
    PayrollHistoryUpdateDTO,
    PayrollHistoryListDTO,
    PayrollHistorySummaryDTO
)


class PayrollHistoryMapper:
    """Mapper for PayrollHistory domain entity to DTOs."""
    
    @staticmethod
    def to_dto(payroll_history: PayrollHistory) -> PayrollHistoryDTO:
        """
        Convert PayrollHistory domain entity to PayrollHistoryDTO.
        
        Args:
            payroll_history: PayrollHistory domain entity
            
        Returns:
            PayrollHistoryDTO with all payroll history information
        """
        return PayrollHistoryDTO(
            identification_number=payroll_history.identification_number,
            payroll_id=payroll_history.payroll_id,
            security_id=payroll_history.security_id,
            works_value_amount=payroll_history.works_value_amount.amount,
            works_value_formatted=str(payroll_history.works_value_amount.amount),
            init_date=payroll_history.init_date,
            end_date=payroll_history.end_date
        )

    @staticmethod
    def to_dto_list(payroll_histories: List[PayrollHistory]) -> PayrollHistoryListDTO:
        """
        Convert list of PayrollHistory domain entities to PayrollHistoryListDTO.
        
        Args:
            payroll_histories: List of PayrollHistory domain entities
            
        Returns:
            PayrollHistoryListDTO with list of payroll histories and total count
        """
        history_dtos = [PayrollHistoryMapper.to_dto(history) for history in payroll_histories]
        return PayrollHistoryListDTO(
            payroll_histories=history_dtos,
            total_count=len(history_dtos)
        )
    
    @staticmethod
    def from_create_dto(create_dto: PayrollHistoryCreateDTO) -> PayrollHistory:
        """
        Convert PayrollHistoryCreateDTO to PayrollHistory domain entity.
        
        Args:
            create_dto: PayrollHistoryCreateDTO with creation data
            
        Returns:
            PayrollHistory domain entity
        """
        # Create Money objects
        works_value = Money(amount=create_dto.works_value_amount)
        
        return PayrollHistory(
            identification_number=create_dto.identification_number,
            payroll_id=create_dto.payroll_id,
            security_id=create_dto.security_id,
            works_value_amount=works_value,
            init_date=create_dto.init_date,
            end_date=create_dto.end_date
        )
    
    @staticmethod
    def apply_update_dto(payroll_history: PayrollHistory, update_dto: PayrollHistoryUpdateDTO) -> PayrollHistory:
        """
        Apply PayrollHistoryUpdateDTO changes to existing PayrollHistory domain entity.
        
        Args:
            payroll_history: Existing PayrollHistory domain entity
            update_dto: PayrollHistoryUpdateDTO with update data
            
        Returns:
            Updated PayrollHistory domain entity
        """
        # Update identification number if provided
        if update_dto.identification_number is not None:
            payroll_history.identification_number = update_dto.identification_number
        
        # Update payroll_id if provided
        if update_dto.payroll_id is not None:
            payroll_history.payroll_id = update_dto.payroll_id
        
        # Update security_id if provided
        if update_dto.security_id is not None:
            payroll_history.security_id = update_dto.security_id
        
        # Update works_value if provided
        if update_dto.works_value_amount is not None:
            payroll_history.works_value_amount = Money(amount=update_dto.works_value_amount)
        
        # Update init_date if provided
        if update_dto.init_date is not None:
            payroll_history.init_date = update_dto.init_date
        
        # Update end_date if provided
        if update_dto.end_date is not None:
            payroll_history.end_date = update_dto.end_date
        
        return payroll_history
    
    @staticmethod
    def to_summary_dto(payroll_histories: List[PayrollHistory]) -> PayrollHistorySummaryDTO:
        """
        Convert list of PayrollHistory domain entities to PayrollHistorySummaryDTO.
        
        Args:
            payroll_histories: List of PayrollHistory domain entities for the same employee
            
        Returns:
            PayrollHistorySummaryDTO with summary statistics
        """
        if not payroll_histories:
            raise ValueError("Cannot create summary from empty list")
        
        # Get employee ID from first record
        employee_id = payroll_histories[0].identification_number
        
        # Calculate totals
        total_works_value = sum(history.works_value_amount.amount for history in payroll_histories)
        
        return PayrollHistorySummaryDTO(
            employee_id=employee_id,
            total_records=len(payroll_histories),
            total_works_value=total_works_value
        )
