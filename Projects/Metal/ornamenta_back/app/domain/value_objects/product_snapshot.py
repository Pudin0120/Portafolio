"""
Product Snapshot Value Object.

Este value object almacena una "instantanea" completa del price y composicion
de un product en el momento de la quotation. Esto asegura que cambios posteriores
en los precios de materials no afecten cotizaciones ya realizadas.
"""
from dataclasses import dataclass
from typing import Dict, Any
from decimal import Decimal
import uuid

from app.domain.value_objects.money import Money


@dataclass(frozen=True)
class ProductSnapshot:
    """
    Value object inmutable que congela el estado de un product.
    
    Cuando un product se agrega a una quotation, se crea un snapshot
    que captura:
    - El price de venta (sale_price) congelado del product
    - El costo de produccion (purchase_price) congelado para analisis de margen
    - La composicion completa de materials (para auditoria)
    - Las dimensiones y properties del product
    
    Una vez creado, este snapshot no puede modificarse (frozen=True),
    garantizando la integridad de la quotation.
    
    Attributes:
        product_id: ID del product del cual se tomo el snapshot
        product_name: Nombre del product
        product_type: Tipo de product ("simple" o "composite")
        purchase_price: Costo de produccion congelado (purchase_price)
        sale_price: Price de venta congelado (sale_price)
        composition: Estructura completa de materials y properties
        dimensions: Dimensiones fisicas del product (si aplica)
        quantity_multiplier: Multiplicador de quantity usado en el calculo
    """
    
    product_id: uuid.UUID
    product_name: str
    product_type: str  # "simple" o "composite"
    purchase_price: Money
    sale_price: Money
    composition: Dict[str, Any]  # Composicion completa de materials
    dimensions: Dict[str, float]
    quantity_multiplier: Decimal
    
    @property
    def price(self) -> Money:
        """Legacy support for .price (returns sale_price)."""
        return self.sale_price

    def __str__(self) -> str:
        return f"Snapshot[{self.product_name}]: {self.sale_price} (Cost: {self.purchase_price})"
    
    def get_price(self) -> Money:
        """Retorna el price de venta congelado del product."""
        return self.sale_price
    
    def get_purchase_price(self) -> Money:
        """Retorna el costo de produccion congelado del product."""
        return self.purchase_price
    
    def get_composition(self) -> Dict[str, Any]:
        """Retorna la composicion congelada del product."""
        return self.composition.copy()
    
    def is_simple_product(self) -> bool:
        """Verifica si es un snapshot de un product simple."""
        return self.product_type == "simple"
    
    def is_composite_product(self) -> bool:
        """Verifica si es un snapshot de un product compuesto."""
        return self.product_type == "composite"

