"""
Unit tests for TaskObserver (Observer Pattern).

Tests cover:
- TaskNotificationObserver functionality
- TaskEventSubject subscription mechanism
- Notification management (create, get, clear)
- Event processing
"""
import pytest
from uuid import uuid4
from datetime import datetime

from app.domain.observers.task_observer import (
    TaskObserver,
    TaskNotificationObserver,
    TaskEventSubject,
    get_task_event_subject
)
from app.domain.events.task_events import TaskUnblocked, TaskCompleted


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def task_unblocked_event():
    """TaskUnblocked event fixture."""
    return TaskUnblocked(
        event_id=uuid4(),
        occurred_at=datetime.utcnow(),
        aggregate_id=uuid4(),
        task_id=uuid4(),
        work_id=uuid4(),
        product_id=uuid4(),
        assigned_user_id=uuid4(),
        task_name="Test Task",
        previous_task_id=uuid4()
    )


@pytest.fixture
def another_task_unblocked_event():
    """Another TaskUnblocked event for different user."""
    return TaskUnblocked(
        event_id=uuid4(),
        occurred_at=datetime.utcnow(),
        aggregate_id=uuid4(),
        task_id=uuid4(),
        work_id=uuid4(),
        product_id=uuid4(),
        assigned_user_id=uuid4(),
        task_name="Another Task",
        previous_task_id=None
    )


@pytest.fixture
def task_completed_event():
    """TaskCompleted event fixture."""
    return TaskCompleted(
        event_id=uuid4(),
        occurred_at=datetime.utcnow(),
        aggregate_id=uuid4(),
        task_id=uuid4(),
        work_id=uuid4(),
        completed_user_id=uuid4(),
        task_name="Completed Task",
        labor_value=50000
    )


# ============================================================================
# TESTS: TaskNotificationObserver
# ============================================================================

def test_notification_observer_creation():
    """Test creating notification observer."""
    observer = TaskNotificationObserver()
    
    assert observer is not None
    assert observer._notifications == {}


def test_notification_observer_on_task_unblocked(task_unblocked_event):
    """Test observer handles TaskUnblocked event."""
    observer = TaskNotificationObserver()
    
    observer.on_task_unblocked(task_unblocked_event)
    
    # Notification should be stored for the user
    notifications = observer.get_notifications_for_user(task_unblocked_event.assigned_user_id)
    assert len(notifications) == 1
    assert notifications[0] == task_unblocked_event


def test_notification_observer_multiple_notifications(task_unblocked_event):
    """Test observer handles multiple notifications for same user."""
    observer = TaskNotificationObserver()
    
    # Same user - create segundo evento con el mismo user_id
    user_id = task_unblocked_event.assigned_user_id
    another_event = TaskUnblocked(
        event_id=uuid4(),
        occurred_at=datetime.utcnow(),
        aggregate_id=uuid4(),
        task_id=uuid4(),
        work_id=uuid4(),
        product_id=uuid4(),
        assigned_user_id=user_id,  # Mismo user
        task_name="Another Task",
        previous_task_id=None
    )
    
    observer.on_task_unblocked(task_unblocked_event)
    observer.on_task_unblocked(another_event)
    
    notifications = observer.get_notifications_for_user(user_id)
    assert len(notifications) == 2


def test_notification_observer_different_users(task_unblocked_event, another_task_unblocked_event):
    """Test observer handles notifications for different users."""
    observer = TaskNotificationObserver()
    
    observer.on_task_unblocked(task_unblocked_event)
    observer.on_task_unblocked(another_task_unblocked_event)
    
    # User 1
    notifications1 = observer.get_notifications_for_user(task_unblocked_event.assigned_user_id)
    assert len(notifications1) == 1
    
    # User 2
    notifications2 = observer.get_notifications_for_user(another_task_unblocked_event.assigned_user_id)
    assert len(notifications2) == 1


def test_get_notifications_for_nonexistent_user():
    """Test getting notifications for user with no notifications."""
    observer = TaskNotificationObserver()
    
    notifications = observer.get_notifications_for_user(uuid4())
    
    assert notifications == []


def test_clear_notifications_for_user(task_unblocked_event):
    """Test clearing notifications for a user."""
    observer = TaskNotificationObserver()
    user_id = task_unblocked_event.assigned_user_id
    
    observer.on_task_unblocked(task_unblocked_event)
    assert len(observer.get_notifications_for_user(user_id)) == 1
    
    observer.clear_notifications_for_user(user_id)
    
    assert len(observer.get_notifications_for_user(user_id)) == 0


def test_has_unread_notifications_true(task_unblocked_event):
    """Test has_unread_notifications returns True."""
    observer = TaskNotificationObserver()
    user_id = task_unblocked_event.assigned_user_id
    
    observer.on_task_unblocked(task_unblocked_event)
    
    assert observer.has_unread_notifications(user_id)


def test_has_unread_notifications_false():
    """Test has_unread_notifications returns False."""
    observer = TaskNotificationObserver()
    
    assert not observer.has_unread_notifications(uuid4())


def test_has_unread_notifications_after_clear(task_unblocked_event):
    """Test has_unread_notifications after clearing."""
    observer = TaskNotificationObserver()
    user_id = task_unblocked_event.assigned_user_id
    
    observer.on_task_unblocked(task_unblocked_event)
    observer.clear_notifications_for_user(user_id)
    
    assert not observer.has_unread_notifications(user_id)


# ============================================================================
# TESTS: TaskEventSubject
# ============================================================================

def test_subject_creation():
    """Test creating subject."""
    subject = TaskEventSubject()
    
    assert subject is not None
    assert subject._observers == []


def test_subject_attach_observer():
    """Test attaching observer to subject."""
    subject = TaskEventSubject()
    observer = TaskNotificationObserver()
    
    subject.attach(observer)
    
    assert observer in subject._observers


def test_subject_attach_same_observer_once():
    """Test attaching same observer multiple times only adds once."""
    subject = TaskEventSubject()
    observer = TaskNotificationObserver()
    
    subject.attach(observer)
    subject.attach(observer)  # Try to attach again
    
    assert len(subject._observers) == 1


def test_subject_detach_observer():
    """Test detaching observer from subject."""
    subject = TaskEventSubject()
    observer = TaskNotificationObserver()
    
    subject.attach(observer)
    assert observer in subject._observers
    
    subject.detach(observer)
    assert observer not in subject._observers


def test_subject_notify_task_unblocked(task_unblocked_event):
    """Test subject notifies observers on task unblocked."""
    subject = TaskEventSubject()
    observer = TaskNotificationObserver()
    
    subject.attach(observer)
    subject.notify_task_unblocked(task_unblocked_event)
    
    # Observer should have received notification
    notifications = observer.get_notifications_for_user(task_unblocked_event.assigned_user_id)
    assert len(notifications) == 1


def test_subject_notify_multiple_observers(task_unblocked_event):
    """Test subject notifies multiple observers."""
    subject = TaskEventSubject()
    observer1 = TaskNotificationObserver()
    observer2 = TaskNotificationObserver()
    
    subject.attach(observer1)
    subject.attach(observer2)
    
    subject.notify_task_unblocked(task_unblocked_event)
    
    # Both observers should have received notification
    user_id = task_unblocked_event.assigned_user_id
    assert len(observer1.get_notifications_for_user(user_id)) == 1
    assert len(observer2.get_notifications_for_user(user_id)) == 1


def test_subject_process_domain_events(task_unblocked_event, task_completed_event):
    """Test subject processes domain events."""
    subject = TaskEventSubject()
    observer = TaskNotificationObserver()
    
    subject.attach(observer)
    
    # Process mixed events
    events = [task_unblocked_event, task_completed_event]
    subject.process_domain_events(events)
    
    # Only TaskUnblocked should trigger notification
    notifications = observer.get_notifications_for_user(task_unblocked_event.assigned_user_id)
    assert len(notifications) == 1


def test_subject_process_only_task_unblocked_events(task_completed_event):
    """Test subject only processes TaskUnblocked events."""
    subject = TaskEventSubject()
    observer = TaskNotificationObserver()
    
    subject.attach(observer)
    
    # Process non-TaskUnblocked event
    subject.process_domain_events([task_completed_event])
    
    # No notifications should be created
    assert not observer._notifications


# ============================================================================
# TESTS: Global Singleton Subject
# ============================================================================

def test_get_task_event_subject_singleton():
    """Test get_task_event_subject returns singleton."""
    subject1 = get_task_event_subject()
    subject2 = get_task_event_subject()
    
    assert subject1 is subject2


def test_global_subject_persists_observers():
    """Test global subject persists attached observers."""
    subject = get_task_event_subject()
    observer = TaskNotificationObserver()
    
    subject.attach(observer)
    
    # Get subject again
    subject2 = get_task_event_subject()
    
    # Should have same observer
    assert observer in subject2._observers


# ============================================================================
# TESTS: Observer Pattern Integration
# ============================================================================

def test_complete_observer_pattern_flow(task_unblocked_event):
    """Test complete observer pattern flow."""
    # Setup
    subject = TaskEventSubject()
    observer = TaskNotificationObserver()
    
    # Subscribe
    subject.attach(observer)
    
    # Event occurs
    subject.notify_task_unblocked(task_unblocked_event)
    
    # User checks notifications
    user_id = task_unblocked_event.assigned_user_id
    has_notifications = observer.has_unread_notifications(user_id)
    assert has_notifications
    
    # User reads notifications
    notifications = observer.get_notifications_for_user(user_id)
    assert len(notifications) == 1
    
    # User marks as read
    observer.clear_notifications_for_user(user_id)
    assert not observer.has_unread_notifications(user_id)


def test_multiple_users_independent_notifications(task_unblocked_event, another_task_unblocked_event):
    """Test notifications are independent per user."""
    subject = TaskEventSubject()
    observer = TaskNotificationObserver()
    
    subject.attach(observer)
    
    user1_id = task_unblocked_event.assigned_user_id
    user2_id = another_task_unblocked_event.assigned_user_id
    
    # Notify both users
    subject.notify_task_unblocked(task_unblocked_event)
    subject.notify_task_unblocked(another_task_unblocked_event)
    
    # User 1 clears notifications
    observer.clear_notifications_for_user(user1_id)
    
    # User 1: no notifications
    assert not observer.has_unread_notifications(user1_id)
    
    # User 2: still has notifications
    assert observer.has_unread_notifications(user2_id)


# ============================================================================
# TESTS: Edge Cases
# ============================================================================

def test_detach_nonexistent_observer():
    """Test detaching observer that was never attached."""
    subject = TaskEventSubject()
    observer = TaskNotificationObserver()
    
    # Should not raise error
    subject.detach(observer)


def test_notify_with_no_observers(task_unblocked_event):
    """Test notifying with no observers attached."""
    subject = TaskEventSubject()
    
    # Should not raise error
    subject.notify_task_unblocked(task_unblocked_event)


def test_clear_notifications_for_nonexistent_user():
    """Test clearing notifications for user with no notifications."""
    observer = TaskNotificationObserver()
    
    # Should not raise error
    observer.clear_notifications_for_user(uuid4())


def test_observer_implements_interface():
    """Test that TaskNotificationObserver implements TaskObserver interface."""
    observer = TaskNotificationObserver()
    
    assert isinstance(observer, TaskObserver)
    assert hasattr(observer, 'on_task_unblocked')


# ============================================================================
# TESTS: Notification Content
# ============================================================================

def test_notification_contains_correct_data(task_unblocked_event):
    """Test that notification contains correct event data."""
    observer = TaskNotificationObserver()
    
    observer.on_task_unblocked(task_unblocked_event)
    
    notifications = observer.get_notifications_for_user(task_unblocked_event.assigned_user_id)
    notification = notifications[0]
    
    assert notification.task_id == task_unblocked_event.task_id
    assert notification.work_id == task_unblocked_event.work_id
    assert notification.product_id == task_unblocked_event.product_id
    assert notification.assigned_user_id == task_unblocked_event.assigned_user_id
    assert notification.task_name == task_unblocked_event.task_name


def test_notification_preserves_event_order(task_unblocked_event):
    """Test that notifications preserve event order."""
    observer = TaskNotificationObserver()
    user_id = task_unblocked_event.assigned_user_id
    
    # Create segundo evento con el mismo user_id
    another_event = TaskUnblocked(
        event_id=uuid4(),
        occurred_at=datetime.utcnow(),
        aggregate_id=uuid4(),
        task_id=uuid4(),
        work_id=uuid4(),
        product_id=uuid4(),
        assigned_user_id=user_id,  # Mismo user
        task_name="Second Task",
        previous_task_id=None
    )
    
    observer.on_task_unblocked(task_unblocked_event)
    observer.on_task_unblocked(another_event)
    
    notifications = observer.get_notifications_for_user(user_id)
    
    assert notifications[0] == task_unblocked_event
    assert notifications[1] == another_event

