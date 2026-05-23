import { apiClient } from "@/services/apiClient";
import type {
  CreateInventoryMovementDTO,
  InventoryLevel,
  InventoryMovement,
} from "@/types/inventory";

const INVENTORY_BASE_ENDPOINT = "/inventory";

const normalizeOptionalString = (value?: string | null): string | null => {
  if (typeof value !== "string") return value ?? null;
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
};

export const inventoryService = {
  async getInventoryLevels(): Promise<InventoryLevel[]> {
    return apiClient.get<InventoryLevel[]>(`${INVENTORY_BASE_ENDPOINT}/levels`);
  },

  async getInventoryLevelByMaterial(
    materialId: string,
  ): Promise<InventoryLevel> {
    return apiClient.get<InventoryLevel>(
      `${INVENTORY_BASE_ENDPOINT}/levels/${materialId}`,
    );
  },

  async getInventoryMovementsByMaterial(
    materialId: string,
  ): Promise<InventoryMovement[]> {
    return apiClient.get<InventoryMovement[]>(
      `${INVENTORY_BASE_ENDPOINT}/movements/${materialId}`,
    );
  },

  async createInventoryMovement(
    payload: CreateInventoryMovementDTO,
  ): Promise<InventoryMovement> {
    return apiClient.post<InventoryMovement>(
      `${INVENTORY_BASE_ENDPOINT}/movements`,
      {
        ...payload,
        batch_number: normalizeOptionalString(payload.batch_number),
        created_at: normalizeOptionalString(payload.created_at),
        reason: normalizeOptionalString(payload.reason),
        reference_id: normalizeOptionalString(payload.reference_id),
        warehouse_id: normalizeOptionalString(payload.warehouse_id),
      },
    );
  },
};
