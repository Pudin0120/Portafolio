"""
Middleware para manejar transacciones automaticamente en cada peticion HTTP.

Este middleware asegura que todas las sesiones de BD se commiteen al final de la peticion,
o hagan rollback si ocurre un error.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from sqlalchemy.orm import Session
from typing import List
import logging

logger = logging.getLogger(__name__)


class TransactionMiddleware(BaseHTTPMiddleware):
    """
    Middleware que maneja el ciclo de vida de las transacciones de BD.
    
    Commit automatico al final de peticiones exitosas.
    Rollback automatico en caso de errores.
    """
    
    def __init__(self, app, sessions_provider=None):
        super().__init__(app)
        self.sessions_provider = sessions_provider
        self.sessions: List[Session] = []
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Intercepta la peticion, ejecuta el endpoint, y maneja la transaccion.
        """
        try:
            # Ejecutar el endpoint
            response = await call_next(request)
            
            # Si fue exitoso, commit todas las sesiones
            self._commit_all_sessions()
            
            return response
        except Exception as e:
            # En caso de error, rollback
            self._rollback_all_sessions()
            logger.error(f"Error en peticion: {str(e)}", exc_info=True)
            raise
        finally:
            # Siempre cerrar las sesiones
            self._close_all_sessions()
    
    def _commit_all_sessions(self):
        """Commit a todas las sesiones activas."""
        for session in self.sessions:
            if session and session.is_active:
                try:
                    session.commit()
                    logger.debug("OK Session committed")
                except Exception as e:
                    logger.error(f"Error committing session: {str(e)}")
                    session.rollback()
                    raise
    
    def _rollback_all_sessions(self):
        """Rollback a todas las sesiones activas."""
        for session in self.sessions:
            if session and session.is_active:
                try:
                    session.rollback()
                    logger.debug(" Session rolled back")
                except Exception as e:
                    logger.error(f"Error rolling back session: {str(e)}")
    
    def _close_all_sessions(self):
        """Cierra todas las sesiones."""
        for session in self.sessions:
            if session:
                try:
                    session.close()
                    logger.debug(" Session closed")
                except Exception as e:
                    logger.error(f"Error closing session: {str(e)}")
        self.sessions.clear()
