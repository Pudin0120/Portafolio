"""
Builders package - Patron Builder para construccion controlada de objetos de dominio.

Los builders proporcionan una interfaz fluida para create objetos complejos
con validacion y normalizacion completas.
"""
from app.domain.builders.product_builder import ProductBuilder

__all__ = ["ProductBuilder"]

