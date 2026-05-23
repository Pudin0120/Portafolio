"""
Tests for PostgreSQL Payroll and PayrollHistory repository implementations.
"""
import pytest
import uuid
from decimal import Decimal
from datetime import date
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.domain.models.Payroll import Payroll
from app.domain.models.payroll_history import PayrollHistory
from app.domain.value_objects.money import Money
from app.domain.value_objects.contract_type import ContractType, ContractTypeEnum
from app.domain.value_objects.state_payroll import StatePayroll, StatePayrollEnum
from app.infrastructure.adapters.repositories.payroll_repository import PostgresPayrollRepository
from app.infrastructure.adapters.repositories.payroll_history_repository import PostgresPayrollHistoryRepository
from app.infrastructure.adapters.db.models.payroll_model import PayrollModel
from app.infrastructure.adapters.db.models.payroll_history_model import PayrollHistoryModel


class TestPostgresPayrollRepository:
    """Test cases for PostgresPayrollRepository."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def payroll_repo(self, mock_session):
        """Create a PostgresPayrollRepository instance."""
        return PostgresPayrollRepository(mock_session)
    
    @pytest.fixture
    def sample_payroll(self):
        """Create a sample Payroll domain entity."""
        return Payroll(
            payroll_id=uuid.uuid4(),
            contract_type=ContractType(value=ContractTypeEnum.FIXED_TERM),
            state=StatePayroll(value=StatePayrollEnum.LIQUIDATED),
            base_salary=Money(amount=Decimal("2000000")),
            total_tasks_value=Money(amount=Decimal("500000")),
            completed_tasks=[uuid.uuid4(), uuid.uuid4()]
        )
    
    @pytest.fixture
    def sample_payroll_model(self, sample_payroll):
        """Create a sample PayrollModel."""
        return PayrollModel(
            id=sample_payroll.payroll_id,
            contract_type=sample_payroll.contract_type.value.value,
            state=sample_payroll.state.value.value,
            base_salary_amount=float(sample_payroll.base_salary.amount),
            base_salary_currency="COP",
            total_tasks_value_amount=float(sample_payroll.total_tasks_value.amount),
            total_tasks_value_currency="COP",
            completed_tasks=sample_payroll.completed_tasks
        )
    
    def test_get_by_id_success(self, payroll_repo, mock_session, sample_payroll_model):
        """Test successful get_by_id operation."""
        # Arrange
        payroll_id = sample_payroll_model.id
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_payroll_model
        mock_session.execute.return_value = mock_result
        
        # Act
        result = payroll_repo.get_by_id(payroll_id)
        
        # Assert
        assert result is not None
        assert result.payroll_id == payroll_id
        assert result.contract_type.value == ContractTypeEnum.FIXED_TERM
        assert result.state.value == StatePayrollEnum.LIQUIDATED
        mock_session.execute.assert_called_once()
    
    def test_get_by_id_not_found(self, payroll_repo, mock_session):
        """Test get_by_id when payroll not found."""
        # Arrange
        payroll_id = uuid.uuid4()
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Act
        result = payroll_repo.get_by_id(payroll_id)
        
        # Assert
        assert result is None
        mock_session.execute.assert_called_once()
    
    def test_get_all(self, payroll_repo, mock_session, sample_payroll_model):
        """Test get_all operation."""
        # Arrange
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_payroll_model]
        mock_session.execute.return_value = mock_result
        
        # Act
        result = payroll_repo.get_all()
        
        # Assert
        assert len(result) == 1
        assert result[0].payroll_id == sample_payroll_model.id
        mock_session.execute.assert_called_once()
    
    def test_get_by_contract_type(self, payroll_repo, mock_session, sample_payroll_model):
        """Test get_by_contract_type operation."""
        # Arrange
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_payroll_model]
        mock_session.execute.return_value = mock_result
        
        # Act
        result = payroll_repo.get_by_contract_type(ContractTypeEnum.FIXED_TERM)
        
        # Assert
        assert len(result) == 1
        assert result[0].contract_type.value == ContractTypeEnum.FIXED_TERM
        mock_session.execute.assert_called_once()
    
    def test_get_by_state(self, payroll_repo, mock_session, sample_payroll_model):
        """Test get_by_state operation."""
        # Arrange
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_payroll_model]
        mock_session.execute.return_value = mock_result
        
        # Act
        result = payroll_repo.get_by_state(StatePayrollEnum.LIQUIDATED)
        
        # Assert
        assert len(result) == 1
        assert result[0].state.value == StatePayrollEnum.LIQUIDATED
        mock_session.execute.assert_called_once()
    
    def test_save_new_payroll(self, payroll_repo, mock_session, sample_payroll, sample_payroll_model):
        """Test save operation for new payroll."""
        # Arrange
        mock_merged_model = Mock()
        mock_merged_model.id = sample_payroll.payroll_id
        mock_merged_model.contract_type = sample_payroll_model.contract_type
        mock_merged_model.state = sample_payroll_model.state
        mock_merged_model.base_salary_amount = sample_payroll_model.base_salary_amount
        mock_merged_model.total_tasks_value_amount = sample_payroll_model.total_tasks_value_amount
        mock_merged_model.completed_tasks = sample_payroll_model.completed_tasks
        mock_session.merge.return_value = mock_merged_model
        
        # Act
        result = payroll_repo.save(sample_payroll)
        
        # Assert
        assert result is not None
        mock_session.merge.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_merged_model)
    
    def test_delete_success(self, payroll_repo, mock_session, sample_payroll_model):
        """Test successful delete operation."""
        # Arrange
        payroll_id = sample_payroll_model.id
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_payroll_model
        mock_session.execute.return_value = mock_result
        
        # Act
        result = payroll_repo.delete(payroll_id)
        
        # Assert
        assert result is True
        mock_session.delete.assert_called_once_with(sample_payroll_model)
        mock_session.commit.assert_called_once()
    
    def test_delete_not_found(self, payroll_repo, mock_session):
        """Test delete when payroll not found."""
        # Arrange
        payroll_id = uuid.uuid4()
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Act
        result = payroll_repo.delete(payroll_id)
        
        # Assert
        assert result is False
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()
    
    def test_exists_true(self, payroll_repo, mock_session):
        """Test exists when payroll exists."""
        # Arrange
        payroll_id = uuid.uuid4()
        mock_result = Mock()
        mock_result.scalar.return_value = 1
        mock_session.execute.return_value = mock_result
        
        # Act
        result = payroll_repo.exists(payroll_id)
        
        # Assert
        assert result is True
        mock_session.execute.assert_called_once()
    
    def test_exists_false(self, payroll_repo, mock_session):
        """Test exists when payroll does not exist."""
        # Arrange
        payroll_id = uuid.uuid4()
        mock_result = Mock()
        mock_result.scalar.return_value = 0
        mock_session.execute.return_value = mock_result
        
        # Act
        result = payroll_repo.exists(payroll_id)
        
        # Assert
        assert result is False
        mock_session.execute.assert_called_once()
    
    def test_count(self, payroll_repo, mock_session):
        """Test count operation."""
        # Arrange
        mock_result = Mock()
        mock_result.scalar.return_value = 5
        mock_session.execute.return_value = mock_result
        
        # Act
        result = payroll_repo.count()
        
        # Assert
        assert result == 5
        mock_session.execute.assert_called_once()
    
    def test_to_domain_conversion(self, sample_payroll_model):
        """Test conversion from model to domain entity."""
        # Act
        result = PostgresPayrollRepository._to_domain(sample_payroll_model)
        
        # Assert
        assert result.payroll_id == sample_payroll_model.id
        assert result.contract_type.value == ContractTypeEnum.FIXED_TERM
        assert result.state.value == StatePayrollEnum.LIQUIDATED
        assert result.base_salary.amount == Decimal(str(sample_payroll_model.base_salary_amount))
        assert result.total_tasks_value.amount == Decimal(str(sample_payroll_model.total_tasks_value_amount))
        assert result.completed_tasks == sample_payroll_model.completed_tasks
    
    def test_to_model_conversion(self, sample_payroll):
        """Test conversion from domain entity to model."""
        # Act
        result = PostgresPayrollRepository._to_model(sample_payroll)
        
        # Assert
        assert result.id == sample_payroll.payroll_id
        assert result.contract_type == sample_payroll.contract_type.value.value
        assert result.state == sample_payroll.state.value.value
        assert result.base_salary_amount == float(sample_payroll.base_salary.amount)
        assert result.total_tasks_value_amount == float(sample_payroll.total_tasks_value.amount)
        assert result.completed_tasks == sample_payroll.completed_tasks


class TestPostgresPayrollHistoryRepository:
    """Test cases for PostgresPayrollHistoryRepository."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def history_repo(self, mock_session):
        """Create a PostgresPayrollHistoryRepository instance."""
        return PostgresPayrollHistoryRepository(mock_session)
    
    @pytest.fixture
    def sample_payroll_history(self):
        """Create a sample PayrollHistory domain entity."""
        return PayrollHistory(
            identification_number="12345678",
            payroll_id=uuid.uuid4(),
            security_id="SEC123456",
            works_value=Money(amount=Decimal("1000000")),
            labor=Money(amount=Decimal("500000")),
            init_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31)
        )
    
    @pytest.fixture
    def sample_payroll_history_model(self, sample_payroll_history):
        """Create a sample PayrollHistoryModel."""
        return PayrollHistoryModel(
            id=uuid.uuid4(),
            identification_number=sample_payroll_history.identification_number,
            payroll_id=sample_payroll_history.payroll_id,
            security_id=sample_payroll_history.security_id,
            works_value_amount=float(sample_payroll_history.works_value.amount),
            works_value_currency="COP",
            labor_amount=float(sample_payroll_history.labor.amount),
            labor_currency="COP",
            init_date=sample_payroll_history.init_date,
            end_date=sample_payroll_history.end_date
        )
    
    def test_get_by_identification_number(self, history_repo, mock_session, sample_payroll_history_model):
        """Test get_by_identification_number operation."""
        # Arrange
        identification_number = sample_payroll_history_model.identification_number
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_payroll_history_model]
        mock_session.execute.return_value = mock_result
        
        # Act
        result = history_repo.get_by_identification_number(identification_number)
        
        # Assert
        assert len(result) == 1
        assert result[0].identification_number == identification_number
        mock_session.execute.assert_called_once()
    
    def test_get_by_payroll_id(self, history_repo, mock_session, sample_payroll_history_model):
        """Test get_by_payroll_id operation."""
        # Arrange
        payroll_id = sample_payroll_history_model.payroll_id
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_payroll_history_model]
        mock_session.execute.return_value = mock_result
        
        # Act
        result = history_repo.get_by_payroll_id(payroll_id)
        
        # Assert
        assert len(result) == 1
        assert result[0].payroll_id == payroll_id
        mock_session.execute.assert_called_once()
    
    def test_get_by_date_range(self, history_repo, mock_session, sample_payroll_history_model):
        """Test get_by_date_range operation."""
        # Arrange
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_payroll_history_model]
        mock_session.execute.return_value = mock_result
        
        # Act
        result = history_repo.get_by_date_range(start_date, end_date)
        
        # Assert
        assert len(result) == 1
        mock_session.execute.assert_called_once()
    
    def test_get_latest_by_employee(self, history_repo, mock_session, sample_payroll_history_model):
        """Test get_latest_by_employee operation."""
        # Arrange
        identification_number = sample_payroll_history_model.identification_number
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_payroll_history_model
        mock_session.execute.return_value = mock_result
        
        # Act
        result = history_repo.get_latest_by_employee(identification_number)
        
        # Assert
        assert result is not None
        assert result.identification_number == identification_number
        mock_session.execute.assert_called_once()
    
    def test_save_new_history(self, history_repo, mock_session, sample_payroll_history, sample_payroll_history_model):
        """Test save operation for new payroll history."""
        # Arrange
        mock_merged_model = Mock()
        mock_merged_model.id = sample_payroll_history_model.id
        mock_merged_model.identification_number = sample_payroll_history_model.identification_number
        mock_merged_model.payroll_id = sample_payroll_history_model.payroll_id
        mock_merged_model.security_id = sample_payroll_history_model.security_id
        mock_merged_model.works_value_amount = sample_payroll_history_model.works_value_amount
        mock_merged_model.labor_amount = sample_payroll_history_model.labor_amount
        mock_merged_model.init_date = sample_payroll_history_model.init_date
        mock_merged_model.end_date = sample_payroll_history_model.end_date
        mock_session.merge.return_value = mock_merged_model
        
        # Act
        result = history_repo.save(sample_payroll_history)
        
        # Assert
        assert result is not None
        mock_session.merge.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_merged_model)
    
    def test_delete_by_payroll_id(self, history_repo, mock_session, sample_payroll_history_model):
        """Test delete_by_payroll_id operation."""
        # Arrange
        payroll_id = sample_payroll_history_model.payroll_id
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_payroll_history_model]
        mock_session.execute.return_value = mock_result
        
        # Act
        result = history_repo.delete_by_payroll_id(payroll_id)
        
        # Assert
        assert result == 1
        mock_session.delete.assert_called_once_with(sample_payroll_history_model)
        mock_session.commit.assert_called_once()
    
    def test_get_employee_summary(self, history_repo, mock_session):
        """Test get_employee_summary operation."""
        # Arrange
        identification_number = "12345678"
        mock_result = Mock()
        mock_result.first.return_value = Mock(
            total_records=2,
            total_works_value=2000000.0,
            total_labor_cost=1000000.0,
            total_value=3000000.0,
            earliest_date=date(2025, 1, 1),
            latest_date=date(2025, 1, 31),
            total_days=31
        )
        mock_session.execute.return_value = mock_result
        
        # Act
        result = history_repo.get_employee_summary(identification_number)
        
        # Assert
        assert result['total_records'] == 2
        assert result['total_works_value'] == 2000000.0
        assert result['total_labor_cost'] == 1000000.0
        assert result['total_value'] == 3000000.0
        assert result['average_daily_value'] == 3000000.0 / 31
        assert result['earliest_date'] == date(2025, 1, 1)
        assert result['latest_date'] == date(2025, 1, 31)
        assert result['total_days'] == 31
        mock_session.execute.assert_called_once()
    
    def test_get_employee_summary_empty(self, history_repo, mock_session):
        """Test get_employee_summary when no records found."""
        # Arrange
        identification_number = "99999999"
        mock_result = Mock()
        mock_result.first.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Act
        result = history_repo.get_employee_summary(identification_number)
        
        # Assert
        assert result['total_records'] == 0
        assert result['total_works_value'] == 0.0
        assert result['total_labor_cost'] == 0.0
        assert result['total_value'] == 0.0
        assert result['average_daily_value'] == 0.0
        assert result['earliest_date'] is None
        assert result['latest_date'] is None
        assert result['total_days'] == 0
        mock_session.execute.assert_called_once()
    
    def test_to_domain_conversion(self, sample_payroll_history_model):
        """Test conversion from model to domain entity."""
        # Act
        result = PostgresPayrollHistoryRepository._to_domain(sample_payroll_history_model)
        
        # Assert
        assert result.identification_number == sample_payroll_history_model.identification_number
        assert result.payroll_id == sample_payroll_history_model.payroll_id
        assert result.security_id == sample_payroll_history_model.security_id
        assert result.works_value.amount == Decimal(str(sample_payroll_history_model.works_value_amount))
        assert result.labor.amount == Decimal(str(sample_payroll_history_model.labor_amount))
        assert result.init_date == sample_payroll_history_model.init_date
        assert result.end_date == sample_payroll_history_model.end_date
    
    def test_to_model_conversion(self, sample_payroll_history):
        """Test conversion from domain entity to model."""
        # Act
        result = PostgresPayrollHistoryRepository._to_model(sample_payroll_history)
        
        # Assert
        assert result.identification_number == sample_payroll_history.identification_number
        assert result.payroll_id == sample_payroll_history.payroll_id
        assert result.security_id == sample_payroll_history.security_id
        assert result.works_value_amount == float(sample_payroll_history.works_value.amount)
        assert result.labor_amount == float(sample_payroll_history.labor.amount)
        assert result.init_date == sample_payroll_history.init_date
        assert result.end_date == sample_payroll_history.end_date
