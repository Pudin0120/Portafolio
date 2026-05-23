"""
Router para servir reportes de tests (Allure).
"""
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

from app.domain.models.user import User
from app.infrastructure.adapters.rest.authorization import get_current_user

router = APIRouter(
    prefix="/reports", 
    tags=["reports"],
    dependencies=[Depends(get_current_user)]
)

# Ruta donde se generan los reportes de Allure
REPORTS_DIR = Path(__file__).parent.parent.parent.parent.parent / "tests" / "reports" / "allure-results"


@router.get("/health", tags=["reports"])
async def health_check():
    """Health check para los reportes."""
    return {"status": "ok", "reports_dir": str(REPORTS_DIR), "exists": REPORTS_DIR.exists()}


@router.get("/", tags=["reports"])
async def list_reports():
    """Lista los reportes disponibles."""
    if not REPORTS_DIR.exists():
        return {"message": "No reports generated yet", "available": []}
    
    files = list(REPORTS_DIR.glob("*.json"))
    return {
        "message": "Reports available",
        "count": len(files),
        "available": [f.name for f in files]
    }
