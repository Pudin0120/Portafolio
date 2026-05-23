
import pytest
from decimal import Decimal
from uuid import uuid4
from app.domain.models.material import Material
from app.domain.models.material_type import MaterialType
from app.domain.models.unit_of_measure import UnitOfMeasure
from app.domain.value_objects.money import Money
from app.domain.value_objects.gauge import SteelGauge
from app.domain.value_objects.measurement import Measurement
from app.domain.builders.product_builder import ProductBuilder
from app.domain.strategies.sheet_measurement_strategy import SheetMeasurementStrategy

@pytest.fixture
def mock_unit_repo(mocker):
    repo = mocker.Mock()
    
    m_unit = UnitOfMeasure(id=uuid4(), name="Metro", symbol="m", pint_unit_text="meter", dimension="length")
    m2_unit = UnitOfMeasure(id=uuid4(), name="Metro cuadrado", symbol="m", pint_unit_text="meter ** 2", dimension="area")
    mm_unit = UnitOfMeasure(id=uuid4(), name="Milimetro", symbol="mm", pint_unit_text="millimeter", dimension="length")
    
    repo.get_all.return_value = [m_unit, m2_unit, mm_unit]
    return repo

def test_sheet_product_price_calculation(mock_unit_repo):
    # 1. Setup Material: Lamina de Acero, Calibre 14, Area de referencia 1m2, Price $100.00
    sheet_type = MaterialType(
        id=uuid4(),
        name="Lamina",
        measurement_strategy="SHEET"
    )
    
    m2_unit = next(u for u in mock_unit_repo.get_all() if u.symbol == "m")
    
    material = Material(
        id=uuid4(),
        material_type=sheet_type,
        sku="SHEET-14",
        purchase_price=Money(amount=Decimal("100.00")), # $100 per m2
        sale_price=Money(amount=Decimal("150.00")),     # $150 per m2
        properties={
            "thickness": SteelGauge(number=14),
            "area": Measurement(value=Decimal("1.0"), unit=m2_unit)
        }
    )
    
    # 2. Build Product: 2m x 2m (Area = 4m2)
    strategy = SheetMeasurementStrategy(mock_unit_repo)
    builder = ProductBuilder()
    product = (builder
        .with_material(material)
        .with_strategy(strategy)
        .with_dimensions_dict({
            "width": 2.0,
            "height": 2.0,
            "unit": "m"
        })
        .build()
    )
    
    # 3. Verify Calculations
    # Area should be 4.0
    # Multiplier should be 4.0 (relative to 1m2 material)
    # Total Sale Price should be 150 * 4 = 600
    
    print(f"\nProduct Multiplier: {product.quantity_multiplier}")
    print(f"Material Sale Price: {material.sale_price}")
    print(f"Product Total Sale Price: {product.get_total_sale_price()}")
    
    assert product.quantity_multiplier == Decimal("4.0")
    assert product.get_total_sale_price().amount == Decimal("600.00")

if __name__ == "__main__":
    # This is for manual debugging if needed
    pass
