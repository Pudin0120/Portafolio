"""
Mapper para Work (dominio  DTO).

Responsabilidades:
1. Convertir entidades Work de dominio a DTOs para API responses
2. Calcular precios de products segun el estado del work:
   - DRAFT: Precios dinamicos del catalogo (reflejan cambios en tiempo real)
   - QUOTED/IN_PROGRESS/DELIVERED: Precios congelados en snapshots


FLUJO COMPLETO: COMO AGREGAR PRODUCTS Y VER PRECIOS CORRECTAMENTE


PASO 1: Create work en DRAFT

POST /works
{
  "client_identification": "1002309888",
  "work_name": "Pintura de puertas",
  "tax": 0.15,
  "end_aprox_delivery_date": "2025-11-21T10:37:00Z",
  "deposit_amount": 200000
}
OK Response: work_id = "123e4567-e89b-12d3-a456-426614174000", state = "DRAFT"


PASO 2: Obtener work sin products (para verificar valores iniciales)

GET /works/123e4567-e89b-12d3-a456-426614174000
OK Response:
{
  "state": "DRAFT",
  "products": [],
  "products_value": null,      null porque no hay products
  "work_value": null,          null porque no hay products
  "completion_percentage": 0.0,
  "tasks": []
}


PASO 3: Agregar primer product (SIEMPRE en DRAFT)

POST /works/123e4567-e89b-12d3-a456-426614174000/products
{
  "product_id": "223e4567-e89b-12d3-a456-426614174000",
  "quantity": 2
}
OK Response: ProductWorkItemDTO con current_price = precio_catalogo, snapshot = null


PASO 4: Obtener work despues de agregar products (aun DRAFT)

GET /works/123e4567-e89b-12d3-a456-426614174000
OK Response (PRECIOS DINAMICOS):
{
  "state": "DRAFT",
  "products": [
    {
      "product_id": "223e4567-e89b-12d3-a456-426614174000",
      "product_name": "Pintura acrilica roja",
      "quantity": 2,
      "current_price": {
        "amount": 100000,      PRECIO ACTUAL DEL CATALOGO
        "currency": "COP"
      },
      "snapshot": null         SIN SNAPSHOT (no congelado)
    }
  ],
  "products_value": 200000,    2  100000 = 200000 (DINAMICO)
  "work_value": 230000,        200000  1.15 = 230000 (DINAMICO)
  "tax": 0.15
}

 IMPORTANTE: Si el price del catalogo cambia a 120000 ahora mismo,
   la siguiente llamada a GET mostrara 240000 en products_value.
   Esto es DINAMICO porque estamos en DRAFT.


PASO 5: Cotizar el work (congelar precios)

POST /works/123e4567-e89b-12d3-a456-426614174000/quote
OK Response: QuoteWorkResponseDTO con state = "QUOTED"


PASO 6: Obtener work despues de cotizar (ahora QUOTED)

GET /works/123e4567-e89b-12d3-a456-426614174000
OK Response (PRECIOS CONGELADOS):
{
  "state": "QUOTED",
  "products": [
    {
      "product_id": "223e4567-e89b-12d3-a456-426614174000",
      "product_name": "Pintura acrilica roja",
      "quantity": 2,
      "current_price": null,   null (no se usa en QUOTED)
      "snapshot": {
        "product_id": "223e4567-e89b-12d3-a456-426614174000",
        "product_name": "Pintura acrilica roja",
        "price_amount": 100000,   PRECIO CONGELADO AL MOMENTO DE COTIZAR
        "price_currency": "COP"
      }
    }
  ],
  "products_value": 200000,    2  snapshot.price_amount (CONGELADO)
  "work_value": 230000,        200000  1.15 (CONGELADO)
  "tax": 0.15
}

 IMPORTANTE: Ahora aunque el catalogo cambie a 120000, los precios
   seguiran siendo 100000 (congelado). El client tiene GARANTIA del price.


PASO 7 (Opcional): Agregar mas products en QUOTED

POST /works/123e4567-e89b-12d3-a456-426614174000/products
{
  "product_id": "323e4567-e89b-12d3-a456-426614174000",
  "quantity": 1
}
OK Response: ProductWorkItemDTO con snapshot INMEDIATAMENTE congelado


PASO 8: Obtener work con multiples products (todos congelados en QUOTED)

GET /works/123e4567-e89b-12d3-a456-426614174000
OK Response (TODOS LOS PRECIOS CONGELADOS):
{
  "state": "QUOTED",
  "products": [
    {
      "product_id": "223e4567-e89b-12d3-a456-426614174000",
      "quantity": 2,
      "snapshot": {
        "price_amount": 100000
      }
    },
    {
      "product_id": "323e4567-e89b-12d3-a456-426614174000",
      "quantity": 1,
      "snapshot": {
        "price_amount": 50000
      }
    }
  ],
  "products_value": 250000,    (2  100000) + (1  50000) = 250000
  "work_value": 287500,        250000  1.15 = 287500
  "tax": 0.15
}


RESUMEN PARA EL FRONTEND


 DRAFT (BORRADOR) 
  Mostrar: current_price de cada product (precios ACTUALES del catalogo)  
  Mostrar: products_value y work_value (se actualizan automaticamente)     
  Advertencia: "Los precios pueden cambiar hasta confirmar quotation"     
  Boton: "Solicitar quotation"  POST /works/{id}/quote               


 QUOTED (COTIZACION) 
  Mostrar: snapshot.price_amount de cada product (precios CONGELADOS)    
  Mostrar: products_value y work_value (GARANTIZADOS al client)          
  Bloqueo: Los precios NO cambian aunque se modifique el catalogo         
  Boton: "Iniciar work"  POST /works/{id}/start               


"""
from typing import List, Dict
from uuid import UUID

from app.domain.models.work import Work
from app.domain.models.product import ProductComponent
from app.application.dto.work_dto import (
    WorkDTO,
    WorkSummaryDTO,
    WorkListDTO,
    CompletionDTO
)
from app.application.mappers.product_work_item_mapper import ProductWorkItemMapper
from app.application.mappers.task_mapper import TaskMapper


class WorkMapper:
    """Mapper para convertir entre Work de dominio y DTOs."""

    @staticmethod
    def to_dto(work: Work, products_registry: Dict[UUID, ProductComponent]) -> WorkDTO:
        """
        Convierte un Work de dominio a WorkDTO completo con calculo inteligente de precios.
        
         REGLA FUNDAMENTAL: Los precios dependen del ESTADO del work
        
        
         ESTADO: DRAFT (Borrador)                                                   
        
          products_value = SUM(product.precio_catalogo * quantity)                 
          work_value = products_value * (1 + tax)                                   
          Fuente: products_registry (catalogo actual)                              
          Actualizacion: Dinamico (recalcula cada vez)                             
                                                                                      
         Ejemplo:                                                                     
           Product 1: price=100000, quantity=2  200000                           
           Product 2: price=50000, quantity=1  50000                             
           products_value = 250000                                                    
           tax = 15% (0.15)                                                           
           work_value = 250000 * 1.15 = 287500                                      
                                                                                      
          Si el price en el catalogo cambia a 120000, en el proximo GET se       
            recalcula automaticamente (precios dinamicos)                           
        
        
        
         ESTADO: QUOTED, IN_PROGRESS, DELIVERED (Cotizado/Iniciado/Entregado)       
        
          products_value = SUM(snapshot.price * quantity)                          
          work_value = products_value * (1 + tax)                                   
          Fuente: snapshots congelados en cada ProductWorkItem                     
          Actualizacion: Estatico (precios congelados, NO recalculan)              
                                                                                      
          Los precios NO cambian aunque se modifique el catalogo                  
            Los snapshots se crean al ejecutar: POST /works/{id}/quote              
        
        
        Args:
            work: Entidad de dominio Work (con estado y products)
            products_registry: Dict[UUID, ProductComponent] - Catalogo de products
                             (requerido para DRAFT, ignorado en QUOTED+)
                              Diccionario de {product_id: ProductComponent}
                              Usado SOLO en DRAFT para obtener precios actuales
                              
        Returns:
            WorkDTO con:
            - state: "DRAFT" | "QUOTED" | "IN_PROGRESS" | "DELIVERED"
            - products_value: Decimal (price total de products)
                             - DRAFT: Calculado de products_registry (dinamico)
                             - QUOTED+: De snapshots (congelado)
            - work_value: Decimal (products_value * (1 + tax))
            - products: [ProductWorkItemDTO] con:
                       - DRAFT: current_price = price del catalogo, snapshot = None
                       - QUOTED+: current_price = None, snapshot = price congelado
                       
         CASOS DE USO EN EL FRONTEND:
        
        1. Mostrar BORRADOR con precios DINAMICOS:
           GET /works/{id} (donde state="DRAFT")
            Mostrar cada product con: current_price (price actual)
            Mostrar totales: products_value, work_value
            Si el client cambia su decision, obten nuevamente y vera precios actualizados
        
        2. Mostrar COTIZACION CONFIRMADA con precios CONGELADOS:
           GET /works/{id} (donde state="QUOTED")
            Mostrar cada product con: snapshot.price_amount (price comprometido)
            Mostrar totales: products_value, work_value (congelados)
            Los precios NO cambiaran aunque se modifique el catalogo
        """
        # Map products
        products_dto = []
        for product_item in work.products:
            product = products_registry.get(product_item.product_id)
            product_dto = ProductWorkItemMapper.to_dto(product_item, product)
            products_dto.append(product_dto)
        
        # Map tasks
        tasks_dto = [TaskMapper.to_dto(task) for task in work.tasks]
        
        # Calculate values based on work state
        products_value = None
        work_value = None
        try:
            if work.is_draft:
                # En DRAFT: usar precios dinamicos del catalogo
                products_value = work._calculate_products_value(products_registry).amount
                work_value = work._calculate_work_value(products_registry).amount
            else:
                # En QUOTED/IN_PROGRESS/DELIVERED: usar precios congelados (snapshots)
                products_value = work.products_value.amount
                work_value = work.work_value.amount
        except Exception:
            # Si el calculo falla por alguna razon, los valores permanecen como None
            pass
        
        return WorkDTO(
            work_id=work.work_id,
            client_identification=work.identification_number_client.value,
            work_name=work.work_name,
            description=work.description,
            state=work.state.get_state_name().value,
            tax=work.tax,
            start_date=work.start_date,
            end_aprox_delivery_date=work.end_aprox_delivery_date,
            end_delivery_date=work.end_delivery_date,
            deposit_amount=work.deposit.amount,
            deposit_currency=work.deposit.currency,
            completion_percentage=work.completion_percentage,
            products_value=products_value,
            work_value=work_value,
            products=products_dto,
            tasks=tasks_dto
        )

    @staticmethod
    def to_summary_dto(work: Work) -> WorkSummaryDTO:
        """
        Convierte un Work de dominio a WorkSummaryDTO (sin products ni tasks).
        
        Args:
            work: Entidad de dominio Work
            
        Returns:
            WorkSummaryDTO con resumen del work
        """
        return WorkSummaryDTO(
            work_id=work.work_id,
            client_identification=work.identification_number_client.value,
            work_name=work.work_name,
            description=work.description,
            state=work.state.get_state_name().value,
            tax=work.tax,
            start_date=work.start_date,
            end_aprox_delivery_date=work.end_aprox_delivery_date,
            end_delivery_date=work.end_delivery_date,
            deposit_amount=work.deposit.amount,
            deposit_currency=work.deposit.currency,
            completion_percentage=work.completion_percentage
        )

    @staticmethod
    def to_dto_list(works: List[Work]) -> WorkListDTO:
        """
        Convierte una lista de Works a WorkListDTO.
        
        Args:
            works: Lista de entidades de dominio Work
            
        Returns:
            WorkListDTO con lista de resumenes y total
        """
        return WorkListDTO(
            works=[WorkMapper.to_summary_dto(work) for work in works],
            total=len(works)
        )

    @staticmethod
    def to_completion_dto(work: Work) -> CompletionDTO:
        """
        Convierte un Work a CompletionDTO (solo information de completitud).
        
        Args:
            work: Entidad de dominio Work
            
        Returns:
            CompletionDTO con information de progreso
        """
        finished_tasks = sum(1 for task in work.tasks if task.is_finished)
        pending_tasks = len(work.tasks) - finished_tasks
        
        return CompletionDTO(
            work_id=work.work_id,
            work_name=work.work_name,
            state=work.state.get_state_name().value,
            completion_percentage=work.completion_percentage,
            total_tasks=len(work.tasks),
            finished_tasks=finished_tasks,
            pending_tasks=pending_tasks
        )

