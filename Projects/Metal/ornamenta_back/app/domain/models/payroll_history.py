"""
Domain model for PayrollHistory entity.

PayrollHistory represents the historical record of payroll calculations
including work values, labor costs, and period information.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import date
from decimal import Decimal
import uuid

from app.domain.value_objects.money import Money


@dataclass
class PayrollHistory:
    """
    Modelo de dominio para historial de payroll.
    
    Representa el registro historico de calculos de payroll incluyendo
    valores de work, costos laborales e information de periodos.
    
    Attributes:
        id: Identificador unico del historial (UUID)
        identification_number: Number de identificacion del empleado
        payroll_id: ID de la payroll asociada
        security_id: ID de seguridad/seguridad social
        works_value_amount: Valor de las obras/works realizados
        init_date: Fecha de inicio del periodo
        end_date: Fecha de fin del periodo
    """
    
    identification_number: str
    payroll_id: uuid.UUID
    security_id: str
    works_value_amount: Money
    init_date: date
    end_date: date
    id: Optional[uuid.UUID] = None  # Opcional para cuando se crea nuevo
    
    def calculate_period_days(self) -> int:
        """
        Calcula el number de dias del periodo.
        
        Returns:
            Number de dias entre init_date y end_date (inclusive)
        """
        return (self.end_date - self.init_date).days + 1
    
    @property
    def total_value(self) -> Money:
        """
        Calcula el valor total (obras).
        
        Returns:
            Valor de works_value_amount
        """
        return self.works_value_amount

    @property
    def daily_average(self) -> Money:
        """Calcula el promedio diario."""
        days = self.calculate_period_days()
        if days <= 0:
            return Money(amount=Decimal("0"))
        return Money(amount=self.works_value_amount.amount / Decimal(str(days)))

    def is_valid_period(self) -> bool:
        """Verifica si el periodo es valid."""
        return self.end_date >= self.init_date

    def get_period_description(self) -> str:
        """Retorna description del periodo."""
        days = self.calculate_period_days()
        return f"{self.init_date.strftime('%d/%m/%Y')} - {self.end_date.strftime('%d/%m/%Y')} ({days} dias)"
