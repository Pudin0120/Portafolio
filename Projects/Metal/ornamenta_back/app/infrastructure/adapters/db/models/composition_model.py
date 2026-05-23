"""
SQLAlchemy model for Composition entity.
"""
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .base import Base, TenantMixin


class CompositionModel(Base, TenantMixin):
    """
    SQLAlchemy model for compositions table.
    
    Represents the chemical/physical composition metadata of materials.
    This is METADATA ONLY - pricing is stored in Material table.
    
    Examples: "Acero galvanizado", "Aluminio 6061", "Pintura epoxica"
    """
    __tablename__ = "compositions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # Identification
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<CompositionModel(id={self.id}, name='{self.name}')>"
