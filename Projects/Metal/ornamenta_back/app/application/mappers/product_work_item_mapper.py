"""
Mapper para ProductWorkItem (dominio  DTO).

Documentacion de respuesta para la API (Scalar/OpenAPI):
- Este mapper construye el ProductWorkItemDTO que devuelven los endpoints de Works.
- Los campos de price varian segun el estado del Work:
  - DRAFT: precios dinamicos (del catalogo), sin snapshot.
  - QUOTED/IN_PROGRESS/DELIVERED: precios congelados (snapshot), sin current_price.
- Siempre que haya price disponible, se incluyen:
  - effective_unit_price: Price unitario efectivo (MoneyDTO)
  - line_total_amount: Total de la linea = effective_unit_price.amount  quantity
"""
from typing import Optional
from decimal import Decimal

from app.domain.value_objects.product_work_item import ProductWorkItem
from app.domain.value_objects.product_snapshot import ProductSnapshot
from app.domain.models.product import ProductComponent
from app.application.dto.product_work_item_dto import (
    ProductWorkItemDTO,
    ProductSnapshotDTO,
    MoneyDTO
)


class ProductWorkItemMapper:
    """Mapper para convertir entre ProductWorkItem de dominio y DTOs.
    
    Campos relevantes del DTO expuesto por la API:
    - product_id (UUID)
    - work_id (UUID)
    - quantity (int)
    - execution_order (int)
    - state (str: PENDING, IN_PROGRESS, COMPLETED)
    - product_name (str | null)
    - product_type (str | null)  # "simple" | "composite"
    - snapshot (ProductSnapshotDTO | null)        # Solo en QUOTED+
    - current_price (MoneyDTO | null)             # Solo en DRAFT
    - effective_unit_price (MoneyDTO | null)      # Presente si hay price
    - line_total_amount (Decimal | null)          # Presente si hay price
    - task_ids (UUID[])

    Ejemplo en DRAFT (precios dinamicos):
    {
      "product_id": "223e4567-e89b-12d3-a456-426614174000",
      "work_id": "123e4567-e89b-12d3-a456-426614174000",
      "quantity": 2,
      "execution_order": 0,
      "state": "PENDING",
      "product_name": "Galon de pintura anticorrosiva 50.0L",
      "product_type": "simple",
      "snapshot": null,
      "current_price": { "amount": 100000, "currency": "COP" },
      "effective_unit_price": { "amount": 100000, "currency": "COP" },
      "line_total_amount": 200000,
      "task_ids": []
    }

    Ejemplo en QUOTED (precios congelados):
    {
      "product_id": "223e4567-e89b-12d3-a456-426614174000",
      "work_id": "123e4567-e89b-12d3-a456-426614174000",
      "quantity": 2,
      "execution_order": 0,
      "state": "PENDING",
      "product_name": "Galon de pintura anticorrosiva 50.0L",
      "product_type": "simple",
      "current_price": null,
      "snapshot": {
        "product_id": "223e4567-e89b-12d3-a456-426614174000",
        "product_name": "Galon de pintura anticorrosiva 50.0L",
        "product_type": "simple",
        "price_amount": 100000,
        "price_currency": "COP",
        "composition": {},
        "dimensions": {},
        "quantity_multiplier": 1
      },
      "effective_unit_price": { "amount": 100000, "currency": "COP" },
      "line_total_amount": 200000,
      "task_ids": []
    }
    """

    @staticmethod
    def to_dto(
        item: ProductWorkItem,
        product: Optional[ProductComponent] = None
    ) -> ProductWorkItemDTO:
        """
        Convierte un ProductWorkItem de dominio a ProductWorkItemDTO.
        
        Reglas de precios en la respuesta de la API:
        - Si el item tiene snapshot (QUOTED+):
           current_price = null
           effective_unit_price = snapshot.price
           line_total_amount = snapshot.price.amount  quantity
        - Si NO tiene snapshot (DRAFT) y hay product:
           current_price = product.get_total_price()
           effective_unit_price = current_price
           line_total_amount = current_price.amount  quantity
        - Si no se puede determinar un price, los campos de price quedan en null.
        
        Returns:
            ProductWorkItemDTO con los campos normalizados para el frontend.
        """
        snapshot_dto = None
        if item.snapshot:
            snapshot_dto = ProductWorkItemMapper.snapshot_to_dto(item.snapshot)
        
        current_price_dto = None
        effective_unit_price_dto = None
        line_total_amount = None

        # Determinar price unitario efectivo
        if item.snapshot:
            # Price congelado
            unit_price = item.snapshot.sale_price
            effective_unit_price_dto = MoneyDTO(amount=unit_price.amount, currency=unit_price.currency)
            line_total_amount = unit_price.amount * Decimal(str(item.quantity))
        else:
            # Price dinamico (si tenemos el product en el registry)
            if product:
                try:
                    current_price = product.get_total_price()
                    current_price_dto = MoneyDTO(
                        amount=current_price.amount,
                        currency=current_price.currency
                    )
                    # En DRAFT, el unitario efectivo es el price actual
                    effective_unit_price_dto = current_price_dto
                    line_total_amount = current_price.amount * Decimal(str(item.quantity))
                except ValueError:
                    # Si el product no tiene price, se omite
                    pass
        
        # Get product info if available
        product_name = None
        product_type = None
        if product:
            product_name = product.name
            product_type = "composite" if product.is_composite() else "simple"
        elif item.snapshot:
            product_name = item.snapshot.product_name
            product_type = item.snapshot.product_type
        
        return ProductWorkItemDTO(
            product_id=item.product_id,
            work_id=item.work_id,
            quantity=item.quantity,
            execution_order=item.execution_order,
            state=item.state.value,
            snapshot=snapshot_dto,
            current_price=current_price_dto,
            task_ids=item.task_ids,
            product_name=product_name,
            product_type=product_type,
            effective_unit_price=effective_unit_price_dto,
            line_total_amount=line_total_amount,
        )

    @staticmethod
    def snapshot_to_dto(snapshot: ProductSnapshot) -> ProductSnapshotDTO:
        """
        Convierte un ProductSnapshot de dominio a ProductSnapshotDTO.
        """
        return ProductSnapshotDTO(
            product_id=snapshot.product_id,
            product_name=snapshot.product_name,
            product_type=snapshot.product_type,
            purchase_price_amount=snapshot.purchase_price.amount,
            purchase_price_currency=snapshot.purchase_price.currency,
            sale_price_amount=snapshot.sale_price.amount,
            sale_price_currency=snapshot.sale_price.currency,
            price_amount=snapshot.sale_price.amount,  # Legacy
            price_currency=snapshot.sale_price.currency,  # Legacy
            composition=snapshot.composition,
            dimensions=snapshot.dimensions,
            quantity_multiplier=snapshot.quantity_multiplier
        )

