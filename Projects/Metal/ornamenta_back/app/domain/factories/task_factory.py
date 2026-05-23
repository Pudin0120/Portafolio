"""
Task Factory Pattern Implementation.

Factory para generar tasks automaticamente desde products.
Maneja la recursion para products compuestos anidados.
Registra la jerarquia de products compuestos en las tasks.
"""
from typing import List, Tuple, Optional, cast
import uuid
from decimal import Decimal

from app.domain.models.product import ProductComponent, SimpleProduct, CompositeProduct
from app.domain.models.task import Task
from app.domain.value_objects.money import Money
from app.domain.value_objects.state_task import StateTask, StateTaskEnum


class TaskFactory:
    """
    Factory para generar tasks desde products.
    
    Responsabilidades:
    - Generar tasks desde SimpleProducts
    - Recursion para CompositeProducts anidados
    - Asignar orden de ejecucion correcto
    - Mantener information de bloqueo para tasks secuenciales
    - Registrar jerarquia de products compuestos (parent_composite_id, slot)
    
    Reglas de negocio:
    - SimpleProduct  1 Task
    - CompositeProduct  N Tasks (recursivamente desde sus componentes)
    - Tasks de un CompositeProduct son secuenciales entre si
    - Tasks de diferentes products pueden ejecutarse en paralelo
    - Las tasks registran su pertenencia a un compuesto (jerarquia)
    """
    
    @staticmethod
    def create_tasks_from_product(
        product: ProductComponent,
        work_id: uuid.UUID,
        product_quantity: int = 1,
        base_order: int = 0,
        parent_composite_id: Optional[uuid.UUID] = None,
        slot_within_composite: Optional[int] = None,
        total_slots_in_composite: Optional[int] = None,
        quotation_quantity: Optional[int] = None,
        tax: float = 0.0
    ) -> Tuple[List[Task], int]:
        """
        Genera tasks desde un product (simple o compuesto).
        
        Args:
            product: Product del cual generar tasks
            work_id: ID del work al que pertenecen las tasks
            product_quantity: Quantity del product (multiplica las tasks)
            base_order: Orden base para comenzar la numeracion
            parent_composite_id: Si este product es parte de un compuesto, el ID del padre
            slot_within_composite: Posicion dentro del compuesto (0, 1, 2...)
            total_slots_in_composite: Total de tasks que genera el compuesto
            quotation_quantity: Quantity original de la quotation (para mostrar en el nombre)
            tax: Porcentaje de impuesto del taller (ej: 0.60 para 60%)
            
        Returns:
            Tupla con (lista de tasks generadas, proximo orden disponible)
            
        Example:
            >>> # Simple product
            >>> tasks, next_order = TaskFactory.create_tasks_from_product(
            ...     chapa_product, work_id, quantity=2, base_order=0, tax=0.60
            ... )
            >>> len(tasks)  # 1 task (SimpleProduct)
            1
            
            >>> # Composite product con jerarquia
            >>> tasks, next_order = TaskFactory.create_tasks_from_product(
            ...     puerta_product, work_id, quantity=1, base_order=0, tax=0.60
            ... )
            >>> len(tasks)  # N tasks segun componentes
            5
            >>> tasks[0].parent_composite_id  # ID del compuesto
            UUID('...')
            >>> tasks[0].composite_task_slot  # Posicion dentro del compuesto
            0
        """
        # Si no se especifica quotation_quantity, usar product_quantity
        if quotation_quantity is None:
            quotation_quantity = product_quantity
            
        if product.is_composite():
            return TaskFactory._create_tasks_from_composite(
                cast(CompositeProduct, product), work_id, product_quantity, base_order,
                parent_composite_id, slot_within_composite, total_slots_in_composite, quotation_quantity, tax
            )
        else:
            return TaskFactory._create_tasks_from_simple(
                cast(SimpleProduct, product), work_id, product_quantity, base_order,
                parent_composite_id, slot_within_composite, total_slots_in_composite, quotation_quantity, tax
            )
    
    @staticmethod
    def _create_tasks_from_simple(
        product: SimpleProduct,
        work_id: uuid.UUID,
        product_quantity: int,
        base_order: int,
        parent_composite_id: Optional[uuid.UUID] = None,
        slot_within_composite: Optional[int] = None,
        total_slots_in_composite: Optional[int] = None,
        quotation_quantity: Optional[int] = None,
        tax: float = 0.0
    ) -> Tuple[List[Task], int]:
        """
        Genera una task desde un product simple.
        
        Args:
            product: Product simple
            work_id: ID del work
            product_quantity: Quantity del product (para calculos internos)
            base_order: Orden base
            parent_composite_id: ID del compuesto padre (si aplica)
            slot_within_composite: Posicion dentro del compuesto
            total_slots_in_composite: Total de slots en el compuesto
            quotation_quantity: Quantity original de la quotation (para mostrar)
            tax: Porcentaje de impuesto del taller (ej: 0.60 para 60%)
            
        Returns:
            Tupla con ([task], proximo_orden)
        """
        # FIXED: Usar quotation_quantity para el nombre de la task
        # - Para products simples standalone: quotation_quantity es la quantity en la quotation
        # - Para componentes de composites: quotation_quantity es la quantity del composite en la quotation
        # Siempre mostrar el multiplicador, incluso si es (x1)
        task_name = f"{product.name}"
        if quotation_quantity:
            task_name += f" (x{quotation_quantity})"
        
        # Get price from product
        base_price = product.get_total_price()
        if base_price is None:
            base_price = Money(amount=Decimal("0"))
        
        # Calculate estimated_value as: base_price * (1 + tax)
        # This is the total price charged to the customer (base + workshop profit)
        tax_multiplier = Decimal(str(1 + tax))
        estimated_value = base_price.multiply(tax_multiplier)
        
        # Calculate labor as: (estimated_value - base_price) / 2
        # This is half of the workshop's profit (the tax portion)
        # Formula:
        # - profit = estimated_value - base_price = base_price * tax
        # - labor = profit / 2 = (base_price * tax) / 2
        profit = estimated_value - base_price  # profit = base_price * tax
        labor = profit.multiply(Decimal("0.5"))  # labor = profit / 2
        
        task = Task(
            task_id=uuid.uuid4(),
            work_id=work_id,
            product_id=product.id,
            parent_composite_id=parent_composite_id,
            composite_task_slot=slot_within_composite,
            composite_total_slots=total_slots_in_composite,
            task_name=task_name,
            description=f"Realizar: {product.description or product.name}",
            state=StateTask(value=StateTaskEnum.PENDING),
            labor=labor,
            estimated_value=estimated_value,
            execution_order=base_order,
            requires_validation=True,
            is_blocked=False,
            previous_task_id=None,
            assigned_user_id=None,
            completed_by_user_id=None,
            validated_by_user_id=None
        )
        
        return ([task], base_order + 1)
    
    @staticmethod
    def _create_tasks_from_composite(
        product: CompositeProduct,
        work_id: uuid.UUID,
        product_quantity: int,
        base_order: int,
        parent_composite_id: Optional[uuid.UUID] = None,
        slot_within_composite: Optional[int] = None,
        total_slots_in_composite: Optional[int] = None,
        quotation_quantity: Optional[int] = None,
        tax: float = 0.0
    ) -> Tuple[List[Task], int]:
        """
        Genera tasks desde un product compuesto (recursivamente).
        
        Las tasks generadas registran su pertenencia al compuesto mediante
        parent_composite_id, composite_task_slot y composite_total_slots.
        
        Args:
            product: Product compuesto
            work_id: ID del work
            product_quantity: Quantity del product
            base_order: Orden base
            parent_composite_id: ID del compuesto padre (para compuestos anidados)
            slot_within_composite: Posicion dentro del compuesto padre
            total_slots_in_composite: Total de slots en el compuesto padre
            quotation_quantity: Quantity original de la quotation
            tax: Porcentaje de impuesto del taller (ej: 0.60 para 60%)
            
        Returns:
            Tupla con (lista de tasks, proximo_orden)
        """
        all_tasks = []
        current_order = base_order
        previous_task_id = None
        
        components = product.get_components()
        total_components = len(components)
        
        # Iterar sobre los componentes en orden
        for component_idx, component_qty in enumerate(components):
            component = component_qty.component
            quantity = component_qty.quantity * product_quantity
            
            # Calcular quotation_quantity correctamente para este componente
            # Si el product compuesto tiene quantity 2 en la quotation y cada componente
            # tiene quantity 10, entonces quotation_quantity del componente debe ser 2 * 10 = 20
            component_quotation_quantity = quotation_quantity * component_qty.quantity if quotation_quantity else None
            
            # Generar tasks recursivamente con information de jerarquia
            component_tasks, next_order = TaskFactory.create_tasks_from_product(
                component, 
                work_id, 
                quantity,  # Quantity total para calculos de materials/precios
                current_order,
                parent_composite_id=product.id,  # Este compuesto es el padre
                slot_within_composite=component_idx,  # Posicion del componente
                total_slots_in_composite=total_components,  # Total de componentes
                quotation_quantity=component_quotation_quantity,  # Multiplicador correcto para el componente
                tax=tax  # Pasar tax a la recursion
            )
            
            # Las tasks de un CompositeProduct son secuenciales
            # La primera task de este componente esta bloqueada por la ultima del anterior
            if component_tasks and previous_task_id is not None:
                first_task = component_tasks[0]
                first_task.is_blocked = True
                first_task.previous_task_id = previous_task_id
            
            all_tasks.extend(component_tasks)
            current_order = next_order
            
            # La ultima task de este componente bloquea la primera del siguiente
            if component_tasks:
                previous_task_id = component_tasks[-1].task_id
        
        return (all_tasks, current_order)
    
    @staticmethod
    def calculate_total_tasks(product: ProductComponent, quantity: int = 1) -> int:
        """
        Calcula el number total de tasks que generara un product.
        
        Util para estimaciones antes de generar las tasks.
        
        Args:
            product: Product a analizar
            quantity: Quantity del product
            
        Returns:
            Number total de tasks que se generaran
        """
        if not product.is_composite():
            return 1  # SimpleProduct  1 task
        
        # CompositeProduct: sumar tasks de todos los componentes
        composite = cast(CompositeProduct, product)
        total = 0
        for component_qty in composite.get_components():
            component_quantity = component_qty.quantity * quantity
            total += TaskFactory.calculate_total_tasks(
                component_qty.component, component_quantity
            )
        
        return total

