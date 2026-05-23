from typing import Dict, Any
from app.domain.models.product import ProductComponent
from app.domain.value_objects.dimensions import Dimensions
from app.domain.value_objects.gauge import Gauge
from app.domain.models.material import Material
from app.domain.units import ureg


class Sheet(ProductComponent):
    """
    Represents a simple component (a leaf in the Composite pattern), like a sheet of metal.
    Its material composition is determined by its surface area.
    """

    def __init__(self, dimensions: Dimensions, gauge: Gauge, material: Material):
        self.dimensions = dimensions
        self.gauge = gauge
        self.material = material

    def get_material_composition(self) -> Dict[str, Any]:
        """
        The material composition of a sheet is its surface area.
        The thickness is implicitly defined by the gauge but not used for this calculation.
        """
        # The key is the material name, and the value is the calculated area.
        return {
            self.material.name: self.dimensions.area
        }

    def get_price(self) -> float:
        """
        Calculates the price of the sheet based on its area and material price.
        """
        material_price = self.material.get_price().amount
        if material_price is None:
            return 0.0
        return float(self.dimensions.area.magnitude * material_price)
