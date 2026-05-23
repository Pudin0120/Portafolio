"""
In-memory implementation of PriceCalculationAuditRepository.

This is a simple in-memory implementation useful for:
- Development and testing
- Production if audit persistence is not required
- Temporary storage before batch writing to persistent storage
"""
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime
from collections import defaultdict

from app.domain.models.price_calculation_audit import PriceCalculationAudit
from app.domain.repositories.price_calculation_audit_repository import PriceCalculationAuditRepository


class InMemoryAuditRepository(PriceCalculationAuditRepository):
    """
    In-memory implementation of audit repository.
    
    This implementation stores audits in memory (lost on restart).
    Suitable for development or if full audit persistence is not needed.
    
    Features:
    - Fast lookups by calculation_id, product_id
    - Automatic indexing for common queries
    - Limited memory usage (configurable max size)
    
    Limitations:
    - Data lost on restart
    - Memory usage grows with audit count
    - Not suitable for distributed systems
    """
    
    def __init__(self, max_size: int = 10000):
        """
        Initialize the in-memory repository.
        
        Args:
            max_size: Maximum number of audit records to keep (oldest are removed)
        """
        self.max_size = max_size
        self._audits: Dict[str, PriceCalculationAudit] = {}  # calculation_id -> audit
        self._by_product: Dict[UUID, List[str]] = defaultdict(list)  # product_id -> [calculation_ids]
        self._chronological: List[str] = []  # Ordered list of calculation_ids (newest last)
    
    def save(self, audit: PriceCalculationAudit) -> PriceCalculationAudit:
        """
        Save an audit record.
        
        Args:
            audit: Audit record to save
        
        Returns:
            The saved audit record
        """
        # Remove oldest if at capacity
        if len(self._audits) >= self.max_size and audit.calculation_id not in self._audits:
            self._remove_oldest()
        
        # Store audit
        self._audits[audit.calculation_id] = audit
        
        # Index by product
        if audit.product_id not in self._by_product:
            self._by_product[audit.product_id] = []
        if audit.calculation_id not in self._by_product[audit.product_id]:
            self._by_product[audit.product_id].append(audit.calculation_id)
        
        # Add to chronological list
        if audit.calculation_id not in self._chronological:
            self._chronological.append(audit.calculation_id)
        
        return audit
    
    def get_by_id(self, calculation_id: str) -> Optional[PriceCalculationAudit]:
        """
        Get audit record by calculation ID.
        
        Args:
            calculation_id: Calculation ID to lookup
        
        Returns:
            Audit record or None if not found
        """
        return self._audits.get(calculation_id)
    
    def get_by_product_id(self, product_id: UUID) -> List[PriceCalculationAudit]:
        """
        Get all audit records for a specific product.
        
        Args:
            product_id: Product UUID
        
        Returns:
            List of audit records for this product (chronological order)
        """
        calculation_ids = self._by_product.get(product_id, [])
        return [self._audits[cid] for cid in calculation_ids if cid in self._audits]
    
    def get_latest_by_product_id(self, product_id: UUID) -> Optional[PriceCalculationAudit]:
        """
        Get the most recent audit record for a specific product.
        
        Args:
            product_id: Product UUID
        
        Returns:
            Audit record or None if not found
        """
        calculation_ids = self._by_product.get(product_id, [])
        if not calculation_ids:
            return None
        
        # In this implementation, newest are at the end of the list
        latest_id = calculation_ids[-1]
        return self._audits.get(latest_id)
    
    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[PriceCalculationAudit]:
        """
        Get audit records within a date range.
        
        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
        
        Returns:
            List of audit records in date range
        """
        result = []
        for audit in self._audits.values():
            if start_date <= audit.calculated_at <= end_date:
                result.append(audit)
        
        # Sort by date
        result.sort(key=lambda a: a.calculated_at)
        return result
    
    def get_recent(self, limit: int = 100) -> List[PriceCalculationAudit]:
        """
        Get most recent audit records.
        
        Args:
            limit: Maximum number of records to return
        
        Returns:
            List of most recent audit records (newest first)
        """
        # Get last N calculation_ids
        recent_ids = self._chronological[-limit:]
        
        # Reverse to get newest first
        recent_ids = list(reversed(recent_ids))
        
        return [self._audits[cid] for cid in recent_ids if cid in self._audits]
    
    def _remove_oldest(self) -> None:
        """Remove the oldest audit record to make space."""
        if not self._chronological:
            return
        
        # Get oldest calculation_id
        oldest_id = self._chronological.pop(0)
        
        # Remove from main storage
        audit = self._audits.pop(oldest_id, None)
        
        # Remove from product index
        if audit and audit.product_id in self._by_product:
            try:
                self._by_product[audit.product_id].remove(oldest_id)
            except ValueError:
                pass
    
    def clear(self) -> None:
        """Clear all audit records (useful for testing)."""
        self._audits.clear()
        self._by_product.clear()
        self._chronological.clear()
    
    def count(self) -> int:
        """Get total number of audit records stored."""
        return len(self._audits)


# Example usage:
"""
>>> audit_repo = InMemoryAuditRepository(max_size=1000)
>>> 
>>> # Save audit record
>>> audit = PriceCalculationAudit(...)
>>> audit_repo.save(audit)
>>> 
>>> # Query by product
>>> product_audits = audit_repo.get_by_product_id(product.id)
>>> 
>>> # Get recent audits
>>> recent = audit_repo.get_recent(limit=50)
>>> 
>>> # Query by date range
>>> from datetime import datetime, timedelta
>>> start = datetime.now() - timedelta(days=7)
>>> end = datetime.now()
>>> week_audits = audit_repo.get_by_date_range(start, end)
"""

