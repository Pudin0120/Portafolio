from fastapi import APIRouter, HTTPException, Depends

from app.domain.models.user import User
from app.infrastructure.adapters.rest.authorization import get_current_user

router = APIRouter(
    prefix="/quotes", 
    tags=["Quotations"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/")
def get_quotations():
    """
    Placeholder endpoint for quotations.

    TODO: Implement new quotation logic with database-backed products
    after completing the persistence layer refactoring.
    """
    return {
        "message": "Quotation API endpoints will be implemented after database integration",
        "status": "pending_implementation",
    }
