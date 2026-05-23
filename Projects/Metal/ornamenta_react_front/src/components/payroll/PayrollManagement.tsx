import React, { useState, useEffect, useCallback } from "react";
import {
  Payroll,
  PayrollFormData,
  PayrollFilters,
  PayrollStateChangeRequest,
  PayrollSummary,
  ContractType,
  StatePayroll,
  createMoney,
  formatMoney,
} from "@/types/payroll";
import { employeeService, Employee } from "@/services/employeeService";
import {
  PayrollForm,
  PayrollCard,
  PayrollDetails,
  PayrollList,
  ServiceProvisionTasksModal,
} from "@components/payroll";
import { CenteredModal } from "@components/common/CenteredModal";
import { payrollService } from "@/services/payrollService";
import { DollarSign, Grid3x3, List } from "lucide-react";
import { useAuth } from "@hooks/useAuth";

export const PayrollManagement: React.FC = () => {
  const { user } = useAuth();

  // Estados principales
  const [payrolls, setPayrolls] = useState<Payroll[]>([]);
  const [summary, setSummary] = useState<PayrollSummary>({
    total_payrolls: 0,
    total_amount: createMoney(0),
    by_state: {} as Record<StatePayroll, number>,
    by_contract_type: {} as Record<ContractType, number>,
  });
  const [filters, setFilters] = useState<PayrollFilters>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Estados de UI
  const [showForm, setShowForm] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [selectedPayroll, setSelectedPayroll] = useState<Payroll | null>(null);
  const [editingPayroll, setEditingPayroll] = useState<Payroll | null>(null);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [viewMode, setViewMode] = useState<"cards" | "list">("cards");
  const [showTasksModal, setShowTasksModal] = useState(false);
  const [selectedPayrollForTasks, setSelectedPayrollForTasks] =
    useState<Payroll | null>(null);
  const [currentUserIdentification, setCurrentUserIdentification] = useState<
    string | null
  >(null);

  // Obtener el identification_number del user actual (gerente)
  const fetchCurrentUserIdentification = useCallback(async () => {
    if (!user) return null;

    try {
      const token = await user.getIdToken();
      const response = await fetch(`${import.meta.env.VITE_API_URL}/users/me`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const userData = await response.json();
        const identification = userData.identification_number || userData.id;
        setCurrentUserIdentification(identification);
        return identification;
      }
    } catch (err) {
      console.error("Error obteniendo identificacion del user:", err);
    }
    return null;
  }, [user]);

  // 1. Function de carga de empleados
  const loadEmployees = useCallback(async () => {
    try {
      const employeesData = await employeeService.getEmployees();
      setEmployees(employeesData);
    } catch (err) {
      setError("Error al cargar los empleados");
      console.error("Error loading employees:", err);
    }
  }, []);

  // 3. Logica de carga de payrolls y resumen
  const loadPayrolls = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Obtener la identificacion del user actual si no la tenemos
      let userIdentification = currentUserIdentification;
      if (!userIdentification) {
        userIdentification = await fetchCurrentUserIdentification();
      }

      // Asegurar que los empleados esten cargados antes de cargar payrolls
      if (employees.length === 0) {
        await loadEmployees();
      }

      const payrollsData = await payrollService.getPayrolls(filters);

      // Filtrar las payrolls para excluir la del gerente actual
      const filteredPayrolls = payrollsData.filter((payroll) => {
        // Excluir la payroll del gerente
        if (
          userIdentification &&
          payroll.identification_number === userIdentification
        ) {
          return false;
        }
        return true;
      });

      // Log para diagnosticar problemas
      for (const payroll of filteredPayrolls) {
        if (
          !payroll.identification_number ||
          payroll.identification_number.trim() === ""
        ) {
          console.warn("loadPayrolls: Payroll sin identification_number:", {
            payroll_id: payroll.payroll_id,
            identification_number: payroll.identification_number,
          });
        }
      }

      setPayrolls(filteredPayrolls);

      try {
        const summaryData = await payrollService.getPayrollSummary();
        setSummary(summaryData);
      } catch (summaryError) {
        console.warn("No se pudo cargar el resumen de payrolls:", summaryError);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Error al cargar las payrolls",
      );
      console.error("Error loading payrolls:", err);
    } finally {
      setIsLoading(false);
    }
  }, [
    filters,
    employees.length,
    loadEmployees,
    currentUserIdentification,
    fetchCurrentUserIdentification,
  ]);

  // 4. Logica de carga de datos iniciales
  useEffect(() => {
    fetchCurrentUserIdentification();
    loadPayrolls();
    loadEmployees();
  }, [loadEmployees, loadPayrolls, fetchCurrentUserIdentification]);

  const handleCreatePayroll = async (formData: PayrollFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      // 1 Create la payroll (el backend crea automaticamente el historial)
      const newPayroll = await payrollService.createPayroll(formData);

      console.log("OK Payroll created exitosamente:", newPayroll.payroll_id);

      // 2 Recargar datos
      await loadPayrolls();
      await loadEmployees();

      // 3 Actualizar resumen
      const summaryData = await payrollService.getPayrollSummary();
      setSummary(summaryData);

      // 4 Cerrar formulario
      setShowForm(false);
      setEditingPayroll(null);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Error al create la payroll";
      setError(errorMessage);
      console.error("Error creating payroll:", err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdatePayroll = async (
    payrollId: string,
    formData: PayrollFormData,
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      await payrollService.updatePayroll(payrollId, formData);
      await loadPayrolls();

      const summaryData = await payrollService.getPayrollSummary();
      setSummary(summaryData);

      setShowForm(false);
      setEditingPayroll(null);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Error al actualizar la payroll",
      );
      console.error("Error updating payroll:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStateChange = async (
    payrollId: string,
    request: PayrollStateChangeRequest,
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      await payrollService.changePayrollState(
        payrollId,
        request.new_state,
        request.reason,
      );
      await loadPayrolls();

      const summaryData = await payrollService.getPayrollSummary();
      setSummary(summaryData);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Error al cambiar el estado de la payroll",
      );
      console.error("Error changing payroll state:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewDetails = (payroll: Payroll) => {
    setSelectedPayroll(payroll);
    setShowDetails(true);
  };

  const handleEdit = (payroll: Payroll) => {
    setEditingPayroll(payroll);
    setShowForm(true);
    setShowDetails(false);
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingPayroll(null);
  };

  const handleCloseDetails = () => {
    setShowDetails(false);
    setSelectedPayroll(null);
  };

  const handleOpenTasksModal = (payroll: Payroll) => {
    setSelectedPayrollForTasks(payroll);
    setShowTasksModal(true);
  };

  const handleCloseTasksModal = () => {
    setShowTasksModal(false);
    setSelectedPayrollForTasks(null);
  };

  const getEmployeeName = (identificationNumber: string): string => {
    const employee = employees.find(
      (emp) => emp.identification_number === identificationNumber,
    );
    return employee
      ? `${employee.first_name} ${employee.last_name}`
      : "Empleado desconocido";
  };

  // Loading state
  if (isLoading && payrolls.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Calcular el valor total de payrolls activas
  const activePayrolls = payrolls.filter(
    (payroll) => payroll.state === StatePayroll.ACTIVE,
  );
  const totalActiveAmount = activePayrolls.reduce((sum, payroll) => {
    const amount = payroll.current_period_salary || payroll.base_salary.amount;
    return sum + (Number.isNaN(amount) ? 0 : amount);
  }, 0);

  const updatedSummary: PayrollSummary = {
    ...summary,
    total_amount: createMoney(totalActiveAmount, "COP"),
    total_payrolls: payrolls.length,
  };

  return (
    <div className="space-y-6">
      {/* Header con boton de create */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div>
          <p className="text-default-500 mt-1">
            Administra las payrolls de todos los empleados
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Toggle de vista */}
          <div className="flex items-center gap-1 bg-content1 border border-divider rounded-xl p-1">
            <button
              type="button"
              onClick={() => setViewMode("cards")}
              className={`p-2 rounded-lg transition-colors ${
                viewMode === "cards"
                  ? "bg-primary text-primary-foreground"
                  : "text-default-600 hover:bg-default-100"
              }`}
              title="Vista de tarjetas"
            >
              <Grid3x3 className="w-5 h-5" />
            </button>
            <button
              type="button"
              onClick={() => setViewMode("list")}
              className={`p-2 rounded-lg transition-colors ${
                viewMode === "list"
                  ? "bg-primary text-primary-foreground"
                  : "text-default-600 hover:bg-default-100"
              }`}
              title="Vista de lista"
            >
              <List className="w-5 h-5" />
            </button>
          </div>
          <button
            type="button"
            onClick={() => setShowForm(true)}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-xl hover:opacity-90 transition-opacity font-semibold"
          >
            + Nueva Payroll
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-danger-50 border border-danger-200 text-danger-700 px-4 py-3 rounded-xl">
          {error}
        </div>
      )}

      {/* Resumen */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
        <div className="bg-content1 border border-divider rounded-xl shadow-sm p-4 md:p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-default-500">Total Payrolls</p>
              <p className="text-2xl font-bold text-foreground">
                {updatedSummary.total_payrolls}
              </p>
            </div>
            <div className="p-2 bg-primary/10 rounded-xl">
              <DollarSign className="w-7 h-7 text-primary" />
            </div>
          </div>
        </div>

        <div className="bg-content1 border border-divider rounded-xl shadow-sm p-4 md:p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-default-500">Total Activas</p>
              <p className="text-2xl font-bold text-success-600">
                {activePayrolls.length}
              </p>
            </div>
            <div className="p-2 bg-success-50 rounded-xl">
              <DollarSign className="w-7 h-7 text-success-500" />
            </div>
          </div>
        </div>

        <div className="bg-content1 border border-divider rounded-xl shadow-sm p-4 md:p-6 sm:col-span-2 lg:col-span-1">
          <div>
            <p className="text-sm text-default-500">Valor Total Payrolls Activas</p>
            <p className="text-2xl font-bold text-primary">
              {formatMoney(updatedSummary.total_amount)}
            </p>
          </div>
        </div>
      </div>

      {/* Vista de payrolls */}
      {viewMode === "list" ? (
        <PayrollList
          payrolls={payrolls}
          summary={updatedSummary}
          filters={filters}
          onFiltersChange={setFilters}
          onPayrollSelect={handleViewDetails}
          onStateChange={handleStateChange}
          isLoading={isLoading}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {payrolls.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <p className="text-default-400">No hay payrolls registradas</p>
            </div>
          ) : (
            payrolls.map((payroll) => (
              <PayrollCard
                key={payroll.payroll_id}
                payroll={payroll}
                onStateChange={handleStateChange}
                onEdit={handleEdit}
                onViewDetails={handleViewDetails}
                onViewTasks={handleOpenTasksModal}
                employeeName={getEmployeeName(payroll.identification_number)}
                isLoading={isLoading}
              />
            ))
          )}
        </div>
      )}

      {/* Modal de formulario */}
      {showForm && (
        <CenteredModal
          isOpen={showForm}
          onOpenChange={setShowForm}
          size="2xl"
          scrollBehavior="inside"
          backdrop="blur"
        >
          {() => (
            <div className="p-2">
              <PayrollForm
                onSubmit={
                  editingPayroll
                    ? (data) =>
                        handleUpdatePayroll(editingPayroll.payroll_id, data)
                    : handleCreatePayroll
                }
                onCancel={handleCloseForm}
                initialData={editingPayroll || undefined}
                employees={employees
                  .filter(
                    (emp) =>
                      emp.identification_number !== currentUserIdentification,
                  )
                  .map((emp) => ({
                    id: emp.identification_number,
                    name: `${emp.first_name} ${emp.last_name}`,
                    identification_number: emp.identification_number,
                  }))}
                isLoading={isLoading}
              />
            </div>
          )}
        </CenteredModal>
      )}

      {/* Modal de detalles */}
      {showDetails && selectedPayroll && (
        <PayrollDetails
          payroll={selectedPayroll}
          onClose={handleCloseDetails}
          onEdit={handleEdit}
          employeeName={getEmployeeName(selectedPayroll.identification_number)}
        />
      )}

      {/* Modal de tasks */}
      {showTasksModal && selectedPayrollForTasks && (
        <ServiceProvisionTasksModal
          payroll={selectedPayrollForTasks}
          isOpen={showTasksModal}
          onClose={handleCloseTasksModal}
        />
      )}
    </div>
  );
};
