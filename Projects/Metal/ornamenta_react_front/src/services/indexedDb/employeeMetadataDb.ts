// src/services/indexedDb/employeeMetadataDb.ts

type Role = {
  id: string;
  label: string;
};

type DocumentType = {
  id: string;
  label: string;
};

export interface EmployeeMetadata {
  roles: Role[];
  document_types: DocumentType[];
}

import { openDatabase } from "./dbHelper";

const STORE_NAME = "employee_metadata_store";

type TransactionMode = "readonly" | "readwrite";

const withStore = async <T>(
  mode: TransactionMode,
  callback: (store: IDBObjectStore) => IDBRequest<T>
): Promise<T> => {
  const db = await openDatabase();
  return new Promise<T>((resolve, reject) => {
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

/** Set the metadata (overwrite existing). */
export const setEmployeeMetadata = async (
  metadata: EmployeeMetadata
): Promise<void> => {
  await withStore("readwrite", (store) =>
    store.put({ key: "metadata", ...metadata })
  );
};

/** Retrieve cached metadata, or undefined if not present. */
export const getEmployeeMetadata = async (): Promise<EmployeeMetadata | undefined> => {
  const result = await withStore("readonly", (store) =>
    store.get("metadata")
  );
  // The returned object includes the `key` field; strip it.
  if (result && typeof result === "object" && "key" in result) {
    const { key, ...meta } = result as any;
    return meta as EmployeeMetadata;
  }
  return undefined;
};

/** Clear stored metadata. */
export const clearEmployeeMetadata = async (): Promise<void> => {
  await withStore("readwrite", (store) => store.clear());
};

export type { Role, DocumentType };
