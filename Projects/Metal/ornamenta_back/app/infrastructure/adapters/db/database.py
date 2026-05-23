from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from typing import Generator
from sqlalchemy.orm import Session
from app.config import settings
import logging
import uuid

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

engine = create_engine(
    settings.database_url,
    pool_size=20,  # Number de conexiones mantenidas en el pool
    max_overflow=40,  # Conexiones adicionales permitidas cuando el pool se agota
    pool_recycle=3600,  # Reciclar conexiones cada hora (evita problemas con PostgreSQL)
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_timeout=30,  # Timeout para obtener conexion del pool
    echo=False,  # Cambiar a True solo para debug
    isolation_level="READ COMMITTED"
)

# SessionLocal for regular usage
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,  #  Importante: False
    bind=engine,
    expire_on_commit=False  #  ANADE ESTO - Evita que los objetos expiren despues del commit
)

from .models.base import Base


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session for each request.
    Automatically commits changes at the end of the request.
    """
    request_id = str(uuid.uuid4())[:8]
    
    db = SessionLocal()
    logger.debug(f"[{request_id}]  Database session created")
    
    exception_occurred = False
    try:
        # Yield session to FastAPI endpoint
        yield db
        
    except Exception as e:
        # On error, mark flag and rollback
        exception_occurred = True
        logger.error(f"[{request_id}] ERROR Exception in request: {e}, rolling back transaction")
        try:
            db.rollback()
            logger.info(f"[{request_id}]   Rollback completed successfully")
        except Exception as rollback_error:
            logger.error(f"[{request_id}] ERROR Rollback failed: {rollback_error}")
        raise
        
    finally:
        # In finally, commit if no exception occurred, then always close
        try:
            if not exception_occurred:
                # On success, commit all changes - THIS IS THE KEY PART
                logger.debug(f"[{request_id}]  Committing transaction...")
                db.commit()
                logger.info(f"[{request_id}] OK Transaction committed successfully")
        except Exception as commit_error:
            logger.error(f"[{request_id}] ERROR Commit failed: {commit_error}, rolling back")
            try:
                db.rollback()
                logger.info(f"[{request_id}]   Rollback completed after commit failure")
            except Exception as rb_error:
                logger.error(f"[{request_id}] ERROR Rollback after commit failure also failed: {rb_error}")
            raise
        finally:
            # Always close session and return connection to pool
            logger.debug(f"[{request_id}]  Closing database session")
            db.close()
