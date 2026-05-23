"""
Domain layer package.

Contiene toda la logica de negocio, entidades, value objects, eventos,
observers, builders, factories y estrategias del sistema.
"""
from app.domain.models.material import Material
from app.domain.models.product import (
    ProductComponent,
    SimpleProduct,
    CompositeProduct
)
from app.domain.models.price_calculation_audit import PriceCalculationAudit
from app.domain.events.material_events import (
    MaterialPriceChanged,
    ProductPriceRecalculated
)
from app.domain.builders.product_builder import ProductBuilder
from app.domain.observers.material_price_observer import (
    MaterialPriceObserver,
    ProductPriceUpdater,
    MaterialPriceSubject
)

__all__ = [
    "Material",
    "ProductComponent",
    "SimpleProduct",
    "CompositeProduct",
    "PriceCalculationAudit",
    "MaterialPriceChanged",
    "ProductPriceRecalculated",
    "ProductBuilder",
    "MaterialPriceObserver",
    "ProductPriceUpdater",
    "MaterialPriceSubject"
]

