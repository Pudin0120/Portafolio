import uuid

from app.application.dto.user_response_dto import UserResponseDTO
from app.application.mappers.user_mapper import UserMapper
from app.domain.models.user import RoleEnum, User
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


class TestUserMapper:
    """Tests para UserMapper."""

    def test_to_response_dto_basic(self):
        """Test conversion basica de user a DTO de respuesta."""
        user_uuid = uuid.uuid4()
        user = make_user(
            identification_number="12345678",
            doc_type=DocumentEnum.CC,
            role=RoleEnum.EMPLOYEE,
            first_name="Ana",
            last_name="Garcia",
            email="ana@example.com",
            state=StateEnum.ACTIVE,
            firebase_uid=user_uuid,
            phone="3001234567",
        )

        dto = UserMapper.to_response_dto(user)

        assert isinstance(dto, UserResponseDTO)
        assert dto.identification_number == "12345678"
        assert dto.document_type == "CC"
        assert dto.first_name == "Ana"
        assert dto.last_name == "Garcia"
        assert dto.email == "ana@example.com"
        assert dto.state == "A"
        assert dto.firebase_uid == str(user_uuid)
        assert dto.phone == "3001234567"
        assert dto.role == "EMPLOYEE"

    def test_to_response_dto_all_roles(self):
        """Test conversion con todos los roles disponibles."""
        base_user_data = {
            "identification_number": "87654321",
            "doc_type": DocumentEnum.CE,
            "first_name": "Carlos",
            "last_name": "Lopez",
            "email": "carlos@example.com",
            "state": StateEnum.INACTIVE,
        }

        # Test cada rol
        for role in RoleEnum:
            user = make_user(**base_user_data, role=role)
            dto = UserMapper.to_response_dto(user)
            assert dto.role == role.value

    def test_to_response_dto_all_document_types(self):
        """Test conversion con todos los tipos de document."""
        base_user_data = {
            "identification_number": "11223344",
            "role": RoleEnum.MANAGER,
            "first_name": "Maria",
            "last_name": "Rodriguez",
            "email": "maria@example.com",
            "state": StateEnum.ACTIVE,
        }

        # Test cada tipo de document
        for doc_type in DocumentEnum:
            user = make_user(**base_user_data, doc_type=doc_type)
            dto = UserMapper.to_response_dto(user)
            assert dto.document_type == doc_type.value

    def test_to_response_dto_all_states(self):
        """Test conversion con todos los estados."""
        base_user_data = {
            "identification_number": "55667788",
            "role": RoleEnum.SUPERVISOR,
            "first_name": "Luis",
            "last_name": "Martinez",
            "email": "luis@example.com",
        }

        # Test cada estado
        for state in StateEnum:
            user = make_user(**base_user_data, state=state)
            dto = UserMapper.to_response_dto(user)
            assert dto.state == state.value

    def test_to_response_dto_without_phone(self):
        """Test conversion cuando el user no tiene telefono."""
        user = make_user(phone=None)
        dto = UserMapper.to_response_dto(user)
        assert dto.phone is None

    def test_to_response_dto_with_phone(self):
        """Test conversion cuando el user tiene telefono."""
        user = make_user(phone="3109876543")
        dto = UserMapper.to_response_dto(user)
        assert dto.phone == "3109876543"

    def test_dto_full_name_property(self):
        """Test que el DTO tenga la propiedad full_name."""
        user = make_user(first_name="Pedro", last_name="Gonzalez")
        dto = UserMapper.to_response_dto(user)
        assert dto.full_name == "Pedro Gonzalez"

    def test_dto_is_active_property_active(self):
        """Test que el DTO detecte correctamente cuando esta active."""
        user = make_user(state=StateEnum.ACTIVE)
        dto = UserMapper.to_response_dto(user)
        assert dto.is_active is True

    def test_dto_is_active_property_inactive(self):
        """Test que el DTO detecte correctamente cuando esta inactive."""
        user = make_user(state=StateEnum.INACTIVE)
        dto = UserMapper.to_response_dto(user)
        assert dto.is_active is False

    def test_dto_email_validation(self):
        """Test que el DTO valide correctamente el email."""
        user = make_user(email="valid@example.com")
        dto = UserMapper.to_response_dto(user)
        assert str(dto.email) == "valid@example.com"

    def test_dto_firebase_uid_type(self):
        """Test que el firebase_uid sea del tipo correcto."""
        test_uuid = uuid.uuid4()
        user = make_user(firebase_uid=test_uuid)
        dto = UserMapper.to_response_dto(user)
        assert isinstance(dto.firebase_uid, str)
        assert dto.firebase_uid == str(test_uuid)

    def test_to_response_dto_super_admin_role(self):
        """Test conversion especifica para rol SUPER_ADMIN."""
        user = make_user(
            role=RoleEnum.SUPER_ADMIN,
            first_name="Admin",
            last_name="Sistema",
            email="admin@system.com",
        )
        dto = UserMapper.to_response_dto(user)
        assert dto.role == "SUPER_ADMIN"
        assert dto.first_name == "Admin"
        assert dto.last_name == "Sistema"

    def test_dto_model_validation(self):
        """Test que el DTO de respuesta cumpla con las validaciones de Pydantic."""
        user = make_user(
            identification_number="1234567890",
            first_name="Test",
            last_name="User",
            email="test@example.com",
        )

        dto = UserMapper.to_response_dto(user)

        # Verificar que es una instancia valid de Pydantic
        assert isinstance(dto, UserResponseDTO)

        # Verificar que se puede serializar/deserializar
        dto_dict = dto.model_dump()
        assert "identification_number" in dto_dict
        assert "email" in dto_dict
        assert "role" in dto_dict

        # Verificar que se puede create desde dict
        new_dto = UserResponseDTO(**dto_dict)
        assert new_dto.identification_number == dto.identification_number
        assert new_dto.email == dto.email
