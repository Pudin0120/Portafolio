import uuid
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from app.application.dto.create_user_request_dto import CreateUserRequestDTO
from app.application.services.firebase_service import FirebaseService
from app.application.use_cases.create_user import CreateUser
from app.domain.models.user import RoleEnum, User
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.document_number import DocumentEnum, DocumentNumber
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateEnum, StateUser


def make_user(
    identification_number="1234567890",
    doc_type=DocumentEnum.CC,
    role=RoleEnum.EMPLOYEE,
    first_name="Juan",
    last_name="Perez",
    email="juan@example.com",
    state=StateEnum.ACTIVE,
    firebase_uid=None,
    phone=None,
) -> User:
    """Factory helper para create un user de prueba."""
    return User(
        identification_number=DocumentNumber(
            value=identification_number, doc_type=doc_type
        ),
        role=role,
        first_name=first_name,
        last_name=last_name,
        email=Email(value=email),
        state=StateUser(value=state),
        firebase_uid=firebase_uid or uuid.uuid4(),
        phone=phone,
    )


class TestFirebaseService:
    """Tests para FirebaseService."""

    @pytest.fixture
    def firebase_service(self):
        """Mock del servicio de Firebase."""
        return Mock(spec=FirebaseService)

    def test_verify_token_success(self, firebase_service):
        """Test verificacion exitosa de token."""
        firebase_service.verify_token.return_value = {
            "uid": "test-uid",
            "email": "test@example.com",
        }

        result = firebase_service.verify_token("valid-token")

        assert result["uid"] == "test-uid"
        assert result["email"] == "test@example.com"
        firebase_service.verify_token.assert_called_once_with("valid-token")

    def test_verify_token_invalid(self, firebase_service):
        """Test verificacion de token invalid."""
        firebase_service.verify_token.return_value = None

        result = firebase_service.verify_token("invalid-token")

        assert result is None

    def test_create_user_success(self, firebase_service):
        """Test creation exitosa de user en Firebase."""
        firebase_service.create_user.return_value = "new-firebase-uid"

        uid = firebase_service.create_user("test@example.com", "password123")

        assert uid == "new-firebase-uid"
        firebase_service.create_user.assert_called_once_with(
            "test@example.com", "password123"
        )

    def test_create_user_failure(self, firebase_service):
        """Test fallo en creation de user en Firebase."""
        firebase_service.create_user.side_effect = Exception("Firebase error")

        with pytest.raises(Exception, match="Firebase error"):
            firebase_service.create_user("test@example.com", "password123")


class TestCreateUser:
    """Tests para el caso de uso CreateUser."""

    @pytest.fixture
    def mock_user_repository(self):
        """Mock del repositorio de users."""
        return Mock(spec=UserRepository)

    @pytest.fixture
    def mock_firebase_service(self):
        """Mock del servicio de Firebase."""
        return Mock(spec=FirebaseService)

    @pytest.fixture
    def create_user_use_case(self, mock_user_repository, mock_firebase_service):
        """Instancia del caso de uso con mocks."""
        return CreateUser(mock_user_repository, mock_firebase_service)

    @pytest.fixture
    def valid_request(self):
        """Request DTO valid para create user."""
        return CreateUserRequestDTO(
            identification_number="1234567890",
            document_type="CC",
            first_name="Nuevo",
            last_name="User",
            email="newuser@example.com",
            state="A",
            phone="3001234567",
            password="securepassword123",
            role="EMPLOYEE"
        )

    def test_create_user_success(
        self,
        create_user_use_case,
        mock_user_repository,
        mock_firebase_service,
        valid_request,
    ):
        """Test creation exitosa de user completo."""
        # Arrange
        firebase_user_mock = Mock()
        firebase_user_mock.uid = "firebase-uid-123"
        firebase_user_mock.email = "newuser@example.com"

        expected_user = make_user(
            email="newuser@example.com",
            firebase_uid=uuid.UUID("12345678-1234-5678-1234-567812345678"),
        )

        # Mocks
        mock_user_repository.get_by_email.return_value = None
        mock_user_repository.create_user.return_value = expected_user

        # Patch Firebase auth calls
        with patch("firebase_admin.auth.get_user_by_email") as mock_get_user, patch(
            "firebase_admin.auth.create_user"
        ) as mock_create_user:

            # User no existe en Firebase (Firebase lanza UserNotFoundError)
            from firebase_admin.auth import UserNotFoundError
            mock_get_user.side_effect = UserNotFoundError("User not found")
            mock_create_user.return_value = firebase_user_mock

            # Act
            result = create_user_use_case.execute(valid_request)

            # Assert
            assert result == expected_user
            mock_user_repository.get_by_email.assert_called_once()
            mock_user_repository.create_user.assert_called_once()
            mock_create_user.assert_called_once()

    def test_create_user_email_exists_in_firebase(
        self, create_user_use_case, valid_request
    ):
        """Test cuando el email ya existe en Firebase."""
        firebase_user_mock = Mock()
        firebase_user_mock.uid = "existing-uid"

        with patch("firebase_admin.auth.get_user_by_email") as mock_get_user:
            mock_get_user.return_value = firebase_user_mock

            with pytest.raises(HTTPException) as exc_info:
                create_user_use_case.execute(valid_request)

            assert exc_info.value.status_code == 409
            assert "already exists in Firebase" in exc_info.value.detail

    def test_create_user_email_exists_in_db(
        self, create_user_use_case, mock_user_repository, valid_request
    ):
        """Test cuando el email ya existe en la base de datos."""
        existing_user = make_user(email="newuser@example.com")
        mock_user_repository.get_by_email.return_value = existing_user

        with patch("firebase_admin.auth.get_user_by_email") as mock_get_user:
            from firebase_admin.auth import UserNotFoundError
            mock_get_user.side_effect = UserNotFoundError("User not found")

            with pytest.raises(HTTPException) as exc_info:
                create_user_use_case.execute(valid_request)

            assert exc_info.value.status_code == 409
            assert "already exists in the database" in exc_info.value.detail

    def test_create_user_firebase_creation_fails(
        self, create_user_use_case, mock_user_repository, valid_request
    ):
        """Test cuando falla la creation en Firebase."""
        mock_user_repository.get_by_email.return_value = None

        with patch("firebase_admin.auth.get_user_by_email") as mock_get_user, patch(
            "firebase_admin.auth.create_user"
        ) as mock_create_user:

            from firebase_admin.auth import UserNotFoundError
            mock_get_user.side_effect = UserNotFoundError("User not found")
            mock_create_user.side_effect = Exception("Firebase creation failed")

            with pytest.raises(HTTPException) as exc_info:
                create_user_use_case.execute(valid_request)

            assert exc_info.value.status_code == 500
            assert "Failed to create user in Firebase" in exc_info.value.detail

    def test_create_user_all_roles(
        self, create_user_use_case, mock_user_repository, mock_firebase_service
    ):
        """Test creation de user con todos los roles valids."""
        for role in ["EMPLOYEE", "SUPERVISOR", "MANAGER", "SUPER_ADMIN"]:
            request = CreateUserRequestDTO(
                identification_number=f"123456789{role[0]}",
                document_type="CC",
                first_name="Test",
                last_name="User",
                email=f"user-{role.lower()}@example.com",
                state="A",
                password="password123",
                role=role,
            )

            firebase_user_mock = Mock()
            firebase_user_mock.uid = f"firebase-uid-{role}"
            firebase_user_mock.email = request.email

            expected_user = make_user(email=request.email, role=RoleEnum(role))

            # Reset mocks
            mock_user_repository.reset_mock()

            # Setup mocks
            mock_user_repository.get_by_email.return_value = None
            mock_user_repository.create_user.return_value = expected_user

            with patch("firebase_admin.auth.get_user_by_email") as mock_get_user, patch(
                "firebase_admin.auth.create_user"
            ) as mock_create_user:

                from firebase_admin.auth import UserNotFoundError
                mock_get_user.side_effect = UserNotFoundError("User not found")
                mock_create_user.return_value = firebase_user_mock

                result = create_user_use_case.execute(request)

                assert result == expected_user
                assert result.role == RoleEnum(role)

    def test_create_user_request_dto_validation(self):
        """Test validacion del DTO de request."""
        # Email valid
        valid_dto = CreateUserRequestDTO(
            identification_number="1234567890",
            document_type="CC",
            first_name="Valid",
            last_name="User",
            email="valid@example.com",
            state="A",
            password="password123",
            role="EMPLOYEE"
        )
        assert valid_dto.email == "valid@example.com"
        assert valid_dto.password == "password123"
        assert valid_dto.role == "EMPLOYEE"

        # Email invalid deberia fallar en validacion de Pydantic
        with pytest.raises(Exception):  # ValidationError de Pydantic
            CreateUserRequestDTO(
                identification_number="1234567890",
                document_type="CC",
                first_name="Invalid",
                last_name="User",
                email="invalid-email",
                state="A",
                password="password123",
                role="EMPLOYEE"
            )

    def test_create_user_password_requirements(self, valid_request):
        """Test diferentes tipos de passwords."""
        # Password normal
        request1 = CreateUserRequestDTO(
            identification_number="1111111111",
            document_type="CC",
            first_name="User",
            last_name="One",
            email="user1@example.com",
            state="A",
            password="normalPassword123",
            role="EMPLOYEE"
        )
        assert request1.password == "normalPassword123"

        # Password con caracteres especiales
        request2 = CreateUserRequestDTO(
            identification_number="2222222222",
            document_type="CC",
            first_name="User",
            last_name="Two",
            email="user2@example.com",
            state="A",
            password="Complex@Pass123!",
            role="EMPLOYEE"
        )
        assert request2.password == "Complex@Pass123!"

        # Password corta (deberia ser valid en el DTO, Firebase decide si es aceptable)
        request3 = CreateUserRequestDTO(
            identification_number="3333333333",
            document_type="CC",
            first_name="User",
            last_name="Three",
            email="user3@example.com",
            state="A",
            password="123",
            role="EMPLOYEE"
        )
        assert request3.password == "123"

    def test_create_user_invalid_role_in_request(self):
        """Test request con rol invalid."""
        # Aunque el DTO permita cualquier string, el dominio deberia validar
        request = CreateUserRequestDTO(
            identification_number="9999999999",
            document_type="CC",
            first_name="Invalid",
            last_name="Role",
            email="test@example.com",
            state="A",
            password="password123",
            role="INVALID_ROLE"
        )
        assert request.role == "INVALID_ROLE"  # DTO permite cualquier string

    def test_create_user_email_case_sensitivity(
        self, create_user_use_case, mock_user_repository
    ):
        """Test manejo de mayusculas/minusculas en email."""
        request = CreateUserRequestDTO(
            identification_number="5555555555",
            document_type="CC",
            first_name="Test",
            last_name="User",
            email="Test.User@EXAMPLE.COM",
            state="A",
            password="password123",
            role="EMPLOYEE"
        )

        firebase_user_mock = Mock()
        firebase_user_mock.uid = "firebase-uid-case"
        firebase_user_mock.email = "test.user@example.com"  # Firebase normaliza

        expected_user = make_user(email="test.user@example.com")

        mock_user_repository.get_by_email.return_value = None
        mock_user_repository.create_user.return_value = expected_user

        with patch("firebase_admin.auth.get_user_by_email") as mock_get_user, patch(
            "firebase_admin.auth.create_user"
        ) as mock_create_user:

            from firebase_admin.auth import UserNotFoundError
            mock_get_user.side_effect = UserNotFoundError("User not found")
            mock_create_user.return_value = firebase_user_mock

            result = create_user_use_case.execute(request)

            assert result == expected_user
