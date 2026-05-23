"""
Tests for Payroll DTOs and Mappers.
"""
import pytest
import uuid
from decimal import Decimal
from datetime import date

from app.domain.models.Payroll import Payroll
from app.domain.models.payroll_history import PayrollHistory
from app.domain.value_objects.money import Money
from app.domain.value_objects.contract_type import ContractType, ContractTypeEnum
from app.domain.value_objects.state_payroll import StatePayroll, StatePayrollEnum
from app.application.dto.payroll_dto import (
    PayrollDTO,
    PayrollCreateDTO,
    PayrollUpdateDTO,
    PayrollListDTO
)
from app.application.dto.payroll_history_dto import (
    PayrollHistoryDTO,
    PayrollHistoryCreateDTO,
    PayrollHistoryUpdateDTO,
    PayrollHistoryListDTO,
    PayrollHistorySummaryDTO
)
from app.application.mappers.payroll_mapper import PayrollMapper
from app.application.mappers.payroll_history_mapper import PayrollHistoryMapper


class TestPayrollMapper:
    """Test cases for PayrollMapper."""
    
    def test_to_dto(self):
        """Test converting Payroll domain entity to DTO."""
        payroll = Payroll(
            payroll_id=uuid.uuid4(),
            contract_type=ContractType(value=ContractTypeEnum.FIXED_TERM),
            state=StatePayroll(value=StatePayrollEnum.LIQUIDATED),
            base_salary=Money(amount=Decimal("2000000"))
        )
        
        dto = PayrollMapper.to_dto(payroll)
        
        assert isinstance(dto, PayrollDTO)
        assert dto.payroll_id == payroll.payroll_id
        assert dto.contract_type == "FIXED_TERM"
        assert dto.state == "LIQUIDATED"
        assert dto.base_salary_amount == Decimal("2000000")
        assert "$2,000,000.00" in dto.base_salary_formatted
        assert dto.is_fixed_term is True
        assert dto.is_indefinite_term is False
        assert dto.is_service_provision is False
        assert dto.is_liquidated is True
        assert dto.is_active is False
    
    def test_to_dto_service_provision(self):
        """Test converting SERVICE_PROVISION Payroll to DTO."""
        payroll = Payroll(
            payroll_id=uuid.uuid4(),
            contract_type=ContractType(value=ContractTypeEnum.SERVICE_PROVISION),
            state=StatePayroll(value=StatePayrollEnum.ACTIVE),
            base_salary=Money(amount=Decimal("0"))
        )
        
        dto = PayrollMapper.to_dto(payroll)
        
        assert dto.contract_type == "SERVICE_PROVISION"
        assert dto.state == "ACTIVE"
        assert dto.base_salary_amount == Decimal("0")
        assert dto.is_service_provision is True
        assert dto.is_active is True
    
    def test_to_dto_list(self):
        """Test converting list of Payroll entities to DTO list."""
        payroll1 = Payroll(
            payroll_id=uuid.uuid4(),
            contract_type=ContractType(value=ContractTypeEnum.FIXED_TERM),
            state=StatePayroll(value=StatePayrollEnum.LIQUIDATED),
            base_salary=Money(amount=Decimal("2000000"))
        )
        
        payroll2 = Payroll(
            payroll_id=uuid.uuid4(),
            contract_type=ContractType(value=ContractTypeEnum.INDEFINITE_TERM),
            state=StatePayroll(value=StatePayrollEnum.ACTIVE),
            base_salary=Money(amount=Decimal("2500000"))
        )
        
        dto_list = PayrollMapper.to_dto_list([payroll1, payroll2])
        
        assert isinstance(dto_list, PayrollListDTO)
        assert len(dto_list.payrolls) == 2
        assert dto_list.total_count == 2
        assert dto_list.payrolls[0].contract_type == "FIXED_TERM"
        assert dto_list.payrolls[1].contract_type == "INDEFINITE_TERM"
    
    def test_from_create_dto(self):
        """Test converting PayrollCreateDTO to Payroll domain entity."""
        create_dto = PayrollCreateDTO(
            contract_type="FIXED_TERM",
            state="LIQUIDATED",
            base_salary_amount=Decimal("2000000"),
            identification_number="12345678",
            start_date=date(2025, 1, 1)
        )
        
        payroll_id = uuid.uuid4()
        payroll = PayrollMapper.from_create_dto(create_dto, payroll_id)
        
        assert isinstance(payroll, Payroll)
        assert payroll.payroll_id == payroll_id
        assert payroll.contract_type.value == ContractTypeEnum.FIXED_TERM
        assert payroll.state.value == StatePayrollEnum.LIQUIDATED
        assert payroll.base_salary.amount == Decimal("2000000")
    
    def test_from_create_dto_invalid_contract_type(self):
        """Test creating Payroll with invalid contract type."""
        create_dto = PayrollCreateDTO(
            contract_type="INVALID_TYPE",
            state="LIQUIDATED",
            base_salary_amount=Decimal("2000000"),
            identification_number="12345678",
            start_date=date(2025, 1, 1)
        )
        
        with pytest.raises(ValueError):
            PayrollMapper.from_create_dto(create_dto, uuid.uuid4())
    
    def test_from_create_dto_invalid_state(self):
        """Test creating Payroll with invalid state."""
        create_dto = PayrollCreateDTO(
            contract_type="FIXED_TERM",
            state="INVALID_STATE",
            base_salary_amount=Decimal("2000000"),
            identification_number="12345678",
            start_date=date(2025, 1, 1)
        )
        
        with pytest.raises(ValueError):
            PayrollMapper.from_create_dto(create_dto, uuid.uuid4())
    
    def test_apply_update_dto(self):
        """Test applying PayrollUpdateDTO to existing Payroll."""
        payroll = Payroll(
            payroll_id=uuid.uuid4(),
            contract_type=ContractType(value=ContractTypeEnum.FIXED_TERM),
            state=StatePayroll(value=StatePayrollEnum.LIQUIDATED),
            base_salary=Money(amount=Decimal("2000000"))
        )
        
        update_dto = PayrollUpdateDTO(
            state="ACTIVE",
            base_salary_amount=Decimal("2500000")
        )
        
        updated_payroll = PayrollMapper.update_from_dto(payroll, update_dto)
        
        assert updated_payroll.state.value == StatePayrollEnum.ACTIVE
        assert updated_payroll.base_salary.amount == Decimal("2500000")
        # Other fields should remain unchanged
        assert updated_payroll.contract_type.value == ContractTypeEnum.FIXED_TERM


class TestPayrollHistoryMapper:
    """Test cases for PayrollHistoryMapper."""
    
    def test_to_dto(self):
        """Test converting PayrollHistory domain entity to DTO."""
        payroll_history = PayrollHistory(
            identification_number="12345678",
            payroll_id=uuid.uuid4(),
            security_id="SEC123456",
            works_value_amount=Money(amount=Decimal("1000000")),
            init_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31)
        )
        
        dto = PayrollHistoryMapper.to_dto(payroll_history)
        
        assert isinstance(dto, PayrollHistoryDTO)
        assert dto.identification_number == "12345678"
        assert dto.payroll_id == payroll_history.payroll_id
        assert dto.security_id == "SEC123456"
        assert dto.works_value_amount == Decimal("1000000")
        assert "1000000" in dto.works_value_formatted
    
    def test_to_dto_list(self):
        """Test converting list of PayrollHistory entities to DTO list."""
        history1 = PayrollHistory(
            identification_number="12345678",
            payroll_id=uuid.uuid4(),
            security_id="SEC123456",
            works_value_amount=Money(amount=Decimal("1000000")),
            init_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31)
        )
        
        history2 = PayrollHistory(
            identification_number="87654321",
            payroll_id=uuid.uuid4(),
            security_id="SEC789012",
            works_value_amount=Money(amount=Decimal("2000000")),
            init_date=date(2025, 2, 1),
            end_date=date(2025, 2, 28)
        )
        
        dto_list = PayrollHistoryMapper.to_dto_list([history1, history2])
        
        assert isinstance(dto_list, PayrollHistoryListDTO)
        assert len(dto_list.payroll_histories) == 2
        assert dto_list.total_count == 2
        assert dto_list.payroll_histories[0].identification_number == "12345678"
        assert dto_list.payroll_histories[1].identification_number == "87654321"
    
    def test_from_create_dto(self):
        """Test converting PayrollHistoryCreateDTO to PayrollHistory domain entity."""
        create_dto = PayrollHistoryCreateDTO(
            identification_number="12345678",
            payroll_id=uuid.uuid4(),
            security_id="SEC123456",
            works_value_amount=Decimal("1000000"),
            init_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31)
        )
        
        payroll_history = PayrollHistoryMapper.from_create_dto(create_dto)
        
        assert isinstance(payroll_history, PayrollHistory)
        assert payroll_history.identification_number == "12345678"
        assert payroll_history.payroll_id == create_dto.payroll_id
        assert payroll_history.security_id == "SEC123456"
        assert payroll_history.works_value_amount.amount == Decimal("1000000")
        assert payroll_history.init_date == date(2025, 1, 1)
        assert payroll_history.end_date == date(2025, 1, 31)
    
    def test_apply_update_dto(self):
        """Test applying PayrollHistoryUpdateDTO to existing PayrollHistory."""
        payroll_history = PayrollHistory(
            identification_number="12345678",
            payroll_id=uuid.uuid4(),
            security_id="SEC123456",
            works_value_amount=Money(amount=Decimal("1000000")),
            init_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31)
        )
        
        update_dto = PayrollHistoryUpdateDTO(
            works_value_amount=Decimal("1500000"),
            end_date=date(2025, 1, 15)
        )
        
        updated_history = PayrollHistoryMapper.apply_update_dto(payroll_history, update_dto)
        
        assert updated_history.works_value_amount.amount == Decimal("1500000")
        assert updated_history.end_date == date(2025, 1, 15)
        # Other fields should remain unchanged
        assert updated_history.identification_number == "12345678"
        assert updated_history.init_date == date(2025, 1, 1)
    
    def test_to_summary_dto(self):
        """Test converting list of PayrollHistory to summary DTO."""
        histories = [
            PayrollHistory(
                identification_number="12345678",
                payroll_id=uuid.uuid4(),
                security_id="SEC123456",
                works_value_amount=Money(amount=Decimal("1000000")),
                init_date=date(2025, 1, 1),
                end_date=date(2025, 1, 31)
            ),
            PayrollHistory(
                identification_number="12345678",
                payroll_id=uuid.uuid4(),
                security_id="SEC123456",
                works_value_amount=Money(amount=Decimal("2000000")),
                init_date=date(2025, 2, 1),
                end_date=date(2025, 2, 28)
            )
        ]
        
        summary = PayrollHistoryMapper.to_summary_dto(histories)
        
        assert isinstance(summary, PayrollHistorySummaryDTO)
        assert summary.employee_id == "12345678"
        assert summary.total_records == 2
        assert summary.total_works_value == Decimal("3000000")
    
    def test_to_summary_dto_empty_list(self):
        """Test creating summary DTO from empty list."""
        with pytest.raises(ValueError, match="Cannot create summary from empty list"):
            PayrollHistoryMapper.to_summary_dto([])


class TestPayrollDTOs:
    """Test cases for Payroll DTOs validation."""
    
    def test_payroll_create_dto_validation(self):
        """Test PayrollCreateDTO validation."""
        dto = PayrollCreateDTO(
            contract_type="FIXED_TERM",
            state="LIQUIDATED",
            base_salary_amount=Decimal("2000000"),
            identification_number="12345678",
            start_date=date(2025, 1, 1)
        )
        
        assert dto.contract_type == "FIXED_TERM"
        assert dto.state == "LIQUIDATED"
        assert dto.base_salary_amount == Decimal("2000000")
        assert dto.identification_number == "12345678"
    
    def test_payroll_update_dto_validation(self):
        """Test PayrollUpdateDTO validation."""
        dto = PayrollUpdateDTO(
            state="ACTIVE",
            base_salary_amount=Decimal("2500000")
        )
        
        assert dto.contract_type is None
        assert dto.state == "ACTIVE"
        assert dto.base_salary_amount == Decimal("2500000")


class TestPayrollHistoryDTOs:
    """Test cases for PayrollHistory DTOs validation."""
    
    def test_payroll_history_create_dto_validation(self):
        """Test PayrollHistoryCreateDTO validation."""
        dto = PayrollHistoryCreateDTO(
            identification_number="12345678",
            payroll_id=uuid.uuid4(),
            security_id="SEC123456",
            works_value_amount=Decimal("1000000"),
            init_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31)
        )
        
        assert dto.identification_number == "12345678"
        assert dto.security_id == "SEC123456"
        assert dto.works_value_amount == Decimal("1000000")
        assert dto.init_date == date(2025, 1, 1)
        assert dto.end_date == date(2025, 1, 31)
    
    def test_payroll_history_update_dto_validation(self):
        """Test PayrollHistoryUpdateDTO validation."""
        dto = PayrollHistoryUpdateDTO(
            works_value_amount=Decimal("1500000"),
            end_date=date(2025, 1, 15)
        )
        
        assert dto.identification_number is None
        assert dto.payroll_id is None
        assert dto.security_id is None
        assert dto.works_value_amount == Decimal("1500000")
        assert dto.init_date is None
        assert dto.end_date == date(2025, 1, 15)
