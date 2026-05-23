"""
Product Service Layer
"""
from decimal import Decimal
from typing import Dict, Any
import uuid

from app.domain.models.product import SimpleProduct
from app.domain.models.material import Material
from app.domain.value_objects.money import Money
from app.domain.repositories.product_repository import ProductRepository
from app.domain.repositories.material_repository import MaterialRepository
from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository
from app.application.dto.product_dto import SimpleProductCreateDTO


class ProductService:
    def __init__(
        self,
        product_repo: ProductRepository,
        material_repo: MaterialRepository,
        unit_repo: UnitOfMeasureRepository,
    ):
        self.product_repo = product_repo
        self.material_repo = material_repo
        self.unit_repo = unit_repo

    def create_simple_product(self, product_data: SimpleProductCreateDTO) -> SimpleProduct:
        """
        Creates a simple product.
        """
        self._validate_product_data(product_data)

        material = self._get_material(product_data.material_id)
        
        generated_name = self._generate_product_name(product_data, material)
        self._check_existing_product(generated_name)

        product_price = self._get_product_price(product_data)

        quantity_multiplier = self._calculate_quantity_multiplier(material, product_data.dimensions)

        product = SimpleProduct(
            id=uuid.uuid4(),
            name=generated_name,
            description=product_data.description,
            material=material,
            dimensions=product_data.dimensions,
            quantity_multiplier=quantity_multiplier,
            price=product_price,
        )

        return self.product_repo.save(product)

    def _validate_product_data(self, product_data: SimpleProductCreateDTO):
        if product_data.material_id is not None and product_data.price_override is not None:
            raise ValueError("No se puede establecer 'price_override' cuando el product tiene un material asociado.")
        
        if product_data.material_id is None and product_data.price_override is None:
            raise ValueError("Se requiere 'price_override' cuando el product no tiene material asociado.")

        if product_data.name is not None:
            raise ValueError("El nombre del product se creara automaticamente.")

    def _get_material(self, material_id: uuid.UUID) -> Material:
        if not material_id:
            return None
        
        material = self.material_repo.get_by_id(material_id)
        if not material:
            raise ValueError(f"Material with ID {material_id} not found")
        return material

    def _generate_product_name(self, product_data: SimpleProductCreateDTO, material: Material) -> str:
        if material:
            width = product_data.dimensions.get('width', '')
            height = product_data.dimensions.get('height', '')
            unit_text = product_data.dimensions.get('unit', '')
            
            unit_name = unit_text
            if unit_text:
                unit_obj = self.unit_repo.get_by_pint_text(unit_text) or self.unit_repo.get_by_symbol(unit_text)
                if unit_obj:
                    unit_name = unit_obj.name + "s"
            
            return f"{material.name} {width}x{height} {unit_name}".strip()
        
        if not product_data.description:
            raise ValueError("Para products sin material se requiere una description.")
        return product_data.description

    def _check_existing_product(self, name: str):
        existing = self.product_repo.get_by_name(name)
        if existing:
            raise ValueError(f"Product with generated name '{name}' already exists")

    def _get_product_price(self, product_data: SimpleProductCreateDTO) -> Money:
        if product_data.price_override:
            return Money(
                amount=product_data.price_override.amount,
                currency=product_data.price_override.currency,
            )
        return None

    def _calculate_quantity_multiplier(self, material: Material, dimensions: Dict[str, Any]) -> Decimal:
        if not material:
            return Decimal("1.0")

        measurement_type = material.get_measurement_type()
        
        if measurement_type == "SHEET":
            width = Decimal(str(dimensions.get('width', 1)))
            height = Decimal(str(dimensions.get('height', 1)))
            return width * height
        elif measurement_type == "PROFILE":
            length = Decimal(str(dimensions.get('length', 1)))
            return length
        elif measurement_type == "SOLID":
            width = Decimal(str(dimensions.get('width', 1)))
            height = Decimal(str(dimensions.get('height', 1)))
            depth = Decimal(str(dimensions.get('depth', 1)))
            return width * height * depth
        elif measurement_type == "LIQUID":
            volume = Decimal(str(dimensions.get('volume', 1)))
            return volume
        
        return Decimal("1.0")
