import React, { useEffect, useState } from "react";
import {
  Alert,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableColumn,
  TableHeader,
  TableRow,
  Tooltip,
} from "@heroui/react";
import { Plus, Pencil, ToggleLeft, ToggleRight } from "lucide-react";
import { CreateEmployeeModal } from "./CreateEmployeeModal";
import { ApiError } from "../../services/apiClient";
import { employeeService, type Employee } from "../../services/employeeService";
import { useAuth } from "@hooks/useAuth";
import { translateError } from "../../utils/errorHandling";
import { useConnectivity } from "@/providers/ConnectivityProvider";

interface EmployeesManagerProps {
  onSubTabChange?: (tab: string) => void;
  onModalOpen?: () => void;
}

export const EmployeesManager: React.FC<EmployeesManagerProps> = ({
  onSubTabChange,
  onModalOpen,
}) => {
  const { user } = useAuth();
  const { isOnline, syncing } = useConnectivity();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(true);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [message, setMessage] = useState<string>("");
  const [error, setError] = useState<string>("");

  const fetchEmployees = React.useCallback(async (forceRefresh = false) => {
    try {
      const data = await employeeService.getEmployees({ forceRefresh });
      setEmployees(data || []);
    } catch {
      setError("Error al cargar empleados");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // Si estamos online y sincronizando cambios pendientes en background, esperamos a que termine
    // para evitar condiciones de carrera y traer datos desactualizados del servidor.
    if (isOnline && syncing) {
      return;
    }

    const timeoutId = window.setTimeout(() => {
      void fetchEmployees();
    }, 0);

    return () => window.clearTimeout(timeoutId);
  }, [fetchEmployees, isOnline, syncing]);

  const handleCreateEmployee = () => {
    setIsModalOpen(true);
    if (onSubTabChange) onSubTabChange("Create Employee");
    if (onModalOpen) onModalOpen();
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setMessage("");
    setError("");
    if (onSubTabChange) onSubTabChange("");
  };

  const handleCloseEditModal = () => {
    setIsEditModalOpen(false);
    setSelectedEmployee(null);
    setMessage("");
    setError("");
    if (onSubTabChange) onSubTabChange("");
  };

  const handleSaveEmployee = async (data: unknown) => {
    try {
      const employee = data as Partial<Employee>;
      setMessage(
        `Empleado ${employee.first_name ?? ""} ${employee.last_name ?? ""} creado exitosamente`,
      );
      
      const isOnlineMode = typeof navigator !== "undefined" ? navigator.onLine : true;
      if (isOnlineMode) {
        employeeService.invalidateEmployeesCache();
        await fetchEmployees(true);
      } else if (employee.identification_number) {
        const { addEmployee } = await import("@/services/indexedDb/employeeDb");
        await addEmployee({
          id: employee.identification_number,
          identification_number: employee.identification_number,
          first_name: employee.first_name || "",
          last_name: employee.last_name || "",
          email: employee.email || "",
          role: employee.role || "",
          documentType: employee.document_type || "CC",
          isActive: employee.state === "A",
          createdAt: Date.now(),
          updatedAt: Date.now(),
          phone: employee.phone || "",
          firebase_uid: employee.firebase_uid || "",
        });
        setEmployees((prev) => {
          const filtered = prev.filter(
            (current) => current.identification_number !== employee.identification_number,
          );
          return [employee as Employee, ...filtered];
        });
      }
      handleCloseModal();
    } catch (error: unknown) {
      const msg =
        error instanceof ApiError
          ? translateError(error.message)
          : error instanceof Error
            ? error.message
            : "Error al create empleado";
      setError(msg);
    }
  };

  const handleUpdateEmployee = async (data: unknown) => {
    try {
      const employee = data as Partial<Employee>;
      setMessage(
        `Empleado ${employee.first_name ?? ""} ${employee.last_name ?? ""} actualizado exitosamente`,
      );
      
      const isOnlineMode = typeof navigator !== "undefined" ? navigator.onLine : true;
      if (isOnlineMode) {
        employeeService.invalidateEmployeesCache();
        await fetchEmployees(true);
      } else if (employee.identification_number) {
        const { updateEmployee } = await import("@/services/indexedDb/employeeDb");
        await updateEmployee(employee.identification_number, {
          first_name: employee.first_name,
          last_name: employee.last_name,
          email: employee.email,
          role: employee.role,
          documentType: employee.document_type,
          isActive: employee.state === "A",
          phone: employee.phone,
          firebase_uid: employee.firebase_uid,
          updatedAt: Date.now(),
        });
        setEmployees((prev) =>
          prev.map((current) =>
            current.identification_number === employee.identification_number
              ? ({ ...current, ...employee } as Employee)
              : current,
          ),
        );
      }
      handleCloseEditModal();
    } catch (error: unknown) {
      const msg =
        error instanceof ApiError
          ? translateError(error.message)
          : error instanceof Error
            ? error.message
            : "Error al actualizar empleado";
      setError(msg);
    }
  };

  const handleToggleState = async (employee: Employee) => {
    try {
      if (employee.state === "A" && user?.email === employee.email) {
        setError(
          "No puedes desactivar tu propia cuenta. Contacta a un administrador si necesitas ayuda.",
        );
        return;
      }

      const newState = employee.state === "A" ? "I" : "A";

      await employeeService.toggleEmployeeState(employee.identification_number, newState, {
        state: newState,
      });

      const isOnlineMode = typeof navigator !== "undefined" ? navigator.onLine : true;
      if (isOnlineMode) {
        employeeService.invalidateEmployeesCache();
        await fetchEmployees(true);
      } else {
        const { updateEmployee } = await import("@/services/indexedDb/employeeDb");
        await updateEmployee(employee.identification_number, {
          isActive: newState === "A",
          updatedAt: Date.now(),
        });
      }

      setEmployees((prev) =>
        prev.map((current) =>
          current.identification_number === employee.identification_number
            ? { ...current, state: newState }
            : current,
        ),
      );

      setMessage(
        `Estado de ${employee.first_name} ${employee.last_name} actualizado a ${newState === "A" ? "Active" : "Inactive"}`,
      );
    } catch (error: unknown) {
      const msg =
        error instanceof ApiError
          ? translateError(error.message)
          : error instanceof Error
            ? error.message
            : "Error al cambiar estado";
      setError(msg);
    }
  };

  const getRoleDisplayName = (role: string) => {
    const roleMap: Record<string, string> = {
      SUPER_ADMIN: "Administrador",
      MANAGER: "Gerente",
      SUPERVISOR: "Supervisor",
      EMPLOYEE: "Empleado",
    };
    return roleMap[role] || role;
  };

  const getStateDisplay = (state: string) => {
    if (state === "A") {
      return { label: "Active", color: "success" as const };
    }
    return { label: "Inactive", color: "danger" as const };
  };

  return (
    <div className="mx-auto max-w-6xl p-4">
      {message && (
        <div className="mb-4">
          <Alert
            color="success"
            variant="flat"
            title={message}
            onClose={() => setMessage("")}
          />
        </div>
      )}

      {error && (
        <div className="mb-4">
          <Alert
            color="danger"
            variant="flat"
            title={error}
            onClose={() => setError("")}
          />
        </div>
      )}

      <div className="mb-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold text-foreground">
            Gestion de Empleados
          </h2>
          <Button
            color="primary"
            variant="solid"
            type="button"
            startContent={<Plus className="w-4 h-4" />}
            onPress={handleCreateEmployee}
            className="font-semibold"
          >
            Create Employee
          </Button>
        </div>
      </div>

      <div className="bg-content1 rounded-lg shadow-sm border border-divider">
        <Table aria-label="Tabla de empleados">
          <TableHeader>
            <TableColumn>Nombre</TableColumn>
            <TableColumn>Email</TableColumn>
            <TableColumn>Rol</TableColumn>
            <TableColumn>Estado</TableColumn>
            <TableColumn>Acciones</TableColumn>
          </TableHeader>
          <TableBody emptyContent={isLoading ? "Cargando empleados..." : "No hay empleados registrados"}>
            {employees.map((employee: Employee) => {
              const stateDisplay = getStateDisplay(employee.state);
              return (
                <TableRow key={employee.identification_number}>
                  <TableCell>
                    <div className="flex flex-col">
                      <span className="font-medium text-foreground">
                        {employee.first_name} {employee.last_name}
                      </span>
                      <span className="text-xs text-default-500">
                        {employee.identification_number}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <span className="text-default-600">{employee.email}</span>
                  </TableCell>
                  <TableCell>
                    <Chip size="sm" variant="flat" color="primary">
                      {getRoleDisplayName(employee.role)}
                    </Chip>
                  </TableCell>
                  <TableCell>
                    <Chip size="sm" color={stateDisplay.color} variant="flat">
                      {stateDisplay.label}
                    </Chip>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Tooltip
                        content={
                          isOnline
                            ? "Edit empleado"
                            : "Se guardara para sincronizar al reconectar"
                        }
                      >
                        <Button
                          size="sm"
                          variant="flat"
                          color="primary"
                          type="button"
                          startContent={<Pencil className="w-3 h-3" />}
                          onPress={() => {
                            setSelectedEmployee(employee);
                            setIsEditModalOpen(true);
                            if (onSubTabChange) onSubTabChange("Edit Empleado");
                            if (onModalOpen) onModalOpen();
                          }}
                        >
                          Edit
                        </Button>
                      </Tooltip>
                      <Tooltip
                        content={
                          isOnline
                            ? "Cambiar estado"
                            : "Se guardara para sincronizar al reconectar"
                        }
                      >
                        <Button
                          size="sm"
                          variant={employee.state === "A" ? "danger" : "secondary"}
                          color={employee.state === "A" ? "danger" : "success"}
                          type="button"
                          startContent={
                            employee.state === "A" ? (
                              <ToggleLeft className="w-3 h-3" />
                            ) : (
                              <ToggleRight className="w-3 h-3" />
                            )
                          }
                          onPress={() => handleToggleState(employee)}
                        >
                          {employee.state === "A" ? "Desactivar" : "Activar"}
                        </Button>
                      </Tooltip>
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      {isModalOpen && (
        <CreateEmployeeModal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          onSave={handleSaveEmployee}
          onError={setError}
        />
      )}

      {isEditModalOpen && selectedEmployee && (
        <CreateEmployeeModal
          isOpen={isEditModalOpen}
          onClose={handleCloseEditModal}
          onSave={handleUpdateEmployee}
          onError={setError}
          initialData={selectedEmployee}
          isEdit={true}
        />
      )}
    </div>
  );
};
