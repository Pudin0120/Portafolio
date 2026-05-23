"""
Work State Pattern Implementation.

Implementa el patron State para manejar los estados del work
y sus transiciones de forma robusta y extensible.

Flujo de estados:
DRAFT  QUOTED  IN_PROGRESS  DELIVERED
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.models.work import Work


class WorkStateEnum(str, Enum):
    """
    Enumeracion de estados de work.
    
    - DRAFT: Borrador, se pueden agregar/delete products libremente
    - QUOTED: Cotizado, precios congelados, aun se pueden agregar products
    - IN_PROGRESS: En proceso, tasks generadas y asignadas
    - DELIVERED: Entregado, work finalizado
    """
    DRAFT = "DRAFT"
    QUOTED = "QUOTED"
    IN_PROGRESS = "IN_PROGRESS"
    DELIVERED = "DELIVERED"


class WorkState(ABC):
    """
    Clase abstracta base para estados de work (State Pattern).
    
    Cada estado concreto implementa su propia logica de:
    - Validacion de operaciones permitidas
    - Transiciones a otros estados
    - Comportamiento especifico del estado
    """
    
    @abstractmethod
    def get_state_name(self) -> WorkStateEnum:
        """Retorna el nombre del estado."""
        pass
    
    @abstractmethod
    def can_add_products(self) -> bool:
        """Verifica si se pueden agregar products en este estado."""
        pass
    
    @abstractmethod
    def can_remove_products(self) -> bool:
        """Verifica si se pueden delete products en este estado."""
        pass
    
    @abstractmethod
    def can_edit_product_order(self) -> bool:
        """Verifica si se puede edit el orden de products."""
        pass
    
    @abstractmethod
    def can_quote(self) -> bool:
        """Verifica si se puede cotizar desde este estado."""
        pass
    
    @abstractmethod
    def can_start_work(self) -> bool:
        """Verifica si se puede iniciar el work desde este estado."""
        pass
    
    @abstractmethod
    def can_deliver(self) -> bool:
        """Verifica si se puede entregar desde este estado."""
        pass
    
    @abstractmethod
    def quote(self, work: 'Work') -> 'WorkState':
        """Transicion a estado QUOTED."""
        pass
    
    @abstractmethod
    def start_work(self, work: 'Work') -> 'WorkState':
        """Transicion a estado IN_PROGRESS."""
        pass
    
    @abstractmethod
    def deliver(self, work: 'Work') -> 'WorkState':
        """Transicion a estado DELIVERED."""
        pass
    
    def __str__(self) -> str:
        return self.get_state_name().value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, WorkState):
            return self.get_state_name() == other.get_state_name()
        return False
    
    def __hash__(self) -> int:
        return hash(self.get_state_name())


class DraftState(WorkState):
    """
    Estado DRAFT (Borrador).
    
    En este estado:
    - Se pueden agregar/delete products libremente
    - No hay precios congelados
    - No hay tasks generadas
    - Se puede cotizar para pasar a QUOTED
    """
    
    def get_state_name(self) -> WorkStateEnum:
        return WorkStateEnum.DRAFT
    
    def can_add_products(self) -> bool:
        return True
    
    def can_remove_products(self) -> bool:
        return True
    
    def can_edit_product_order(self) -> bool:
        return True
    
    def can_quote(self) -> bool:
        return True
    
    def can_start_work(self) -> bool:
        return False
    
    def can_deliver(self) -> bool:
        return False
    
    def quote(self, work: 'Work') -> WorkState:
        """Transicion de DRAFT  QUOTED."""
        # La logica de congelar precios se maneja en Work.quote()
        return QuotedState()
    
    def start_work(self, work: 'Work') -> WorkState:
        raise ValueError("No se puede iniciar un work desde estado DRAFT. Primero debe cotizarse.")
    
    def deliver(self, work: 'Work') -> WorkState:
        raise ValueError("No se puede entregar un work desde estado DRAFT.")


class QuotedState(WorkState):
    """
    Estado QUOTED (Cotizado).
    
    En este estado:
    - Precios estan congelados (snapshot)
    - AUN se pueden agregar/delete products (cada nuevo product se congela al agregarse)
    - No se pueden edit snapshots existentes
    - Se puede iniciar el work para pasar a IN_PROGRESS
    """
    
    def get_state_name(self) -> WorkStateEnum:
        return WorkStateEnum.QUOTED
    
    def can_add_products(self) -> bool:
        return True
    
    def can_remove_products(self) -> bool:
        return True
    
    def can_edit_product_order(self) -> bool:
        return True
    
    def can_quote(self) -> bool:
        return False  # Ya esta cotizado
    
    def can_start_work(self) -> bool:
        return True
    
    def can_deliver(self) -> bool:
        return False
    
    def quote(self, work: 'Work') -> WorkState:
        raise ValueError("El work ya esta cotizado.")
    
    def start_work(self, work: 'Work') -> WorkState:
        """Transicion de QUOTED  IN_PROGRESS."""
        # La logica de generar tasks se maneja en Work.start_work()
        return InProgressState()
    
    def deliver(self, work: 'Work') -> WorkState:
        raise ValueError("No se puede entregar un work cotizado que no ha iniciado.")


class InProgressState(WorkState):
    """
    Estado IN_PROGRESS (En Proceso).
    
    En este estado:
    - Tasks generadas y asignadas a empleados
    - Ya NO se pueden agregar/delete products (work en ejecucion)
    - Empleados ejecutan tasks
    - Se puede entregar cuando todas las tasks esten finalizadas
    """
    
    def get_state_name(self) -> WorkStateEnum:
        return WorkStateEnum.IN_PROGRESS
    
    def can_add_products(self) -> bool:
        return False  # Work ya iniciado
    
    def can_remove_products(self) -> bool:
        return False  # Work ya iniciado
    
    def can_edit_product_order(self) -> bool:
        return False
    
    def can_quote(self) -> bool:
        return False
    
    def can_start_work(self) -> bool:
        return False  # Ya esta en progreso
    
    def can_deliver(self) -> bool:
        return True
    
    def quote(self, work: 'Work') -> WorkState:
        raise ValueError("No se puede cotizar un work que ya esta en progreso.")
    
    def start_work(self, work: 'Work') -> WorkState:
        raise ValueError("El work ya esta en progreso.")
    
    def deliver(self, work: 'Work') -> WorkState:
        """Transicion de IN_PROGRESS  DELIVERED."""
        # Validacion de que todas las tasks esten finalizadas se hace en Work.deliver()
        return DeliveredState()


class DeliveredState(WorkState):
    """
    Estado DELIVERED (Entregado).
    
    En este estado:
    - Work finalizado y entregado al client
    - No se puede modificar nada
    - Estado final (sin transiciones)
    """
    
    def get_state_name(self) -> WorkStateEnum:
        return WorkStateEnum.DELIVERED
    
    def can_add_products(self) -> bool:
        return False
    
    def can_remove_products(self) -> bool:
        return False
    
    def can_edit_product_order(self) -> bool:
        return False
    
    def can_quote(self) -> bool:
        return False
    
    def can_start_work(self) -> bool:
        return False
    
    def can_deliver(self) -> bool:
        return False  # Ya esta entregado
    
    def quote(self, work: 'Work') -> WorkState:
        raise ValueError("No se puede cotizar un work ya entregado.")
    
    def start_work(self, work: 'Work') -> WorkState:
        raise ValueError("No se puede iniciar un work ya entregado.")
    
    def deliver(self, work: 'Work') -> WorkState:
        raise ValueError("El work ya esta entregado.")


# Factory function para create estados por nombre
def create_work_state(state_name: WorkStateEnum) -> WorkState:
    """
    Factory function para create instancias de estados.
    
    Args:
        state_name: Nombre del estado a create
        
    Returns:
        Instancia del estado correspondiente
    """
    state_map = {
        WorkStateEnum.DRAFT: DraftState,
        WorkStateEnum.QUOTED: QuotedState,
        WorkStateEnum.IN_PROGRESS: InProgressState,
        WorkStateEnum.DELIVERED: DeliveredState,
    }
    
    state_class = state_map.get(state_name)
    if state_class is None:
        raise ValueError(f"Estado desconocido: {state_name}")
    
    return state_class()

