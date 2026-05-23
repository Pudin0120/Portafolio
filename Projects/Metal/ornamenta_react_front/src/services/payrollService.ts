import { ApiClient } from './apiClient';
import { apiClient } from './apiClient';
import {
  Payroll,
  PayrollFormData,
  PayrollFilters,
  PayrollStateChangeRequest,
  PayrollSummary,
  ContractType,
  StatePayroll,
  createMoney
} from '../types/payroll';
import { PayrollHistoryDTO } from './payrollHistoryService';
import { PayrollHistory, PayrollHistoryListDTO } from '@/types/payroll_history';
import { ServiceProvisionTasksDetail } from '@/types/payroll-tasks';

// DTOs que coinciden con el backend
interface PayrollHistoryCreateDTO {
  identification_number: string;
  payroll_id: string;
  security_id: string;
  works_value_amount: number;
  init_date: string;
  end_date: string;
}

export interface PayrollDTO {
  payroll_id: string;
  identification_number: string;
  contract_type: ContractType;
  state: StatePayroll;
  base_salary_amount: string;
  base_salary_formatted: string;
  current_period_salary?: string;
  current_period_salary_formatted?: string;
  current_period_start_date?: string;
  current_period_end_date?: string;
  is_liquidated: boolean;
  is_active: boolean;
  is_paid: boolean;
  is_cancelled: boolean;
  is_fixed_term: boolean;
  is_indefinite_term: boolean;
  is_service_provision: boolean;
}

export interface PayrollListDTO {
  payrolls: PayrollDTO[];
}

export interface PayrollCreateDTO {
  identification_number: string;
  contract_type: ContractType;
  base_salary_amount: number;
  start_date: string;
  end_date?: string;
  state?: StatePayroll;
}

export interface PayrollUpdateDTO {
  identification_number?: string;
  contract_type?: ContractType;
  state?: StatePayroll;
  base_salary_amount?: number;
  start_date?: string;
  end_date?: string;
}

export interface PayrollStatsDTO {
  total_count: number;
  by_state: {
    liquidated: number;
    active: number;
    paid: number;
    cancelled: number;
  };
  by_contract_type: {
    fixed_term: number;
    indefinite_term: number;
    service_provision: number;
  };
}

export class PayrollService {
  private baseEndpoint = '/payrolls';
  private apiClient: ApiClient;

  //  Usamos el TIPO (Clase) en el constructor
  constructor(apiClient: ApiClient) {
    this.apiClient = apiClient;
  }

  // Convertir DTO del backend a tipo interno
  private fromDTO(dto: PayrollDTO): Payroll {
    const identification_number = dto.identification_number || '';

    if (!identification_number.trim()) {
      console.warn('fromDTO: PayrollDTO sin identification_number:', {
        payroll_id: dto.payroll_id
      });
    }

    return {
      payroll_id: dto.payroll_id,
      identification_number: identification_number.trim(),
      contract_type: dto.contract_type,
      state: dto.state,
      base_salary: createMoney(parseFloat(dto.base_salary_amount)),
      base_salary_formatted: dto.base_salary_formatted,
      current_period_salary: dto.current_period_salary ? parseFloat(dto.current_period_salary) : undefined,
      current_period_salary_formatted: dto.current_period_salary_formatted,
      current_period_start_date: dto.current_period_start_date,
      current_period_end_date: dto.current_period_end_date,
      start_date: dto.current_period_start_date || '',
      end_date: dto.current_period_end_date,
      is_liquidated: dto.is_liquidated,
      is_active: dto.is_active,
      is_paid: dto.is_paid,
      is_cancelled: dto.is_cancelled,
      is_fixed_term: dto.is_fixed_term,
      is_indefinite_term: dto.is_indefinite_term,
      is_service_provision: dto.is_service_provision,
      _domain_events: []
    };
  }


  // Convertir tipo interno a DTO del backend
  private toCreateDTO(data: PayrollFormData): PayrollCreateDTO {
    return {
      contract_type: data.contract_type,
      base_salary_amount: data.base_salary.amount,
      identification_number: data.identification_number,
      start_date: data.start_date,
      end_date: data.end_date,
      state: StatePayroll.ACTIVE // Estado por defecto
    };
  }

  private toUpdateDTO(data: PayrollFormData): PayrollUpdateDTO {
    return {
      identification_number: data.identification_number,
      contract_type: data.contract_type,
      base_salary_amount: data.base_salary.amount,
      start_date: data.start_date,
      end_date: data.end_date
    };
  }

  async getPayrolls(filters?: PayrollFilters): Promise<Payroll[]> {
    try {
      const params = new URLSearchParams();
      if (filters?.contract_type) params.append('contract_type', filters.contract_type);
      if (filters?.state) params.append('state', filters.state);

      const endpoint = params.toString()
        ? `${this.baseEndpoint}/?${params.toString()}`
        : `${this.baseEndpoint}/`;

      const response = await this.apiClient.get<{ payrolls: any[] }>(endpoint);

      const fixedPayrolls = await Promise.all(
        response.payrolls.map(async dto => {
          let identification_number = dto.identification_number?.trim() || '';

          // Si no hay identification_number, intentar obtener del historial
          if (!identification_number) {
            try {
              const history = await this.getPayrollHistory(dto.payroll_id);
              if (history.length > 0) {
                identification_number = history[0].identification_number || '';
                if (identification_number) {
                  console.log(
                    'getPayrolls: Usando identification_number desde PayrollHistory para payroll:',
                    dto.payroll_id
                  );
                }
              }
            } catch (err: any) {
              console.warn(`getPayrolls: No se pudo obtener historial para payroll ${dto.payroll_id}:`, err.message);
            }
          }

          if (!identification_number) {
            console.warn('getPayrolls: PayrollDTO sin identification_number ni historial:', { payroll_id: dto.payroll_id });
          }

          return { ...dto, identification_number };
        })
      );

      return fixedPayrolls.map(dto => this.fromDTO(dto));
    } catch (error) {
      console.error('Error obteniendo payrolls:', error);
      throw error;
    }
  }

  // Obtener una payroll especifica
  async getPayrollById(payrollId: string): Promise<Payroll> {
    try {
      const response: PayrollDTO = await apiClient.get(`${this.baseEndpoint}/${payrollId}`);
      return this.fromDTO(response);
    } catch (error) {
      console.error('Error obteniendo payroll:', error);
      throw error;
    }
  }

  // Create new payroll
  async createPayroll(data: any): Promise<PayrollDTO> {
    try {
      const response = await this.apiClient.post('/payrolls/', data);
      return response as PayrollDTO;
    } catch (error) {
      console.error("Error creando payroll:", error);
      throw error;
    }
  }

  // Actualizar payroll existente
  async updatePayroll(payrollId: string, payrollData: PayrollFormData): Promise<Payroll> {
    try {
      const updateDTO = this.toUpdateDTO(payrollData);
      const response: PayrollDTO = await apiClient.patch(`${this.baseEndpoint}/${payrollId}`, updateDTO);
      return this.fromDTO(response);
    } catch (error) {
      console.error('Error actualizando payroll:', error);
      throw error;
    }
  }

  // Delete payroll
  async deletePayroll(payrollId: string): Promise<void> {
    try {
      await apiClient.delete(`${this.baseEndpoint}/${payrollId}`);
    } catch (error) {
      console.error('Error eliminando payroll:', error);
      throw error;
    }
  }

  // Cambiar estado de payroll
  async changePayrollState(payrollId: string, newState: StatePayroll, reason: string): Promise<Payroll> {
    try {
      // Intentar primero con el endpoint especifico para cambio de estado con razon
      try {
        const response: PayrollDTO = await apiClient.post(
          `${this.baseEndpoint}/${payrollId}/change-state`,
          {
            new_state: newState,
            reason: reason
          }
        );
        return this.fromDTO(response);
      } catch (specificEndpointError) {
        // Si falla, intentar con PATCH estandar incluyendo la razon
        console.log('Endpoint especifico no disponible, usando PATCH estandar');
        const updateDTO: PayrollUpdateDTO & { reason?: string } = {
          state: newState,
          reason: reason
        };
        const response: PayrollDTO = await apiClient.patch(`${this.baseEndpoint}/${payrollId}`, updateDTO);
        return this.fromDTO(response);
      }
    } catch (error) {
      console.error('Error cambiando estado de payroll:', error);
      throw error;
    }
  }

  // Obtener payrolls por tipo de contract
  async getPayrollsByContractType(contractType: ContractType): Promise<Payroll[]> {
    try {
      const response: PayrollListDTO = await apiClient.get(`${this.baseEndpoint}/contract-type/${contractType}`);
      return response.payrolls.map(dto => this.fromDTO(dto));
    } catch (error) {
      console.error('Error obteniendo payrolls por tipo de contract:', error);
      throw error;
    }
  }

  // Obtener payrolls por estado
  async getPayrollsByState(state: StatePayroll): Promise<Payroll[]> {
    try {
      const response: PayrollListDTO = await apiClient.get(`${this.baseEndpoint}/state/${state}`);
      return response.payrolls.map(dto => this.fromDTO(dto));
    } catch (error) {
      console.error('Error obteniendo payrolls por estado:', error);
      throw error;
    }
  }

  // Obtener payrolls liquidadas
  async getLiquidatedPayrolls(): Promise<Payroll[]> {
    try {
      const response: PayrollListDTO = await apiClient.get(`${this.baseEndpoint}/liquidated/`);
      return response.payrolls.map(dto => this.fromDTO(dto));
    } catch (error) {
      console.error('Error obteniendo payrolls liquidadas:', error);
      throw error;
    }
  }

  // Obtener payrolls activas
  async getActivePayrolls(): Promise<Payroll[]> {
    try {
      const response: PayrollListDTO = await apiClient.get(`${this.baseEndpoint}/active/`);
      return response.payrolls.map(dto => this.fromDTO(dto));
    } catch (error) {
      console.error('Error obteniendo payrolls activas:', error);
      throw error;
    }
  }

  // Obtener payrolls pagadas
  async getPaidPayrolls(): Promise<Payroll[]> {
    try {
      const response: PayrollListDTO = await apiClient.get(`${this.baseEndpoint}/paid/`);
      return response.payrolls.map(dto => this.fromDTO(dto));
    } catch (error) {
      console.error('Error obteniendo payrolls pagadas:', error);
      throw error;
    }
  }

  // Obtener payrolls canceladas
  async getCancelledPayrolls(): Promise<Payroll[]> {
    try {
      const response: PayrollListDTO = await apiClient.get(`${this.baseEndpoint}/cancelled/`);
      return response.payrolls.map(dto => this.fromDTO(dto));
    } catch (error) {
      console.error('Error obteniendo payrolls canceladas:', error);
      throw error;
    }
  }

  // Obtener estadisticas de payrolls
  async getPayrollStats(): Promise<PayrollStatsDTO> {
    try {
      return await apiClient.get(`${this.baseEndpoint}/stats/count`);
    } catch (error) {
      console.error('Error obteniendo estadisticas de payrolls:', error);
      throw error;
    }
  }

  // Convertir estadisticas del backend a resumen interno
  async getPayrollSummary(): Promise<PayrollSummary> {
    try {
      const stats = await this.getPayrollStats();

      return {
        total_payrolls: stats.total_count,
        total_amount: createMoney(0), // El backend no proporciona el monto total
        by_state: {
          [StatePayroll.LIQUIDATED]: stats.by_state.liquidated,
          [StatePayroll.ACTIVE]: stats.by_state.active,
          [StatePayroll.PAID]: stats.by_state.paid,
          [StatePayroll.CANCELLED]: stats.by_state.cancelled
        },
        by_contract_type: {
          [ContractType.FIXED_TERM]: stats.by_contract_type.fixed_term,
          [ContractType.INDEFINITE_TERM]: stats.by_contract_type.indefinite_term,
          [ContractType.SERVICE_PROVISION]: stats.by_contract_type.service_provision
        }
      };
    } catch (error) {
      console.error('Error obteniendo resumen de payrolls:', error);
      throw error;
    }
  }

  // Obtener el historial de una payroll por payroll_id
  async getPayrollHistory(payrollId: string): Promise<PayrollHistory[]> {
    try {
      // OK Usar el endpoint correcto con query parameter
      const endpoint = `/payroll-histories/?payroll_id=${payrollId}`;
      const response: PayrollHistoryListDTO = await this.apiClient.get(endpoint);
      
      // Verificar que la respuesta tenga el array esperado
      if (!response || !response.payroll_histories) {
        console.warn(`No se encontro historial para payroll ${payrollId}`);
        return [];
      }
      
      return response.payroll_histories;
    } catch (error: any) {
      // Si es un 404, significa que no hay historial aun (es valid para payrolls nuevos)
      if (error.status === 404) {
        console.log(`No hay historial aun para payroll ${payrollId} (esperado para payrolls nuevos)`);
        return [];
      }
      
      console.error(`Error obteniendo historial de payroll ${payrollId}:`, error);
      return [];
    }
  }

  /**
   * Obtener el detalle de tasks para payrolls de prestacion de servicios
   * Solo funciona para payrolls con contract_type = SERVICE_PROVISION
   */
  async getServiceProvisionTasks(payrollId: string): Promise<ServiceProvisionTasksDetail> {
    try {
      // Agregar timestamp para evitar cache del navegador
      const timestamp = Date.now();
      const endpoint = `${this.baseEndpoint}/${payrollId}/service-provision-tasks?t=${timestamp}`;
      const response: ServiceProvisionTasksDetail = await this.apiClient.get(endpoint);
      return response;
    } catch (error: any) {
      throw error;
    }
  }
}

export const payrollService = new PayrollService(apiClient);
