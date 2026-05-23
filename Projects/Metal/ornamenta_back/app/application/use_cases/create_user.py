import logging

import firebase_admin.auth as auth
from fastapi import HTTPException, status

from app.application.dto.create_user_request_dto import CreateUserRequestDTO
from app.application.services.firebase_service import FirebaseService
from app.domain.models.user import RoleEnum, User
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.document_number import DocumentEnum, DocumentNumber
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateEnum, StateUser

logger = logging.getLogger(__name__)


class CreateUser:
    def __init__(
        self, user_repository: UserRepository, firebase_service: FirebaseService
    ):
        self.user_repository = user_repository
        self.firebase_service = firebase_service

    def execute(self, request: CreateUserRequestDTO, admin_user: User = None) -> User:
        # Log de la information recibida
        logger.info("=== CREATE USER REQUEST RECEIVED ===")
        logger.info(f"Request data: {request.model_dump()}")
        logger.info(f"Identification number: {request.identification_number}")
        logger.info(f"Document type: {request.document_type}")
        logger.info(f"First name: {request.first_name}")
        logger.info(f"Last name: {request.last_name}")
        logger.info(f"Email: {request.email}")
        logger.info(f"Phone: {request.phone}")
        logger.info(
            f"Password: {'*' * len(request.password) if request.password else 'None'}"
        )
        logger.info(f"Role: {request.role}")
        logger.info(f"State: {request.state}")
        logger.info(f"Firebase UID: {request.firebase_uid}")
        logger.info("=====================================")

        # 1. Check if user already exists in Firebase or DB
        try:
            firebase_user = auth.get_user_by_email(str(request.email))
            if firebase_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A user with this email already exists in Firebase.",
                )
        except auth.UserNotFoundError:
            pass  # User does not exist, which is what we want

        db_user = self.user_repository.get_by_email(Email(value=request.email))
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists in the database.",
            )

        # 2. Create user in Firebase Authentication
        try:
            new_firebase_user = auth.create_user(
                email=str(request.email), password=request.password, email_verified=True
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user in Firebase: {e}",
            )

        # 3. Create user in PostgreSQL database with default values
        # Map frontend role to RoleEnum
        role_mapping = {
            "empleado": RoleEnum.EMPLOYEE,
            "supervisor": RoleEnum.SUPERVISOR,
            "gerente": RoleEnum.MANAGER,
            "admin": RoleEnum.SUPER_ADMIN,
            # Agregar mapeo para valores en mayusculas que vienen del frontend
            "EMPLOYEE": RoleEnum.EMPLOYEE,
            "SUPERVISOR": RoleEnum.SUPERVISOR,
            "MANAGER": RoleEnum.MANAGER,
            "SUPER_ADMIN": RoleEnum.SUPER_ADMIN,
        }

        # Check if the role exists in the mapping
        logger.info(f"Processing role: '{request.role}'")
        logger.info(f"Available role mappings: {list(role_mapping.keys())}")

        if request.role in role_mapping:
            role_enum = role_mapping[request.role]
            logger.info(
                f"Role found in mapping (exact match): {request.role} -> {role_enum}"
            )
        elif request.role.lower() in role_mapping:
            role_enum = role_mapping[request.role.lower()]
            logger.info(
                f"Role found in mapping (lowercase): {request.role.lower()} -> {role_enum}"
            )
        else:
            # Try direct conversion if not in mapping
            try:
                role_enum = RoleEnum(request.role.upper())
                logger.info(
                    f"Role converted directly: {request.role.upper()} -> {role_enum}"
                )
            except ValueError as e:
                logger.error(f"Invalid role: {request.role}. Error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid role: {request.role}. Valid roles are: {', '.join([k for k in role_mapping.keys() if not k.isupper()])} or {', '.join([r.value for r in RoleEnum])}",
                )

        # Validar permisos para create user con el rol especificado
        if admin_user:
            if not admin_user.can_create_user_with_role(role_enum):
                logger.error(
                    f"User {admin_user.identification_number} (role: {admin_user.role}) cannot create user with role {role_enum}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"No tiene permisos para create un user con el rol {role_enum.value}. "
                    f"Solo SUPER_ADMIN puede create MANAGER. MANAGER puede create MANAGER, SUPERVISOR y EMPLOYEE.",
                )

        # Create document number from request data
        # Map frontend document type to backend enum
        document_type_mapping = {
            "Cedula de Ciudadania": DocumentEnum.CC,
            "Cedula de Extranjeria": DocumentEnum.CE,
            "NIT": DocumentEnum.NIT,
            "CC": DocumentEnum.CC,
            "CE": DocumentEnum.CE,
            "NI": DocumentEnum.NIT,
        }

        logger.info(f"Processing document type: '{request.document_type}'")
        logger.info(
            f"Available document type mappings: {list(document_type_mapping.keys())}"
        )

        doc_type = document_type_mapping.get(request.document_type)
        if not doc_type:
            logger.error(f"Invalid document type: {request.document_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid document type: {request.document_type}. Valid types are: {', '.join(document_type_mapping.keys())}",
            )
        logger.info(f"Document type mapped: {request.document_type} -> {doc_type}")

        logger.info(
            f"Creating DocumentNumber with value: '{request.identification_number}' and type: {doc_type}"
        )
        try:
            document_number = DocumentNumber(
                value=request.identification_number, doc_type=doc_type
            )
            logger.info(f"DocumentNumber created successfully: {document_number}")
        except Exception as e:
            logger.error(f"Error creating DocumentNumber: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid document number: {e}",
            )

        # Map frontend state to backend enum
        state_mapping = {
            "Active": StateEnum.ACTIVE,
            "Inactive": StateEnum.INACTIVE,
            "A": StateEnum.ACTIVE,
            "I": StateEnum.INACTIVE,
        }

        logger.info(f"Processing state: '{request.state}'")
        logger.info(f"Available state mappings: {list(state_mapping.keys())}")

        state_value = state_mapping.get(request.state)
        if not state_value:
            logger.error(f"Invalid state: {request.state}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid state: {request.state}. Valid states are: {', '.join(state_mapping.keys())}",
            )
        logger.info(f"State mapped: {request.state} -> {state_value}")

        logger.info(f"Creating StateUser with value: {state_value}")
        try:
            state = StateUser(value=state_value)
            logger.info(f"StateUser created successfully: {state}")
        except Exception as e:
            logger.error(f"Error creating StateUser: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid state: {e}"
            )

        logger.info("=== CREATING USER IN DATABASE ===")
        logger.info(f"Firebase UID: {new_firebase_user.uid}")
        logger.info(f"Email: {new_firebase_user.email}")
        logger.info(f"Role: {role_enum}")
        logger.info(f"Document Number: {document_number}")
        logger.info(f"State: {state}")
        logger.info(f"First Name: {request.first_name}")
        logger.info(f"Last Name: {request.last_name}")
        logger.info(f"Phone: {request.phone}")
        logger.info("==================================")

        try:
            # Seteamos el tenant_id del admin que crea el user o el tenant_id por defecto
            tenant_id = admin_user.tenant_id if admin_user else None
            
            new_db_user = self.user_repository.create_user(
                firebase_uid=new_firebase_user.uid,
                email=Email(value=new_firebase_user.email),
                role=role_enum,
                document_number=document_number,
                state=state,
                first_name=request.first_name,
                last_name=request.last_name,
                phone=request.phone,
                tenant_id=tenant_id
            )
            
            # 4. Set custom claims in Firebase (tenant_id)
            # Esto permite que el token de Firebase ya traiga el tenant_id
            if new_db_user.tenant_id:
                self.firebase_service.set_custom_claims(
                    new_db_user.firebase_uid, 
                    {"tenant_id": str(new_db_user.tenant_id)}
                )
            
            logger.info(f"User created successfully in database: {new_db_user}")
            return new_db_user
        except Exception as e:
            logger.error(f"Error creating user in database: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user in database: {e}",
            )
