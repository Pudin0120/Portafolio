"""
SQLAlchemy model for Role entity.
"""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .base import Base, TenantMixin


class Role(Base, TenantMixin):
    __tablename__ = "roles"
    name = Column(String(20), primary_key=True)
    users = relationship("User", back_populates="role")
