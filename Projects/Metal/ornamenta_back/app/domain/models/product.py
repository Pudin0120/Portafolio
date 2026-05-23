"""
Product domain models using Composite Pattern.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import uuid
from decimal import Decimal
from datetime import datetime

from app.domain.models.material import Material
from app.domain.models.material_type import MaterialType
from app.domain.models.price_calculation_audit import PriceCalculationAudit
from app.domain.value_objects.money import Money
from app.domain.value_objects.dimension_rule import ComponentRelationship
from app.domain.units import ureg


@dataclass
class ProductComponent(ABC):
    """
    Abstract base component for the Composite Pattern.
    """
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    purchase_price: Optional[Money] = None  # Cost to produce (calculated or manual)
    sale_price: Optional[Money] = None      # Price for the customer
    image_url: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    tenant_id: Optional[uuid.UUID] = field(default=None)
    last_calculation_audit: Optional[PriceCalculationAudit] = field(default=None)
    
    @abstractmethod
    def get_total_purchase_price(self) -> Optional[Money]:
        """Calculate total cost (purchase price)."""
        pass

    @abstractmethod
    def get_total_sale_price(self) -> Optional[Money]:
        """Calculate total sale price."""
        pass
    
    def get_total_price(self) -> Optional[Money]:
        """Legacy support."""
        return self.get_total_sale_price()

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.now()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None

    @abstractmethod
    def get_material_composition(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def is_composite(self) -> bool:
        pass
    
    @abstractmethod
    def get_all_materials(self) -> Dict[uuid.UUID, Dict[str, Any]]:
        pass
    
    @abstractmethod
    def calculate_total_area(self) -> float:
        pass
    
    @property
    @abstractmethod
    def is_complete(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_template(self) -> bool:
        pass

    @abstractmethod
    def get_required_material_types(self) -> Dict[uuid.UUID, str]:
        pass
    
    def __str__(self) -> str:
        return f"{self.name} - {self.get_total_price()}"


@dataclass
class ProductMaterial:
    """
    Relacion entre un product simple y un material que lo compone.
    Permite definir que quantity de un material especifico (vidrio, aluminio, mano de obra)
    consume este product.
    """
    material: Material
    quantity: Decimal = Decimal("1.0")
    dimensions: Dict[str, Any] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def get_purchase_price(self) -> Money:
        return self.material.get_price().multiply(self.quantity)
    
    def get_sale_price(self) -> Money:
        return self.material.sale_price.multiply(self.quantity)


@dataclass
class SimpleProduct(ProductComponent):
    materials: List[ProductMaterial] = field(default_factory=list)
    material_type: Optional[MaterialType] = field(default=None) # Keep for template requirements
    dimensions: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        # We still might want a primary material type for classification
        if not self.material_type and self.materials:
            self.material_type = self.materials[0].material.material_type
    
    @property
    def is_template(self) -> bool:
        # A template is a product that has material types required but no materials assigned yet
        return len(self.materials) == 0 and self.material_type is not None

    @property
    def is_complete(self) -> bool:
        if self.is_template:
            return False
        return len(self.materials) > 0 or (self.purchase_price is not None and self.sale_price is not None)
    
    def get_total_purchase_price(self) -> Optional[Money]:
        if self.is_template: return None
        # Priority: Hardcoded price > Recipe sum
        if self.purchase_price is not None and self.purchase_price.amount > 0: 
            return self.purchase_price
        
        if not self.materials: return Money(amount=Decimal("0"))
        
        total = Money(amount=Decimal("0"))
        for pm in self.materials:
            total = total + pm.get_purchase_price()
            
        return total

    def get_total_sale_price(self) -> Optional[Money]:
        if self.is_template: return None
        # Priority: Hardcoded price > Recipe sum
        if self.sale_price is not None and self.sale_price.amount > 0: 
            return self.sale_price
            
        if not self.materials: return Money(amount=Decimal("0"))
        
        total = Money(amount=Decimal("0"))
        for pm in self.materials:
            total = total + pm.get_sale_price()
            
        return total
    
    def get_material_composition(self) -> Dict[str, Any]:
        if self.is_template:
             return {
                "is_template": True,
                "required_material_type": self.material_type.name if self.material_type else "Unknown",
                "dimensions": self.dimensions,
                "properties": self.properties,
            }
        
        return {
            "materials": [
                {
                    "material_id": str(pm.material.id),
                    "material_name": pm.material.full_name,
                    "material_type": pm.material.material_type.name,
                    "measurement_type": pm.material.get_measurement_type(),
                    "quantity": float(pm.quantity),
                    "dimensions": pm.dimensions,
                    "purchase_price": str(pm.get_purchase_price()),
                    "sale_price": str(pm.get_sale_price()),
                } for pm in self.materials
            ],
            "dimensions": self.dimensions,
            "properties": self.properties,
        }
    
    def is_composite(self) -> bool:
        return False
    
    def get_all_materials(self) -> Dict[uuid.UUID, Dict[str, Any]]:
        materials_dict = {}
        for pm in self.materials:
            materials_dict[pm.material.id] = {
                "material_name": pm.material.full_name,
                "material_type": pm.material.material_type.name,
                "measurement_type": pm.material.get_measurement_type(),
                "total_usage": float(pm.quantity)
            }
        return materials_dict
    
    def calculate_total_area(self) -> float:
        if 'area' in self.dimensions:
            return self.dimensions['area']
        elif 'width' in self.dimensions and 'height' in self.dimensions:
            return self.dimensions['width'] * self.dimensions['height']
        return 0.0

    def get_required_material_types(self) -> Dict[uuid.UUID, str]:
        if self.is_template and self.material_type:
            return {self.id: self.material_type.name}
        return {}


@dataclass
class ComponentQuantity:
    """
    Represents a component within a composite product.
    Supports dynamic calculation based on parent dimensions.
    """
    component: ProductComponent
    
    # Base quantity (for template/dynamic mode)
    base_quantity: int = 1
    
    # Relationship with parent (how to calculate dimensions and quantity)
    relationship: Optional[ComponentRelationship] = None
    
    # --- SNAPSHOT (frozen for Work Orders / Quotations) ---
    snapshot_quantity: Optional[Decimal] = None
    snapshot_dimensions: Optional[Dict[str, float]] = None
    snapshot_purchase_price: Optional[Money] = None
    snapshot_sale_price: Optional[Money] = None
    snapshot_created_at: Optional[datetime] = None
    
    @property
    def is_snapshot(self) -> bool:
        """Indicates if this component is in snapshot mode."""
        return self.snapshot_created_at is not None
    
    @property
    def quantity(self) -> int:
        """Legacy property for backward compatibility."""
        return self.base_quantity
    
    def calculate_quantity(self, parent_dimensions: Dict[str, float]) -> Decimal:
        """
        Calculate real quantity based on parent dimensions.
        If snapshot exists, returns snapshot.
        """
        if self.is_snapshot and self.snapshot_quantity is not None:
            return self.snapshot_quantity
        
        if not self.relationship:
            return Decimal(str(self.base_quantity))
        
        return self.relationship.calculate_quantity(parent_dimensions)
    
    def calculate_dimensions(self, parent_dimensions: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate component dimensions based on rules.
        """
        if self.is_snapshot:
            return self.snapshot_dimensions or {}
        
        if not self.relationship:
            return {}
        
        return self.relationship.calculate_dimensions(parent_dimensions)
    
    def create_snapshot(self, parent_dimensions: Dict[str, float]) -> None:
        """
        Freezes current component state (for quotations/orders).
        """
        self.snapshot_quantity = self.calculate_quantity(parent_dimensions)
        self.snapshot_dimensions = self.calculate_dimensions(parent_dimensions)
        
        # Ensure we have valid prices before creating snapshot
        purchase = self.get_subtotal_purchase_price(parent_dimensions)
        sale = self.get_subtotal_sale_price(parent_dimensions)
        
        self.snapshot_purchase_price = purchase
        self.snapshot_sale_price = sale
        self.snapshot_created_at = datetime.now()
    
    def clear_snapshot(self) -> None:
        """Clears snapshot to return to dynamic mode."""
        self.snapshot_quantity = None
        self.snapshot_dimensions = None
        self.snapshot_purchase_price = None
        self.snapshot_sale_price = None
        self.snapshot_created_at = None
    
    def get_subtotal_purchase_price(self, parent_dimensions: Optional[Dict[str, float]] = None) -> Optional[Money]:
        """Calculate subtotal purchase price."""
        if self.is_snapshot:
            return self.snapshot_purchase_price
        
        price = self.component.get_total_purchase_price()
        if price is None:
            return None
        
        if parent_dimensions is None:
            # Legacy mode: use base_quantity
            return price.multiply(Decimal(str(self.base_quantity)))
        
        # Dynamic mode: calculate quantity based on dimensions
        quantity = self.calculate_quantity(parent_dimensions)
        return price.multiply(quantity)

    def get_subtotal_sale_price(self, parent_dimensions: Optional[Dict[str, float]] = None) -> Optional[Money]:
        """Calculate subtotal sale price."""
        if self.is_snapshot:
            return self.snapshot_sale_price
        
        price = self.component.get_total_sale_price()
        if price is None:
            return None
        
        if parent_dimensions is None:
            # Legacy mode: use base_quantity
            return price.multiply(Decimal(str(self.base_quantity)))
        
        # Dynamic mode: calculate quantity based on dimensions
        quantity = self.calculate_quantity(parent_dimensions)
        return price.multiply(quantity)
    
    def get_subtotal_price(self, parent_dimensions: Optional[Dict[str, float]] = None) -> Optional[Money]:
        """Legacy support."""
        return self.get_subtotal_sale_price(parent_dimensions)


@dataclass
class CompositeProduct(ProductComponent):
    """
    Composite product with dynamic dimensional calculation support.
    """
    components: List[ComponentQuantity] = field(default_factory=list)
    
    # Dimensions of the composite product (e.g., Door 2m x 1m)
    dimensions: Dict[str, float] = field(default_factory=dict)
    
    # Snapshot mode for entire composition
    composition_snapshot_created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.components is None:
            self.components = []
    
    @property
    def is_snapshot_mode(self) -> bool:
        """Indicates if the entire product is in snapshot mode."""
        return self.composition_snapshot_created_at is not None

    def add_component(
        self, 
        component: ProductComponent, 
        quantity: int = 1,
        relationship: Optional[ComponentRelationship] = None
    ) -> None:
        """Adds a component with its dimensional relationship."""
        cq = ComponentQuantity(
            component=component,
            base_quantity=quantity,
            relationship=relationship
        )
        self.components.append(cq)
    
    def remove_component(self, component: ProductComponent) -> None:
        self.components = [cq for cq in self.components if cq.component.id != component.id]
    
    def get_components(self) -> List[ComponentQuantity]:
        return self.components.copy()
    
    @property
    def is_complete(self) -> bool:
        if not self.components: return False
        return all(cq.component.is_complete for cq in self.components)
    
    def get_total_purchase_price(self) -> Optional[Money]:
        """Calculate total price considering dynamic or snapshot mode."""
        if self.purchase_price is not None and self.purchase_price.amount > 0:
            return self.purchase_price
        
        if not self.components:
            return Money(amount=Decimal("0"))
        
        total = Money(amount=Decimal("0"))
        for cq in self.components:
            if cq.is_snapshot:
                sub = cq.snapshot_purchase_price
            else:
                sub = cq.get_subtotal_purchase_price(self.dimensions)
            
            if sub is None:
                return None
            total = total + sub
        
        return total

    def get_total_sale_price(self) -> Optional[Money]:
        """Calculate sale price considering dynamic or snapshot mode."""
        if self.sale_price is not None and self.sale_price.amount > 0:
            return self.sale_price
        
        if not self.components:
            return Money(amount=Decimal("0"))
        
        total = Money(amount=Decimal("0"))
        for cq in self.components:
            if cq.is_snapshot:
                sub = cq.snapshot_sale_price
            else:
                sub = cq.get_subtotal_sale_price(self.dimensions)
            
            if sub is None:
                return None
            total = total + sub
        
        return total
    
    def create_composition_snapshot(self) -> None:
        """
        Freezes ENTIRE composition of the product.
        Useful for quotations going to the client.
        """
        for cq in self.components:
            cq.create_snapshot(self.dimensions)
        
        self.composition_snapshot_created_at = datetime.now()
        
        # Create audit trail
        total_sale = self.get_total_sale_price()
        self.last_calculation_audit = PriceCalculationAudit(
            calculation_id=f"calc-{uuid.uuid4()}",
            tenant_id=self.tenant_id or uuid.uuid4(),
            product_id=self.id,
            product_name=self.name,
            calculated_at=datetime.now(),
            calculation_type="MANUAL_RECALCULATION",
            dimensions=self.dimensions,
            calculated_price_amount=total_sale.amount if total_sale else Decimal("0"),
            calculated_price_currency="COP",
            notes="Snapshot created for composite product composition"
        )
    
    def clear_composition_snapshot(self) -> None:
        """
        Clears snapshot to return to dynamic mode.
        Useful when client requests changes in quotation.
        """
        for cq in self.components:
            cq.clear_snapshot()
        
        self.composition_snapshot_created_at = None
    
    def recalculate_with_new_dimensions(self, new_dimensions: Dict[str, float]) -> None:
        """
        Updates dimensions and recalculates everything.
        If in snapshot, clears it automatically.
        """
        self.clear_composition_snapshot()
        self.dimensions = new_dimensions
        
        # Next get_total_price() will calculate dynamically
    
    def get_material_composition(self) -> Dict[str, Any]:
        composition = {
            "composite": True, 
            "total_components": len(self.components), 
            "components": [],
            "dimensions": self.dimensions,
            "is_snapshot_mode": self.is_snapshot_mode,
            "properties": {k: v for k, v in self.properties.items() if k != "composition_breakdown"}
        }
        for cq in self.components:
            child = cq.component.get_material_composition()
            
            # Get calculated or snapshot values
            if cq.is_snapshot:
                calc_quantity = cq.snapshot_quantity
                calc_dimensions = cq.snapshot_dimensions
            else:
                calc_quantity = cq.calculate_quantity(self.dimensions)
                calc_dimensions = cq.calculate_dimensions(self.dimensions)
            
            composition["components"].append({
                "product_id": str(cq.component.id),
                "product_name": cq.component.name,
                "base_quantity": cq.base_quantity,
                "calculated_quantity": float(calc_quantity) if calc_quantity else None,
                "calculated_dimensions": calc_dimensions,
                "is_snapshot": cq.is_snapshot,
                "composition": child,
                "purchase_price": str(cq.get_subtotal_purchase_price(self.dimensions)) if cq.get_subtotal_purchase_price(self.dimensions) else "N/A",
                "sale_price": str(cq.get_subtotal_sale_price(self.dimensions)) if cq.get_subtotal_sale_price(self.dimensions) else "N/A"
            })
        return composition
    
    def is_composite(self) -> bool:
        return True

    @property
    def is_template(self) -> bool:
        if not self.components: return False
        return any(comp.component.is_template for comp in self.components)
    
    def get_all_materials(self) -> Dict[uuid.UUID, Dict[str, Any]]:
        materials = {}
        for cq in self.components:
            child = cq.component.get_all_materials()
            quantity = cq.calculate_quantity(self.dimensions)
            
            for mat_id, mat_info in child.items():
                usage = mat_info["total_usage"] * float(quantity)
                if mat_id in materials:
                    materials[mat_id]["total_usage"] += usage
                else:
                    materials[mat_id] = mat_info.copy()
                    materials[mat_id]["total_usage"] = usage
        return materials
    
    def calculate_total_area(self) -> float:
        total = 0.0
        for cq in self.components:
            quantity = cq.calculate_quantity(self.dimensions)
            total += cq.component.calculate_total_area() * float(quantity)
        return total

    def get_required_material_types(self) -> Dict[uuid.UUID, str]:
        reqs = {}
        for cq in self.components:
            reqs.update(cq.component.get_required_material_types())
        return reqs
