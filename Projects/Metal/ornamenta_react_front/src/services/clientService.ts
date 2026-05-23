import { apiClient } from './apiClient';
import { Client, ClientsResponse, CreateClientRequest } from '../types/clients';

export interface UpdateClientRequest {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  address?: string;
}

export const clientService = {
  /**
   * Obtiene todos los clients
   */
  async getClients(): Promise<ClientsResponse> {
    return apiClient.get<ClientsResponse>('/clients/');
  },

  /**
   * Obtiene un client por number de identificacion
   */
  async getClientById(identificationNumber: string): Promise<Client> {
    try {
      const response = await apiClient.get<Client>(`/clients/${identificationNumber}`);
      return response;
    } catch (error) {
      console.error('Error obteniendo client:', error);
      throw error;
    }
  },

  /**
   * Crea un nuevo client
   */
  async createClient(clientData: CreateClientRequest): Promise<Client> {
    return apiClient.post<Client>('/clients/', clientData);
  },

  /**
   * Actualiza un client existente
   */
  async updateClient(identificationNumber: string, clientData: UpdateClientRequest): Promise<Client> {
    try {
      const response = await apiClient.patch<Client>(`/clients/${identificationNumber}`, clientData);
      return response;
    } catch (error) {
      console.error('Error actualizando client:', error);
      throw error;
    }
  },

  /**
   * Elimina un client
   */
  async deleteClient(identificationNumber: string): Promise<void> {
    try {
      await apiClient.delete(`/clients/${identificationNumber}`);
    } catch (error) {
      console.error('Error eliminando client:', error);
      throw error;
    }
  },
};
