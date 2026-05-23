import { apiClient } from './apiClient';
import {
  Work,
  WorksResponse,
  CreateWorkRequest,
  AddProductToWorkRequest,
  StartWorkResponseDTO,
  DeliverWorkResponseDTO,
  TasksHierarchyResponse,
} from '@/types/works';

const API_BASE_URL: string = import.meta.env.VITE_API_URL;

export const workService = {
  /**
   * Gets all works
   */
  async getWorks(): Promise<WorksResponse> {
    return apiClient.get<WorksResponse>(`${API_BASE_URL}/works/`);
  },

  /**
   * Gets works with optional filters
   */
  async getWorksByState(
    state?: string,
    clientIdentification?: string
  ): Promise<WorksResponse> {
    const params = new URLSearchParams();
    if (state) params.append('state', state);
    if (clientIdentification) params.append('client_identification', clientIdentification);
    
    const queryString = params.toString();
    const url = queryString ? `${API_BASE_URL}/works/?${queryString}` : `${API_BASE_URL}/works/`;
    
    return apiClient.get<WorksResponse>(url);
  },

  /**
   * Gets a specific work
   */
  async getWorkById(workId: string): Promise<Work> {
    return apiClient.get<Work>(`${API_BASE_URL}/works/${workId}`);
  },

  /**
   * Creates a new work in DRAFT status
   */
  async createWork(workData: CreateWorkRequest): Promise<Work> {
    // Preparar los datos para enviar, asegurando tipos correctos
    const payload = {
      client_identification: workData.client_identification,
      work_name: workData.work_name,
      description: workData.description || null,
      tax: workData.tax ?? 0,
      end_aprox_delivery_date: workData.end_aprox_delivery_date ? workData.end_aprox_delivery_date + ':00Z' : null,
      deposit_amount: workData.deposit_amount !== undefined && workData.deposit_amount !== null ? Number(workData.deposit_amount) : null,
    };
    
    return apiClient.post<Work>(`${API_BASE_URL}/works/`, payload);
  },

  /**
   * Adds a product to a work
   */
  async addProductToWork(
    workId: string,
    productData: AddProductToWorkRequest
  ): Promise<any> {
    console.log(' POST /works/{workId}/products', { productData });
    const response = await apiClient.post<any>(
      `${API_BASE_URL}/works/${workId}/products`,
      productData
    );
    console.log(' Response:', response);
    return response;
  },

  /**
   * Removes a product from a work
   */
  async removeProductFromWork(workId: string, productId: string): Promise<void> {
    return apiClient.delete<void>(
      `${API_BASE_URL}/works/${workId}/products/${productId}`
    );
  },

  /**
   * Changes the execution order of a product
   */
  async updateProductOrder(
    workId: string,
    productId: string,
    newOrder: number
  ): Promise<any> {
    return apiClient.patch<any>(
      `${API_BASE_URL}/works/${workId}/products/${productId}/order?new_order=${newOrder}`,
      {}
    );
  },

  /**
   * Alias para updateProductOrder (compatibilidad)
   */
  async reorderProduct(
    workId: string,
    productId: string,
    newOrder: number
  ): Promise<any> {
    return this.updateProductOrder(workId, productId, newOrder);
  },

  /**
   * Generates a quotation for the work
   */
  async generateQuote(workId: string): Promise<Work> {
    return apiClient.post<Work>(`${API_BASE_URL}/works/${workId}/quote`, {});
  },

  /**
   * Starts the work
   */
  async startWork(workId: string): Promise<StartWorkResponseDTO> {
    return apiClient.post<StartWorkResponseDTO>(`${API_BASE_URL}/works/${workId}/start`, {});
  },

  /**
   * Marks the work as delivered
   */
  async deliverWork(workId: string): Promise<DeliverWorkResponseDTO> {
    return apiClient.post<DeliverWorkResponseDTO>(`${API_BASE_URL}/works/${workId}/deliver`, {});
  },

  /**
   * Gets the tasks for a work
   */
  async getWorkTasks(workId: string): Promise<any> {
    return apiClient.get<any>(`${API_BASE_URL}/works/${workId}/tasks`);
  },

  /**
   * Gets the task hierarchy grouped by composite products
   */
  async getTasksHierarchy(workId: string): Promise<TasksHierarchyResponse> {
    return apiClient.get<TasksHierarchyResponse>(`${API_BASE_URL}/works/${workId}/tasks/hierarchy`);
  },

  /**
   * Gets the completion percentage of a work
   */
  async getWorkCompletion(workId: string): Promise<any> {
    return apiClient.get<any>(`${API_BASE_URL}/works/${workId}/completion`);
  },

  /**
   * Deletes a work from the database
   * Only works in DRAFT or QUOTED status can be deleted
   */
  async deleteWork(workId: string): Promise<void> {
    return apiClient.delete<void>(`${API_BASE_URL}/works/${workId}`);
  },
};

export type { AddProductToWorkRequest } from '@/types/works';
