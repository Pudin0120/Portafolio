"""
Mapper for Payroll domain entity and DTOs.
"""
from typing import List, Optional, Union, cast, TYPE_CHECKING
from uuid import UUID
from datetime import date
from decimal import Decimal

from app.domain.models.Payroll import Payroll
from app.domain.value_objects.money import Money
from app.domain.value_objects.contract_type import ContractType
from app.domain.value_objects.state_payroll import StatePayroll
from app.application.dto.payroll_dto import (
    PayrollDTO,
    PayrollCreateDTO,
    PayrollUpdateDTO,
    PayrollListDTO
)

if TYPE_CHECKING:
    from app.domain.models.payroll_history import PayrollHistory


class PayrollMapper:
    """Mapper for converting between Payroll domain entities and DTOs."""

    @staticmethod
    def to_dto(
        payroll: Payroll, 
        identification_number: Optional[str] = None,
        latest_history: Optional['PayrollHistory'] = None
    ) -> PayrollDTO:
        """
        Convert domain entity to DTO.
        
        Args:
            payroll: Payroll domain entity
            identification_number: Optional identification number from PayrollHistory
            latest_history: Optional latest PayrollHistory record
        
        Returns:
            PayrollDTO with all payroll information
        """
        # Extract information from latest history if available
        current_period_salary = None
        current_period_salary_formatted = None
        current_period_start_date = None
        current_period_end_date = None
        
        if latest_history:
            current_period_salary = latest_history.works_value_amount.amount
            current_period_salary_formatted = f"${latest_history.works_value_amount.amount:,.2f} {latest_history.works_value_amount.currency}"
            current_period_start_date = latest_history.init_date
            current_period_end_date = latest_history.end_date
        
        return PayrollDTO(
            payroll_id=payroll.payroll_id,
            identification_number=identification_number,
            contract_type=payroll.contract_type.value.value, 
            state=payroll.state.value.value,
            base_salary_amount=payroll.base_salary.amount,
            base_salary_formatted=f"${payroll.base_salary.amount:,.2f} {payroll.base_salary.currency}",
            # Current period info from latest history
            current_period_salary=current_period_salary,
            current_period_salary_formatted=current_period_salary_formatted,
            current_period_start_date=current_period_start_date,
            current_period_end_date=current_period_end_date,
            # State checks
            is_liquidated=payroll.is_liquidated,
            is_active=payroll.is_active,
            is_paid=payroll.is_paid,
            is_cancelled=payroll.is_cancelled,
            # Contract type checks
            is_fixed_term=payroll.is_fixed_term,
            is_indefinite_term=payroll.is_indefinite_term,
            is_service_provision=payroll.is_service_provision
        )

    @staticmethod
    def to_dto_list(
        payrolls: Union[
            List[Payroll], 
            List[tuple[Payroll, Optional[str]]],
            List[tuple[Payroll, Optional[str], Optional['PayrollHistory']]]
        ]
    ) -> PayrollListDTO:
        """
        Convert list of payrolls to DTO list.
        
        Args:
            payrolls: Either:
                     - a list of Payroll objects
                     - a list of (Payroll, identification_number) tuples
                     - a list of (Payroll, identification_number, PayrollHistory) tuples
        
        Returns:
            PayrollListDTO with converted payrolls
        """
        if not payrolls:
            return PayrollListDTO(payrolls=[], total_count=0)
        
        # Detectar si son tuplas o objetos simples
        if isinstance(payrolls[0], tuple):
            # Check if it's a 3-tuple (with PayrollHistory)
            if len(payrolls[0]) == 3:
                from app.domain.models.payroll_history import PayrollHistory
                payrolls_triple_list = cast(List[tuple[Payroll, Optional[str], Optional[PayrollHistory]]], payrolls)
                dto_list = [
                    PayrollMapper.to_dto(p, id_num, history) 
                    for p, id_num, history in payrolls_triple_list
                ]
            else:
                # Es una lista de tuplas (Payroll, identification_number)
                payrolls_tuple_list = cast(List[tuple[Payroll, Optional[str]]], payrolls)
                dto_list = [
                    PayrollMapper.to_dto(p, id_num) 
                    for p, id_num in payrolls_tuple_list
                ]
        else:
            # Es una lista de objetos Payroll simples
            payrolls_obj_list = cast(List[Payroll], payrolls)
            dto_list = [
                PayrollMapper.to_dto(p) 
                for p in payrolls_obj_list
            ]
        
        return PayrollListDTO(
            payrolls=dto_list,
            total_count=len(dto_list)
        )

    @staticmethod
    def from_create_dto(dto: PayrollCreateDTO, payroll_id: UUID) -> Payroll:
        """
        Convert create DTO to domain entity.
        
        Args:
            dto: PayrollCreateDTO with creation data
            payroll_id: UUID for the new payroll
        
        Returns:
            Payroll domain entity
        """
        from app.domain.value_objects.contract_type import ContractTypeEnum
        from app.domain.value_objects.state_payroll import StatePayrollEnum
        
        return Payroll(
        payroll_id=payroll_id,
        contract_type=ContractType(value=ContractTypeEnum(dto.contract_type)),
        state=StatePayroll(value=StatePayrollEnum(dto.state)),
        base_salary=Money(amount=dto.base_salary_amount, currency='COP')
        )

    @staticmethod
    def update_from_dto(payroll: Payroll, dto: PayrollUpdateDTO) -> Payroll:
        """
        Update domain entity from update DTO.
        
        Args:
            payroll: Existing Payroll entity to update
            dto: PayrollUpdateDTO with update data
        
        Returns:
            Updated Payroll entity
        """
        from app.domain.value_objects.contract_type import ContractTypeEnum
        from app.domain.value_objects.state_payroll import StatePayrollEnum
        
        if dto.contract_type is not None:
            payroll.contract_type = ContractType(value=ContractTypeEnum(dto.contract_type))
        if dto.state is not None:
            payroll.state = StatePayroll(value=StatePayrollEnum(dto.state))
        if dto.base_salary_amount is not None:
            payroll.base_salary = Money(amount=dto.base_salary_amount, currency='COP')
        
        return payroll