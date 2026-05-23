// Types related to payroll history

export interface PayrollHistory {
    history_id?: string;
    identification_number: string;
    payroll_id: string;
    security_id: string;
    works_value_amount: number;
    init_date: string;
    end_date: string;
}

export interface PayrollHistoryFormData {
    identification_number: string;
    payroll_id: string;
    security_id: string;
    works_value_amount: number;
    init_date: string;
    end_date: string;
}

export interface PayrollHistoryFilters {
    identification_number?: string;
    payroll_id?: string;
    security_id?: string;
}

export interface PayrollHistorySummary {
    total_records: number;
    total_works_value: number;
    average_works_value: number;
}

export interface PayrollHistoryListDTO {
    payroll_histories: PayrollHistory[];
    total_count: number;
}

// Utilidades para trabajar con Money
export const createMoney = (amount: number, currency: string = 'COP'): Money => ({
    amount,
    currency
});

export interface Money {
    amount: number;
    currency: string;
}

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