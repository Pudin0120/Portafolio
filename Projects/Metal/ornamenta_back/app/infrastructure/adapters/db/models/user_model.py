"""
SQLAlchemy model for User entity.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from .base import Base, TenantMixin
import uuid

if TYPE_CHECKING:
    from .role_model import Role


class User(Base, TenantMixin):
    """
    SQLAlchemy model for users table.
    Maps to the domain User entity.
    """
    __tablename__ = "users"
    
    # Identification
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    firebase_uid: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    document_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    
    # Personal Information
    email: Mapped[str] = mapped_column(CITEXT, unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    
    # Role
    role_name: Mapped[str] = mapped_column(String(20), ForeignKey("roles.name"), nullable=False, index=True)
    
    # Status
    state: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE", index=True)  # ACTIVE, INACTIVE, SUSPENDED
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    role: Mapped["Role"] = relationship("Role", back_populates="users")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role_name}', tenant_id={self.tenant_id})>"
