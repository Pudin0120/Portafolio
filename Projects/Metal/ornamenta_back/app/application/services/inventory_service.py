import uuid
from decimal import Decimal
from typing import Optional, List, Dict
from datetime import datetime

from app.domain.models.material import Material
from app.domain.models.product import ProductComponent
from app.domain.models.inventory_movement import InventoryMovement
from app.domain.models.inventory_level import InventoryLevel
from app.domain.events.material_events import MaterialPriceChanged
from app.domain.observers.material_price_observer import MaterialPriceSubject
from app.domain.repositories.material_repository import MaterialRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.value_objects.money import Money

class InventoryService:
    """
    Application service that orchestrates inventory logic.
    Ensures consistency between movements (Kardex), levels (Stock), and pricing history.
    """
    
    def __init__(
        self, 
        inventory_repo: InventoryRepository, 
        material_repo: MaterialRepository,
        price_subject: Optional[MaterialPriceSubject] = None
    ):
        self.inventory_repo = inventory_repo
        self.material_repo = material_repo
        self.price_subject = price_subject

    def initialize_stock(self, material_id: uuid.UUID, tenant_id: uuid.UUID, warehouse_id: Optional[uuid.UUID] = None) -> InventoryLevel:
        """
        Initializes the inventory level for a new material.
        If it already exists, it returns the existing one.
        """
        level = self.inventory_repo.get_level(material_id, tenant_id, warehouse_id)
        if not level:
            level = InventoryLevel(
                id=uuid.uuid4(),
                material_id=material_id,
                tenant_id=tenant_id,
                quantity=Decimal("0"),
                warehouse_id=warehouse_id
            )
            self.inventory_repo.save_level(level)
            
        return level

    def register_movement(
        self,
        material_id: uuid.UUID,
        quantity: Decimal,
        movement_type: str,
        tenant_id: uuid.UUID,
        reference_id: Optional[uuid.UUID] = None,
        batch_number: Optional[str] = None,
        reason: Optional[str] = None,
        warehouse_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
        created_at: Optional[datetime] = None
    ) -> InventoryMovement:
        """
        Registers a new inventory movement and updates the corresponding level.
        Atomic operation (handled by middleware transaction).
        """
        # 1. Create the movement entity
        movement = InventoryMovement(
            id=uuid.uuid4(),
            material_id=material_id,
            quantity=quantity,
            type=movement_type,
            tenant_id=tenant_id,
            reference_id=reference_id,
            batch_number=batch_number,
            reason=reason,
            created_by=user_id,
            created_at=created_at or datetime.now()
        )

        # 2. Update or Create Inventory Level
        level = self.inventory_repo.get_level(material_id, tenant_id, warehouse_id)
        
        if not level:
            level = InventoryLevel(
                id=uuid.uuid4(),
                material_id=material_id,
                tenant_id=tenant_id,
                quantity=Decimal("0"),
                warehouse_id=warehouse_id
            )

        # 3. Apply the change to the level
        level.update_quantity(quantity)

        # 4. Persist both
        self.inventory_repo.save_movement(movement)
        self.inventory_repo.save_level(level)

        return movement

    def consume_product_materials(
        self,
        product: ProductComponent,
        quantity: Decimal,
        tenant_id: uuid.UUID,
        reference_id: Optional[uuid.UUID] = None,
        reason: Optional[str] = None,
        warehouse_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
        created_at: Optional[datetime] = None,
    ) -> List[InventoryMovement]:
        """Consumes the materials required by a product."""
        movements: List[InventoryMovement] = []
        material_usage = product.get_all_materials()

        for material_id, info in material_usage.items():
            usage_per_unit = Decimal(str(info.get("total_usage", 0)))
            total_usage = usage_per_unit * quantity
            if total_usage == 0:
                continue

            movement = self.register_movement(
                material_id=material_id,
                quantity=total_usage * Decimal("-1"),
                movement_type="PRODUCTION_CONSUMPTION",
                tenant_id=tenant_id,
                reference_id=reference_id,
                reason=reason,
                warehouse_id=warehouse_id,
                user_id=user_id,
                created_at=created_at,
            )
            movements.append(movement)

        return movements

    def validate_work_materials_sufficient(
        self,
        products: Dict[uuid.UUID, ProductComponent],
        work_product_items: List[tuple[uuid.UUID, Decimal]],
        tenant_id: uuid.UUID,
        warehouse_id: Optional[uuid.UUID] = None,
    ) -> Dict[uuid.UUID, Decimal]:
        """Validates that there is enough stock for all materials required by a work."""
        required_materials: Dict[uuid.UUID, Decimal] = {}

        for product_id, quantity in work_product_items:
            product = products.get(product_id)
            if not product:
                raise ValueError(f"Product {product_id} not found")

            for material_id, info in product.get_all_materials().items():
                usage_per_unit = Decimal(str(info.get("total_usage", 0)))
                needed = usage_per_unit * quantity
                required_materials[material_id] = required_materials.get(material_id, Decimal("0")) + needed

        for material_id, needed_quantity in required_materials.items():
            level = self.inventory_repo.get_level(material_id, tenant_id, warehouse_id)
            available_quantity = level.quantity if level else Decimal("0")

            if available_quantity < needed_quantity:
                material_name = None
                for product_id, _ in work_product_items:
                    product = products.get(product_id)
                    if not product:
                        continue
                    materials = product.get_all_materials()
                    if material_id in materials:
                        material_name = materials[material_id].get("material_name")
                        break

                display_name = material_name or str(material_id)
                raise ValueError(
                    f"Insufficient stock for material {display_name}: required {needed_quantity}, available {available_quantity}"
                )

        return required_materials

    def consume_work_materials(
        self,
        products: Dict[uuid.UUID, ProductComponent],
        work_product_items: List[tuple[uuid.UUID, Decimal]],
        tenant_id: uuid.UUID,
        reference_id: Optional[uuid.UUID] = None,
        reason: Optional[str] = None,
        warehouse_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
        created_at: Optional[datetime] = None,
    ) -> List[InventoryMovement]:
        """Consumes all materials required by a confirmed work/order."""
        movements: List[InventoryMovement] = []

        for product_id, quantity in work_product_items:
            product = products.get(product_id)
            if not product:
                continue

            movements.extend(
                self.consume_product_materials(
                    product=product,
                    quantity=quantity,
                    tenant_id=tenant_id,
                    reference_id=reference_id,
                    reason=reason,
                    warehouse_id=warehouse_id,
                    user_id=user_id,
                    created_at=created_at,
                )
            )

        return movements

    def update_material_prices(
        self, 
        material_id: uuid.UUID, 
        user_id: uuid.UUID,
        tenant_id: Optional[uuid.UUID] = None,
        purchase_price: Optional[Decimal] = None,
        sale_price: Optional[Decimal] = None,
        user_name: str = "System",
        reason: str = "Price update"
    ) -> Material:
        """
        Updates material prices and notifies observers (products) if purchase price changes.
        """
        material = self.material_repo.get_by_id(material_id, tenant_id=tenant_id)
        if not material:
            raise ValueError("Material not found")

        # Track changes for notification
        changes = []

        if purchase_price is not None and material.purchase_price.amount != purchase_price:
            old_price = material.purchase_price.amount
            material.purchase_price = Money(amount=purchase_price)
            changes.append(("PURCHASE", old_price, purchase_price))

        if sale_price is not None and material.sale_price.amount != sale_price:
            old_price = material.sale_price.amount
            material.sale_price = Money(amount=sale_price)
            changes.append(("SALE", old_price, sale_price))

        if not changes:
            return material

        self.material_repo.save(material)

        # Notify observers (like ProductPriceUpdater)
        if self.price_subject:
            for price_type, old_val, new_val in changes:
                event = MaterialPriceChanged(
                    event_id=uuid.uuid4(),
                    occurred_at=datetime.now(),
                    aggregate_id=material.id,
                    material_id=material.id,
                    material_name=material.full_name,
                    old_price_amount=old_val,
                    new_price_amount=new_val,
                    currency=material.purchase_price.currency,
                    changed_by_user_id=user_id,
                    changed_by_user_name=user_name,
                    price_type=price_type,
                    reason=reason
                )
                self.price_subject.notify(event)

        return material

    def delete_material(self, material_id: uuid.UUID, tenant_id: uuid.UUID):
        """Soft delete material only if stock is zero."""
        material = self.material_repo.get_by_id(material_id, tenant_id=tenant_id)
        if not material:
            raise ValueError("Material not found")
            
        level = self.inventory_repo.get_level(material_id, tenant_id)
        if level and level.quantity != 0:
            raise ValueError(f"Cannot delete material with active stock ({level.quantity})")
            
        material.soft_delete()
        self.material_repo.save(material)

    def restore_material(self, material_id: uuid.UUID, tenant_id: Optional[uuid.UUID] = None):
        """Restores a soft-deleted material."""
        material = self.material_repo.get_by_id(material_id, tenant_id=tenant_id)
        if not material:
            raise ValueError("Material not found")
        
        material.restore()
        self.material_repo.save(material)
