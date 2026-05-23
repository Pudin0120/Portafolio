from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey, func
from sqlalchemy.sql import func
import uuid

class Base(DeclarativeBase):
    """Base class for all models using SQLAlchemy 2.0 Mapped style."""
    pass

class TenantMixin:
    """Mixin to add tenant isolation to models."""
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, 
        index=True
    )
