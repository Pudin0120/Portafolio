r"""
Work Domain Model - Aggregate Root.

Modelo de dominio para works y cotizaciones.
Implementa el patron State para manejar transiciones de estados.
Integra con Product (Composite Pattern) y Task (Factory Pattern).

Flujo de estados:
DRAFT  QUOTED  IN_PROGRESS  DELIVERED


CALCULO DE PRECIOS: LA CLAVE DEL MODELO


El modelo diferencia entre PRECIOS DINAMICOS (DRAFT) y PRECIOS CONGELADOS (QUOTED+):

 METODOS DISPONIBLES:

1. _calculate_products_value(products_registry: Dict[UUID, ProductComponent])  Money
   - Calcula el valor total de products usando el catalogo actual
   - Se usa en DRAFT para obtener precios DINAMICOS
   - Requiere products_registry (diccionario de products del catalogo)
   - Cada llamada recalcula usando precios ACTUALES
   
2. products_value (propiedad)
   - Calcula el valor total usando snapshots congelados
   - Se usa en QUOTED/IN_PROGRESS/DELIVERED
   - NO requiere parametros
   - Retorna precios CONGELADOS (nunca cambian)

3. _calculate_work_value(products_registry: Dict[UUID, ProductComponent])  Money
   - Calcula: _calculate_products_value(registry) * (1 + tax)
   - Se usa en DRAFT para precios DINAMICOS CON TAX
   
4. work_value (propiedad)
   - Calcula: products_value * (1 + tax)
   - Se usa en QUOTED/IN_PROGRESS/DELIVERED
   - Precios CONGELADOS CON TAX

 REGLA DE CONVERSION A API (WorkMapper):
   
   if work.is_draft:
       products_value = work._calculate_products_value(products_registry).amount
       work_value = work._calculate_work_value(products_registry).amount
   else:
       # QUOTED, IN_PROGRESS, DELIVERED
       products_value = work.products_value.amount
       work_value = work.work_value.amount


"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from uuid import UUID, uuid4
from datetime import datetime
from decimal import Decimal

from app.domain.value_objects import DocumentNumber, Money
from app.domain.value_objects.product_work_item import ProductWorkItem, ProductItemState
from app.domain.value_objects.work_state import WorkState, DraftState, WorkStateEnum, create_work_state
from app.domain.value_objects.product_snapshot import ProductSnapshot
from app.domain.models.task import Task
from app.domain.models.product import ProductComponent
from app.domain.models.user import User, RoleEnum
from app.domain.factories.task_factory import TaskFactory
from app.domain.domain_event import DomainEvent


@dataclass
class Work:
    """
    Modelo de dominio para work (Aggregate Root).
    
    Un work representa un proyecto completo para un client, compuesto por:
    - Products (simples o compuestos)
    - Tasks (generadas automaticamente desde los products)
    - Estados (DRAFT  QUOTED  IN_PROGRESS  DELIVERED)
    
    Reglas de negocio:
    - Solo MANAGER puede create works
    - En DRAFT: se agregan/eliminan products libremente
    - En QUOTED: se congelan precios, aun se pueden agregar products
    - En IN_PROGRESS: se generan tasks, no se pueden modificar products
    - En DELIVERED: work completed, inmutable
    
    Attributes:
        work_id: Identificador unico del work
        identification_number_client: Identificacion del client
        work_name: Nombre del work
        description: Description detallada
        state: Estado actual del work (State Pattern)
        products: Lista de products con sus snapshots
        tasks: Lista de tasks generadas (solo en IN_PROGRESS)
        tax: Porcentaje de ganancia del taller (ej: 0.15 = 15%)
        start_date: Fecha de inicio
        end_aprox_delivery_date: Fecha aproximada de entrega
        end_delivery_date: Fecha real de entrega (None hasta DELIVERED)
        deposit: Deposito inicial del client
    """
    
    work_id: UUID
    identification_number_client: DocumentNumber
    work_name: str
    description: str
    state: WorkState
    products: List[ProductWorkItem] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    tax: float = 0.0
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_aprox_delivery_date: Optional[datetime] = None
    end_delivery_date: Optional[datetime] = None
    deposit: Money = field(default_factory=lambda: Money(amount=Decimal("0")))
    tenant_id: Optional[UUID] = None
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False, repr=False)
    
    def __post_init__(self):
        """Validaciones post-inicializacion."""
        if self.tax < 0:
            raise ValueError("El tax no puede ser negativo")
        
        if not self.deposit.is_positive() and self.deposit.amount != Decimal("0"):
            raise ValueError("El deposito debe ser positivo o cero")
    
    # ==================== PROPIEDADES ====================
    
    @property
    def is_draft(self) -> bool:
        """Verifica si el work esta en estado DRAFT."""
        return self.state.get_state_name() == WorkStateEnum.DRAFT
    
    @property
    def is_quoted(self) -> bool:
        """Verifica si el work esta en estado QUOTED."""
        return self.state.get_state_name() == WorkStateEnum.QUOTED
    
    @property
    def is_in_progress(self) -> bool:
        """Verifica si el work esta en estado IN_PROGRESS."""
        return self.state.get_state_name() == WorkStateEnum.IN_PROGRESS
    
    @property
    def is_delivered(self) -> bool:
        """Verifica si el work esta en estado DELIVERED."""
        return self.state.get_state_name() == WorkStateEnum.DELIVERED
    
    @property
    def products_value(self) -> Money:
        """
        Calcula el valor total de products usando snapshots congelados.
        
        En estados cotizados o posteriores, usa los precios congelados.
        En DRAFT, retorna 0 si no hay snapshots.
        
        Returns:
            Suma de todos los products  cantidades
        """
        total = Money(amount=Decimal("0"))
        
        for product_item in self.products:
            if product_item.has_snapshot():
                price = product_item.get_frozen_price()
                item_total = price.multiply(Decimal(str(product_item.quantity)))
                total = total + item_total
        
        return total
    
    def _calculate_products_value(
        self,
        products_registry: Optional[Dict[UUID, ProductComponent]] = None
    ) -> Money:
        """
        Calcula el valor total de products (version con parametro).
        
        - En DRAFT: usa el price actual del product (requiere products_registry)
        - En otros estados: usa el price congelado del snapshot
        
        Args:
            products_registry: Diccionario {product_id: ProductComponent}
            
        Returns:
            Suma de todos los products  cantidades
        """
        total = Money(amount=Decimal("0"))
        
        for product_item in self.products:
            price = None
            if product_item.has_snapshot():
                price = product_item.get_frozen_price()
            elif products_registry:
                product = products_registry.get(product_item.product_id)
                if product:
                    try:
                        price = product.get_total_price()
                    except ValueError:
                        price = None  # O manejar como error si se prefiere
            
            if price is None:
                # Si no hay price, no se puede calcular el valor
                # En un escenario real, esto podria lanzar un error o ser manejado
                # de una forma especifica segun las reglas de negocio.
                # Por ahora, lo omitimos del calculo.
                continue

            item_total = price.multiply(Decimal(str(product_item.quantity)))
            total = total + item_total
        
        return total
    
    @property
    def work_value(self) -> Money:
        """
        Calcula el valor total del work (products_value  (1 + tax)) usando snapshots.
        
        Returns:
            Valor con tax aplicado
        """
        tax_multiplier = Decimal(str(1 + self.tax))
        return self.products_value.multiply(tax_multiplier)
    
    def _calculate_work_value(
        self,
        products_registry: Optional[Dict[UUID, ProductComponent]] = None
    ) -> Money:
        """
        Calcula el valor total del work (version con parametro).
        
        Args:
            products_registry: Diccionario para calcular `products_value`
            
        Returns:
            Valor con tax aplicado
        """
        products_val = self._calculate_products_value(products_registry)
        tax_multiplier = Decimal(str(1 + self.tax))
        return products_val.multiply(tax_multiplier)
    
    @property
    def completion_percentage(self) -> float:
        """
        Calcula el porcentaje de completitud del work.
        
        Se basa en (tasks finalizadas / total tasks)  100.
        
        Returns:
            Porcentaje de 0 a 100
        """
        if not self.tasks:
            return 0.0
        
        finished_tasks = sum(1 for task in self.tasks if task.is_finished)
        return (finished_tasks / len(self.tasks)) * 100
    
    # ==================== GESTION DE PRODUCTS ====================
    
    def add_product(
        self, 
        product: ProductComponent, 
        quantity: int,
        execution_order: Optional[int] = None
    ) -> ProductWorkItem:
        """
        Agrega un product al work.
        
        En DRAFT: se agrega sin snapshot
        En QUOTED: se agrega y se congela su snapshot inmediatamente
        
        Args:
            product: Product a agregar (Simple o Composite)
            quantity: Quantity del product
            execution_order: Orden de ejecucion (si None, se agrega al final)
            
        Returns:
            ProductWorkItem creado
            
        Raises:
            ValueError: Si el estado no permite agregar products
        """
        from app.domain.events.work_events import ProductAddedToWork
        
        if not self.state.can_add_products():
            raise ValueError(f"No se pueden agregar products en estado {self.state}")
        
        # Validar que el product tenga un price valid
        try:
            product_price = product.get_total_price()
            if product_price is None:
                raise ValueError(
                    f"El product '{product.name}' no tiene un price valid. "
                    f"Configure un price manual o asigne un material con price."
                )
        except (ValueError, AttributeError) as e:
            raise ValueError(
                f"No se puede agregar el product '{product.name}': {str(e)}"
            )
        
        # Determinar orden de ejecucion
        if execution_order is None:
            execution_order = len(self.products)
        
        # Create ProductWorkItem
        product_item = ProductWorkItem(
            product_id=product.id,
            work_id=self.work_id,
            quantity=quantity,
            execution_order=execution_order,
            state=ProductItemState.PENDING,
            snapshot=None
        )
        
        # Si ya esta cotizado, congelar snapshot inmediatamente
        if self.is_quoted:
            try:
                snapshot = self._create_product_snapshot(product)
                product_item.freeze_snapshot(snapshot)
            except ValueError as e:
                raise ValueError(
                    f"No se puede agregar el product a un work cotizado: {str(e)}"
                )
        
        self.products.append(product_item)
        
        # Generar evento
        event = ProductAddedToWork(
            event_id=uuid4(),
            occurred_at=datetime.utcnow(),
            aggregate_id=self.work_id,
            work_id=self.work_id,
            product_id=product.id,
            product_name=product.name,
            quantity=quantity,
            execution_order=execution_order
        )
        self._domain_events.append(event)
        
        return product_item
    
    def remove_product(self, product_id: UUID) -> None:
        """
        Elimina un product del work.
        
        Solo permitido en DRAFT o QUOTED.
        
        Args:
            product_id: ID del product a delete
            
        Raises:
            ValueError: Si el estado no permite delete products
        """
        from app.domain.events.work_events import ProductRemovedFromWork
        
        if not self.state.can_remove_products():
            raise ValueError(f"No se pueden delete products en estado {self.state}")
        
        # Search product
        product_item = next((p for p in self.products if p.product_id == product_id), None)
        if product_item is None:
            raise ValueError(f"Product {product_id} no encontrado en el work")
        
        self.products.remove(product_item)
        
        # Generar evento
        event = ProductRemovedFromWork(
            event_id=uuid4(),
            occurred_at=datetime.utcnow(),
            aggregate_id=self.work_id,
            work_id=self.work_id,
            product_id=product_id,
            product_name="Product"  # Podriamos almacenar el nombre antes de delete
        )
        self._domain_events.append(event)
    
    def reorder_product(self, product_id: UUID, new_order: int) -> None:
        """
        Changes the execution order of a product.
        
        Permitido en DRAFT, QUOTED e IN_PROGRESS.
        - En DRAFT/QUOTED: Solo reordena products
        - En IN_PROGRESS: Reordena products Y sus tasks asociadas (respetando jerarquia)
        
        Args:
            product_id: ID del product
            new_order: Nuevo orden de ejecucion (0-based)
            
        Raises:
            ValueError: Si el estado no permite reordenar o hay errores
        """
        # Validar que el estado permite reordenar
        # DRAFT, QUOTED permiten siempre. IN_PROGRESS permite solo si hay tasks.
        state_name = self.state.get_state_name().value
        if state_name == "DELIVERED":
            raise ValueError(f"No se puede reordenar products en estado {self.state}")
        
        product_item = next((p for p in self.products if p.product_id == product_id), None)
        if product_item is None:
            raise ValueError(f"Product {product_id} no encontrado en el work")
        
        # Validate new order
        if new_order < 0 or new_order >= len(self.products):
            raise ValueError(f"Orden invalid: {new_order}. Debe estar entre 0 y {len(self.products) - 1}")
        
        # Get current position
        current_index = self.products.index(product_item)
        
        # Si no cambia de posicion, no hacer nada
        if current_index == new_order:
            return
        
        # Si hay tasks (IN_PROGRESS), reordenar las tasks asociadas al product primero
        if self.tasks:
            self._reorder_product_tasks(product_id, current_index, new_order)
        
        # Remove from current position
        self.products.pop(current_index)
        
        # Insert at new position
        self.products.insert(new_order, product_item)
        
        # Reassign execution_order to all products to maintain consecutive indices
        for idx, product in enumerate(self.products):
            product.execution_order = idx
    
    def _reorder_product_tasks(self, product_id: UUID, old_product_order: int, new_product_order: int) -> None:
        """
        Reordena las tasks asociadas a un product cuando el product cambia de orden.
        
        Mueve todas las tasks del product manteniendo su orden relativo (slots).
        
        Este metodo simula el reordenamiento de products y recalcula las posiciones de todas las tasks.
        
        Args:
            product_id: ID del product a mover
            old_product_order: Orden anterior del product (antes de moverlo)
            new_product_order: Nuevo orden del product (donde se quiere mover)
        """
        # Create una lista simulada del nuevo orden de products
        products_copy = self.products.copy()
        product_to_move = products_copy[old_product_order]
        
        # Simular el reordenamiento de products
        products_copy.pop(old_product_order)
        products_copy.insert(new_product_order, product_to_move)
        
        # Ahora recalcular las posiciones de las tasks basandonos en el nuevo orden
        new_execution_order = 0
        
        for product_item in products_copy:
            # Obtener todas las tasks de este product, ordenadas por su slot/orden actual
            product_tasks = sorted(
                [t for t in self.tasks if t.product_id == product_item.product_id],
                key=lambda t: (t.composite_task_slot if t.composite_task_slot is not None else 0, t.execution_order)
            )
            
            # Asignar nuevos execution_order a las tasks de este product
            for task in product_tasks:
                task.execution_order = new_execution_order
                new_execution_order += 1
        
        # Reordenar la lista completa de tasks por su nuevo execution_order
        self.tasks.sort(key=lambda t: t.execution_order)
    
    # ==================== TRANSICIONES DE ESTADO ====================
    
    def quote(self, quoted_by: User, products_registry: Dict[UUID, ProductComponent]) -> None:
        """
        Cotiza el work (DRAFT  QUOTED).
        
        Congela los precios de todos los products creando snapshots.
        
        Args:
            quoted_by: User que cotiza (debe ser MANAGER)
            products_registry: Diccionario {product_id: ProductComponent} para obtener products
            
        Raises:
            ValueError: Si no se puede cotizar
        """
        from app.domain.events.work_events import WorkQuoted
        
        # EMPLOYEE, SUPERVISOR y MANAGER pueden cotizar
        allowed_roles = {RoleEnum.EMPLOYEE, RoleEnum.SUPERVISOR, RoleEnum.MANAGER}
        if quoted_by.role not in allowed_roles:
            raise ValueError("Solo EMPLOYEE, SUPERVISOR o MANAGER pueden cotizar works")
        
        if not self.state.can_quote():
            raise ValueError(f"No se puede cotizar desde estado {self.state}")
        
        if not self.products:
            raise ValueError("No se puede cotizar un work sin products")
        
        # Congelar snapshots de todos los products
        for product_item in self.products:
            if not product_item.has_snapshot():
                product = products_registry.get(product_item.product_id)
                if product is None:
                    raise ValueError(f"Product {product_item.product_id} no encontrado")
                
                snapshot = self._create_product_snapshot(product)
                product_item.freeze_snapshot(snapshot)
        
        # Transicion de estado
        self.state = self.state.quote(self)
        
        # Calcular valores
        products_val = self._calculate_products_value(products_registry)
        work_val = self._calculate_work_value(products_registry)
        
        # Generar evento
        event = WorkQuoted(
            event_id=uuid4(),
            occurred_at=datetime.utcnow(),
            aggregate_id=self.work_id,
            work_id=self.work_id,
            client_identification=str(self.identification_number_client),
            work_name=self.work_name,
            products_value=products_val.amount,
            work_value=work_val.amount,
            tax_percentage=self.tax,
            total_products=len(self.products),
            quoted_by_user_id=uuid4()  # Idealmente UUID del user
        )
        self._domain_events.append(event)
    
    def start_work(
        self, 
        started_by: User, 
        products_registry: Dict[UUID, ProductComponent]
    ) -> List[Task]:
        """
        Starts the work (QUOTED  IN_PROGRESS).
        
        Genera todas las tasks desde los products usando TaskFactory.
        
        Args:
            started_by: User que inicia (debe ser MANAGER)
            products_registry: Diccionario {product_id: ProductComponent}
            
        Returns:
            Lista de tasks generadas
            
        Raises:
            ValueError: Si no se puede iniciar
        """
        from app.domain.events.work_events import WorkStarted
        
        if started_by.role != RoleEnum.MANAGER:
            raise ValueError("Solo MANAGER puede iniciar works")
        
        if not self.state.can_start_work():
            raise ValueError(f"No se puede iniciar work desde estado {self.state}")
        
        if not self.products:
            raise ValueError("No se puede iniciar un work sin products")
        
        # Generar tasks para todos los products
        all_tasks = []
        current_order = 0
        
        # Ordenar products por execution_order
        sorted_products = sorted(self.products, key=lambda p: p.execution_order)
        
        for product_item in sorted_products:
            product = products_registry.get(product_item.product_id)
            if product is None:
                raise ValueError(f"Product {product_item.product_id} no encontrado")
            
            # Generar tasks usando TaskFactory
            tasks, next_order = TaskFactory.create_tasks_from_product(
                product=product,
                work_id=self.work_id,
                product_quantity=product_item.quantity,
                base_order=current_order,
                quotation_quantity=product_item.quantity,
                tax=self.tax
            )
            
            # Vincular tasks al ProductWorkItem
            for task in tasks:
                product_item.add_task_id(task.task_id)
            
            all_tasks.extend(tasks)
            current_order = next_order
        
        # Marcar todos los products como en progreso
        for product_item in self.products:
            product_item.start_progress()
        
        self.tasks = all_tasks
        
        # Transicion de estado
        self.state = self.state.start_work(self)
        
        # Generar evento
        event = WorkStarted(
            event_id=uuid4(),
            occurred_at=datetime.utcnow(),
            aggregate_id=self.work_id,
            work_id=self.work_id,
            client_identification=str(self.identification_number_client),
            work_name=self.work_name,
            total_tasks_generated=len(all_tasks),
            started_by_user_id=uuid4()
        )
        self._domain_events.append(event)
        
        return all_tasks
    
    def deliver(self, delivered_by: User) -> None:
        """
        Entrega el work (IN_PROGRESS  DELIVERED).
        
        Todas las tasks deben estar finalizadas.
        
        Args:
            delivered_by: User que entrega (debe ser MANAGER)
            
        Raises:
            ValueError: Si no se puede entregar
        """
        from app.domain.events.work_events import WorkDelivered
        
        if delivered_by.role != RoleEnum.MANAGER:
            raise ValueError("Solo MANAGER puede entregar works")
        
        if not self.state.can_deliver():
            raise ValueError(f"No se puede entregar desde estado {self.state}")
        
        # Verificar que todas las tasks esten finalizadas
        unfinished_tasks = [t for t in self.tasks if not t.is_finished]
        if unfinished_tasks:
            raise ValueError(
                f"No se puede entregar: {len(unfinished_tasks)} tasks sin finalizar"
            )
        
        # Marcar todos los products como completados
        for product_item in self.products:
            if not product_item.is_completed():
                product_item.mark_completed()
        
        # Transicion de estado
        self.state = self.state.deliver(self)
        self.end_delivery_date = datetime.utcnow()
        
        # Generar evento
        event = WorkDelivered(
            event_id=uuid4(),
            occurred_at=datetime.utcnow(),
            aggregate_id=self.work_id,
            work_id=self.work_id,
            client_identification=str(self.identification_number_client),
            work_name=self.work_name,
            delivery_date=self.end_delivery_date,
            final_value=self.work_value.amount,
            delivered_by_user_id=uuid4()
        )
        self._domain_events.append(event)
    
    # ==================== GESTION DE TAREAS ====================
    
    def get_task(self, task_id: UUID) -> Optional[Task]:
        """Obtiene una task por su ID."""
        return next((t for t in self.tasks if t.task_id == task_id), None)
    
    def get_tasks_by_product(self, product_id: UUID) -> List[Task]:
        """Obtiene todas las tasks de un product especifico."""
        return [t for t in self.tasks if t.product_id == product_id]
    
    def get_tasks_by_user(self, user_id: str) -> List[Task]:
        """Obtiene todas las tasks asignadas a un user."""
        return [t for t in self.tasks if t.assigned_user_id == user_id]
    
    def get_ready_tasks(self) -> List[Task]:
        """Obtiene todas las tasks listas para ejecutar (estado READY)."""
        return [t for t in self.tasks if t.is_ready]
    
    def unblock_next_task(self, completed_task: Task) -> Optional[Task]:
        """
        Desbloquea la siguiente task en la secuencia despues de que una task se completa o finaliza.
        
        Busca la siguiente task en orden de ejecucion que:
        1. Este bloqueada (is_blocked=True)
        2. Tenga como previous_task_id el ID de la task completada
        
        Args:
            completed_task: La task que acaba de completarse o finalizarse
            
        Returns:
            La task desbloqueada, o None si no hay ninguna task para desbloquear
        """
        if not (completed_task.is_completed or completed_task.is_finished):
            return None
        
        # Search la task que esta bloqueada directamente por esta task
        # Una task solo puede bloquear a otra task (relacion 1:1)
        next_task = next(
            (task for task in self.tasks
             if task.is_blocked and task.previous_task_id == completed_task.task_id),
            None
        )
        
        if next_task:
            # Desbloquear la task (ASSIGNED  READY)
            next_task.unblock()
            
            # Agregar los eventos de dominio de la task al work
            self._domain_events.extend(next_task._domain_events)
            
            return next_task
        
        return None
    
    def get_composite_task_groups(self) -> Dict[Optional[UUID], List[Task]]:
        """
        Agrupa las tasks por su product compuesto padre.
        
        Returns:
            Dictionary where:
            - Key: parent_composite_id (None for standalone tasks, UUID for composite tasks)
            - Value: List of tasks belonging to that group, sorted by execution_order
            
        Example:
            {
                None: [standalone_task_1, standalone_task_2],
                composite_id_1: [subtask_1, subtask_2, subtask_3],
                composite_id_2: [subtask_1, subtask_2],
            }
        """
        groups: Dict[Optional[UUID], List[Task]] = {}
        
        for task in self.tasks:
            composite_id = task.parent_composite_id
            if composite_id not in groups:
                groups[composite_id] = []
            groups[composite_id].append(task)
        
        # Sort tasks within each group by execution_order
        for composite_id in groups:
            groups[composite_id].sort(key=lambda t: t.execution_order)
        
        return groups
    
    def reorder_task(self, task_id: UUID, new_execution_order: int) -> None:
        """
        Cambia el orden de ejecucion de una task, respetando la jerarquia.
        
        Ahora permite reordenar tasks dentro de products compuestos,
        actualizando automaticamente los composite_task_slot.
        
        REGLAS CLAVE:
        - Las subtareas NO pueden salir de su bloque compuesto
        - Las tasks simples NO pueden insertarse DENTRO de un bloque compuesto
        - Solo pueden insertarse ANTES o DESPUES de un bloque (como unidad)
        
        Valida que:
        - La task existe
        - El nuevo orden es valid
        - No se rompe la jerarquia del product compuesto
        
        Args:
            task_id: ID de la task
            new_execution_order: Nuevo orden (debe estar en rango valid si es de compuesto)
            
        Raises:
            ValueError: Si viola restricciones jerarquicas
        """
        from app.domain.validators.task_hierarchy_validator import TaskHierarchyValidator
        
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} no encontrada")
        
        # Si la task no se movio, no hacer nada
        if task.execution_order == new_execution_order:
            return
        
        # NUEVA LOGICA: Detectar si la nueva posicion cae DENTRO de un bloque compuesto
        # (no antes ni despues, sino adentro) y rechazarlo
        if not task.parent_composite_id:
            # Es una task simple
            composite_at_target = self._get_composite_at_position(new_execution_order)
            if composite_at_target:
                # La task simple intenta insertarse DENTRO de un bloque compuesto
                # Necesitamos determinar si esta antes o despues del bloque
                composite_tasks = sorted(
                    [t for t in self.tasks if t.parent_composite_id == composite_at_target],
                    key=lambda t: t.execution_order
                )
                block_start = composite_tasks[0].execution_order
                block_end = composite_tasks[-1].execution_order
                
                # Si intenta entrar en la mitad del bloque, rechazarlo
                if block_start < new_execution_order < block_end:
                    raise ValueError(
                        f"No se puede insertar una task simple dentro de un bloque compuesto. "
                        f"Bloque ocupa posiciones [{block_start}, {block_end}]. "
                        f"Intenta insertar en posicion {new_execution_order}. "
                        f"Use posiciones {block_start} (antes) o {block_end + 1} (despues)."
                    )
        else:
            # Es una subtarea: validar que no salga de su rango
            is_valid, error_msg = TaskHierarchyValidator.validate_task_reorder(
                task=task,
                new_execution_order=new_execution_order,
                all_tasks=self.tasks
            )
            
            if not is_valid:
                raise ValueError(f"No se puede reordenar task: {error_msg}")
        
        # Save orden anterior para reordenar otras tasks
        old_order = task.execution_order
        
        # Actualizar orden de la task
        task.execution_order = new_execution_order
        
        # Reordenar otras tasks para mantener consistencia
        if new_execution_order < old_order:
            # Movio hacia arriba: desplazar hacia abajo las tasks en el medio
            for other_task in self.tasks:
                if other_task.task_id != task_id:
                    if new_execution_order <= other_task.execution_order < old_order:
                        other_task.execution_order += 1
        elif new_execution_order > old_order:
            # Movio hacia abajo: desplazar hacia arriba las tasks en el medio
            for other_task in self.tasks:
                if other_task.task_id != task_id:
                    if old_order < other_task.execution_order <= new_execution_order:
                        other_task.execution_order -= 1
        
        # Actualizar composite_task_slot si es una task de compuesto
        if task.parent_composite_id:
            self._update_composite_task_slots(task.parent_composite_id)
        
        # Reordenar lista para mantener consistencia
        self.tasks.sort(key=lambda t: t.execution_order)
    
    def _update_composite_task_slots(self, composite_id: UUID) -> None:
        """
        Actualiza los composite_task_slot de todas las tasks de un compuesto.
        
        Recalcula los slots basandose en el execution_order actual,
        asegurando que sean consecutivos (0, 1, 2, 3, ...).
        
        Args:
            composite_id: ID del product compuesto
        """
        # Obtener todas las tasks del compuesto
        composite_tasks = [
            t for t in self.tasks 
            if t.parent_composite_id == composite_id
        ]
        
        # Ordenar por execution_order
        composite_tasks.sort(key=lambda t: t.execution_order)
        
        # Actualizar slots consecutivos
        for idx, task in enumerate(composite_tasks):
            task.composite_task_slot = idx
            task.composite_total_slots = len(composite_tasks)
    
    def _get_composite_at_position(self, position: int) -> Optional[UUID]:
        """
        Detecta si una posicion cae dentro de un bloque compuesto.
        
        Verifica si la posicion solicitada cae DENTRO del rango de cualquier
        bloque compuesto (no solo en tasks exactas).
        
        Args:
            position: Posicion (execution_order) a verificar
            
        Returns:
            UUID del product compuesto si la posicion esta dentro de un bloque,
            None en caso contrario
        """
        # Agrupar tasks por composite
        composites: Dict[Optional[UUID], List['Task']] = {}
        for task in self.tasks:
            composite_id = task.parent_composite_id
            if composite_id not in composites:
                composites[composite_id] = []
            composites[composite_id].append(task)
        
        # Para cada bloque compuesto, verificar si position cae dentro
        for composite_id, tasks in composites.items():
            if composite_id is None:  # Skip tasks sin composite
                continue
            
            task_orders = [t.execution_order for t in tasks]
            min_order = min(task_orders)
            max_order = max(task_orders)
            
            # Si la posicion cae DENTRO del rango del bloque
            if min_order <= position <= max_order:
                return composite_id
        
        return None
    
    # ==================== UTILIDADES ====================
    
    def _create_product_snapshot(self, product: ProductComponent) -> ProductSnapshot:
        """
        Crea un snapshot congelado de un product.
        
        Args:
            product: Product del cual create el snapshot
            
        Returns:
            ProductSnapshot inmutable con price y composicion congelados
            
        Raises:
            ValueError: Si el product no tiene price definido
        """
        try:
            total_price = product.get_total_price()
        except (ValueError, AttributeError) as e:
            raise ValueError(
                f"No se puede create snapshot del product '{product.name}': "
                f"El product no tiene un price valid configurado. {str(e)}"
            )
        
        if total_price is None:
            raise ValueError(
                f"No se puede create snapshot del product '{product.name}': "
                f"El price es None. Asegurate de que el product tenga un price "
                f"manual o un material con price configurado."
            )
        
        return ProductSnapshot(
            product_id=product.id,
            product_name=product.name,
            product_type="composite" if product.is_composite() else "simple",
            price=total_price,
            composition=product.get_material_composition(),
            dimensions=getattr(product, 'dimensions', {}),
            quantity_multiplier=getattr(product, 'quantity_multiplier', Decimal("1.0"))
        )
    
    def clear_domain_events(self) -> List[DomainEvent]:
        """
        Retorna y limpia los eventos de dominio acumulados.
        
        Returns:
            Lista de eventos de dominio
        """
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    def __str__(self) -> str:
        return f"Work[{self.work_name}] - {self.state} - {len(self.products)} products"
