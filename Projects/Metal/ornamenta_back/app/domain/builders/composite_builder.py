"""
Builder for CompositeProduct and Template Instantiation.

This builder handles the lifecycle of complex products:
1. Creation from scratch.
2. Instantiation from a Template (deep copy).
3. Structural modification (add/remove components).
4. Material Injection (assigning concrete materials to template placeholders).
"""
import copy
import uuid
from typing import Dict, Optional, List

from app.domain.models.product import CompositeProduct, ProductComponent, SimpleProduct, ProductMaterial
from app.domain.models.material import Material


class CompositeProductBuilder:
    """
    Builder for managing Composite Products and Templates.
    
    Features:
    - Immutability of source template (uses deepcopy).
    - Recursive search for component updates.
    - validation of Material Type compatibility.
    """

    def __init__(self, template: Optional[CompositeProduct] = None):
        """
        Initialize the builder.
        
        Args:
            template: Optional CompositeProduct to use as a starting point.
                      If provided, it will be deep-copied.
        """
        if template:
            # Create a full independent copy of the template structure
            self._product = copy.deepcopy(template)
            # Assign a new ID for the new instance, but keep structure
            self._product.id = uuid.uuid4()
            # Note: Child component IDs are PRESERVED from the template.
            # This is crucial so the caller can reference them by the IDs 
            # they know from the template definition.
        else:
            self._product = CompositeProduct(
                id=uuid.uuid4(),
                name="New Composite Product"
            )

    def with_name(self, name: str) -> "CompositeProductBuilder":
        """Update the root product name."""
        self._product.name = name
        return self

    def with_description(self, description: str) -> "CompositeProductBuilder":
        """Update the root product description."""
        self._product.description = description
        return self

    def with_image_url(self, image_url: str) -> "CompositeProductBuilder":
        """Update the root product image URL."""
        self._product.image_url = image_url
        return self

    def with_properties(self, properties: Dict) -> "CompositeProductBuilder":
        """Update the root product properties."""
        self._product.properties = properties
        return self

    def override_component_image(self, component_id: uuid.UUID, image_url: str) -> "CompositeProductBuilder":
        """Override the image URL of a specific component in the hierarchy."""
        if not self._update_recursive(self._product, component_id, {"image_url": image_url}):
            raise ValueError(f"Component with ID {component_id} not found in product hierarchy.")
        return self

    def override_component_properties(self, component_id: uuid.UUID, properties: Dict) -> "CompositeProductBuilder":
        """Override properties of a specific component in the hierarchy."""
        if not self._update_recursive(self._product, component_id, {"properties": properties}):
            raise ValueError(f"Component with ID {component_id} not found in product hierarchy.")
        return self

    def assign_material(self, component_id: uuid.UUID, material: Material) -> "CompositeProductBuilder":
        """
        Inject a concrete material into a specific component (Template).
        
        This searches the entire product tree for the component with `component_id`.
        
        Args:
            component_id: The ID of the SimpleProduct (template) to update.
            material: The concrete Material to assign.
            
        Raises:
            ValueError: If component not found or material type mismatch.
        """
        if not self._assign_recursive(self._product, component_id, material):
            raise ValueError(f"Component with ID {component_id} not found in product hierarchy.")
        return self

    def _update_recursive(self, current_node: ProductComponent, target_id: uuid.UUID, updates: Dict) -> bool:
        """
        Recursive helper to find and update any attribute of a component.
        """
        if current_node.id == target_id:
            for attr, value in updates.items():
                setattr(current_node, attr, value)
            return True

        if current_node.is_composite():
            if isinstance(current_node, CompositeProduct):
                for comp_qty in current_node.components:
                    if comp_qty.component.id == target_id:
                        for attr, value in updates.items():
                            setattr(comp_qty.component, attr, value)
                        return True
                    
                    if self._update_recursive(comp_qty.component, target_id, updates):
                        return True
        return False

    def _assign_recursive(self, current_node: ProductComponent, target_id: uuid.UUID, material: Material) -> bool:
        """
        Recursive helper to find and update a component.
        
        Returns:
            True if found and updated, False otherwise.
        """
        # Case 1: The current node is the target (works for root too, though unusual for material assignment)
        if current_node.id == target_id:
            self._apply_material(current_node, material)
            return True

        # Case 2: It's a composite, search children
        if current_node.is_composite():
            # We know it's a CompositeProduct if is_composite() is True
            # (Type hinting might need casting if using strict mypy, but duck typing works here)
            if isinstance(current_node, CompositeProduct):
                for comp_qty in current_node.components:
                    # Check the child itself
                    if comp_qty.component.id == target_id:
                        self._apply_material(comp_qty.component, material)
                        return True
                    
                    # Recurse into the child
                    if self._assign_recursive(comp_qty.component, target_id, material):
                        return True
        
        return False

    def _apply_material(self, component: ProductComponent, material: Material):
        """
        Apply the material to the component with validation.
        """
        if not isinstance(component, SimpleProduct):
            raise ValueError(f"Cannot assign material to {type(component).__name__}. Only SimpleProduct supports materials.")
        
        # Validation: Check Material Type compatibility
        if component.material_type:
            # We compare IDs if available, or names as fallback
            if component.material_type.id != material.material_type.id:
                 raise ValueError(
                     f"Material Type Mismatch. "
                     f"Component requires '{component.material_type.name}', "
                     f"but got '{material.material_type.name}'."
                 )
        
        # Apply the material
        # Create a new ProductMaterial instance (default quantity 1.0 for now)
        from decimal import Decimal
        product_material = ProductMaterial(material=material, quantity=Decimal("1.0"))
        component.materials.append(product_material)
        
        # The component is now "Concrete" (no longer just a template)

    def get_missing_requirements(self) -> Dict[uuid.UUID, str]:
        """
        Get a list of all components that still need materials.
        
        Returns:
             Dict[ComponentID, MaterialTypeName]
        """
        return self._product.get_required_material_types()

    def build(self) -> CompositeProduct:
        """
        Return the constructed/modified CompositeProduct.
        """
        return self._product
