"""
Domain model for Payroll entity.

Payroll represents the payroll information for an employee including
base salary, task values, and completed tasks tracking.
"""
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING
import uuid

from app.domain.value_objects.money import Money
from app.domain.value_objects.contract_type import ContractType
from app.domain.value_objects.state_payroll import StatePayroll
from app.domain.domain_event import DomainEvent
from app.domain.models.payroll_history import PayrollHistory

if TYPE_CHECKING:
    from app.domain.models.user import User
    from app.domain.models.task_assignment import TaskAssignment


@dataclass
class Payroll:
    
    payroll_id: uuid.UUID
    contract_type: ContractType
    state: StatePayroll
    base_salary: Money
    histories: List[PayrollHistory] = field(default_factory=list) 
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False, repr=False)
    
    def __post_init__(self):
        """
        Validaciones post-inicializacion.
        
        Valida que los contratos de prestacion de servicios no tengan salario base.
        """
        if self.contract_type.is_service_provision and not self.base_salary.is_zero():
            raise ValueError(
                "Los contratos de prestacion de servicios (SERVICE_PROVISION) "
                "no pueden tener salario base. Solo deben tener valor de tasks."
            )
    
    """@property
    def total_payroll(self) -> Money:
    
        if self.contract_type.is_service_provision:
            return 
        else:
            return self.base_salary
    """
    @property
    def is_liquidated(self) -> bool:
        """Verifica si la payroll esta liquidada."""
        return self.state.is_liquidated
    
    @property
    def is_active(self) -> bool:
        """Verifica si la payroll esta activa."""
        return self.state.is_active
    
    @property
    def is_paid(self) -> bool:
        """Verifica si la payroll esta pagada."""
        return self.state.is_paid
    
    @property
    def is_cancelled(self) -> bool:
        """Verifica si la payroll esta cancelada."""
        return self.state.is_cancelled
    
    @property
    def is_fixed_term(self) -> bool:
        """Check if contract type is FIXED_TERM."""
        return self.contract_type.is_fixed_term
    
    @property
    def is_indefinite_term(self) -> bool:
        """Check if contract type is INDEFINITE_TERM."""
        return self.contract_type.is_indefinite_term
    
    @property
    def is_service_provision(self) -> bool:
        """Check if contract type is SERVICE_PROVISION."""
        return self.contract_type.is_service_provision
    
    def change_state(self, new_state: StatePayroll, changed_by: 'User', reason: str = "") -> None:
        """
        Cambia el estado de la payroll y registra el evento de dominio.
        
        Args:
            new_state: Nuevo estado de la payroll
            changed_by: User que ejecuta el cambio
            reason: Razon opcional del cambio
        """
        from datetime import datetime
        from app.domain.events.payroll_events import PayrollStateChanged
        
        previous_state = self.state.value.value
        self.state = new_state
        
        # Generar evento de dominio
        event = PayrollStateChanged(
            event_id=uuid.uuid4(),
            occurred_at=datetime.now(),
            aggregate_id=uuid.uuid4(),
            payroll_id=self.payroll_id,
            previous_state=previous_state,
            new_state=new_state.value.value,
            changed_by_user_id=changed_by.identification_number.value,
            changed_by_user_name=changed_by.full_name,
            reason=reason
        )
        
        self._domain_events.append(event)
    
    def activate(self, activated_by: 'User', reason: str = "") -> None:
        """
        Activa la payroll.
        
        Args:
            activated_by: User que activa la payroll
            reason: Razon opcional de la activacion
        """
        self.change_state(self.state.to_active(), activated_by, reason)
    
    def pay(self, paid_by: 'User', reason: str = "") -> None:
        """
        Marca la payroll como pagada.
        
        Args:
            paid_by: User que marca como pagada
            reason: Razon opcional del pago
        """
        self.change_state(self.state.to_paid(), paid_by, reason)
    
    def cancel(self, cancelled_by: 'User', reason: str = "") -> None:
        """
        Cancela la payroll.
        
        Args:
            cancelled_by: User que cancela la payroll
            reason: Razon opcional de la cancelacion
        """
        self.change_state(self.state.to_cancelled(), cancelled_by, reason)
    
    def clear_domain_events(self) -> List[DomainEvent]:
        """
        Retorna y limpia los eventos de dominio acumulados.
        
        Returns:
            Lista de eventos de dominio acumulados
        """
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
