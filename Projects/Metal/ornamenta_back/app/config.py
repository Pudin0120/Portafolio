from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
from decimal import Decimal


class Settings(BaseSettings):
    # Core application settings
    database_url: str
    firebase_service_account_key_path: str
    firebase_project_id: Optional[str] = None
    # Optional variables from .env that Pydantic needs to know about
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None
    manager_email: Optional[str] = None
    manager_password: Optional[str] = None
    manager_firebase_uid: Optional[str] = None
    frontend_url: Optional[str] = None
    frontend_prod_url: Optional[str] = None
    environment: Optional[str] = "production"  # Default to production for safety
    
    # Product validation settings
    product_min_dimension: Optional[float] = 0.01  # 1cm en metros
    product_max_dimension: Optional[float] = 100.0  # 100m
    product_min_price: Optional[Decimal] = Decimal("100")  # 100 COP minimo

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
