import uuid
from unittest.mock import Mock, MagicMock
import pytest

from app.domain.models.user import RoleEnum, User as DomainUser
from app.domain.value_objects.document_number import DocumentEnum, DocumentNumber
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateEnum, StateUser
from app.infrastructure.adapters.db.models import Role as DbRole
from app.infrastructure.adapters.db.models import User as DbUser
from app.infrastructure.adapters.repositories.postgres_user_repository import (
    PostgresUserRepository,
)


class TestPostgresUserRepository:
    """Tests para PostgresUserRepository."""

    @pytest.fixture
    def mock_session(self):
        """Mock de la sesion de base de datos."""
        return Mock()

    @pytest.fixture
    def repository(self, mock_session):
        """Instancia del repositorio con sesion mock."""
        return PostgresUserRepository(mock_session)

    @pytest.fixture
    def db_role(self):
        """Mock de rol de base de datos."""
        role = Mock(spec=DbRole)
        role.name = "EMPLOYEE"
        return role

    @pytest.fixture
    def db_user(self, db_role):
        """Mock de user de base de datos."""
        user = Mock(spec=DbUser)
        user.id = 1234567890
        user.firebase_uid = str(uuid.uuid4())
        user.document_number = "1234567890"
        user.first_name = "Juan"
        user.last_name = "Perez"
        user.email = "juan@example.com"
        user.state = "A"
        user.phone = 3001234567
        user.role = db_role
        user.role_name = "EMPLOYEE"  # Agregar role_name
        return user

    def test_db_user_to_domain_conversion(self, repository, db_user):
        """Test conversion de user de BD a modelo de dominio."""
        domain_user = repository._db_user_to_domain(db_user)

        assert isinstance(domain_user, DomainUser)
        assert domain_user.identification_number.value == "1234567890"
        assert domain_user.identification_number.doc_type == DocumentEnum.CC
        assert domain_user.role == RoleEnum.EMPLOYEE
        assert domain_user.first_name == "Juan"
        assert domain_user.last_name == "Perez"
        assert domain_user.email.value == "juan@example.com"
        assert domain_user.state.value == StateEnum.ACTIVE
        assert domain_user.id == db_user.id
        assert domain_user.phone == "3001234567"

    def test_db_user_to_domain_without_phone(self, repository, db_user):
        """Test conversion cuando el user no tiene telefono."""
        db_user.phone = None
        domain_user = repository._db_user_to_domain(db_user)
        assert domain_user.phone is None

    def test_db_user_to_domain_without_role(self, repository, db_user):
        """Test conversion cuando el user no tiene rol (usar por defecto)."""
        db_user.role = None
        domain_user = repository._db_user_to_domain(db_user)
        assert domain_user.role == RoleEnum.EMPLOYEE

    def test_get_by_firebase_uid_found(self, repository, mock_session, db_user):
        """Test search user por firebase_uid cuando existe."""
        firebase_uid = "test-firebase-uid"
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = db_user

        result = repository.get_by_firebase_uid(firebase_uid)

        mock_session.query.assert_called_once_with(DbUser)
        mock_query.filter.assert_called_once()
        assert result is not None
        assert isinstance(result, DomainUser)

    def test_get_by_firebase_uid_not_found(self, repository, mock_session):
        """Test search user por firebase_uid cuando no existe."""
        firebase_uid = "nonexistent-firebase-uid"
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        result = repository.get_by_firebase_uid(firebase_uid)

        mock_session.query.assert_called_once_with(DbUser)
        assert result is None

    def test_get_by_email_found(self, repository, mock_session, db_user):
        """Test search user por email cuando existe."""
        email = Email(value="juan@example.com")
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = db_user

        result = repository.get_by_email(email)

        mock_session.query.assert_called_once_with(DbUser)
        mock_query.filter.assert_called_once()
        assert result is not None
        assert isinstance(result, DomainUser)

    def test_get_by_email_not_found(self, repository, mock_session):
        """Test search user por email cuando no existe."""
        email = Email(value="nonexistent@example.com")
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        result = repository.get_by_email(email)

        mock_session.query.assert_called_once_with(DbUser)
        assert result is None

    def test_create_user_success(self, repository, mock_session, db_role, db_user):
        """Test create user exitosamente."""
        firebase_uid = "12345678-1234-5678-1234-567812345678"
        email = Email(value="newuser@example.com")
        role = RoleEnum.MANAGER
        document_number = DocumentNumber(value="9876543210", doc_type=DocumentEnum.CE)
        state = StateUser(value=StateEnum.ACTIVE)

        # Mock para las consultas - primera es para el rol, segunda para verificar duplicados
        def mock_query_side_effect(model):
            mock_q = Mock()
            mock_q.filter = Mock(return_value=mock_q)
            if model == DbRole:
                mock_q.first = Mock(return_value=db_role)
            else:  # DbUser - no existe user duplicado
                mock_q.first = Mock(return_value=None)
            return mock_q
        
        mock_session.query.side_effect = mock_query_side_effect

        # Mock para add, commit, refresh
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.refresh = Mock()

        # Configurar el db_user que se "creara"
        db_user.firebase_uid = firebase_uid
        db_user.email = str(email.value)
        db_user.document_type = document_number.doc_type.value
        db_user.state = state.value.value

        # Mock para simular que refresh actualiza el objeto
        def refresh_side_effect(user):
            user.id = 9876543210

        mock_session.refresh.side_effect = refresh_side_effect

        result = repository.create_user(
            firebase_uid, email, role, document_number, state,
            first_name="Juan",
            last_name="Perez"
        )

        # Verificar que se agrego, confirmo y refresco
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

        assert isinstance(result, DomainUser)

    def test_create_user_role_not_found(self, repository, mock_session):
        """Test create user cuando el rol no existe."""
        firebase_uid = "new-firebase-uid"
        email = Email(value="newuser@example.com")
        role = RoleEnum.MANAGER
        document_number = DocumentNumber(value="9876543210", doc_type=DocumentEnum.CE)
        state = StateUser(value=StateEnum.ACTIVE)

        # Mock para las consultas - rol no existe
        def mock_query_side_effect(model):
            mock_q = Mock()
            mock_q.filter = Mock(return_value=mock_q)
            mock_q.first = Mock(return_value=None)  # Rol no encontrado
            return mock_q
        
        mock_session.query.side_effect = mock_query_side_effect

        with pytest.raises(ValueError, match="Role 'MANAGER' does not exist"):
            repository.create_user(
                firebase_uid, email, role, document_number, state,
                first_name="Test",
                last_name="User"
            )

        # Verificar que no se llamaron add, commit, refresh
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()
        mock_session.refresh.assert_not_called()

    def test_db_user_to_domain_all_document_types(self, repository, db_user, db_role):
        """Test conversion con todos los tipos de document."""
        for doc_type in DocumentEnum:
            db_user.document_type = doc_type.value
            domain_user = repository._db_user_to_domain(db_user)
            assert domain_user.identification_number.doc_type == DocumentEnum.CC

    def test_db_user_to_domain_all_roles(self, repository, db_user):
        """Test conversion con todos los roles."""
        for role in RoleEnum:
            mock_role = Mock()
            mock_role.name = role.value
            db_user.role = mock_role
            db_user.role_name = role.value  # Tambien actualizar role_name
            domain_user = repository._db_user_to_domain(db_user)
            assert domain_user.role == role

    def test_db_user_to_domain_all_states(self, repository, db_user, db_role):
        """Test conversion con todos los estados."""
        for state in StateEnum:
            db_user.state = state.value
            domain_user = repository._db_user_to_domain(db_user)
            assert domain_user.state.value == state

    def test_create_user_all_roles(self, repository, mock_session, db_role, db_user):
        """Test create user con todos los roles."""
        firebase_uid = "12345678-1234-5678-1234-567812345678"
        email = Email(value="test@example.com")
        state = StateUser(value=StateEnum.ACTIVE)

        for idx, role in enumerate(RoleEnum):
            # Resetear mocks
            mock_session.reset_mock()
            
            # Usar ID unico para cada iteracion
            document_number = DocumentNumber(value=f"12345678{idx:02d}", doc_type=DocumentEnum.CC)

            # Mock para las consultas
            def mock_query_side_effect(model):
                mock_q = Mock()
                mock_q.filter = Mock(return_value=mock_q)
                if model == DbRole:
                    mock_q.first = Mock(return_value=db_role)
                else:  # DbUser - no existe user duplicado
                    mock_q.first = Mock(return_value=None)
                return mock_q
            
            mock_session.query.side_effect = mock_query_side_effect

            # Mock para add, commit, refresh
            mock_session.add = Mock()
            mock_session.commit = Mock()
            mock_session.refresh = Mock()

            result = repository.create_user(
                firebase_uid, email, role, document_number, state,
                first_name="Test",
                last_name="User"
            )

            assert isinstance(result, DomainUser)
            mock_session.add.assert_called_once()
            mock_session.flush.assert_called_once()

    def test_create_user_all_document_types(self, repository, mock_session, db_role):
        """Test create user con todos los tipos de document."""
        firebase_uid = "12345678-1234-5678-1234-567812345678"
        email = Email(value="test@example.com")
        role = RoleEnum.EMPLOYEE
        state = StateUser(value=StateEnum.ACTIVE)

        for idx, doc_type in enumerate(DocumentEnum):
            # Resetear mocks
            mock_session.reset_mock()

            # Usar ID unico para cada iteracion
            document_number = DocumentNumber(value=f"98765432{idx:02d}", doc_type=doc_type)

            # Mock para las consultas
            def mock_query_side_effect(model):
                mock_q = Mock()
                mock_q.filter = Mock(return_value=mock_q)
                if model == DbRole:
                    mock_q.first = Mock(return_value=db_role)
                else:  # DbUser - no existe user duplicado
                    mock_q.first = Mock(return_value=None)
                return mock_q
            
            mock_session.query.side_effect = mock_query_side_effect

            # Mock para add, commit, refresh
            mock_session.add = Mock()
            mock_session.commit = Mock()
            mock_session.refresh = Mock()

            result = repository.create_user(
                firebase_uid, email, role, document_number, state,
                first_name="Test",
                last_name="User"
            )

            assert isinstance(result, DomainUser)
            mock_session.add.assert_called_once()

    def test_create_user_all_states(self, repository, mock_session, db_role):
        """Test create user con todos los estados."""
        firebase_uid = "12345678-1234-5678-1234-567812345678"
        email = Email(value="test@example.com")
        role = RoleEnum.EMPLOYEE

        for idx, state_enum in enumerate(StateEnum):
            # Resetear mocks
            mock_session.reset_mock()
            
            # Usar ID unico para cada iteracion
            document_number = DocumentNumber(value=f"55555555{idx:02d}", doc_type=DocumentEnum.CC)
            state = StateUser(value=state_enum)

            # Mock para las consultas
            def mock_query_side_effect(model):
                mock_q = Mock()
                mock_q.filter = Mock(return_value=mock_q)
                if model == DbRole:
                    mock_q.first = Mock(return_value=db_role)
                else:  # DbUser - no existe user duplicado
                    mock_q.first = Mock(return_value=None)
                return mock_q
            
            mock_session.query.side_effect = mock_query_side_effect

            # Mock para add, commit, refresh
            mock_session.add = Mock()
            mock_session.commit = Mock()
            mock_session.refresh = Mock()

            result = repository.create_user(
                firebase_uid, email, role, document_number, state,
                first_name="Test",
                last_name="User"
            )

            assert isinstance(result, DomainUser)
            mock_session.flush.assert_called_once()
