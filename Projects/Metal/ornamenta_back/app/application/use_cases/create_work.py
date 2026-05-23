"""
Use case para create un work.
"""
from uuid import uuid4
from decimal import Decimal
from fastapi import HTTPException, status

from app.domain.models.work import Work
from app.domain.models.user import User, RoleEnum
from app.domain.repositories.work_repository import WorkRepository
from app.domain.repositories.client_repository import ClientRepository
from app.domain.value_objects.document_number import DocumentNumber, DocumentEnum
from app.domain.value_objects.work_state import DraftState
from app.domain.value_objects.money import Money
from app.application.dto.work_dto import WorkCreateDTO


class CreateWork:
    """Use case para create un nuevo work (solo MANAGER)."""

    def __init__(
        self,
        work_repository: WorkRepository,
        client_repository: ClientRepository
    ):
        self.work_repository = work_repository
        self.client_repository = client_repository

    def execute(self, request: WorkCreateDTO, created_by: User) -> Work:
        """
        Creates a new work in DRAFT status.
        
        Args:
            request: DTO con datos del work a create
            created_by: User que crea el work (debe ser MANAGER)
            
        Returns:
            Work created
            
        Raises:
            HTTPException: Si el user no tiene permisos (403) o el client no existe (404)
        """
        # Validate permissions
        if created_by.role != RoleEnum.MANAGER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo MANAGER puede create works"
            )
        
        # Verify client exists
        # Note: We use CC (Cedula de Ciudadania) as default for lookup,
        # but the client repository should handle this transparently
        client = self.client_repository.get_by_identification(
            DocumentNumber(value=request.client_identification, doc_type=DocumentEnum.CC),
            created_by.tenant_id
        )
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client con identificacion {request.client_identification} no encontrado"
            )
        
        # Create work in DRAFT state
        work = Work(
            work_id=uuid4(),
            identification_number_client=client.identification_number,
            work_name=request.work_name,
            description=request.description or "",
            state=DraftState(),
            products=[],
            tasks=[],
            tax=request.tax,
            end_aprox_delivery_date=request.end_aprox_delivery_date,
            deposit=Money(amount=request.deposit_amount or Decimal("0"), currency="COP"),
            tenant_id=created_by.tenant_id
        )
        
        # Save work
        saved_work = self.work_repository.save(work)
        
        # Clear domain events
        saved_work.clear_domain_events()
        
        return saved_work
