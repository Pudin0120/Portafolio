"""
Factory service for creating products from materials.

This service handles the conversion of materials into simple products
for two main use cases:
1. Direct material sales (selling material "as-is" from catalog)
2. Custom fabricated products (using material with specific dimensions)

IMPORTANT: Prices are ALWAYS stored in materials, NOT in products.
Products calculate their price dynamically based on the material's current price.
If material price changes, all products using that material reflect the new price automatically.

UPDATED: Ahora incluye integracion con ProductBuilder para validacion completa
y soporte mejorado para estrategias de measurement con pint.
"""
from typing import Optional, Dict, Any
from decimal import Decimal
import uuid

from app.domain.models.material import Material
from app.domain.models.product import SimpleProduct
from app.domain.builders.product_builder import ProductBuilder
from app.domain.strategies.measurement_strategy import MeasurementStrategy


class ProductFactoryService:
    """
    Service for creating SimpleProducts from Materials.
    
    Key principle: Products do NOT store prices. They always calculate
    their price in real-time from the material's current price.
    
    This ensures:
    - Material price changes propagate automatically to all products
    - No price inconsistencies between material and products
    - Single source of truth for pricing (the Material)
    """
    
    @staticmethod
    def create_material_sale_product(
        material: Material,
        quantity: Decimal = Decimal("1.0"),
        name_override: Optional[str] = None,
        description_override: Optional[str] = None
    ) -> SimpleProduct:
        """
        Create a SimpleProduct for selling a material directly.
        
        Use case: Customer wants to buy material "as-is" from catalog.
        Example: "Vender 2.5m de lamina de acero calibre 14"
        
        The product will calculate its price dynamically:
        - price = material.price  quantity
        - If material price changes, this product's price changes automatically
        
        Args:
            material: The material to sell
            quantity: Quantity to sell (in material's base unit)
            name_override: Optional custom name (defaults to material name)
            description_override: Optional custom description
        
        Returns:
            SimpleProduct that calculates price from material dynamically
            
        Example:
            >>> steel_sheet = Material(name="Acero calibre 14", price=Money(50000), ...)
            >>> product = ProductFactoryService.create_material_sale_product(
            ...     material=steel_sheet,
            ...     quantity=Decimal("2.5")
            ... )
            >>> product.name
            'Venta: Acero calibre 14 (2.5m)'
            >>> product.get_total_price()  # Calculated in real-time
            Money(amount=125000)  # $50,000  2.5
            
            >>> # If material price changes:
            >>> steel_sheet.price = Money(55000)
            >>> product.get_total_price()  # Automatically updated
            Money(amount=137500)  # $55,000  2.5
        """
        # Generate name for the sale
        unit = ProductFactoryService._get_material_unit(material)
        default_name = f"Venta: {material.name} ({quantity}{unit})"
        product_name = name_override or default_name
        
        # Generate description
        if description_override:
            product_description = description_override
        else:
            product_description = f"Venta directa de material: {material.full_name}"
        
        # Create dimensions dictionary based on material strategy
        dimensions = ProductFactoryService._create_dimensions_for_quantity(material, quantity)
        
        # Create product - note that NO PRICE is stored here!
        # Price is calculated dynamically via material.price
        builder = ProductBuilder()
        builder.with_id(uuid.uuid4())
        builder.with_name(product_name)
        builder.with_description(product_description)
        builder.with_material(material, quantity=quantity)
        builder.with_normalized_dimensions(**dimensions)
        
        return builder.build()
    
    @staticmethod
    def create_custom_product_from_material(
        material: Material,
        name: str,
        dimensions: Dict[str, float],
        description: Optional[str] = None
    ) -> SimpleProduct:
        """
        Create a SimpleProduct with custom dimensions from a material.
        
        Use case: Customer needs a specific cut/size of material.
        Example: "Lamina de 1m  2.5m para porton lateral"
        
        The product will calculate its price dynamically based on:
        - Material's current price
        - Calculated quantity from dimensions and material strategy
        
        Args:
            material: The material to use
            name: Name for the custom product
            dimensions: Specific dimensions for this use
            description: Optional description
        
        Returns:
            SimpleProduct with custom dimensions that calculates price dynamically
            
        Example:
            >>> steel_sheet = Material(name="Acero calibre 14", ...)
            >>> product = ProductFactoryService.create_custom_product_from_material(
            ...     material=steel_sheet,
            ...     name="Lamina lateral izquierda del porton #1234",
            ...     dimensions={"width": 1.0, "height": 2.5},
            ...     description="Corte especifico para porton industrial"
            ... )
            >>> product.get_total_price()  # Calculated in real-time
            Money(amount=125000)  # $50,000/m  2.5m
            
            >>> # If material price changes:
            >>> steel_sheet.price = Money(55000)
            >>> product.get_total_price()  # Automatically updated
            Money(amount=137500)  # $55,000/m  2.5m
        """
        # Calculate quantity based on dimensions and material strategy
        quantity = ProductFactoryService._calculate_quantity_from_dimensions(
            material, dimensions
        )
        
        # Create product - NO PRICE stored!
        builder = ProductBuilder()
        builder.with_id(uuid.uuid4())
        builder.with_name(name)
        builder.with_description(description or f"Product personalizado usando {material.name}")
        builder.with_material(material, quantity=quantity)
        builder.with_normalized_dimensions(**dimensions)
        
        return builder.build()
    
    @staticmethod
    def _get_material_unit(material: Material) -> str:
        """
        Get the unit symbol for a material based on its strategy.
        
        Args:
            material: The material
        
        Returns:
            Unit symbol (e.g., "m", "m", "L", "kg")
        """
        strategy_name = material.material_type.measurement_strategy or "SIMPLE"
        
        unit_map = {
            "SHEET": "m",
            "PROFILE": "m",
            "LIQUID": "L",
            "SOLID": "kg"
        }
        
        return unit_map.get(strategy_name, "unidad")
    
    @staticmethod
    def _create_dimensions_for_quantity(
        material: Material,
        quantity: Decimal
    ) -> Dict[str, Any]:
        """
        Create dimensions dictionary based on material type and quantity.
        
        This is used for direct material sales where we know the quantity
        but need to represent it as dimensions for the SimpleProduct.
        
        Args:
            material: The material
            quantity: The quantity to sell
        
        Returns:
            Dimensions dictionary appropriate for the material's strategy
        """
        strategy_name = material.material_type.measurement_strategy or "SIMPLE"
        
        if strategy_name == "SHEET":
            # For sheets, quantity is typically area
            return {"area": float(quantity), "unit": "m"}
        elif strategy_name == "PROFILE":
            # For profiles, quantity is typically length
            return {"length": float(quantity), "unit": "m"}
        elif strategy_name == "LIQUID":
            # For liquids, quantity is volume
            return {"volume": float(quantity), "unit": "L"}
        elif strategy_name == "SOLID":
            # For solids, quantity is mass
            return {"mass": float(quantity), "unit": "kg"}
        else:
            # Generic fallback
            return {"quantity": float(quantity)}
    
    @staticmethod
    def _calculate_quantity_from_dimensions(
        material: Material,
        dimensions: Dict[str, float]
    ) -> Decimal:
        """
        Calculate quantity multiplier from dimensions using material's strategy.
        
        This delegates to the material's measurement strategy to calculate
        how much material is needed based on the dimensions.
        
        Args:
            material: The material
            dimensions: Product dimensions
        
        Returns:
            Quantity multiplier (e.g., area in m, length in m, etc.)
        """
        strategy_name = material.material_type.measurement_strategy or "SIMPLE"
        
        if strategy_name == "SHEET":
            # For sheets, calculate area from width  height
            if "width" in dimensions and "height" in dimensions:
                area = dimensions["width"] * dimensions["height"]
                return Decimal(str(area))
            elif "area" in dimensions:
                return Decimal(str(dimensions["area"]))
            else:
                # Default to 1.0 if no dimensions
                return Decimal("1.0")
        
        elif strategy_name == "PROFILE":
            # For profiles, use length
            if "length" in dimensions:
                return Decimal(str(dimensions["length"]))
            else:
                return Decimal("1.0")
        
        elif strategy_name == "LIQUID":
            # For liquids, use volume
            if "volume" in dimensions:
                return Decimal(str(dimensions["volume"]))
            else:
                return Decimal("1.0")
        
        elif strategy_name == "SOLID":
            # For solids, use mass
            if "mass" in dimensions:
                return Decimal(str(dimensions["mass"]))
            else:
                return Decimal("1.0")
        
        else:
            # Generic fallback
            if "quantity" in dimensions:
                return Decimal(str(dimensions["quantity"]))
            else:
                return Decimal("1.0")
    
    @staticmethod
    def create_product_with_builder(
        material: Material,
        dimensions: Dict[str, Any],
        strategy: Optional[MeasurementStrategy] = None,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> SimpleProduct:
        """
        Crea un SimpleProduct usando ProductBuilder con validacion completa.
        
        Este metodo es la forma RECOMENDADA de create products cuando se necesita:
        - Validacion completa de dimensiones
        - Normalizacion de unidades con pint
        - Validacion por estrategia de measurement
        
        Args:
            material: Material base del product
            dimensions: Dimensiones con unidades (dict con values y units)
            strategy: Estrategia de measurement opcional para validacion
            name: Nombre opcional (se genera si no se proporciona)
            description: Description opcional
        
        Returns:
            SimpleProduct completamente validado
        
        Raises:
            ValueError: Si las dimensiones son invalid para la estrategia
        
        Example JSON input:
            {
                "material_id": "123e4567-e89b-12d3-a456-426614174000",
                "dimensions": {
                    "width": {"value": 1.0, "unit": "m"},
                    "height": {"value": 2.5, "unit": "m"}
                },
                "name": "Lamina lateral izquierda",
                "description": "Corte personalizado para porton"
            }
        
        Example usage:
            >>> from app.domain.strategies.strategy_registry import MeasurementStrategyRegistry
            >>> registry = MeasurementStrategyRegistry(unit_repo)
            >>> strategy = registry.get_strategy("SHEET")
            >>> 
            >>> product = ProductFactoryService.create_product_with_builder(
            ...     material=steel_material,
            ...     dimensions={
            ...         "width": {"value": 1.0, "unit": "m"},
            ...         "height": {"value": 2.5, "unit": "m"}
            ...     },
            ...     strategy=strategy,
            ...     name="Lamina lateral"
            ... )
            >>> 
            >>> # Las dimensiones estan normalizadas a SI estandar
            >>> product.dimensions  # {"width": 1.0, "height": 2.5}
            >>> product.quantity_multiplier  # Decimal("2.5") = 1.0  2.5
        """
        builder = ProductBuilder()
        builder.with_material(material)
        builder.with_dimensions_dict(dimensions)
        
        if strategy:
            builder.with_strategy(strategy)
        
        if name:
            builder.with_name(name)
        
        if description:
            builder.with_description(description)
        
        return builder.build()
    
    @staticmethod
    def create_product_with_normalized_dimensions(
        material: Material,
        normalized_dimensions: Dict[str, float],
        strategy: Optional[MeasurementStrategy] = None,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> SimpleProduct:
        """
        Crea un SimpleProduct con dimensiones ya normalizadas (en SI estandar).
        
        Util cuando las dimensiones ya fueron normalizadas previamente
        y no se necesita conversion de unidades adicional.
        
        Args:
            material: Material base del product
            normalized_dimensions: Dimensiones en unidades SI (metros, m, etc.)
            strategy: Estrategia de measurement opcional para validacion
            name: Nombre opcional
            description: Description opcional
        
        Returns:
            SimpleProduct con dimensiones normalizadas
        
        Example:
            >>> # Dimensiones ya en SI estandar (metros)
            >>> product = ProductFactoryService.create_product_with_normalized_dimensions(
            ...     material=steel_material,
            ...     normalized_dimensions={"width": 1.0, "height": 2.5},  # metros
            ...     name="Lamina cortada"
            ... )
        """
        builder = ProductBuilder()
        builder.with_material(material)
        
        # Aplicar dimensiones normalizadas
        builder.with_normalized_dimensions(**normalized_dimensions)
        
        if strategy:
            builder.with_strategy(strategy)
        
        if name:
            builder.with_name(name)
        
        if description:
            builder.with_description(description)
        
        return builder.build()


# Example usage documentation
"""
Usage Examples:
===============

1. Direct Material Sale:
-----------------------
>>> # Customer wants to buy 3.5m of steel sheet
>>> steel_material = material_repo.get_by_id(material_id)
>>> product = ProductFactoryService.create_material_sale_product(
...     material=steel_material,
...     quantity=Decimal("3.5")
... )
>>> 
>>> # Price is calculated dynamically
>>> product.get_total_price()  # $50,000/m  3.5m = $175,000
>>>
>>> # If material price changes later
>>> steel_material.price = Money(55000)
>>> product.get_total_price()  # NOW returns $192,500 automatically!


2. Custom Fabricated Product:
-----------------------------
>>> # Customer needs a custom cut for a door frame
>>> steel_material = material_repo.get_by_id(material_id)
>>> door_frame = ProductFactoryService.create_custom_product_from_material(
...     material=steel_material,
...     name="Marco de puerta lateral",
...     dimensions={"width": 0.8, "height": 2.0},  # 1.6m
...     description="Marco para puerta de oficina"
... )
>>>
>>> # Price calculated from dimensions
>>> door_frame.get_total_price()  # $50,000/m  1.6m = $80,000
>>>
>>> # Material price changes are reflected immediately
>>> steel_material.price = Money(52000)
>>> door_frame.get_total_price()  # NOW returns $83,200


3. Multiple Products from Same Material:
----------------------------------------
>>> # All these products will update if material price changes
>>> lamina1 = ProductFactoryService.create_custom_product_from_material(
...     material=steel_material,
...     name="Lamina izquierda",
...     dimensions={"width": 1.0, "height": 2.5}  # 2.5m
... )
>>>
>>> lamina2 = ProductFactoryService.create_custom_product_from_material(
...     material=steel_material,
...     name="Lamina derecha",
...     dimensions={"width": 1.0, "height": 2.5}  # 2.5m
... )
>>>
>>> # Both use the same material reference
>>> assert lamina1.material is lamina2.material  # True!
>>>
>>> # If material price changes, BOTH products update
>>> steel_material.price = Money(60000)
>>> lamina1.get_total_price()  # $150,000
>>> lamina2.get_total_price()  # $150,000
"""
