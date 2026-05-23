import React, { useState } from 'react';
import {
  PayrollFormData,
  ContractType,
  createMoney,
  getContractTypeLabel,
  formatMoney,
  isServiceProvision
} from '../../types/payroll';

interface PayrollFormProps {
  onSubmit: (data: PayrollFormData) => void;
  onCancel: () => void;
  initialData?: Partial<PayrollFormData>;
  isLoading?: boolean;
  employees?: Array<{ id: string; name: string; identification_number: string }>;
}

export const PayrollForm: React.FC<PayrollFormProps> = ({
  onSubmit,
  onCancel,
  initialData,
  isLoading = false,
  employees = []
}) => {
  const [formData, setFormData] = useState<PayrollFormData>({
    identification_number: initialData?.identification_number || '',
    contract_type: initialData?.contract_type || ContractType.FIXED_TERM,
    base_salary: initialData?.base_salary || createMoney(0),
    start_date: initialData?.start_date || new Date().toISOString().split('T')[0],
    end_date: initialData?.end_date || ''
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  
  // Estado local para el valor del input de salario (permite estar vacio)
  const [salaryInputValue, setSalaryInputValue] = useState<string>(
    initialData?.base_salary?.amount ? String(initialData.base_salary.amount) : ''
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validaciones
    const newErrors: Record<string, string> = {};

    if (!formData.identification_number) {
      newErrors.employee_id = 'Debe seleccionar un empleado (number de identificacion).';
    }

    if (!formData.start_date) {
      newErrors.start_date = 'La fecha de inicio es requerida';
    }

    if (formData.contract_type === ContractType.FIXED_TERM && !formData.end_date) {
      newErrors.end_date = 'La fecha de fin es requerida para contratos a termino fijo';
    }

    if (formData.end_date && formData.start_date && new Date(formData.end_date) <= new Date(formData.start_date)) {
      newErrors.end_date = 'La fecha de fin debe ser posterior a la fecha de inicio';
    }

    if (isServiceProvision(formData.contract_type) && formData.base_salary.amount > 0) {
      newErrors.base_salary = 'Los contratos de prestacion de servicios no pueden tener salario base';
    }

    if (formData.base_salary.amount < 0) {
      newErrors.base_salary = 'El salario base no puede ser negativo';
    }

    setErrors(newErrors);

    if (Object.keys(newErrors).length === 0) {
      //  PASO DE MAPEO CRITICO: Transformar formData al formato DTO del Backend
      const payrollCreateDTO = {
        identification_number: formData.identification_number,
        contract_type: formData.contract_type,
        //  SOLUCION 1: EXTRAER SOLO EL NUMERO DEL OBJETO MONEY
        base_salary_amount: formData.base_salary.amount,
        start_date: formData.start_date,
        end_date: formData.end_date || undefined, // Enviar undefined o null si es opcional y esta vacio
      };

      //  SOLUCION 2: Enviar el DTO mapeado en lugar del formData completo
      onSubmit(payrollCreateDTO as unknown as PayrollFormData);
    }
  };

  const handleInputChange = <K extends keyof PayrollFormData>(
    field: K,
    value: PayrollFormData[K]
  ) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Si cambia el tipo de contract a prestacion de servicios, limpiar el salario
    if (field === 'contract_type' && isServiceProvision(value as ContractType)) {
      setSalaryInputValue('');
      setFormData(prev => ({ ...prev, base_salary: createMoney(0) }));
    }
    
    // Limpiar error del campo cuando el user empiece a escribir
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleMoneyChange = (value: string) => {
    setSalaryInputValue(value);
    
    // Actualizar formData solo si hay un valor numerico valid
    const amount = value === '' ? 0 : parseFloat(value);
    if (!isNaN(amount)) {
      handleInputChange('base_salary', createMoney(amount, 'COP'));
    }
  };

  return (
    <div className="bg-content1 border border-divider rounded-xl shadow-sm p-4 md:p-6">
      <h2 className="text-xl md:text-2xl font-bold text-foreground mb-6">
        {initialData ? 'Edit Payroll' : 'Create Nueva Payroll'}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Empleado */}
        <div>
          <label htmlFor="pf-employee" className="block text-sm font-medium text-default-700 mb-2">
            Empleado *
          </label>
          <select
            id="pf-employee"
            value={formData.identification_number}
            onChange={(e) => {
              handleInputChange('identification_number', e.target.value);
            }}
className={`w-full px-3 py-2.5 border rounded-xl bg-content2 text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary transition-all ${errors.employee_id ? 'border-danger-500' : 'border-default-300'}`}
            disabled={isLoading}
          >
            <option value="">Seleccione un empleado</option>
            {employees.map(employee => (
              <option key={employee.identification_number} value={employee.identification_number}>
                {employee.name} - {employee.identification_number}
              </option>
            ))}
          </select>
          {errors.employee_id && (
            <p className="mt-1 text-sm text-danger-600">{errors.employee_id}</p>
          )}
        </div>

        {/* Tipo de Contract */}
        <div>
          <label htmlFor="pf-contract-type" className="block text-sm font-medium text-default-700 mb-2">
            Tipo de Contract *
          </label>
          <select
            id="pf-contract-type"
            value={formData.contract_type}
            onChange={(e) => handleInputChange('contract_type', e.target.value as ContractType)}
className="w-full px-3 py-2.5 border border-default-300 rounded-xl bg-content2 text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary transition-all"
            disabled={isLoading}
          >
            {Object.values(ContractType).map(type => (
              <option key={type} value={type}>
                {getContractTypeLabel(type)}
              </option>
            ))}
          </select>
        </div>

        {/* Fechas */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Fecha de Inicio */}
          <div>
            <label htmlFor="pf-start-date" className="block text-sm font-medium text-default-700 mb-2">
              Fecha de Inicio *
            </label>
            <input
              id="pf-start-date"
              type="date"
              value={formData.start_date}
              onChange={(e) => handleInputChange('start_date', e.target.value)}
className={`w-full px-3 py-2.5 border rounded-xl bg-content2 text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary transition-all ${errors.start_date ? 'border-danger-500' : 'border-default-300'}`}
              disabled={isLoading}
            />
            {errors.start_date && (
              <p className="mt-1 text-sm text-danger-600">{errors.start_date}</p>
            )}
          </div>

          {/* Fecha de Fin */}
          <div>
            <label htmlFor="pf-end-date" className="block text-sm font-medium text-default-700 mb-2">
              Fecha de Fin {formData.contract_type === ContractType.FIXED_TERM && '*'}
            </label>
            <input
              id="pf-end-date"
              type="date"
              value={formData.end_date || ''}
              onChange={(e) => handleInputChange('end_date', e.target.value)}
className={`w-full px-3 py-2.5 border rounded-xl bg-content2 text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary transition-all disabled:opacity-50 ${errors.end_date ? 'border-danger-500' : 'border-default-300'}`}
              disabled={isLoading || formData.contract_type !== ContractType.FIXED_TERM}
              min={formData.start_date}
            />
            {errors.end_date && (
              <p className="mt-1 text-sm text-danger-600">{errors.end_date}</p>
            )}
          </div>
        </div>

        {/* Salario Base */}
        <div>
          <label htmlFor="pf-salary" className="block text-sm font-medium text-default-700 mb-2">
            Salario Base (COP) *
            {isServiceProvision(formData.contract_type) && (
              <span className="text-default-400 text-xs ml-2">
                (No aplica para prestacion de servicios)
              </span>
            )}
          </label>
          <input
            id="pf-salary"
            type="number"
            min="0"
            step="1000"
            value={salaryInputValue}
            onChange={(e) => handleMoneyChange(e.target.value)}
className={`w-full px-3 py-2.5 border rounded-xl bg-content2 text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary transition-all disabled:opacity-50 ${errors.base_salary ? 'border-danger-500' : 'border-default-300'}`}
            disabled={isLoading || isServiceProvision(formData.contract_type)}
            placeholder="Ingrese el salario base"
          />
          {errors.base_salary && (
            <p className="mt-1 text-sm text-danger-600">{errors.base_salary}</p>
          )}
        </div>

        {/* Resumen */}
        <div className="bg-default-50 border border-divider p-4 rounded-xl">
          <h3 className="text-sm font-semibold text-default-700 mb-3">Resumen</h3>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-default-500">Salario Base:</span>
              <span className="font-medium text-foreground">
                {formatMoney(formData.base_salary)}
              </span>
            </div>
            <div className="flex justify-between border-t border-divider pt-2">
              <span className="text-foreground font-semibold text-sm">Total Base:</span>
              <span className="font-bold text-base text-foreground">
                {formatMoney(formData.base_salary)}
              </span>
            </div>
          </div>
        </div>

        {/* Botones */}
        <div className="flex flex-col-reverse sm:flex-row justify-end gap-3 pt-1">
          <button
            type="button"
            onClick={onCancel}
            className="px-5 py-2.5 text-default-600 bg-default-100 rounded-xl hover:bg-default-200 transition-colors font-medium disabled:opacity-50"
            disabled={isLoading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-5 py-2.5 bg-primary text-primary-foreground rounded-xl hover:opacity-90 transition-opacity font-semibold disabled:opacity-50"
            disabled={isLoading}
          >
            {isLoading ? 'Guardando...' : (initialData ? 'Actualizar' : 'Create')}
          </button>
        </div>
      </form>
    </div>
  );
};
