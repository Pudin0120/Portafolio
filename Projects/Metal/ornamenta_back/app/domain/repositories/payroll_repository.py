"""
Repository interface for Payroll entity.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.models.Payroll import Payroll
from app.domain.value_objects.contract_type import ContractTypeEnum
from app.domain.value_objects.state_payroll import StatePayrollEnum


class PayrollRepository(ABC):
    """
    Abstract repository for managing Payroll persistence.
    """
    
    @abstractmethod
    def get_by_id(self, payroll_id: UUID) -> Optional[Payroll]:
        """Get payroll by UUID."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Payroll]:
        """Get all payrolls."""
        pass
    
    @abstractmethod
    def get_by_contract_type(self, contract_type: ContractTypeEnum) -> List[Payroll]:
        """Get payrolls by contract type."""
        pass
    
    @abstractmethod
    def get_by_state(self, state: StatePayrollEnum) -> List[Payroll]:
        """Get payrolls by state."""
        pass
    
    @abstractmethod
    def get_by_contract_type_and_state(
        self, 
        contract_type: ContractTypeEnum, 
        state: StatePayrollEnum
    ) -> List[Payroll]:
        """Get payrolls by contract type and state."""
        pass
    
    @abstractmethod
    def get_liquidated_payrolls(self) -> List[Payroll]:
        """Get all liquidated payrolls."""
        pass
    
    @abstractmethod
    def get_active_payrolls(self) -> List[Payroll]:
        """Get all active payrolls."""
        pass
    
    @abstractmethod
    def get_paid_payrolls(self) -> List[Payroll]:
        """Get all paid payrolls."""
        pass
    
    @abstractmethod
    def get_cancelled_payrolls(self) -> List[Payroll]:
        """Get all cancelled payrolls."""
        pass
    
    @abstractmethod
    def get_fixed_term_payrolls(self) -> List[Payroll]:
        """Get all fixed term contract payrolls."""
        pass
    
    @abstractmethod
    def get_indefinite_term_payrolls(self) -> List[Payroll]:
        """Get all indefinite term contract payrolls."""
        pass
    
    @abstractmethod
    def get_service_provision_payrolls(self) -> List[Payroll]:
        """Get all service provision contract payrolls."""
        pass
    
    @abstractmethod
    def save(self, payroll: Payroll) -> Payroll:
        """Save or update a payroll."""
        pass
    
    @abstractmethod
    def delete(self, payroll_id: UUID) -> bool:
        """Delete a payroll by ID."""
        pass
    
    @abstractmethod
    def exists(self, payroll_id: UUID) -> bool:
        """Check if a payroll exists by ID."""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Get total count of payrolls."""
        pass
    
    @abstractmethod
    def count_by_state(self, state: StatePayrollEnum) -> int:
        """Get count of payrolls by state."""
        pass
    
    @abstractmethod
    def count_by_contract_type(self, contract_type: ContractTypeEnum) -> int:
        """Get count of payrolls by contract type."""
        pass
