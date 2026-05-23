"""
Product Work Item Value Object.

Value object que representa un product dentro de un work,
incluyendo quantity, orden de ejecucion, estado y snapshot de price.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
import uuid

from app.domain.value_objects.product_snapshot import ProductSnapshot


class ProductItemState(str, Enum):
    """
    Estado de completitud de un product dentro de un work.
    
    - PENDING: Product aun no iniciado
    - IN_PROGRESS: Product en ejecucion (al menos una task iniciada)
    - COMPLETED: Todas las tasks del product completadas
    """
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


@dataclass
class ProductWorkItem:
    """
    Value object que representa un product dentro de un work.
    
    Este objeto evoluciono de ProductByWork para incluir:
    - Snapshot de price congelado (inmutable despues de cotizar)
    - Orden de ejecucion dentro del work
    - Estado de completitud del product
    - Lista de IDs de tasks generadas para este product
    
    Attributes:
        product_id: ID del product original
        work_id: ID del work al que pertenece
        quantity: Quantity de este product en el work
        execution_order: Orden de ejecucion (definido por SUPERVISOR/MANAGER)
        state: Estado de completitud del product
        snapshot: Snapshot congelado del price y composicion (None si no cotizado)
        task_ids: Lista de IDs de tasks generadas para este product
    """
    
    product_id: uuid.UUID
    work_id: uuid.UUID
    quantity: int
    execution_order: int
    state: ProductItemState = ProductItemState.PENDING
    snapshot: Optional[ProductSnapshot] = None
    task_ids: List[uuid.UUID] = field(default_factory=list)
    
    def __post_init__(self):
        """Validaciones post-inicializacion."""
        if self.quantity <= 0:
            raise ValueError("La quantity debe ser mayor a 0")
        
        if self.execution_order < 0:
            raise ValueError("El orden de ejecucion no puede ser negativo")
    
    def is_pending(self) -> bool:
        """Verifica si el product esta pending."""
        return self.state == ProductItemState.PENDING
    
    def is_in_progress(self) -> bool:
        """Verifica si el product esta en progreso."""
        return self.state == ProductItemState.IN_PROGRESS
    
    def is_completed(self) -> bool:
        """Verifica si el product esta completed."""
        return self.state == ProductItemState.COMPLETED
    
    def has_snapshot(self) -> bool:
        """Verifica si el product tiene un snapshot de price."""
        return self.snapshot is not None
    
    def get_frozen_price(self):
        """
        Retorna el price congelado del snapshot.
        
        Raises:
            ValueError: Si no hay snapshot disponible
        """
        if not self.has_snapshot():
            raise ValueError("Este product no tiene un snapshot de price")
        return self.snapshot.get_price()
    
    def freeze_snapshot(self, snapshot: ProductSnapshot) -> None:
        """
        Congela el snapshot de price y composicion.
        
        Args:
            snapshot: Snapshot del product a congelar
            
        Raises:
            ValueError: Si ya existe un snapshot congelado
        """
        if self.has_snapshot():
            raise ValueError("El snapshot ya esta congelado y no puede modificarse")
        
        if snapshot.product_id != self.product_id:
            raise ValueError("El snapshot debe corresponder al mismo product")
        
        self.snapshot = snapshot
    
    def add_task_id(self, task_id: uuid.UUID) -> None:
        """Agrega un ID de task generada para este product."""
        if task_id not in self.task_ids:
            self.task_ids.append(task_id)
    
    def start_progress(self) -> None:
        """Marca el product como en progreso."""
        if not self.is_pending():
            raise ValueError("Solo se puede iniciar un product en estado PENDING")
        self.state = ProductItemState.IN_PROGRESS
    
    def mark_completed(self) -> None:
        """Marca el product como completed."""
        if not self.is_in_progress():
            raise ValueError("Solo se puede completar un product en estado IN_PROGRESS")
        self.state = ProductItemState.COMPLETED
    
    def calculate_completion_percentage(self, finished_task_ids: List[uuid.UUID]) -> float:
        """
        Calcula el porcentaje de completitud basado en tasks finalizadas.
        
        Args:
            finished_task_ids: Lista de IDs de tasks que estan finalizadas
            
        Returns:
            Porcentaje de completitud (0-100)
        """
        if not self.task_ids:
            return 0.0
        
        finished_count = sum(1 for task_id in self.task_ids if task_id in finished_task_ids)
        return (finished_count / len(self.task_ids)) * 100
    
    def __str__(self) -> str:
        return f"ProductWorkItem[{self.product_id}] x{self.quantity} - Order:{self.execution_order} - {self.state.value}"

