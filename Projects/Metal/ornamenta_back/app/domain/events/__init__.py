"""
Domain events package.

Eventos de dominio para notificacion de cambios importantes en el sistema.
"""
from app.domain.events.material_events import (
    MaterialPriceChanged,
    ProductPriceRecalculated
)
from app.domain.events.user_events import UserStateChanged
from app.domain.events.payroll_events import *

__all__ = [
    "MaterialPriceChanged",
    "ProductPriceRecalculated",
    "UserStateChanged"
]
