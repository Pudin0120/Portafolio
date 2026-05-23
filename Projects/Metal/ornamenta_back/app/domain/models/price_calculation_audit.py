"""
Modelo de dominio para auditoria de calculos de price.

Este modelo registra todos los inputs y outputs de calculos de price de products,
permitiendo reproducir y auditar como se calculo el price en un momento dado.
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List
import uuid


@dataclass
class PriceCalculationAudit:
    """
    Registro de auditoria para calculo de price de product.
    
    Este objeto de dominio registra:
    - Que inputs se usaron (material, dimensiones, estrategia)
    - Que price se calculo
    - Cuando y por que se calculo
    - Quien lo solicito (si aplica)
    
    El registro es inmutable una vez creado y sirve para:
    1. Auditoria regulatoria (trazabilidad de precios)
    2. Debug de calculos incorrectos
    3. Historico de cambios de price
    4. Reproducir calculos pasados con los mismos inputs
    
    Attributes:
        calculation_id: Identificador unico del calculo
        product_id: ID del product cuyo price se calculo
        product_name: Nombre del product para referencia rapida
        calculated_at: Timestamp del calculo
        calculation_type: Tipo de calculo ("INITIAL_CREATION", "MATERIAL_PRICE_CHANGE", "MANUAL_RECALCULATION")
        
        # Inputs del calculo
        material_id: ID del material usado (si aplica)
        material_name: Nombre del material
        material_price_amount: Price del material al momento del calculo
        material_price_currency: Price currency del material
        measurement_strategy: Estrategia de measurement usada (SHEET, TUBE, etc.)
        dimensions: Dimensiones/properties del product
        computed_quantity: Quantity computada (area, volumen, etc.)
        quantity_unit: Unidad de la quantity computada
        
        # Output del calculo
        calculated_price_amount: Price calculado resultante
        calculated_price_currency: Price currency calculado
        
        # Contexto adicional
        triggered_by_event_id: ID del evento que disparo el calculo (si aplica)
        triggered_by_user_id: ID del user que causo el calculo (si aplica)
        notes: Notas adicionales sobre el calculo
    
    Example JSON (para docstrings):
        {
            "calculation_id": "calc-00001",
            "product_id": "prod-0001",
            "product_name": "Lamina cortada 1x2",
            "calculated_at": "2025-10-25T10:30:00Z",
            "calculation_type": "MATERIAL_PRICE_CHANGE",
            
            "material_id": "123e4567-e89b-12d3-a456-426614174000",
            "material_name": "Lamina acero cal 14",
            "material_price_amount": 105000.0,
            "material_price_currency": "COP",
            "measurement_strategy": "SHEET",
            "dimensions": {
                "width": {"value": 1.0, "unit": "m"},
                "length": {"value": 2.0, "unit": "m"}
            },
            "computed_quantity": {"value": 2.0, "unit": "m2"},
            "quantity_unit": "m2",
            
            "calculated_price_amount": 210000.0,
            "calculated_price_currency": "COP",
            
            "triggered_by_event_id": "550e8400-e29b-41d4-a716-446655440000",
            "triggered_by_user_id": "user-001",
            "notes": "Recalculo automatico por cambio de price de material"
        }
    """
    
    # Identificacion
    calculation_id: str
    tenant_id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    calculated_at: datetime
    calculation_type: str  # INITIAL_CREATION, MATERIAL_PRICE_CHANGE, MANUAL_RECALCULATION
    
    # Inputs del calculo
    material_id: Optional[uuid.UUID] = None
    material_name: Optional[str] = None
    material_price_amount: Optional[Decimal] = None
    material_price_currency: Optional[str] = None
    measurement_strategy: Optional[str] = None
    dimensions: Dict[str, Any] = field(default_factory=dict)
    computed_quantity: Optional[Decimal] = None
    quantity_unit: Optional[str] = None
    
    # Recipe breakdown for multi-material products
    recipe_details: List[Dict[str, Any]] = field(default_factory=list)
    
    # Output del calculo
    calculated_price_amount: Decimal = field(default=Decimal("0"))
    calculated_price_currency: str = "COP"
    
    # Contexto adicional
    triggered_by_event_id: Optional[uuid.UUID] = None
    triggered_by_user_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Validacion basica despues de inicializacion."""
        valid_types = [
            "INITIAL_CREATION", 
            "MATERIAL_PRICE_CHANGE", 
            "MATERIAL_PURCHASE_PRICE_CHANGE", 
            "MATERIAL_SALE_PRICE_CHANGE",
            "MANUAL_RECALCULATION"
        ]
        if self.calculation_type not in valid_types:
            raise ValueError(
                f"calculation_type debe ser uno de {valid_types}, "
                f"se recibio: {self.calculation_type}"
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el registro a diccionario para persistencia."""
        return {
            "calculation_id": self.calculation_id,
            "tenant_id": str(self.tenant_id),
            "product_id": str(self.product_id),
            "product_name": self.product_name,
            "calculated_at": self.calculated_at.isoformat(),
            "calculation_type": self.calculation_type,
            
            "material_id": str(self.material_id) if self.material_id else None,
            "material_name": self.material_name,
            "material_price_amount": float(self.material_price_amount) if self.material_price_amount else None,
            "material_price_currency": self.material_price_currency,
            "measurement_strategy": self.measurement_strategy,
            "dimensions": self.dimensions,
            "computed_quantity": float(self.computed_quantity) if self.computed_quantity else None,
            "quantity_unit": self.quantity_unit,
            "recipe_details": self.recipe_details,
            
            "calculated_price_amount": float(self.calculated_price_amount),
            "calculated_price_currency": self.calculated_price_currency,
            
            "triggered_by_event_id": str(self.triggered_by_event_id) if self.triggered_by_event_id else None,
            "triggered_by_user_id": str(self.triggered_by_user_id) if self.triggered_by_user_id else None,
            "notes": self.notes,
        }
    
    def __str__(self) -> str:
        """Representacion legible."""
        return (
            f"PriceCalculationAudit({self.calculation_id}): "
            f"{self.product_name} = {self.calculated_price_amount} {self.calculated_price_currency} "
            f"[{self.calculation_type}]"
        )


# INTEGRATION HOOK: La infraestructura debe proporcionar un repositorio o mecanismo
# de persistencia para estos registros de auditoria. Por ejemplo:
# - PriceCalculationAuditRepository.save(audit: PriceCalculationAudit)
# - O almacenamiento en memoria/cache si no hay persistencia implementada
# 
# La capa de aplicacion sera responsable de create estos registros cada vez que
# se calcule o recalcule el price de un product.

