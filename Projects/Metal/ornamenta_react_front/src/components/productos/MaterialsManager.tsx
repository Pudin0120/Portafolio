import React, { useState, useMemo } from "react";
import {
  Plus,
  Copy,
  Pencil,
  Trash,
  AlertCircle,
  Package,
  FileImage,
} from "lucide-react";
import { useIsMobile } from "@hooks/useIsMobile";
import { formatPrice } from "@/utils";
import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Button,
  Chip,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Tabs,
  Tab,
  Pagination,
  Tooltip,
  Alert,
  Image,
} from "@heroui/react";
import { Material } from "@/types/products";
import { CreateMaterial } from "./CreateMaterial";
import { CreateMaterialModal } from "./CreateMaterialModal";
import { EditMaterialModal } from "./EditMaterialModal";
import { MaterialTypeManager } from "./MaterialTypeManager";
import { CompositionsManager } from "./CompositionsManager";
import { TableSearchBar } from "@components/common/TableSearchBar";
import { TableSkeleton } from "@components/common/TableSkeleton";
import { UndoToast } from "@components/common/UndoToast";
import { HelpTooltip, helpContent } from "@components/HelpTooltip";
import { CenteredModal } from "@components/common/CenteredModal";
import { useMaterials } from "@context/MaterialsContext";
import { useConnectivity } from "@/providers/ConnectivityProvider";

type MaterialsManagerProps = {
  onSubTabChange?: (tab: string) => void;
  onBack?: () => void;
  context?: string;
};

// Estado local simplificado para UI (modales, tabs, etc.)
type ModalState =
  | { type: "closed" }
  | { type: "create" }
  | { type: "clone"; material: Material }
  | { type: "edit"; material: Material }
  | { type: "delete"; material: Material }
  | { type: "detail"; material: Material };

export const MaterialsManager: React.FC<MaterialsManagerProps> = ({
  onSubTabChange,
}) => {
  const isMobile = useIsMobile();
  const { isOnline } = useConnectivity();
  const {
    state: {
      materials,
      isLoading,
      error,
      searchQuery,
      pagination,
      deletedMaterial,
    },
    setSearchQuery,
    setPage,
    deleteMaterial,
    undoDelete,
    clearError,
  } = useMaterials();

  // Estados locales para UI
  const [selectedTab, setSelectedTab] = useState("materials");
  const [modalState, setModalState] = useState<ModalState>({ type: "closed" });
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Estado para saber si es la primera carga
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  // Cuando termina el loading por primera vez, marcamos que ya no es inicial
  React.useEffect(() => {
    if (!isLoading && isInitialLoad) {
      setIsInitialLoad(false);
    }
  }, [isLoading, isInitialLoad]);

  // ============================================================================
  // FILTRADO LOCAL
  // ============================================================================

  // Filtrado local INSTANTANEO para mejor UX
  // El debounce del contexto se encarga de la busqueda en servidor como backup
  const filteredMaterials = useMemo(() => {
    if (!searchQuery.trim()) {
      return materials;
    }

    const query = searchQuery.toLowerCase();
    return materials.filter((material) => {
      return (
        material.name?.toLowerCase().includes(query) ||
        material.description?.toLowerCase().includes(query) ||
        material.material_type_name?.toLowerCase().includes(query)
      );
    });
  }, [materials, searchQuery]);

  // ============================================================================
  // HANDLERS
  // ============================================================================

  const handleSearchChange = (value: string) => {
    setSearchQuery(value);
  };

  const handleRowClick = (material: Material) => {
    setModalState({ type: "detail", material });
  };

  const handleEditClick = (material: Material) => {
    setModalState({ type: "edit", material });
  };

  const handleCloneClick = (material: Material) => {
    setModalState({ type: "clone", material });
  };

  const handleDeleteClick = (material: Material) => {
    setModalState({ type: "delete", material });
  };

  const handleDeleteConfirm = async () => {
    if (modalState.type !== "delete") return;
    await deleteMaterial(modalState.material.id);
    setModalState({ type: "closed" });
  };

  const handleModalClose = () => {
    setModalState({ type: "closed" });
  };

  const showSuccess = (message: string) => {
    setSuccessMessage(message);
    setTimeout(() => setSuccessMessage(null), 3000);
  };

  // ============================================================================
  // RENDER HELPERS
  // ============================================================================

  const renderTableContent = () => {
    // Solo mostramos skeleton en la carga inicial, NO durante busquedas
    if (isLoading && isInitialLoad) {
      return <TableSkeleton rows={10} columns={isMobile ? 2 : 4} />;
    }

    return (
      <Table
        key={isMobile ? "mobile" : "desktop"}
        aria-label="Materials table"
        isCompact={isMobile}
        isHeaderSticky
        isStriped
        removeWrapper
        shadow="sm"
        radius="md"
        selectionMode="single"
        onRowAction={(key: React.Key) => {
          const material = filteredMaterials.find((m) => m.id === key);
          if (material) handleRowClick(material);
        }}
        classNames={{
          base: "materials-table max-h-[calc(100dvh-250px)] overflow-y-auto",
          row: "cursor-pointer hover:bg-table-row-hover transition-colors",
          wrapper: "max-h-[calc(100dvh-250px)]",
        }}
        bottomContent={
          pagination.totalPages > 1 ? (
            <div className="flex justify-center p-2">
              <Pagination
                page={pagination.currentPage}
                total={pagination.totalPages}
                onChange={(p: number) => setPage(p)}
                showControls
              />
            </div>
          ) : null
        }
      >
        <TableHeader>
          {[
            <TableColumn key="image" width={60}>
              Imagen
            </TableColumn>,
            <TableColumn key="name">Nombre</TableColumn>,
            !isMobile && (
              <TableColumn key="description">Description</TableColumn>
            ),
            !isMobile && <TableColumn key="type">Tipo</TableColumn>,
            <TableColumn key="purchase_price">P. Compra</TableColumn>,
            <TableColumn key="sale_price">P. Venta</TableColumn>,
            <TableColumn key="actions" width={200}>
              Acciones
            </TableColumn>,
          ].filter(Boolean)}
        </TableHeader>
        <TableBody
          emptyContent={
            searchQuery
              ? "No se encontraron materials con ese criterio"
              : "Sin materials"
          }
          items={filteredMaterials}
          isLoading={isLoading && !isInitialLoad}
          loadingContent={
            <div className="flex items-center justify-center py-8">
              <div className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-warning"></div>
                <span className="text-sm text-default-500">Buscando...</span>
              </div>
            </div>
          }
        >
          {(item: Material) => (
            <TableRow key={item.id}>
              {[
                <TableCell key="image">
                  {item.image_url || item.properties?.image_url ? (
                    <Image
                      src={
                        (item.image_url || item.properties?.image_url) as string
                      }
                      alt={item.name}
                      width={40}
                      height={40}
                      className="object-cover rounded-lg shadow-sm"
                      fallbackSrc="https://via.placeholder.com/40"
                    />
                  ) : (
                    <div className="w-10 h-10 rounded-lg bg-default-100 flex items-center justify-center text-default-400">
                      <FileImage className="w-5 h-5" />
                    </div>
                  )}
                </TableCell>,
                <TableCell key="name" className="max-w-[200px]">
                  <Tooltip content={item.name} showArrow placement="top-start">
                    <button
                      type="button"
                      className="text-left hover:text-primary transition-colors underline decoration-transparent hover:decoration-current truncate w-full block font-medium"
                      onClick={() => handleRowClick(item)}
                    >
                      {item.name}
                    </button>
                  </Tooltip>
                </TableCell>,
                !isMobile && (
                  <TableCell key="description" className="max-w-[250px]">
                    <Tooltip content={item.description} showArrow>
                      <span className="truncate block text-default-500">
                        {item.description}
                      </span>
                    </Tooltip>
                  </TableCell>
                ),
                !isMobile && (
                  <TableCell key="type" className="max-w-[150px] truncate">
                    {item.material_type_name}
                  </TableCell>
                ),
                <TableCell key="purchase_price">
                  <Chip
                    color="warning"
                    variant="flat"
                    size="sm"
                    className="font-medium"
                  >
                    $
                    {formatPrice(
                      parseFloat(
                        item.purchase_price_amount || item.price_amount || "0",
                      ),
                    )}{" "}
                    {item.purchase_price_currency || item.price_currency}
                  </Chip>
                </TableCell>,
                <TableCell key="sale_price">
                  <Chip
                    color="success"
                    variant="flat"
                    size="sm"
                    className="font-medium"
                  >
                    $
                    {formatPrice(
                      parseFloat(
                        item.sale_price_amount || item.price_amount || "0",
                      ),
                    )}{" "}
                    {item.sale_price_currency || item.price_currency}
                  </Chip>
                </TableCell>,
                <TableCell key="actions">
                  <div className="flex items-center gap-1">
                    <Tooltip content="Clonar" size="sm">
                      <Button
                        isIconOnly
                        size="sm"
                        color="primary"
                        variant="flat"
                        onPress={() => handleCloneClick(item)}
                        isDisabled={!isOnline}
                        className="hover:bg-primary/10"
                      >
                        <Copy className="w-4 h-4" />
                      </Button>
                    </Tooltip>
                    <Tooltip content="Edit" size="sm">
                      <Button
                        isIconOnly
                        size="sm"
                        color="default"
                        variant="flat"
                        onPress={() => handleEditClick(item)}
                        isDisabled={!isOnline}
                        className="text-primary hover:bg-primary/10"
                      >
                        <Pencil className="w-4 h-4" />
                      </Button>
                    </Tooltip>
                    <Tooltip content="Delete" size="sm">
                      <Button
                        isIconOnly
                        size="sm"
                        color="danger"
                        variant="flat"
                        onPress={() => handleDeleteClick(item)}
                        isDisabled={!isOnline}
                      >
                        <Trash className="w-4 h-4" />
                      </Button>
                    </Tooltip>
                  </div>
                </TableCell>,
              ].filter(Boolean)}
            </TableRow>
          )}
        </TableBody>
      </Table>
    );
  };

  // ============================================================================
  // EFFECTS
  // ============================================================================

  // Notificar al padre cuando cambie la subpestana
  React.useEffect(() => {
    if (onSubTabChange) {
      onSubTabChange(selectedTab);
    }
  }, [selectedTab, onSubTabChange]);

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className={`mx-auto max-w-6xl ${isMobile ? "p-2" : "p-4"}`}>
      {/* Success Message */}
      {successMessage && (
        <Alert
          color="success"
          variant="flat"
          className="mb-4"
          onClose={() => setSuccessMessage(null)}
        >
          {successMessage}
        </Alert>
      )}

      {/* Error Message */}
      {error && (
        <Alert
          color="danger"
          variant="flat"
          className="mb-4"
          startContent={<AlertCircle className="w-5 h-5" />}
          onClose={clearError}
        >
          {error}
        </Alert>
      )}

      {/* Undo Toast */}
      {deletedMaterial && (
        <UndoToast
          message={`Material "${deletedMaterial.material.name}" eliminado`}
          onUndo={undoDelete}
          onDismiss={() => {}}
        />
      )}

      {/* Header */}
      <div className="mb-4">
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-semibold text-foreground">
            Gestion de Materials
          </h2>
          <HelpTooltip content={helpContent.materials} />
        </div>
      </div>

      {/* Tabs */}
      <Tabs
        selectedKey={selectedTab}
        onSelectionChange={(key: React.Key) => setSelectedTab(key as string)}
        className="mb-4"
      >
        <Tab key="materials" title="Materials">
          <div className="space-y-4">
            {/* Search Bar + Actions */}
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div className="w-full md:flex-1 flex items-center gap-2">
                <div className="flex-1">
                  <TableSearchBar
                    value={searchQuery}
                    onValueChange={handleSearchChange}
                    placeholder="Search por nombre, description o tipo..."
                    label="Search materials"
                    description={`Mostrando ${filteredMaterials.length} de ${pagination.totalItems} material(es)`}
                  />
                </div>
                {isLoading && !isInitialLoad && (
                  <div className="flex-shrink-0">
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-warning border-t-transparent"></div>
                  </div>
                )}
              </div>
              <div className="flex flex-col sm:flex-row sm:items-center gap-3 w-full sm:w-auto sm:justify-end">
                <Chip color="primary" variant="flat">
                  Mostrando: {filteredMaterials.length} /{" "}
                  {pagination.totalItems}
                </Chip>
                <Button
                  color="primary"
                  variant="solid"
                  onPress={() => setModalState({ type: "create" })}
                  startContent={<Plus className="w-4 h-4" />}
                  className="font-semibold"
                >
                  Create Material
                </Button>
              </div>
            </div>

            {/* Table */}
            {renderTableContent()}
          </div>
        </Tab>

        <Tab key="compositions" title="Composiciones">
          <CompositionsManager />
        </Tab>

        <Tab key="types" title="Material Types">
          <MaterialTypeManager />
        </Tab>
      </Tabs>

      {/* ========================================================================
          MODALS
      ======================================================================== */}

      {/* Detail Modal */}
      <CenteredModal
        isOpen={modalState.type === "detail"}
        onOpenChange={(isOpen: boolean) => !isOpen && handleModalClose()}
        size="lg"
        scrollBehavior="inside"
        backdrop="blur"
      >
        {(onClose) => (
          <>
            <ModalHeader className="border-b border-divider">
              Detalles del Material
            </ModalHeader>
            <ModalBody className="py-5 sm:py-6">
              {modalState.type === "detail" && (
                <div className="space-y-6">
                  {/* Image Display */}
                  <div className="flex justify-center">
                    {modalState.material.image_url ||
                    modalState.material.properties?.image_url ? (
                      <Image
                        src={
                          (modalState.material.image_url ||
                            modalState.material.properties?.image_url) as string
                        }
                        alt={modalState.material.name}
                        className="w-full max-h-[300px] object-contain rounded-xl shadow-lg border border-divider"
                      />
                    ) : (
                      <div className="w-full h-[200px] rounded-xl bg-default-100 flex flex-col items-center justify-center text-default-400 gap-3 border-2 border-dashed border-divider">
                        <FileImage className="w-12 h-12" />
                        <span className="text-sm">Sin imagen disponible</span>
                      </div>
                    )}
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold mb-2">
                      Informacion General
                    </h3>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      <div className="flex flex-col gap-1 sm:col-span-2">
                        <span className="text-sm font-medium text-default-500">
                          Nombre
                        </span>
                        <p className="text-base font-medium">
                          {modalState.material.name}
                        </p>
                      </div>
                      <div className="flex flex-col gap-1">
                        <span className="text-sm font-medium text-default-500">
                          Description
                        </span>
                        <p className="text-base">
                          {modalState.material.description || "Sin description"}
                        </p>
                      </div>
                      <div className="flex flex-col gap-1">
                        <span className="text-sm font-medium text-default-500">
                          Tipo de Material
                        </span>
                        <p className="text-base">
                          {modalState.material.material_type_name}
                        </p>
                      </div>
                      <div className="flex flex-col gap-1">
                        <span className="text-sm font-medium text-default-500">
                          SKU
                        </span>
                        <p className="text-base font-mono">
                          {modalState.material.sku || "N/A"}
                        </p>
                      </div>
                      <div className="flex flex-col gap-1">
                        <span className="text-sm font-medium text-default-500">
                          Codigo de Barras
                        </span>
                        <p className="text-base font-mono">
                          {modalState.material.barcode || "N/A"}
                        </p>
                      </div>
                      <div className="flex flex-col gap-1">
                        <span className="text-sm font-medium text-default-500">
                          Price de Venta
                        </span>
                        <p className="text-base font-medium text-success-600">
                          $
                          {formatPrice(
                            parseFloat(
                              modalState.material.sale_price_amount ||
                                modalState.material.price_amount,
                            ),
                          )}{" "}
                          {modalState.material.sale_price_currency ||
                            modalState.material.price_currency}
                        </p>
                      </div>
                      <div className="flex flex-col gap-1">
                        <span className="text-sm font-medium text-default-500">
                          Price de Compra
                        </span>
                        <p className="text-base font-medium text-warning-600">
                          $
                          {formatPrice(
                            parseFloat(
                              modalState.material.purchase_price_amount ||
                                modalState.material.price_amount,
                            ),
                          )}{" "}
                          {modalState.material.purchase_price_currency ||
                            modalState.material.price_currency}
                        </p>
                      </div>

                      {/* Properties Tecnicas */}
                      {modalState.material.properties &&
                        Object.keys(modalState.material.properties).length >
                          0 && (
                          <div className="pt-4 border-t border-divider">
                            <h3 className="text-lg font-semibold mb-3">
                              Properties Tecnicas
                            </h3>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                              {Object.entries(
                                modalState.material.properties,
                              ).map(([key, val]) => {
                                if (
                                  val === undefined ||
                                  val === null ||
                                  key === "image_url"
                                )
                                  return null;

                                const displayKey =
                                  key === "thickness"
                                    ? "Espesor / Calibre"
                                    : key === "part_number"
                                      ? "Referencia"
                                      : key === "brand"
                                        ? "Marca"
                                        : key === "width"
                                          ? "Ancho"
                                          : key === "length"
                                            ? "Largo"
                                            : key === "area"
                                              ? "Area"
                                              : key === "color"
                                                ? "Color"
                                                : key === "unit_type"
                                                  ? "Tipo de Unidad"
                                                  : key === "shape"
                                                    ? "Forma"
                                                    : key === "is_hollow"
                                                      ? "Hueco"
                                                      : key.replace("_", " ");

                                if (typeof val === "object" && val !== null) {
                                  const objVal = val as Record<
                                    string,
                                    string | number
                                  >;
                                  return (
                                    <div
                                      key={key}
                                      className="p-3 rounded-lg bg-default-50 border border-divider"
                                    >
                                      <span className="text-xs font-bold text-default-400 uppercase block mb-1">
                                        {displayKey}
                                      </span>
                                      <span className="text-sm font-bold text-foreground">
                                        {objVal.value ?? objVal.gauge ?? "-"}{" "}
                                        <span className="text-xs text-primary">
                                          {(objVal.unit as string) ??
                                            (objVal.gauge ? "Ga" : "")}
                                        </span>
                                      </span>
                                    </div>
                                  );
                                }

                                const displayValue =
                                  key === "unit_type"
                                    ? val === "linear_meter"
                                      ? "Metro Lineal"
                                      : val === "square_meter"
                                        ? "Metro Cuadrado"
                                        : String(val)
                                    : key === "is_hollow"
                                      ? val
                                        ? "Si"
                                        : "No"
                                      : String(val);

                                return (
                                  <div
                                    key={key}
                                    className="p-3 rounded-lg bg-default-50 border border-divider"
                                  >
                                    <span className="text-xs font-bold text-default-400 uppercase block mb-1">
                                      {displayKey}
                                    </span>
                                    <span className="text-sm font-bold text-foreground">
                                      {displayValue}
                                    </span>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        )}
                    </div>
                  </div>
                </div>
              )}
            </ModalBody>
            <ModalFooter className="flex flex-col-reverse gap-2 border-t border-divider sm:flex-row">
              <Button
                color="primary"
                variant="solid"
                type="button"
                onPress={() => {
                  if (modalState.type === "detail") {
                    setModalState({
                      type: "edit",
                      material: modalState.material,
                    });
                  }
                }}
                className="w-full font-semibold sm:w-auto"
              >
                Edit Material
              </Button>
              <Button
                color="default"
                variant="flat"
                type="button"
                onPress={() => {
                  handleModalClose();
                  onClose();
                }}
                className="w-full sm:w-auto"
              >
                Cerrar
              </Button>
            </ModalFooter>
          </>
        )}
      </CenteredModal>

      {/* Edit Modal */}
      {modalState.type === "edit" && (
        <EditMaterialModal
          isOpen={true}
          onOpenChange={(isOpen: boolean) => {
            if (!isOpen) handleModalClose();
          }}
          material={modalState.material}
          onSuccess={() => {
            handleModalClose();
            showSuccess("Material actualizado exitosamente");
          }}
        />
      )}

      {/* Create Modal */}
      <CreateMaterialModal
        isOpen={modalState.type === "create" || modalState.type === "clone"}
        onOpenChange={(isOpen: boolean) => !isOpen && handleModalClose()}
        cloneFrom={
          modalState.type === "clone" ? modalState.material : undefined
        }
        onSuccess={() => {
          const isClone = modalState.type === "clone";
          showSuccess(
            isClone
              ? "Material clonado exitosamente"
              : "Material creado exitosamente",
          );
        }}
      />

      {/* Delete Confirmation Modal */}
      <CenteredModal
        isOpen={modalState.type === "delete"}
        onOpenChange={(isOpen: boolean) => !isOpen && handleModalClose()}
        backdrop="blur"
      >
        {(onClose) => (
          <>
            <ModalHeader className="border-b border-divider">
              Confirmar Eliminacion
            </ModalHeader>
            <ModalBody className="py-5 sm:py-6">
              <p>
                Estas seguro de que deseas delete el material "
                <span className="font-semibold">
                  {modalState.type === "delete" && modalState.material.name}
                </span>
                "? Podras deshacer esta accion en los proximos 5 segundos.
              </p>
            </ModalBody>
            <ModalFooter className="flex flex-col-reverse gap-2 border-t border-divider sm:flex-row">
              <Button
                variant="flat"
                type="button"
                onPress={onClose}
                className="w-full sm:w-auto"
              >
                Cancel
              </Button>
              <Button
                color="danger"
                variant="solid"
                type="button"
                onPress={handleDeleteConfirm}
                className="w-full sm:w-auto"
              >
                Delete
              </Button>
            </ModalFooter>
          </>
        )}
      </CenteredModal>
    </div>
  );
};
