// src/services/indexedDb/employeeDb.ts
export interface EmployeeCache {
  id: string;
  identification_number: string;
  first_name: string;
  last_name: string;
  email: string;
  role: string;
  documentType: string;
  isActive: boolean;
  createdAt: number;
  updatedAt: number;
  phone?: string;
  firebase_uid?: string;
}

import { openDatabase } from "./dbHelper";

const STORE_NAME = "employee_store";

type TransactionMode = "readonly" | "readwrite" | "versionchange";

const withStore = async <T>(
  mode: TransactionMode,
  callback: (store: IDBObjectStore) => IDBRequest<T>
): Promise<T> => {
  const db = await openDatabase();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, mode);
    const request = callback(tx.objectStore(STORE_NAME));
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
    tx.oncomplete = () => db.close();
    tx.onerror = () => {
      db.close();
      reject(tx.error);
    };
  });
};

export const addEmployee = async (employee: EmployeeCache): Promise<void> => {
  await withStore("readwrite", (store) => store.put(employee));
};

export const updateEmployee = async (
  id: string,
  patch: Partial<EmployeeCache>
): Promise<void> => {
  const existing = await getEmployeeById(id);
  if (!existing) return;
  const updated = { ...existing, ...patch } as EmployeeCache;
  await withStore("readwrite", (store) => store.put(updated));
};

export const getAllEmployees = async (): Promise<EmployeeCache[]> => {
  return await withStore("readonly", (store) => store.getAll());
};

export const getEmployeeById = async (
  id: string
): Promise<EmployeeCache | undefined> => {
  return await withStore("readonly", (store) => store.get(id));
};

export const clearEmployees = async (): Promise<void> => {
  await withStore("readwrite", (store) => store.clear());
};
