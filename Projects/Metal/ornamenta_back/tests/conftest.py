"""
Pytest configuration and shared fixtures.

IMPORTANTE: Este conftest usa una BASE DE DATOS DE TEST SEPARADA
para garantizar que los tests NUNCA afecten los datos de desarrollo.
"""
import os
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Import all models to ensure they're registered with the Base
from app.infrastructure.adapters.db.database import Base


@pytest.fixture(scope="session")
def test_database_url():
    """
    Get the TEST database URL.
    
    NUNCA usa la base de datos de desarrollo - siempre usa una BD de test separada.
    """
    # Intentar usar una variable de entorno especifica para tests
    test_db = os.getenv("TEST_DATABASE_URL")
    
    if test_db:
        return test_db
    
    # Si no existe, create una BD de test basada en la de desarrollo
    dev_db = os.getenv("DATABASE_URL", "postgresql+psycopg://user:password@db:5432/serviperfiles_db")
    
    # Reemplazar el nombre de la BD por uno de test
    if "serviperfiles_db" in dev_db:
        return dev_db.replace("serviperfiles_db", "serviperfiles_test_db")
    else:
        # Fallback: agregar _test al final
        return dev_db.rstrip("/") + "_test"


@pytest.fixture(scope="session")
def engine(test_database_url):
    """
    Create a SQLAlchemy engine for testing.
    
    Crea las tablas en la BD de test al inicio de la sesion.
    """
    engine = create_engine(test_database_url, echo=False)
    
    # Create all tables in the test database
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup: Drop all tables after all tests
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def mock_unit_repo():
    """Mock unit of measure repository."""
    from unittest.mock import Mock
    from app.domain.factories.unit_factory import UnitFactory
    mock = Mock()
    all_units = [
        UnitFactory.meter(), UnitFactory.millimeter(), UnitFactory.centimeter(),
        UnitFactory.inch(), UnitFactory.foot(), UnitFactory.meter_squared(),
        UnitFactory.millimeter_squared(), UnitFactory.centimeter_squared(),
        UnitFactory.meter_cubed(), UnitFactory.liter(), UnitFactory.milliliter(),
        UnitFactory.gallon(), UnitFactory.kilogram(), UnitFactory.gram(),
        UnitFactory.pound(), UnitFactory.ounce(), UnitFactory.kg_per_liter(),
        UnitFactory.kg_per_cubic_meter(),
    ]
    mock.get_all.return_value = all_units
    
    # Setup get_by_symbol behavior
    def get_by_symbol(symbol):
        # Handle mapping for common symbols
        target = symbol
        if symbol == "m":
            return next((u for u in all_units if u.symbol == "m"), None)
        if symbol == "m":
            return next((u for u in all_units if u.symbol == "m"), None)
        return next((u for u in all_units if u.symbol == target), None)
    
    mock.get_by_symbol.side_effect = get_by_symbol
    
    # Setup get_by_id behavior
    mock.get_by_id.side_effect = lambda id: next((u for u in all_units if u.id == id), None)
    
    return mock


@pytest.fixture
def db_session(engine) -> Generator[Session, None, None]:
    """
    Create a new database session for each test with automatic rollback.
    
    Cada test se ejecuta en una transaccion que se revierte al final,
    garantizando aislamiento total entre tests y que NINGUN dato persista.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()
    
    yield session
    
    # Cleanup: Rollback everything and close
    session.close()
    transaction.rollback()
    connection.close()
