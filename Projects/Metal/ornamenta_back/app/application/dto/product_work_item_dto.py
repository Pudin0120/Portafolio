"""
DTOs para ProductWorkItem y ProductSnapshot.
"""
from typing import Optional, Dict, Any, List
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class MoneyDTO(BaseModel):
    """DTO para el value object Money."""
    amount: Decimal
    currency: str

    model_config = ConfigDict(from_attributes=True)


class ProductSnapshotDTO(BaseModel):
    """DTO para snapshot de product congelado."""
    
    product_id: UUID
    product_name: str
    product_type: str  # 'simple' or 'composite'
    purchase_price_amount: Decimal
    purchase_price_currency: str
    sale_price_amount: Decimal
    sale_price_currency: str
    # Legacy support
    price_amount: Optional[Decimal] = None
    price_currency: Optional[str] = None
    composition: Dict[str, Any]
    dimensions: Dict[str, Any]
    quantity_multiplier: Decimal
    
    model_config = ConfigDict(from_attributes=True)


class ProductWorkItemDTO(BaseModel):
    """DTO para product dentro de un work.
    
    Campos de price:
    - current_price: Solo en DRAFT (price actual del catalogo)
    - snapshot: Solo en QUOTED+ (price congelado)
    - effective_unit_price: Siempre presente si hay price (normalizado)
    - line_total_amount: effective_unit_price.amount * quantity
    """
    
    product_id: UUID
    work_id: UUID
    quantity: int
    execution_order: int
    state: str  # PENDING, IN_PROGRESS, COMPLETED
    snapshot: Optional[ProductSnapshotDTO] = None
    current_price: Optional[MoneyDTO] = None  # Price actual si no hay snapshot
    task_ids: List[UUID] = Field(default_factory=list)
    
    # Informacion del product (no congelada, para referencia)
    product_name: Optional[str] = None
    product_type: Optional[str] = None

    # Price normalizado para frontend (siempre el unitario efectivo)
    effective_unit_price: Optional[MoneyDTO] = None
    # Total por renglon (unitario * quantity) - se serializa como number
    line_total_amount: Optional[Decimal] = Field(default=None, json_schema_extra={"type": "number"})
    
    model_config = ConfigDict(from_attributes=True)


class AddProductToWorkDTO(BaseModel):
    """DTO para agregar product a un work."""
    
    product_id: UUID
    # Quantity (> 0). Validado en dominio/UC. Se evita usar gt para compatibilidad de linters.
    quantity: int
    # Orden de ejecucion (>= 0 o None). Validado en dominio/UC.
    execution_order: Optional[int] = None
