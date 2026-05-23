// Types related to payroll

export interface Money {
  amount: number;
  currency: string;
}

export enum ContractType {
  FIXED_TERM = 'FIXED_TERM',
  INDEFINITE_TERM = 'INDEFINITE_TERM',
  SERVICE_PROVISION = 'SERVICE_PROVISION'
}

export enum StatePayroll {
  ACTIVE = 'ACTIVE',
  LIQUIDATED = 'LIQUIDATED',
  PAID = 'PAID',
  CANCELLED = 'CANCELLED'
}

export interface DomainEvent {
  event_id: string;
  occurred_at: Date;
}

export interface PayrollStateChanged extends DomainEvent {
  payroll_id: string;
  previous_state: string;
  new_state: string;
  changed_by_user_id: string;
  changed_by_user_name: string;
  reason: string;
}

export interface Payroll {
  payroll_id: string;
  identification_number: string;
  contract_type: ContractType;
  state: StatePayroll;
  base_salary: Money;
  base_salary_formatted?: string;
  current_period_salary?: number;
  current_period_salary_formatted?: string;
  current_period_start_date?: string;
  current_period_end_date?: string;
  start_date: string;
  end_date?: string;
  is_liquidated: boolean;
  is_active: boolean;
  is_paid: boolean;
  is_cancelled: boolean;
  is_fixed_term: boolean;
  is_indefinite_term: boolean;
  is_service_provision: boolean;
  _domain_events?: DomainEvent[];
}

export interface PayrollFormData {
  identification_number: string;
  contract_type: ContractType;
  base_salary: Money;
  start_date: string;
  end_date?: string;
}

export interface PayrollStateChangeRequest {
  new_state: StatePayroll;
  reason: string;
}

export interface PayrollFilters {
  contract_type?: ContractType;
  state?: StatePayroll;
  date_from?: Date;
  date_to?: Date;
}

export interface PayrollSummary {
  total_payrolls: number;
  total_amount: Money;
  by_state: Record<StatePayroll, number>;
  by_contract_type: Record<ContractType, number>;
}

// Utilidades para trabajar con Money
export const createMoney = (amount: number, currency: string = 'COP'): Money => ({
  amount,
  currency
});

export const addMoney = (a: Money, b: Money): Money => {
  if (a.currency !== b.currency) {
    throw new Error('No se pueden sumar monedas de diferentes divisas');
  }
  return createMoney(a.amount + b.amount, a.currency);
};

export const formatMoney = (money: Money): string => {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: money.currency,
  }).format(money.amount);
};

// Utilidades para trabajar con estados
export const getStateLabel = (state: StatePayroll): string => {
  const labels: Record<StatePayroll, string> = {
    [StatePayroll.ACTIVE]: 'Activa',
    [StatePayroll.LIQUIDATED]: 'Liquidada',
    [StatePayroll.PAID]: 'Pagada',
    [StatePayroll.CANCELLED]: 'Cancelada'
  };
  return labels[state];
};

export const getStateColor = (state: StatePayroll): string => {
  const colors: Record<StatePayroll, string> = {
    [StatePayroll.ACTIVE]: 'bg-orange-100 text-orange-800',
    [StatePayroll.LIQUIDATED]: 'bg-yellow-100 text-yellow-800',
    [StatePayroll.PAID]: 'bg-green-100 text-green-800',
    [StatePayroll.CANCELLED]: 'bg-red-100 text-red-800'
  };
  return colors[state];
};

// Utilities for working with contract types
export const getContractTypeLabel = (contractType: ContractType): string => {
  const labels: Record<ContractType, string> = {
    [ContractType.FIXED_TERM]: 'Fixed Term',
    [ContractType.INDEFINITE_TERM]: 'Indefinite Term',
    [ContractType.SERVICE_PROVISION]: 'Service Provision'
  };
  return labels[contractType];
};

export const isServiceProvision = (contractType: ContractType): boolean => {
  return contractType === ContractType.SERVICE_PROVISION;
};
