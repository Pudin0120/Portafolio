import { useEffect, useState } from "react";
import { inventoryService } from "@/services/inventoryService";
import type { InventoryLevel, InventoryMovement } from "@/types/inventory";

interface UseInventoryResult {
  levels: InventoryLevel[];
  selectedLevel: InventoryLevel | null;
  movements: InventoryMovement[];
  loadingLevels: boolean;
  loadingDetail: boolean;
  error: string | null;
  selectedMaterialId: string;
  setSelectedMaterialId: (materialId: string) => void;
  refresh: () => Promise<void>;
}

export function useInventory(): UseInventoryResult {
  const [levels, setLevels] = useState<InventoryLevel[]>([]);
  const [selectedMaterialId, setSelectedMaterialId] = useState("");
  const [movements, setMovements] = useState<InventoryMovement[]>([]);
  const [loadingLevels, setLoadingLevels] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState(0);
  const selectedLevel = levels.find((level) => level.material_id === selectedMaterialId) ?? null;
  const visibleMovements = selectedMaterialId ? movements : [];

  useEffect(() => {
    let isMounted = true;

    const loadLevels = async () => {
      setLoadingLevels(true);
      setError(null);

      try {
        const data = await inventoryService.getInventoryLevels();

        if (!isMounted) {
          return;
        }

        setLevels(data);

        const hasSelection = data.some(
          (level) => level.material_id === selectedMaterialId,
        );

        if (data.length > 0 && (!selectedMaterialId || !hasSelection)) {
          setSelectedMaterialId(data[0].material_id);
        } else if (data.length === 0) {
          setSelectedMaterialId("");
        }
      } catch (requestError) {
        if (isMounted) {
          setError(
            requestError instanceof Error
              ? requestError.message
              : "No se pudieron cargar las existencias.",
          );
        }
      } finally {
        if (isMounted) {
          setLoadingLevels(false);
        }
      }
    };

    void loadLevels();

    return () => {
      isMounted = false;
    };
  }, [refreshToken, selectedMaterialId]);

  useEffect(() => {
    if (!selectedMaterialId) {
      return;
    }

    let isMounted = true;

    const loadDetail = async () => {
      setLoadingDetail(true);
      setError(null);

      try {
        const movementHistory = await inventoryService.getInventoryMovementsByMaterial(selectedMaterialId);

        if (!isMounted) {
          return;
        }

        setMovements(movementHistory);
      } catch (requestError) {
        if (isMounted) {
          setError(
            requestError instanceof Error
              ? requestError.message
              : "No se pudo cargar el detalle del material.",
          );
        }
      } finally {
        if (isMounted) {
          setLoadingDetail(false);
        }
      }
    };

    void loadDetail();

    return () => {
      isMounted = false;
    };
  }, [selectedMaterialId, refreshToken]);

  const refresh = async (): Promise<void> => {
    setRefreshToken((current) => current + 1);
  };

  return {
    levels,
    selectedLevel,
    movements: visibleMovements,
    loadingLevels,
    loadingDetail,
    error,
    selectedMaterialId,
    setSelectedMaterialId,
    refresh,
  };
}
