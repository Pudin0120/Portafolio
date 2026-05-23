
import pytest
import uuid
from decimal import Decimal
from unittest.mock import Mock
from app.application.use_cases.update_product import UpdateProductUseCase
from app.application.dto.product_dto import ProductUpdateDTO, ProductDimensionsDTO, DimensionValueDTO
from app.domain.models.product import SimpleProduct, ProductMaterial
from app.domain.models.material import Material
from app.domain.models.material_type import MaterialType
from app.domain.models.user import User, RoleEnum
from app.domain.value_objects.money import Money
from app.domain.value_objects.document_number import DocumentNumber, DocumentEnum
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateUser, StateEnum

@pytest.fixture
def mock_product_repo():
    return Mock()

@pytest.fixture
def test_user():
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

@pytest.fixture
def material_type():
    return MaterialType(
        id=uuid.uuid4(),
        name="Lamina",
        description="Lamina de prueba",
        measurement_strategy="SHEET"
    )

@pytest.fixture
def material(material_type, test_user):
    return Material(
        id=uuid.uuid4(),
        sku="SKU-123",
        material_type=material_type,
        purchase_price=Money(amount=Decimal("100"), currency="COP"),
        sale_price=Money(amount=Decimal("150"), currency="COP"),
        description="Lamina cal 14",
        properties={"thickness": 14},
        tenant_id=test_user.tenant_id
    )

def test_update_product_regenerates_technical_name(mock_product_repo, test_user, material):
    # Arrange
    product_id = uuid.uuid4()
    original_name = "Mi Ventana - Lamina 1x1m"
    product = SimpleProduct(
        id=product_id,
        name=original_name,
        description="Description original",
        purchase_price=None,
        sale_price=None,
        image_url=None,
        properties={},
        is_deleted=False,
        deleted_at=None,
        tenant_id=test_user.tenant_id,
        materials=[ProductMaterial(material=material, quantity=Decimal("1.0"))],
        dimensions={"width": 1.0, "height": 1.0}
    )
    
    mock_product_repo.get_by_id.return_value = product
    mock_product_repo.get_by_name.return_value = None
    mock_product_repo.save.side_effect = lambda p: p
    
    use_case = UpdateProductUseCase(mock_product_repo)
    
    # Act: Update dimensions
    from app.application.dto.product_dto import ProductDimensionsDTO, DimensionValueDTO
    update_data = ProductUpdateDTO(
        dimensions=ProductDimensionsDTO(
            width=DimensionValueDTO(value=2.0, unit="m"),
            height=DimensionValueDTO(value=1.5, unit="m")
        )
    )
    
    result = use_case.execute(product_id, update_data, test_user)
    
    # Assert
    assert result.name == "Mi Ventana - Lamina 2mx1.5m"

def test_update_product_regenerates_technical_name_with_multiple_materials(mock_product_repo, test_user, material):
    # Arrange
    product_id = uuid.uuid4()
    
    # Second material (e.g. glass)
    glass_type = MaterialType(id=uuid.uuid4(), name="Vidrio", measurement_strategy="SHEET")
    glass_material = Material(
        id=uuid.uuid4(),
        sku="SKU-GLASS",
        material_type=glass_type,
        purchase_price=Money(amount=Decimal("200")),
        description="Vidrio templado",
        tenant_id=test_user.tenant_id
    )
    
    original_name = "Puerta - Lamina 1x1m"
    product = SimpleProduct(
        id=product_id,
        name=original_name,
        description="Description original",
        purchase_price=None,
        sale_price=None,
        image_url=None,
        properties={},
        is_deleted=False,
        deleted_at=None,
        tenant_id=test_user.tenant_id,
        materials=[
            ProductMaterial(material=material, quantity=Decimal("1.0")),
            ProductMaterial(material=glass_material, quantity=Decimal("1.0"))
        ],
        dimensions={"width": 1.0, "height": 1.0}
    )
    
    mock_product_repo.get_by_id.return_value = product
    mock_product_repo.get_by_name.return_value = None
    mock_product_repo.save.side_effect = lambda p: p
    
    use_case = UpdateProductUseCase(mock_product_repo)
    
    # Act
    update_data = ProductUpdateDTO(
        dimensions=ProductDimensionsDTO(
            width=DimensionValueDTO(value=1.2, unit="m"),
            height=DimensionValueDTO(value=2.0, unit="m")
        )
    )
    
    result = use_case.execute(product_id, update_data, test_user)
    
    # Assert
    assert result.name == "Puerta - Lamina 1.2x2m"

