"""
Integration tests for Material API endpoints.

Tests cover:
- Listing materials with filters (by material_type_id, by strategy)
- Getting material by ID
- Creating materials
- Updating materials
- Deleting materials
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
from app.domain.models.unit_of_measure import UnitOfMeasure
from app.domain.repositories.material_repository import MaterialRepository
from app.domain.repositories.material_type_repository import MaterialTypeRepository
from app.domain.strategies.strategy_registry import MeasurementStrategyRegistry
from app.domain.value_objects.money import Money
from app.domain.value_objects.gauge import Gauge, SteelGauge, SteelGauge
from app.domain.value_objects.measurement import Measurement
from app.domain.value_objects.document_number import DocumentNumber, DocumentEnum
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateUser, StateEnum
from app.infrastructure.adapters.rest.material_router import router
from app.application.services.inventory_service import InventoryService
from app.infrastructure.dependencies.inventory_dependencies import (
    get_inventory_service,
    get_unit_repository
)
from app.infrastructure.dependencies.material_dependencies import (
    get_material_repository, 
    get_material_type_repository, 
    get_create_material_use_case,
    get_update_material_use_case,
)


def make_user(role: RoleEnum = RoleEnum.MANAGER) -> User:
    """Factory helper to create a test user."""
    return User(
        identification_number=DocumentNumber(value="1234567890", doc_type=DocumentEnum.CC),
        role=role,
        first_name="Test",
        last_name="User",
        email=Email(value="test@test.com"),
        state=StateUser(value=StateEnum.ACTIVE),
        firebase_uid=str(uuid.uuid4()),
        tenant_id=uuid.uuid4()
    )


def make_material_type(
    material_type_id: uuid.UUID = None,
    name: str = "Acero galvanizado",
    strategy: str = "SHEET"
) -> MaterialType:
    """Factory helper to create a test material type."""
    return MaterialType(
        id=material_type_id or uuid.uuid4(),
        name=name,
        description=f"Test {name}",
        measurement_strategy=strategy
    )


def make_material(
    material_id: uuid.UUID = None,
    material_type: MaterialType = None,
    strategy_name: str = "SHEET",
    description: str = "Calibre 14",
    price_amount: Decimal = Decimal("50.00"),
    properties: dict = None,
    unit_repo = None,
    tenant_id: uuid.UUID = None
) -> Material:
    """Factory helper to create a test material."""
    if material_type is None:
        material_type = make_material_type()
    
    # Use mock_unit_repo if provided, otherwise create a simple one for tests
    if unit_repo is None:
        from unittest.mock import Mock
        from app.domain.factories.unit_factory import UnitFactory
        unit_repo = Mock()
        all_units = [
            UnitFactory.meter(), UnitFactory.millimeter(), UnitFactory.centimeter(),
            UnitFactory.inch(), UnitFactory.foot(), UnitFactory.meter_squared(),
            UnitFactory.millimeter_squared(), UnitFactory.centimeter_squared(),
            UnitFactory.meter_cubed(), UnitFactory.liter(), UnitFactory.milliliter(),
            UnitFactory.gallon(), UnitFactory.kilogram(), UnitFactory.gram(),
            UnitFactory.pound(), UnitFactory.ounce(), UnitFactory.kg_per_liter(),
            UnitFactory.kg_per_cubic_meter(),
        ]
        unit_repo.get_all.return_value = all_units
    
    registry = MeasurementStrategyRegistry(unit_repo)
    strategy = registry.get_strategy(strategy_name)
    
    # Create default properties based on strategy if not provided
    if properties is None:
        if strategy_name == "SHEET":
            # Create unit for area
            from app.domain.factories.unit_factory import UnitFactory
            area_unit = UnitFactory.meter_squared()
            
            from app.domain.value_objects.gauge import SteelGauge
            properties = {
                "thickness": SteelGauge(number=14),
                "area": Measurement(value=Decimal("1.0"), unit=area_unit)
            }
        elif strategy_name == "PROFILE":
            # Create units for profile
            from app.domain.factories.unit_factory import UnitFactory
            length_unit = UnitFactory.meter()
            
            properties = {
                "shape": "ROUND",
                "diameter": Measurement(value=Decimal("2.0"), unit=length_unit),
                "length": Measurement(value=Decimal("6.0"), unit=length_unit),
                "thickness": Measurement(value=Decimal("2.5"), unit=length_unit)
            }
    
    return Material(
        id=material_id or uuid.uuid4(),
        material_type=material_type,
        sku=f"SKU-{uuid.uuid4().hex[:8]}",
        purchase_price=Money(amount=price_amount),
        sale_price=Money(amount=price_amount * Decimal("1.2")),
        description=description,
        properties=properties,
        tenant_id=tenant_id
    )


class TestMaterialAPI:
    """Test suite for Material API endpoints."""
    
    @pytest.fixture
    def mock_material_repo(self):
        """Mock material repository."""
        repo = Mock(spec=MaterialRepository)
        # Mock methods to return values/lists instead of raising AttributeError
        repo.get_all.return_value = []
        repo.count_all = Mock(return_value=0)
        repo.get_by_material_type.return_value = []
        repo.count_by_material_type = Mock(return_value=0)
        repo.get_by_strategy.return_value = []
        repo.count_by_strategy = Mock(return_value=0)
        return repo
    
    @pytest.fixture
    def mock_material_type_repo(self):
        """Mock material type repository."""
        return Mock(spec=MaterialTypeRepository)
    
    @pytest.fixture
    def mock_unit_repo(self):
        """Mock unit of measure repository."""
        from app.domain.factories.unit_factory import UnitFactory
        mock = Mock()
        all_units = [
            UnitFactory.meter(), UnitFactory.millimeter(), UnitFactory.centimeter(),
            UnitFactory.inch(), UnitFactory.foot(), UnitFactory.meter_squared(),
            UnitFactory.millimeter_squared(), UnitFactory.centimeter_squared(),
            UnitFactory.meter_cubed(), UnitFactory.liter(), UnitFactory.milliliter(),
            UnitFactory.gallon(), UnitFactory.kilogram(), UnitFactory.gram(),
            UnitFactory.pound(), UnitFactory.ounce(), UnitFactory.kg_per_liter(),
            UnitFactory.kg_per_cubic_meter(),
        ]
        mock.get_all.return_value = all_units
        
        # Setup get_by_symbol behavior
        def get_by_symbol(symbol):
            # Handle mapping for common symbols
            target = symbol
            if symbol == "m":
                return next((u for u in all_units if u.symbol == "m"), None)
            if symbol == "m":
                return next((u for u in all_units if u.symbol == "m"), None)
            return next((u for u in all_units if u.symbol == target), None)
        
        mock.get_by_symbol.side_effect = get_by_symbol
            
        mock.get_by_symbol.side_effect = get_by_symbol

        # Setup get_by_id behavior
        mock.get_by_id.side_effect = lambda id: next((u for u in all_units if u.id == id), None)
        
        return mock
    
    @pytest.fixture
    def test_user(self):
        """Test user for authentication (MANAGER by default)."""
        user = make_user(RoleEnum.MANAGER)
        return user
    
    @pytest.fixture
    def employee_user(self, test_user):
        """Test user with EMPLOYEE role (no permissions for price updates)."""
        user = make_user(RoleEnum.EMPLOYEE)
        user.tenant_id = test_user.tenant_id
        return user
    
    @pytest.fixture
    def material_type(self):
        """Test material type."""
        return make_material_type()
    
    @pytest.fixture
    def sheet_material(self, material_type, test_user):
        """Test sheet material."""
        return make_material(
            material_type=material_type,
            strategy_name="SHEET",
            description="Calibre 14",
            tenant_id=test_user.tenant_id
        )
    
    @pytest.fixture
    def tube_material(self, mock_unit_repo, test_user):
        """Test tube material."""
        tube_type = make_material_type(strategy="PROFILE", name="Tubo")
        return make_material(
            material_type=tube_type,
            strategy_name="PROFILE",
            description="Tubo 2 pulgadas",
            unit_repo=mock_unit_repo,
            tenant_id=test_user.tenant_id
        )
    
    @pytest.fixture
    def app(self, mock_material_repo, mock_material_type_repo, mock_unit_repo):
        """FastAPI test application."""
        from app.infrastructure.containers import Container
        from app.infrastructure.adapters.rest import material_router
        
        # Create app
        app = FastAPI()
        
        # Create and configure container
        container = Container()
        
        # Override providers with mocks
        container.material_repository.override(mock_material_repo)
        container.material_type_repository.override(mock_material_type_repo)
        container.unit_of_measure_repo.override(mock_unit_repo)
        
        # Wire container to material router
        container.wire(modules=[material_router])
        
        # Attach container to app
        app.container = container
        
        # Include router
        app.include_router(router)
        
        return app
    
    @pytest.fixture
    def mock_inventory_service(self):
        """Mock inventory service."""
        return Mock(spec=InventoryService)
    
    @pytest.fixture
    def client(self, app, test_user, mock_material_repo, mock_material_type_repo, mock_unit_repo, mock_inventory_service):
        """Test client for FastAPI with dependency overrides."""
        # Mock authentication dependency
        from app.infrastructure.adapters.rest.authorization import get_current_user
        
        app.dependency_overrides[get_current_user] = lambda: test_user
        app.dependency_overrides[get_material_repository] = lambda: mock_material_repo
        app.dependency_overrides[get_material_type_repository] = lambda: mock_material_type_repo
        app.dependency_overrides[get_unit_repository] = lambda: mock_unit_repo
        app.dependency_overrides[get_inventory_service] = lambda: mock_inventory_service
        
        return TestClient(app)
    
    # ============================================================================
    # LIST MATERIALS TESTS
    # ============================================================================
    
    def test_list_all_materials(self, client, mock_material_repo, sheet_material, tube_material):
        """Test listing all materials without filters."""
        # Arrange
        mock_material_repo.get_all.return_value = [sheet_material, tube_material]
        mock_material_repo.count_all.return_value = 2
        
        # Act
        response = client.get("/materials/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["materials"]) == 2
        mock_material_repo.get_all.assert_called_once()
    
    def test_list_materials_by_material_type(self, client, mock_material_repo, material_type, sheet_material):
        """Test filtering materials by material_type_id."""
        # Arrange
        mock_material_repo.get_by_material_type.return_value = [sheet_material]
        mock_material_repo.count_by_material_type.return_value = 1
        
        # Act
        response = client.get(f"/materials/?material_type_id={material_type.id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["materials"][0]["material_type_id"] == str(material_type.id)
        mock_material_repo.get_by_material_type.assert_called_once_with(material_type.id, tenant_id=sheet_material.tenant_id, limit=10, offset=0)
    
    def test_list_materials_by_strategy(self, client, mock_material_repo, sheet_material):
        """Test filtering materials by measurement strategy."""
        # Arrange
        mock_material_repo.get_by_strategy.return_value = [sheet_material]
        mock_material_repo.count_by_strategy.return_value = 1
        
        # Act
        response = client.get("/materials/?strategy=sheet")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["materials"][0]["measurement_strategy"] == "SHEET"
        mock_material_repo.get_by_strategy.assert_called_once_with("sheet", tenant_id=sheet_material.tenant_id, limit=10, offset=0)
    
    def test_list_empty_materials(self, client, mock_material_repo):
        """Test listing materials when none exist."""
        # Arrange
        mock_material_repo.get_all.return_value = []
        mock_material_repo.count_all.return_value = 0
        
        # Act
        response = client.get("/materials/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["materials"]) == 0
    
    # ============================================================================
    # GET MATERIAL BY ID TESTS
    # ============================================================================
    
    def test_get_material_by_id_success(self, client, mock_material_repo, sheet_material):
        """Test getting a material by ID."""
        # Arrange
        mock_material_repo.get_by_id.return_value = sheet_material
        
        # Act
        response = client.get(f"/materials/{sheet_material.id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sheet_material.id)
        assert data["description"] == sheet_material.description
        assert data["purchase_price_amount"] == str(sheet_material.purchase_price.amount)
        assert data["purchase_price_currency"] == "COP"
        mock_material_repo.get_by_id.assert_called_once_with(sheet_material.id, tenant_id=sheet_material.tenant_id)

    def test_get_material_by_id_not_found(self, client, mock_material_repo, test_user):
        """Test getting a non-existent material."""
        # Arrange
        material_id = uuid.uuid4()
        mock_material_repo.get_by_id.return_value = None
        
        # Act
        response = client.get(f"/materials/{material_id}")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
        mock_material_repo.get_by_id.assert_called_once_with(material_id, tenant_id=test_user.tenant_id)

    
    # ============================================================================
    # CREATE MATERIAL TESTS
    # ============================================================================
    
    def test_create_material_success(self, client, mock_material_repo, mock_material_type_repo, material_type):
        """
        Test creating a new material.
        """
        # Arrange
        mock_material_type_repo.get_by_id.return_value = material_type
        
        # Create a material with proper domain objects that will be returned
        area_unit = UnitOfMeasure(
            id=uuid.uuid4(),
            name="Metro cuadrado",
            symbol="m",
            pint_unit_text="meter ** 2",
            dimension="area"
        )
        
        created_material = Material(
            id=uuid.uuid4(),
            material_type=material_type,
            sku=f"SKU-{uuid.uuid4().hex[:8]}",
            purchase_price=Money(amount=Decimal("45.50")),
            sale_price=Money(amount=Decimal("54.60")),
            description="Calibre 16",
            properties={
                "thickness": SteelGauge(number=16),
                "area": Measurement(value=Decimal("1.0"), unit=area_unit)
            }
        )
        mock_material_repo.save.return_value = created_material
        
        payload = {
            "material_type_id": str(material_type.id),
            "description": "Calibre 16",
            "purchase_price_amount": "45.50",
            "properties": {
                "thickness": {"gauge": 16},
                "area": {"value": 1.0, "unit": "m2"}
            }
        }
        
        # Act
        response = client.post("/materials/", json=payload)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["description"] == payload["description"]
        assert data["purchase_price_amount"] == payload["purchase_price_amount"]
    
    def test_create_material_with_tube_strategy(self, client, mock_material_repo, mock_material_type_repo):
        """
        Test creating a material with tube measurement strategy.
        """
        # Arrange
        tube_type = make_material_type(strategy="PROFILE", name="Tubo")
        mock_material_type_repo.get_by_id.return_value = tube_type
        
        length_unit = UnitOfMeasure(id=uuid.uuid4(), name="Metro", symbol="m", dimension="length", pint_unit_text="meter")
        
        created_material = Material(
            id=uuid.uuid4(),
            material_type=tube_type,
            sku=f"SKU-{uuid.uuid4().hex[:8]}",
            purchase_price=Money(amount=Decimal("120.00")),
            sale_price=Money(amount=Decimal("144.00")),
            description="Tubo 2 pulg x 6m",
            properties={
                "shape": "ROUND",
                "diameter": Measurement(value=Decimal("50.8"), unit=length_unit),
                "length": Measurement(value=Decimal("6.0"), unit=length_unit),
                "thickness": Measurement(value=Decimal("1.5"), unit=length_unit)
            }
        )
        mock_material_repo.save.return_value = created_material
        
        payload = {
            "material_type_id": str(tube_type.id),
            "description": "Tubo 2 pulg x 6m",
            "purchase_price_amount": "120.00",
            "properties": {
                "shape": "ROUND",
                "diameter": {"value": 50.8, "unit": "mm"},
                "length": {"value": 6, "unit": "m"},
                "thickness": {"value": 1.5, "unit": "mm"}
            }
        }
        
        # Act
        response = client.post("/materials/", json=payload)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["measurement_strategy"] == "PROFILE"
    
    def test_create_material_material_type_not_found(self, client, mock_material_type_repo, test_user):
        """Test creating a material with non-existent material type."""
        # Arrange
        material_type_id = uuid.uuid4()
        mock_material_type_repo.get_by_id.return_value = None
        
        payload = {
            "material_type_id": str(material_type_id),
            "description": "Test",
            "measurement_strategy": "sheet",
            "purchase_price_amount": "50.00",
            "properties": {}
        }
        
        # Act
        response = client.post("/materials/", json=payload)
        
        # Assert
        # The UseCase raises ValueError when not found, which maps to 400
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()
        mock_material_type_repo.get_by_id.assert_called_once_with(material_type_id, tenant_id=test_user.tenant_id)
    
    def test_create_material_invalid_strategy(self, client, mock_material_type_repo, material_type):
        """Test creating a material with invalid measurement strategy properties."""
        # Arrange
        mock_material_type_repo.get_by_id.return_value = material_type
        
        # We send properties that don't match the SHEET strategy (empty properties)
        payload = {
            "material_type_id": str(material_type.id),
            "description": "Test",
            "measurement_strategy": "invalid_strategy", # This is ignored by backend, it uses material_type.strategy
            "purchase_price_amount": "50.00",
            "properties": {} # Empty properties should fail for SHEET strategy
        }
        
        # Act
        response = client.post("/materials/", json=payload)
        
        # Assert
        assert response.status_code == 400
        # The error comes from property validation
        detail = response.json()["detail"].lower()
        assert "invalid material" in detail
        assert "sheet material requires" in detail
    
    def test_create_material_negative_price(self, client, mock_material_type_repo, material_type):
        """Test creating a material with negative price (should be caught by DTO validation)."""
        # Arrange
        mock_material_type_repo.get_by_id.return_value = material_type
        
        payload = {
            "material_type_id": str(material_type.id),
            "description": "Test",
            "measurement_strategy": "sheet",
            "purchase_price_amount": "-50.00",
            "properties": {}
        }
        
        # Act
        response = client.post("/materials/", json=payload)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    # ============================================================================
    # UPDATE MATERIAL TESTS
    # ============================================================================
    
    def test_update_material_description(self, client, mock_material_repo, sheet_material):
        """Test updating a material's description."""
        # Arrange
        mock_material_repo.get_by_id.return_value = sheet_material
        mock_material_repo.save.side_effect = lambda material: material
        
        payload = {
            "description": "Calibre 18 Actualizado"
        }
        
        # Act
        response = client.patch(f"/materials/{sheet_material.id}", json=payload)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == payload["description"]
        mock_material_repo.get_by_id.assert_called_once_with(sheet_material.id, tenant_id=sheet_material.tenant_id)
        mock_material_repo.save.assert_called_once()
    
    def test_update_material_price(self, client, mock_material_repo, sheet_material):
        """Test updating a material's price."""
        # Arrange
        mock_material_repo.get_by_id.return_value = sheet_material
        mock_material_repo.save.side_effect = lambda material: material
    
        payload = {
            "purchase_price_amount": "75.00"
        }
    
        # Act
        response = client.patch(f"/materials/{sheet_material.id}", json=payload)
    
        # Assert
        assert response.status_code == 200
        data = response.json()
    
        # Response might be wrapped in 'material' if it's an update response
        if "material" in data:
            data = data["material"]
    
        assert data["purchase_price_amount"] == payload["purchase_price_amount"]
        assert data["purchase_price_currency"] == "COP"  # Currency should always be COP
        mock_material_repo.get_by_id.assert_called_with(sheet_material.id, tenant_id=sheet_material.tenant_id)
        mock_material_repo.save.assert_called()
    
    def test_update_material_properties(self, client, mock_material_repo, sheet_material):
        """Test updating a material's properties."""
        # Arrange
        mock_material_repo.get_by_id.return_value = sheet_material
        mock_material_repo.save.side_effect = lambda material: material
    
        # Use valid property structure with valid unit symbol
        payload = {
            "properties": {
                "thickness": {"gauge": 20},
                "area": {"value": 1.5, "unit": "m2"}, # Use m2 instead of m
            }
        }
    
        # Act
        response = client.patch(f"/materials/{sheet_material.id}", json=payload)
    
        # Assert
        assert response.status_code == 200
        data = response.json()
    
        # Response might be wrapped in 'material'
        if "material" in data:
            data = data["material"]
    
        # Verify specific properties
        assert "thickness" in data["properties"]
        assert "area" in data["properties"]
        mock_material_repo.get_by_id.assert_called_with(sheet_material.id, tenant_id=sheet_material.tenant_id)
        mock_material_repo.save.assert_called()

    def test_update_labor_material_properties_persists_dynamic_description(self, client, mock_material_repo, test_user):
        """LABOR update should persist strategic description with area measurement."""
        # Arrange
        labor_type = make_material_type(strategy="LABOR", name="Soldada")
        labor_material = make_material(
            material_type=labor_type,
            strategy_name="LABOR",
            description="Soldada",
            properties={"unit_type": "square_meter"},
            tenant_id=test_user.tenant_id,
        )

        mock_material_repo.get_by_id.return_value = labor_material
        mock_material_repo.save.side_effect = lambda material: material

        payload = {
            "properties": {
                "unit_type": "metro cuadrado",
                "area": {"value": 20, "unit": "m2"}
            }
        }

        # Act
        response = client.patch(f"/materials/{labor_material.id}", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        if "material" in data:
            data = data["material"]

        assert data["measurement_strategy"] == "LABOR"
        assert data["properties"]["unit_type"] == "square_meter"
        assert data["properties"]["area"]["value"] == 20.0
        assert "Por metro cuadrado" in (data["description"] or "")
        assert "20" in (data["description"] or "")
        mock_material_repo.save.assert_called()
    
    def test_update_material_multiple_fields(self, client, mock_material_repo, sheet_material):
        """Test updating multiple fields at once."""
        # Arrange
        mock_material_repo.get_by_id.return_value = sheet_material
        mock_material_repo.save.side_effect = lambda material: material
    
        payload = {
            "description": "Nueva description",
            "purchase_price_amount": "90.00",
            "properties": {"thickness": {"gauge": 22}}
        }
    
        # Act
        response = client.patch(f"/materials/{sheet_material.id}", json=payload)
    
        # Assert
        assert response.status_code == 200
        data = response.json()
    
        # Response might be wrapped in 'material'
        if "material" in data:
            data = data["material"]
    
        # When properties are updated, the description might be auto-generated for Sheet materials.
        # So we should check if the new price is set correctly, which is a direct field update.
        assert data["purchase_price_amount"] == payload["purchase_price_amount"]
    
        # Verify save was called
        mock_material_repo.get_by_id.assert_called_with(sheet_material.id, tenant_id=sheet_material.tenant_id)
        mock_material_repo.save.assert_called()
    
    def test_update_material_not_found(self, client, mock_material_repo, test_user):
        """Test updating a non-existent material."""
        # Arrange
        material_id = uuid.uuid4()
        mock_material_repo.get_by_id.return_value = None
        
        payload = {
            "description": "Test"
        }
        
        # Act
        response = client.patch(f"/materials/{material_id}", json=payload)
        
        # Assert
        # UseCase raises ValueError -> 400
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()
        mock_material_repo.get_by_id.assert_called_once_with(material_id, tenant_id=test_user.tenant_id)
    
    def test_update_material_price_currency_ignored(self, client, mock_material_repo, sheet_material):
        """Test that price_currency is ignored during update (always COP)."""
        # Arrange
        mock_material_repo.get_by_id.return_value = sheet_material
        mock_material_repo.save.side_effect = lambda material: material
        
        payload = {
            "purchase_price_amount": "80.00",
            "price_currency": "USD"  # This should be ignored
        }
        
        # Act
        response = client.patch(f"/materials/{sheet_material.id}", json=payload)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Response might be wrapped in 'material'
        if "material" in data:
            data = data["material"]
            
        assert data["purchase_price_currency"] == "COP"  # Should always be COP, not USD
        mock_material_repo.get_by_id.assert_called_with(sheet_material.id, tenant_id=sheet_material.tenant_id)
    
    # ============================================================================
    # DELETE MATERIAL TESTS
    # ============================================================================
    
    def test_delete_material_success(self, client, mock_inventory_service, sheet_material):
        """Test deleting a material."""
        # Arrange
        # The router calls inventory_service.delete_material
        mock_inventory_service.delete_material.return_value = None
        
        # Act
        response = client.delete(f"/materials/{sheet_material.id}")
        
        # Assert
        assert response.status_code == 204
        mock_inventory_service.delete_material.assert_called_once_with(sheet_material.id, tenant_id=sheet_material.tenant_id)
    
    def test_delete_material_not_found(self, client, mock_inventory_service, test_user):
        """Test deleting a non-existent material."""
        # Arrange
        material_id = uuid.uuid4()
        # inventory_service raises Exception if not found
        mock_inventory_service.delete_material.side_effect = Exception("Material not found")
        
        # Act
        response = client.delete(f"/materials/{material_id}")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
        mock_inventory_service.delete_material.assert_called_once_with(material_id, tenant_id=test_user.tenant_id)
    
    # ============================================================================
    # EDGE CASES AND VALIDATION TESTS
    # ============================================================================
    
    def test_list_materials_invalid_uuid(self, client):
        """Test listing materials with invalid UUID format."""
        # Act
        response = client.get("/materials/?material_type_id=invalid-uuid")
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_create_material_missing_required_fields(self, client):
        """Test creating a material without required fields."""
        # Arrange
        payload = {
            "description": "Test"
            # Missing material_type_id, measurement_strategy, price_amount
        }
        
        # Act
        response = client.post("/materials/", json=payload)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_update_material_price_forbidden_for_employee(self, client, app, mock_material_repo, sheet_material, employee_user):
        """Test that an employee cannot update material price."""
        # Arrange
        from app.infrastructure.adapters.rest.authorization import get_current_user
        app.dependency_overrides[get_current_user] = lambda: employee_user
        
        mock_material_repo.get_by_id.return_value = sheet_material
        
        payload = {
            "purchase_price_amount": "100.00"
        }
        
        # Act
        response = client.patch(f"/materials/{sheet_material.id}", json=payload)
        
        # Assert
        assert response.status_code == 403
        assert "permisos" in response.json()["detail"].lower()
    
    def test_update_material_price_cascading_impact(self, client, mock_material_repo, sheet_material):
        """Test that updating price returns the impact on products."""
        # Arrange
        mock_material_repo.get_by_id.return_value = sheet_material
        mock_material_repo.save.side_effect = lambda material: material
        
        # Mock the response from price_service via the UseCase
        # In the real test, we'd need to mock the service dependency or its method
        
        payload = {
            "purchase_price_amount": "200.00"
        }
        
        # Act
        response = client.patch(f"/materials/{sheet_material.id}", json=payload)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "impact" in data
        assert "products_affected" in data["impact"]
        assert data["material"]["purchase_price_amount"] == "200.00"

    def test_create_material_liquid_strategy(self, client, mock_material_repo, mock_material_type_repo):
        """Test creating a material with LIQUID measurement strategy."""
        # Arrange
        liquid_type = make_material_type(strategy="LIQUID", name="Pintura")
        mock_material_type_repo.get_by_id.return_value = liquid_type
        
        from app.domain.factories.unit_factory import UnitFactory
        volume_unit = UnitFactory.liter()
        
        created_material = Material(
            id=uuid.uuid4(),
            material_type=liquid_type,
            sku=f"SKU-{uuid.uuid4().hex[:8]}",
            purchase_price=Money(amount=Decimal("85.00")),
            sale_price=Money(amount=Decimal("102.00")),
            description="Pintura Blanca 1 Galon",
            properties={
                "volume": Measurement(value=Decimal("3.785"), unit=volume_unit)
            }
        )
        mock_material_repo.save.return_value = created_material
        
        payload = {
            "material_type_id": str(liquid_type.id),
            "description": "Pintura Blanca 1 Galon",
            "purchase_price_amount": "85.00",
            "properties": {
                "volume": {"value": 3.785, "unit": "L"}
            }
        }
        
        # Act
        response = client.post("/materials/", json=payload)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["measurement_strategy"] == "LIQUID"
        assert data["properties"]["volume"]["value"] == 3.785

    def test_create_material_solid_strategy(self, client, mock_material_repo, mock_material_type_repo):
        """Test creating a material with SOLID measurement strategy."""
        # Arrange
        solid_type = make_material_type(strategy="SOLID", name="Tornillos")
        mock_material_type_repo.get_by_id.return_value = solid_type
        
        from app.domain.factories.unit_factory import UnitFactory
        mass_unit = UnitFactory.kilogram()
        
        created_material = Material(
            id=uuid.uuid4(),
            material_type=solid_type,
            sku=f"SKU-{uuid.uuid4().hex[:8]}",
            purchase_price=Money(amount=Decimal("15.00")),
            sale_price=Money(amount=Decimal("18.00")),
            description="Tornillo 2 pulg",
            properties={
                "mass": Measurement(value=Decimal("1.0"), unit=mass_unit)
            }
        )
        mock_material_repo.save.return_value = created_material
        
        payload = {
            "material_type_id": str(solid_type.id),
            "description": "Tornillo 2 pulg",
            "purchase_price_amount": "15.00",
            "properties": {
                "mass": {"value": 1.0, "unit": "kg"}
            }
        }
        
        # Act
        response = client.post("/materials/", json=payload)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["measurement_strategy"] == "SOLID"
        assert data["properties"]["mass"]["value"] == 1.0

    def test_create_material_unit_strategy(self, client, mock_material_repo, mock_material_type_repo):
        """Test creating a material with UNIT measurement strategy."""
        # Arrange
        unit_type = make_material_type(strategy="UNIT", name="Manija")
        mock_material_type_repo.get_by_id.return_value = unit_type
        
        created_material = Material(
            id=uuid.uuid4(),
            material_type=unit_type,
            sku=f"SKU-{uuid.uuid4().hex[:8]}",
            purchase_price=Money(amount=Decimal("15000.00")),
            sale_price=Money(amount=Decimal("18000.00")),
            description="Manija Acero Inox",
            properties={
                "brand": "Hettich",
                "part_number": "12345"
            }
        )
        mock_material_repo.save.return_value = created_material
        
        payload = {
            "material_type_id": str(unit_type.id),
            "description": "Manija Acero Inox",
            "purchase_price_amount": "15000.00",
            "properties": {
                "brand": "Hettich",
                "part_number": "12345"
            }
        }
        
        # Act
        response = client.post("/materials/", json=payload)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["measurement_strategy"] == "UNIT"
        assert data["properties"]["brand"] == "Hettich"

    def test_update_material_tube_properties_full(self, client, mock_material_repo, tube_material):
        """Test full update of tube properties."""
        # Arrange
        mock_material_repo.get_by_id.return_value = tube_material
        mock_material_repo.save.side_effect = lambda material: material
        
        payload = {
            "properties": {
                "shape": "ROUND",
                "diameter": {"value": 76.2, "unit": "mm"}, # 3 inches
                "length": {"value": 12.0, "unit": "m"},
                "thickness": {"value": 5.0, "unit": "mm"}
            }
        }
        
        # Act
        response = client.patch(f"/materials/{tube_material.id}", json=payload)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        if "material" in data:
            data = data["material"]
            
        assert data["properties"]["diameter"]["value"] == 76.2
        assert data["properties"]["length"]["value"] == 12.0
        assert data["properties"]["thickness"]["value"] == 5.0
