// Types related to users and authentication

export interface IUserData {
  identification_number: string;
  document_type: string;
  first_name: string;
  last_name: string;
  email: string;
  state: string;
  firebase_uid: string;
  phone: string;
  role: string;
  password: string;
}

// Role is now dynamic and can be any string or null
export type Role = string | null;

export interface EmployeeFormState {
  formData: IUserData;
  isLoading: boolean;
}
