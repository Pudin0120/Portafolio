
import pytest
import uuid
from decimal import Decimal
from datetime import datetime
from app.domain.models.material import Material
from app.domain.models.material_type import MaterialType
from app.domain.models.product import SimpleProduct, CompositeProduct
from app.domain.value_objects.money import Money
from app.application.mappers.material_mapper import MaterialMapper
from app.application.services.inventory_service import InventoryService
from app.infrastructure.adapters.repositories.postgres_material_repository import PostgresMaterialRepository
from app.infrastructure.adapters.repositories.postgres_product_repository import PostgresProductRepository
from app.infrastructure.adapters.repositories.postgres_inventory_repository import PostgresInventoryRepository
from app.infrastructure.adapters.repositories.postgres_material_type_repository import PostgresMaterialTypeRepository
from app.domain.observers.material_price_observer import MaterialPriceSubject, ProductPriceUpdater
from app.infrastructure.adapters.db.models.tenant_model import TenantModel

@pytest.fixture
def tenant_id(db_session):
    tenant = TenantModel(
        id=uuid.uuid4(),
        name="Test Tenant",
        slug=f"test-tenant-{uuid.uuid4().hex[:6]}"
    )
    db_session.add(tenant)
    db_session.flush()
    return tenant.id

@pytest.fixture
def material_type(db_session, tenant_id):
    repo = PostgresMaterialTypeRepository(db_session)
    m_type = MaterialType(
        id=uuid.uuid4(),
        name="Lamina",
        measurement_strategy="SHEET",
        tenant_id=tenant_id
    )
    # The domain model doesn't have a save method, we use the repo
    # But for integration tests, let's use the repo implementation
    from app.infrastructure.adapters.db.models.material_type_model import MaterialTypeModel
    model = MaterialTypeModel(
        id=m_type.id,
        name=m_type.name,
        measurement_strategy=m_type.measurement_strategy,
        tenant_id=tenant_id
    )
    db_session.add(model)
    db_session.flush()
    return m_type

@pytest.fixture
def material_repo(db_session, mock_unit_repo):
    return PostgresMaterialRepository(db_session, unit_repo=mock_unit_repo)

@pytest.fixture
def product_repo(db_session, mock_unit_repo):
    return PostgresProductRepository(db_session, unit_repo=mock_unit_repo)

@pytest.fixture
def inventory_repo(db_session):
    return PostgresInventoryRepository(db_session)

@pytest.fixture
def price_subject(product_repo):
    subject = MaterialPriceSubject()
    updater = ProductPriceUpdater(product_repo)
    subject.attach(updater)
    return subject

@pytest.fixture
def inventory_service(inventory_repo, material_repo, price_subject):
    return InventoryService(inventory_repo, material_repo, price_subject)

def test_material_inventory_integration_flow(
    db_session, 
    tenant_id, 
    material_type, 
    material_repo, 
    product_repo, 
    inventory_service,
    price_subject
):
    # 1. Creation de Material
    material = Material(
        id=uuid.uuid4(),
        material_type=material_type,
        sku="LAM-AC-001",
        # name is a property, not an init field
        purchase_price=Money(amount=Decimal("100.00")),
        sale_price=Money(amount=Decimal("150.00")),
        tenant_id=tenant_id,
        properties={"thickness": 2.0}
    )
    
    saved_material = material_repo.save(material)
    db_session.flush()
    
    # Validar persistencia y defaults
    assert saved_material.purchase_price.amount == Decimal("100.00")
    assert saved_material.sale_price.amount == Decimal("150.00")
    assert saved_material.is_deleted is False
    
    # Validar con Mapper
    dto = MaterialMapper.to_dto(saved_material)
    assert dto.purchase_price_amount == Decimal("100.00")
    assert dto.sale_price_amount == Decimal("150.00")

    # 2. Integracion con Inventario (Entrada)
    inventory_service.register_movement(
        material_id=saved_material.id,
        quantity=Decimal("10.0"),
        movement_type="PURCHASE",
        tenant_id=tenant_id,
        reason="Compra inicial"
    )
    db_session.flush()
    
    level = inventory_service.inventory_repo.get_level(saved_material.id, tenant_id)
    assert level is not None
    assert level.quantity == Decimal("10.0")

    # 3. Costo de Product (Dual Pricing)
    # Creamos un product que usa 2 unidades de este material
    from app.domain.models.product import ProductMaterial
    product = SimpleProduct(
        id=uuid.uuid4(),
        name="Panel de Acero",
        materials=[ProductMaterial(material=saved_material, quantity=Decimal("2.0"))],
        tenant_id=tenant_id
    )
    saved_product = product_repo.save(product)
    db_session.flush()

    # Verificar precios calculados (Dual Pricing)
    # purchase_price = 100 * 2 = 200
    assert saved_product.get_total_purchase_price().amount == Decimal("200.00")
    # sale_price = 150 * 2 = 300
    assert saved_product.get_total_sale_price().amount == Decimal("300.00")

    # 4. Observer de Precios
    # Actualizar price de compra del material a 120.00
    user_id = uuid.uuid4()
    inventory_service.update_material_prices(
        material_id=saved_material.id,
        user_id=user_id,
        purchase_price=Decimal("120.00"),
        reason="Aumento de proveedor"
    )
    db_session.flush()

    # Recargar product para validar actualizacion via Observer
    updated_product = product_repo.get_by_id(saved_product.id)
    # nuevo purchase_price = 120 * 2 = 240
    assert updated_product.get_total_purchase_price().amount == Decimal("240.00")
    # el sale_price del material no cambio, sigue siendo 150 * 2 = 300
    assert updated_product.get_total_sale_price().amount == Decimal("300.00")

    # 5. Ciclo de Vida (Soft Delete)
    # Intentar borrar con stock active (debe fallar)
    with pytest.raises(ValueError, match="Cannot delete material with active stock"):
        inventory_service.delete_material(saved_material.id, tenant_id)

    # Registrar salida para dejar stock en cero
    inventory_service.register_movement(
        material_id=saved_material.id,
        quantity=Decimal("-10.0"),
        movement_type="SALE",
        tenant_id=tenant_id,
        reason="Venta total para vaciar stock"
    )
    db_session.flush()

    # Ahora si borrar
    inventory_service.delete_material(saved_material.id, tenant_id)
    db_session.flush()

    # Validar Soft Delete
    deleted_material = material_repo.get_by_id(saved_material.id)
    assert deleted_material.is_deleted is True
    assert deleted_material.deleted_at is not None

    # Validar que no aparece en consultas normales
    all_materials = material_repo.get_all(tenant_id)
    assert not any(m.id == saved_material.id for m in all_materials), "Material borrado no deberia aparecer en get_all"

def test_composite_product_price_propagation(
    db_session,
    tenant_id,
    material_type,
    material_repo,
    product_repo,
    inventory_service
):
    # 1. Create Material Base
    material = Material(
        id=uuid.uuid4(),
        material_type=material_type,
        sku="MAT-BASE-01",
        purchase_price=Money(amount=Decimal("10.00")),
        sale_price=Money(amount=Decimal("20.00")),
        tenant_id=tenant_id
    )
    material_repo.save(material)
    db_session.flush()

    # 2. Create SimpleProduct (Hijo 1) - usa 5 unidades de material
    from app.domain.models.product import ProductMaterial
    child1 = SimpleProduct(
        id=uuid.uuid4(),
        name="Componente A",
        materials=[ProductMaterial(material=material, quantity=Decimal("5.0"))],
        tenant_id=tenant_id
    )
    product_repo.save(child1)

    # 3. Create otro SimpleProduct (Hijo 2) - usa 2 unidades de material
    child2 = SimpleProduct(
        id=uuid.uuid4(),
        name="Componente B",
        materials=[ProductMaterial(material=material, quantity=Decimal("2.0"))],
        tenant_id=tenant_id
    )
    product_repo.save(child2)
    db_session.flush()

    # 4. Create CompositeProduct (Padre) - compuesto de 1 child1 y 3 child2
    parent = CompositeProduct(
        id=uuid.uuid4(),
        name="Product Final",
        tenant_id=tenant_id
    )
    parent.add_component(child1, quantity=1)
    parent.add_component(child2, quantity=3)
    product_repo.save(parent)
    db_session.flush()

    # Calcular costo esperado:
    # Child 1: 10 * 5 = 50
    # Child 2: 10 * 2 = 20
    # Parent: (50 * 1) + (20 * 3) = 50 + 60 = 110
    assert parent.get_total_purchase_price().amount == Decimal("110.00")

    # 5. Actualizar price del Material y ver propagacion
    # El Observer deberia actualizar child1 y child2 en la DB.
    # El Parent, al recargarse, deberia reflejar el nuevo costo de sus componentes.
    inventory_service.update_material_prices(
        material_id=material.id,
        user_id=uuid.uuid4(),
        purchase_price=Decimal("20.00"), # Doblamos el price
        reason="Update for composite test"
    )
    db_session.flush()

    # Recargar y verificar
    # Child 1 ahora deberia costar: 20 * 5 = 100
    # Child 2 ahora deberia costar: 20 * 2 = 40
    # Parent ahora deberia costar: (100 * 1) + (40 * 3) = 100 + 120 = 220
    
    updated_parent = product_repo.get_by_id(parent.id)
    assert updated_parent.get_total_purchase_price().amount == Decimal("220.00")
    
    # Verificar que los hijos tambien se actualizaron en DB
    updated_child1 = product_repo.get_by_id(child1.id)
    assert updated_child1.get_total_purchase_price().amount == Decimal("100.00")
