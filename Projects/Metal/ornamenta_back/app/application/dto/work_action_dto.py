"""
DTOs para acciones de Work (quote, start, deliver).
"""
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class QuoteWorkResponseDTO(BaseModel):
    """DTO de respuesta al cotizar un work."""
    
    work_id: str
    work_name: str
    state: str  # Should be 'QUOTED'
    products_value: Decimal
    work_value: Decimal
    tax_percentage: float
    total_products: int
    quoted_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class StartWorkResponseDTO(BaseModel):
    """DTO de respuesta al iniciar un work."""
    
    work_id: str
    work_name: str
    state: str  # Should be 'IN_PROGRESS'
    total_tasks_generated: int
    started_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DeliverWorkResponseDTO(BaseModel):
    """DTO de respuesta al entregar un work."""
    
    work_id: str
    work_name: str
    state: str  # Should be 'DELIVERED'
    delivery_date: datetime
    final_value: Decimal
    completion_percentage: float
    
    model_config = ConfigDict(from_attributes=True)

