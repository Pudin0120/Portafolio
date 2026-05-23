"""
Tests for PostgresClientRepository tenant isolation.
"""
from uuid import uuid4

import pytest

from app.domain.models.client import Client
from app.domain.value_objects.document_number import DocumentEnum, DocumentNumber
from app.domain.value_objects.email import Email
from app.infrastructure.adapters.repositories.postgres_client_repository import PostgresClientRepository


class TestPostgresClientRepository:
    @pytest.fixture
    def tenant_id(self, db_session):
        from app.infrastructure.adapters.db.models.tenant_model import TenantModel

        tenant = TenantModel(
            id=uuid4(),
            name="Test Tenant",
            slug=f"test-client-tenant-{uuid4().hex[:8]}",
            is_active=True,
        )
        db_session.add(tenant)
        db_session.flush()
        return tenant.id

    def test_save_persists_tenant_id(self, db_session, tenant_id):
        repo = PostgresClientRepository(db_session)
        client = Client(
            identification_number=DocumentNumber(value="3134123412", doc_type=DocumentEnum.CC),
            first_name="Juan",
            last_name="Bodoque",
            email=Email(value="juan@example.com"),
            phone="2018310",
            address="de la nueva villa.",
            tenant_id=tenant_id,
        )

        saved = repo.save(client)

        assert saved.tenant_id == tenant_id

    def test_get_by_identification_filters_by_tenant(self, db_session, tenant_id):
        repo = PostgresClientRepository(db_session)
        other_tenant = uuid4()
        client = Client(
            identification_number=DocumentNumber(value="3134123413", doc_type=DocumentEnum.CC),
            first_name="Ana",
            last_name="Perez",
            email=Email(value="ana@example.com"),
            phone="2018311",
            address="another street",
            tenant_id=tenant_id,
        )
        repo.save(client)

        assert repo.get_by_identification(client.identification_number, tenant_id) is not None
        assert repo.get_by_identification(client.identification_number, other_tenant) is None
