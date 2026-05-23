"""
Tests for Payroll and PayrollHistory repository interfaces.
"""
import pytest
import uuid
from decimal import Decimal
from datetime import date
from abc import ABC

from app.domain.repositories.payroll_repository import PayrollRepository
from app.domain.repositories.payroll_history_repository import PayrollHistoryRepository
from app.domain.models.Payroll import Payroll
from app.domain.models.payroll_history import PayrollHistory
from app.domain.value_objects.money import Money
from app.domain.value_objects.contract_type import ContractType, ContractTypeEnum
from app.domain.value_objects.state_payroll import StatePayroll, StatePayrollEnum


class TestPayrollRepository:
    """Test cases for PayrollRepository interface."""
    
    def test_payroll_repository_is_abstract(self):
        """Test that PayrollRepository is abstract and cannot be instantiated."""
        with pytest.raises(TypeError):
            PayrollRepository()
    
    def test_payroll_repository_methods_exist(self):
        """Test that all required methods exist in PayrollRepository."""
        methods = [
            'get_by_id',
            'get_all',
            'get_by_contract_type',
            'get_by_state',
            'get_by_contract_type_and_state',
            'get_by_completed_task',
            'get_liquidated_payrolls',
            'get_active_payrolls',
            'get_paid_payrolls',
            'get_cancelled_payrolls',
            'get_fixed_term_payrolls',
            'get_indefinite_term_payrolls',
            'get_service_provision_payrolls',
            'save',
            'delete',
            'exists',
            'count',
            'count_by_state',
            'count_by_contract_type'
        ]
        
        for method_name in methods:
            assert hasattr(PayrollRepository, method_name)
            method = getattr(PayrollRepository, method_name)
            assert callable(method)
    
    def test_payroll_repository_inherits_from_abc(self):
        """Test that PayrollRepository inherits from ABC."""
        assert issubclass(PayrollRepository, ABC)
    
    def test_payroll_repository_method_signatures(self):
        """Test that PayrollRepository methods have correct signatures."""
        # Test get_by_id signature
        import inspect
        sig = inspect.signature(PayrollRepository.get_by_id)
        params = list(sig.parameters.keys())
        assert params == ['self', 'payroll_id']
        assert sig.return_annotation.__name__ == 'Optional'
        
        # Test get_by_contract_type signature
        sig = inspect.signature(PayrollRepository.get_by_contract_type)
        params = list(sig.parameters.keys())
        assert params == ['self', 'contract_type']
        assert sig.return_annotation.__name__ == 'List'
        
        # Test save signature
        sig = inspect.signature(PayrollRepository.save)
        params = list(sig.parameters.keys())
        assert params == ['self', 'payroll']
        assert sig.return_annotation.__name__ == 'Payroll'


class TestPayrollHistoryRepository:
    """Test cases for PayrollHistoryRepository interface."""
    
    def test_payroll_history_repository_is_abstract(self):
        """Test that PayrollHistoryRepository is abstract and cannot be instantiated."""
        with pytest.raises(TypeError):
            PayrollHistoryRepository()
    
    def test_payroll_history_repository_methods_exist(self):
        """Test that all required methods exist in PayrollHistoryRepository."""
        methods = [
            'get_by_id',
            'get_all',
            'get_by_identification_number',
            'get_by_payroll_id',
            'get_by_security_id',
            'get_by_date_range',
            'get_by_employee_and_date_range',
            'get_by_init_date',
            'get_by_end_date',
            'get_by_period',
            'get_by_employee_and_period',
            'get_latest_by_employee',
            'get_earliest_by_employee',
            'get_by_minimum_works_value',
            'get_by_minimum_labor_cost',
            'get_by_minimum_total_value',
            'get_valid_periods',
            'get_invalid_periods',
            'save',
            'delete',
            'delete_by_payroll_id',
            'delete_by_employee',
            'exists_by_payroll_id',
            'exists_by_employee',
            'count',
            'count_by_employee',
            'count_by_payroll_id',
            'count_by_date_range',
            'get_employee_summary'
        ]
        
        for method_name in methods:
            assert hasattr(PayrollHistoryRepository, method_name)
            method = getattr(PayrollHistoryRepository, method_name)
            assert callable(method)
    
    def test_payroll_history_repository_inherits_from_abc(self):
        """Test that PayrollHistoryRepository inherits from ABC."""
        assert issubclass(PayrollHistoryRepository, ABC)
    
    def test_payroll_history_repository_method_signatures(self):
        """Test that PayrollHistoryRepository methods have correct signatures."""
        import inspect
        
        # Test get_by_identification_number signature
        sig = inspect.signature(PayrollHistoryRepository.get_by_identification_number)
        params = list(sig.parameters.keys())
        assert params == ['self', 'identification_number']
        assert sig.return_annotation.__name__ == 'List'
        
        # Test get_by_date_range signature
        sig = inspect.signature(PayrollHistoryRepository.get_by_date_range)
        params = list(sig.parameters.keys())
        assert params == ['self', 'start_date', 'end_date']
        assert sig.return_annotation.__name__ == 'List'
        
        # Test save signature
        sig = inspect.signature(PayrollHistoryRepository.save)
        params = list(sig.parameters.keys())
        assert params == ['self', 'payroll_history']
        assert sig.return_annotation.__name__ == 'PayrollHistory'
        
        # Test get_employee_summary signature
        sig = inspect.signature(PayrollHistoryRepository.get_employee_summary)
        params = list(sig.parameters.keys())
        assert params == ['self', 'identification_number']
        assert sig.return_annotation.__name__ == 'dict'


class ConcretePayrollRepository(PayrollRepository):
    """Concrete implementation for testing PayrollRepository interface."""
    
    def __init__(self):
        self.payrolls = {}
    
    def get_by_id(self, payroll_id: uuid.UUID):
        return self.payrolls.get(payroll_id)
    
    def get_all(self):
        return list(self.payrolls.values())
    
    def get_by_contract_type(self, contract_type: ContractTypeEnum):
        return [p for p in self.payrolls.values() if p.contract_type.value == contract_type]
    
    def get_by_state(self, state: StatePayrollEnum):
        return [p for p in self.payrolls.values() if p.state.value == state]
    
    def get_by_contract_type_and_state(self, contract_type: ContractTypeEnum, state: StatePayrollEnum):
        return [p for p in self.payrolls.values() 
                if p.contract_type.value == contract_type and p.state.value == state]
    
    def get_by_completed_task(self, task_id: uuid.UUID):
        return [p for p in self.payrolls.values() if task_id in p.completed_tasks]
    
    def get_liquidated_payrolls(self):
        return self.get_by_state(StatePayrollEnum.LIQUIDATED)
    
    def get_active_payrolls(self):
        return self.get_by_state(StatePayrollEnum.ACTIVE)
    
    def get_paid_payrolls(self):
        return self.get_by_state(StatePayrollEnum.PAID)
    
    def get_cancelled_payrolls(self):
        return self.get_by_state(StatePayrollEnum.CANCELLED)
    
    def get_fixed_term_payrolls(self):
        return self.get_by_contract_type(ContractTypeEnum.FIXED_TERM)
    
    def get_indefinite_term_payrolls(self):
        return self.get_by_contract_type(ContractTypeEnum.INDEFINITE_TERM)
    
    def get_service_provision_payrolls(self):
        return self.get_by_contract_type(ContractTypeEnum.SERVICE_PROVISION)
    
    def save(self, payroll: Payroll):
        self.payrolls[payroll.payroll_id] = payroll
        return payroll
    
    def delete(self, payroll_id: uuid.UUID):
        if payroll_id in self.payrolls:
            del self.payrolls[payroll_id]
            return True
        return False
    
    def exists(self, payroll_id: uuid.UUID):
        return payroll_id in self.payrolls
    
    def count(self):
        return len(self.payrolls)
    
    def count_by_state(self, state: StatePayrollEnum):
        return len(self.get_by_state(state))
    
    def count_by_contract_type(self, contract_type: ContractTypeEnum):
        return len(self.get_by_contract_type(contract_type))


class ConcretePayrollHistoryRepository(PayrollHistoryRepository):
    """Concrete implementation for testing PayrollHistoryRepository interface."""
    
    def __init__(self):
        self.histories = []
    
    def get_by_id(self, history_id: uuid.UUID):
        # Since PayrollHistory doesn't have an ID field, this would need to be implemented
        # when an ID field is added to the domain model
        return None
    
    def get_all(self):
        return self.histories.copy()
    
    def get_by_identification_number(self, identification_number: str):
        return [h for h in self.histories if h.identification_number == identification_number]
    
    def get_by_payroll_id(self, payroll_id: uuid.UUID):
        return [h for h in self.histories if h.payroll_id == payroll_id]
    
    def get_by_security_id(self, security_id: str):
        return [h for h in self.histories if h.security_id == security_id]
    
    def get_by_date_range(self, start_date: date, end_date: date):
        return [h for h in self.histories 
                if h.init_date >= start_date and h.end_date <= end_date]
    
    def get_by_employee_and_date_range(self, identification_number: str, start_date: date, end_date: date):
        return [h for h in self.histories 
                if h.identification_number == identification_number
                and h.init_date >= start_date and h.end_date <= end_date]
    
    def get_by_init_date(self, init_date: date):
        return [h for h in self.histories if h.init_date == init_date]
    
    def get_by_end_date(self, end_date: date):
        return [h for h in self.histories if h.end_date == end_date]
    
    def get_by_period(self, init_date: date, end_date: date):
        return [h for h in self.histories 
                if h.init_date == init_date and h.end_date == end_date]
    
    def get_by_employee_and_period(self, identification_number: str, init_date: date, end_date: date):
        return [h for h in self.histories 
                if h.identification_number == identification_number
                and h.init_date == init_date and h.end_date == end_date]
    
    def get_latest_by_employee(self, identification_number: str):
        employee_histories = self.get_by_identification_number(identification_number)
        if not employee_histories:
            return None
        return max(employee_histories, key=lambda h: h.end_date)
    
    def get_earliest_by_employee(self, identification_number: str):
        employee_histories = self.get_by_identification_number(identification_number)
        if not employee_histories:
            return None
        return min(employee_histories, key=lambda h: h.init_date)
    
    def get_by_minimum_works_value(self, min_value: float):
        return [h for h in self.histories if h.works_value.amount >= Decimal(str(min_value))]
    
    def get_by_minimum_labor_cost(self, min_cost: float):
        return [h for h in self.histories if h.labor.amount >= Decimal(str(min_cost))]
    
    def get_by_minimum_total_value(self, min_value: float):
        return [h for h in self.histories if h.total_value.amount >= Decimal(str(min_value))]
    
    def get_valid_periods(self):
        return [h for h in self.histories if h.is_valid_period()]
    
    def get_invalid_periods(self):
        return [h for h in self.histories if not h.is_valid_period()]
    
    def save(self, payroll_history: PayrollHistory):
        self.histories.append(payroll_history)
        return payroll_history
    
    def delete(self, history_id: uuid.UUID):
        # Since PayrollHistory doesn't have an ID field, this would need to be implemented
        # when an ID field is added to the domain model
        return False
    
    def delete_by_payroll_id(self, payroll_id: uuid.UUID):
        initial_count = len(self.histories)
        self.histories = [h for h in self.histories if h.payroll_id != payroll_id]
        return initial_count - len(self.histories)
    
    def delete_by_employee(self, identification_number: str):
        initial_count = len(self.histories)
        self.histories = [h for h in self.histories if h.identification_number != identification_number]
        return initial_count - len(self.histories)
    
    def exists_by_payroll_id(self, payroll_id: uuid.UUID):
        return any(h.payroll_id == payroll_id for h in self.histories)
    
    def exists_by_employee(self, identification_number: str):
        return any(h.identification_number == identification_number for h in self.histories)
    
    def count(self):
        return len(self.histories)
    
    def count_by_employee(self, identification_number: str):
        return len(self.get_by_identification_number(identification_number))
    
    def count_by_payroll_id(self, payroll_id: uuid.UUID):
        return len(self.get_by_payroll_id(payroll_id))
    
    def count_by_date_range(self, start_date: date, end_date: date):
        return len(self.get_by_date_range(start_date, end_date))
    
    def get_employee_summary(self, identification_number: str):
        employee_histories = self.get_by_identification_number(identification_number)
        if not employee_histories:
            return {
                'total_records': 0,
                'total_works_value': 0.0,
                'total_labor_cost': 0.0,
                'total_value': 0.0,
                'average_daily_value': 0.0,
                'earliest_date': None,
                'latest_date': None,
                'total_days': 0
            }
        
        total_works_value = sum(h.works_value.amount for h in employee_histories)
        total_labor_cost = sum(h.labor.amount for h in employee_histories)
        total_value = sum(h.total_value.amount for h in employee_histories)
        total_days = sum(h.calculate_period_days() for h in employee_histories)
        average_daily_value = total_value / total_days if total_days > 0 else 0
        
        all_dates = []
        for h in employee_histories:
            all_dates.extend([h.init_date, h.end_date])
        
        return {
            'total_records': len(employee_histories),
            'total_works_value': float(total_works_value),
            'total_labor_cost': float(total_labor_cost),
            'total_value': float(total_value),
            'average_daily_value': float(average_daily_value),
            'earliest_date': min(all_dates),
            'latest_date': max(all_dates),
            'total_days': total_days
        }


class TestConcretePayrollRepository:
    """Test cases for concrete PayrollRepository implementation."""
    
    def test_concrete_payroll_repository_operations(self):
        """Test basic operations of concrete PayrollRepository."""
        repo = ConcretePayrollRepository()
        
        # Create a payroll
        payroll = Payroll(
            payroll_id=uuid.uuid4(),
            contract_type=ContractType(value=ContractTypeEnum.FIXED_TERM),
            state=StatePayroll(value=StatePayrollEnum.LIQUIDATED),
            base_salary=Money(amount=Decimal("2000000")),
            total_tasks_value=Money(amount=Decimal("500000"))
        )
        
        # Test save
        saved_payroll = repo.save(payroll)
        assert saved_payroll == payroll
        
        # Test get_by_id
        retrieved_payroll = repo.get_by_id(payroll.payroll_id)
        assert retrieved_payroll == payroll
        
        # Test exists
        assert repo.exists(payroll.payroll_id) is True
        assert repo.exists(uuid.uuid4()) is False
        
        # Test count
        assert repo.count() == 1
        
        # Test get_by_contract_type
        fixed_term_payrolls = repo.get_by_contract_type(ContractTypeEnum.FIXED_TERM)
        assert len(fixed_term_payrolls) == 1
        assert fixed_term_payrolls[0] == payroll
        
        # Test get_by_state
        liquidated_payrolls = repo.get_by_state(StatePayrollEnum.LIQUIDATED)
        assert len(liquidated_payrolls) == 1
        assert liquidated_payrolls[0] == payroll
        
        # Test delete
        deleted = repo.delete(payroll.payroll_id)
        assert deleted is True
        assert repo.count() == 0
        assert repo.exists(payroll.payroll_id) is False


class TestConcretePayrollHistoryRepository:
    """Test cases for concrete PayrollHistoryRepository implementation."""
    
    def test_concrete_payroll_history_repository_operations(self):
        """Test basic operations of concrete PayrollHistoryRepository."""
        repo = ConcretePayrollHistoryRepository()
        
        # Create a payroll history
        payroll_history = PayrollHistory(
            identification_number="12345678",
            payroll_id=uuid.uuid4(),
            security_id="SEC123456",
            works_value=Money(amount=Decimal("1000000")),
            labor=Money(amount=Decimal("500000")),
            init_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31)
        )
        
        # Test save
        saved_history = repo.save(payroll_history)
        assert saved_history == payroll_history
        
        # Test get_all
        all_histories = repo.get_all()
        assert len(all_histories) == 1
        assert all_histories[0] == payroll_history
        
        # Test get_by_identification_number
        employee_histories = repo.get_by_identification_number("12345678")
        assert len(employee_histories) == 1
        assert employee_histories[0] == payroll_history
        
        # Test get_by_payroll_id
        payroll_histories = repo.get_by_payroll_id(payroll_history.payroll_id)
        assert len(payroll_histories) == 1
        assert payroll_histories[0] == payroll_history
        
        # Test exists_by_employee
        assert repo.exists_by_employee("12345678") is True
        assert repo.exists_by_employee("87654321") is False
        
        # Test count
        assert repo.count() == 1
        assert repo.count_by_employee("12345678") == 1
        
        # Test get_employee_summary
        summary = repo.get_employee_summary("12345678")
        assert summary['total_records'] == 1
        assert summary['total_works_value'] == 1000000.0
        assert summary['total_labor_cost'] == 500000.0
        assert summary['total_value'] == 1500000.0
        assert summary['total_days'] == 31
        assert summary['earliest_date'] == date(2025, 1, 1)
        assert summary['latest_date'] == date(2025, 1, 31)
        
        # Test delete_by_employee
        deleted_count = repo.delete_by_employee("12345678")
        assert deleted_count == 1
        assert repo.count() == 0
