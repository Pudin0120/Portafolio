"""
Domain model for Task entity.

Task represents a task within a work project that can be assigned to employees.
Tasks se generan automaticamente desde products usando TaskFactory.
"""
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
import uuid

from app.domain.value_objects.money import Money
from app.domain.value_objects.state_task import StateTask
from app.domain.domain_event import DomainEvent
from app.domain.strategies.task_completion_strategy import TaskCompletionStrategyFactory

if TYPE_CHECKING:
    from app.domain.models.user import User


@dataclass
class Task:
    """
    Modelo de dominio para task.
    
    Representa una task dentro de un work que puede ser asignada a empleados.
    Las tasks se generan automaticamente desde products (SimpleProduct o componentes
    de CompositeProduct).
    
    Flujo de estados:
    PENDING  ASSIGNED  READY  IN_PROGRESS  COMPLETED  FINISHED
    
    Explicacion:
    - PENDING: Task recien creada, no asignada
    - ASSIGNED: Task assigned a un user. Si is_blocked=True, espera desbloqueo
    - READY: Task desbloqueada (o nunca fue bloqueada), lista para comenzar
    - IN_PROGRESS: Empleado esta trabajando en ella
    - COMPLETED: Empleado completo (solo EMPLOYEE, requiere validacion)
      * La siguiente task se desbloquea automaticamente en este estado
    - FINISHED: Completada y validada (o auto-validada por SUPERVISOR/MANAGER)
    
    El bloqueo (is_blocked) controla si una task depende de otra anterior.
    Si is_blocked=True: ASSIGNED  espera desbloqueo  READY
    Si is_blocked=False: ASSIGNED  READY (inmediato)
    
    IMPORTANTE: Desde la actualizacion, las tasks siguientes se desbloquean cuando
    la task anterior alcanza el estado COMPLETED (no es necesario esperar a FINISHED).
    Esto permite que el work continue sin esperar la validacion de cada task.
    
    Attributes:
        task_id: Identificador unico de la task
        work_id: Identificador del work al que pertenece
        product_id: Identificador del product del cual se genero esta task
        parent_composite_id: ID del CompositeProduct padre (si la task proviene de uno)
        composite_task_slot: Posicion dentro del compuesto (0, 1, 2...)
        composite_total_slots: Total de tasks en el compuesto
        task_name: Nombre de la task
        description: Description detallada de la task
        state: Estado actual de la task
        labor: Valor economico de la mano de obra
        estimated_value: Valor estimado de la task
        execution_order: Orden de ejecucion dentro del work
        requires_validation: Si requiere validacion (depende del rol)
        is_blocked: Si esta bloqueada por una task anterior
        previous_task_id: ID de la task que bloquea esta (si aplica)
        assigned_user_id: ID del user asignado (opcional)
        completed_by_user_id: ID del user que completo la task
        validated_by_user_id: ID del user que valido la task
        _domain_events: Lista de eventos de dominio acumulados
    """
    
    task_id: uuid.UUID
    work_id: uuid.UUID
    product_id: uuid.UUID
    task_name: str
    description: str
    state: StateTask
    labor: Money
    estimated_value: Money
    execution_order: int
    parent_composite_id: Optional[uuid.UUID] = None
    composite_task_slot: Optional[int] = None
    composite_total_slots: Optional[int] = None
    requires_validation: bool = True
    is_blocked: bool = False
    previous_task_id: Optional[uuid.UUID] = None
    assigned_user_id: Optional[str] = None  # Firebase UID (string, puede no ser UUID valid)
    completed_by_user_id: Optional[str] = None
    validated_by_user_id: Optional[str] = None
    updated_at: Optional['datetime'] = None  # Timestamp of last update from database
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False, repr=False)
    
    def __post_init__(self):
        """
        Validaciones post-inicializacion.
        
        Valida que los valores economicos sean positivos y la jerarquia de compuestos.
        """
        if self.labor.amount < 0:
            raise ValueError("El valor de mano de obra no puede ser negativo")
        
        if self.estimated_value.amount < 0:
            raise ValueError("El valor estimado no puede ser negativo")
        
        if self.execution_order < 0:
            raise ValueError("El orden de ejecucion no puede ser negativo")
        
        # Validar jerarquia de compuestos
        if self.parent_composite_id is not None:
            if self.composite_task_slot is None or self.composite_total_slots is None:
                raise ValueError(
                    "Las tasks de un compuesto deben tener composite_task_slot "
                    "y composite_total_slots definidos"
                )
            
            if self.composite_task_slot >= self.composite_total_slots:
                raise ValueError(
                    f"composite_task_slot ({self.composite_task_slot}) no puede ser >= "
                    f"composite_total_slots ({self.composite_total_slots})"
                )
            
            if self.composite_task_slot < 0:
                raise ValueError("composite_task_slot no puede ser negativo")
    
    # Properties para verificar estados
    @property
    def is_pending(self) -> bool:
        """Verifica si la task esta pending (no asignada)."""
        return self.state.is_pending
    
    @property
    def is_assigned_state(self) -> bool:
        """Verifica si la task esta en estado ASSIGNED (bloqueada)."""
        return self.state.is_assigned
    
    @property
    def is_ready(self) -> bool:
        """Verifica si la task esta lista para comenzar."""
        return self.state.is_ready
    
    @property
    def is_in_progress(self) -> bool:
        """Verifica si la task esta en progreso."""
        return self.state.is_in_progress
    
    @property
    def is_completed(self) -> bool:
        """Verifica si la task esta completada (pending de validacion)."""
        return self.state.is_completed
    
    @property
    def is_finished(self) -> bool:
        """Verifica si la task esta finalizada (completada y validada)."""
        return self.state.is_finished
    
    @property
    def is_assigned(self) -> bool:
        """Verifica si la task esta asignada a un user."""
        return self.assigned_user_id is not None
    
    # Properties legacy (mantener compatibilidad)
    @property
    def is_sin_iniciar(self) -> bool:
        """Verifica si la task esta sin iniciar (legacy)."""
        return self.state.is_sin_iniciar
    
    @property
    def is_en_proceso(self) -> bool:
        """Verifica si la task esta en proceso (legacy)."""
        return self.state.is_en_proceso
    
    @property
    def is_finalizada(self) -> bool:
        """Verifica si la task esta finalizada (legacy)."""
        return self.state.is_finalizada
    
    def assign_to(self, user: 'User', assigned_by: 'User') -> None:
        """
        Asigna la task a un user.
        
        Solo SUPERVISOR y MANAGER pueden asignar tasks.
        - Si NO esta bloqueada (is_blocked=False): PENDING  ASSIGNED  READY (lista inmediatamente)
        - Si esta bloqueada (is_blocked=True): PENDING  ASSIGNED (espera desbloqueo)
        
        Args:
            user: User al que se asigna la task
            assigned_by: User que asigna la task (debe ser SUPERVISOR o MANAGER)
            
        Raises:
            ValueError: Si la task no puede asignarse o el user no tiene permisos
        """
        from app.domain.models.user import RoleEnum
        
        # Validar que quien asigna tenga permisos
        if assigned_by.role not in [RoleEnum.SUPERVISOR, RoleEnum.MANAGER]:
            raise ValueError("Solo SUPERVISOR o MANAGER pueden asignar tasks")
        
        # Validar que ambos users esten activos
        if not assigned_by.is_active:
            raise ValueError("El user que asigna debe estar active")
        
        if not user.is_active:
            raise ValueError("Solo se pueden asignar tasks a users activos")
        
        # Validar estado de la task: solo se pueden asignar tasks en PENDING (inicial) o reasignar ASSIGNED/READY
        if not (self.is_pending or self.is_assigned_state or self.is_ready):
            raise ValueError("Solo se pueden asignar tasks en estado PENDING, ASSIGNED o READY")
        
        # Usar firebase_uid como identificador unico del user (es un string)
        self.assigned_user_id = user.firebase_uid
        
        # Determinar si requiere validacion segun el rol del asignado
        strategy = TaskCompletionStrategyFactory.get_strategy(user.role)
        self.requires_validation = strategy.requires_validation()
        
        # Cambiar a ASSIGNED
        self.state = self.state.to_assigned()  # PENDING  ASSIGNED
        
        # Si NO esta bloqueada, cambiar inmediatamente a READY
        # (Primera task de un product simple o primera de un compuesto)
        if not self.is_blocked:
            self.state = self.state.to_ready()  # ASSIGNED  READY
        # Si esta bloqueada, permanece en ASSIGNED esperando desbloqueo
        
        # Generar evento de dominio
        from datetime import datetime
        from app.domain.events.task_events import TaskAssigned
        
        event = TaskAssigned(
            event_id=uuid.uuid4(),
            occurred_at=datetime.utcnow(),
            aggregate_id=self.task_id,
            task_id=self.task_id,
            work_id=self.work_id,
            assigned_user_id=self.assigned_user_id,  # type: ignore
            task_name=self.task_name,
            labor_value=self.labor.amount
        )
        
        self._domain_events.append(event)
    
    def reassign_to(self, user: 'User', reassigned_by: 'User', reason: str = "") -> None:
        """
        Reasigna la task a otro user.
        
        Solo SUPERVISOR y MANAGER pueden reasignar tasks.
        Se mantiene el progreso de la task.
        
        Args:
            user: Nuevo user asignado
            reassigned_by: User que reasigna (debe ser SUPERVISOR o MANAGER)
            reason: Razon de la reasignacion
            
        Raises:
            ValueError: Si la task no puede reasignarse o el user no tiene permisos
        """
        from app.domain.models.user import RoleEnum
        from datetime import datetime
        from app.domain.events.task_events import TaskReassigned
        
        # Validar permisos
        if reassigned_by.role not in [RoleEnum.SUPERVISOR, RoleEnum.MANAGER]:
            raise ValueError("Solo SUPERVISOR o MANAGER pueden reasignar tasks")
        
        if not reassigned_by.is_active or not user.is_active:
            raise ValueError("Ambos users deben estar activos")
        
        # Validar que la task este asignada
        if not self.is_assigned:
            raise ValueError("Solo se pueden reasignar tasks ya asignadas")
        
        # No se puede reasignar una task ya finalizada
        if self.is_finished:
            raise ValueError("No se puede reasignar una task finalizada")
        
        previous_user_id = self.assigned_user_id
        self.assigned_user_id = user.firebase_uid
        
        # Actualizar requires_validation segun el nuevo user
        strategy = TaskCompletionStrategyFactory.get_strategy(user.role)
        self.requires_validation = strategy.requires_validation()
        
        # Generar evento
        event = TaskReassigned(
            event_id=uuid.uuid4(),
            occurred_at=datetime.utcnow(),
            aggregate_id=self.task_id,
            task_id=self.task_id,
            work_id=self.work_id,
            previous_user_id=previous_user_id,
            new_user_id=self.assigned_user_id,
            reassigned_by_user_id=reassigned_by.firebase_uid,
            task_name=self.task_name,
            reason=reason
        )
        
        self._domain_events.append(event)
    
    def unblock(self) -> 'DomainEvent':
        """
        Desbloquea la task (ASSIGNED  READY).
        
        Se llama cuando la task anterior en la secuencia se completa.
        Genera un evento TaskUnblocked para notificar al empleado asignado.
        
        Returns:
            Evento TaskUnblocked generado
            
        Raises:
            ValueError: Si la task no esta bloqueada o no esta asignada
        """
        from datetime import datetime
        from app.domain.events.task_events import TaskUnblocked
        
        if not self.is_blocked:
            raise ValueError("Esta task no esta bloqueada")
        
        if not self.is_assigned_state:
            raise ValueError("Solo se pueden desbloquear tasks en estado ASSIGNED")
        
        self.is_blocked = False
        self.state = self.state.to_ready()
        
        # Generar evento para notificar al empleado
        event = TaskUnblocked(
            event_id=uuid.uuid4(),
            occurred_at=datetime.utcnow(),
            aggregate_id=self.task_id,
            task_id=self.task_id,
            work_id=self.work_id,
            product_id=self.product_id,
            assigned_user_id=self.assigned_user_id,  # type: ignore
            task_name=self.task_name,
            previous_task_id=self.previous_task_id
        )
        
        self._domain_events.append(event)
        return event
    
    def start(self, started_by: 'User') -> None:
        """
        Inicia la task (READY  IN_PROGRESS).
        
        Args:
            started_by: User que inicia la task
            
        Raises:
            ValueError: Si la task no puede iniciarse
        """
        if not self.is_ready:
            raise ValueError("Solo se pueden iniciar tasks en estado READY")
        
        if not self.is_assigned:
            raise ValueError("La task debe estar asignada para poder iniciarse")
        
        # Comparar usando firebase_uid (ambos son strings)
        if started_by.firebase_uid != self.assigned_user_id:
            raise ValueError("Solo el user asignado puede iniciar la task")
        
        self.state = self.state.to_in_progress()
    
    def complete(self, completed_by: 'User') -> None:
        """
        Completa la task segun la estrategia del rol.
        
        - EMPLOYEE: IN_PROGRESS  COMPLETED (requiere validacion)
        - SUPERVISOR/MANAGER: IN_PROGRESS  FINISHED (auto-validada)
        
        Args:
            completed_by: User que completa la task
            
        Raises:
            ValueError: Si la task no puede completarse
        """
        from datetime import datetime
        from app.domain.events.task_events import TaskCompleted
        
        if not self.is_in_progress:
            raise ValueError("Solo se pueden completar tasks en estado IN_PROGRESS")
        
        if not self.is_assigned:
            raise ValueError("La task debe estar asignada")
        
        # Comparar usando firebase_uid (strings)
        if completed_by.firebase_uid != self.assigned_user_id:
            raise ValueError("Solo el user asignado puede completar la task")
        
        # Usar estrategia segun el rol
        strategy = TaskCompletionStrategyFactory.get_strategy(completed_by.role)
        self.state = strategy.complete_task(self, completed_by)
        self.completed_by_user_id = completed_by.firebase_uid
        
        # Si es auto-validada, tambien registrar validador
        if self.is_finished:
            self.validated_by_user_id = completed_by.firebase_uid
        
        # Generar evento
        event = TaskCompleted(
            event_id=uuid.uuid4(),
            occurred_at=datetime.utcnow(),
            aggregate_id=self.task_id,
            task_id=self.task_id,
            work_id=self.work_id,
            completed_user_id=self.completed_by_user_id,
            task_name=self.task_name,
            labor_value=self.labor.amount
        )
        
        self._domain_events.append(event)
    
    def validate(self, validated_by: 'User') -> None:
        """
        Valida una task completada (COMPLETED  FINISHED).
        
        Solo SUPERVISOR o MANAGER pueden validar.
        
        Args:
            validated_by: User que valida la task
            
        Raises:
            ValueError: Si la task no puede validarse o el user no tiene permisos
        """
        from datetime import datetime
        from app.domain.events.task_events import TaskValidated
        
        if not self.is_completed:
            raise ValueError("Solo se pueden validar tasks en estado COMPLETED")
        
        # Verificar permisos usando la estrategia
        strategy = TaskCompletionStrategyFactory.get_strategy(validated_by.role)
        if not strategy.can_validate_tasks():
            raise ValueError(f"El rol {validated_by.role.value} no puede validar tasks")
        
        self.state = self.state.to_finished()
        self.validated_by_user_id = validated_by.firebase_uid
        
        # Generar evento
        event = TaskValidated(
            event_id=uuid.uuid4(),
            occurred_at=datetime.utcnow(),
            aggregate_id=self.task_id,
            task_id=self.task_id,
            work_id=self.work_id,
            completed_by_user_id=self.completed_by_user_id,
            validated_by_user_id=self.validated_by_user_id,
            task_name=self.task_name
        )
        
        self._domain_events.append(event)
    
    # Metodos legacy (mantener compatibilidad)
    def unassign(self) -> None:
        """Desasigna la task (legacy - deprecated)."""
        if self.is_finished:
            raise ValueError("No se puede desasignar una task finalizada")
        
        if not self.is_assigned:
            raise ValueError("La task no esta asignada")
        
        self.assigned_user_id = None
        self.state = self.state.to_pending()
    
    def finish(self) -> None:
        """Finaliza la task (legacy - usar complete() o validate())."""
        if not self.is_in_progress:
            raise ValueError("Solo se pueden finalizar tasks en proceso")
        
        self.state = self.state.to_finished()
        
        from datetime import datetime
        from app.domain.events.task_events import TaskCompleted
        
        event = TaskCompleted(
            event_id=uuid.uuid4(),
            occurred_at=datetime.utcnow(),
            aggregate_id=self.task_id,
            task_id=self.task_id,
            work_id=self.work_id,
            completed_user_id=self.assigned_user_id,
            task_name=self.task_name,
            labor_value=self.labor.amount
        )
        
        self._domain_events.append(event)
    
    def change_state(self, new_state: StateTask, changed_by: 'User', reason: str = "") -> None:
        """
        Cambia el estado de la task y registra el evento de dominio.
        
        Args:
            new_state: Nuevo estado de la task
            changed_by: User que ejecuta el cambio
            reason: Razon opcional del cambio
        """
        from datetime import datetime
        from app.domain.events.task_events import TaskStateChanged
        
        previous_state = self.state.value.value
        self.state = new_state
        
        # Generar evento de dominio
        event = TaskStateChanged(
            event_id=uuid.uuid4(),
            occurred_at=datetime.utcnow(),
            aggregate_id=self.task_id,
            task_id=self.task_id,
            work_id=self.work_id,
            previous_state=previous_state,
            new_state=new_state.value.value,
            changed_by_user_id=changed_by.firebase_uid,
            changed_by_user_name=changed_by.full_name,
            reason=reason
        )
        
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> List[DomainEvent]:
        """
        Retorna y limpia los eventos de dominio acumulados.
        
        Returns:
            Lista de eventos de dominio acumulados
        """
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
