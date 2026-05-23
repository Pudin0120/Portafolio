"""
Observers package - Patron Observer para notificacion de cambios en el dominio.

Los observers permiten que objetos se suscriban a cambios en otros objetos
y reaccionen automaticamente cuando ocurren dichos cambios.
"""
from app.domain.observers.material_price_observer import (
    MaterialPriceObserver,
    ProductPriceUpdater,
    MaterialPriceSubject
)

__all__ = [
    "MaterialPriceObserver",
    "ProductPriceUpdater",
    "MaterialPriceSubject"
]

