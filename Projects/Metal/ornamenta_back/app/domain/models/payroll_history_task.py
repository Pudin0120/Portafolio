"""
Domain model for PayrollHistoryTask entity.

PayrollHistoryTask represents the association between a PayrollHistory
and a Task, tracking which tasks were completed and validated for a specific
payroll period (SERVICE_PROVISION contracts only).
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class PayrollHistoryTask:
    """
    Modelo de dominio para la asociacion entre PayrollHistory y Task.
    
    Esta entidad representa la relacion entre un historial de payroll
    y una task finalizada, permitiendo trazabilidad completa de que
    tasks contribuyen al pago de un periodo especifico.
    
    Solo aplica para contratos de prestacion de servicios (SERVICE_PROVISION).
    
    Attributes:
        id: Identificador unico de la asociacion
        payroll_history_id: ID del historial de payroll
        task_id: ID de la task finalizada
        added_at: Fecha y hora en que se asocio la task
        added_by_user_id: ID del user que asocio la task (opcional, para auditoria)
    """
    
    id: uuid.UUID
    payroll_history_id: uuid.UUID
    task_id: uuid.UUID
    added_at: datetime
    added_by_user_id: Optional[str] = None  # Firebase UID del user que asocio
    
    def __post_init__(self):
        """Validaciones post-inicializacion."""
        if not self.payroll_history_id:
            raise ValueError("payroll_history_id es requerido")
        if not self.task_id:
            raise ValueError("task_id es requerido")
        if not self.added_at:
            raise ValueError("added_at es requerido")
    
    def __str__(self) -> str:
        return f"PayrollHistoryTask[{self.id}]: History={self.payroll_history_id}, Task={self.task_id}"
    
    def __repr__(self) -> str:
        return (f"PayrollHistoryTask(id={self.id}, "
                f"payroll_history_id={self.payroll_history_id}, "
                f"task_id={self.task_id}, "
                f"added_at={self.added_at})")
