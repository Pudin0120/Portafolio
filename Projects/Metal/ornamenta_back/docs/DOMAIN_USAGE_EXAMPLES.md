# Ejemplos de Uso del Dominio

Este document proporciona ejemplos practicos de como usar los nuevos componentes de dominio y aplicacion implementados.

---

## 1. Create Simple Product con ProductBuilder

```python
from app.domain.builders.product_builder import ProductBuilder
from app.domain.repositories.material_repository import MaterialRepository
from app.domain.strategies.strategy_registry import MeasurementStrategyRegistry
from uuid import UUID

# Obtener material del repositorio
material_repo = container.material_repository()
material = material_repo.get_by_id(UUID("123e4567-e89b-12d3-a456-426614174000"))

# Obtener estrategia de measurement
unit_repo = container.unit_of_measure_repo()
strategy_registry = MeasurementStrategyRegistry(unit_repo)
strategy = strategy_registry.get_strategy("SHEET")

# Construir product con ProductBuilder
builder = ProductBuilder()
product = (builder
    .with_material(material)
    .with_name("Lamina lateral izquierda")
    .with_description("Corte personalizado para porton industrial")
    .with_dimensions_dict({
        "width": {"value": 1.0, "unit": "m"},
        "height": {"value": 2.5, "unit": "m"}
    })
    .with_strategy(strategy)
    .build()
)

print(f"Product: {product.name}")
print(f"Price calculado: {product.get_total_price()}")
print(f"Quantity multiplier: {product.quantity_multiplier}")  # 2.5 m
```

---

## 2. Actualizar Price de Material y Propagar a Products

```python
from app.application.services.material_price_service import MaterialPriceUpdateService
from decimal import Decimal
from uuid import UUID

# Obtener servicios del container
material_repo = container.material_repository()
product_repo = container.product_repository()

# Create servicio
price_service = MaterialPriceUpdateService(material_repo, product_repo)

# User manager (debe tener rol MANAGER)
manager_user = user_repo.get_by_id(UUID("user-manager-001"))

# Actualizar price
result = price_service.update_material_price(
    material_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
    new_price_amount=Decimal("105000"),
    user=manager_user,
    currency="COP",
    reason="Ajuste por inflacion trimestral Q4 2025"
)

print(f" Material actualizado: {result['material']['name']}")
print(f"  Price anterior: ${result['material']['old_price']:,.2f}")
print(f"  Price nuevo: ${result['material']['new_price']:,.2f}")
print(f"  Cambio: {result['material']['price_change_percent']:.2f}%")
print(f"\n Products afectados: {result['impact']['products_affected']}")
print(f" Cambio total en precios: ${result['impact']['total_price_change']:,.2f}")
print(f" Eventos generados: {result['impact']['events_generated']}")

# Registros de auditoria
for audit in result['audit_records']:
    print(f"\nAuditoria: {audit['calculation_id']}")
    print(f"  Product: {audit['product_name']}")
    print(f"  Price: {audit['calculated_price_amount']} {audit['calculated_price_currency']}")
```

---

## 3. Create Simple Product desde Servicio de Aplicacion

```python
from app.application.services.product_creation_service import ProductCreationService
from uuid import UUID

# Create servicio
creation_service = ProductCreationService(
    material_repository=material_repo,
    product_repository=product_repo,
    unit_repository=unit_repo
)

# User manager
manager_user = user_repo.get_by_id(UUID("user-manager-001"))

# Create product con material
result = creation_service.create_simple_product_from_material(
    material_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
    dimensions={
        "width": {"value": 1.0, "unit": "m"},
        "length": {"value": 2.0, "unit": "m"}
    },
    user=manager_user,
    name="Lamina cortada 1x2",
    description="Corte estandar para puertas"
)

print(f" Product creado: {result['product']['name']}")
print(f"  ID: {result['product']['id']}")
print(f"  Price: ${result['product']['price']['amount']:,.2f}")
print(f"  Quantity computada: {result['product']['computed_quantity']['value']} {result['product']['computed_quantity']['unit']}")

# Auditoria
audit = result['audit']
print(f"\n Auditoria: {audit['calculation_id']}")
print(f"  Tipo: {audit['calculation_type']}")
print(f"  Fecha: {audit['calculated_at']}")
```

---

## 4. Create Product sin Material (Servicio)

```python
from app.domain.value_objects.money import Money
from decimal import Decimal

# Create servicio/product sin material
result = creation_service.create_simple_product_without_material(
    name="Instalacion de porton industrial",
    price=Money(amount=Decimal("500000"), currency="COP"),
    user=manager_user,
    description="Servicio de instalacion profesional incluye transporte y mano de obra"
)

print(f" Servicio creado: {result['product']['name']}")
print(f"  Price fijo: ${result['product']['price']['amount']:,.2f}")
```

---

## 5. Create Composite Product

```python
from app.application.services.composite_product_service import CompositeProductService

# Create servicio
composite_service = CompositeProductService(product_repository=product_repo)

# Create product compuesto
result = composite_service.create_composite_product(
    name="Caja metalica simple",
    description="Caja hecha con 4 laminas 1x1m",
    components=[
        {"product_id": "prod-std-1m2", "quantity": 4}
    ],
    user=manager_user
)

print(f" Product compuesto creado: {result['product']['name']}")
print(f"  Price total: ${result['product']['price']['amount']:,.2f}")
print(f"  Componentes: {len(result['product']['components'])}")

# Breakdown de precios
for comp in result['product']['price_breakdown']:
    print(f"    - {comp['quantity']}x ${comp['unit_price']:,.2f} = ${comp['subtotal']:,.2f}")
```

---

## 6. Agregar Componente a Product Compuesto

```python
from uuid import UUID

# Agregar nuevo componente
result = composite_service.add_component_to_composite(
    composite_id=UUID("box-0001"),
    component_product_id=UUID("prod-chapa"),
    quantity=1,
    user=manager_user
)

print(f" Componente agregado a: {result['product']['name']}")
print(f"  Price anterior: ${result['price_change']['old_amount']:,.2f}")
print(f"  Price nuevo: ${result['price_change']['new_amount']:,.2f}")
print(f"  Diferencia: ${result['price_change']['difference']:,.2f}")
```

---

## 7. Obtener Breakdown Detallado de Price

```python
result = composite_service.get_price_breakdown(
    composite_id=UUID("box-0001")
)

print(f"Product compuesto: {result['composite_name']}")
print(f"Price total: ${result['total_price']:,.2f} {result['currency']}")
print(f"\nDesglose por componente:")

for item in result['breakdown']:
    print(f"  [{item['component_type']}] {item['component_name']}")
    print(f"    {item['quantity']}x ${item['unit_price']:,.2f} = ${item['subtotal']:,.2f} ({item['percentage']:.1f}%)")
```

---

## 8. Usar ProductFactory con Builder

```python
from app.application.services.product_factory_service import ProductFactoryService

# Create product usando factory con builder (validacion completa)
product = ProductFactoryService.create_product_with_builder(
    material=steel_material,
    dimensions={
        "width": {"value": 80, "unit": "cm"},  # pint convierte automaticamente
        "height": {"value": 200, "unit": "cm"}
    },
    strategy=sheet_strategy,
    name="Marco de puerta lateral"
)

print(f" Product creado con factory+builder")
print(f"  Dimensiones normalizadas: {product.dimensions}")  # En metros
print(f"  Price: {product.get_total_price()}")
```

---

## 9. Observer Pattern en Accion

```python
from app.domain.observers.material_price_observer import (
    MaterialPriceSubject,
    ProductPriceUpdater
)
from app.domain.events.material_events import MaterialPriceChanged
from datetime import datetime

# Setup del Observer
subject = MaterialPriceSubject()
updater = ProductPriceUpdater(product_repo)
subject.attach(updater)

# Create evento de cambio de price
event = MaterialPriceChanged(
    event_id=uuid4(),
    occurred_at=datetime.now(),
    aggregate_id=material.id,
    material_id=material.id,
    material_name=material.name,
    old_price_amount=Decimal("100000"),
    new_price_amount=Decimal("105000"),
    currency="COP",
    changed_by_user_id=manager_user.id,
    changed_by_user_name=f"{manager_user.name} ({manager_user.role})",
    reason="Ajuste inflacion"
)

# Notificar observers
result = subject.notify(event)

print(f" Notificacion enviada a {subject.get_observers_count()} observers")
print(f" Products afectados: {result['products_affected']}")
print(f" Eventos generados: {len(result['product_events'])}")

# Obtener registros de auditoria
audits = updater.get_audit_records()
print(f" Registros de auditoria: {len(audits)}")
```

---

## 10. Validacion de Roles

```python
from app.application.services.material_price_service import MaterialPriceUpdateService

# User sin permisos
employee_user = user_repo.get_by_email("employee@example.com")
assert employee_user.role == "EMPLOYEE"

# Intento de actualizar price (debe fallar)
try:
    result = price_service.update_material_price(
        material_id=material.id,
        new_price_amount=Decimal("110000"),
        user=employee_user,  # ERROR No es MANAGER
        currency="COP"
    )
except PermissionError as e:
    print(f"ERROR Permiso denegado: {e}")
    # Output: "Solo users con rol MANAGER o SUPER_ADMIN pueden actualizar precios..."

# Con manager funciona
manager_user = user_repo.get_by_email("manager@example.com")
assert manager_user.role == "MANAGER"

result = price_service.update_material_price(
    material_id=material.id,
    new_price_amount=Decimal("110000"),
    user=manager_user,  #  Es MANAGER
    currency="COP"
)
print(f" Price actualizado correctamente por {manager_user.name}")
```

---

## Notas de Integracion

- **Todos los ejemplos asumen** que los repositorios estan correctamente inyectados por el container de DI.
- **Las operaciones administrativas** (create products, cambiar precios) requieren rol `MANAGER` o `SUPER_ADMIN`.
- **Los precios de products** se calculan dinamicamente desde el material, excepto si tienen `price_override`.
- **La normalizacion con pint** es automatica en ProductBuilder (convierte cm  m, mm  m, etc.).
- **Los eventos de dominio** se pueden integrar con un event bus para publicar a otros sistemas.

