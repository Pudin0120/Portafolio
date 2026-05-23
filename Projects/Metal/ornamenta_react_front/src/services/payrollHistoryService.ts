import { apiClient } from './apiClient';
import {
    PayrollHistory,
    PayrollHistoryFormData,
    PayrollHistoryFilters,
    PayrollHistoryListDTO
} from '../types/payroll_history';

export interface PayrollHistoryDTO {
    history_id: string;
    identification_number: string;
    payroll_id: string;
    security_id: string;
    works_value_amount: number;
    init_date: string;
    end_date: string;
}

interface PayrollHistoryCreateDTO {
    identification_number: string;
    payroll_id: string;
    security_id: string;
    works_value_amount: number;
    init_date: string;
    end_date: string;
}

interface PayrollHistoryUpdateDTO {
    identification_number?: string;
    payroll_id?: string;
    security_id?: string;
    works_value_amount?: number;
    init_date?: string;
    end_date?: string;
}

class PayrollHistoryService {
    private baseEndpoint = '/payroll-histories';

    // Convertir DTO del backend a tipo interno
    private fromDTO(dto: PayrollHistoryDTO): PayrollHistory {
        return {
            history_id: dto.history_id,
            identification_number: dto.identification_number,
            payroll_id: dto.payroll_id,
            security_id: dto.security_id,
            works_value_amount: dto.works_value_amount,
            init_date: dto.init_date,
            end_date: dto.end_date,
        };
    }

    // Convertir tipo interno a DTO para create
    private toCreateDTO(data: PayrollHistoryFormData): PayrollHistoryCreateDTO {
        return { ...data };
    }

    // Convertir tipo interno a DTO para actualizar
    private toUpdateDTO(data: PayrollHistoryFormData): PayrollHistoryUpdateDTO {
        return { ...data };
    }

    // Obtener todas las historias con filtros opcionales
    async getPayrollHistories(filters?: PayrollHistoryFilters): Promise<PayrollHistory[]> {
        try {
            const params = new URLSearchParams();

            if (filters?.identification_number) params.append('identification_number', filters.identification_number);
            if (filters?.payroll_id) params.append('payroll_id', filters.payroll_id);
            if (filters?.security_id) params.append('security_id', filters.security_id);

            const endpoint = params.toString() ? `${this.baseEndpoint}/?${params.toString()}` : `${this.baseEndpoint}/`;
            const response: PayrollHistoryListDTO = await apiClient.get(endpoint);
            console.log('RESPONSE API:', response);
            const histories = response?.payroll_histories ?? [];
            return histories.map(dto => this.fromDTO(dto as PayrollHistoryDTO));
        } catch (error) {
            console.error('Error obteniendo historias de payroll:', error);
            throw error;
        }
    }

    // Obtener historia por ID
    async getPayrollHistoryById(historyId: string): Promise<PayrollHistory> {
        try {
            const response: PayrollHistoryDTO = await apiClient.get(`${this.baseEndpoint}/${historyId}`);
            return this.fromDTO(response);
        } catch (error) {
            console.error('Error obteniendo historia de payroll:', error);
            throw error;
        }
    }

    // Create history
    async createPayrollHistory(historyData: PayrollHistoryFormData): Promise<PayrollHistory> {
        try {
            const createDTO = this.toCreateDTO(historyData);
            const response: PayrollHistoryDTO = await apiClient.post(`${this.baseEndpoint}/`, createDTO);
            return this.fromDTO(response);
        } catch (error) {
            console.error('Error creando historia de payroll:', error);
            throw error;
        }
    }

    // Actualizar historia
    async updatePayrollHistory(historyId: string, historyData: PayrollHistoryFormData): Promise<PayrollHistory> {
        try {
            const updateDTO = this.toUpdateDTO(historyData);
            const response: PayrollHistoryDTO = await apiClient.patch(`${this.baseEndpoint}/${historyId}`, updateDTO);
            return this.fromDTO(response);
        } catch (error) {
            console.error('Error actualizando historia de payroll:', error);
            throw error;
        }
    }

    // Delete history
    async deletePayrollHistory(historyId: string): Promise<void> {
        try {
            await apiClient.delete(`${this.baseEndpoint}/${historyId}`);
        } catch (error) {
            console.error('Error eliminando historia de payroll:', error);
            throw error;
        }
    }

    // Obtener historias filtrando por identification_number
    async getHistoriesByIdentificationNumber(identificationNumber: string): Promise<PayrollHistory[]> {
        return this.getPayrollHistories({ identification_number: identificationNumber });
    }

    // Obtener historias filtrando por payroll_id
    async getHistoriesByPayroll(payrollId: string): Promise<PayrollHistory[]> {
        return this.getPayrollHistories({ payroll_id: payrollId });
    }

    // Obtener estadisticas simples
    async getPayrollHistoryStats(): Promise<{ total_count: number }> {
        try {
            return await apiClient.get(`${this.baseEndpoint}/stats/count`);
        } catch (error) {
            console.error('Error obteniendo estadisticas:', error);
            throw error;
        }
    }
}

export const payrollHistoryService = new PayrollHistoryService();
