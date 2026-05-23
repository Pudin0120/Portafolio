from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class StateTaskEnum(str, Enum):
    """
    Enumeracion de estados de task.
    
    Flujo de estados:
    PENDING  ASSIGNED  READY  IN_PROGRESS  COMPLETED  FINISHED
    
    - PENDING: Task no asignada aun
    - ASSIGNED: Task assigned pero bloqueada por task anterior (solo para tasks secuenciales)
    - READY: Task assigned y desbloqueada, lista para comenzar
    - IN_PROGRESS: Empleado esta trabajando en la task
    - COMPLETED: Empleado marco como completada, pending de validacion (solo EMPLOYEE)
    - FINISHED: Task completada y validada (o auto-validada para SUPERVISOR/MANAGER)
    """

    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    READY = "READY"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FINISHED = "FINISHED"


class StateTask(BaseModel):
    """Value object para estado de task con validacion usando pydantic."""

    value: StateTaskEnum = Field(..., description="Estado valid de la task")

    def __str__(self) -> str:
        return self.value.value

    def __eq__(self, other) -> bool:
        if isinstance(other, StateTask):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)

    # Properties para verificar estados
    @property
    def is_pending(self) -> bool:
        """Verifica si el estado es pending."""
        return self.value == StateTaskEnum.PENDING

    @property
    def is_assigned(self) -> bool:
        """Verifica si el estado es assigned (bloqueada)."""
        return self.value == StateTaskEnum.ASSIGNED

    @property
    def is_ready(self) -> bool:
        """Verifica si el estado es ready (desbloqueada)."""
        return self.value == StateTaskEnum.READY

    @property
    def is_in_progress(self) -> bool:
        """Verifica si el estado es in progress."""
        return self.value == StateTaskEnum.IN_PROGRESS

    @property
    def is_completed(self) -> bool:
        """Verifica si el estado es completed (pending de validacion)."""
        return self.value == StateTaskEnum.COMPLETED

    @property
    def is_finished(self) -> bool:
        """Verifica si el estado es finished (completada y validada)."""
        return self.value == StateTaskEnum.FINISHED

    # Properties legacy (mantener compatibilidad con codigo existente)
    @property
    def is_sin_iniciar(self) -> bool:
        """Verifica si el estado es pending (legacy)."""
        return self.is_pending or self.is_assigned

    @property
    def is_en_proceso(self) -> bool:
        """Verifica si el estado es in progress (legacy)."""
        return self.is_ready or self.is_in_progress

    @property
    def is_finalizada(self) -> bool:
        """Verifica si el estado es finished (legacy)."""
        return self.is_completed or self.is_finished

    # Metodos de transicion
    def to_pending(self) -> "StateTask":
        """Cambia el estado a pending."""
        return StateTask(value=StateTaskEnum.PENDING)

    def to_assigned(self) -> "StateTask":
        """Cambia el estado a assigned (bloqueada).
        
        Permite transiciones desde:
        - PENDING: Asignacion inicial
        - READY: Reasignacion
        - ASSIGNED: Reasignacion de task ya asignada
        """
        if not (self.is_pending or self.is_ready or self.is_assigned):
            raise ValueError("Solo se puede asignar una task en estado PENDING, READY o ASSIGNED")
        return StateTask(value=StateTaskEnum.ASSIGNED)

    def to_ready(self) -> "StateTask":
        """Cambia el estado a ready (desbloqueada)."""
        if not (self.is_pending or self.is_assigned):
            raise ValueError("Solo se puede desbloquear una task PENDING o ASSIGNED")
        return StateTask(value=StateTaskEnum.READY)

    def to_in_progress(self) -> "StateTask":
        """Cambia el estado a in progress."""
        if not self.is_ready:
            raise ValueError("Solo se puede iniciar una task READY")
        return StateTask(value=StateTaskEnum.IN_PROGRESS)

    def to_completed(self) -> "StateTask":
        """Cambia el estado a completed (pending de validacion)."""
        if not self.is_in_progress:
            raise ValueError("Solo se puede completar una task IN_PROGRESS")
        return StateTask(value=StateTaskEnum.COMPLETED)

    def to_finished(self) -> "StateTask":
        """Cambia el estado a finished (completada y validada)."""
        if not (self.is_in_progress or self.is_completed):
            raise ValueError("Solo se puede finalizar una task IN_PROGRESS o COMPLETED")
        return StateTask(value=StateTaskEnum.FINISHED)

    # Metodos legacy (mantener compatibilidad)
    def to_sin_iniciar(self) -> "StateTask":
        """Cambia el estado a pending (legacy)."""
        return self.to_pending()

    def to_en_proceso(self) -> "StateTask":
        """Cambia el estado a ready (legacy)."""
        return self.to_ready()

    def to_finalizada(self) -> "StateTask":
        """Cambia el estado a finished (legacy)."""
        return self.to_finished()
