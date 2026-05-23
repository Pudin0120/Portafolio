from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dependency_injector.wiring import inject, Provide
from typing import Generator
from sqlalchemy.orm import Session
from fastapi import Depends

from app.application.services.firebase_service import FirebaseService
from app.domain.repositories.user_repository import UserRepository
from app.domain.models.user import User
from app.infrastructure.containers import Container
from app.infrastructure.adapters.db.database import SessionLocal
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.adapters.repositories.postgres_user_repository import PostgresUserRepository
from app.infrastructure.adapters.db.database import get_db_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user_repository(db: Session = Depends(get_db_session)) -> UserRepository:
    """Provee una instancia del repositorio de users, inyectando la sesion de DB."""
    # Esto es inyeccion de dependencias pura de Python/FastAPI, sin dependency-injector
    return PostgresUserRepository(db_session=db)

@inject
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    firebase_service: FirebaseService = Depends(
        Provide[Container.firebase_service]),
    user_repo: UserRepository = Depends(Provide[Container.user_repo]),
) -> User:
    decoded_token = firebase_service.verify_token(token)
    if not decoded_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    firebase_uid = decoded_token.get("uid")
    user = user_repo.get_by_firebase_uid(firebase_uid)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user
