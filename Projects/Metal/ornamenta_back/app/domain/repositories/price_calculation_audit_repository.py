"""
Repository interface for PriceCalculationAudit entity.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.domain.models.price_calculation_audit import PriceCalculationAudit


class PriceCalculationAuditRepository(ABC):
    """
    Abstract repository for managing PriceCalculationAudit persistence.
    """
    
    @abstractmethod
    def save(self, audit: PriceCalculationAudit) -> PriceCalculationAudit:
        """Save an audit record."""
        pass
    
    @abstractmethod
    def get_by_id(self, calculation_id: str) -> Optional[PriceCalculationAudit]:
        """Get audit record by calculation ID."""
        pass
    
    @abstractmethod
    def get_by_product_id(self, product_id: UUID) -> List[PriceCalculationAudit]:
        """Get all audit records for a specific product."""
        pass
    
    @abstractmethod
    def get_latest_by_product_id(self, product_id: UUID) -> Optional[PriceCalculationAudit]:
        """Get the most recent audit record for a specific product."""
        pass
    
    @abstractmethod
    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[PriceCalculationAudit]:
        """Get audit records within a date range."""
        pass
    
    @abstractmethod
    def get_recent(self, limit: int = 100) -> List[PriceCalculationAudit]:
        """Get most recent audit records."""
        pass

