import React, { useState } from 'react';
import { FileText } from 'lucide-react';
import { 
  Payroll, 
  StatePayroll, 
  PayrollStateChangeRequest,
  getStateLabel,
  getStateColor,
  formatMoney,
  getContractTypeLabel
} from '../../types/payroll';

// Helper para formatear fechas mostrando "Hoy" cuando corresponda
const formatDateOrToday = (dateString: string | undefined, isActive: boolean): string => {
  if (!dateString) return 'Presente';
  
  const date = new Date(dateString);
  const today = new Date();
  
  // Comparar solo ano, mes y dia
  const isSameDay = 
    date.getFullYear() === today.getFullYear() &&
    date.getMonth() === today.getMonth() &&
    date.getDate() === today.getDate();
  
  if (isSameDay && isActive) {
    return 'Hoy';
  }
  
  return date.toLocaleDateString('es-CO');
};

interface PayrollCardProps {
  payroll: Payroll;
  onStateChange: (payrollId: string, request: PayrollStateChangeRequest) => void;
  onEdit: (payroll: Payroll) => void;
  onViewDetails: (payroll: Payroll) => void;
  onViewTasks?: (payroll: Payroll) => void;
  isLoading?: boolean;
  employeeName?: string;
}

export const PayrollCard: React.FC<PayrollCardProps> = ({
  payroll,
  onStateChange,
  onEdit,
  onViewDetails,
  onViewTasks,
  isLoading = false,
  employeeName = 'Empleado'
}) => {
  const [showStateChangeModal, setShowStateChangeModal] = useState(false);
  const [newState, setNewState] = useState<StatePayroll>(payroll.state);
  const [reason, setReason] = useState('');

  const handleStateChange = () => {
    if (newState !== payroll.state) {
      onStateChange(payroll.payroll_id, {
        new_state: newState,
        reason: reason.trim()
      });
      setShowStateChangeModal(false);
      setReason('');
    }
  };

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

  const availableStates = getAvailableStates(payroll.state);
  const totalPayroll = payroll.current_period_salary || payroll.base_salary.amount;

  return (
    <>
      <div className="bg-content1 border border-divider rounded-xl shadow-sm p-4 md:p-6 hover:shadow-md transition-shadow">
        <div className="flex justify-between items-start mb-4 gap-2">
          <div className="flex-1 min-w-0">
            <h3 className="text-base md:text-lg font-semibold text-foreground truncate">
              Payroll #{payroll.payroll_id.slice(0, 8)}
            </h3>
            <p className="text-sm text-default-500 truncate">
              {employeeName} - {getContractTypeLabel(payroll.contract_type)}
            </p>
            {payroll.current_period_start_date && (
              <p className="text-xs text-default-400 mt-1">
                Periodo: {formatDateOrToday(payroll.current_period_start_date, payroll.state === StatePayroll.ACTIVE)} - {' '}
                {formatDateOrToday(payroll.current_period_end_date, payroll.state === StatePayroll.ACTIVE)}
              </p>
            )}
          </div>
          <span className={`flex-shrink-0 px-3 py-1 rounded-full text-xs font-medium ${getStateColor(payroll.state)}`}>
            {getStateLabel(payroll.state)}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-default-50 rounded-lg p-3">
            <p className="text-xs text-default-500 mb-1">Salario Base</p>
            <p className="font-semibold text-foreground text-sm">
              {payroll.base_salary_formatted || formatMoney(payroll.base_salary)}
            </p>
          </div>
          {payroll.current_period_salary !== undefined && (
            <div className="bg-default-50 rounded-lg p-3">
              <p className="text-xs text-default-500 mb-1">Periodo Actual</p>
              <p className="font-semibold text-foreground text-sm">
                {payroll.current_period_salary_formatted || 
                 formatMoney({ amount: payroll.current_period_salary, currency: 'COP' })}
              </p>
            </div>
          )}
        </div>

        <div className="border-t border-divider pt-3 mb-4">
          <div className="flex justify-between items-center">
            <span className="text-sm text-default-500">Total Payroll</span>
            <span className="text-xl font-bold text-success-600">
              {payroll.current_period_salary_formatted || 
               formatMoney({ amount: totalPayroll, currency: 'COP' })}
            </span>
          </div>
        </div>

        <div className="flex flex-col space-y-2">
          {payroll.is_service_provision && onViewTasks && (
            <button
              onClick={() => onViewTasks(payroll)}
              className="w-full px-3 py-2 text-primary-foreground bg-primary rounded-xl hover:opacity-90 transition-opacity text-sm flex items-center justify-center gap-2 font-medium disabled:opacity-50"
              disabled={isLoading}
            >
              <FileText className="w-4 h-4" />
              Ver Tasks
            </button>
          )}
          
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => onViewDetails(payroll)}
              className="flex-1 px-3 py-2 text-primary bg-primary/10 rounded-xl hover:bg-primary/20 transition-colors text-sm font-medium disabled:opacity-50"
              disabled={isLoading}
            >
              Ver Detalles
            </button>
            <button
              onClick={() => onEdit(payroll)}
              className="flex-1 px-3 py-2 text-default-600 bg-default-100 rounded-xl hover:bg-default-200 transition-colors text-sm font-medium disabled:opacity-50"
              disabled={isLoading}
            >
              Edit
            </button>
            {availableStates.length > 0 && (
              <button
                onClick={() => setShowStateChangeModal(true)}
                className="flex-1 px-3 py-2 text-warning-700 bg-warning-50 rounded-xl hover:bg-warning-100 transition-colors text-sm font-medium disabled:opacity-50"
                disabled={isLoading}
              >
                Cambiar Estado
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Modal para cambio de estado */}
      {showStateChangeModal && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-content1 border border-divider rounded-xl shadow-xl p-5 md:p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-foreground mb-4">
              Cambiar Estado de Payroll
            </h3>
            
            <div className="space-y-4">
              <div>
                <label htmlFor="card-new-state" className="block text-sm font-medium text-default-700 mb-2">
                  Nuevo Estado
                </label>
                <select
                  id="card-new-state"
                  value={newState}
                  onChange={(e) => setNewState(e.target.value as StatePayroll)}
className="w-full px-3 py-2.5 border border-default-300 rounded-xl bg-content2 text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
                >
                  {availableStates.map(state => (
                    <option key={state} value={state}>
                      {getStateLabel(state)}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="card-reason" className="block text-sm font-medium text-default-700 mb-2">
                  Razon del Cambio
                </label>
                <textarea
                  id="card-reason"
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
className="w-full px-3 py-2.5 border border-default-300 rounded-xl bg-content2 text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary resize-none"
                  rows={3}
                  placeholder="Describe la razon del cambio de estado..."
                />
              </div>
            </div>

            <div className="flex flex-col-reverse sm:flex-row justify-end gap-3 mt-5">
              <button
                onClick={() => setShowStateChangeModal(false)}
                className="px-4 py-2 text-default-600 bg-default-100 rounded-xl hover:bg-default-200 transition-colors font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleStateChange}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-xl hover:opacity-90 transition-opacity font-semibold disabled:opacity-50"
                disabled={isLoading || newState === payroll.state}
              >
                {isLoading ? 'Cambiando...' : 'Cambiar Estado'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
