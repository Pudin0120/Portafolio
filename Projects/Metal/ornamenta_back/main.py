import os
import subprocess
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from scalar_fastapi.scalar_fastapi import get_scalar_api_reference

from app.infrastructure.adapters.rest import (
    admin_router,
    authorization,
    composition_router,
    dependencies,
    material_type_router,
    material_router,
    inventory_router,
    material_price_router,
    measurement_strategy_router,
    product_router,
    composite_product_router,
    quotation_router,
    roles_router,
    unit_measure_router,
    user_router,
    payroll_router,
    payroll_history,
    client_router,
    work_router,
    task_router,
)
from app.infrastructure.containers import Container

# Cargar variables de entorno
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context.
    Handle startup and shutdown events.
    """
    # Startup
    print(" Starting application...", flush=True)
    
    # Optional startup seed (disabled by default).
    # Database bootstrap/seed should be handled by entrypoint, not app lifespan.
    run_seed_on_startup = os.getenv("RUN_SEED_ON_STARTUP", "false").lower() in (
        "1",
        "true",
        "yes",
    )

    if run_seed_on_startup:
        try:
            print(" Running seed script from app startup...", flush=True)
            subprocess.run([sys.executable, "seed.py"], timeout=60, check=True)
            print("OK seed.py executed", flush=True)
            print("OK Database initialized successfully", flush=True)
        except Exception as e:
            print(f"ERROR Startup seed failed: {e}", flush=True)
            raise
    else:
        print("  RUN_SEED_ON_STARTUP disabled - skipping startup seed.", flush=True)
    
    print("OK Application started successfully", flush=True)
    
    yield
    
    # Shutdown
    print(" Shutting down application...")


def create_app() -> FastAPI:
    """
    Creates and configures a FastAPI application instance.
    """
    container = Container()
    container.wire(
        modules=[
            unit_measure_router,
            material_type_router,
            composition_router,
            material_router,
            material_price_router,
            measurement_strategy_router,
            product_router,
            composite_product_router,
            quotation_router,
            user_router,
            admin_router,
            roles_router,
            dependencies,
            authorization,
            payroll_router,
            payroll_history,
            client_router,
            work_router,
            task_router,
        ]
    )

    app = FastAPI(lifespan=lifespan)
    app.container = container  # type: ignore

    # Configurar CORS
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    frontend_prod_url = os.getenv("FRONTEND_PROD_URL", "")

    # Lista de origenes permitidos
    environment = os.getenv("ENVIRONMENT", "development")
    if environment == "development":
        origins = ["*"]  # Permitir cualquier origen en desarrollo
    else:
        # En produccion, usar la URL de produccion como principal
        origins = []
        if frontend_prod_url:
            origins.append(frontend_prod_url)
        # Tambien permitir localhost para desarrollo/testing si es necesario
        if frontend_url and frontend_url != "http://localhost:5173":
            origins.append(frontend_url)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # URLs del frontend
        allow_credentials=True,
        allow_methods=["*"],  # Permitir todos los metodos HTTP
        allow_headers=["*"],  # Permitir todas las cabeceras
    )

    # Middleware para deshabilitar cache en todas las respuestas
    @app.middleware("http")
    async def add_no_cache_header(request, call_next):
        response = await call_next(request)
        # Aplicar cabeceras para prevenir cache en navegadores
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    # Global exception handler for Pydantic validation errors
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request, exc):
        """Handle Pydantic validation errors gracefully with detailed info."""
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Validation error on {request.url.path}: {exc}")
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": "validation_error",
                "message": "Error de validacion en los datos enviados",
                "errors": [
                    {
                        "field": list(error["loc"]),
                        "message": error["msg"],
                        "type": error["type"],
                        "input": str(error.get("input", "N/A")),
                    }
                    for error in exc.errors()
                ],
            },
        )

    app.include_router(unit_measure_router.router)
    app.include_router(material_type_router.router)
    app.include_router(composition_router.router)
    app.include_router(material_router.router)
    app.include_router(inventory_router.router)
    app.include_router(material_price_router.router)
    app.include_router(measurement_strategy_router.router)
    app.include_router(product_router.router)
    app.include_router(composite_product_router.router)
    app.include_router(quotation_router.router)
    app.include_router(user_router.router)
    app.include_router(admin_router.router)
    app.include_router(roles_router.router)
    app.include_router(payroll_router.router)
    app.include_router(payroll_history.router)
    app.include_router(client_router.router)
    app.include_router(work_router.router)
    app.include_router(task_router.router)

    @app.get("/")
    async def root():
        """
        Root endpoint - Welcome message
        """
        return {
            "message": "ServiPerfiles API",
            "status": "running",
            "version": "1.0.0",
            "docs": "/docs",
            "scalar_docs": "/scalar",
        }

    @app.get("/health")
    async def health_check():
        """
        Health check endpoint for monitoring
        """
        return {"status": "healthy"}

    @app.get("/scalar", include_in_schema=False)
    async def scalar_html():
        return get_scalar_api_reference(
            openapi_url=app.openapi_url or "/openapi.json",
            title=app.title,
        )

    return app


app = create_app()
