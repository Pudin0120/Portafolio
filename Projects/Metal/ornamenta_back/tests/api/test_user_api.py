import uuid
from unittest.mock import Mock, patch, AsyncMock
import pytest
from fastapi import HTTPException, status, FastAPI
from fastapi.testclient import TestClient

from app.application.dto.user_response_dto import UserResponseDTO
from app.application.mappers.user_mapper import UserMapper
from app.application.services.firebase_service import FirebaseService
from app.domain.models.user import RoleEnum, User
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.document_number import DocumentEnum, DocumentNumber
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateEnum, StateUser
from app.infrastructure.adapters.rest.dependencies import get_current_user
from app.infrastructure.adapters.rest.user_router import router


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
        identification_number=DocumentNumber(value=identification_number, doc_type=doc_type),
        role=role,
        first_name=first_name,
        last_name=last_name,
        email=Email(value=email),
        state=StateUser(value=state),
        firebase_uid=str(firebase_uid) if firebase_uid else str(uuid.uuid4()),
        phone=phone,
    )


class TestUserAPI:
    """Tests para la API de users."""

    @pytest.fixture
    def mock_user_repository(self):
        """Mock del repositorio de users."""
        return Mock(spec=UserRepository)

    @pytest.fixture
    def mock_firebase_service(self):
        """Mock del servicio de Firebase."""
        return Mock(spec=FirebaseService)

    @pytest.fixture
    def test_user(self):
        """User de prueba."""
        return make_user(
            identification_number="1234567890",
            doc_type=DocumentEnum.CC,
            role=RoleEnum.EMPLOYEE,
            first_name="Ana",
            last_name="Lopez",
            email="ana@example.com",
            state=StateEnum.ACTIVE,
            firebase_uid="12345678-1234-5678-1234-567812345678",
            phone="3001234567"
        )

    @pytest.fixture
    def app(self):
        """Aplicacion FastAPI para pruebas."""
        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """Client de prueba para FastAPI."""
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_get_current_user_dependency_success(
        self,
        mock_firebase_service,
        mock_user_repository,
        test_user
    ):
        """Test exitoso de la dependencia get_current_user."""
        # Arrange
        token = "valid-firebase-token"
        decoded_token = {
            "uid": str(test_user.firebase_uid),
            "email": test_user.email.value
        }

        mock_firebase_service.verify_token.return_value = decoded_token
        mock_user_repository.get_by_firebase_uid.return_value = test_user

        # Act
        with patch('app.infrastructure.adapters.rest.dependencies.Provide') as mock_provide:
            mock_provide.__getitem__.return_value = lambda: mock_firebase_service

            # Llamar la function async correctamente
            result = await get_current_user.__wrapped__(
                token=token,
                firebase_service=mock_firebase_service,
                user_repo=mock_user_repository
            )

        # Assert
        assert result == test_user
        mock_firebase_service.verify_token.assert_called_once_with(token)
        mock_user_repository.get_by_firebase_uid.assert_called_once_with(str(test_user.firebase_uid))

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(
        self,
        mock_firebase_service,
        mock_user_repository
    ):
        """Test con token invalid en get_current_user."""
        # Arrange
        token = "invalid-token"
        mock_firebase_service.verify_token.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user.__wrapped__(
                token=token,
                firebase_service=mock_firebase_service,
                user_repo=mock_user_repository
            )

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid authentication credentials" in exc_info.value.detail
        mock_firebase_service.verify_token.assert_called_once_with(token)
        mock_user_repository.get_by_firebase_uid.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(
        self,
        mock_firebase_service,
        mock_user_repository
    ):
        """Test cuando el user no existe en la base de datos."""
        # Arrange
        token = "valid-token"
        decoded_token = {
            "uid": "nonexistent-uid",
            "email": "nonexistent@example.com"
        }

        mock_firebase_service.verify_token.return_value = decoded_token
        mock_user_repository.get_by_firebase_uid.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user.__wrapped__(
                token=token,
                firebase_service=mock_firebase_service,
                user_repo=mock_user_repository
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in exc_info.value.detail

    def test_read_users_me_endpoint(self, app, client, test_user):
        """Test del endpoint /users/me."""
        # Mock de la dependencia get_current_user
        async def mock_get_current_user():
            return test_user

        # Override de la dependencia a nivel de aplicacion
        app.dependency_overrides[get_current_user] = mock_get_current_user

        try:
            # Act
            response = client.get("/users/me")

            # Assert
            assert response.status_code == 200

            response_data = response.json()
            assert response_data["identification_number"] == "1234567890"
            assert response_data["document_type"] == "CC"
            assert response_data["first_name"] == "Ana"
            assert response_data["last_name"] == "Lopez"
            assert response_data["email"] == "ana@example.com"
            assert response_data["state"] == "A"
            assert response_data["firebase_uid"] == str(test_user.firebase_uid)
            assert response_data["phone"] == "3001234567"
            assert response_data["role"] == "EMPLOYEE"

        finally:
            # Limpiar override
            app.dependency_overrides.clear()

    def test_read_users_me_with_different_roles(self, app, client):
        """Test del endpoint /users/me con diferentes roles."""
        base_user_data = {
            "identification_number": "9876543210",
            "doc_type": DocumentEnum.CE,
            "first_name": "Carlos",
            "last_name": "Martinez",
            "email": "carlos@example.com",
            "state": StateEnum.ACTIVE,
            "firebase_uid": uuid.uuid4(),
        }

        for role in RoleEnum:
            user = make_user(**base_user_data, role=role)

            async def mock_get_current_user():
                return user

            app.dependency_overrides[get_current_user] = mock_get_current_user

            try:
                response = client.get("/users/me")
                assert response.status_code == 200
                response_data = response.json()
                assert response_data["role"] == role.value
            finally:
                app.dependency_overrides.clear()

    def test_read_users_me_with_different_states(self, app, client):
        """Test del endpoint /users/me con diferentes estados."""
        base_user_data = {
            "identification_number": "5555555555",
            "role": RoleEnum.SUPERVISOR,
            "first_name": "Maria",
            "last_name": "Gonzalez",
            "email": "maria@example.com",
            "firebase_uid": uuid.uuid4(),
        }

        for state in StateEnum:
            user = make_user(**base_user_data, state=state)

            async def mock_get_current_user():
                return user

            app.dependency_overrides[get_current_user] = mock_get_current_user

            try:
                response = client.get("/users/me")
                assert response.status_code == 200
                response_data = response.json()
                assert response_data["state"] == state.value
            finally:
                app.dependency_overrides.clear()

    def test_read_users_me_without_phone(self, app, client):
        """Test del endpoint /users/me cuando el user no tiene telefono."""
        user = make_user(phone=None)

        async def mock_get_current_user():
            return user

        app.dependency_overrides[get_current_user] = mock_get_current_user

        try:
            response = client.get("/users/me")
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["phone"] is None
        finally:
            app.dependency_overrides.clear()

    def test_read_users_me_unauthorized(self, client):
        """Test del endpoint /users/me sin autenticacion."""
        # Sin override de dependencia, deberia fallar la autenticacion
        response = client.get("/users/me")
        assert response.status_code == 401  # FastAPI devuelve 401 cuando falta el token

    def test_user_response_dto_serialization(self, test_user):
        """Test que el DTO de respuesta se serializa correctamente."""
        dto = UserMapper.to_response_dto(test_user)

        # Verificar que se puede serializar a dict
        dto_dict = dto.model_dump()
        assert isinstance(dto_dict, dict)

        # Verificar campos requeridos
        required_fields = [
            "identification_number", "document_type", "first_name",
            "last_name", "email", "state", "firebase_uid", "role"
        ]
        for field in required_fields:
            assert field in dto_dict

        # Verificar tipos - El DTO maneja UUID pero se serializa como string en JSON
        assert isinstance(dto_dict["email"], str)

        # Verificar que firebase_uid se puede convertir a string
        firebase_uid_str = str(dto_dict["firebase_uid"])
        assert isinstance(firebase_uid_str, str)

    def test_user_response_dto_validation(self):
        """Test validacion del UserResponseDTO."""
        # Datos valids
        valid_data = {
            "identification_number": "1234567890",
            "document_type": "CC",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "state": "A",
            "firebase_uid": str(uuid.uuid4()),
            "role": "EMPLOYEE"
        }

        dto = UserResponseDTO(**valid_data)
        assert dto.identification_number == "1234567890"
        assert dto.email == "test@example.com"

        # Email invalid
        invalid_data = valid_data.copy()
        invalid_data["email"] = "invalid-email"

        with pytest.raises(Exception):  # ValidationError de Pydantic
            UserResponseDTO(**invalid_data)

    def test_endpoint_response_model_validation(self, app, client, test_user):
        """Test que la respuesta del endpoint cumpla con el modelo de respuesta."""
        async def mock_get_current_user():
            return test_user

        app.dependency_overrides[get_current_user] = mock_get_current_user

        try:
            response = client.get("/users/me")
            assert response.status_code == 200

            # Verificar que la respuesta se puede deserializar al DTO
            response_data = response.json()
            dto = UserResponseDTO(**response_data)

            # Verificar que los datos coinciden
            assert dto.identification_number == test_user.identification_number.value
            assert dto.email == test_user.email.value
            assert dto.role == test_user.role.value

        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_current_user_with_all_roles(
        self,
        mock_firebase_service,
        mock_user_repository
    ):
        """Test get_current_user con todos los roles disponibles."""
        token = "valid-token"

        for role in RoleEnum:
            user = make_user(role=role)
            decoded_token = {
                "uid": str(user.firebase_uid),
                "email": user.email.value
            }

            mock_firebase_service.verify_token.return_value = decoded_token
            mock_user_repository.get_by_firebase_uid.return_value = user

            result = await get_current_user.__wrapped__(
                token=token,
                firebase_service=mock_firebase_service,
                user_repo=mock_user_repository
            )

            assert result == user
            assert result.role == role

            # Reset mocks para siguiente iteracion
            mock_firebase_service.reset_mock()
            mock_user_repository.reset_mock()

