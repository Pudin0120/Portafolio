"""
SQLAlchemy model for MaterialType entity.
"""
from sqlalchemy import Column, String, Text, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base, TenantMixin


class MaterialTypeModel(Base, TenantMixin):
    """
    SQLAlchemy model for material_types table.
    Maps to the domain MaterialType entity.
    
    Each material type has a measurement strategy that determines
    how materials of this type are measured and priced.
    
    Strategies: SHEET, TUBE, LIQUID, SOLID
    """
    __tablename__ = "material_types"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # Identification
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Measurement Strategy
    measurement_strategy = Column(String(50), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship to Material (one material type has many materials)
    materials = relationship("MaterialModel", back_populates="material_type", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        UniqueConstraint('tenant_id', 'name', name='uq_material_type_tenant_name'),
    )
    
    def __repr__(self):
        return f"<MaterialTypeModel(id={self.id}, name='{self.name}', strategy='{self.measurement_strategy}')>"
