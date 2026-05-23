"""
SQLAlchemy model for Client entity.
"""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base, TenantMixin


class ClientModel(Base, TenantMixin):
    """
    SQLAlchemy model for clients table.
    Maps to the domain Client entity.
    """
    __tablename__ = "clients"
    
    # Identification
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    identification_number = Column(String(20), nullable=False, unique=True, index=True)
    document_type = Column(String(10), nullable=False)  # CC, CE, NIT
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(CITEXT, unique=True, nullable=False, index=True)
    phone = Column(String(15), nullable=True)
    address = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    works = relationship("WorkModel", back_populates="client", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ClientModel(id={self.id}, identification='{self.identification_number}', name='{self.first_name} {self.last_name}')>"

