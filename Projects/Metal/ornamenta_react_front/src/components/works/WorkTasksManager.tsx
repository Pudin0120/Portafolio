import React, { useState, useEffect, useCallback } from "react";
import {
  Card,
  CardBody,
  CardHeader,
  Divider,
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Button,
  useDisclosure,
} from "@heroui/react";
import {
  ArrowUp,
  ArrowDown,
  Users,
  ChevronDown,
  ChevronRight,
  Package,
} from "lucide-react";
import { Work } from "@/types/works";
import { workService } from "@/services/workService";
import { taskService } from "@/services/taskService";
import { employeeService, Employee } from "@/services/employeeService";
import { useAuth } from "@/hooks/useAuth";
import { convertHierarchyToGroups, TaskGroup } from "./TaskHierarchy";
import { AssignTaskModal } from "./AssignTaskModal";

interface WorkTasksManagerProps {
  work: Work;
  onTasksUpdated?: (updatedWork: Work) => void;
}

export const WorkTasksManager: React.FC<WorkTasksManagerProps> = ({
  work,
  onTasksUpdated,
}) => {
  const { userRole } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());
  const [taskGroups, setTaskGroups] = useState<TaskGroup[]>([]);
  const [assigningTaskId, setAssigningTaskId] = useState<string | null>(null);
  const [assigningTaskName, setAssigningTaskName] = useState<string>("");
  const [isAssigning, setIsAssigning] = useState(false);

  const { isOpen, onOpen, onClose } = useDisclosure();

  const loadTasksHierarchy = useCallback(async () => {
    try {
      // Solo cargar jerarquia si el work tiene tasks (IN_PROGRESS o DELIVERED)
      if (work.state !== "IN_PROGRESS" && work.state !== "DELIVERED") {
        setTaskGroups([]);
        return;
      }

      const hierarchyResponse = await workService.getTasksHierarchy(
        work.work_id,
      );
      const groups = convertHierarchyToGroups(
        hierarchyResponse.composite_groups,
        work,
      );
      setTaskGroups(groups);

      // Expandir todos los grupos por defecto
      const allGroupIds = groups.map((g) => g.parentProductId);
      setExpandedGroups(new Set(allGroupIds));
    } catch (err) {
      console.error("Error al cargar jerarquia de tasks:", err);
      setTaskGroups([]);
    }
  }, [work]);

  const loadEmployees = useCallback(async () => {
    try {
      const emps = await employeeService.getEmployees();
      setEmployees(emps);
    } catch (err) {
      console.error("Error al cargar empleados:", err);
    }
  }, []);

  const isManagerOrSupervisor =
    userRole === "MANAGER" || userRole === "SUPERVISOR";

  useEffect(() => {
    if (isManagerOrSupervisor) {
      loadEmployees();
    }
  }, [isManagerOrSupervisor, loadEmployees]);

  // Expandir todos los grupos por defecto
  useEffect(() => {
    loadTasksHierarchy();
  }, [loadTasksHierarchy]);

  const getStateLabel = (state: string) => {
    switch (state) {
      case "PENDING":
        return "Pending";
      case "ASSIGNED":
        return "Asignada";
      case "READY":
        return "Por Iniciar";
      case "IN_PROGRESS":
        return "En Proceso";
      case "COMPLETED":
        return "Completada";
      case "FINISHED":
        return "Finalizada";
      default:
        return state;
    }
  };

  const getStateColor = (state: string) => {
    switch (state) {
      case "PENDING":
        return { bg: "#f5f5f5", color: "#666666" };
      case "ASSIGNED":
        return { bg: "#dbeafe", color: "#1e40af" };
      case "READY":
        return { bg: "#c7d2fe", color: "#3730a3" };
      case "IN_PROGRESS":
        return { bg: "#fef3c7", color: "#92400e" };
      case "COMPLETED":
        return { bg: "#d1fae5", color: "#065f46" };
      case "FINISHED":
        return { bg: "#fed7aa", color: "#9a3412" };
      default:
        return { bg: "#f0fdf4", color: "#166534" };
    }
  };

  const handleMoveGroup = async (
    groupIndex: number,
    direction: "up" | "down",
  ) => {
    const newIndex = direction === "up" ? groupIndex - 1 : groupIndex + 1;

    if (newIndex < 0 || newIndex >= taskGroups.length) return;

    try {
      setIsLoading(true);
      setError(null);

      const group1 = taskGroups[groupIndex];
      const group2 = taskGroups[newIndex];

      // OK IMPORTANT: Use the PRODUCTS endpoint to move groups
      // Cada grupo representa un product (compuesto o simple)
      // Los products simples tambien tienen un product_id en parentProductId

      // Encontrar los products correspondientes en work.products
      const product1 = work.products.find(
        (p) => p.product_id === group1.parentProductId,
      );
      const product2 = work.products.find(
        (p) => p.product_id === group2.parentProductId,
      );

      if (!product1 || !product2) {
        throw new Error("No se encontraron los products para reordenar");
      }

      // Swap the execution_order values of PRODUCTS (not tasks)
      const order1 = product1.execution_order;
      const order2 = product2.execution_order;

      // Use the PRODUCTS reorder endpoint
      // Esto funciona tanto para products compuestos como simples
      await Promise.all([
        workService.reorderProduct(work.work_id, product1.product_id, order2),
        workService.reorderProduct(work.work_id, product2.product_id, order1),
      ]);

      setSuccess("Orden de products actualizado exitosamente");

      // Recargar jerarquia
      await loadTasksHierarchy();

      // Notificar al padre
      const updatedWork = await workService.getWorkById(work.work_id);
      onTasksUpdated?.(updatedWork);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Error al reordenar product",
      );
    } finally {
      setIsLoading(false);
      setTimeout(() => {
        setSuccess(null);
        setError(null);
      }, 3000);
    }
  };

  const handleMoveTaskWithinGroup = async (
    groupIndex: number,
    taskIndex: number,
    direction: "up" | "down",
  ) => {
    const group = taskGroups[groupIndex];
    // Permitir reorden dentro de cualquier grupo (compuesto o simple)

    const sortedTasks = [...group.tasks].sort(
      (a, b) => (a.execution_order || 0) - (b.execution_order || 0),
    );
    const newTaskIndex = direction === "up" ? taskIndex - 1 : taskIndex + 1;

    if (newTaskIndex < 0 || newTaskIndex >= sortedTasks.length) return;

    try {
      setIsLoading(true);
      setError(null);

      const task1 = sortedTasks[taskIndex];
      const task2 = sortedTasks[newTaskIndex];

      // Intercambiar execution_order
      const newOrder1 = task2.execution_order || 0;
      const newOrder2 = task1.execution_order || 0;

      // Actualizar en servidor usando el endpoint correcto
      await Promise.all([
        taskService.reorderTask(work.work_id, task1.task_id, newOrder1),
        taskService.reorderTask(work.work_id, task2.task_id, newOrder2),
      ]);

      setSuccess("Orden de tasks actualizado exitosamente");

      // Recargar jerarquia
      await loadTasksHierarchy();

      // Notificar al padre
      const updatedWork = await workService.getWorkById(work.work_id);
      onTasksUpdated?.(updatedWork);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al reordenar task");
    } finally {
      setIsLoading(false);
      setTimeout(() => {
        setSuccess(null);
        setError(null);
      }, 3000);
    }
  };

  const handleAssignTask = async (employeeId: string) => {
    if (!assigningTaskId) return;

    try {
      setError(null);
      setIsAssigning(true);

      // Usar el nuevo metodo assignTask que usa POST /tasks/{id}/assign
      await taskService.assignTask(assigningTaskId, employeeId);

      setSuccess("Task assigned exitosamente");

      // Recargar jerarquia de tasks para reflejar el nuevo estado
      await loadTasksHierarchy();

      // Recargar work completo
      const updatedWork = await workService.getWorkById(work.work_id);
      onTasksUpdated?.(updatedWork);

      // Cerrar modal
      onClose();
      setAssigningTaskId(null);
      setAssigningTaskName("");
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Error al asignar task";
      setError(errorMessage);
    } finally {
      setIsAssigning(false);
      setTimeout(() => {
        setSuccess(null);
        setError(null);
      }, 3000);
    }
  };

  const getAssignedEmployeeName = (taskId: string): string => {
    const task = work.tasks?.find((t) => t.task_id === taskId);
    if (!task || !task.assigned_user_id) return "-";

    const employee = employees.find(
      (e) => e.firebase_uid === task.assigned_user_id,
    );
    return employee
      ? `${employee.first_name} ${employee.last_name}`
      : "User desconocido";
  };

  const openAssignModal = (taskId: string, taskName: string) => {
    setAssigningTaskId(taskId);
    setAssigningTaskName(taskName);
    onOpen();
  };

  const toggleGroupExpansion = (groupId: string) => {
    const newExpanded = new Set(expandedGroups);
    if (newExpanded.has(groupId)) {
      newExpanded.delete(groupId);
    } else {
      newExpanded.add(groupId);
    }
    setExpandedGroups(newExpanded);
  };

  const renderTableRows = () => {
    const rows: React.ReactElement[] = [];

    taskGroups.forEach((group, groupIndex) => {
      const isExpanded = expandedGroups.has(group.parentProductId);
      const sortedTasks = [...group.tasks].sort(
        (a, b) => (a.execution_order || 0) - (b.execution_order || 0),
      );

      const badgeColor = group.isComposite
        ? {
            bg: "bg-primary-100",
            border: "border-primary-300",
            text: "text-primary-700",
          }
        : {
            bg: "bg-surface-3",
            border: "border-surface-border",
            text: "text-surface-foreground",
          };

      // Fila del grupo (product)
      rows.push(
        <TableRow
          key={`group-${group.parentProductId}`}
          className={`${group.isComposite ? "bg-primary-50/50" : "bg-surface-1"}`}
        >
          <TableCell>
            <div className="flex items-center gap-3">
              {/* Mostrar chevron solo para products compuestos */}
              {group.isComposite && group.tasks.length > 0 && (
                <button
                  type="button"
                  onClick={() => toggleGroupExpansion(group.parentProductId)}
                  className="flex-shrink-0 rounded p-1 hover:bg-table-row-hover"
                  title={isExpanded ? "Contraer" : "Expandir"}
                >
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4" />
                  ) : (
                    <ChevronRight className="w-4 h-4" />
                  )}
                </button>
              )}
              {!group.isComposite && <div className="w-6" />}
              <div className="flex-shrink-0">
                <Package
                  className={`w-4 h-4 ${group.isComposite ? "text-primary" : "text-default-400"}`}
                />
              </div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-foreground">
                  {group.isComposite
                    ? group.productName
                    : sortedTasks.length > 0
                      ? sortedTasks[0].task_name
                      : group.productName}
                </span>
                <span
                  className={`px-2 py-0.5 text-xs font-medium rounded-full border ${badgeColor.bg} ${badgeColor.border} ${badgeColor.text}`}
                >
                  {group.isComposite ? "Compuesto" : "Simple"}
                </span>
                {group.isComposite && (
                  <span className="text-xs text-default-500">
                    ({sortedTasks.length} tasks)
                  </span>
                )}
              </div>
            </div>
          </TableCell>
          <TableCell>
            <span className="text-sm text-gray-600">{group.productType}</span>
          </TableCell>
          <TableCell>
            {/* Para products simples, mostrar el estado de la task */}
            {!group.isComposite && sortedTasks.length > 0 && (
              <span
                className="px-2 py-1 text-xs font-medium rounded"
                style={{
                  backgroundColor: getStateColor(sortedTasks[0].state).bg,
                  color: getStateColor(sortedTasks[0].state).color,
                }}
              >
                {getStateLabel(sortedTasks[0].state)}
              </span>
            )}
          </TableCell>
          <TableCell>
            {/* Para products simples, mostrar el valor estimado */}
            {!group.isComposite && sortedTasks.length > 0 && (
              <span className="text-sm font-medium">
                {sortedTasks[0].estimated_value_formatted}
              </span>
            )}
          </TableCell>
          <TableCell>
            {/* Para products simples, mostrar asignacion */}
            {!group.isComposite && sortedTasks.length > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-sm">
                  {getAssignedEmployeeName(sortedTasks[0].task_id)}
                </span>
                {isManagerOrSupervisor && (
                  <Button
                    size="sm"
                    variant="light"
                    isIconOnly
                    type="button"
                    onPress={() =>
                      openAssignModal(
                        sortedTasks[0].task_id,
                        sortedTasks[0].task_name,
                      )
                    }
                    title="Asignar empleado"
                  >
                    <Users className="w-4 h-4" />
                  </Button>
                )}
              </div>
            )}
          </TableCell>
          <TableCell>
            <div className="flex items-center justify-center gap-2">
              {isManagerOrSupervisor && (
                <>
                  <Button
                    size="sm"
                    isIconOnly
                    variant="light"
                    type="button"
                    onPress={() => handleMoveGroup(groupIndex, "up")}
                    isDisabled={groupIndex === 0 || isLoading}
                    title="Mover product arriba"
                  >
                    <ArrowUp className="w-4 h-4" />
                  </Button>
                  <Button
                    size="sm"
                    isIconOnly
                    variant="light"
                    type="button"
                    onPress={() => handleMoveGroup(groupIndex, "down")}
                    isDisabled={
                      groupIndex === taskGroups.length - 1 || isLoading
                    }
                    title="Mover product abajo"
                  >
                    <ArrowDown className="w-4 h-4" />
                  </Button>
                </>
              )}
            </div>
          </TableCell>
        </TableRow>,
      );

      // Filas de tasks internas (solo para products compuestos expandidos)
      if (group.isComposite && isExpanded) {
        sortedTasks.forEach((task, taskIndex) => {
          const stateColors = getStateColor(task.state);
          const assignedName = getAssignedEmployeeName(task.task_id);

          rows.push(
            <TableRow key={`task-${task.task_id}`} className="bg-surface-2">
              <TableCell>
                <div className="flex items-center gap-3 pl-12">
                  <span className="text-sm">
                    [{task.composite_task_slot || 0}/
                    {task.composite_total_slots || 0}] {task.task_name}
                  </span>
                </div>
              </TableCell>
              <TableCell>
                <span className="text-sm text-gray-600">
                  {task.description}
                </span>
              </TableCell>
              <TableCell>
                <span
                  className="px-2 py-1 text-xs font-medium rounded"
                  style={{
                    backgroundColor: stateColors.bg,
                    color: stateColors.color,
                  }}
                >
                  {getStateLabel(task.state)}
                </span>
              </TableCell>
              <TableCell>
                <span className="text-sm font-medium">
                  {task.estimated_value_formatted}
                </span>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <span className="text-sm">{assignedName}</span>
                  {isManagerOrSupervisor && (
                    <Button
                      size="sm"
                      variant="light"
                      isIconOnly
                      type="button"
                      onPress={() =>
                        openAssignModal(task.task_id, task.task_name)
                      }
                      title="Asignar empleado"
                    >
                      <Users className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center justify-center gap-2">
                  {isManagerOrSupervisor && (
                    <>
                      <Button
                        size="sm"
                        isIconOnly
                        variant="light"
                        type="button"
                        onPress={() =>
                          handleMoveTaskWithinGroup(groupIndex, taskIndex, "up")
                        }
                        isDisabled={taskIndex === 0 || isLoading}
                        title="Mover task arriba en el product"
                      >
                        <ArrowUp className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        isIconOnly
                        variant="light"
                        type="button"
                        onPress={() =>
                          handleMoveTaskWithinGroup(
                            groupIndex,
                            taskIndex,
                            "down",
                          )
                        }
                        isDisabled={
                          taskIndex === sortedTasks.length - 1 || isLoading
                        }
                        title="Mover task abajo en el product"
                      >
                        <ArrowDown className="w-4 h-4" />
                      </Button>
                    </>
                  )}
                </div>
              </TableCell>
            </TableRow>,
          );
        });
      }
    });

    return rows;
  };

  return (
    <Card className="border-1 border-default-200">
      <CardHeader className="flex flex-col items-start px-4 py-4 bg-primary-50/30">
        <div className="flex items-center gap-2 w-full">
          <h2 className="text-xl font-semibold">Gestionar Tasks</h2>
        </div>
        <p className="text-sm text-default-600 mt-1">
          {isManagerOrSupervisor
            ? "Reordena las tasks, cambia su orden de ejecucion y asigna a empleados"
            : "Visualiza las tasks del work y su orden de ejecucion"}
        </p>
      </CardHeader>
      <Divider />
      <CardBody className="gap-4 p-6">
        {error && (
          <div className="bg-danger-50 border border-danger-200 rounded-lg p-4">
            <p className="text-danger-600 text-sm">{error}</p>
          </div>
        )}

        {success && (
          <div className="bg-success-50 border border-success-200 rounded-lg p-4">
            <p className="text-success-600 text-sm">{success}</p>
          </div>
        )}

        {taskGroups && taskGroups.length > 0 ? (
          <>
            <div className="flex items-center justify-between">
              <p className="font-semibold text-lg text-foreground">
                Products y Tasks
              </p>
              <span className="text-sm text-default-500">
                {taskGroups.length} product{taskGroups.length !== 1 ? "s" : ""}{" "}
                ({work.tasks?.length || 0} task
                {work.tasks?.length !== 1 ? "s" : ""})
              </span>
            </div>

            <div className="overflow-x-auto">
              <Table aria-label="Tabla jerarquica de products y tasks">
                <TableHeader>
                  <TableColumn>PRODUCT / TASK</TableColumn>
                  <TableColumn>DESCRIPTION</TableColumn>
                  <TableColumn>ESTADO</TableColumn>
                  <TableColumn>VALOR ESTIMADO</TableColumn>
                  <TableColumn>ASIGNADO A</TableColumn>
                  <TableColumn className="text-center">ACCIONES</TableColumn>
                </TableHeader>
                <TableBody>{renderTableRows()}</TableBody>
              </Table>
            </div>

            {/* Resumen de totales */}
            <div className="mt-6 bg-gradient-to-r from-primary-50 to-primary-100/50 p-6 rounded-2xl border border-primary-200 shadow-sm">
              <div className="grid grid-cols-3 gap-8">
                <div>
                  <p className="text-xs text-primary-700 font-bold uppercase tracking-wider mb-2">
                    Total de Products
                  </p>
                  <p className="text-3xl font-black text-primary-900">
                    {taskGroups.length}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-primary-700 font-bold uppercase tracking-wider mb-2">
                    Products Compuestos
                  </p>
                  <p className="text-3xl font-black text-primary-900">
                    {taskGroups.filter((g) => g.isComposite).length}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-primary-700 font-bold uppercase tracking-wider mb-2">
                    Total de Tasks
                  </p>
                  <p className="text-3xl font-black text-primary-900">
                    {taskGroups.reduce((sum, g) => sum + g.tasks.length, 0)}
                  </p>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">
              No hay tasks asignadas a este work
            </p>
            <p className="text-sm text-gray-400">
              Las tasks se generaran automaticamente al iniciar el work
            </p>
          </div>
        )}
      </CardBody>

      {/* Modal de asignacion */}
      <AssignTaskModal
        isOpen={isOpen}
        onClose={onClose}
        onAssign={handleAssignTask}
        employees={employees}
        taskName={assigningTaskName}
        isLoading={isAssigning}
      />
    </Card>
  );
};

export default WorkTasksManager;
