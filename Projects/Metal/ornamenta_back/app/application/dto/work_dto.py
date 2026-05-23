"""
DTOs para Work.
"""
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.application.dto.product_work_item_dto import ProductWorkItemDTO
from app.application.dto.task_dto import TaskDTO


class WorkCreateDTO(BaseModel):
    """DTO para create un nuevo work en estado DRAFT."""
    
    client_identification: str = Field(
        ..., 
        min_length=5, 
        max_length=20, 
        description="Identificacion del client (cedula, NIT, pasaporte). Rango: 5-20 caracteres. Ejemplo: '1002309888'"
    )
    work_name: str = Field(
        ..., 
        min_length=3, 
        max_length=255, 
        description="Nombre o titulo del work. Rango: 3-255 caracteres. Ejemplo: 'Pintura de puertas en la casa de don timoteo.'"
    )
    description: Optional[str] = Field(
        None, 
        max_length=2000, 
        description="Description detallada del work con especificaciones y requerimientos. Maximo: 2000 caracteres. Ejemplo: 'pintura de la ornamentacion de la casa de don timoteo'"
    )
    tax: float = Field(
        0.0, 
        ge=0.0, 
        le=1.0, 
        description="Porcentaje de ganancia/utilidad del taller. Rango: 0.0 a 1.0 (0% a 100%). Ejemplo: 0.15 = 15%. Valor por defecto: 0.0"
    )
    end_aprox_delivery_date: Optional[datetime] = Field(
        None, 
        description="Fecha y hora aproximada de entrega. Formato ISO 8601 COMPLETO: '2025-11-21T10:37:00Z' o '2025-11-21T10:37:00+00:00'.  Debe incluir segundos y zona horaria. Error 422 si envias solo '2025-11-21T10:37'"
    )
    deposit_amount: Optional[Decimal] = Field(
        Decimal("0"), 
        ge=0, 
        description="Monto del deposito o anticipo inicial (en COP). Debe ser  0. Ejemplo: 200000. Valor por defecto: 0"
    )


class WorkSummaryDTO(BaseModel):
    """DTO de resumen de work (sin products ni tasks)."""
    
    work_id: UUID
    client_identification: str
    work_name: str
    description: Optional[str]
    state: str
    tax: float
    start_date: datetime
    end_aprox_delivery_date: Optional[datetime]
    end_delivery_date: Optional[datetime]
    deposit_amount: Decimal
    deposit_currency: str
    completion_percentage: float
    
    model_config = ConfigDict(from_attributes=True)


class WorkDTO(BaseModel):
    """DTO completo de work con products y tasks."""
    
    work_id: UUID
    client_identification: str
    work_name: str
    description: Optional[str]
    state: str
    tax: float
    start_date: datetime
    end_aprox_delivery_date: Optional[datetime]
    end_delivery_date: Optional[datetime]
    deposit_amount: Decimal
    deposit_currency: str
    
    # Calculated fields
    completion_percentage: float
    products_value: Optional[Decimal] = None  # Disponible despues de cotizar
    work_value: Optional[Decimal] = None  # Disponible despues de cotizar
    
    # Relationships
    products: List[ProductWorkItemDTO] = Field(default_factory=list)
    tasks: List[TaskDTO] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


class WorkListDTO(BaseModel):
    """DTO para lista de works."""
    
    works: List[WorkSummaryDTO]
    total: int


class CompletionDTO(BaseModel):
    """DTO para porcentaje de completitud de un work."""
    
    work_id: UUID
    work_name: str
    state: str
    completion_percentage: float
    total_tasks: int
    finished_tasks: int
    pending_tasks: int

