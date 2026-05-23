import React, { useState } from "react";
import {
  Button,
  Card,
  CardBody,
  Select,
  SelectItem,
  TableCell,
  TableRow,
} from "@heroui/react";
import {
  ArrowDown,
  ArrowUp,
  ChevronDown,
  ChevronRight,
  Package,
  Users,
} from "lucide-react";
import { Employee } from "@/services/employeeService";
import { TaskGroup } from "./TaskHierarchy";

interface TaskGroupRowProps {
  group: TaskGroup;
  groupIndex: number;
  totalGroups: number;
  isManagerOrSupervisor: boolean;
  isLoading: boolean;
  employees: Employee[];
  getStateLabel: (state: string) => string;
  getStateColor: (state: string) => { bg: string; color: string };
  getAssignedEmployeeName: (taskId: string) => string;
  onMoveGroup: (groupIndex: number, direction: "up" | "down") => Promise<void>;
  onMoveTaskWithinGroup: (
    groupIndex: number,
    taskIndex: number,
    direction: "up" | "down",
  ) => Promise<void>;
  onAssignTask: (taskId: string, employeeId: string) => Promise<void>;
}

export const TaskGroupRow: React.FC<TaskGroupRowProps> = ({
  group,
  groupIndex,
  totalGroups,
  isManagerOrSupervisor,
  isLoading,
  employees,
  getStateLabel,
  getStateColor,
  getAssignedEmployeeName,
  onMoveGroup,
  onMoveTaskWithinGroup,
  onAssignTask,
}) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [assigningTaskId, setAssigningTaskId] = useState<string | null>(null);
  const [selectedEmployeeId, setSelectedEmployeeId] = useState("");

  const activeEmployees = employees.filter((employee) => employee.state === "A");
  const sortedTasks = [...group.tasks].sort(
    (firstTask, secondTask) =>
      (firstTask.execution_order || 0) - (secondTask.execution_order || 0),
  );

  const handleAssignTask = async (taskId: string, employeeId: string) => {
    await onAssignTask(taskId, employeeId);
    setAssigningTaskId(null);
    setSelectedEmployeeId("");
  };

  const badgeColor = group.isComposite
    ? { bg: "bg-orange-100", border: "border-orange-300", text: "text-orange-700" }
    : {
        bg: "bg-surface-3",
        border: "border-surface-border",
        text: "text-surface-foreground",
      };

  return (
    <>
      <TableRow className={group.isComposite ? "bg-orange-50" : "bg-surface-1"}>
        <TableCell colSpan={6}>
          <div className="flex items-center gap-3 py-2">
            {group.tasks.length > 0 && (
              <button
                type="button"
                onClick={() => setIsExpanded(!isExpanded)}
                className="flex-shrink-0 rounded p-1 hover:bg-table-row-hover"
                title={isExpanded ? "Contraer" : "Expandir"}
              >
                {isExpanded ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                )}
              </button>
            )}

            <div className="flex-shrink-0">
              <Package
                className={`h-4 w-4 ${
                  group.isComposite ? "text-orange-600" : "text-secondary"
                }`}
              />
            </div>

            <div className="flex-grow">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-foreground">
                  {group.productName}
                </span>
                <span
                  className={`rounded-full border px-2 py-0.5 text-xs font-medium ${badgeColor.bg} ${badgeColor.border} ${badgeColor.text}`}
                >
                  {group.isComposite ? "Compuesto" : "Simple"}
                </span>
                <span className="text-xs text-surface-muted">
                  ({sortedTasks.length} tasks)
                </span>
              </div>
            </div>

            {isManagerOrSupervisor && (
              <div className="flex flex-shrink-0 items-center gap-1">
                <Button
                  isIconOnly
                  size="sm"
                  variant="light"
                  color="default"
                  isDisabled={groupIndex === 0 || isLoading}
                  onPress={() => onMoveGroup(groupIndex, "up")}
                  title="Mover grupo hacia arriba"
                >
                  <ArrowUp className="h-4 w-4" />
                </Button>
                <Button
                  isIconOnly
                  size="sm"
                  variant="light"
                  color="default"
                  isDisabled={groupIndex === totalGroups - 1 || isLoading}
                  onPress={() => onMoveGroup(groupIndex, "down")}
                  title="Mover grupo hacia abajo"
                >
                  <ArrowDown className="h-4 w-4" />
                </Button>
              </div>
            )}
          </div>
        </TableCell>
      </TableRow>

      {isExpanded &&
        sortedTasks.map((task, taskIndex) => {
          const stateColor = getStateColor(task.state);

          return (
            <TableRow
              key={`task-${task.task_id}`}
              className="bg-surface-2 hover:bg-table-row-hover"
            >
              <TableCell>
                <div className="flex items-center gap-2 pl-8">
                  <span className="text-xs text-surface-muted">|-</span>
                  <span className="text-sm font-semibold text-surface-muted">
                    {taskIndex + 1}
                  </span>
                </div>
              </TableCell>
              <TableCell>
                <p className="text-sm text-surface-muted">
                  {task.description || "-"}
                </p>
              </TableCell>
              <TableCell>
                <span
                  className="rounded-full px-2 py-1 text-xs font-medium"
                  style={{
                    backgroundColor: stateColor.bg,
                    color: stateColor.color,
                  }}
                >
                  {getStateLabel(task.state)}
                </span>
              </TableCell>
              <TableCell>
                <span className="text-sm font-semibold">
                  {task.estimated_value_formatted || "-"}
                </span>
              </TableCell>
              <TableCell>
                <span className="text-sm">
                  {getAssignedEmployeeName(task.task_id)}
                </span>
              </TableCell>
              <TableCell>
                <div className="flex items-center justify-center gap-1">
                  {isManagerOrSupervisor && group.isComposite ? (
                    <>
                      <Button
                        isIconOnly
                        size="sm"
                        variant="light"
                        color="default"
                        isDisabled={taskIndex === 0 || isLoading}
                        onPress={() =>
                          onMoveTaskWithinGroup(groupIndex, taskIndex, "up")
                        }
                        title="Mover task hacia arriba dentro del grupo"
                      >
                        <ArrowUp className="h-4 w-4" />
                      </Button>
                      <Button
                        isIconOnly
                        size="sm"
                        variant="light"
                        color="default"
                        isDisabled={
                          taskIndex === sortedTasks.length - 1 || isLoading
                        }
                        onPress={() =>
                          onMoveTaskWithinGroup(groupIndex, taskIndex, "down")
                        }
                        title="Mover task hacia abajo dentro del grupo"
                      >
                        <ArrowDown className="h-4 w-4" />
                      </Button>
                      <Button
                        isIconOnly
                        size="sm"
                        variant="light"
                        color="warning"
                        onPress={() => setAssigningTaskId(task.task_id)}
                        title="Asignar a empleado"
                      >
                        <Users className="h-4 w-4" />
                      </Button>
                    </>
                  ) : isManagerOrSupervisor ? (
                    <Button
                      isIconOnly
                      size="sm"
                      variant="light"
                      color="warning"
                      onPress={() => setAssigningTaskId(task.task_id)}
                      title="Asignar a empleado"
                    >
                      <Users className="h-4 w-4" />
                    </Button>
                  ) : (
                    <span className="text-xs text-surface-muted">-</span>
                  )}
                </div>
              </TableCell>
            </TableRow>
          );
        })}

      {assigningTaskId && (
        <TableRow className="bg-surface-elevated">
          <TableCell colSpan={6}>
            <Card className="m-2 border border-orange-200 bg-orange-50">
              <CardBody className="gap-3">
                <p className="text-sm font-semibold">Asignar task a empleado</p>
                <div className="flex gap-2">
                  <Select
                    label="Empleado (Actives)"
                    size="sm"
                    placeholder={
                      activeEmployees.length === 0
                        ? "No hay empleados activos disponibles"
                        : "Selecciona un empleado"
                    }
                    value={selectedEmployeeId}
                    onChange={(event: React.ChangeEvent<HTMLSelectElement>) =>
                      setSelectedEmployeeId(event.target.value)
                    }
                    aria-label="Seleccionar empleado para asignar task"
                    isDisabled={activeEmployees.length === 0}
                  >
                    {activeEmployees.map((employee) => (
                      <SelectItem
                        key={employee.firebase_uid}
                        value={employee.firebase_uid}
                        textValue={`${employee.first_name} ${employee.last_name}`}
                      >
                        {employee.first_name} {employee.last_name}
                      </SelectItem>
                    ))}
                  </Select>
                  <Button
                    size="sm"
                    color="warning"
                    isDisabled={!selectedEmployeeId || isLoading}
                    onPress={() =>
                      handleAssignTask(assigningTaskId, selectedEmployeeId)
                    }
                  >
                    Asignar
                  </Button>
                  <Button
                    size="sm"
                    variant="bordered"
                    onPress={() => {
                      setAssigningTaskId(null);
                      setSelectedEmployeeId("");
                    }}
                    isDisabled={isLoading}
                  >
                    Cancel
                  </Button>
                </div>
              </CardBody>
            </Card>
          </TableCell>
        </TableRow>
      )}
    </>
  );
};
