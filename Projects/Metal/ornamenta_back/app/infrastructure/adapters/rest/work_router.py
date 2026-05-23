"""
REST API endpoints for works (works/cotizaciones).
"""
from typing import Optional
from uuid import UUID
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.domain.models.user import User
from app.domain.value_objects.work_state import WorkStateEnum
from app.application.dto.work_dto import (
    WorkDTO,
    WorkCreateDTO,
    WorkListDTO,
    CompletionDTO
)
from app.application.dto.product_work_item_dto import AddProductToWorkDTO, ProductWorkItemDTO
from app.application.dto.work_action_dto import (
    QuoteWorkResponseDTO,
    StartWorkResponseDTO,
    DeliverWorkResponseDTO
)
from app.application.dto.task_dto import (
    TaskDTO,
    TaskListDTO,
    TaskHierarchyInfoDTO,
    TaskHierarchyListDTO
)
from app.application.mappers.work_mapper import WorkMapper
from app.application.mappers.task_mapper import TaskMapper
from app.application.use_cases.create_work import CreateWork
from app.application.use_cases.quote_work import QuoteWork
from app.application.use_cases.start_work import StartWork
from app.application.use_cases.deliver_work import DeliverWork
from app.application.use_cases.add_product_to_work import AddProductToWork
from app.application.use_cases.remove_product_from_work import RemoveProductFromWork
from app.application.use_cases.reorder_product_in_work import ReorderProductInWork
from app.application.use_cases.delete_work import DeleteWork
from app.application.use_cases.get_work import GetWork
from app.infrastructure.adapters.rest.dependencies import get_current_user
from app.infrastructure.adapters.db.database import get_db_session
from app.infrastructure.adapters.repositories.postgres_work_repository import PostgresWorkRepository
from app.infrastructure.adapters.repositories.postgres_product_repository import PostgresProductRepository
from app.infrastructure.adapters.repositories.postgres_client_repository import PostgresClientRepository
from app.infrastructure.adapters.repositories.postgres_unit_of_measure_repository import PostgresUnitOfMeasureRepository
from app.infrastructure.dependencies.inventory_dependencies import get_inventory_service


router = APIRouter(
    prefix="/works",
    tags=["Works"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/", response_model=WorkDTO, status_code=status.HTTP_201_CREATED)
def create_work(
    work_data: WorkCreateDTO,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Creates a new work in DRAFT status.
    
    **Requiere rol: MANAGER**
    
    El work se crea sin products. Usa POST /works/{work_id}/products para agregarlos.
    
    ## Parametros de Entrada
    
    | Campo | Tipo | Requerido | Validacion | Ejemplo |
    |-------|------|-----------|-----------|---------|
    | `client_identification` | string | OK Si | 5-20 caracteres | `"1002309888"` |
    | `work_name` | string | OK Si | 3-255 caracteres | `"Pintura de puertas"` |
    | `description` | string | ERROR No | Max 2000 caracteres | `"Detalles de la obra"` |
    | `tax` | number | ERROR No | 0.0 a 1.0 (default: 0.0) | `0.15` (15%) |
    | `end_aprox_delivery_date` | datetime | ERROR No | ISO 8601 con zona horaria | `"2025-11-21T10:37:00Z"` |
    | `deposit_amount` | number | ERROR No |  0 (default: 0) | `200000` |
    
    ## Formato de Fecha
    
    La fecha debe estar en formato ISO 8601 **COMPLETO** con zona horaria:
    - OK Valido: `"2025-11-21T10:37:00Z"` o `"2025-11-21T10:37:00+00:00"`
    - ERROR Invalid: `"2025-11-21T10:37"` (sin segundos)
    
    ## Response (201 Created)
    
    Devuelve un `WorkDTO` con el work creado en estado DRAFT, incluyendo:
    - `work_id`: UUID unico del work
    - `state`: "DRAFT"
    - `products`: Lista vacia (agregar despues)
    - `tasks`: Lista vacia (se generan al iniciar)
    - `products_value`: null (se calcula al cotizar)
    - `work_value`: null (se calcula al cotizar)
    - `completion_percentage`: 0.0
    
    ## Ejemplo de Request
    
    ```json
    {
      "client_identification": "1002309888",
      "work_name": "Pintura de puertas en la casa de don timoteo.",
      "description": "pintura de la ornamentacion de la casa de don timoteo",
      "tax": 0.15,
      "end_aprox_delivery_date": "2025-11-21T10:37:00Z",
      "deposit_amount": 200000
    }
    ```
    
    ## Posibles Errores
    
    - **400 Bad Request**: El client no existe o hay error de validacion
    - **403 Forbidden**: El user no tiene rol MANAGER
    - **422 Unprocessable Entity**: Datos invalids (verificar formato de fecha)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Creating work with data: client_id={work_data.client_identification}, name={work_data.work_name}, user_role={current_user.role}")
        
        # Create repositories with the same session
        unit_repo = PostgresUnitOfMeasureRepository(db_session)
        product_repo = PostgresProductRepository(db_session, unit_repo)
        client_repo = PostgresClientRepository(db_session)
        work_repo = PostgresWorkRepository(db_session, product_repo)
        
        use_case = CreateWork(work_repository=work_repo, client_repository=client_repo)
        work = use_case.execute(work_data, created_by=current_user)
        
        logger.info(f"Work created successfully: {work.work_id}")
        
        # Build products registry
        products_registry = {}
        for product_item in work.products:
            product = product_repo.get_by_id(product_item.product_id)
            if product:
                products_registry[product.id] = product
        
        return WorkMapper.to_dto(work, products_registry)
    except HTTPException as http_exc:
        logger.warning(f"HTTP Exception: {http_exc.status_code} - {http_exc.detail}")
        raise
    except ValueError as val_err:
        logger.error(f"ValueError: {str(val_err)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de validacion: {str(val_err)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {type(e).__name__}: {str(e)}"
        )


@router.get("/", response_model=WorkListDTO)
def list_works(
    state: Optional[str] = Query(None, description="Filtrar por estado: DRAFT, QUOTED, IN_PROGRESS, DELIVERED"),
    client_identification: Optional[str] = Query(None, description="Filtrar por identificacion del client"),
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Lista todos los works con filtros opcionales.
    
    ## Parametros de Filtrado (Query)
    
    - `state`: Filtrar por estado del work (DRAFT, QUOTED, IN_PROGRESS, DELIVERED)
    - `client_identification`: Filtrar por identificacion del client
    
    ## Response (200 OK)
    
    Devuelve un `WorkListDTO` con:
    - `works`: Lista de `WorkSummaryDTO`
    - `total`: Total de works encontrados
    """
    # Create repositories with the same session
    unit_repo = PostgresUnitOfMeasureRepository(db_session)
    product_repo = PostgresProductRepository(db_session, unit_repo)
    work_repo = PostgresWorkRepository(db_session, product_repo)
    
    use_case = GetWork(work_repository=work_repo)
    
    if state:
        try:
            state_enum = WorkStateEnum(state)
            works = use_case.execute_by_state(state_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estado invalid: {state}. Valores valids: DRAFT, QUOTED, IN_PROGRESS, DELIVERED"
            )
    elif client_identification:
        works = use_case.execute_by_client(client_identification)
    else:
        works = use_case.execute_all()
    
    return WorkMapper.to_dto_list(works)


@router.get("/{work_id}", response_model=WorkDTO)
def get_work(
    work_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Obtiene un work completo por su ID con precios calculados segun el estado.
    
    ##  CALCULO DE PRECIOS POR ESTADO
    
    ### DRAFT (Borrador)
    - **products_value**: Suma de (precio_actual_catalogo  quantity)
    - **work_value**: products_value  (1 + tax)
    - Los precios son **dinamicos** y se recalculan cada vez
    - Si el price de un product cambia en el catalogo, se refleja automaticamente
    
    ### QUOTED (Cotizado)
    - **products_value**: Suma de precios **congelados** en snapshots
    - **work_value**: products_value  (1 + tax)
    - Los precios **NO cambian** aunque se modifique el catalogo
    - Los snapshots se crearon al ejecutar POST /works/{id}/quote
    
    ### IN_PROGRESS / DELIVERED
    - **products_value**: Suma de precios congelados en snapshots
    - **work_value**: products_value  (1 + tax)
    - Los precios permanecen congelados
    
    ##  Ejemplo de Response en DRAFT
    
    ```json
    {
      "work_id": "123e4567-e89b-12d3-a456-426614174000",
      "work_name": "Pintura de puertas",
      "state": "DRAFT",
      "tax": 0.15,
      "products": [
        {
          "product_id": "223e4567-e89b-12d3-a456-426614174000",
          "product_name": "Pintura acrilica roja",
          "quantity": 2,
          "current_price": {
            "amount": 100000,
            "currency": "COP"
          },
          "snapshot": null
        },
        {
          "product_id": "323e4567-e89b-12d3-a456-426614174000",
          "product_name": "Brocha profesional",
          "quantity": 1,
          "current_price": {
            "amount": 50000,
            "currency": "COP"
          },
          "snapshot": null
        }
      ],
      "products_value": 250000,
      "work_value": 287500,
      "completion_percentage": 0.0,
      "tasks": []
    }
    ```
    
    **Calculo:**
    - Product 1: 100000  2 = 200000
    - Product 2: 50000  1 = 50000
    - products_value = 250000
    - work_value = 250000  1.15 = 287500
    
    ##  Ejemplo de Response en QUOTED
    
    Despues de ejecutar `POST /works/{id}/quote`, los precios se congelan:
    
    ```json
    {
      "work_id": "123e4567-e89b-12d3-a456-426614174000",
      "work_name": "Pintura de puertas",
      "state": "QUOTED",
      "tax": 0.15,
      "products": [
        {
          "product_id": "223e4567-e89b-12d3-a456-426614174000",
          "product_name": "Pintura acrilica roja",
          "quantity": 2,
          "current_price": null,
          "snapshot": {
            "product_id": "223e4567-e89b-12d3-a456-426614174000",
            "product_name": "Pintura acrilica roja",
            "price_amount": 100000,
            "price_currency": "COP"
          }
        }
      ],
      "products_value": 200000,
      "work_value": 230000,
      "completion_percentage": 0.0,
      "tasks": []
    }
    ```
    
    ## Parametros de Ruta
    
    - `work_id`: UUID del work (ejemplo: `123e4567-e89b-12d3-a456-426614174000`)
    
    ## Response (200 OK)
    
    Devuelve un `WorkDTO` completo con:
    - Datos basicos del work (name, description, estado, tax)
    - Lista de products con precios segun estado (current_price o snapshot)
    - Lista de tasks (vacia en DRAFT, se genera al iniciar work)
    - Valores calculados: `products_value`, `work_value`, `completion_percentage`
    
    ## Posibles Errores
    
    - **404 Not Found**: El work no existe
    - **403 Forbidden**: No tienes permiso para ver este work
    """
    # Create repositories with the same session
    unit_repo = PostgresUnitOfMeasureRepository(db_session)
    product_repo = PostgresProductRepository(db_session, unit_repo)
    work_repo = PostgresWorkRepository(db_session, product_repo)
    
    use_case = GetWork(work_repository=work_repo)
    work = use_case.execute_by_id(work_id)
    
    # Build products registry
    products_registry = {}
    for product_item in work.products:
        product = product_repo.get_by_id(product_item.product_id)
        if product:
            products_registry[product.id] = product
    
    return WorkMapper.to_dto(work, products_registry)


@router.delete("/{work_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_work(
    work_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Deletes a work from the database.
    
    **Requiere rol: MANAGER**
    
    ## Restricciones
    
     **Only works in DRAFT or QUOTED status can be deleted**.
    Los works en IN_PROGRESS o DELIVERED son inmutables y no pueden eliminarse.
    
    ## Comportamiento
    
    1. Valida que el work exista
    2. Valida que este en estado DRAFT o QUOTED
    3. Elimina el work y todos sus datos asociados en cascada:
       - Products agregados al work
       - Snapshots de precios (si esta en QUOTED)
       - Tasks asociadas (si las hay)
    4. La eliminacion es irreversible
    
    ## Parametros de Ruta
    
    - `work_id`: UUID del work a delete
    
    ## Response (204 No Content)
    
    Sin cuerpo de respuesta. Si la eliminacion es exitosa, devuelve estado 204.
    
    ## Posibles Errores
    
    - **400 Bad Request**: El work esta en estado IN_PROGRESS o DELIVERED (no se puede delete)
    - **403 Forbidden**: El user no tiene rol MANAGER
    - **404 Not Found**: El work no existe
    - **500 Internal Server Error**: Error al delete el work de la base de datos
    
    ## Ejemplos de Uso
    
    **Delete work en DRAFT:**
    ```bash
    DELETE /works/123e4567-e89b-12d3-a456-426614174000
    # Response: 204 No Content
    ```
    
    **Intento de delete work en IN_PROGRESS:**
    ```bash
    DELETE /works/223e4567-e89b-12d3-a456-426614174000
    # Response: 400 Bad Request
    # {
    #   "detail": "No se puede delete un work en estado IN_PROGRESS. 
    #              Solo se pueden delete works en DRAFT o QUOTED."
    # }
    ```
    """
    # Create repositories with the same session
    unit_repo = PostgresUnitOfMeasureRepository(db_session)
    product_repo = PostgresProductRepository(db_session, unit_repo)
    work_repo = PostgresWorkRepository(db_session, product_repo)
    
    use_case = DeleteWork(work_repository=work_repo)
    use_case.execute(work_id, deleted_by=current_user)


@router.post("/{work_id}/products", response_model=ProductWorkItemDTO, status_code=status.HTTP_201_CREATED)
def add_product_to_work(
    work_id: UUID,
    product_data: AddProductToWorkDTO,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Adds a product to a work (quotation).
    
    ##  FLUJO DE USO CORRECTO
    
    1. **Create work (DRAFT):**
       ```bash
       POST /works
       {
         "client_identification": "1002309888",
         "work_name": "Pintura de puertas",
         "tax": 0.15
       }
       # Response: work_id = "123e4567-e89b-12d3-a456-426614174000"
       ```
    
    2. **Agregar products al work (DRAFT):**
       ```bash
       POST /works/123e4567-e89b-12d3-a456-426614174000/products
       {
         "product_id": "223e4567-e89b-12d3-a456-426614174000",
         "quantity": 2
       }
       ```
       Repite para cada product que necesites agregar.
    
    3. **Ver precios dinamicos en DRAFT:**
       ```bash
       GET /works/123e4567-e89b-12d3-a456-426614174000
       # Response incluye: products_value (price total), work_value (con tax)
       ```
    
    4. **Cotizar (congelar precios):**
       ```bash
       POST /works/123e4567-e89b-12d3-a456-426614174000/quote
       # Ahora state = "QUOTED" y los precios se congelan
       ```
    
    5. **Ver precios congelados en QUOTED:**
       ```bash
       GET /works/123e4567-e89b-12d3-a456-426614174000
       # Response incluye: products_value (congelado), snapshot en cada product
       ```
    
    ##  Comportamiento por Estado del Work
    
    ### DRAFT (Borrador)
    - OK **Permitido**: Agregar products
    -  **Sin snapshot**: Los products se almacenan sin congelar price
    -  **Precios dinamicos**: Al obtener GET /works/{id}, se usan precios actuales del catalogo
    -  **Editable**: Puedes agregar/quitar products libremente
    -  **Sin tasks**: Las tasks se generan al iniciar (start_work), no en DRAFT
    
    ### QUOTED (Cotizado)
    - OK **Permitido**: Agregar products (opcional, para agregar mas despues de cotizar)
    -  **Con snapshot**: Los products nuevos congelan snapshot inmediatamente
    -  **Precios congelados**: Al obtener GET /works/{id}, se usan precios del snapshot
    -  **Semi-editable**: Solo agregar/quitar, no modificar cantidades
    
    ### IN_PROGRESS / DELIVERED
    - ERROR **No permitido**: El work es inmutable
    
    ##  Parametros de Entrada
    
    ```json
    {
      "product_id": "223e4567-e89b-12d3-a456-426614174000",
      "quantity": 2,
      "execution_order": null
    }
    ```
    
    - `product_id` *(requerido)*: UUID del product a agregar (obten de GET /products)
    - `quantity` *(requerido)*: Quantity (debe ser > 0)
    - `execution_order` *(opcional)*: Orden de ejecucion (si null, se agrega al final)
    
    ##  Response (201 Created)
    
    ### En DRAFT (precios dinamicos, SIN snapshot):
    ```json
    {
      "product_id": "223e4567-e89b-12d3-a456-426614174000",
      "work_id": "123e4567-e89b-12d3-a456-426614174000",
      "product_name": "Pintura acrilica roja",
      "product_type": "simple",
      "quantity": 2,
      "execution_order": 0,
      "state": "PENDING",
      "current_price": {
        "amount": 100000,
        "currency": "COP"
      },
      "snapshot": null,
      "task_ids": []
    }
    ```
    
    ### En QUOTED (precios congelados, CON snapshot):
    ```json
    {
      "product_id": "223e4567-e89b-12d3-a456-426614174000",
      "work_id": "123e4567-e89b-12d3-a456-426614174000",
      "product_name": "Pintura acrilica roja",
      "product_type": "simple",
      "quantity": 2,
      "execution_order": 1,
      "state": "PENDING",
      "current_price": null,
      "snapshot": {
        "product_id": "223e4567-e89b-12d3-a456-426614174000",
        "product_name": "Pintura acrilica roja",
        "product_type": "simple",
        "price_amount": 100000,
        "price_currency": "COP",
        "composition": {},
        "dimensions": {}
      },
      "task_ids": []
    }
    ```
    
    ##  Como Mostrar Precios Correctamente en tu Frontend
    
    **Opcion 1: Mostrar price unitario y total**
    ```
    Product: Pintura acrilica roja
    Quantity: 2
    Price unitario: $100,000 (mostrar current_price.amount o snapshot.price_amount)
    Subtotal: $200,000 (precio_unitario  quantity)
    ```
    
    **Opcion 2: Mostrar en tabla**
    ```
    | Product | Quantity | Price Unit. | Subtotal | Snapshot |
    |----------|----------|--------------|----------|----------|
    | Pintura  | 2        | $100,000     | $200,000 |  (congelado) |
    ```
    
    **Opcion 3: Mostrar resumen final**
    ```
    Subtotal de products: $250,000  (products_value)
    Tax (15%):              $37,500
    Total work:          $287,500  (work_value)
    ```
    
    ## Posibles Errores
    
    - **400 Bad Request**: El product no existe, quantity invalid, o estado no permite agregar
    - **404 Not Found**: El work no existe
    - **409 Conflict**: El work ya esta iniciado (IN_PROGRESS) o entregado (DELIVERED)
    - **422 Unprocessable Entity**: Datos invalids o product sin price
    """
    # Create repositories with the same session
    unit_repo = PostgresUnitOfMeasureRepository(db_session)
    product_repo = PostgresProductRepository(db_session, unit_repo)
    work_repo = PostgresWorkRepository(db_session, product_repo)
    
    # Execute use case
    use_case = AddProductToWork(work_repository=work_repo, product_repository=product_repo)
    return use_case.execute(work_id, product_data, added_by=current_user)


@router.delete("/{work_id}/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_product_from_work(
    work_id: UUID,
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Elimina un product de un work.
    
    ## Restricciones
    
    Solo permitido en estados **DRAFT** o **QUOTED**.
    En otros estados el work es inmutable.
    
    ## Parametros de Ruta
    
    - `work_id`: UUID del work
    - `product_id`: UUID del product a delete
    
    ## Response (204 No Content)
    
    Sin cuerpo de respuesta.
    
    ## Posibles Errores
    
    - **400 Bad Request**: El work no esta en estado valid
    - **404 Not Found**: El work o product no existe
    """
    # Create repositories with the same session
    unit_repo = PostgresUnitOfMeasureRepository(db_session)
    product_repo = PostgresProductRepository(db_session, unit_repo)
    work_repo = PostgresWorkRepository(db_session, product_repo)
    
    use_case = RemoveProductFromWork(work_repository=work_repo)
    use_case.execute(work_id, product_id, removed_by=current_user)


@router.patch("/{work_id}/products/{product_id}/order", status_code=status.HTTP_204_NO_CONTENT)
def reorder_product_in_work(
    work_id: UUID,
    product_id: UUID,
    new_order: int = Query(..., ge=0, description="Nuevo orden de ejecucion"),
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Changes the execution order of a product en un work.
    
    ##  Comportamiento por Estado
    
    ### DRAFT / QUOTED (Antes de iniciar)
    - OK **Permitido**: Reordenar products libremente
    -  **Efecto**: Solo cambia el orden de los products
    -  **Sin tasks**: Las tasks aun no existen
    
    ### IN_PROGRESS (Despues de iniciar)
    - OK **Permitido**: Reordenar products Y sus tasks
    -  **Efecto**: Mueve el product y TODAS sus tasks asociadas
    -  **Automatico**: Las tasks mantienen su orden relativo (slots)
    -  **Jerarquia**: Las tasks de products compuestos se mueven juntas
    
    ### DELIVERED
    - ERROR **No permitido**: El work es inmutable
    
    ##  Caso de Uso Principal
    
    Este endpoint es ideal para **reordenar products compuestos completos** en IN_PROGRESS:
    
    **Ejemplo**: Si tienes "Puerta Metalica" con 4 tasks en posiciones [2, 3, 4, 5]
    y quieres moverlo despues de otras tasks:
    
    ```bash
    PATCH /works/{work_id}/products/{puerta_id}/order?new_order=3
    ```
    
    **Resultado automatico**:
    - Todas las 4 tasks de la puerta se mueven juntas
    - Mantienen su orden relativo (slot 0, 1, 2, 3)
    - Las demas tasks se desplazan para hacer espacio
    - La jerarquia del compuesto se preserva
    
    ## Parametros de Ruta
    
    - `work_id`: UUID del work
    - `product_id`: UUID del product a reordenar
    
    ## Parametros de Query
    
    - `new_order`: Nuevo orden del product (0-based,  0)
    
    ## Response (204 No Content)
    
    Sin cuerpo de respuesta. El reorden fue exitoso.
    
    ## Ejemplo Completo
    
    ### Antes de mover:
    ```
    Product 0: Marco (1 task)      Task en posicion 0
    Product 1: Puerta (4 tasks)    Tasks en posiciones [1, 2, 3, 4]
    Product 2: Pintura (1 task)    Task en posicion 5
    ```
    
    ### Despues de `PATCH /products/puerta_id/order?new_order=2`:
    ```
    Product 0: Marco (1 task)      Task en posicion 0
    Product 1: Pintura (1 task)    Task en posicion 1
    Product 2: Puerta (4 tasks)    Tasks en posiciones [2, 3, 4, 5]
    ```
    
    ## Posibles Errores
    
    - **400 Bad Request**: El work esta en DELIVERED o el orden es invalid
    - **404 Not Found**: El work o product no existe
    
    ##  Diferencia con `/tasks/{task_id}/reorder`
    
    - **Este endpoint** (`/products/{id}/order`): Mueve TODO el product con todas sus tasks
    - **Endpoint de tasks** (`/tasks/{id}/reorder`): Solo para tasks standalone (sin compuesto)
    
    Para products compuestos en IN_PROGRESS, **usa este endpoint**.
    """
    # Create repositories with the same session
    unit_repo = PostgresUnitOfMeasureRepository(db_session)
    product_repo = PostgresProductRepository(db_session, unit_repo)
    work_repo = PostgresWorkRepository(db_session, product_repo)
    
    use_case = ReorderProductInWork(work_repository=work_repo)
    use_case.execute(work_id, product_id, new_order, reordered_by=current_user)


@router.post("/{work_id}/quote", response_model=QuoteWorkResponseDTO)
def quote_work(
    work_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Cotiza un work (transicion DRAFT  QUOTED).
    
    **Requiere rol: MANAGER**
    
    ## Comportamiento
    
    1. Congela los precios de todos los products creando snapshots
    2. Calcula el valor total (products_value + tax)
    3. Cambia el estado a QUOTED
    4. Genera evento de dominio `WorkQuoted`
    
    Despues de cotizar aun se pueden agregar products (con snapshot inmediato).
    
    ## Parametros de Ruta
    
    - `work_id`: UUID del work a cotizar
    
    ## Response (200 OK)
    
    Devuelve un `QuoteWorkResponseDTO` con:
    - `work_id`: UUID del work
    - `work_name`: Nombre del work
    - `state`: "QUOTED"
    - `products_value`: Valor total de products
    - `work_value`: Valor final (con tax aplicado)
    - `tax_percentage`: Porcentaje de ganancia
    - `total_products`: Quantity de products
    - `quoted_at`: Timestamp de quotation
    
    ## Posibles Errores
    
    - **400 Bad Request**: El work no tiene products o no esta en DRAFT
    - **403 Forbidden**: El user no tiene rol MANAGER
    - **404 Not Found**: El work no existe
    """
    # Create repositories with the same session
    unit_repo = PostgresUnitOfMeasureRepository(db_session)
    product_repo = PostgresProductRepository(db_session, unit_repo)
    work_repo = PostgresWorkRepository(db_session, product_repo)
    
    use_case = QuoteWork(work_repository=work_repo, product_repository=product_repo)
    return use_case.execute(work_id, quoted_by=current_user)


@router.post("/{work_id}/start", response_model=StartWorkResponseDTO)
def start_work(
    work_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
    inventory_service = Depends(get_inventory_service),
):
    """
    Inicia un work (transicion QUOTED  IN_PROGRESS).
    
    **Requiere rol: MANAGER**
    
    ## Comportamiento
    
    1. Genera todas las tasks automaticamente desde los products
    2. Utiliza TaskFactory para create tasks segun el tipo de product
    3. Cambia el estado a IN_PROGRESS
    4. Bloquea modificacion de products (inmutable de ahora en adelante)
    5. Genera evento de dominio `WorkStarted`
    
    ## Parametros de Ruta
    
    - `work_id`: UUID del work a iniciar
    
    ## Response (200 OK)
    
    Devuelve un `StartWorkResponseDTO` con:
    - `work_id`: UUID del work
    - `work_name`: Nombre del work
    - `state`: "IN_PROGRESS"
    - `total_tasks_generated`: Quantity de tasks creadas
    - `started_at`: Timestamp de inicio
    
    ## Posibles Errores
    
    - **400 Bad Request**: El work no esta en QUOTED o no tiene products
    - **403 Forbidden**: El user no tiene rol MANAGER
    - **404 Not Found**: El work no existe
    """
    # Create repositories with the same session
    unit_repo = PostgresUnitOfMeasureRepository(db_session)
    product_repo = PostgresProductRepository(db_session, unit_repo)
    work_repo = PostgresWorkRepository(db_session, product_repo)
    
    use_case = StartWork(
        work_repository=work_repo,
        product_repository=product_repo,
        inventory_service=inventory_service,
    )
    return use_case.execute(work_id, started_by=current_user)


@router.post("/{work_id}/deliver", response_model=DeliverWorkResponseDTO)
def deliver_work(
    work_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Entrega un work al client (transicion IN_PROGRESS  DELIVERED).
    
    **Requiere rol: MANAGER**
    
    ## Restricciones
    
     **Todas las tasks deben estar finalizadas** para poder entregar.
    Si hay tasks pendientes, la entrega sera rechazada.
    
    ## Comportamiento
    
    1. Valida que todas las tasks esten en estado FINISHED
    2. Cambia el estado a DELIVERED
    3. Registra la fecha real de entrega
    4. Genera evento de dominio `WorkDelivered`
    5. El work pasa a ser inmutable
    
    ## Parametros de Ruta
    
    - `work_id`: UUID del work a entregar
    
    ## Response (200 OK)
    
    Devuelve un `DeliverWorkResponseDTO` con:
    - `work_id`: UUID del work
    - `work_name`: Nombre del work
    - `state`: "DELIVERED"
    - `delivery_date`: Fecha de entrega
    - `final_value`: Valor final del work
    - `completion_percentage`: 100.0
    
    ## Posibles Errores
    
    - **400 Bad Request**: El work no esta en IN_PROGRESS o hay tasks pendientes
    - **403 Forbidden**: El user no tiene rol MANAGER
    - **404 Not Found**: El work no existe
    """
    # Create repositories with the same session
    unit_repo = PostgresUnitOfMeasureRepository(db_session)
    product_repo = PostgresProductRepository(db_session, unit_repo)
    work_repo = PostgresWorkRepository(db_session, product_repo)
    
    use_case = DeliverWork(work_repository=work_repo)
    return use_case.execute(work_id, delivered_by=current_user)


@router.get("/{work_id}/tasks", response_model=TaskListDTO)
def get_work_tasks(
    work_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Obtiene todas las tasks de un work.
    
    ## Disponibilidad
    
    Solo disponible despues de iniciar el work (estados IN_PROGRESS o DELIVERED).
    En estados DRAFT o QUOTED no hay tasks.
    
    ## Parametros de Ruta
    
    - `work_id`: UUID del work
    
    ## Response (200 OK)
    
    Devuelve un `TaskListDTO` con:
    - `tasks`: Lista de `TaskDTO` con todas las tasks
    - `total_count`: Total de tasks
    
    Cada task incluye:
    - `task_id`: UUID de la task
    - `work_id`: UUID del work
    - `state`: Estado (PENDING, IN_PROGRESS, FINISHED)
    - `product_component_id`: Referencia al product que genero la task
    - `order`: Orden de ejecucion
    - Y mas detalles segun la task
    
    ## Posibles Errores
    
    - **404 Not Found**: El work no existe
    """
    # Create repositories with the same session
    unit_repo = PostgresUnitOfMeasureRepository(db_session)
    product_repo = PostgresProductRepository(db_session, unit_repo)
    work_repo = PostgresWorkRepository(db_session, product_repo)
    
    use_case = GetWork(work_repository=work_repo)
    work = use_case.execute_by_id(work_id)
    
    tasks_dto = [TaskMapper.to_dto(task) for task in work.tasks]
    return TaskListDTO(tasks=tasks_dto, total_count=len(tasks_dto))


@router.get("/{work_id}/completion", response_model=CompletionDTO)
def get_work_completion(
    work_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Gets the completion percentage of a work.
    
    ## Calculo
    
    El porcentaje se calcula como:
    ```
    (tareas_finalizadas / total_tareas)  100
    ```
    
    - **DRAFT / QUOTED**: 0% (sin tasks aun)
    - **IN_PROGRESS**: 0% a 100% (segun tasks completadas)
    - **DELIVERED**: 100%
    
    ## Parametros de Ruta
    
    - `work_id`: UUID del work
    
    ## Response (200 OK)
    
    Devuelve un `CompletionDTO` con:
    - `work_id`: UUID del work
    - `completion_percentage`: Porcentaje (0-100)
    - `finished_tasks`: Quantity de tasks finalizadas
    - `total_tasks`: Total de tasks
    
    ## Posibles Errores
    
    - **404 Not Found**: El work no existe
    """
    # Create repositories with the same session
    unit_repo = PostgresUnitOfMeasureRepository(db_session)
    product_repo = PostgresProductRepository(db_session, unit_repo)
    work_repo = PostgresWorkRepository(db_session, product_repo)
    
    use_case = GetWork(work_repository=work_repo)
    work = use_case.execute_by_id(work_id)
    
    return WorkMapper.to_completion_dto(work)


@router.get("/{work_id}/tasks/hierarchy", response_model=TaskHierarchyListDTO)
def get_work_tasks_hierarchical(
    work_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Gets the tasks for a work agrupadas por products compuestos (vista jerarquica).
    
    Esta vista muestra la estructura jerarquica de las tasks, agrupando las que
    pertenecen al mismo product compuesto. Util para:
    
    - Visualizar la relacion entre tasks y products compuestos
    - Entender que tasks forman parte de que ensamblaje
    - Validar que el orden de ejecucion respeta la jerarquia
    
    ## Estructura de Response
    
    Las tasks se agrupan por `parent_composite_id`:
    - Tasks sin compuesto (standalone): `composite_id = null`
    - Tasks de "Puerta Metalica": agrupadas bajo el ID del compuesto
    - Cada grupo muestra su rango de ejecucion
    
    ## Parametros de Ruta
    
    - `work_id`: UUID del work
    
    ## Response (200 OK)
    
    Devuelve `TaskHierarchyListDTO` con:
    - `work_id`: UUID del work
    - `total_tasks`: Total de tasks
    - `composite_groups`: Array de grupos (cada uno con sus tasks)
      - `composite_id`: ID del product compuesto (null para standalone)
      - `composite_name`: Nombre del product compuesto
      - `tasks`: Array de tasks en este grupo
      - `start_execution_order`: Primera task del grupo
      - `end_execution_order`: Ultima task del grupo
    
    ## Ejemplo
    
    ```json
    {
      "work_id": "...",
      "total_tasks": 8,
      "composite_groups": [
        {
          "composite_id": null,
          "composite_name": null,
          "tasks": [...],  // Tasks standalone
          "start_execution_order": 0,
          "end_execution_order": 1
        },
        {
          "composite_id": "uuid-puerta",
          "composite_name": "Puerta Metalica",
          "tasks": [...],  // Tasks de la puerta
          "start_execution_order": 2,
          "end_execution_order": 6
        }
      ]
    }
    ```
    
    ## Posibles Errores
    
    - **404 Not Found**: El work no existe o no tiene tasks
    """
    from app.application.dto.task_dto import TaskHierarchyListDTO
    
    # Create repositories
    unit_repo = PostgresUnitOfMeasureRepository(db_session)
    product_repo = PostgresProductRepository(db_session, unit_repo)
    work_repo = PostgresWorkRepository(db_session, product_repo)
    
    # Get work
    use_case = GetWork(work_repository=work_repo)
    work = use_case.execute_by_id(work_id)
    
    if not work.tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El work no tiene tasks generadas aun"
        )
    
    # DEBUG: Log task hierarchy info
    logger = logging.getLogger(__name__)
    logger.info(f"Work {work_id} has {len(work.tasks)} tasks")
    for task in work.tasks:
        logger.info(
            f"Task {task.task_id}: parent_composite={task.parent_composite_id}, "
            f"slot={task.composite_task_slot}, product_id={task.product_id}"
        )
    
    # Get composite task groups
    composite_groups = work.get_composite_task_groups()
    
    logger.info(f"Found {len(composite_groups)} composite groups")
    for composite_id, tasks in composite_groups.items():
        logger.info(f"Group {composite_id}: {len(tasks)} tasks")
    
    # Build products registry from work's products
    products_registry = {}
    for product_item in work.products:
        product = product_repo.get_by_id(product_item.product_id)
        if product:
            products_registry[product.id] = product
            logger.info(
                f"Product {product.id}: name={product.name}, "
                f"is_composite={product.is_composite()}"
            )
    
    # Convert to DTO
    hierarchy_dto = TaskMapper.to_hierarchy_list_dto(
        work_id=work.work_id,
        composite_groups=composite_groups,
        products_registry=products_registry
    )
    
    return hierarchy_dto


@router.get("/{work_id}/tasks/{task_id}/hierarchy", response_model=TaskHierarchyInfoDTO)
def get_task_hierarchy_info(
    work_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Obtiene information detallada sobre la jerarquia de una task especifica.
    
    Devuelve information completa sobre:
    - Si la task pertenece a un product compuesto
    - Su posicion (slot) dentro del compuesto
    - Tasks hermanas (mismo compuesto)
    - Ordenes de ejecucion valids (para reordenamiento)
    - Si puede ser reordenada
    
    Util para:
    - Validar restricciones antes de reordenar
    - Mostrar contexto de la task en el UI
    - Entender dependencias dentro del compuesto
    
    ## Parametros de Ruta
    
    - `work_id`: UUID del work
    - `task_id`: UUID de la task
    
    ## Response (200 OK)
    
    Devuelve `TaskHierarchyInfoDTO` con:
    - `task`: TaskDTO completo
    - `parent_composite_id`: ID del compuesto padre (null si standalone)
    - `current_slot`: Posicion dentro del compuesto (0, 1, 2...)
    - `total_slots`: Total de tasks en el compuesto
    - `valid_execution_orders`: Array de ordenes valids
    - `can_be_reordered`: Si puede cambiar de orden
    - `sibling_task_ids`: IDs de tasks hermanas
    
    ## Ejemplo
    
    ### Task de un compuesto:
    ```json
    {
      "task": {...},
      "parent_composite_id": "uuid-puerta",
      "current_slot": 1,
      "total_slots": 3,
      "valid_execution_orders": [3],  // Solo puede estar en posicion 3
      "can_be_reordered": false,
      "sibling_task_ids": ["uuid-task-0", "uuid-task-2"]
    }
    ```
    
    ### Task standalone:
    ```json
    {
      "task": {...},
      "parent_composite_id": null,
      "current_slot": null,
      "total_slots": null,
      "valid_execution_orders": [0, 1, 2, 3, 4, 5],  // Puede ir a cualquier posicion
      "can_be_reordered": true,
      "sibling_task_ids": []
    }
    ```
    
    ## Posibles Errores
    
    - **404 Not Found**: El work o la task no existe
    """
    from app.application.dto.task_dto import TaskHierarchyInfoDTO
    
    # Create repositories
    unit_repo = PostgresUnitOfMeasureRepository(db_session)
    product_repo = PostgresProductRepository(db_session, unit_repo)
    work_repo = PostgresWorkRepository(db_session, product_repo)
    
    # Get work
    use_case = GetWork(work_repository=work_repo)
    work = use_case.execute_by_id(work_id)
    
    # Get hierarchy info
    hierarchy_info = work.get_task_hierarchy_info(task_id)
    
    if not hierarchy_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task no encontrada"
        )
    
    # Convert task to DTO
    task = hierarchy_info['task']
    task_dto = TaskMapper.to_dto(task)
    
    # Convert to hierarchy info DTO
    hierarchy_dto = TaskMapper.to_hierarchy_info_dto(hierarchy_info, task_dto)
    
    return hierarchy_dto


@router.patch("/{work_id}/tasks/{task_id}/reorder", status_code=status.HTTP_204_NO_CONTENT)
def reorder_task(
    work_id: UUID,
    task_id: UUID,
    new_execution_order: int = Query(..., ge=0, description="Nuevo orden de ejecucion"),
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Reordena una task dentro del work.
    
    ##  NUEVO COMPORTAMIENTO: Reordenamiento Flexible
    
    Ahora puedes reordenar tasks de products compuestos dentro de su rango.
    Los `composite_task_slot` se actualizan automaticamente.
    
    ## Restricciones
    
    ### Tasks de Products Compuestos
    
    - **PUEDEN** reordenarse dentro del rango del compuesto
    - **NO PUEDEN** salir del rango del compuesto
    - Los `composite_task_slot` se recalculan automaticamente
    
    Ejemplo: Si "Puerta Metalica" tiene tasks en posiciones [2, 3, 4, 5]:
    - OK La task en posicion 3 PUEDE ir a posicion 2, 4 o 5
    - ERROR La task en posicion 3 NO PUEDE ir a posicion 1 o 6 (fuera del rango)
    
    ### Tasks Standalone (sin compuesto)
    
    - Pueden moverse a cualquier posicion
    - No tienen restricciones jerarquicas
    
    ## Parametros de Ruta
    
    - `work_id`: UUID del work
    - `task_id`: UUID de la task a reordenar
    
    ## Parametros de Query
    
    - `new_execution_order`: Nueva posicion (0-indexed,  0)
    
    ## Response (204 No Content)
    
    Si el reorden es exitoso, no devuelve contenido.
    
    ## Posibles Errores
    
    - **400 Bad Request**: El orden viola restricciones jerarquicas
      - Ejemplo: "La task no puede moverse fuera del rango del compuesto [2, 5]"
    - **404 Not Found**: El work o la task no existe
    
    ## Ejemplo de Uso
    
    ```bash
    # Reordenar una task de compuesto dentro de su rango
    curl -X PATCH /works/{work_id}/tasks/{task_id}/reorder?new_execution_order=3
    ```
    
    ## Validacion
    
    Usa `GET /works/{work_id}/tasks/{task_id}/hierarchy`
    para obtener `valid_execution_orders` antes de reordenar.
    """
    # Create repositories
    unit_repo = PostgresUnitOfMeasureRepository(db_session)
    product_repo = PostgresProductRepository(db_session, unit_repo)
    work_repo = PostgresWorkRepository(db_session, product_repo)
    
    # Get work
    use_case = GetWork(work_repository=work_repo)
    work = use_case.execute_by_id(work_id)
    
    try:
        # Reorder task (validates hierarchy constraints)
        work.reorder_task(task_id, new_execution_order)
        
        # Save changes (repository save method)
        work_repo.save(work)
        db_session.commit()
        
    except ValueError as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al reordenar task: {str(e)}"
        )


@router.get("/{work_id}/debug/products", include_in_schema=False)
def debug_work_products(
    work_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Debug endpoint: Muestra info detallada de products del work.
    
    Ayuda a diagnosticar por que las tasks no tienen parent_composite_id.
    """
    # Create repositories
    unit_repo = PostgresUnitOfMeasureRepository(db_session)
    product_repo = PostgresProductRepository(db_session, unit_repo)
    work_repo = PostgresWorkRepository(db_session, product_repo)
    
    # Get work
    use_case = GetWork(work_repository=work_repo)
    work = use_case.execute_by_id(work_id)
    
    products_info = []
    for product_item in work.products:
        product = product_repo.get_by_id(product_item.product_id)
        if product:
            is_composite = product.is_composite()
            components_list = []
            
            if is_composite:
                from typing import cast
                from app.domain.models.product import CompositeProduct
                composite = cast(CompositeProduct, product)
                components_list = [
                    {
                        "component_id": str(comp.component.id),
                        "component_name": comp.component.name,
                        "quantity": comp.quantity
                    }
                    for comp in composite.get_components()
                ]
            
            products_info.append({
                "product_id": str(product.id),
                "product_name": product.name,
                "product_type": "COMPOSITE" if is_composite else "SIMPLE",
                "quantity_in_work": product_item.quantity,
                "execution_order": product_item.execution_order,
                "components_count": len(components_list),
                "components": components_list
            })
    
    return {
        "work_id": str(work_id),
        "work_name": work.work_name,
        "state": work.state.get_state_name().value,
        "total_products": len(work.products),
        "products": products_info,
        "tasks_count": len(work.tasks),
        "tasks_with_parent_composite": sum(
            1 for t in work.tasks if t.parent_composite_id is not None
        )
    }
