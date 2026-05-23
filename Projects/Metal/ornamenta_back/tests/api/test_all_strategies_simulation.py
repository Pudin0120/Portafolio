"""
Comprehensive tests for product simulation with all measurement strategies.
Verifies that dual pricing (purchase vs sale) works correctly for all strategies.
"""
import pytest
import uuid
from decimal import Decimal
from unittest.mock import Mock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.domain.models.material import Material
from app.domain.models.material_type import MaterialType
from app.domain.models.user import User, RoleEnum
from app.domain.value_objects.money import Money
from app.domain.value_objects.document_number import DocumentNumber, DocumentEnum
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateUser, StateEnum
from app.infrastructure.adapters.rest.product_router import router

def make_user() -> User:
    return User(
        identification_number=DocumentNumber(value="1234567890", doc_type=DocumentEnum.CC),
        role=RoleEnum.SUPER_ADMIN,
        first_name="Admin",
        last_name="User",
        email=Email(value="admin@test.com"),
        state=StateUser(value=StateEnum.ACTIVE),
        firebase_uid=str(uuid.uuid4()),
        tenant_id=uuid.uuid4()
    )

def make_material_type(strategy: str) -> MaterialType:
    return MaterialType(
        id=uuid.uuid4(),
        name=f"Material {strategy}",
        description=f"Test {strategy}",
        measurement_strategy=strategy
    )

def make_material(material_type: MaterialType, buy: float, sell: float, base_props: dict) -> Material:
    from app.domain.value_objects.measurement import Measurement
    from app.domain.factories.unit_factory import UnitFactory
    
    # Pre-process base_props to convert dict measurements
    processed_props = {}
    for k, v in base_props.items():
        if isinstance(v, dict) and "value" in v and "unit" in v:
            unit_obj = None
            if v["unit"] == "m": unit_obj = UnitFactory.meter()
            elif v["unit"] == "mm": unit_obj = UnitFactory.millimeter()
            elif v["unit"] == "m2": unit_obj = UnitFactory.meter_squared()
            elif v["unit"] == "m3": unit_obj = UnitFactory.meter_cubed()
            elif v["unit"] == "L": unit_obj = UnitFactory.liter()
            elif v["unit"] == "kg": unit_obj = UnitFactory.kilogram()
            
            if unit_obj:
                processed_props[k] = Measurement(value=Decimal(str(v["value"])), unit=unit_obj)
            else:
                processed_props[k] = v
        elif k in ["volume", "mass"] and isinstance(v, (int, float)):
            # Direct numeric volume/mass (usually in L/kg)
            u = UnitFactory.liter() if k == "volume" else UnitFactory.kilogram()
            processed_props[k] = Measurement(value=Decimal(str(v)), unit=u)
        else:
            processed_props[k] = v

    return Material(
        id=uuid.uuid4(),
        sku=f"SKU-{uuid.uuid4().hex[:8]}",
        material_type=material_type,
        purchase_price=Money(amount=Decimal(str(buy))),
        sale_price=Money(amount=Decimal(str(sell))),
        description=f"Material {material_type.measurement_strategy}",
        properties=processed_props,
        tenant_id=uuid.uuid4()
    )

class TestAllStrategiesSimulation:
    
    @pytest.fixture
    def mock_material_repo(self):
        return Mock()
    
    @pytest.fixture
    def mock_product_repo(self):
        return Mock()

    @pytest.fixture
    def mock_unit_repo(self):
        from app.domain.factories.unit_factory import UnitFactory
        mock = Mock()
        mock.get_all.return_value = [
            UnitFactory.meter(), 
            UnitFactory.meter_squared(),
            UnitFactory.liter(),
            UnitFactory.kilogram()
        ]
        return mock

    @pytest.fixture
    def client(self, mock_material_repo, mock_product_repo, mock_unit_repo):
        from app.infrastructure.adapters.rest.authorization import get_current_user
        from app.infrastructure.dependencies.material_dependencies import (
            get_material_repository, get_product_repository, get_unit_repository
        )
        
        app = FastAPI()
        app.include_router(router)
        
        test_user = make_user()
        app.dependency_overrides[get_current_user] = lambda: test_user
        app.dependency_overrides[get_material_repository] = lambda: mock_material_repo
        app.dependency_overrides[get_product_repository] = lambda: mock_product_repo
        app.dependency_overrides[get_unit_repository] = lambda: mock_unit_repo
        
        return TestClient(app)

    @pytest.mark.parametrize("strategy, base_props, sim_dims, expected_qty", [
        # SHEET: Base 1x2=2m2. Sim 2x2=4m2. Qty = 4/2 = 2.0
        ("SHEET", {"width": 1.0, "length": 2.0, "area": 2.0}, {"width": 2.0, "height": 2.0}, 2.0),
        
        # PROFILE: Base 6m. Sim 12m. Qty = 12/6 = 2.0
        # NOTE: Profile also calculates Volume (m3).
        # Round 100mm diam, 6m length. Area ~ 7854 mm2. Vol ~ 0.0471 m3.
        # Sim 12m length. Vol ~ 0.0942 m3. Ratio = 2.0
        ("PROFILE", {"shape": "ROUND", "diameter": {"value": 100, "unit": "mm"}, "length": {"value": 6.0, "unit": "m"}}, {"length": 12.0}, 2.0),
        
        # LIQUID: Base 1L. Sim 5L. Qty = 5.0
        ("LIQUID", {"volume": 1.0}, {"volume": 5.0}, 5.0),
        
        # SOLID: Base 1kg. Sim 10kg. Qty = 10.0
        ("SOLID", {"mass": 1.0}, {"mass": 10.0}, 10.0),
        
        # LABOR: Base 1hr. Sim 8hr. Qty = 8.0
        # NOTE: LABOR requires unit_type property
        ("LABOR", {"unit_type": "square_meter"}, {"width": 2.0, "height": 4.0}, 8.0),
    ])
    def test_simulation_all_strategies(self, client, mock_material_repo, strategy, base_props, sim_dims, expected_qty):
        # Arrange
        m_type = make_material_type(strategy)
        # Prices: Buy 100, Sell 200
        material = make_material(m_type, 100.0, 200.0, base_props)
        mock_material_repo.get_by_id.return_value = material
    
        # Adjust dimensions for DTO format (value/unit)
        unit_map = {
            "SHEET": "m",
            "PROFILE": "m",
            "LIQUID": "L",
            "SOLID": "kg",
            "LABOR": "m"
        }
        unit = unit_map.get(strategy, "m")
        formatted_dims = {k: {"value": v, "unit": unit} for k, v in sim_dims.items()}
        
        payload = {
            "name": f"Simulated {strategy}",
            "materials": [
                {
                    "material_id": str(material.id),
                    "dimensions": formatted_dims
                }
            ],
            "dimensions": formatted_dims
        }
        
        # Act
        response = client.post("/products/simple/simulate", json=payload)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        expected_purchase = 100.0 * expected_qty
        expected_sale = 200.0 * expected_qty
        
        print(f"\nStrategy: {strategy} | Qty: {expected_qty} | Purchase: {data['purchase_price']} | Sale: {data['sale_price']}")
        
        assert float(data["purchase_price"]) == expected_purchase
        assert float(data["sale_price"]) == expected_sale
        assert data["materials"][0]["calculated_quantity"] == expected_qty
        assert data["materials"][0]["purchase_price"] == expected_purchase
        assert data["materials"][0]["sale_price"] == expected_sale
