import React, { useState, useEffect } from 'react';
import {
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  Divider,
  Input,
  Spinner,
} from '@heroui/react';
import { Task, UpdateTaskRequest } from '@/types/tasks';
import { taskService } from '@/services/taskService';
import { workService } from '@/services/workService';
import { useAuth } from '@/hooks/useAuth';
import { CenteredModal } from '@components/common/CenteredModal';

interface ViewTaskModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  task: Task | null;
  employeeName?: string;
  stateLabel?: string;
  stateColor?: { bg: string; color: string };
  onTaskUpdated?: () => void;
}

export const ViewTaskModal: React.FC<ViewTaskModalProps> = ({
  isOpen,
  onOpenChange,
  task,
  employeeName,
  stateLabel,
  stateColor,
  onTaskUpdated,
}) => {
  const { userRole, user } = useAuth();
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isEditingPrice, setIsEditingPrice] = useState(false);
  const [labor, setLabor] = useState<string>(task?.labor_amount ? parseFloat(task.labor_amount).toString() : task?.labor?.toString() || '0');
  const [isSavingPrice, setIsSavingPrice] = useState(false);
  const [workName, setWorkName] = useState<string>('');
  const [isLoadingWorkName, setIsLoadingWorkName] = useState(false);

  // Update labor when task changes
  useEffect(() => {
    if (task) {
      const laborValue = task.labor_amount 
        ? parseFloat(task.labor_amount).toString() 
        : task.labor?.toString() || '0';
      setLabor(laborValue);
    }
  }, [task?.task_id, task?.labor_amount, task?.labor]);

  // Load work name when modal opens or task changes
  useEffect(() => {
    if (isOpen && task?.work_id) {
      loadWorkName();
    }
  }, [isOpen, task?.work_id]);

  const loadWorkName = async () => {
    if (!task?.work_id) return;
    try {
      setIsLoadingWorkName(true);
      const work = await workService.getWorkById(task.work_id);
      setWorkName(work.work_name || '');
    } catch (err) {
      console.error('Error al cargar el nombre del work:', err);
    } finally {
      setIsLoadingWorkName(false);
    }
  };

  // Clean leading zeros from input
  const cleanLeadingZeros = (value: string): string => {
    if (!value) return '';
    // Remove leading zeros but keep at least one digit
    const cleaned = value.replace(/^0+/, '');
    return cleaned === '' || cleaned === '.' ? '0' : cleaned;
  };

  const handleLaborChange = (value: string) => {
    setLabor(cleanLeadingZeros(value));
  };

  const handleStartEditingPrice = () => {
    // Asegurar que el valor este limpio antes de edit
    // Si task.labor_amount o task.labor vienen formateados, limpiarlos
    if (task) {
      const rawValue = task.labor_amount || task.labor?.toString() || '0';
      // Limpiar formato: delete todo excepto digitos y punto decimal
      const cleanValue = String(rawValue)
        .replace(/[^\d,.-]/g, '')  // Delete simbolos de moneda y espacios
        .replace(/\./g, '')        // Delete puntos (separadores de miles)
        .replace(',', '.');         // Convertir coma decimal a punto
      
      const parsed = parseFloat(cleanValue);
      const finalValue = isNaN(parsed) ? '0' : parsed.toString();
      
      console.log(' handleStartEditingPrice - Limpieza de valor:');
      console.log('  - Valor original:', rawValue);
      console.log('  - Valor limpio:', cleanValue);
      console.log('  - Valor final:', finalValue);
      
      setLabor(finalValue);
    }
    setIsEditingPrice(true);
  };

  if (!task) return null;

  // Determine if current user is a manager or supervisor
  const isManager = userRole === 'MANAGER';
  const isSupervisor = userRole === 'SUPERVISOR';
  const isEmployee = userRole === 'EMPLOYEE';
  const currentUserId = user?.uid;
  const isTaskAssignedToCurrentUser = task.assigned_user_id === currentUserId;

  const handleStartTask = async () => {
    try {
      setIsStarting(true);
      setError(null);

      await taskService.updateTaskState(task.task_id, 'IN_PROGRESS');

      if (onTaskUpdated) {
        onTaskUpdated();
      }

      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al iniciar la task');
    } finally {
      setIsStarting(false);
    }
  };

  const canStartTask = task.state === 'READY' && isTaskAssignedToCurrentUser;
  const canCompleteTask = task.state === 'IN_PROGRESS' && isTaskAssignedToCurrentUser;

  const handleCompleteTask = async () => {
    try {
      setIsStarting(true);
      setError(null);

      await taskService.updateTaskState(task.task_id, 'COMPLETED');

      if (onTaskUpdated) {
        onTaskUpdated();
      }

      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al marcar la task como completada');
    } finally {
      setIsStarting(false);
    }
  };

  // Validation logic
  const canValidateTask = isManager || isSupervisor;
  const canValidateDirectlyToFinished = isManager;
  const canRejectTask = isManager || isSupervisor;

  // Manager can validate any task in COMPLETED or IN_PROGRESS state
  // Supervisor can validate tasks from other users only (not their own)
  const canShowValidationButtons = () => {
    if (task.state === 'COMPLETED') {
      if (isManager) return true;
      if (isSupervisor && !isTaskAssignedToCurrentUser) return true;
    }
    if (task.state === 'IN_PROGRESS' && isManager) return true;
    return false;
  };

  // Show reject button only when task is COMPLETED
  const canShowRejectButton = () => {
    if (task.state === 'COMPLETED') {
      if (isManager) return true;
      if (isSupervisor && !isTaskAssignedToCurrentUser) return true;
    }
    return false;
  };

  const handleValidateTask = async () => {
    try {
      setIsStarting(true);
      setError(null);

      // Manager can validate directly from IN_PROGRESS to FINISHED
      // Supervisor can only validate COMPLETED to FINISHED
      const newState = isManager && task.state === 'IN_PROGRESS' ? 'FINISHED' : 'FINISHED';
      await taskService.updateTaskState(task.task_id, newState);

      if (onTaskUpdated) {
        onTaskUpdated();
      }

      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al validar la task');
    } finally {
      setIsStarting(false);
    }
  };

  const handleRejectTask = async () => {
    try {
      setIsStarting(true);
      setError(null);

      // Return task to IN_PROGRESS if it was COMPLETED
      await taskService.updateTaskState(task.task_id, 'IN_PROGRESS');

      if (onTaskUpdated) {
        onTaskUpdated();
      }

      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al rechazar la validacion');
    } finally {
      setIsStarting(false);
    }
  };

  const handleSavePrice = async () => {
    try {
      setIsSavingPrice(true);
      setError(null);

      console.log(' [ViewTaskModal] handleSavePrice - Iniciando actualizacion');
      console.log(' [ViewTaskModal] Task actual:', {
        task_id: task.task_id,
        task_name: task.task_name,
        description: task.description,
        labor_amount_actual: task.labor_amount,
        estimated_value_actual: task.estimated_value,
      });
      console.log(' [ViewTaskModal] Labor ingresada (string):', labor);

      // Parse labor_amount from input (string -> number)
      const parsedLabor = parseFloat(labor);
      const finalLaborAmount = isNaN(parsedLabor) ? 0 : parsedLabor;
      console.log(' [ViewTaskModal] Labor parseada:', finalLaborAmount);

      // Build payload with only the field we want to update
      const updatePayload: UpdateTaskRequest = {
        labor_amount: finalLaborAmount
      };

      console.log(' [ViewTaskModal] Payload completo a enviar:', updatePayload);

      await taskService.updateTask(task.task_id, updatePayload);

      console.log('OK [ViewTaskModal] Actualizacion exitosa');

      // Primero cerramos el modo de edicion
      setIsEditingPrice(false);
      
      // Pequeno delay para que la UI se actualice
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Cerrar la modal
      onOpenChange(false);
      
      // Luego actualizamos la lista (despues de que la modal se cierre)
      if (onTaskUpdated) {
        setTimeout(() => {
          onTaskUpdated();
        }, 300); // Delay para asegurar que la modal este cerrada
      }
    } catch (err) {
      console.error('ERROR [ViewTaskModal] Error al save la mano de obra:', err);
      setError(err instanceof Error ? err.message : 'Error al save la mano de obra');
    } finally {
      setIsSavingPrice(false);
    }
  };

  return (
    <CenteredModal isOpen={isOpen} onOpenChange={onOpenChange} size="lg">
      {(onClose: () => void) => (
        <>
          <ModalHeader className="flex flex-col gap-1">
            <h2 className="text-xl font-semibold">{task.task_name}</h2>
              {isLoadingWorkName ? (
                <p className="text-sm text-gray-600">
                  <Spinner size="sm" color="warning" /> Cargando work...
                </p>
              ) : (
                workName && (
                  <p className="text-sm text-gray-600">Work: <span className="font-medium text-gray-900">{workName}</span></p>
                )
              )}
              {employeeName && (
                <p className="text-sm text-gray-600">Asignado a: <span className="font-medium text-gray-900">{employeeName}</span></p>
              )}
            </ModalHeader>
            <Divider />
            <ModalBody>
              <div className={isEditingPrice ? "space-y-4" : "space-y-6"}>
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <p className="text-red-600 text-sm">{error}</p>
                  </div>
                )}

                {/* Estado */}
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-2">Estado</p>
                  {stateColor && (
                    <span
                      className="px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap inline-block"
                      style={{
                        backgroundColor: stateColor.bg,
                        color: stateColor.color,
                      }}
                    >
                      {stateLabel}
                    </span>
                  )}
                </div>

                {/* ...existing code... */}

                {/* Description */}
                {task.description && (
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-2">Description</p>
                    <p className="text-gray-900">{task.description}</p>
                  </div>
                )}

                {/* Precios en modo edicion - Layout mejorado */}
                {isManager && isEditingPrice && (
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 space-y-4">
                    <h3 className="font-semibold text-gray-900">Edit mano de obra</h3>
                    
                    <div>
                      <label className="text-sm font-medium text-gray-600 mb-2 block">Mano de obra</label>
                      <Input
                        type="number"
                        value={labor}
                        onValueChange={handleLaborChange}
                        placeholder="0.00"
                        startContent={<span className="text-gray-600">$</span>}
                        step="0.01"
                        min="0"
                        size="lg"
                      />
                    </div>
                  </div>
                )}

                {/* Precios en modo vista */}
                {isManager && !isEditingPrice && (
                  <>
                    {/* Mano de obra */}
                    <div>
                      <p className="text-sm font-medium text-gray-600 mb-2">Mano de obra</p>
                      <p className="text-gray-900">{task.labor_formatted || `$${parseFloat(task.labor?.toString() || '0').toFixed(2)}`}</p>
                    </div>

                    {/* Valor de la task */}
                    <div>
                      <p className="text-sm font-medium text-gray-600 mb-2">Valor de la task</p>
                      <p className="text-gray-900">{task.estimated_value_formatted || `$${parseFloat(task.estimated_value?.toString() || '0').toFixed(2)}`}</p>
                    </div>
                  </>
                )}

                {/* Bloqueado */}
                {task.is_blocked && (
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-2">Estado</p>
                    <p className="text-orange-600 font-medium"> Bloqueada por task anterior</p>
                  </div>
                )}

                {/* Requiere validacion */}
                {task.requires_validation && (
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-2">Validacion</p>
                    <p className="text-blue-600"> Requiere validacion</p>
                  </div>
                )}
              </div>
            </ModalBody>
            <Divider />
            <ModalFooter>
              {isManager && !isEditingPrice && (
                <Button
                  color="default"
                  variant="flat"
                  onPress={handleStartEditingPrice}
                >
                  Edit mano de obra
                </Button>
              )}
              
              {isManager && isEditingPrice && (
                <>
                  <Button
                    color="default"
                    variant="light"
                    onPress={() => setIsEditingPrice(false)}
                    disabled={isSavingPrice}
                  >
                    Cancel
                  </Button>
                  <Button
                    color="warning"
                    isLoading={isSavingPrice}
                    onPress={handleSavePrice}
                    disabled={isSavingPrice}
                  >
                    Save precios
                  </Button>
                </>
              )}

              {canStartTask && (
                <Button
                  color="warning"
                  isLoading={isStarting}
                  onPress={handleStartTask}
                  disabled={isStarting || isEditingPrice}
                >
                  Iniciar task
                </Button>
              )}
              {canCompleteTask && (
                <Button
                  color="warning"
                  isLoading={isStarting}
                  onPress={handleCompleteTask}
                  disabled={isStarting || isEditingPrice}
                >
                  Marcar como completada
                </Button>
              )}
              {canShowValidationButtons() && (
                <>
                  <Button
                    color="warning"
                    isLoading={isStarting}
                    onPress={handleValidateTask}
                    disabled={isStarting || isEditingPrice}
                  >
                    {isManager && task.state === 'IN_PROGRESS' ? 'Finalizar task' : 'Validar task'}
                  </Button>
                  {canShowRejectButton() && (
                    <Button
                      color="danger"
                      variant="bordered"
                      isLoading={isStarting}
                      onPress={handleRejectTask}
                      disabled={isStarting || isEditingPrice}
                    >
                      No validar
                    </Button>
                  )}
                </>
              )}
            </ModalFooter>
          </>
        )}
      </CenteredModal>
  );
};
