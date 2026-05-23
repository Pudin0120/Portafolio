import { useEffect, useState } from "react";
import {
  Autocomplete,
  AutocompleteItem,
  Button,
  Chip,
  ModalBody,
  ModalFooter,
  ModalHeader,
} from "@heroui/react";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { CenteredModal } from "@components/common/CenteredModal";
import { inventoryService } from "@services/inventoryService";
import {
  INVENTORY_MOVEMENT_TYPES,
  type CreateInventoryMovementDTO,
  type InventoryLevel,
  type InventoryMovementType,
} from "@/types/inventory";

interface InventoryMovementModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  selectedMaterialId: string;
  onSubmit: (payload: CreateInventoryMovementDTO) => Promise<void>;
}

interface MovementFormState {
  materialId: string;
  type: InventoryMovementType;
  quantity: string;
  reason: string;
  batchNumber: string;
  referenceId: string;
  warehouseId: string;
  createdAt: string;
}

const MOVEMENT_TYPE_OPTIONS = [
  INVENTORY_MOVEMENT_TYPES.PURCHASE,
  INVENTORY_MOVEMENT_TYPES.SALE,
  INVENTORY_MOVEMENT_TYPES.ADJUSTMENT,
  INVENTORY_MOVEMENT_TYPES.PRODUCTION_CONSUMPTION,
  INVENTORY_MOVEMENT_TYPES.RETURN,
];

const MOVEMENT_TYPE_LABELS: Record<InventoryMovementType, string> = {
  [INVENTORY_MOVEMENT_TYPES.PURCHASE]: "Compra",
  [INVENTORY_MOVEMENT_TYPES.SALE]: "Venta",
  [INVENTORY_MOVEMENT_TYPES.ADJUSTMENT]: "Ajuste",
  [INVENTORY_MOVEMENT_TYPES.PRODUCTION_CONSUMPTION]: "Consumo de produccion",
  [INVENTORY_MOVEMENT_TYPES.RETURN]: "Devolucion",
};

const DEFAULT_FORM_STATE: MovementFormState = {
  materialId: "",
  type: INVENTORY_MOVEMENT_TYPES.PURCHASE,
  quantity: "",
  reason: "",
  batchNumber: "",
  referenceId: "",
  warehouseId: "",
  createdAt: "",
};

const signedQuantityByType = (
  type: InventoryMovementType,
  quantity: number,
): number => {
  if (type === INVENTORY_MOVEMENT_TYPES.SALE || type === INVENTORY_MOVEMENT_TYPES.PRODUCTION_CONSUMPTION) {
    return -Math.abs(quantity);
  }

  return Math.abs(quantity);
};

const movementTypeMeta = {
  [INVENTORY_MOVEMENT_TYPES.PURCHASE]: {
    label: "Compra",
    searchTerm: "Compras",
    tone: "success" as const,
    icon: ArrowUpRight,
  },
  [INVENTORY_MOVEMENT_TYPES.RETURN]: {
    label: "Devolucion",
    searchTerm: "Devoluciones",
    tone: "success" as const,
    icon: ArrowUpRight,
  },
  [INVENTORY_MOVEMENT_TYPES.SALE]: {
    label: "Venta",
    searchTerm: "Ventas",
    tone: "danger" as const,
    icon: ArrowDownRight,
  },
  [INVENTORY_MOVEMENT_TYPES.PRODUCTION_CONSUMPTION]: {
    label: "Consumo de produccion",
    searchTerm: "Consumo de produccion",
    tone: "danger" as const,
    icon: ArrowDownRight,
  },
  [INVENTORY_MOVEMENT_TYPES.ADJUSTMENT]: {
    label: "Ajuste",
    searchTerm: "Ajustes",
    tone: "warning" as const,
    icon: ArrowDownRight,
  },
} as const;

const FIELD_LABEL_CLASS = "mb-2 block text-sm font-medium text-default-600";
const FIELD_CONTROL_CLASS =
  "w-full rounded-xl border border-default-300 bg-content2 px-3 py-2.5 text-sm text-foreground shadow-sm transition-colors placeholder:text-default-400 focus:border-primary focus:outline-hidden focus:ring-2 focus:ring-primary/20";
const FIELD_SELECT_CLASS =
  "w-full rounded-xl border border-default-300 bg-content2 px-3 py-2.5 text-sm text-foreground shadow-sm transition-colors focus:border-primary focus:outline-hidden focus:ring-2 focus:ring-primary/20";

export function InventoryMovementModal({
  isOpen,
  onOpenChange,
  selectedMaterialId,
  onSubmit,
}: InventoryMovementModalProps) {
  const [form, setForm] = useState<MovementFormState>(DEFAULT_FORM_STATE);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [levels, setLevels] = useState<InventoryLevel[]>([]);
  const [loadingLevels, setLoadingLevels] = useState(false);
  const [levelsError, setLevelsError] = useState<string | null>(null);

  const materialSelectValue = form.materialId || null;
  const activeMeta = movementTypeMeta[form.type];
  const ActiveIcon = activeMeta.icon;
  const selectedLevel = levels.find((level) => level.material_id === materialSelectValue) ?? null;
  const quantityValue = Number(form.quantity);
  const normalizedQuantity = Number.isFinite(quantityValue) ? Math.abs(quantityValue) : 0;
  const signedPreviewQuantity =
    form.type === INVENTORY_MOVEMENT_TYPES.SALE ||
    form.type === INVENTORY_MOVEMENT_TYPES.PRODUCTION_CONSUMPTION
      ? -normalizedQuantity
      : normalizedQuantity;
  const previewStock = selectedLevel
    ? Number(selectedLevel.quantity || 0) + signedPreviewQuantity
    : null;
  const signedPreviewLabel = `${signedPreviewQuantity > 0 ? "+" : ""}${normalizedQuantity}`;

  const movementTypeSearchTerm = movementTypeMeta[form.type].searchTerm;

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    let isMounted = true;

    const loadLevels = async (): Promise<void> => {
      setLoadingLevels(true);
      setLevelsError(null);

      try {
        const data = await inventoryService.getInventoryLevels();

        if (!isMounted) {
          return;
        }

        setLevels(data);

        if (selectedMaterialId) {
          return { ...current, materialId: selectedMaterialId };
        }

        return current;
      } catch (requestError) {
        if (isMounted) {
          setLevelsError(
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
  }, [isOpen, selectedMaterialId]);

  const handleOpenChange = (open: boolean): void => {
    if (!open) {
      setForm(DEFAULT_FORM_STATE);
      setSubmitError(null);
      setLevels([]);
      setLevelsError(null);
    }

    onOpenChange(open);
  };

  const handleFieldChange = <K extends keyof MovementFormState>(
    key: K,
    value: MovementFormState[K],
  ): void => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const handleSubmit = async (): Promise<void> => {
    const quantityValue = Number(form.quantity);

    if (!materialSelectValue || !form.reason.trim() || !Number.isFinite(quantityValue) || quantityValue <= 0) {
      setSubmitError("Completa material, quantity positiva y motivo antes de save.");
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      await onSubmit({
        material_id: materialSelectValue,
        quantity: signedQuantityByType(form.type, quantityValue),
        type: form.type,
        reason: form.reason.trim(),
        batch_number: form.batchNumber.trim() || null,
        reference_id: form.referenceId.trim() || null,
        warehouse_id: form.warehouseId.trim() || null,
        created_at: form.createdAt ? new Date(form.createdAt).toISOString() : null,
      });

      setForm(DEFAULT_FORM_STATE);
      onOpenChange(false);
    } catch (requestError) {
      setSubmitError(
        requestError instanceof Error
          ? requestError.message
          : "No se pudo registrar el movimiento.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <CenteredModal
      isOpen={isOpen}
      onOpenChange={handleOpenChange}
      size="lg"
      scrollBehavior="inside"
      hideCloseButton={false}
    >
      {(onClose) => (
        <div className="flex h-full max-h-[calc(100dvh-2rem)] w-full min-w-0 flex-col overflow-hidden rounded-3xl border border-divider bg-content1 shadow-2xl dark:border-white/10 dark:bg-content1">
          <ModalHeader className="border-b border-divider bg-content2 px-6 py-5 dark:border-white/10 dark:bg-content2">
            <div className="flex min-w-0 w-full items-start justify-between gap-4">
              <div className="min-w-0 space-y-2">
                <h2 className="text-xl font-bold text-foreground">Nuevo movimiento</h2>
              </div>
              <Chip color={activeMeta.tone} variant="flat" startContent={<ActiveIcon className="h-4 w-4" />} className="shrink-0">
                {activeMeta.label}
              </Chip>
            </div>
          </ModalHeader>

          <ModalBody className="min-h-0 flex-1 overflow-y-scroll overflow-x-hidden px-6 py-6 [scrollbar-gutter:stable]">
            <div className="grid min-w-0 gap-4 md:grid-cols-2">
              <div className="min-w-0 md:col-span-2">
                <Autocomplete
                  label="Search material"
                  placeholder="SKU, nombre o ID..."
                  selectedKey={materialSelectValue}
                  onSelectionChange={(key) => handleFieldChange("materialId", (key as string) || "")}
                  isDisabled={loadingLevels}
                  isLoading={loadingLevels}
                  errorMessage={levelsError || undefined}
                  variant="flat"
                  size="md"
                  fullWidth
                >
                  {levels.map((level) => (
                    <AutocompleteItem
                      key={level.material_id}
                      textValue={`${level.material_name} ${level.sku}`}
                    >
                      <div className="flex items-center justify-between gap-3">
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm font-medium text-foreground">{level.material_name}</p>
                          <p className="truncate text-xs text-default-500">SKU: {level.sku}</p>
                        </div>
                        <Chip size="sm" variant="flat" className="shrink-0">
                          {level.quantity}
                        </Chip>
                      </div>
                    </AutocompleteItem>
                  ))}
                </Autocomplete>
              </div>

              <div className="min-w-0">
                <label htmlFor="inventory-type" className={FIELD_LABEL_CLASS}>
                  Tipo de movimiento
                </label>
                <select
                  id="inventory-type"
                  value={form.type}
                  onChange={(event) => {
                    handleFieldChange("type", event.target.value as InventoryMovementType);
                  }}
                  className={`${FIELD_SELECT_CLASS} min-w-0`}
                >
                  {MOVEMENT_TYPE_OPTIONS.map((movementType) => (
                    <option key={movementType} value={movementType}>
                      {MOVEMENT_TYPE_LABELS[movementType]}
                    </option>
                  ))}
                </select>
              </div>

              <div className="min-w-0 rounded-2xl border border-divider bg-content1 p-4 dark:border-white/10 dark:bg-content2">
                <p className="text-xs font-semibold uppercase tracking-wide text-default-600">{movementTypeSearchTerm}</p>
                <div className="mt-2 flex min-w-0 items-center justify-between gap-4">
                  <div className="min-w-0">
                    <p className="truncate font-semibold text-foreground">
                      {selectedLevel?.material_name ?? "Selecciona un material"}
                    </p>
                    <p className="text-sm text-default-600">
                      Stock actual: {selectedLevel ? selectedLevel.quantity : "-"}
                    </p>
                  </div>
                  <Chip
                    color={signedPreviewQuantity < 0 ? "danger" : "success"}
                    variant="flat"
                    startContent={signedPreviewQuantity < 0 ? <ArrowDownRight className="h-4 w-4" /> : <ArrowUpRight className="h-4 w-4" />}
                    className="shrink-0"
                  >
                    {signedPreviewLabel}
                  </Chip>
                </div>
                {selectedLevel ? (
                  <p className="mt-3 text-sm text-default-600">
                    Resultado estimado: <span className="font-semibold text-foreground">{previewStock}</span>
                  </p>
                ) : (
                  <p className="mt-3 text-sm text-default-600">
                    Elegi un material para ver el impacto del movimiento.
                  </p>
                )}
              </div>

              <div className="min-w-0">
                <label htmlFor="inventory-quantity" className={FIELD_LABEL_CLASS}>
                  Quantity
                </label>
                <input
                  id="inventory-quantity"
                  type="number"
                  min={0.01}
                  step="0.01"
                  value={form.quantity}
                  onChange={(event) => handleFieldChange("quantity", event.target.value)}
                  className={`${FIELD_CONTROL_CLASS} min-w-0`}
                />
              </div>

              <div className="min-w-0">
                <label htmlFor="inventory-batch" className={FIELD_LABEL_CLASS}>
                  Lote / batch
                </label>
                <input
                  id="inventory-batch"
                  value={form.batchNumber}
                  onChange={(event) => handleFieldChange("batchNumber", event.target.value)}
                  className={`${FIELD_CONTROL_CLASS} min-w-0`}
                />
              </div>

              <div className="min-w-0">
                <label htmlFor="inventory-reference" className={FIELD_LABEL_CLASS}>
                  Referencia externa
                </label>
                <input
                  id="inventory-reference"
                  value={form.referenceId}
                  onChange={(event) => handleFieldChange("referenceId", event.target.value)}
                  className={`${FIELD_CONTROL_CLASS} min-w-0`}
                />
              </div>

              <div className="min-w-0">
                <label htmlFor="inventory-warehouse" className={FIELD_LABEL_CLASS}>
                  Bodega
                </label>
                <input
                  id="inventory-warehouse"
                  value={form.warehouseId}
                  onChange={(event) => handleFieldChange("warehouseId", event.target.value)}
                  className={`${FIELD_CONTROL_CLASS} min-w-0`}
                />
              </div>

              <div className="min-w-0">
                <label htmlFor="inventory-created-at" className={FIELD_LABEL_CLASS}>
                  Fecha personalizada
                </label>
                <input
                  id="inventory-created-at"
                  type="datetime-local"
                  value={form.createdAt}
                  onChange={(event) => handleFieldChange("createdAt", event.target.value)}
                  className={`${FIELD_CONTROL_CLASS} min-w-0`}
                />
              </div>

              <div className="min-w-0 md:col-span-2">
                <label htmlFor="inventory-reason" className={FIELD_LABEL_CLASS}>
                  Motivo
                </label>
                <textarea
                  id="inventory-reason"
                  rows={4}
                  value={form.reason}
                  onChange={(event) => handleFieldChange("reason", event.target.value)}
                  className={`${FIELD_CONTROL_CLASS} resize-none`}
                />
              </div>
            </div>
          </ModalBody>

          <ModalFooter className="w-full min-w-0 border-t border-divider bg-content2 px-6 py-4 dark:border-white/10 dark:bg-content2">
            <div className="w-full min-w-0">
              {submitError ? (
                <div className="mb-4 rounded-xl border border-danger-200 bg-danger-50 px-4 py-3 text-sm text-danger-700" role="alert" aria-live="polite">
                  {submitError}
                </div>
              ) : null}

              <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
                <Button variant="flat" onPress={onClose}>
                  Cancel
                </Button>
                <Button color="primary" onPress={handleSubmit} isLoading={isSubmitting}>
                  Registrar movimiento
                </Button>
              </div>
            </div>
          </ModalFooter>
        </div>
      )}
    </CenteredModal>
  );
}
