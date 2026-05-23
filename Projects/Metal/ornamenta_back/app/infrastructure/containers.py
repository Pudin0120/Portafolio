from dependency_injector import containers, providers
from sqlalchemy.orm import Session
from app.config import settings
from app.infrastructure.adapters.db.database import SessionLocal
from app.application.services.firebase_service import FirebaseService
from app.application.services.product_service import ProductService
from app.application.services.material_price_service import MaterialPriceUpdateService
from app.application.services.product_creation_service import ProductCreationService
from app.application.services.composite_product_service import CompositeProductService
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository
from app.domain.repositories.material_type_repository import MaterialTypeRepository
from app.domain.repositories.material_repository import MaterialRepository
from app.domain.repositories.product_repository import ProductRepository
from app.domain.repositories.payroll_repository import PayrollRepository
from app.domain.repositories.payroll_history_repository import PayrollHistoryRepository
from app.domain.repositories.payroll_history_task_repository import PayrollHistoryTaskRepository
from app.domain.repositories.price_calculation_audit_repository import PriceCalculationAuditRepository
from app.infrastructure.adapters.repositories.postgres_user_repository import PostgresUserRepository
from app.infrastructure.adapters.repositories.postgres_unit_of_measure_repository import PostgresUnitOfMeasureRepository
from app.infrastructure.adapters.repositories.postgres_material_type_repository import PostgresMaterialTypeRepository
from app.infrastructure.adapters.repositories.postgres_material_repository import PostgresMaterialRepository
from app.infrastructure.adapters.repositories.postgres_product_repository import PostgresProductRepository
from app.infrastructure.adapters.repositories.postgres_client_repository import PostgresClientRepository
from app.infrastructure.adapters.repositories.postgres_work_repository import PostgresWorkRepository
from app.infrastructure.adapters.repositories.postgres_task_repository import PostgresTaskRepository
from app.infrastructure.adapters.repositories.payroll_repository import PostgresPayrollRepository
from app.infrastructure.adapters.repositories.payroll_history_repository import PostgresPayrollHistoryRepository
from app.infrastructure.adapters.repositories.payroll_history_task_repository import PostgresPayrollHistoryTaskRepository
from app.infrastructure.adapters.repositories.postgres_audit_repository import PostgresPriceCalculationAuditRepository
from app.infrastructure.adapters.db.database import get_db_session
from app.infrastructure.adapters.repositories.in_memory_task_assignment_repository import InMemoryTaskAssignmentRepository
from app.domain.repositories.task_assignment_repository import TaskAssignmentRepository
from app.domain.repositories.client_repository import ClientRepository
from app.domain.repositories.work_repository import WorkRepository
from app.domain.repositories.task_repository import TaskRepository
from app.application.use_cases.update_payroll_task import (
    UpdatePayrollHistoryOnTaskCompletionV2
)
from app.application.use_cases.template_use_cases import (
    GetTemplateRequirementsUseCase,
    InstantiateProductUseCase
)


class Container(containers.DeclarativeContainer):
    """
    Main DI container for the application.
    
    IMPORTANT: db_session uses providers.Resource to ensure proper transaction handling.
    The session is created per request and will commit/rollback at the end of the request.
    """
    config = providers.Configuration()
    config.from_dict(settings.model_dump())

    # Session per request - will commit at end of request
    db_session: providers.Resource[Session] = providers.Resource(
        get_db_session
    )

    # Services
    firebase_service = providers.Singleton(
        FirebaseService,
        credential_path=config.firebase_service_account_key_path
    )

    # Repositories
    user_repo: providers.Factory[UserRepository] = providers.Factory(
        PostgresUserRepository,
        db_session=db_session
    )
    unit_of_measure_repo: providers.Factory[UnitOfMeasureRepository] = providers.Factory(
        PostgresUnitOfMeasureRepository,
        db_session=db_session
    )
    material_type_repo: providers.Factory[MaterialTypeRepository] = providers.Factory(
        PostgresMaterialTypeRepository,
        db_session=db_session
    )
    material_repository: providers.Factory[MaterialRepository] = providers.Factory(
        PostgresMaterialRepository,
        db_session=db_session,
        unit_repo=unit_of_measure_repo
    )
    product_repository: providers.Factory[ProductRepository] = providers.Factory(
        PostgresProductRepository,
        db_session=db_session,
        unit_repo=unit_of_measure_repo
    )
    payroll_repository: providers.Factory[PayrollRepository] = providers.Factory(
        PostgresPayrollRepository,
        db_session=db_session
    )
    payroll_history_repository: providers.Factory[PayrollHistoryRepository] = providers.Factory(
        PostgresPayrollHistoryRepository,
        db_session=db_session
    )
    payroll_history_task_repository: providers.Factory[PayrollHistoryTaskRepository] = providers.Factory(
        PostgresPayrollHistoryTaskRepository,
        db_session=db_session
    )
    
    task_assignment_repository: providers.Factory[TaskAssignmentRepository] = providers.Factory(
        InMemoryTaskAssignmentRepository
    )
    
    client_repository: providers.Factory[ClientRepository] = providers.Factory(
        PostgresClientRepository,
        db_session=db_session
    )
    
    task_repository: providers.Factory[TaskRepository] = providers.Factory(
        PostgresTaskRepository,
        db_session=db_session
    )
    
    work_repository: providers.Factory[WorkRepository] = providers.Factory(
        PostgresWorkRepository,
        db_session=db_session,
        product_repo=product_repository
    )
    
    # Audit Repository
    audit_repository: providers.Factory[PriceCalculationAuditRepository] = providers.Factory(
        PostgresPriceCalculationAuditRepository,
        db_session=db_session
    )
    
    # Services
    product_service: providers.Factory[ProductService] = providers.Factory(
        ProductService,
        product_repo=product_repository,
        material_repo=material_repository,
        unit_repo=unit_of_measure_repo,
    )
    
    # New Domain Services
    material_price_service: providers.Factory[MaterialPriceUpdateService] = providers.Factory(
        MaterialPriceUpdateService,
        material_repository=material_repository,
        product_repository=product_repository,
        audit_repository=audit_repository
    )
    
    product_creation_service: providers.Factory[ProductCreationService] = providers.Factory(
        ProductCreationService,
        material_repository=material_repository,
        product_repository=product_repository,
        unit_repository=unit_of_measure_repo,
        audit_repository=audit_repository
    )
    
    composite_product_service: providers.Factory[CompositeProductService] = providers.Factory(
        CompositeProductService,
        product_repository=product_repository
    )
    
    # Legacy aliases for compatibility
    material_type_repository = material_type_repo

    # Use Cases
    create_user_use_case = providers.Factory(
        'app.application.use_cases.create_user.CreateUser',
        user_repository=user_repo,
        firebase_service=firebase_service
    )

    get_available_roles_use_case = providers.Factory(
        'app.application.use_cases.get_available_roles.GetAvailableRoles'
    )

    update_payroll_on_task_completion = providers.Factory(
    UpdatePayrollHistoryOnTaskCompletionV2,
    task_repo=task_repository,
    payroll_history_repo=payroll_history_repository,
    payroll_repo=payroll_repository,
    user_repo=user_repo,
    payroll_history_task_repo=payroll_history_task_repository
)

    # Template Use Cases
    get_template_requirements_use_case = providers.Factory(
        GetTemplateRequirementsUseCase,
        product_repo=product_repository
    )

    instantiate_product_use_case = providers.Factory(
        InstantiateProductUseCase,
        product_repo=product_repository,
        material_repo=material_repository
    )


