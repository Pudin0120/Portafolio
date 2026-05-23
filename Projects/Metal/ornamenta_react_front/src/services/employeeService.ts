// src/services/employeeService.ts
import { apiClient } from "./apiClient";
import { addEmployee, clearEmployees, getAllEmployees, getEmployeeById as dbGetEmployeeById } from "@/services/indexedDb/employeeDb";

export interface Employee {
  identification_number: string;
  first_name: string;
  last_name: string;
  email: string;
  state: string; // "A" active, "I" inactive
  phone: string;
  firebase_uid: string;
  role: string;
  document_type: string;
}

/** Offlinefirst service for employee data.
 * - When online: fetch from backend then sync to IndexedDB.
 * - When offline: serve from IndexedDB cache.
 * - Mutations use apiClient with `offlineOperation` payload so they are queued when offline.
 */
export const employeeService = {
  /** Get all employees. */
  async getEmployees(options: { forceRefresh?: boolean } = {}): Promise<Employee[]> {
    const isOnline = typeof navigator !== "undefined" ? navigator.onLine : true;
    if (!isOnline && !options.forceRefresh) {
      const cached = await getAllEmployees();
      return cached.map((c) => ({
        identification_number: c.identification_number,
        first_name: c.first_name,
        last_name: c.last_name,
        email: c.email,
        state: c.isActive ? "A" : "I",
        phone: c.phone,
        firebase_uid: c.firebase_uid,
        role: c.role,
        document_type: c.documentType,
      } as Employee));
    }
    // Online - fetch from API
    const response = await apiClient.get<any>("/admin/users");

    // Robust array extraction helper
    const extractEmployees = (res: any): any[] => {
      if (!res) return [];
      if (Array.isArray(res)) return res;
      if (res.users && Array.isArray(res.users)) return res.users;
      if (res.data && Array.isArray(res.data)) return res.data;
      if (res.data && res.data.users && Array.isArray(res.data.users)) return res.data.users;
      
      // Fallback: first field that is an array
      const possibleArray = Object.values(res).find((val) => Array.isArray(val));
      if (possibleArray) return possibleArray as any[];
      
      if (res.data && typeof res.data === "object") {
        const possibleDataArray = Object.values(res.data).find((val) => Array.isArray(val));
        if (possibleDataArray) return possibleDataArray as any[];
      }
      return [];
    };

    const rawEmployees = extractEmployees(response);

    // Normalize keys to support snake_case/camelCase and robust fallback properties
    const normalizedEmployees: Employee[] = rawEmployees.map((emp: any) => {
      const stateVal = emp.state || emp.status;
      const isActiveVal = emp.isActive || emp.is_active;
      const isAct = stateVal === "A" || stateVal === "active" || isActiveVal === true;
      
      return {
        identification_number: String(emp.identification_number || emp.identificationNumber || emp.id || ""),
        first_name: emp.first_name || emp.firstName || "",
        last_name: emp.last_name || emp.lastName || "",
        email: emp.email || "",
        state: isAct ? "A" : "I",
        phone: emp.phone || "",
        firebase_uid: emp.firebase_uid || emp.firebaseUid || "",
        role: emp.role || "",
        document_type: emp.document_type || emp.documentType || "",
      };
    });

    // Sync cache
    await clearEmployees();
    for (const emp of normalizedEmployees) {
      await addEmployee({
        id: emp.identification_number,
        identification_number: emp.identification_number,
        first_name: emp.first_name,
        last_name: emp.last_name,
        email: emp.email,
        role: emp.role,
        documentType: emp.document_type,
        isActive: emp.state === "A",
        createdAt: Date.now(),
        updatedAt: Date.now(),
        phone: emp.phone,
        firebase_uid: emp.firebase_uid,
      });
    }
    return normalizedEmployees;
  },

  /** Get a single employee by ID. */
  async getEmployeeById(identification_number: string): Promise<Employee> {
    const isOnline = typeof navigator !== "undefined" ? navigator.onLine : true;
    if (!isOnline) {
      const cached = await dbGetEmployeeById(identification_number);
      if (!cached) throw new Error("Employee not found in offline cache");
      return {
        identification_number: cached.identification_number,
        first_name: cached.first_name,
        last_name: cached.last_name,
        email: cached.email,
        state: cached.isActive ? "A" : "I",
        phone: cached.phone,
        firebase_uid: cached.firebase_uid,
        role: cached.role,
        document_type: cached.documentType,
      } as Employee;
    }
    const emp = await apiClient.get<Employee>(`/users/employees/${identification_number}`);
    // Update cache
    await addEmployee({
      id: emp.identification_number,
      identification_number: emp.identification_number,
      first_name: emp.first_name,
      last_name: emp.last_name,
      email: emp.email,
      role: emp.role,
      documentType: emp.document_type,
      isActive: emp.state === "A",
      createdAt: Date.now(),
      updatedAt: Date.now(),
      phone: emp.phone,
      firebase_uid: emp.firebase_uid,
    });
    return emp;
  },

  /** Activate / deactivate employee - works offline via queued operation. */
  async toggleEmployeeState(
    identificationNumber: string,
    newState: string,
    payload: Record<string, string>
  ): Promise<unknown> {
    const operation = newState === "A" ? "activate" : "deactivate";
    return apiClient.patch(`/admin/users/${identificationNumber}/state`, payload, {
      offlineOperation: {
        entity: "employee",
        operation,
        endpoint: `/admin/users/${identificationNumber}/state`,
        method: "PATCH",
        body: payload,
      },
    });
  },

  /** Clear employee cache - used to force refresh. */
  invalidateEmployeesCache(): void {
    void clearEmployees();
  },
};


