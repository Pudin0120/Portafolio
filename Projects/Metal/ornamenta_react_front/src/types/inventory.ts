export const INVENTORY_MOVEMENT_TYPES = {
  PURCHASE: "PURCHASE",
  SALE: "SALE",
  ADJUSTMENT: "ADJUSTMENT",
  PRODUCTION_CONSUMPTION: "PRODUCTION_CONSUMPTION",
  RETURN: "RETURN",
} as const;

export type InventoryMovementType =
  (typeof INVENTORY_MOVEMENT_TYPES)[keyof typeof INVENTORY_MOVEMENT_TYPES];

export interface InventoryLevel {
  material_id: string;
  material_name: string;
  sku: string;
  image_url: string | null;
  quantity: string;
  warehouse_id: string | null;
  last_updated: string | null;
}

export interface InventoryMovement {
  id: string;
  material_id: string;
  quantity: string;
  type: InventoryMovementType;
  tenant_id: string;
  reference_id: string | null;
  batch_number: string | null;
  reason: string | null;
  created_at: string;
  created_by: string | null;
}

export interface CreateInventoryMovementDTO {
  material_id: string;
  quantity: number;
  type: InventoryMovementType;
  batch_number?: string | null;
  created_at?: string | null;
  reason?: string | null;
  reference_id?: string | null;
  warehouse_id?: string | null;
}
