import { useState } from "react";
import {
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  History as HistoryIcon,
  LayoutDashboard,
  Package,
  RefreshCw,
  Search,
  TrendingUp,
} from "lucide-react";
import {
  Button,
  Card,
  CardBody,
  Chip,
  Input,
  Table,
  TableBody,
  TableCell,
  TableColumn,
  TableHeader,
  TableRow,
  Tab,
  Tabs,
} from "@heroui/react";
import type { Key, ReactNode } from "react";
import { useDebounce } from "@hooks/useDebounce";
import { useInventory } from "@hooks/useInventory";
import { InventoryMovementModal } from "@components/inventory/InventoryMovementModal";
import { inventoryService } from "@services/inventoryService";
import { INVENTORY_MOVEMENT_TYPES, type InventoryMovement } from "@/types/inventory";

type InventoryTab = "dashboard" | "existencias" | "movimientos";

const LOW_STOCK_THRESHOLD = 10;

const formatQuantity = (value: string): string => {
  const parsedValue = Number(value);
  if (!Number.isFinite(parsedValue)) {
    return value;
  }

  return new Intl.NumberFormat("es-AR", {
    maximumFractionDigits: 2,
  }).format(parsedValue);
};

const getQuantityChipColor = (quantity: number): "success" | "warning" | "danger" => {
  if (quantity <= 0) return "danger";
  if (quantity <= LOW_STOCK_THRESHOLD) return "warning";
  return "success";
};

const getMovementChipColor = (
  movementType: InventoryMovement["type"],
): "success" | "danger" | "warning" | "primary" => {
  if (movementType === INVENTORY_MOVEMENT_TYPES.PURCHASE || movementType === INVENTORY_MOVEMENT_TYPES.RETURN) {
    return "success";
  }

  if (movementType === INVENTORY_MOVEMENT_TYPES.SALE || movementType === INVENTORY_MOVEMENT_TYPES.PRODUCTION_CONSUMPTION) {
    return "danger";
  }

  return "warning";
};

const getSignedQuantityLabel = (movement: InventoryMovement): string => {
  const quantity = Number(movement.quantity);

  if (!Number.isFinite(quantity)) {
    return movement.quantity;
  }

  const sign = quantity > 0 ? "+" : "-";

  return `${sign}${formatQuantity(String(Math.abs(quantity)))}`;
};

function InventorySummaryCard({
  title,
  value,
  icon,
  tone,
}: {
  title: string;
  value: string;
  icon: ReactNode;
  tone: string;
}) {
  return (
    <Card className="border border-divider shadow-sm">
      <CardBody className="flex flex-row items-center gap-4 p-4">
        <div className={`rounded-xl p-3 ${tone}`}>
          {icon}
        </div>
        <div>
          <p className="text-xs font-bold uppercase text-default-500">{title}</p>
          <h3 className="text-xl font-bold text-foreground">{value}</h3>
        </div>
      </CardBody>
    </Card>
  );
}

export function InventoryManager() {
  const [activeTab, setActiveTab] = useState<InventoryTab>("dashboard");
  const [searchQuery, setSearchQuery] = useState("");
  const [isMovementModalOpen, setIsMovementModalOpen] = useState(false);

  const {
    levels,
    selectedLevel,
    movements,
    loadingLevels,
    loadingDetail,
    error,
    selectedMaterialId,
    setSelectedMaterialId,
    refresh,
  } = useInventory();

  const debouncedSearch = useDebounce(searchQuery, 250);

  const filteredLevels = levels.filter((level) => {
    const search = debouncedSearch.trim().toLowerCase();
    if (!search) {
      return true;
    }

    return (
      level.material_name.toLowerCase().includes(search) ||
      level.sku.toLowerCase().includes(search) ||
      level.material_id.toLowerCase().includes(search)
    );
  });

  const totalMaterials = levels.length;
  const totalQuantity = levels.reduce((accumulator, level) => accumulator + (Number(level.quantity) || 0), 0);
  const lowStockCount = levels.filter((level) => (Number(level.quantity) || 0) <= LOW_STOCK_THRESHOLD).length;
  const warehouseCount = new Set(levels.map((level) => level.warehouse_id).filter(Boolean)).size;

  const handleSelectMaterial = (materialId: string): void => {
    setSelectedMaterialId(materialId);
    setActiveTab("movimientos");
  };

  const handleSubmitMovement = async (payload: Parameters<typeof inventoryService.createInventoryMovement>[0]): Promise<void> => {
    await inventoryService.createInventoryMovement(payload);
    await refresh();
  };

  const movementTypeLabelByType: Record<InventoryMovement["type"], string> = {
    [INVENTORY_MOVEMENT_TYPES.PURCHASE]: "Compra",
    [INVENTORY_MOVEMENT_TYPES.SALE]: "Venta",
    [INVENTORY_MOVEMENT_TYPES.ADJUSTMENT]: "Ajuste",
    [INVENTORY_MOVEMENT_TYPES.PRODUCTION_CONSUMPTION]: "Consumo de produccion",
    [INVENTORY_MOVEMENT_TYPES.RETURN]: "Devolucion",
  };

  return (
    <div className="flex flex-col gap-6 p-4 md:p-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Gestion de Inventario</h1>
          <p className="text-default-500">Stock real, kardex y movimientos atomicos contra backend.</p>
        </div>

        <div className="flex gap-3">
          <Button variant="flat" startContent={<RefreshCw className="h-4 w-4" />} onPress={() => void refresh()}>
            Refrescar
          </Button>
          <Button color="primary" startContent={<ArrowUpRight className="h-4 w-4" />} onPress={() => setIsMovementModalOpen(true)}>
            Nuevo movimiento
          </Button>
        </div>
      </div>

      {error ? (
        <div className="rounded-2xl border border-danger-200 bg-danger-50 px-4 py-3 text-sm text-danger-700">
          {error}
        </div>
      ) : null}

      <Tabs
        aria-label="Inventario"
        selectedKey={activeTab}
        onSelectionChange={(key: Key) => setActiveTab(String(key) as InventoryTab)}
        color="primary"
        variant="underlined"
      >
          <Tab key="dashboard" title={<span className="flex items-center gap-2"><LayoutDashboard className="h-4 w-4" />Dashboard</span>} />
          <Tab key="existencias" title={<span className="flex items-center gap-2"><Package className="h-4 w-4" />Existencias</span>} />
          <Tab key="movimientos" title={<span className="flex items-center gap-2"><ArrowDownRight className="h-4 w-4" />Movimientos</span>} />
        </Tabs>

      <div className="space-y-6">
        {activeTab === "dashboard" ? (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
            <InventorySummaryCard
              title="Materials con stock"
              value={String(totalMaterials)}
              icon={<TrendingUp className="h-6 w-6 text-primary" />}
              tone="bg-primary/10"
            />
            <InventorySummaryCard
              title="Unidades totales"
              value={formatQuantity(String(totalQuantity))}
              icon={<Package className="h-6 w-6 text-secondary" />}
              tone="bg-secondary/10"
            />
            <InventorySummaryCard
              title="Stock bajo"
              value={String(lowStockCount)}
              icon={<AlertTriangle className="h-6 w-6 text-warning" />}
              tone="bg-warning/10"
            />
            <InventorySummaryCard
              title="Bodegas"
              value={String(warehouseCount)}
              icon={<HistoryIcon className="h-6 w-6 text-danger" />}
              tone="bg-danger/10"
            />
          </div>
        ) : null}

        {activeTab === "existencias" ? (
          <Card className="shadow-sm">
            <CardBody className="p-0">
              <div className="flex flex-col gap-4 p-4 md:flex-row md:items-center md:justify-between">
                <Input
                  placeholder="Search por material, SKU o ID..."
                  value={searchQuery}
                  onValueChange={setSearchQuery}
                  startContent={<Search className="h-4 w-4 text-default-400" />}
                  className="md:max-w-md"
                />

                <div className="text-sm text-default-500">
                  {loadingLevels ? "Cargando existencias..." : `${filteredLevels.length} registros`}
                </div>
              </div>

              <Table aria-label="Existencias actuales" removeWrapper>
                <TableHeader>
                  <TableColumn>MATERIAL</TableColumn>
                  <TableColumn>SKU</TableColumn>
                  <TableColumn>CANTIDAD</TableColumn>
                  <TableColumn>BODEGA</TableColumn>
                  <TableColumn>ACTUALIZADO</TableColumn>
                  <TableColumn align="center">ACCIONES</TableColumn>
                </TableHeader>
                <TableBody emptyContent="No hay existencias para mostrar.">
                  {filteredLevels.map((level) => {
                    const quantity = Number(level.quantity) || 0;

                    return (
                      <TableRow key={level.material_id}>
                        <TableCell>
                          <div className="flex flex-col">
                            <span className="font-semibold text-foreground">{level.material_name}</span>
                            <span className="text-tiny text-default-400">{level.material_id}</span>
                          </div>
                        </TableCell>
                        <TableCell>{level.sku}</TableCell>
                        <TableCell>
                          <Chip size="sm" color={getQuantityChipColor(quantity)} variant="flat">
                            {formatQuantity(level.quantity)}
                          </Chip>
                        </TableCell>
                        <TableCell>{level.warehouse_id ?? "Sin definir"}</TableCell>
                        <TableCell>{level.last_updated ? new Date(level.last_updated).toLocaleString("es-AR") : "-"}</TableCell>
                        <TableCell>
                          <div className="flex justify-center gap-2">
                            <Button size="sm" variant="flat" onPress={() => handleSelectMaterial(level.material_id)}>
                              Ver detalle
                            </Button>
                            <Button size="sm" color="primary" onPress={() => {
                              setSelectedMaterialId(level.material_id);
                              setIsMovementModalOpen(true);
                            }}>
                              Movimiento
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </CardBody>
          </Card>
        ) : null}

        {activeTab === "movimientos" ? (
          <Card className="shadow-sm">
            <CardBody className="space-y-4">
              <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                <div>
                  <h2 className="text-lg font-bold text-foreground">Movimientos del inventario</h2>
                  <p className="text-sm text-default-500">Elegi un material para ver su lista de movimientos y el detalle asociado.</p>
                </div>
                {selectedLevel ? <Chip color="primary" variant="flat">{selectedLevel.material_name}</Chip> : null}
              </div>

              <div className="grid gap-4 lg:grid-cols-[320px_minmax(0,1fr)]">
                <Card className="border border-divider shadow-none">
                  <CardBody className="space-y-3">
                    <div>
                      <p className="text-sm font-semibold text-foreground">Materials</p>
                      <p className="text-sm text-default-500">Selecciona uno para cargar su kardex.</p>
                    </div>

                    <div className="max-h-[420px] space-y-2 overflow-y-auto pr-1">
                      {levels.map((level) => {
                        const isSelected = level.material_id === selectedMaterialId;

                        return (
                          <button
                            key={level.material_id}
                            type="button"
                            onClick={() => setSelectedMaterialId(level.material_id)}
                            className={`flex w-full items-center justify-between gap-3 rounded-2xl border px-4 py-3 text-left transition-colors ${
                              isSelected
                                ? "border-primary bg-primary/10"
                                : "border-divider bg-content1 hover:border-primary/50 hover:bg-content2"
                            }`}
                          >
                            <div className="min-w-0">
                              <p className="truncate font-semibold text-foreground">{level.material_name}</p>
                              <p className="text-xs text-default-500">SKU: {level.sku}</p>
                            </div>
                            <Chip size="sm" variant="flat" color={isSelected ? "primary" : "default"} className="shrink-0">
                              {formatQuantity(level.quantity)}
                            </Chip>
                          </button>
                        );
                      })}
                    </div>
                  </CardBody>
                </Card>

                <Card className="border border-divider shadow-none">
                  <CardBody className="space-y-4">
                    {loadingDetail ? (
                      <div className="py-8 text-center text-sm text-default-500">Cargando detalle...</div>
                    ) : selectedLevel ? (
                      <>
                        <div className="flex flex-col gap-1">
                          <h3 className="text-base font-bold text-foreground">{selectedLevel.material_name}</h3>
                          <p className="text-sm text-default-500">SKU: {selectedLevel.sku}</p>
                          <p className="text-sm text-default-500">Stock actual: {formatQuantity(selectedLevel.quantity)}</p>
                        </div>

                        <Table aria-label="Movimientos del inventario" removeWrapper>
                          <TableHeader>
                            <TableColumn>FECHA</TableColumn>
                            <TableColumn>TIPO</TableColumn>
                            <TableColumn>CANTIDAD</TableColumn>
                            <TableColumn>MOTIVO</TableColumn>
                            <TableColumn>REFERENCIA</TableColumn>
                          </TableHeader>
                          <TableBody emptyContent="No hay movimientos para este material.">
                            {movements.map((movement) => (
                              <TableRow key={movement.id}>
                                <TableCell>{new Date(movement.created_at).toLocaleString("es-AR")}</TableCell>
                                <TableCell>
                                  <Chip size="sm" color={getMovementChipColor(movement.type)} variant="flat">
                                    {movementTypeLabelByType[movement.type]}
                                  </Chip>
                                </TableCell>
                                <TableCell>{getSignedQuantityLabel(movement)}</TableCell>
                                <TableCell>{movement.reason ?? "-"}</TableCell>
                                <TableCell>{movement.reference_id ?? "-"}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </>
                    ) : (
                      <div className="py-8 text-center text-sm text-default-500">No hay un material seleccionado.</div>
                    )}
                  </CardBody>
                </Card>
              </div>
            </CardBody>
          </Card>
        ) : null}

      <InventoryMovementModal
        isOpen={isMovementModalOpen}
        onOpenChange={setIsMovementModalOpen}
        selectedMaterialId={selectedMaterialId}
        onSubmit={handleSubmitMovement}
      />
    </div>
    </div>
  );
}
