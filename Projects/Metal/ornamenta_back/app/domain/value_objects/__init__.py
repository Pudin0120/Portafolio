"""Value Objects package."""
from app.domain.value_objects.document_number import DocumentNumber
from app.domain.value_objects.email import Email
from app.domain.value_objects.money import Money
from app.domain.value_objects.state_user import StateUser, StateEnum
from app.domain.value_objects.state_task import StateTask, StateTaskEnum
from app.domain.value_objects.product_snapshot import ProductSnapshot
from app.domain.value_objects.product_work_item import ProductWorkItem, ProductItemState
from app.domain.value_objects.work_state import (
    WorkState,
    WorkStateEnum,
    DraftState,
    QuotedState,
    InProgressState,
    DeliveredState,
    create_work_state
)

__all__ = [
    "DocumentNumber",
    "Email",
    "Money",
    "StateUser",
    "StateEnum",
    "StateTask",
    "StateTaskEnum",
    "ProductSnapshot",
    "ProductWorkItem",
    "ProductItemState",
    "WorkState",
    "WorkStateEnum",
    "DraftState",
    "QuotedState",
    "InProgressState",
    "DeliveredState",
    "create_work_state",
]

