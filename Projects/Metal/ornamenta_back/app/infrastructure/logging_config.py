"""Configuration de logging para auditoria de eventos de dominio."""
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_audit_logger() -> logging.Logger:
    """
    Configura y retorna un logger especifico para auditoria de users.
    
    Este logger escribe en un archivo separado user_audit.log con rotacion automatica.
    """
    # Create directorio de logs si no existe
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create logger especifico para auditoria
    audit_logger = logging.getLogger("user_audit")
    audit_logger.setLevel(logging.INFO)
    
    # Evitar duplicacion si ya esta configurado
    if audit_logger.handlers:
        return audit_logger
    
    # Handler para archivo con rotacion (10MB por archivo, mantener 10 backups)
    file_handler = RotatingFileHandler(
        logs_dir / "user_audit.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    
    # Formato estructurado para analisis
    formatter = logging.Formatter(
        fmt='%(message)s',  # El mensaje ya viene formateado desde el evento
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    audit_logger.addHandler(file_handler)
    
    # No propagar al logger raiz para evitar duplicacion
    audit_logger.propagate = False
    
    return audit_logger


# Instancia global del logger de auditoria
audit_logger = setup_audit_logger()
