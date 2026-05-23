"""Bootstrap database schema for first-time environments.

If the database has no business tables, create the schema from SQLAlchemy
metadata and stamp Alembic to head so new developers start from a valid state.
Otherwise, apply normal Alembic migrations.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Final

# Ensure project root (/app) is importable when this file is executed directly
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import os
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text, Table, MetaData
from sqlalchemy.engine import Engine

from app.config import settings
from app.infrastructure.adapters.db.database import Base

# Import models so they are registered in Base.metadata
from app.infrastructure.adapters.db import models as _models  # noqa: F401


logger: Final[logging.Logger] = logging.getLogger("bootstrap_db")
logging.basicConfig(level=logging.INFO, format="[bootstrap-db] %(message)s")


def _create_engine() -> Engine:
    return create_engine(settings.database_url)


def _is_effectively_empty(engine: Engine) -> bool:
    inspector = inspect(engine)
    table_names = [
        table_name
        for table_name in inspector.get_table_names(schema="public")
        if table_name != "alembic_version"
    ]
    return len(table_names) == 0


def _force_stamp_head(engine: Engine, alembic_config: Config) -> None:
    """Force stamp the database to head by clearing alembic_version first.
    This bypasses the 'Can't locate revision' error during stamp.
    """
    logger.info(" Clearing old alembic_version table to force reconciliation...")
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
    
    logger.info(" Stamping database to current head...")
    command.stamp(alembic_config, "head")


def _ensure_extensions(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS citext"))
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))


def _alembic_config() -> Config:
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", settings.database_url)
    return config


def main() -> None:
    engine = _create_engine()
    alembic_config = _alembic_config()

    if _is_effectively_empty(engine):
        logger.info("Empty database detected. Bootstrapping schema from metadata...")
        _ensure_extensions(engine)
        Base.metadata.create_all(bind=engine)
        command.stamp(alembic_config, "head")
        logger.info("Schema bootstrapped and Alembic stamped to head.")
        return

    logger.info("Existing schema detected. Running Alembic upgrade head...")
    try:
        command.upgrade(alembic_config, "head")
        logger.info("Alembic upgrade completed.")
    except Exception as e:
        # Check if error is due to missing migration files (ResolutionError or KeyError)
        # This happens when we cleanup the migration history but the DB still has old revision IDs
        error_msg = str(e)
        if "ResolutionError" in error_msg or "KeyError" in error_msg or "Can't locate revision" in error_msg:
            logger.warning(" Alembic history mismatch detected (likely due to migration cleanup).")
            logger.info(" Reconciling database state with current migration head...")
            # Use force stamp to bypass the error during normal stamp
            _force_stamp_head(engine, alembic_config)
            logger.info("OK Database state reconciled. You can continue working with your existing data.")
        else:
            logger.error(f"ERROR Critical error during migration: {e}")
            raise e


if __name__ == "__main__":
    main()
