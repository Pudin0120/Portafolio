// src/services/indexedDb/dbHelper.ts

const DB_NAME = "pwa-sync-db";
const DB_VERSION = 2; // Incremented to 2 to trigger onupgradeneeded and guarantee all stores exist

export const openDatabase = (): Promise<IDBDatabase> => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = () => {
      const db = request.result;

      // 1. Create "operations" store if it doesn't exist
      if (!db.objectStoreNames.contains("operations")) {
        const store = db.createObjectStore("operations", { keyPath: "id" });
        store.createIndex("status", "status", { unique: false });
        store.createIndex("entity", "entity", { unique: false });
        store.createIndex("createdAt", "createdAt", { unique: false });
        store.createIndex("updatedAt", "updatedAt", { unique: false });
      }

      // 2. Create "employee_store" if it doesn't exist
      if (!db.objectStoreNames.contains("employee_store")) {
        const store = db.createObjectStore("employee_store", { keyPath: "id" });
        store.createIndex("byRole", "role", { unique: false });
        store.createIndex("byDocType", "documentType", { unique: false });
        store.createIndex("byActive", "isActive", { unique: false });
      }

      // 3. Create "employee_metadata_store" if it doesn't exist
      if (!db.objectStoreNames.contains("employee_metadata_store")) {
        db.createObjectStore("employee_metadata_store", { keyPath: "key" });
      }
    };

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
};
