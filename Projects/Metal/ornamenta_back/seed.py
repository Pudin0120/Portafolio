import uuid
import os
import sys

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import auth, credentials
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()

# Add the app directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))

from app.domain.models.user import RoleEnum
from app.domain.value_objects.document_number import DocumentEnum, DocumentNumber
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateEnum, StateUser
from app.infrastructure.adapters.db.models import Role, TenantModel
from app.infrastructure.adapters.repositories.postgres_user_repository import (
    PostgresUserRepository,
)
from app.infrastructure.adapters.repositories.postgres_unit_of_measure_repository import (
    PostgresUnitOfMeasureRepository,
)
from app.infrastructure.adapters.repositories.postgres_material_type_repository import (
    PostgresMaterialTypeRepository,
)
from app.domain.models.unit_of_measure import UnitOfMeasure
from app.domain.models.material_type import MaterialType
from app.domain.models.composition import Composition
from app.infrastructure.adapters.db.repositories.postgresql_composition_repository import (
    PostgreSQLCompositionRepository,
)
from app.domain.strategies.strategy_registry import MeasurementStrategyRegistry


def initialize_firebase():
    """Initializes the Firebase Admin SDK."""
    # Check if the app is already initialized
    if not firebase_admin._apps:
        firebase_service_account_key_path = os.getenv(
            "FIREBASE_SERVICE_ACCOUNT_KEY_PATH"
        )
        firebase_project_id = os.getenv("FIREBASE_PROJECT_ID")

        if firebase_service_account_key_path and os.path.exists(
            firebase_service_account_key_path
        ):
            # Use service account key file
            cred = credentials.Certificate(firebase_service_account_key_path)
        else:
            # Fallback to Application Default Credentials
            cred = credentials.ApplicationDefault()

        firebase_admin.initialize_app(
            cred,
            {
                "projectId": firebase_project_id,
            },
        )
    print("Firebase Admin SDK initialized successfully.")




def seed_units_of_measure(session, tenant_id: uuid.UUID):
    """Seed initial units of measure."""
    print("\n Seeding Units of Measure...")

    # We query the DB directly to avoid repository filters that might be causing issues
    from app.infrastructure.adapters.db.models.unit_of_measure_model import (
        UnitOfMeasureModel,
    )

    units_data = [
        # Length
        {
            "name": "Metro",
            "symbol": "m",
            "pint_unit_text": "meter",
            "dimension": "length",
        },
        {
            "name": "Milimetro",
            "symbol": "mm",
            "pint_unit_text": "millimeter",
            "dimension": "length",
        },
        {
            "name": "Centimetro",
            "symbol": "cm",
            "pint_unit_text": "centimeter",
            "dimension": "length",
        },
        {
            "name": "Pulgada",
            "symbol": "in",
            "pint_unit_text": "inch",
            "dimension": "length",
        },
        {
            "name": "Pie",
            "symbol": "ft",
            "pint_unit_text": "foot",
            "dimension": "length",
        },
        # Area
        {
            "name": "Metro cuadrado",
            "symbol": "m",
            "pint_unit_text": "meter ** 2",
            "dimension": "area",
        },
        {
            "name": "Milimetro cuadrado",
            "symbol": "mm",
            "pint_unit_text": "millimeter ** 2",
            "dimension": "area",
        },
        {
            "name": "Centimetro cuadrado",
            "symbol": "cm",
            "pint_unit_text": "centimeter ** 2",
            "dimension": "area",
        },
        {
            "name": "Pie cuadrado",
            "symbol": "ft",
            "pint_unit_text": "foot ** 2",
            "dimension": "area",
        },
        {
            "name": "Pulgada cuadrada",
            "symbol": "in",
            "pint_unit_text": "inch ** 2",
            "dimension": "area",
        },
        # Mass/Weight
        {
            "name": "Kilogramo",
            "symbol": "kg",
            "pint_unit_text": "kilogram",
            "dimension": "mass",
        },
        {"name": "Gramo", "symbol": "g", "pint_unit_text": "gram", "dimension": "mass"},
        {
            "name": "Libra",
            "symbol": "lb",
            "pint_unit_text": "pound",
            "dimension": "mass",
        },
        {
            "name": "Onza",
            "symbol": "oz",
            "pint_unit_text": "ounce",
            "dimension": "mass",
        },
        # Volume
        {
            "name": "Litro",
            "symbol": "L",
            "pint_unit_text": "liter",
            "dimension": "volume",
        },
        {
            "name": "Mililitro",
            "symbol": "mL",
            "pint_unit_text": "milliliter",
            "dimension": "volume",
        },
        {
            "name": "Metro cubico",
            "symbol": "m",
            "pint_unit_text": "meter ** 3",
            "dimension": "volume",
        },
        {
            "name": "Galon",
            "symbol": "gal",
            "pint_unit_text": "gallon",
            "dimension": "volume",
        },
        {
            "name": "Onza fluida",
            "symbol": "fl oz",
            "pint_unit_text": "fluid_ounce",
            "dimension": "volume",
        },
        # Density
        {
            "name": "Kilogramo por metro cubico",
            "symbol": "kg/m",
            "pint_unit_text": "kilogram / meter ** 3",
            "dimension": "density",
        },
        {
            "name": "Kilogramo por litro",
            "symbol": "kg/L",
            "pint_unit_text": "kilogram / liter",
            "dimension": "density",
        },
        {
            "name": "Gramo por centimetro cubico",
            "symbol": "g/cm",
            "pint_unit_text": "gram / centimeter ** 3",
            "dimension": "density",
        },
    ]

    created_count = 0
    skipped_count = 0

    for data in units_data:
        try:
            # Check if unit already exists by name (unique constraint in model)
            existing = (
                session.query(UnitOfMeasureModel)
                .filter(UnitOfMeasureModel.name == data["name"])
                .first()
            )

            if existing:
                skipped_count += 1
                continue

            # Unit doesn't exist, create it
            unit = UnitOfMeasureModel(
                id=uuid.uuid4(),
                name=data["name"],
                symbol=data["symbol"],
                pint_unit_text=data["pint_unit_text"],
                dimension=data["dimension"],
                tenant_id=tenant_id,
            )
            session.add(unit)
            session.commit()
            created_count += 1
            print(f"  OK Created unit: {data['name']} ({data['symbol']})")

        except Exception as e:
            print(f"    Warning: Could not create unit {data['name']}: {e}")
            session.rollback()

    print(
        f"  OK Units of measure seeding completed: {created_count} created, {skipped_count} already exist"
    )


def seed_material_types(session, tenant_id: uuid.UUID):
    """Seed initial material types."""
    print("\n Seeding Material Types...")

    from app.infrastructure.adapters.db.models.material_type_model import (
        MaterialTypeModel,
    )

    material_types_data = [
        {
            "name": "Lamina",
            "desc": "Lamina de acero, aluminio, cobre, etc.",
            "strategy": "SHEET",
        },
        {
            "name": "Varilla corrugada",
            "desc": "Varilla corrugada de acero, aluminio, cobre, etc.",
            "strategy": "PROFILE",
        },
        {
            "name": "Tubo cuadrado",
            "desc": "Tubo cuadrado de acero, aluminio, cobre, etc.",
            "strategy": "PROFILE",
        },
        {
            "name": "Tubo redondo",
            "desc": "Tubo redondo de acero, aluminio, cobre, etc.",
            "strategy": "PROFILE",
        },
        {
            "name": "Galon de pintura",
            "desc": "Galon de pintura de acero, aluminio, cobre, etc.",
            "strategy": "LIQUID",
        },
        {
            "name": "Soldadura",
            "desc": "Soldadura de acero, aluminio, cobre, etc.",
            "strategy": "SOLID",
        },
        {
            "name": "Servicio",
            "desc": "Servicios de mano de obra: soldadura, pintura, instalacion, etc.",
            "strategy": "LABOR",
        },
        {
            "name": "Accesorio",
            "desc": "Elementos que se venden por unidad: chapas, manijas, tornillos, etc.",
            "strategy": "UNIT",
        },
    ]

    created_count = 0
    skipped_count = 0

    for data in material_types_data:
        try:
            # Check if exists by name for this tenant
            existing = (
                session.query(MaterialTypeModel)
                .filter(
                    MaterialTypeModel.name == data["name"],
                    MaterialTypeModel.tenant_id == tenant_id,
                )
                .first()
            )

            if existing:
                skipped_count += 1
                continue

            mat_type = MaterialTypeModel(
                id=uuid.uuid4(),
                name=data["name"],
                description=data["desc"],
                measurement_strategy=data["strategy"],
                tenant_id=tenant_id,
            )
            session.add(mat_type)
            session.commit()
            created_count += 1
            print(f"  OK Created material type: {data['name']} ({data['strategy']})")
        except Exception as e:
            print(f"    Warning: Could not create material type {data['name']}: {e}")
            session.rollback()

    print(f"  OK Seeded {created_count} material types, {skipped_count} already exist")


def seed_compositions(session, tenant_id: uuid.UUID):
    """Seed initial compositions."""
    print("\n Seeding Compositions...")

    repo = PostgreSQLCompositionRepository(session)

    # Check if already seeded for this tenant
    existing_compositions = repo.get_all(tenant_id)
    if len(existing_compositions) > 0:
        print(
            f"    Compositions already seeded for this tenant ({len(existing_compositions)} found). Skipping."
        )
        return

    compositions = [
        Composition(
            id=uuid.uuid4(),
            name="Acero galvanizado",
            description="Acero con recubrimiento de zinc G90",
            tenant_id=tenant_id,
        ),
        Composition(
            id=uuid.uuid4(),
            name="Acero inoxidable 304",
            description="Acero inoxidable austenitico",
            tenant_id=tenant_id,
        ),
        Composition(
            id=uuid.uuid4(),
            name="Acero cold rolled",
            description="Acero laminado en frio",
            tenant_id=tenant_id,
        ),
        Composition(
            id=uuid.uuid4(),
            name="Aluminio 6061",
            description="Aleacion de aluminio de uso general",
            tenant_id=tenant_id,
        ),
        Composition(
            id=uuid.uuid4(),
            name="Pintura epoxica",
            description="Pintura de dos componentes",
            tenant_id=tenant_id,
        ),
        Composition(
            id=uuid.uuid4(),
            name="Pintura anticorrosiva",
            description="Primer anticorrosivo para metales",
            tenant_id=tenant_id,
        ),
    ]

    for composition in compositions:
        try:
            repo.save(composition)
            session.commit()  # Commit each composition individually
            print(f"  OK Created composition: {composition.name}")
        except Exception as e:
            print(f"    Warning: Could not create composition {composition.name}: {e}")
            session.rollback()  # Rollback on error to continue with next composition

    print(f"  OK Seeded {len(compositions)} compositions")


def validate_measurement_strategies(session):
    """
    Validate that all measurement strategies are properly configured and functional.
    This is critical as measurement strategies are fundamental to the application.
    """
    print("\n Validating Measurement Strategies...")

    try:
        # Create repositories needed for strategies
        unit_repo = PostgresUnitOfMeasureRepository(session)

        # Create strategy registry
        registry = MeasurementStrategyRegistry(unit_repo)

        # Required strategies that must be available
        required_strategies = ["SHEET", "PROFILE", "LIQUID", "SOLID", "UNIT"]

        print("   Checking strategy registration...")
        for strategy_name in required_strategies:
            if not registry.has_strategy(strategy_name):
                raise ValueError(
                    f"Required strategy '{strategy_name}' is not registered"
                )
            print(f"     Strategy '{strategy_name}' is registered")

        print("   Testing strategy instantiation and basic functionality...")

        # Test each strategy can be instantiated and describe itself
        for strategy_name in required_strategies:
            try:
                strategy = registry.get_strategy(strategy_name)
                description = strategy.describe()
                type_name = strategy.get_type_name()

                if type_name != strategy_name:
                    raise ValueError(
                        f"Strategy '{strategy_name}' returns wrong type name: '{type_name}'"
                    )

                print(f"     Strategy '{strategy_name}' instantiated successfully")
                print(f"      Description: {description[:50]}...")

            except Exception as e:
                raise ValueError(
                    f"Failed to instantiate or test strategy '{strategy_name}': {e}"
                )

        print("   Testing strategy-specific functionality...")

        # Test SHEET strategy with basic validation
        try:
            sheet_strategy = registry.get_strategy("SHEET")
            # This should not raise an exception
            sheet_strategy.describe()
            print("     SHEET strategy basic functionality OK")
        except Exception as e:
            raise ValueError(f"SHEET strategy validation failed: {e}")

        # Test PROFILE strategy
        try:
            profile_strategy = registry.get_strategy("PROFILE")
            profile_strategy.describe()
            print("     PROFILE strategy basic functionality OK")
        except Exception as e:
            raise ValueError(f"PROFILE strategy validation failed: {e}")

        # Test LIQUID strategy
        try:
            liquid_strategy = registry.get_strategy("LIQUID")
            liquid_strategy.describe()
            print("     LIQUID strategy basic functionality OK")
        except Exception as e:
            raise ValueError(f"LIQUID strategy validation failed: {e}")

        # Test SOLID strategy
        try:
            solid_strategy = registry.get_strategy("SOLID")
            solid_strategy.describe()
            print("     SOLID strategy basic functionality OK")
        except Exception as e:
            raise ValueError(f"SOLID strategy validation failed: {e}")

        print("  OK All measurement strategies validated successfully")
        return True

    except Exception as e:
        print(f"  ERROR Measurement strategies validation failed: {e}")
        return False




def migrate_products_add_dimensions_column(engine):
    """
    Migration: Add dimensions column to products table (JSONB format).
    This migration is safe to run multiple times.
    Needed for persisting product dimensions (SHEET, TUBE, LIQUID, SOLID, LABOR).

    Stores normalized dimensions as JSON:
    - LIQUID: {"volume": 1.0} (in liters)
    - SHEET: {"width": 1.5, "height": 2.0} (in meters)
    - PROFILE: {"length": 5.0, "thickness": 0.002, "shape": "ROUND"} (in meters)
    - SOLID: {"width": 1.0, "height": 2.0, "depth": 0.5} (in meters)
    - LABOR: Various depending on unit_type
    """
    print("\n Checking products table migration...")

    try:
        with engine.connect() as conn:
            # Check if dimensions column already exists
            result = conn.execute(
                text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'products' AND column_name = 'dimensions'
            """)
            )
            column_exists = result.fetchone() is not None

            if column_exists:
                print(
                    "    Column 'dimensions' already exists in products table. Skipping migration."
                )
                return True

            print("   Adding 'dimensions' column to products table...")

            # Add the dimensions column as JSONB (PostgreSQL JSON type)
            conn.execute(
                text("""
                ALTER TABLE products
                ADD COLUMN dimensions JSONB DEFAULT '{}'::jsonb
            """)
            )

            # Create GIN index on dimensions for better query performance
            conn.execute(
                text("""
                CREATE INDEX ix_products_dimensions ON products USING gin(dimensions)
            """)
            )

            conn.commit()
            print("  OK Column 'dimensions' added successfully as JSONB")
            print("  OK GIN index created for dimensions column")
            return True

    except Exception as e:
        print(f"  ERROR Error during migration: {e}")
        return False


def seed_database():
    """
    Populates the database with roles and creates a manager user in both
    Firebase and the local database.
    """
    print("=" * 60)
    print("DATABASE SEED SCRIPT")
    print("=" * 60)

    database_url = os.getenv("DATABASE_URL")
    manager_email = os.getenv("MANAGER_EMAIL")
    manager_password = os.getenv("MANAGER_PASSWORD")
    manager_firebase_uid = os.getenv("MANAGER_FIREBASE_UID")
    firebase_project_id = os.getenv("FIREBASE_PROJECT_ID")

    print(f"\nConfiguration:")
    print(
        f"  - Database URL: {database_url.replace(os.getenv('POSTGRES_PASSWORD', ''), '***') if database_url else 'NOT SET'}"
    )
    print(f"  - Manager Email: {manager_email or 'NOT SET'}")
    print(
        f"  - Manager Password: {'***' if manager_password else 'NOT SET (only needed if creating new Firebase user)'}"
    )
    print(f"  - Manager Firebase UID: {manager_firebase_uid or 'NOT SET'}")
    print(f"  - Firebase Project ID: {firebase_project_id or 'NOT SET'}")
    print()

    # Validar solo database_url y manager_email como obligatorios
    if not all([database_url, manager_email]):
        print("ERROR Error: DATABASE_URL and MANAGER_EMAIL must be set in the .env file.")
        return

    if not firebase_project_id:
        print(
            "ERROR Error: FIREBASE_PROJECT_ID must be set in the .env file for Firebase authentication."
        )
        print(
            "Please add FIREBASE_PROJECT_ID=your-firebase-project-id to your .env file."
        )
        return

    # --- Initialize Services ---
    try:
        initialize_firebase()
    except Exception as e:
        print(f"\n  Warning: Failed to initialize Firebase: {e}")
        print(f"   Skipping Firebase user verification. You may need to:")
        print(f"   1. Check Firebase credentials have proper permissions")
        print(f"   2. Run seed manually after fixing permissions")
        print()
        # Continue without Firebase - user already exists in DB
        if not manager_firebase_uid:
            print(
                f"ERROR Error: Cannot proceed without MANAGER_FIREBASE_UID or working Firebase connection"
            )
            return

    engine = create_engine(str(database_url))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # --- 0. Run migrations ---
        print(" Step 0: Migrations are handled by Alembic.")
        
        # --- 0.1 Create Development Tenant ---
        print("\n Step 0.1: Creating development tenant...")
        dev_tenant_slug = "serviperfiles_db"
        
        default_tenant = (
            db.query(TenantModel).filter(TenantModel.slug == dev_tenant_slug).first()
        )
        if not default_tenant:
            default_tenant = TenantModel(
                name="Serviperfiles (Desarrollo)", slug=dev_tenant_slug, is_active=True
            )
            db.add(default_tenant)
            db.flush()
            db.commit()
            print(f"  OK Created default tenant: {default_tenant.id}")
        else:
            print(f"   Default tenant already exists: {default_tenant.id}")

        tenant_id = default_tenant.id

        # --- 1. Create Roles ---
        roles_to_create = ["EMPLOYEE", "SUPERVISOR", "MANAGER", "SUPER_ADMIN"]
        print(" Step 1: Creating or verifying roles...")
        for role_name in roles_to_create:
            role = (
                db.query(Role)
                .filter(Role.name == role_name, Role.tenant_id == tenant_id)
                .first()
            )
            if not role:
                new_role = Role(name=role_name, tenant_id=tenant_id)
                db.add(new_role)
                print(f"   Role '{role_name}' created.")
            else:
                print(f"   Role '{role_name}' already exists.")
        db.commit()

        # --- 2. Create Manager User in Firebase ---
        print(f"\n Step 2: Processing manager user in Firebase")
        print(f"  Email: {manager_email}")

        # Use provided UID if available, otherwise create new user
        if manager_firebase_uid:
            print(f"  Using provided Firebase UID: {manager_firebase_uid}")
            try:
                firebase_user = auth.get_user(manager_firebase_uid)
                print(f"   Firebase user found with provided UID")
                # Verify email matches
                if firebase_user.email != manager_email:
                    print(
                        f"    Warning: Firebase user email ({firebase_user.email}) doesn't match MANAGER_EMAIL ({manager_email})"
                    )
            except Exception as e:
                # Catch all Firebase errors (UserNotFoundError, InsufficientPermissionError, etc.)
                print(
                    f"    Warning: Could not verify Firebase user: {type(e).__name__}"
                )
                print(f"     Error: {str(e)}")
                print(f"     Continuing with provided UID: {manager_firebase_uid}")
                # Don't set to None - trust the provided UID

        if not manager_firebase_uid:
            try:
                firebase_user = auth.get_user_by_email(manager_email)
                print(f"   Manager user already exists in Firebase")
                print(f"    UID: {firebase_user.uid}")
                manager_firebase_uid = firebase_user.uid
            except auth.UserNotFoundError:
                # Solo aqui necesitamos la password
                if not manager_password:
                    print(
                        f"  ERROR Error: Manager user not found in Firebase and MANAGER_PASSWORD is not set."
                    )
                    print(
                        f"     To create a new Firebase user, please set MANAGER_PASSWORD in .env"
                    )
                    return

                print("   Manager user not found in Firebase, creating...")
                firebase_user = auth.create_user(
                    email=manager_email, password=manager_password, email_verified=True
                )
                manager_firebase_uid = firebase_user.uid
                print(f"   User created in Firebase with UID: {firebase_user.uid}")
            except Exception as e:
                print(f"  ERROR Error: Could not access Firebase: {type(e).__name__}")
                print(f"     {str(e)}")
                print(
                    f"     Cannot proceed without Firebase connection or MANAGER_FIREBASE_UID"
                )
                return

        # --- 3. Create Super Admin User in Database using Repository ---
        print(f"\n Step 3: Creating super admin user in database")
        user_repository = PostgresUserRepository(db)

        # Check if user already exists by email
        existing_user = user_repository.get_by_email(Email(value=str(manager_email)))

        if not existing_user:
            print("   Super admin user not found in DB, creating...")

            # Datos fijos para el super admin - estos no cambiaran en ejecuciones posteriores
            SUPER_ADMIN_DATA = {
                "document_number": "1234567890",  # Document fijo para super admin
                "first_name": "Alex",
                "last_name": "Super Admin",
                "phone": "3001234567",
            }

            # Create value objects for super admin
            super_admin_email = Email(value=str(manager_email))
            super_admin_document = DocumentNumber(
                value=SUPER_ADMIN_DATA["document_number"],
                doc_type=DocumentEnum.CC,
            )
            super_admin_state = StateUser(
                value=StateEnum.ACTIVE
            )  # Esto se guardara como 'A' en la BD

            # Create user through repository with all required fields
            super_admin_user = user_repository.create_user(
                firebase_uid=manager_firebase_uid,
                email=super_admin_email,
                first_name=SUPER_ADMIN_DATA["first_name"],
                last_name=SUPER_ADMIN_DATA["last_name"],
                phone=SUPER_ADMIN_DATA["phone"],
                role=RoleEnum.SUPER_ADMIN,
                document_number=super_admin_document,
                state=super_admin_state,
                tenant_id=tenant_id,
            )

            # Commit the transaction to ensure the user is persisted
            db.commit()

            print(f"  OK Super admin user created successfully in DB")
            print(f"    Email: {manager_email}")
            print(f"    Document: {SUPER_ADMIN_DATA['document_number']}")
            print(
                f"    Name: {SUPER_ADMIN_DATA['first_name']} {SUPER_ADMIN_DATA['last_name']}"
            )
            print(f"    Phone: {SUPER_ADMIN_DATA['phone']}")
            print(f"    Role: SUPER_ADMIN")
            print(f"    State: ACTIVE (stored as 'A' in DB)")
            print(f"    Firebase UID: {manager_firebase_uid}")
        else:
            print(f"   Super admin user already exists in DB")
            print(f"    Email: {existing_user.email.value}")
            print(f"    Name: {existing_user.first_name} {existing_user.last_name}")
            print(f"    Document: {existing_user.identification_number.value}")
            print(f"    Phone: {existing_user.phone}")
            print(f"    Role: {existing_user.role.value}")
            print(f"    State: {existing_user.state.value.value}")
            print(f"    Firebase UID: {existing_user.firebase_uid}")

            # Verify the user has SUPER_ADMIN role
            if existing_user.role != RoleEnum.SUPER_ADMIN:
                print(
                    f"    WARNING: Existing user has role '{existing_user.role.value}' instead of SUPER_ADMIN"
                )
                print(f"    Consider updating the role manually if needed")

        # --- 3b. Create Additional Core System Users ---
        print(f"\n Step 3b: Creating additional core system users")

        # Datos fijos para los users del sistema - estos no cambiaran en ejecuciones posteriores
        CORE_USERS = [
            {
                "email": "superadmin@serviperfilesayc.com",
                "firebase_uid": "HVv6QurWyvhqHAnPGlueKK7RPZP2",
                "role": RoleEnum.SUPER_ADMIN,
                "document_number": "1000000001",
                "first_name": "Super",
                "last_name": "Administrador",
                "phone": "3000000001",
                "description": "Tiene control total sobre el sistema. Puede create y administrar gerentes.",
            },
            {
                "email": "gerente@serviperfilesayc.com",
                "firebase_uid": "y1HuQZiQNpaY6udNq51Cx9GqcwG3",
                "role": RoleEnum.MANAGER,
                "document_number": "1000000002",
                "first_name": "Gerente",
                "last_name": "Sistema",
                "phone": "3000000002",
                "description": "Administra todo el sistema. Tiene los mismos permisos que el supervisor y el empleado. Puede create products, materials y cotizaciones.",
            },
            {
                "email": "supervisor@serviperfilesayc.com",
                "firebase_uid": "LRrb40nJgmWvQItyQFWHOy2OSFu1",
                "role": RoleEnum.SUPERVISOR,
                "document_number": "1000000003",
                "first_name": "Supervisor",
                "last_name": "Sistema",
                "phone": "3000000003",
                "description": "Asigna tasks a los empleados y verifica su cumplimiento. Tambien puede create cotizaciones.",
            },
            {
                "email": "empleado@serviperfilesayc.com",
                "firebase_uid": "R1rVbvR0JVTjj5EhNXSgODdWk1C2",
                "role": RoleEnum.EMPLOYEE,
                "document_number": "1000000004",
                "first_name": "Empleado",
                "last_name": "Sistema",
                "phone": "3000000004",
                "description": "Visualiza las tasks asignadas y las marca como completadas. Puede create cotizaciones basadas en los products y materials creados por el gerente.",
            },
        ]

        created_users = 0
        skipped_users = 0

        for user_data in CORE_USERS:
            try:
                # Check if user already exists by email
                existing = user_repository.get_by_email(Email(value=user_data["email"]))

                if existing:
                    skipped_users += 1
                    print(
                        f"    User already exists: {user_data['email']} ({user_data['role'].value})"
                    )
                    print(f"      {user_data['description']}")
                    continue

                # Create value objects
                user_email = Email(value=user_data["email"])
                user_document = DocumentNumber(
                    value=user_data["document_number"],
                    doc_type=DocumentEnum.CC,
                )
                user_state = StateUser(value=StateEnum.ACTIVE)

                # Create user through repository
                new_user = user_repository.create_user(
                    firebase_uid=user_data["firebase_uid"],
                    email=user_email,
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    phone=user_data["phone"],
                    role=user_data["role"],
                    document_number=user_document,
                    state=user_state,
                    tenant_id=tenant_id,
                )

                db.commit()
                created_users += 1
                print(
                    f"  OK Created user: {user_data['email']} ({user_data['role'].value})"
                )
                print(f"      {user_data['description']}")

            except Exception as e:
                print(f"    Warning: Could not create user {user_data['email']}: {e}")
                db.rollback()

        print(
            f"  OK Core users seeding completed: {created_users} created, {skipped_users} already exist"
        )

        # --- 4. Seed Units of Measure ---
        seed_units_of_measure(db, tenant_id)

        # --- 5. Validate Measurement Strategies ---
        if not validate_measurement_strategies(db):
            print(
                "ERROR Critical: Measurement strategies validation failed. Aborting seed process."
            )
            return

        # --- 6. Seed Material Types ---
        seed_material_types(db, tenant_id)

        # --- 7. Seed Compositions ---
        seed_compositions(db, tenant_id)

        print("\n" + "=" * 60)
        print("OK SEED SCRIPT COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"\nYou can now login with:")
        print(f"  Email: {manager_email}")
        print(f"  Password: (the one you set in .env)")
        print()

    except Exception as e:
        print("\n" + "=" * 60)
        print("ERROR ERROR OCCURRED DURING SEED")
        print("=" * 60)
        print(f"\nError: {e}")
        print("\nStack trace:")
        import traceback

        traceback.print_exc()
        print()
        db.rollback()
        raise  # Re-raise to signal failure
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
