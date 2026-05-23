"""
Use case para actualizar PayrollHistory cuando se completa una task.
Este caso de uso se ejecuta automaticamente cuando una task alcanza el estado FINISHED.

Ubicacion: app/application/use_cases/update_payroll_task.py
"""
import uuid
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.domain.repositories.task_repository import TaskRepository
from app.domain.repositories.payroll_history_repository import PayrollHistoryRepository
from app.domain.repositories.payroll_repository import PayrollRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.payroll_history_task_repository import PayrollHistoryTaskRepository
from app.domain.models.task import Task
from app.domain.models.payroll_history_task import PayrollHistoryTask
from app.domain.value_objects.contract_type import ContractTypeEnum
from app.domain.value_objects.money import Money


class UpdatePayrollHistoryOnTaskCompletionV2:
    """
    Caso de uso corregido segun los modelos SQLAlchemy reales.
    
    CORRECCION IMPORTANTE: Task.assigned_user_id en DB es firebase_uid (no document_number)
    Por lo tanto, necesitamos user_repo para obtener el document_number del user.
    
    NUEVA FUNCIONALIDAD: Crea una entrada en payroll_history_tasks para asociar
    la task con el historial de payroll (trazabilidad dinamica).
    """
    
    def __init__(
        self,
        task_repo: TaskRepository,
        payroll_history_repo: PayrollHistoryRepository,
        payroll_repo: PayrollRepository,
        user_repo: UserRepository,
        payroll_history_task_repo: PayrollHistoryTaskRepository
    ):
        self.task_repo = task_repo
        self.payroll_history_repo = payroll_history_repo
        self.payroll_repo = payroll_repo
        self.user_repo = user_repo
        self.payroll_history_task_repo = payroll_history_task_repo
    
    def execute(self, task_id: UUID) -> Optional[dict]:
        """
        Actualiza el PayrollHistory cuando una task es completada.
        
        Args:
            task_id: ID de la task completada
            
        Returns:
            Diccionario con information de la actualizacion o None si no aplica
        """
        print(f" [DEBUG] Iniciando actualizacion para task: {task_id}")
        
        # 1. Obtener la task
        task = self.task_repo.get_by_id(task_id)
        if not task:
            print(f"ERROR [DEBUG] Task no encontrada: {task_id}")
            return None
        
        if not task.assigned_user_id:
            print(f"ERROR [DEBUG] Task sin user asignado")
            return None
        
        print(f"OK [DEBUG] Task encontrada: {task.task_name}, assigned_user_id: {task.assigned_user_id}")
        
        # 2. Verificar que la task este en estado FINISHED usando la property
        if not task.is_finished:
            print(f"ERROR [DEBUG] Task no esta FINISHED, estado actual: {task.state}")
            return None
        
        print(f"OK [DEBUG] Task esta FINISHED")
        
        # 3. Verificar que la task tenga valor de mano de obra
        if not task.labor or task.labor.amount <= 0:
            print(f"ERROR [DEBUG] Task sin valor de mano de obra: {task.labor}")
            return None
        
        print(f"OK [DEBUG] Valor de mano de obra: {task.labor.amount} {task.labor.currency}")
        
        # 4. Obtener el user para sacar su identification_number
        user = self.user_repo.get_by_firebase_uid(task.assigned_user_id)
        if not user:
            print(f"ERROR [DEBUG] User no encontrado con firebase_uid: {task.assigned_user_id}")
            return None
        
        # El modelo de dominio User tiene identification_number (no document_number)
        identification_number = str(user.identification_number) if hasattr(user, 'identification_number') else None
        if not identification_number:
            print(f"ERROR [DEBUG] User sin identification_number")
            return None
        
        print(f"OK [DEBUG] User encontrado: {user.full_name if hasattr(user, 'full_name') else 'N/A'}, identification_number: {identification_number}")
        
        # 5. Search el PayrollHistory active del empleado
        latest_history = self.payroll_history_repo.get_latest_service_provision_history_by_employee(identification_number)  # type: ignore

        
        if not latest_history:
            print(f"ERROR [DEBUG] No hay PayrollHistory para el empleado: {identification_number}")
            return None

        print(f"OK [DEBUG] PayrollHistory encontrado: {latest_history.id}, payroll_id: {latest_history.payroll_id}")

        # 6. Verificar que el payroll asociado sea de tipo SERVICE_PROVISION
        payroll = self.payroll_repo.get_by_id(latest_history.payroll_id)
        if not payroll:
            print(f"ERROR [DEBUG] Payroll no encontrado: {latest_history.payroll_id}")
            return None
        
        print(f"OK [DEBUG] Payroll encontrado, contract_type: {payroll.contract_type}")
        
        # CRITICO: Solo actualizar si el contract es SERVICE_PROVISION
        # payroll.contract_type es un objeto ContractType, necesitamos acceder a su value
        contract_type_enum = payroll.contract_type.value if hasattr(payroll.contract_type, 'value') else payroll.contract_type
        if contract_type_enum != ContractTypeEnum.SERVICE_PROVISION:
            print(f"ERROR [DEBUG] Payroll NO es SERVICE_PROVISION, es: {contract_type_enum}")
            return None
        
        print(f"OK [DEBUG] Payroll es SERVICE_PROVISION")
        
        # 7. Sumar el valor de mano de obra
        current_amount = latest_history.works_value_amount.amount
        new_amount = current_amount + task.labor.amount
        
        print(f" [DEBUG] Actualizando: {current_amount} + {task.labor.amount} = {new_amount}")
        
        latest_history.works_value_amount = Money(
            amount=new_amount,
            currency=task.labor.currency
        )
        
        # 8. Save
        updated_history = self.payroll_history_repo.save(latest_history)
        
        print(f"OK [DEBUG] PayrollHistory actualizado exitosamente")
        
        # 9. NUEVO: Create entrada en payroll_history_tasks para trazabilidad
        try:
            association = PayrollHistoryTask(
                id=uuid.uuid4(),
                payroll_history_id=updated_history.id,  # type: ignore
                task_id=task_id,
                added_at=datetime.now(),
                added_by_user_id=task.assigned_user_id  # Firebase UID del user asignado
            )
            
            saved_association = self.payroll_history_task_repo.save(association)
            print(f"OK [DEBUG] Asociacion creada en payroll_history_tasks: {saved_association.id}")
        except Exception as e:
            print(f" [DEBUG] Error creando asociacion en payroll_history_tasks: {e}")
            import traceback
            traceback.print_exc()
            # No lanzamos la excepcion para no bloquear el flujo principal
        
        # 10. Retornar information de la actualizacion
        return {
            "task_id": str(task_id),
            "task_name": task.task_name,
            "payroll_history_id": str(updated_history.id),
            "payroll_id": str(payroll.id) if hasattr(payroll, 'id') else str(payroll.payroll_id),  # type: ignore
            "employee_identification": identification_number,
            "contract_type": str(contract_type_enum),
            "labor_cost_added": float(task.labor.amount),
            "previous_total": float(current_amount),
            "new_total": float(new_amount),
            "currency": task.labor.currency,
            "updated_at": datetime.now().isoformat()
        }