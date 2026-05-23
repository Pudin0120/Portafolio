export type DocumentType = 'CC' | 'CE' | 'NIT';

export interface Client {
  identification_number: string;
  document_type: DocumentType;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  address: string;
}

export interface ClientsResponse {
  clients: Client[];
  total: number;
}

export interface CreateClientRequest {
  identification_number: string;
  document_type: DocumentType;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  address: string;
}

export interface UpdateClientRequest {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  address?: string;
}
