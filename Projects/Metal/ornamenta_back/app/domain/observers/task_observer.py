"""
Task Observer Pattern Implementation.

Implementa el patron Observer para manejar notificaciones cuando
las tasks son desbloqueadas y estan listas para ejecutarse.
"""
from abc import ABC, abstractmethod
from typing import List, Dict
import uuid

from app.domain.domain_event import DomainEvent
from app.domain.events.task_events import TaskUnblocked


class TaskObserver(ABC):
    """
    Interfaz abstracta para observadores de tasks.
    
    Los observadores se suscriben a eventos de tasks (ej: TaskUnblocked)
    y reaccionan cuando ocurren cambios relevantes.
    """
    
    @abstractmethod
    def on_task_unblocked(self, event: TaskUnblocked) -> None:
        """
        Maneja el evento cuando una task es desbloqueada.
        
        Args:
            event: Evento TaskUnblocked con information de la task
        """
        pass


class TaskNotificationObserver(TaskObserver):
    """
    Observador que maneja notificaciones para empleados.
    
    Cuando una task se desbloquea, este observador:
    - Crea una notificacion para el empleado asignado
    - Almacena la notificacion en la lista de notificaciones del empleado
    
    En una implementacion completa, podria:
    - Enviar emails
    - Enviar notificaciones push
    - Create registros en base de datos
    """
    
    def __init__(self):
        """Inicializa el observador con un registro de notificaciones."""
        self._notifications: Dict[uuid.UUID, List[TaskUnblocked]] = {}
    
    def on_task_unblocked(self, event: TaskUnblocked) -> None:
        """
        Maneja el desbloqueo de task creando una notificacion.
        
        Args:
            event: Evento TaskUnblocked
        """
        user_id = event.assigned_user_id
        
        # Agregar notificacion a la lista del user
        if user_id not in self._notifications:
            self._notifications[user_id] = []
        
        self._notifications[user_id].append(event)
        
        # Aqui podrias agregar logica adicional:
        # - Enviar email
        # - Enviar notificacion push
        # - Registrar en logs
        # - etc.
    
    def get_notifications_for_user(self, user_id: uuid.UUID) -> List[TaskUnblocked]:
        """
        Obtiene todas las notificaciones pendientes para un user.
        
        Args:
            user_id: ID del user
            
        Returns:
            Lista de eventos TaskUnblocked para el user
        """
        return self._notifications.get(user_id, [])
    
    def clear_notifications_for_user(self, user_id: uuid.UUID) -> None:
        """
        Limpia las notificaciones de un user (marcar como leidas).
        
        Args:
            user_id: ID del user
        """
        if user_id in self._notifications:
            self._notifications[user_id].clear()
    
    def has_unread_notifications(self, user_id: uuid.UUID) -> bool:
        """
        Verifica si un user tiene notificaciones sin leer.
        
        Args:
            user_id: ID del user
            
        Returns:
            True si hay notificaciones pendientes
        """
        return user_id in self._notifications and len(self._notifications[user_id]) > 0


class TaskEventSubject:
    """
    Subject del patron Observer.
    
    Mantiene una lista de observadores y los notifica cuando
    ocurren eventos relevantes de tasks.
    """
    
    def __init__(self):
        """Inicializa el subject sin observadores."""
        self._observers: List[TaskObserver] = []
    
    def attach(self, observer: TaskObserver) -> None:
        """
        Registra un observador.
        
        Args:
            observer: Observador a registrar
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: TaskObserver) -> None:
        """
        Desregistra un observador.
        
        Args:
            observer: Observador a desregistrar
        """
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_task_unblocked(self, event: TaskUnblocked) -> None:
        """
        Notifica a todos los observadores sobre una task desbloqueada.
        
        Args:
            event: Evento TaskUnblocked
        """
        for observer in self._observers:
            observer.on_task_unblocked(event)
    
    def process_domain_events(self, events: List[DomainEvent]) -> None:
        """
        Procesa una lista de eventos de dominio y notifica observadores.
        
        Args:
            events: Lista de eventos de dominio
        """
        for event in events:
            if isinstance(event, TaskUnblocked):
                self.notify_task_unblocked(event)


# Singleton global para el subject (opcional, segun arquitectura)
_task_event_subject = TaskEventSubject()


def get_task_event_subject() -> TaskEventSubject:
    """
    Obtiene la instancia singleton del TaskEventSubject.
    
    Returns:
        Instancia global del subject
    """
    return _task_event_subject

