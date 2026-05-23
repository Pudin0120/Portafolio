import uuid
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import select, func, cast, String

from app.domain.models.user import RoleEnum
from app.domain.models.user import User as DomainUser
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.document_number import DocumentEnum, DocumentNumber
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateEnum, StateUser
from app.infrastructure.adapters.db.models import Role as DbRole
from app.infrastructure.adapters.db.models import User as DbUser


class PostgresUserRepository(UserRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _db_user_to_domain(self, db_user: DbUser) -> DomainUser:
        """Convierte un user de base de datos a modelo de dominio."""
        # Mapear el rol de la BD al enum del dominio
        role_name = db_user.role_name if db_user.role_name is not None else RoleEnum.EMPLOYEE.value
        role_enum = RoleEnum(role_name) if isinstance(role_name, str) else RoleEnum.EMPLOYEE

        return DomainUser(
            identification_number=DocumentNumber(
                value=str(db_user.document_number), doc_type=DocumentEnum.CC
            ),
            role=role_enum,
            first_name=str(db_user.first_name),
            last_name=str(db_user.last_name),
            email=Email(value=str(db_user.email)),
            state=StateUser(value=StateEnum(str(db_user.state))),
            firebase_uid=str(db_user.firebase_uid),
            id=db_user.id,
            tenant_id=db_user.tenant_id,
            phone=str(db_user.phone) if db_user.phone is not None else None,
        )

    def get_by_firebase_uid(self, firebase_uid: str) -> Optional[DomainUser]:
        try:
            user = (
                self.db_session.query(DbUser)
                .filter(DbUser.firebase_uid == firebase_uid)
                .first()
            )
            if user:
                return self._db_user_to_domain(user)
            return None
        except Exception:
            self.db_session.rollback()
            raise
    
    def get_by_role(self, role: RoleEnum) -> List[DomainUser]:
    # Obtener el valor de busqueda (el valor del Enum es 'employee')
        role_value = str(role.value) 
    
    # Imprimir (para depuracion, puedes eliminarlo despues)
        print(f"Buscando el valor de rol con ILIKE: {role_value}")
    
    # 1. Create la sentencia SELECT (Sintaxis 2.0)
        stmt = select(DbUser).where(
        #  CORRECCION: Usar .ilike() para ignorar mayusculas/minusculas.
        # Esto generara la clausula SQL "WHERE role_name ILIKE 'employee'".
        DbUser.role_name.ilike(role_value)
        ).order_by(DbUser.created_at.desc())
    
    # 2. Ejecutar la consulta
        models = self.db_session.execute(stmt).scalars().all()
        print(f"DEBUG A: Modelos de DB encontrados: {len(models)}")
        domain_users = [self._db_user_to_domain(model) for model in models]
        print(f"DEBUG B: Entidades de dominio mapeadas: {len(domain_users)}")
    # 3. Convertir y retornar
    # Si la lista esta vacia, devuelve [], si no, devuelve los users mapeados.
        return domain_users
    
    def get_all_except_super_admin(self) -> List[DomainUser]:
        """
        Obtiene todos los users excepto los SUPER_ADMIN.
        """
        stmt = select(DbUser).where(
            DbUser.role_name.ilike('SUPER_ADMIN') == False
        ).order_by(DbUser.created_at.desc())
        
        models = self.db_session.execute(stmt).scalars().all()
        domain_users = [self._db_user_to_domain(model) for model in models]
        return domain_users
    
    def get_by_identification_number(self, identification_number: str) -> Optional[DomainUser]:
        """Obtiene un user por su number de identificacion."""
        try:
            user = (
                self.db_session.query(DbUser)
                .filter(DbUser.document_number == identification_number)
                .first()
            )
            if user:
                return self._db_user_to_domain(user)
            return None
        except Exception:
            self.db_session.rollback()
            raise

    def update_user_state(self, identification_number: str, new_state: StateUser) -> DomainUser:
        """Actualiza el estado de un user."""
        try:
            user = (
                self.db_session.query(DbUser)
                .filter(DbUser.document_number == identification_number)
                .first()
            )
            if not user:
                raise ValueError(f"User with identification number {identification_number} not found")
            
            user.state = new_state.value.value
            self.db_session.commit()
            self.db_session.refresh(user)
            return self._db_user_to_domain(user)
        except Exception:
            self.db_session.rollback()
            raise

    def update_user(
        self,
        identification_number: str,
        first_name: str,
        last_name: str,
        phone: Optional[str],
        role: str,
    ) -> DomainUser:
        """Actualiza los datos de un user (excepto email y document)."""
        from app.domain.models.user import RoleEnum
        
        try:
            user = (
                self.db_session.query(DbUser)
                .filter(DbUser.document_number == identification_number)
                .first()
            )
            if not user:
                raise ValueError(f"User with identification number {identification_number} not found")
            
            user.first_name = first_name
            user.last_name = last_name
            user.phone = phone
            user.role_name = role
            
            self.db_session.commit()
            self.db_session.refresh(user)
            return self._db_user_to_domain(user)
        except Exception:
            self.db_session.rollback()
            raise
    

    def get_by_email(self, email: Email) -> Optional[DomainUser]:
        user = (
            self.db_session.query(DbUser)
            .filter(DbUser.email == str(email.value))
            .first()
        )
        if user:
            return self._db_user_to_domain(user)
        return None

    def create_user(
        self,
        firebase_uid: str,
        email: Email,
        role: RoleEnum,
        document_number: DocumentNumber,
        state: StateUser,
        first_name: str,
        last_name: str,
        tenant_id: Optional[uuid.UUID] = None,
        phone: Optional[str] = None,
    ) -> DomainUser:
        # Verificar que el rol existe en la base de datos
        db_role = (
            self.db_session.query(DbRole).filter(DbRole.name == role.value).first()
        )

        if not db_role:
            raise ValueError(f"Role '{role.value}' does not exist.")

        # Verificar si ya existe un user con este document_number
        existing_user = (
            self.db_session.query(DbUser)
            .filter(DbUser.document_number == document_number.value)
            .first()
        )
        if existing_user:
            raise ValueError(
                f"User with document number {document_number.value} already exists."
            )

        # Verificar si ya existe un user con este email
        existing_email_user = (
            self.db_session.query(DbUser)
            .filter(DbUser.email == str(email.value))
            .first()
        )
        if existing_email_user:
            raise ValueError(f"User with email {email.value} already exists.")

        # Create el user en la base de datos
        db_user = DbUser(
            firebase_uid=firebase_uid,
            document_number=document_number.value,
            email=str(email.value),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role_name=role.value,
            state=state.value.value,
            tenant_id=tenant_id
        )

        self.db_session.add(db_user)
        self.db_session.flush()  # Flush to get generated IDs and validate constraints
        self.db_session.refresh(db_user)
        return self._db_user_to_domain(db_user)
