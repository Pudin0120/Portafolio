import React, { useState } from "react";
import {
  Payroll,
  PayrollFilters,
  ContractType,
  StatePayroll,
  PayrollSummary,
  PayrollStateChangeRequest,
  getContractTypeLabel,
  getStateLabel,
  formatMoney,
} from "../../types/payroll";
import { ServiceProvisionTasksModal } from "./ServiceProvisionTasksModal";
import { FileText } from "lucide-react";

// Helper para formatear fechas mostrando "Hoy" cuando corresponda
const formatDateOrToday = (
  dateString: string | undefined,
  isActive: boolean,
): string => {
  if (!dateString) return "Presente";

  const date = new Date(dateString);
  const today = new Date();

  // Comparar solo ano, mes y dia
  const isSameDay =
    date.getFullYear() === today.getFullYear() &&
    date.getMonth() === today.getMonth() &&
    date.getDate() === today.getDate();

  if (isSameDay && isActive) {
    return "Hoy";
  }

  return date.toLocaleDateString("es-CO");
};

interface PayrollListProps {
  payrolls: Payroll[];
  summary: PayrollSummary;
  filters: PayrollFilters;
  onFiltersChange: (filters: PayrollFilters) => void;
  onPayrollSelect: (payroll: Payroll) => void;
  onStateChange: (
    payrollId: string,
    request: PayrollStateChangeRequest,
  ) => void;
  isLoading?: boolean;
}

export const PayrollList: React.FC<PayrollListProps> = ({
  payrolls,
  summary,
  filters,
  onFiltersChange,
  onPayrollSelect,
  onStateChange,
  isLoading = false,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [actionError, setActionError] = useState<string | null>(null);
  const [showStateChangeModal, setShowStateChangeModal] = useState<
    string | null
  >(null);
  const [selectedPayrollForStateChange, setSelectedPayrollForStateChange] =
    useState<Payroll | null>(null);
  const [newState, setNewState] = useState<StatePayroll | null>(null);
  const [reason, setReason] = useState("");
  const [showTasksModal, setShowTasksModal] = useState(false);
  const [selectedPayrollForTasks, setSelectedPayrollForTasks] =
    useState<Payroll | null>(null);

  const getAvailableStates = (currentState: StatePayroll): StatePayroll[] => {
    switch (currentState) {
      case StatePayroll.ACTIVE:
        return [StatePayroll.LIQUIDATED, StatePayroll.CANCELLED];
      case StatePayroll.LIQUIDATED:
        return [StatePayroll.PAID, StatePayroll.CANCELLED];
      case StatePayroll.PAID:
        return [StatePayroll.CANCELLED];
      case StatePayroll.CANCELLED:
        return [StatePayroll.ACTIVE];
      default:
        return [];
    }
  };

  const handleOpenStateChangeModal = (payroll: Payroll) => {
    setActionError(null);
    setSelectedPayrollForStateChange(payroll);
    const availableStates = getAvailableStates(payroll.state);
    setNewState(availableStates[0] || null);
    setReason("");
    setShowStateChangeModal(payroll.payroll_id);
  };

  const handleCloseStateChangeModal = () => {
    setShowStateChangeModal(null);
    setSelectedPayrollForStateChange(null);
    setNewState(null);
    setReason("");
  };

  const handleOpenTasksModal = (payroll: Payroll, e: React.MouseEvent) => {
    e.stopPropagation();
    setActionError(null);
    setSelectedPayrollForTasks(payroll);
    setShowTasksModal(true);
  };

  const handleCloseTasksModal = () => {
    setShowTasksModal(false);
    setSelectedPayrollForTasks(null);
  };

  const handleStateChange = async () => {
    if (!selectedPayrollForStateChange || !newState) return;
    if (newState === selectedPayrollForStateChange.state) return;
    if (!reason.trim()) return;

    try {
      await onStateChange(selectedPayrollForStateChange.payroll_id, {
        new_state: newState,
        reason: reason.trim(),
      });
      setActionError(null);
      handleCloseStateChangeModal();
    } catch {
      setActionError(
        "No se pudo cambiar el estado de la payroll. Intenta nuevamente.",
      );
    }
  };

  const handleFilterChange = <K extends keyof PayrollFilters>(
    key: K,
    value: PayrollFilters[K],
  ) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const filteredPayrolls = payrolls.filter((payroll) => {
    const matchesSearch =
      payroll.payroll_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      payroll.identification_number
        .toLowerCase()
        .includes(searchTerm.toLowerCase());
    const matchesContractType =
      !filters.contract_type || payroll.contract_type === filters.contract_type;
    const matchesState = !filters.state || payroll.state === filters.state;

    return matchesSearch && matchesContractType && matchesState;
  });

  return (
    <div className="space-y-6">
      {/* Resumen */}
      <div className="bg-content1 rounded-2xl shadow-lg border border-divider p-6">
        <h2 className="text-2xl font-bold text-foreground mb-6">
          Resumen de Payrolls
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center p-4 rounded-xl bg-primary-50 border border-primary-100">
            <p className="text-3xl font-bold text-primary-700 mb-1">
              {summary.total_payrolls}
            </p>
            <p className="text-sm font-medium text-default-600">
              Total Payrolls
            </p>
          </div>
          <div className="text-center p-4 rounded-xl bg-success-50 border border-success-100">
            <p className="text-3xl font-bold text-success-700 mb-1">
              {formatMoney(summary.total_amount)}
            </p>
            <p className="text-sm font-medium text-default-600">Valor Total</p>
          </div>
          <div className="text-center p-4 rounded-xl bg-warning-50 border border-warning-100">
            <p className="text-3xl font-bold text-warning-700 mb-1">
              {summary.by_state[StatePayroll.ACTIVE] || 0}
            </p>
            <p className="text-sm font-medium text-default-600">Activas</p>
          </div>
          <div className="text-center p-4 rounded-xl bg-secondary-50 border border-secondary-100">
            <p className="text-3xl font-bold text-secondary-700 mb-1">
              {summary.by_state[StatePayroll.PAID] || 0}
            </p>
            <p className="text-sm font-medium text-default-600">Pagadas</p>
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-content1 rounded-2xl shadow-lg border border-divider p-6">
        <h3 className="text-xl font-bold text-foreground mb-6">Filtros</h3>
        {actionError && (
          <div className="mb-4 rounded-xl border border-danger-200 bg-danger-50 px-4 py-3 text-sm text-danger-700">
            {actionError}
          </div>
        )}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-default-700 mb-2">
              Search
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
className="w-full px-4 py-2.5 border border-default-300 rounded-xl focus:outline-hidden focus:ring-2 focus:ring-primary focus:border-transparent transition-all bg-content2 text-foreground"
              placeholder="ID payroll o number de identificacion..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-default-700 mb-2">
              Tipo de Contract
            </label>
            <select
              value={filters.contract_type || ""}
              onChange={(e) =>
                handleFilterChange(
                  "contract_type",
                  (e.target.value || undefined) as ContractType | undefined,
                )
              }
className="w-full px-4 py-2.5 border border-default-300 rounded-xl focus:outline-hidden focus:ring-2 focus:ring-primary focus:border-transparent transition-all bg-content2 text-foreground"
            >
              <option value="">Todos</option>
              {Object.values(ContractType).map((type) => (
                <option key={type} value={type}>
                  {getContractTypeLabel(type)}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-default-700 mb-2">
              Estado
            </label>
            <select
              value={filters.state || ""}
              onChange={(e) =>
                handleFilterChange(
                  "state",
                  (e.target.value || undefined) as StatePayroll | undefined,
                )
              }
className="w-full px-4 py-2.5 border border-default-300 rounded-xl focus:outline-hidden focus:ring-2 focus:ring-primary focus:border-transparent transition-all bg-content2 text-foreground"
            >
              <option value="">Todos</option>
              {Object.values(StatePayroll).map((state) => (
                <option key={state} value={state}>
                  {getStateLabel(state)}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={() => {
                onFiltersChange({});
                setSearchTerm("");
              }}
              className="w-full px-4 py-2.5 text-default-700 bg-default-100 rounded-xl hover:bg-default-200 transition-colors font-medium"
            >
              Limpiar Filtros
            </button>
          </div>
        </div>
      </div>

      {/* Lista de Payrolls */}
      <div className="bg-content1 border border-divider rounded-2xl shadow-sm overflow-hidden">
        <div className="p-4 md:p-6 border-b border-divider bg-default-50">
          <h3 className="text-lg md:text-xl font-bold text-foreground">
            Payrolls ({filteredPayrolls.length})
          </h3>
        </div>

        {isLoading ? (
          <div className="p-6 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            <p className="mt-2 text-default-500">Cargando payrolls...</p>
          </div>
        ) : filteredPayrolls.length === 0 ? (
          <div className="p-6 text-center text-default-400">
            <p>No se encontraron payrolls con los filtros aplicados.</p>
          </div>
        ) : (
          <div className="divide-y divide-divider">
            {filteredPayrolls.map((payroll) => {
              const availableStates = getAvailableStates(payroll.state);
              const stateClass =
                payroll.state === StatePayroll.ACTIVE
                  ? "bg-warning-100 text-warning-800"
                  : payroll.state === StatePayroll.LIQUIDATED
                  ? "bg-warning-50 text-warning-700"
                  : payroll.state === StatePayroll.PAID
                  ? "bg-success-100 text-success-800"
                  : "bg-danger-100 text-danger-800";
              return (
                <button
                  key={payroll.payroll_id}
                  type="button"
                  className="w-full text-left p-4 md:p-6 hover:bg-default-50 transition-colors"
                  onClick={() => onPayrollSelect(payroll)}
                >
                  <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2 mb-1">
                        <h4 className="text-base font-medium text-foreground">
                          Payroll #{payroll.payroll_id.slice(0, 8)}
                        </h4>
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${stateClass}`}>
                          {getStateLabel(payroll.state)}
                        </span>
                      </div>
                      <p className="text-sm text-default-500">
                        {getContractTypeLabel(payroll.contract_type)}
                      </p>
                      <p className="text-sm font-medium text-default-600 mt-0.5">
                        ID Empleado: {payroll.identification_number}
                      </p>
                      {payroll.current_period_start_date && (
                        <p className="text-xs text-default-400 mt-0.5">
                          Periodo:{" "}
                          {formatDateOrToday(payroll.current_period_start_date, payroll.state === StatePayroll.ACTIVE)}{" "}
                          -{" "}
                          {formatDateOrToday(payroll.current_period_end_date, payroll.state === StatePayroll.ACTIVE)}
                        </p>
                      )}
                      <p className="text-sm font-semibold text-success-600 mt-1">
                        {formatMoney({
                          amount: payroll.current_period_salary || payroll.base_salary.amount,
                          currency: "COP",
                        })}
                      </p>
                    </div>

                    <div className="flex flex-wrap gap-2 w-full sm:w-auto">
                      {payroll.is_service_provision && (
                        <button
                          onClick={(e) => handleOpenTasksModal(payroll, e)}
                          className="px-3 py-2 bg-primary text-primary-foreground rounded-xl hover:opacity-90 transition-opacity font-medium text-sm flex items-center gap-2 disabled:opacity-50"
                          disabled={isLoading}
                        >
                          <FileText className="w-4 h-4" />
                          Ver Tasks
                        </button>
                      )}
                      {availableStates.length > 0 && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleOpenStateChangeModal(payroll);
                          }}
                          className="px-3 py-2 bg-warning text-warning-foreground rounded-xl hover:opacity-90 transition-opacity font-medium text-sm disabled:opacity-50"
                          disabled={isLoading}
                        >
                          Cambiar Estado
                        </button>
                      )}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Modal de cambio de estado */}
      {showStateChangeModal && selectedPayrollForStateChange && newState && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-content1 border border-divider rounded-2xl shadow-xl p-5 md:p-6 w-full max-w-md">
            <h3 className="text-lg md:text-xl font-bold text-foreground mb-1">
              Cambiar Estado de Payroll
            </h3>
            <p className="text-sm text-default-500 mb-4">
              Payroll #{selectedPayrollForStateChange.payroll_id.slice(0, 8)}
            </p>

            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-default-700 mb-2">Estado Actual</p>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  selectedPayrollForStateChange.state === StatePayroll.ACTIVE
                    ? "bg-warning-100 text-warning-800"
                    : selectedPayrollForStateChange.state === StatePayroll.LIQUIDATED
                    ? "bg-warning-50 text-warning-700"
                    : selectedPayrollForStateChange.state === StatePayroll.PAID
                    ? "bg-success-100 text-success-800"
                    : "bg-danger-100 text-danger-800"
                }`}>
                  {getStateLabel(selectedPayrollForStateChange.state)}
                </span>
              </div>

              <div>
                <label htmlFor="list-new-state" className="block text-sm font-medium text-default-700 mb-2">
                  Nuevo Estado
                </label>
                <select
                  id="list-new-state"
                  value={newState}
                  onChange={(e) => setNewState(e.target.value as StatePayroll)}
className="w-full px-4 py-2.5 border border-default-300 rounded-xl bg-content2 text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
                >
                  {getAvailableStates(selectedPayrollForStateChange.state).map((state) => (
                    <option key={state} value={state}>
                      {getStateLabel(state)}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="list-reason" className="block text-sm font-medium text-default-700 mb-2">
                  Razon <span className="text-danger-500">*</span>
                </label>
                <textarea
                  id="list-reason"
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
className="w-full px-4 py-2.5 border border-default-300 rounded-xl bg-content2 text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary resize-none"
                  rows={3}
                  placeholder="Describe la razon del cambio de estado..."
                />
              </div>
            </div>

            <div className="flex flex-col-reverse sm:flex-row justify-end gap-3 mt-5">
              <button
                onClick={handleCloseStateChangeModal}
                className="px-5 py-2.5 text-default-600 bg-default-100 rounded-xl hover:bg-default-200 transition-colors font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleStateChange}
                className="px-5 py-2.5 bg-primary text-primary-foreground rounded-xl hover:opacity-90 transition-opacity font-semibold disabled:opacity-50"
                disabled={isLoading || !reason.trim() || newState === selectedPayrollForStateChange.state}
              >
                {isLoading ? "Cambiando..." : "Cambiar Estado"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de tasks de prestacion de servicios */}
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
