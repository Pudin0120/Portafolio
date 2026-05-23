"""
PostgreSQL implementation of ClientRepository.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.domain.models.client import Client
from app.domain.repositories.client_repository import ClientRepository
from app.domain.value_objects.document_number import DocumentNumber, DocumentEnum
from app.domain.value_objects.email import Email
from app.infrastructure.adapters.db.models.client_model import ClientModel


class PostgresClientRepository(ClientRepository):
    """Implementacion PostgreSQL del repositorio de clients."""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def save(self, client: Client) -> Client:
        """
        Guarda o actualiza un client en la base de datos.
        
        NOTE: Does NOT commit - relies on get_db_session() to commit at end of request.
        This ensures atomicity across multiple operations in the same request.
        
        Args:
            client: Client a save
            
        Returns:
            Client guardado
        """
        # Check if client already exists
        stmt = select(ClientModel).where(
            ClientModel.identification_number == client.identification_number.value,
            ClientModel.tenant_id == client.tenant_id
        )
        existing = self.db_session.execute(stmt).scalar_one_or_none()
        
        if existing:
            # Update existing client
            existing.document_type = client.identification_number.doc_type.value  # type: ignore[assignment]
            existing.first_name = client.first_name  # type: ignore[assignment]
            existing.last_name = client.last_name  # type: ignore[assignment]
            existing.email = str(client.email.value)  # type: ignore[assignment]
            existing.phone = client.phone  # type: ignore[assignment]
            existing.address = client.address  # type: ignore[assignment]
            existing.tenant_id = client.tenant_id  # type: ignore[assignment]
            model = existing
        else:
            # Create new client
            model = self._to_model(client)
            self.db_session.add(model)
        
        # Flush to assign IDs and make client available immediately
        self.db_session.flush()
        self.db_session.refresh(model)
        return self._to_domain(model)

    def get_by_identification(self, identification: DocumentNumber, tenant_id: UUID) -> Optional[Client]:
        """
        Obtiene un client por su number de identificacion.
        
        Args:
            identification: Number de identificacion del client
            
        Returns:
            Client encontrado o None
        """
        stmt = select(ClientModel).where(
            ClientModel.identification_number == identification.value,
            ClientModel.tenant_id == tenant_id
        )
        model = self.db_session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None

    def get_by_email(self, email: Email, tenant_id: UUID) -> Optional[Client]:
        """
        Obtiene un client por su email.
        
        Args:
            email: Email del client
            
        Returns:
            Client encontrado o None
        """
        stmt = select(ClientModel).where(
            ClientModel.email == str(email.value),
            ClientModel.tenant_id == tenant_id
        )
        model = self.db_session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None

    def get_all(self, tenant_id: UUID) -> List[Client]:
        """
        Obtiene todos los clients.
        
        Returns:
            Lista de todos los clients
        """
        stmt = select(ClientModel).where(
            ClientModel.tenant_id == tenant_id
        ).order_by(ClientModel.first_name, ClientModel.last_name)
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]

    def delete(self, identification: DocumentNumber, tenant_id: UUID) -> bool:
        """
        Elimina un client por su number de identificacion.
        
        NOTE: Does NOT commit - relies on get_db_session() to commit at end of request.
        This ensures atomicity across multiple operations in the same request.
        
        Args:
            identification: Number de identificacion del client
            
        Returns:
            True si se elimino correctamente, False si no existia
        """
        stmt = select(ClientModel).where(
            ClientModel.identification_number == identification.value,
            ClientModel.tenant_id == tenant_id
        )
        model = self.db_session.execute(stmt).scalar_one_or_none()
        
        if not model:
            return False
        
        self.db_session.delete(model)
        self.db_session.flush()  # Flush to validate constraints
        return True

    def _to_domain(self, model: ClientModel) -> Client:
        """
        Convierte un modelo de base de datos a entidad de dominio.
        
        Args:
            model: Modelo de base de datos
            
        Returns:
            Entidad de dominio Client
        """
        # Map document type string to enum
        doc_type_map = {
            'CC': DocumentEnum.CC,
            'CE': DocumentEnum.CE,
            'NIT': DocumentEnum.NIT,
        }
        doc_type = doc_type_map.get(str(getattr(model, "document_type", "CC")), DocumentEnum.CC)
        
        return Client(
            identification_number=DocumentNumber(
                value=str(getattr(model, "identification_number", "")),
                doc_type=doc_type
            ),
            first_name=str(getattr(model, "first_name", "")),
            last_name=str(getattr(model, "last_name", "")),
            email=Email(value=str(getattr(model, "email", ""))),
            phone=str(getattr(model, "phone", "") or ""),
            address=str(getattr(model, "address", "") or ""),
            tenant_id=getattr(model, "tenant_id", None)
        )

    def _to_model(self, client: Client) -> ClientModel:
        """
        Convierte una entidad de dominio a modelo de base de datos.
        
        Args:
            client: Entidad de dominio
            
        Returns:
            Modelo de base de datos ClientModel
        """
        return ClientModel(
            identification_number=client.identification_number.value,
            document_type=client.identification_number.doc_type.value,
            first_name=client.first_name,
            last_name=client.last_name,
            email=str(client.email.value),
            phone=client.phone,
            address=client.address,
            tenant_id=client.tenant_id
        )
