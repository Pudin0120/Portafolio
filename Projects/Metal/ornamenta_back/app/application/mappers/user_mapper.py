from app.application.dto.user_response_dto import UserResponseDTO
from app.domain.models.user import User as DomainUser


class UserMapper:
    """Mapper para convertir entre modelos de dominio y DTOs."""

    @staticmethod
    def to_response_dto(domain_user: DomainUser) -> UserResponseDTO:
        """Convierte un user de dominio a DTO de respuesta."""
        return UserResponseDTO(
            identification_number=str(domain_user.identification_number.value),
            document_type=domain_user.identification_number.doc_type.value,
            first_name=domain_user.first_name,
            last_name=domain_user.last_name,
            email=str(domain_user.email.value),
            state=domain_user.state.value.value,
            firebase_uid=str(domain_user.firebase_uid),
            phone=domain_user.phone,
            role=domain_user.role.value,
        )
