"""
Domain value objects for dimensional calculation rules.

These value objects define how component dimensions are calculated
based on parent product dimensions in composite products.
"""
from dataclasses import dataclass
from typing import Optional, Literal
from decimal import Decimal


@dataclass(frozen=True)
class DimensionRule:
    """
    Rule for calculating a specific dimension of a component.
    
    Immutable value object that defines how a component's dimension
    (width, height, or depth) should be calculated based on the parent
    product's dimensions.
    
    Reference Types:
        - "parent": Takes dimension directly from parent (e.g., height = parent.height)
        - "fixed": Uses a fixed value regardless of parent (e.g., height = 30cm always)
        - "formula": Applies a formula referencing parent dimensions (future)
    
    Attributes:
        reference_type: How to calculate this dimension
        parent_dimension: Which parent dimension to use (for "parent" type)
        fixed_value: Fixed value to use (for "fixed" type)
        formula: Formula expression (for "formula" type, future enhancement)
        unit: Unit of measurement (mm, cm, m)
    
    Examples:
        >>> # Profile height matches door height
        >>> height_rule = DimensionRule(
        ...     reference_type="parent",
        ...     parent_dimension="height",
        ...     unit="mm"
        ... )
        
        >>> # Decorative angle always 30cm
        >>> angle_rule = DimensionRule(
        ...     reference_type="fixed",
        ...     fixed_value=Decimal("300"),
        ...     unit="mm"
        ... )
    """
    
    reference_type: Literal["parent", "fixed", "formula"]
    parent_dimension: Optional[str] = None  # "width", "height", "depth"
    fixed_value: Optional[Decimal] = None
    formula: Optional[str] = None  # For future enhancement
    unit: str = "mm"
    
    def __post_init__(self) -> None:
        """Validate the dimension rule."""
        if self.reference_type == "parent" and not self.parent_dimension:
            raise ValueError("parent_dimension is required when reference_type is 'parent'")
        
        if self.reference_type == "fixed" and self.fixed_value is None:
            raise ValueError("fixed_value is required when reference_type is 'fixed'")
        
        if self.reference_type == "formula" and not self.formula:
            raise ValueError("formula is required when reference_type is 'formula'")
        
        if self.parent_dimension and self.parent_dimension not in ["width", "height", "depth"]:
            raise ValueError(f"Invalid parent_dimension: {self.parent_dimension}")
    
    def calculate(self, parent_dimensions: dict[str, float]) -> float:
        """
        Calculate the dimension value based on parent dimensions.
        
        Args:
            parent_dimensions: Dictionary with parent's width, height, depth
        
        Returns:
            Calculated dimension value in the specified unit
        
        Raises:
            ValueError: If parent dimension is missing or formula is invalid
        """
        if self.reference_type == "parent":
            if self.parent_dimension not in parent_dimensions:
                raise ValueError(f"Parent dimension '{self.parent_dimension}' not found")
            return parent_dimensions[self.parent_dimension]
        
        elif self.reference_type == "fixed":
            if self.fixed_value is None:
                raise ValueError("fixed_value cannot be None for 'fixed' reference type")
            return float(self.fixed_value)
        
        elif self.reference_type == "formula":
            # Future: Implement safe formula evaluation
            # For now, raise NotImplementedError
            raise NotImplementedError("Formula-based dimension rules not yet implemented")
        
        return 0.0


@dataclass(frozen=True)
class ComponentRelationship:
    """
    Defines how a component relates to its parent product.
    
    Immutable value object that encapsulates the complete relationship
    between a component and its parent composite product, including
    dimensional rules and quantity calculation logic.
    
    Attributes:
        width_rule: How to calculate component width
        height_rule: How to calculate component height
        depth_rule: How to calculate component depth
        quantity_type: How quantity is calculated (fixed, perimeter, area)
        base_quantity: Base quantity before multipliers
        quantity_multiplier: Multiplier applied to calculated quantity
    
    Quantity Types:
        - "fixed": Constant quantity regardless of dimensions
        - "perimeter": Quantity based on parent perimeter (e.g., profiles)
        - "area": Quantity based on parent area (e.g., sheets, paint)
    
    Examples:
        >>> # Vertical profile: height from parent, fixed 2 units
        >>> vertical_profile = ComponentRelationship(
        ...     height_rule=DimensionRule(reference_type="parent", parent_dimension="height"),
        ...     width_rule=DimensionRule(reference_type="fixed", fixed_value=Decimal("50")),
        ...     quantity_type="fixed",
        ...     base_quantity=Decimal("2")
        ... )
        
        >>> # Perimeter gasket: follows perimeter
        >>> gasket = ComponentRelationship(
        ...     quantity_type="perimeter",
        ...     base_quantity=Decimal("1"),
        ...     quantity_multiplier=Decimal("1")
        ... )
    """
    
    width_rule: Optional[DimensionRule] = None
    height_rule: Optional[DimensionRule] = None
    depth_rule: Optional[DimensionRule] = None
    quantity_type: Literal["fixed", "perimeter", "area"] = "fixed"
    base_quantity: Decimal = Decimal("1")
    quantity_multiplier: Decimal = Decimal("1")
    
    def __post_init__(self) -> None:
        """Validate the component relationship."""
        if self.base_quantity <= 0:
            raise ValueError("base_quantity must be positive")
        
        if self.quantity_multiplier <= 0:
            raise ValueError("quantity_multiplier must be positive")
    
    def calculate_dimensions(self, parent_dimensions: dict[str, float]) -> dict[str, float]:
        """
        Calculate component dimensions based on parent dimensions.
        
        Args:
            parent_dimensions: Dictionary with parent's width, height, depth
        
        Returns:
            Dictionary with calculated width, height, depth
        """
        result = {}
        
        if self.width_rule:
            result["width"] = self.width_rule.calculate(parent_dimensions)
        
        if self.height_rule:
            result["height"] = self.height_rule.calculate(parent_dimensions)
        
        if self.depth_rule:
            result["depth"] = self.depth_rule.calculate(parent_dimensions)
        
        return result
    
    def calculate_quantity(self, parent_dimensions: dict[str, float]) -> Decimal:
        """
        Calculate component quantity based on parent dimensions.
        
        Args:
            parent_dimensions: Dictionary with parent's width, height, depth
        
        Returns:
            Calculated quantity as Decimal
        """
        if self.quantity_type == "fixed":
            return self.base_quantity * self.quantity_multiplier
        
        elif self.quantity_type == "perimeter":
            width = Decimal(str(parent_dimensions.get("width", 0)))
            height = Decimal(str(parent_dimensions.get("height", 0)))
            perimeter = (width + height) * Decimal("2")
            return perimeter * self.quantity_multiplier
        
        elif self.quantity_type == "area":
            width = Decimal(str(parent_dimensions.get("width", 0)))
            height = Decimal(str(parent_dimensions.get("height", 0)))
            area = width * height
            return area * self.quantity_multiplier
        
        return self.base_quantity
