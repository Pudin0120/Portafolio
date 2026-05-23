"""
Integration tests for Product API endpoints.

Tests cover:
- Creating simple products
- Creating composite products
- Listing products with filters
- Getting product by ID
- Updating products
- Deleting products
- Getting product components
"""
import pytest
import uuid
from decimal import Decimal
from typing import Optional, List
from unittest.mock import Mock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.domain.models.product import SimpleProduct, CompositeProduct
from app.domain.models.material import Material
from app.domain.models.material_type import MaterialType
from app.domain.models.user import User, RoleEnum
from app.domain.repositories.product_repository import ProductRepository
from app.domain.repositories.material_repository import MaterialRepository
from app.domain.value_objects.money import Money
from app.domain.value_objects.document_number import DocumentNumber, DocumentEnum
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateUser, StateEnum
from app.infrastructure.adapters.rest.product_router import router


def make_user() -> User:
    """Factory helper to create a test user."""
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


def make_material_type() -> MaterialType:
    """Factory helper to create a test material type."""
    return MaterialType(
        id=uuid.uuid4(),
        name="Acero galvanizado",
        description="Test steel",
        measurement_strategy="SHEET"
    )


def make_material(material_type: MaterialType, tenant_id: Optional[uuid.UUID] = None) -> Material:
    """Factory helper to create a test material."""
    return Material(
        id=uuid.uuid4(),
        sku=f"SKU-{uuid.uuid4().hex[:8]}",
        material_type=material_type,
        purchase_price=Money(amount=Decimal("50.00")),
        sale_price=Money(amount=Decimal("60.00")),
        description="Sheet metal calibre 14",
        properties={
            "thickness": 14,
            "area": {"value": 1.0, "unit": "m2"}
        },
        tenant_id=tenant_id
    )


def make_simple_product(material: Material, product_id: Optional[uuid.UUID] = None, tenant_id: Optional[uuid.UUID] = None) -> SimpleProduct:
    """Factory helper to create a test simple product."""
    from app.domain.models.product import ProductMaterial
    
    return SimpleProduct(
        id=product_id or uuid.uuid4(),
        name=f"Test Product {uuid.uuid4().hex[:8]}",
        description="Test simple product",
        materials=[ProductMaterial(material=material, quantity=Decimal("1.0"))],
        dimensions={"width": 2.0, "height": 2.5},
        tenant_id=tenant_id
    )


def make_composite_product(components: Optional[list] = None, product_id: Optional[uuid.UUID] = None, tenant_id: Optional[uuid.UUID] = None) -> CompositeProduct:
    """Factory helper to create a test composite product."""
    composite = CompositeProduct(
        id=product_id or uuid.uuid4(),
        name=f"Test Composite {uuid.uuid4().hex[:8]}",
        description="Test composite product",
        components=[],
        tenant_id=tenant_id
    )
    
    if components:
        for component, quantity in components:
            composite.add_component(component, quantity)
    
    return composite


class TestProductAPI:
    """Test suite for Product API endpoints."""
    
    @pytest.fixture
    def mock_product_repo(self):
        """Mock product repository."""
        return Mock(spec=ProductRepository)
    
    @pytest.fixture
    def mock_material_repo(self):
        """Mock material repository."""
        return Mock(spec=MaterialRepository)
    
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
        return mock
    
    @pytest.fixture
    def test_user(self):
        """Test user for authentication."""
        return make_user()
    
    @pytest.fixture
    def material_type(self):
        """Test material type."""
        return make_material_type()
    
    @pytest.fixture
    def material(self, material_type, test_user):
        """Test material."""
        return make_material(material_type, tenant_id=test_user.tenant_id)
    
    @pytest.fixture
    def simple_product(self, material, test_user):
        """Test simple product."""
        return make_simple_product(material, tenant_id=test_user.tenant_id)
    
    @pytest.fixture
    def composite_product(self, simple_product, test_user):
        """Test composite product."""
        return make_composite_product([(simple_product, 2)], tenant_id=test_user.tenant_id)
    
    @pytest.fixture
    def app(self, mock_product_repo, mock_material_repo, mock_unit_repo):
        """FastAPI test application."""
        from app.infrastructure.containers import Container
        
        # Create app
        app = FastAPI()
        
        # Create and configure container (still needed for some services if they use @inject)
        container = Container()
        container.product_repository.override(mock_product_repo)
        container.material_repository.override(mock_material_repo)
        container.unit_of_measure_repo.override(mock_unit_repo)
        
        # Attach container to app
        app.container = container
        
        # Include router
        app.include_router(router)
        
        return app
    
    @pytest.fixture
    def client(self, app, test_user, mock_product_repo, mock_material_repo, mock_unit_repo):
        """Test client for FastAPI with dependency overrides."""
        from app.infrastructure.adapters.rest.authorization import get_current_user
        from app.infrastructure.dependencies.material_dependencies import (
            get_product_repository,
            get_material_repository,
            get_unit_repository,
            get_product_creation_service,
            get_composite_product_service
        )
        from app.application.services.product_creation_service import ProductCreationService
        from app.application.services.composite_product_service import CompositeProductService
        
        # Mock services that depend on repos
        product_creation_service = ProductCreationService(
            material_repository=mock_material_repo,
            product_repository=mock_product_repo,
            unit_repository=mock_unit_repo
        )
        composite_product_service = CompositeProductService(
            product_repository=mock_product_repo
        )
        
        app.dependency_overrides[get_current_user] = lambda: test_user
        app.dependency_overrides[get_product_repository] = lambda: mock_product_repo
        app.dependency_overrides[get_material_repository] = lambda: mock_material_repo
        app.dependency_overrides[get_unit_repository] = lambda: mock_unit_repo
        app.dependency_overrides[get_product_creation_service] = lambda: product_creation_service
        app.dependency_overrides[get_composite_product_service] = lambda: composite_product_service
        
        return TestClient(app)
    
    # ============================================================================
    # LIST PRODUCTS TESTS
    # ============================================================================
    
    def test_list_all_products(self, client, mock_product_repo, test_user, simple_product, composite_product):
        """Test listing all products."""
        # Arrange
        mock_product_repo.get_all.return_value = [simple_product, composite_product]
        mock_product_repo.count_all.return_value = 2
        
        # Act
        response = client.get("/products/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["products"]) == 2
        mock_product_repo.get_all.assert_called_once()
    
    def test_list_simple_products_only(self, client, mock_product_repo, simple_product):
        """Test filtering simple products."""
        # Arrange
        mock_product_repo.get_all_simple.return_value = [simple_product]
        mock_product_repo.count_simple.return_value = 1
        
        # Act
        response = client.get("/products/?product_type=simple")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["products"][0]["product_type"] == "simple"
        mock_product_repo.get_all_simple.assert_called_once()
    
    def test_list_composite_products_only(self, client, mock_product_repo, composite_product):
        """Test filtering composite products."""
        # Arrange
        mock_product_repo.get_all_composite.return_value = [composite_product]
        mock_product_repo.count_composite.return_value = 1
        
        # Act
        response = client.get("/products/?product_type=composite")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["products"][0]["product_type"] == "composite"
        mock_product_repo.get_all_composite.assert_called_once()
    
    # ============================================================================
    # GET PRODUCT BY ID TESTS
    # ============================================================================
    
    def test_get_product_by_id_success(self, client, mock_product_repo, simple_product):
        """Test getting a product by ID."""
        # Arrange
        mock_product_repo.get_by_id.return_value = simple_product
        
        # Act
        response = client.get(f"/products/{simple_product.id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(simple_product.id)
        assert data["name"] == simple_product.name
        mock_product_repo.get_by_id.assert_called_once_with(simple_product.id)
    
    def test_get_product_by_id_not_found(self, client, mock_product_repo):
        """Test getting a non-existent product."""
        # Arrange
        product_id = uuid.uuid4()
        mock_product_repo.get_by_id.return_value = None
        
        # Act
        response = client.get(f"/products/{product_id}")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    # ============================================================================
    # CREATE SIMPLE PRODUCT TESTS
    # ============================================================================
    
    def test_create_simple_product_success(self, client, mock_product_repo, mock_material_repo, material):
        """Test creating a simple product."""
        from app.domain.models.product import ProductMaterial

        # Arrange
        mock_material_repo.get_by_id.return_value = material
        mock_product_repo.get_by_name.return_value = None
        mock_product_repo.get_by_name_and_material.return_value = None
        
        # Simular guardado exitoso devolviendo un objeto real
        product_id = uuid.uuid4()
        saved_product = SimpleProduct(
            id=product_id,
            name="New Simple Product",
            materials=[ProductMaterial(material=material, quantity=Decimal("1.0"))],
            dimensions={"width": 2.0, "height": 3.0},
            properties={"original_unit": "m"}
        )
        mock_product_repo.save.return_value = saved_product
        
        payload = {
            "name": "New Simple Product",
            "materials": [
                {
                    "material_id": str(material.id),
                    "dimensions": {
                        "width": {"value": 2.0, "unit": "m"},
                        "height": {"value": 3.0, "unit": "m"}
                    }
                }
            ],
            "dimensions": {
                "width": {"value": 2.0, "unit": "m"},
                "height": {"value": 3.0, "unit": "m"}
            }
        }
        
        # Act
        response = client.post("/products/simple", json=payload)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert "product" in data
        assert data["product"]["name"] == payload["name"]
    
    def test_create_simple_product_material_not_found(self, client, mock_material_repo):
        """Test creating a simple product with non-existent material."""
        # Arrange
        material_id = uuid.uuid4()
        mock_material_repo.get_by_id.return_value = None
        
        payload = {
            "name": "Invalid Product",
            "materials": [
                {
                    "material_id": str(material_id),
                    "dimensions": {
                        "width": {"value": 2.0, "unit": "m"},
                        "height": {"value": 3.0, "unit": "m"}
                    }
                }
            ],
            "dimensions": {
                "width": {"value": 2.0, "unit": "m"},
                "height": {"value": 3.0, "unit": "m"}
            }
        }
        
        # Act
        response = client.post("/products/simple", json=payload)
        
        # Assert
        # product_creation_service raises ValueError if material not found, 
        # which router converts to 400.
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()
    
    def test_create_simple_product_duplicate_name(self, client, mock_product_repo, mock_material_repo, material, simple_product):
        """Test creating a simple product with duplicate name."""
        # Arrange
        mock_material_repo.get_by_id.return_value = material
        mock_product_repo.get_by_name.return_value = simple_product
        mock_product_repo.get_by_name_and_material.return_value = None
        
        # Simular que el repositorio lanza la excepcion de duplicado si se intenta save
        # Aunque el router deberia atraparlo antes con get_by_name
        
        payload = {
            "name": simple_product.name,
            "materials": [
                {
                    "material_id": str(material.id),
                    "dimensions": {
                        "width": {"value": 2.0, "unit": "m"},
                        "height": {"value": 3.0, "unit": "m"}
                    }
                }
            ],
            "dimensions": {
                "width": {"value": 2.0, "unit": "m"},
                "height": {"value": 3.0, "unit": "m"}
            }
        }
        
        # Act
        response = client.post("/products/simple", json=payload)
        
        # Assert
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    # ============================================================================
    # CREATE COMPOSITE PRODUCT TESTS
    # ============================================================================
    
    def test_create_composite_product_success(self, client, mock_product_repo, simple_product):
        """Test creating a composite product."""
        # Arrange
        mock_product_repo.get_by_name.return_value = None
        
        # Simular guardado exitoso devolviendo un objeto real compatible con lo que espera el service
        composite_id = uuid.uuid4()
        saved_composite = CompositeProduct(
            id=composite_id,
            name="New Composite Product",
            description="A composite product"
        )
        saved_composite.add_component(simple_product, quantity=2)
        
        # Configurar mock para devolver simple_product en la creation y saved_composite despues
        mock_product_repo.get_by_id.side_effect = [
            simple_product, # Primera llamada dentro del service para el componente
            saved_composite # Segunda llamada en el router para el DTO de retorno
        ]
        
        mock_product_repo.save.return_value = saved_composite
    
        payload = {
            "name": "New Composite Product",
            "description": "A composite product",
            "components": [
                {"product_id": str(simple_product.id), "quantity": 2}
            ]
        }
    
        # Act
        response = client.post("/products/composite", json=payload)
    
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["product_type"] == "composite"
        mock_product_repo.save.assert_called_once()
    
    def test_create_composite_product_component_not_found(self, client, mock_product_repo):
        """Test creating a composite product with non-existent component."""
        # Arrange
        component_id = uuid.uuid4()
        mock_product_repo.get_by_name.return_value = None
        mock_product_repo.get_by_id.return_value = None
    
        payload = {
            "name": "Invalid Composite",
            "description": "Composite with invalid component",
            "components": [
                {"product_id": str(component_id), "quantity": 1}
            ]
        }
    
        # Act
        response = client.post("/products/composite", json=payload)
    
        # Assert
        assert response.status_code == 400
        assert "no encontrado" in response.json()["detail"].lower()
    
    def test_create_composite_product_duplicate_name(self, client, mock_product_repo, composite_product):
        """Test creating a composite product with duplicate name."""
        # Arrange
        mock_product_repo.get_by_name.return_value = composite_product
    
        payload = {
            "name": composite_product.name,
            "description": "Duplicate name",
            "components": [{"product_id": str(uuid.uuid4()), "quantity": 1}]
        }
    
        # Act
        response = client.post("/products/composite", json=payload)
    
        # Assert
        assert response.status_code == 400
        assert "ya existe" in response.json()["detail"].lower()
    
    def test_create_composite_product_empty_components(self, client, mock_product_repo):
        """Test creating a composite product with empty components (should fail)."""
        # Arrange
        mock_product_repo.get_by_name.return_value = None
    
        payload = {
            "name": "Empty Components Composite",
            "description": "Should fail due to empty components",
            "components": []
        }
    
        # Act
        response = client.post("/products/composite", json=payload)
    
        # Assert
        assert response.status_code == 400
        assert "al menos un componente" in response.json()["detail"].lower()
    
    def test_create_composite_product_invalid_quantity(self, client, mock_product_repo, simple_product):
        """Test creating composite product with invalid (zero or negative) component quantity."""
        # Arrange
        mock_product_repo.get_by_name.return_value = None
        mock_product_repo.get_by_id.return_value = simple_product
    
        payloads = [
            {"name": "Invalid Qty 0", "components": [{"product_id": str(simple_product.id), "quantity": 0}]},
            {"name": "Invalid Qty Negative", "components": [{"product_id": str(simple_product.id), "quantity": -1}]}
        ]
    
        for payload in payloads:
            response = client.post("/products/composite", json=payload)
            assert response.status_code == 400
            assert "quantity" in response.json()["detail"].lower()

    def test_create_simple_product_with_recipe_success(self, client, mock_product_repo, mock_material_repo, material):
        """Test creating a simple product with multiple materials (recipe)."""
        from app.domain.models.product import ProductMaterial

        # Arrange
        mock_material_repo.get_by_id.return_value = material
        mock_product_repo.get_by_name.return_value = None
        
        product_id = uuid.uuid4()
        saved_product = SimpleProduct(
            id=product_id,
            name="Recipe Product",
            materials=[
                ProductMaterial(material=material, quantity=Decimal("1.5")),
                ProductMaterial(material=material, quantity=Decimal("2.0"))
            ],
            dimensions={"width": 1.0, "height": 1.0}
        )
        mock_product_repo.save.return_value = saved_product
        
        payload = {
            "name": "Recipe Product",
            "materials": [
                {
                    "material_id": str(material.id),
                    "quantity": 1.5,
                    "dimensions": {
                        "width": {"value": 1.0, "unit": "m"}
                    }
                },
                {
                    "material_id": str(material.id),
                    "quantity": 2.0
                }
            ],
            "dimensions": {
                "width": {"value": 1.0, "unit": "m"},
                "height": {"value": 1.0, "unit": "m"}
            }
        }
        
        # Act
        response = client.post("/products/simple", json=payload)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["product"]["name"] == "Recipe Product"
        assert len(data["product"]["recipe"]) == 2
        assert data["product"]["recipe"][0]["quantity"] == 1.5
        assert data["product"]["recipe"][1]["quantity"] == 2.0
    
    def test_update_simple_product(self, client, mock_product_repo, simple_product):
        """Test updating a simple product."""
        # Arrange
        simple_product.materials[0].material.id = uuid.uuid4() # Ensure it has an ID for checks
        mock_product_repo.get_by_id.return_value = simple_product
        updated = make_simple_product(simple_product.materials[0].material, simple_product.id)
        updated.name = "Updated Name"
        mock_product_repo.save.return_value = updated
        mock_product_repo.get_by_name.return_value = None
        
        payload = {
            "name": "Updated Name",
            "dimensions": {
                "width": {"value": 3.0, "unit": "m"},
                "height": {"value": 4.0, "unit": "m"}
            }
        }
        
        # Act
        response = client.patch(f"/products/{simple_product.id}", json=payload)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        mock_product_repo.save.assert_called_once()
    
    def test_update_product_not_found(self, client, mock_product_repo):
        """Test updating a non-existent product."""
        # Arrange
        product_id = uuid.uuid4()
        mock_product_repo.get_by_id.return_value = None
        
        payload = {"name": "Updated Name"}
        
        # Act
        response = client.patch(f"/products/{product_id}", json=payload)
        
        # Assert
        assert response.status_code == 404
    
    def test_update_price_reflected_in_dto(self, client, mock_product_repo, simple_product, test_user):
        """Verify that updating price via PATCH is returned in the response DTO."""
        # Arrange
        simple_product.materials = [] # Clear material to allow price override
        mock_product_repo.get_by_id.return_value = simple_product

        from app.domain.value_objects.money import Money
        from decimal import Decimal

        updated = SimpleProduct(
            id=simple_product.id,
            name=simple_product.name,
            materials=[],
            purchase_price=Money(amount=Decimal("100.00")),
            sale_price=Money(amount=Decimal("123.45")),
            tenant_id=test_user.tenant_id
        )
        mock_product_repo.save.return_value = updated
        mock_product_repo.get_by_name.return_value = None

        # Fix: price should be a decimal/float, not a dict for ProductUpdateDTO
        payload = {
            "sale_price": 123.45
        }

        # Act
        response = client.patch(f"/products/{simple_product.id}", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        # En ProductDTO, sale_price es un Decimal directo (en el JSON un float o string)
        assert Decimal(str(data["sale_price"])) == Decimal("123.45")
    
    # ============================================================================
    # DELETE PRODUCT TESTS
    # ============================================================================
    
    def test_delete_product_success(self, client, mock_product_repo, simple_product):
        """Test deleting a product."""
        # Arrange
        mock_product_repo.get_by_id.return_value = simple_product
        mock_product_repo.delete.return_value = True
        
        # Act
        response = client.delete(f"/products/{simple_product.id}")
        
        # Assert
        assert response.status_code == 204
        mock_product_repo.delete.assert_called_once_with(simple_product.id)
    
    def test_delete_product_not_found(self, client, mock_product_repo):
        """Test deleting a non-existent product."""
        # Arrange
        product_id = uuid.uuid4()
        mock_product_repo.get_by_id.return_value = None
        mock_product_repo.delete.return_value = False
        
        # Act
        response = client.delete(f"/products/{product_id}")
        
        # Assert
        assert response.status_code == 404
    
    # ============================================================================
    # GET COMPONENTS TESTS
    # ============================================================================
    
    def test_get_composite_product_components(self, client, mock_product_repo, composite_product, simple_product):
        """Test getting components of a composite product."""
        # Arrange
        mock_product_repo.get_by_id.return_value = composite_product
        mock_product_repo.get_components.return_value = [(simple_product, 2)]
        
        # Act
        response = client.get(f"/products/{composite_product.id}/components")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        mock_product_repo.get_components.assert_called_once_with(composite_product.id)
    
    def test_get_simple_product_components(self, client, mock_product_repo, simple_product):
        """Test getting components of a simple product (should be empty)."""
        # Arrange
        mock_product_repo.get_by_id.return_value = simple_product
        
        # Act
        response = client.get(f"/products/{simple_product.id}/components")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["products"]) == 0
    
    def test_get_components_product_not_found(self, client, mock_product_repo):
        """Test getting components of a non-existent product."""
        # Arrange
        product_id = uuid.uuid4()
        mock_product_repo.get_by_id.return_value = None
        
        # Act
        response = client.get(f"/products/{product_id}/components")
        
        # Assert
        assert response.status_code == 404
