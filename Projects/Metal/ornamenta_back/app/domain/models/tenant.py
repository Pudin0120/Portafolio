from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime
from typing import Optional

@dataclass
class Tenant:
    """Domain model for a Tenant (Company/Client)."""
    id: UUID
    name: str
    slug: str  # For subdomains or identification
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def deactivate(self):
        self.is_active = False
        self.updated_at = datetime.now()

    def activate(self):
        self.is_active = True
        self.updated_at = datetime.now()
