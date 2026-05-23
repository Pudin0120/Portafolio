import React, { useState, useMemo } from "react";
import {
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  Input,
  ScrollShadow,
  Card,
  CardBody,
} from "@heroui/react";
import { Search, User } from "lucide-react";
import { Employee } from "@/services/employeeService";
import { CenteredModal } from "@components/common/CenteredModal";

interface AssignTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAssign: (employeeId: string) => Promise<void>;
  employees: Employee[];
  taskName: string;
  isLoading: boolean;
}

export const AssignTaskModal: React.FC<AssignTaskModalProps> = ({
  isOpen,
  onClose,
  onAssign,
  employees,
  taskName,
  isLoading,
}) => {
  const [searchValue, setSearchValue] = useState("");
  const [assignError, setAssignError] = useState<string | null>(null);
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string | null>(
    null,
  );

  const filteredEmployees = useMemo(() => {
    return employees
      .filter((employee) => employee.state === "A")
      .filter((employee) => {
        const fullName =
          `${employee.first_name} ${employee.last_name}`.toLowerCase();
        const email = employee.email?.toLowerCase() || "";
        const search = searchValue.toLowerCase();

        return fullName.includes(search) || email.includes(search);
      });
  }, [employees, searchValue]);

  const selectedEmployee = useMemo(() => {
    return (
      filteredEmployees.find(
        (employee) => employee.firebase_uid === selectedEmployeeId,
      ) ?? null
    );
  }, [filteredEmployees, selectedEmployeeId]);

  const handleAssign = async () => {
    if (!selectedEmployeeId) {
      return;
    }

    try {
      await onAssign(selectedEmployeeId);
      setAssignError(null);
      setSearchValue("");
      setSelectedEmployeeId(null);
      onClose();
    } catch {
      setAssignError(
        "No se pudo asignar la task en este momento. Intenta nuevamente.",
      );
    }
  };

  const handleClose = () => {
    setAssignError(null);
    setSearchValue("");
    setSelectedEmployeeId(null);
    onClose();
  };

  return (
    <CenteredModal
      isOpen={isOpen}
      onOpenChange={(open: boolean) => !open && handleClose()}
      size="md"
      backdrop="blur"
    >
      {() => (
        <>
          <ModalHeader className="flex flex-col gap-1 border-b border-divider">
            <h2 className="text-lg font-semibold text-foreground">
              Asignar task
            </h2>
            <p className="mt-1 text-sm font-normal text-default-500">
              {taskName}
            </p>
          </ModalHeader>

          <ModalBody className="py-6">
            <div className="mb-4 flex items-center gap-2">
              <Input
                isClearable
                className="w-full"
                placeholder="Search por nombre o email..."
                startContent={<Search className="h-4 w-4 text-default-400" />}
                value={searchValue}
                onValueChange={setSearchValue}
                onClear={() => setSearchValue("")}
              />
            </div>

            {assignError && (
              <div className="mb-4 rounded-lg border border-danger-200 bg-danger-50 px-3 py-2 text-sm text-danger-700">
                {assignError}
              </div>
            )}

            <ScrollShadow className="h-[300px] max-h-[60dvh]">
              {filteredEmployees.length > 0 ? (
                <div className="flex flex-col gap-2 pr-4">
                  {filteredEmployees.map((employee) => {
                    const isSelected =
                      selectedEmployeeId === employee.firebase_uid;

                    return (
                      <Card
                        key={employee.firebase_uid}
                        isPressable
                        isHoverable
                        className={`cursor-pointer transition-all ${
                          isSelected
                            ? "border-2 border-primary bg-primary-50 shadow-sm"
                            : "border border-divider hover:border-primary/40"
                        }`}
                        onPress={() =>
                          setSelectedEmployeeId(employee.firebase_uid)
                        }
                      >
                        <CardBody className="p-3">
                          <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
                              <User className="h-5 w-5" />
                            </div>
                            <div className="min-w-0 flex-1">
                              <p className="truncate font-semibold text-foreground">
                                {employee.first_name} {employee.last_name}
                              </p>
                              <p className="truncate text-xs text-default-500">
                                {employee.email || "Sin email"}
                              </p>
                            </div>
                            {isSelected && (
                              <div className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
                                <span className="text-sm"></span>
                              </div>
                            )}
                          </div>
                        </CardBody>
                      </Card>
                    );
                  })}
                </div>
              ) : (
                <div className="flex h-full items-center justify-center">
                  <div className="text-center">
                    <User className="mx-auto mb-2 h-8 w-8 text-default-300" />
                    <p className="text-sm text-default-500">
                      {searchValue
                        ? "No se encontraron empleados"
                        : "Cargando empleados..."}
                    </p>
                  </div>
                </div>
              )}
            </ScrollShadow>

            {selectedEmployeeId && (
              <div className="mt-4 rounded-lg border border-primary-200 bg-primary-50 p-3">
                <span className="mb-1 block text-xs font-medium text-primary-700">
                  Asignado a:
                </span>
                <p className="text-sm font-semibold text-primary-900">
                  {selectedEmployee
                    ? `${selectedEmployee.first_name} ${selectedEmployee.last_name}`
                    : "Empleado"}
                </p>
              </div>
            )}
          </ModalBody>

          <ModalFooter className="flex-col-reverse gap-2 border-t border-divider sm:flex-row sm:justify-end">
            <Button
              color="default"
              variant="flat"
              onPress={handleClose}
              isDisabled={isLoading}
              className="w-full sm:w-auto"
              type="button"
            >
              Cancel
            </Button>
            <Button
              color="primary"
              onPress={handleAssign}
              isDisabled={!selectedEmployeeId || isLoading}
              isLoading={isLoading}
              className="w-full sm:w-auto"
              type="button"
            >
              Asignar task
            </Button>
          </ModalFooter>
        </>
      )}
    </CenteredModal>
  );
};

export default AssignTaskModal;
