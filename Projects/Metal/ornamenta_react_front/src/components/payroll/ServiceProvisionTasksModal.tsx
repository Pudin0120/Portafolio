import React, { useEffect, useState, useCallback } from "react";
import {
  FileText,
  Calendar,
  DollarSign,
  Briefcase,
  Info,
  Edit2,
  Check,
  X,
} from "lucide-react";
import {
  ModalHeader,
  ModalBody,
  ModalFooter,
  Input,
  Button,
  Spinner,
} from "@heroui/react";
import { CenteredModal } from "@/components/common/CenteredModal";
import { payrollService } from "@/services/payrollService";
import { taskService } from "@/services/taskService";
import { workService } from "@/services/workService";
import { employeeService } from "@/services/employeeService";
import {
  ServiceProvisionTasksDetail,
  TaskSummaryItem,
} from "@/types/payroll-tasks";
import { Payroll, StatePayroll } from "@/types/payroll";
import { Task, UpdateTaskRequest } from "@/types/tasks";
import { useAuth } from "@/hooks/useAuth";

interface TaskWithWork extends Task {
  work_name?: string;
}

interface ServiceProvisionTasksModalProps {
  payroll: Payroll;
  isOpen: boolean;
  onClose: () => void;
}

export const ServiceProvisionTasksModal: React.FC<
  ServiceProvisionTasksModalProps
> = ({ payroll, isOpen, onClose }) => {
  const { userRole } = useAuth();
  const [tasksDetail, setTasksDetail] =
    useState<ServiceProvisionTasksDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editingTaskName, setEditingTaskName] = useState<string | null>(null);
  const [editingLabor, setEditingLabor] = useState<string>("");
  const [isSavingLabor, setIsSavingLabor] = useState(false);
  const [tasksWithWork, setTasksWithWork] = useState<
    Map<string, TaskWithWork[]>
  >(new Map());
  const [employeeFirebaseUid, setEmployeeFirebaseUid] = useState<string>("");

  const isManager = userRole === "MANAGER";
  const canEditLabor = isManager && payroll.state === StatePayroll.ACTIVE;

  const loadEmployeeData = useCallback(async () => {
    try {
      const employees = await employeeService.getEmployees();
      const employee = employees.find(
        (emp) => emp.identification_number === payroll.identification_number,
      );

      if (!employee) {
        return "";
      }

      setEmployeeFirebaseUid(employee.firebase_uid);
      return employee.firebase_uid;
    } catch {
      return "";
    }
  }, [payroll.identification_number]);

  const loadIndividualTasks = useCallback(
    async (detail: ServiceProvisionTasksDetail, firebaseUid: string) => {
      try {
        const response = await taskService.getTasksByUserId(firebaseUid, {});
        const taskNamesInSummary = new Set(
          detail.tasks_summary.map((t) => t.task_name),
        );
        const tasksMap = new Map<string, TaskWithWork[]>();

        for (const task of response.tasks) {
          if (!taskNamesInSummary.has(task.task_name)) {
            continue;
          }

          try {
            const work = await workService.getWorkById(task.work_id);
            const taskWithWork: TaskWithWork = {
              ...task,
              work_name: work.work_name,
            };

            const existingTasks = tasksMap.get(task.task_name) || [];
            existingTasks.push(taskWithWork);
            tasksMap.set(task.task_name, existingTasks);
          } catch {
            // Si un work no carga, mantenemos la task sin nombre de obra.
          }
        }

        setTasksWithWork(tasksMap);
        return tasksMap;
      } catch {
        return new Map<string, TaskWithWork[]>();
      }
    },
    [],
  );

  const recalculateTasksSummary = useCallback(
    (
      detail: ServiceProvisionTasksDetail,
      tasksMap: Map<string, TaskWithWork[]>,
    ): ServiceProvisionTasksDetail => {
      if (tasksMap.size === 0) {
        return detail;
      }

      const updatedSummary = detail.tasks_summary.map(
        (summaryItem: TaskSummaryItem) => {
          const individualTasks = tasksMap.get(summaryItem.task_name);

          if (!individualTasks || individualTasks.length === 0) {
            return summaryItem;
          }

          const laborPerTask = parseFloat(
            individualTasks[0].labor_amount || "0",
          );
          const taskCount = individualTasks.length;
          const totalCost = laborPerTask * taskCount;

          return {
            ...summaryItem,
            task_count: taskCount,
            labor_cost_per_task: laborPerTask.toFixed(2),
            labor_cost_per_task_formatted: new Intl.NumberFormat("es-CO", {
              style: "currency",
              currency: "COP",
              minimumFractionDigits: 2,
            }).format(laborPerTask),
            total_labor_cost: totalCost.toFixed(2),
            total_labor_cost_formatted: new Intl.NumberFormat("es-CO", {
              style: "currency",
              currency: "COP",
              minimumFractionDigits: 2,
            }).format(totalCost),
          };
        },
      );

      const newTotalCost = updatedSummary.reduce((sum, item) => {
        return sum + parseFloat(item.total_labor_cost);
      }, 0);

      return {
        ...detail,
        tasks_summary: updatedSummary,
        total_labor_cost: newTotalCost.toFixed(2),
        total_labor_cost_formatted: new Intl.NumberFormat("es-CO", {
          style: "currency",
          currency: "COP",
          minimumFractionDigits: 2,
        }).format(newTotalCost),
      };
    },
    [],
  );

  const loadTasksDetail = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const uid = employeeFirebaseUid || (await loadEmployeeData());
      const detail = await payrollService.getServiceProvisionTasks(
        payroll.payroll_id,
      );

      if (uid) {
        const tasksMap = await loadIndividualTasks(detail, uid);
        const recalculatedDetail = recalculateTasksSummary(detail, tasksMap);
        setTasksDetail(recalculatedDetail);
      } else {
        setTasksDetail(detail);
      }
    } catch {
      setError(
        "No se pudo cargar el detalle de las tasks. Please, intenta nuevamente.",
      );
    } finally {
      setIsLoading(false);
    }
  }, [
    payroll.payroll_id,
    employeeFirebaseUid,
    loadEmployeeData,
    loadIndividualTasks,
    recalculateTasksSummary,
  ]);

  useEffect(() => {
    if (isOpen && payroll.is_service_provision) {
      loadTasksDetail();
    }
  }, [isOpen, payroll.is_service_provision, loadTasksDetail]);

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString("es-CO", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const cleanLeadingZeros = (value: string): string => {
    if (!value) return "";
    const cleaned = value.replace(/^0+/, "");
    return cleaned === "" || cleaned === "." ? "0" : cleaned;
  };

  const handleEditTaskLabor = (taskName: string, currentLabor: string) => {
    setEditingTaskName(taskName);
    let numericValue = (currentLabor || "0")
      .replace(/[^\d,.-]/g, "")
      .replace(/\./g, "")
      .replace(",", ".");

    setEditingLabor(cleanLeadingZeros(numericValue));
  };

  const handleCancelEdit = () => {
    setEditingTaskName(null);
    setEditingLabor("");
  };

  const handleSaveLabor = async (taskName: string) => {
    try {
      setIsSavingLabor(true);
      setError(null);

      const tasksToUpdate = tasksWithWork.get(taskName);

      if (!tasksToUpdate || tasksToUpdate.length === 0) {
        throw new Error("No se encontraron tasks para actualizar");
      }

      const newLabor = parseFloat(editingLabor);
      if (isNaN(newLabor) || newLabor < 0) {
        throw new Error(
          "El valor de la mano de obra debe ser un number valid mayor o igual a 0",
        );
      }

      for (const task of tasksToUpdate) {
        const updatePayload: UpdateTaskRequest = {
          labor_amount: newLabor,
        };

        await taskService.updateTask(task.task_id, updatePayload);
      }

      setEditingTaskName(null);
      setEditingLabor("");

      await new Promise((resolve) => setTimeout(resolve, 500));
      await loadTasksDetail();

      setIsSavingLabor(false);
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : "No se pudo actualizar la mano de obra. Please, intenta nuevamente.";
      setError(errorMessage);
      setIsSavingLabor(false);
    }
  };

  if (!isOpen) return null;

  return (
    <CenteredModal
      isOpen={isOpen}
      onOpenChange={(open: boolean) => !open && onClose()}
      size="2xl"
      scrollBehavior="inside"
    >
      {() => (
        <>
          <ModalHeader className="bg-primary text-white flex items-center gap-3">
            <Briefcase className="w-6 h-6" />
            <span className="text-xl font-bold">
              Detalle de Tasks Realizadas
            </span>
          </ModalHeader>

          <ModalBody className="py-6">
            {isLoading && (
              <div className="flex items-center justify-center py-12">
                <Spinner size="lg" color="primary" />
              </div>
            )}

            {error && (
              <div className="bg-danger-50 border border-danger-200 rounded-lg p-4 flex items-start gap-3">
                <Info className="w-5 h-5 text-danger flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-danger-800">Error</p>
                  <p className="text-sm text-danger-600 mt-1">{error}</p>
                </div>
              </div>
            )}

            {!isLoading && !error && tasksDetail && (
              <div className="space-y-6">
                <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-5 h-5 text-primary" />
                      <div>
                        <p className="text-xs font-medium text-default-600">
                          Periodo
                        </p>
                        <p className="text-sm font-bold text-default-900">
                          {formatDate(tasksDetail.period_start_date)} -{" "}
                          {formatDate(tasksDetail.period_end_date)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <FileText className="w-5 h-5 text-primary" />
                      <div>
                        <p className="text-xs font-medium text-default-600">
                          Total de Tasks
                        </p>
                        <p className="text-sm font-bold text-default-900">
                          {tasksDetail.total_tasks_count}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <DollarSign className="w-5 h-5 text-primary" />
                      <div>
                        <p className="text-xs font-medium text-default-600">
                          Total a Pagar
                        </p>
                        <p className="text-sm font-bold text-primary-700">
                          {tasksDetail.total_labor_cost_formatted}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-warning-50 border border-warning-200 rounded-lg p-4 flex items-start gap-3">
                  <Info className="w-5 h-5 text-warning flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-warning-900">
                      Este pago corresponde a las tasks completadas durante el
                      periodo
                    </p>
                    <p className="text-xs text-warning-700 mt-1">
                      Cada task muestra el nombre, quantity realizada y el
                      costo de mano de obra asociado.
                    </p>
                    {isManager && !canEditLabor && (
                      <p className="text-xs text-warning-700 mt-2 font-medium">
                         Solo puedes edit la mano de obra cuando la payroll
                        esta en estado ACTIVA
                      </p>
                    )}
                  </div>
                </div>

                <div className="space-y-3">
                  <h3 className="text-lg font-bold text-default-900 mb-4">
                    Resumen de Tasks
                  </h3>

                  {tasksDetail.tasks_summary.length === 0 ? (
                    <div className="text-center py-8 bg-default-50 rounded-lg">
                      <FileText className="w-12 h-12 text-default-400 mx-auto mb-2" />
                      <p className="text-default-600">
                        No hay tasks registradas para este periodo
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {tasksDetail.tasks_summary.map(
                        (task: TaskSummaryItem, index: number) => (
                          <div
                            key={`task-${task.task_name}-${index}`}
                            className="border border-divider rounded-lg p-4 hover:shadow-sm transition-shadow"
                          >
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex-1">
                                <h4 className="font-semibold text-default-900 mb-2">
                                  {task.task_name}
                                </h4>

                                {tasksWithWork.get(task.task_name) &&
                                  tasksWithWork.get(task.task_name)!.length >
                                    0 && (
                                    <div className="mb-2">
                                      <p className="text-xs text-default-500">
                                        Work(s):{" "}
                                        <span className="font-medium text-default-700">
                                          {Array.from(
                                            new Set(
                                              tasksWithWork
                                                .get(task.task_name)!
                                                .map((t) => t.work_name),
                                            ),
                                          ).join(", ")}
                                        </span>
                                      </p>
                                    </div>
                                  )}

                                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                                  <div>
                                    <span className="text-default-600">
                                      Quantity:
                                    </span>
                                    <span className="ml-2 font-medium text-default-900">
                                      {task.task_count}
                                    </span>
                                  </div>
                                  <div>
                                    <span className="text-default-600">
                                      Costo por task:
                                    </span>
                                    <span className="ml-2 font-medium text-default-900">
                                      {task.labor_cost_per_task_formatted}
                                    </span>
                                  </div>
                                  <div>
                                    <span className="text-default-600">
                                      Total:
                                    </span>
                                    <span className="ml-2 font-bold text-primary-700">
                                      {task.total_labor_cost_formatted}
                                    </span>
                                  </div>
                                </div>
                              </div>

                              {canEditLabor && (
                                <div className="relative">
                                  {editingTaskName === task.task_name ? (
                                    <div className="flex items-center gap-2">
                                      <Input
                                        type="text"
                                        value={editingLabor}
                                        onValueChange={(value: string) =>
                                          setEditingLabor(
                                            cleanLeadingZeros(value),
                                          )
                                        }
                                        className="w-24 text-right"
                                        placeholder="0"
                                        aria-label="Edit labor"
                                      />
                                      <Button
                                        onPress={() =>
                                          handleSaveLabor(task.task_name)
                                        }
                                        color="primary"
                                        isDisabled={isSavingLabor}
                                        isIconOnly
                                        size="sm"
                                      >
                                        {isSavingLabor ? (
                                          <Spinner size="sm" />
                                        ) : (
                                          <Check className="w-4 h-4" />
                                        )}
                                      </Button>
                                      <Button
                                        onPress={handleCancelEdit}
                                        variant="flat"
                                        isIconOnly
                                        size="sm"
                                      >
                                        <X className="w-4 h-4" />
                                      </Button>
                                    </div>
                                  ) : (
                                    <Button
                                      onPress={() =>
                                        handleEditTaskLabor(
                                          task.task_name,
                                          task.labor_cost_per_task_formatted,
                                        )
                                      }
                                      color="primary"
                                      variant="flat"
                                      size="sm"
                                      startContent={
                                        <Edit2 className="w-4 h-4" />
                                      }
                                    >
                                      Edit Mano de Obra
                                    </Button>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>
                        ),
                      )}
                    </div>
                  )}
                </div>

                {tasksDetail.tasks_summary.length > 0 && (
                  <div className="border-t border-divider pt-4 mt-6">
                    <div className="flex items-center justify-between bg-primary-100 rounded-lg p-4">
                      <span className="text-lg font-bold text-default-900">
                        Total del Periodo
                      </span>
                      <span className="text-2xl font-bold text-primary-700">
                        {tasksDetail.total_labor_cost_formatted}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </ModalBody>

          <ModalFooter className="bg-default-50 border-t border-divider">
            <Button
              onPress={onClose}
              color="primary"
              variant="solid"
              className="font-medium"
            >
              Cerrar
            </Button>
          </ModalFooter>
        </>
      )}
    </CenteredModal>
  );
};
