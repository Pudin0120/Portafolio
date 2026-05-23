import React, { useEffect, useState, useMemo } from "react";
import {
  Clipboard,
  Plus,
  Pencil,
  Trash,
} from "lucide-react";
import { useAuth } from "@hooks/useAuth";
import { useIsMobile } from "@hooks/useIsMobile";
import { useConnectivity } from "@/providers/ConnectivityProvider";
import { apiClient } from "@services/apiClient";
import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Button,
  Spinner,
  Chip,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Input,
  Textarea,
  Select,
  SelectItem,
  Pagination,
  Tooltip,
  Divider,
} from "@heroui/react";
import { Search } from "lucide-react";
import {
  MaterialType,
  MeasurementStrategy,
  MeasurementStrategiesResponse,
} from "@/types/products";
import { CreateMaterialTypeModal } from "./CreateMaterialTypeModal";
import { CenteredModal } from "@components/common/CenteredModal";

type MaterialTypesResponse = {
  material_types: MaterialType[];
  total: number;
};

type SortDescriptor = {
  column: string;
  direction: "ascending" | "descending";
};

const PAGE_SIZE = 20;

export const MaterialTypeManager: React.FC = () => {
  const { isAuthenticated, sessionReady } = useAuth();
  const isMobile = useIsMobile();
  const { connectionEpoch } = useConnectivity();
  const [isLoading, setIsLoading] = useState(false);
  const [materialTypes, setMaterialTypes] = useState<MaterialType[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [measurementStrategies, setMeasurementStrategies] = useState<
    MeasurementStrategy[]
  >([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showPropertiesModal, setShowPropertiesModal] = useState(false);
  const [selectedMaterialType, setSelectedMaterialType] =
    useState<MaterialType | null>(null);
  const [editingMaterialType, setEditingMaterialType] =
    useState<MaterialType | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [deletingMaterialType, setDeletingMaterialType] =
    useState<MaterialType | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [deleteSuccess, setDeleteSuccess] = useState<string | null>(null);
  const [editSuccess, setEditSuccess] = useState<string | null>(null);
  const [sortDescriptor, setSortDescriptor] = useState<SortDescriptor>({
    column: "name",
    direction: "ascending",
  });
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  // Memoize selected keys for measurement strategy
  const totalPages = useMemo(() => {
    if (total === 0) return 1;
    return Math.max(1, Math.ceil(total / PAGE_SIZE));
  }, [total]);

  const handleRowClick = (materialType: MaterialType) => {
    setSelectedMaterialType(materialType);
    setShowDetailModal(true);
  };

  const handleSearchChange = (value: string) => {
    setSearchQuery(value);
    setPage(1);
  };

  const handleEditClick = (materialType: MaterialType) => {
    setEditingMaterialType(materialType);
    setShowEditModal(true);
  };

  const handleEditSuccess = () => {
    setShowEditModal(false);
    setEditingMaterialType(null);
    setEditSuccess("Tipo de material actualizado exitosamente");
    setTimeout(() => setEditSuccess(null), 3000);
    fetchData();
  };

  const handleEditCancel = () => {
    setShowEditModal(false);
    setEditingMaterialType(null);
  };

  const handleDeleteClick = (materialType: MaterialType) => {
    setDeletingMaterialType(materialType);
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deletingMaterialType || (!isAuthenticated && !sessionReady)) return;

    try {
      setError("");
      await apiClient.delete(`/material-types/${deletingMaterialType.id}`);
      setDeleteSuccess(
        `Tipo de material "${deletingMaterialType.name}" eliminado exitosamente`,
      );
      setTimeout(() => setDeleteSuccess(null), 3000);
      fetchData();
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "No se pudo delete el tipo de material.";
      setError(message);
    } finally {
      setShowDeleteConfirm(false);
      setDeletingMaterialType(null);
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteConfirm(false);
    setDeletingMaterialType(null);
  };

  const handleDetailModalClose = () => {
    setShowDetailModal(false);
    setSelectedMaterialType(null);
  };

  const handleMaterialTypeCreated = async () => {
    setShowCreateModal(false);
    fetchData();
  };

  const fetchData = React.useCallback(async () => {
    if (!isAuthenticated && !sessionReady) return;
    setIsLoading(true);
    try {
      setError("");

      const searchParams = new URLSearchParams();
      searchParams.set("limit", String(PAGE_SIZE));
      searchParams.set("offset", String((page - 1) * PAGE_SIZE));

      const [typesData, strategiesData] = await Promise.all([
        apiClient.get<MaterialTypesResponse>(`/material-types/?${searchParams.toString()}`),
        apiClient.get<MeasurementStrategiesResponse>("/measurement-strategies/"),
      ]);

      if (typesData) {
        setMaterialTypes(typesData.material_types || []);
        setTotal(typesData.total || 0);
      }

      if (strategiesData) {
        setMeasurementStrategies(strategiesData || []);
      } else {
        setMeasurementStrategies([]);
      }
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "No se pudieron cargar los tipos de material.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated, sessionReady, page]);

  useEffect(() => {
    fetchData();
  }, [fetchData, connectionEpoch]);

  // Filtrar y ordenar tipos de materials
  const filteredMaterialTypes = useMemo(() => {
    let result = materialTypes;

    // Aplicar busqueda
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = materialTypes.filter((materialType) => {
        const strategy = (measurementStrategies || []).find(
          (s) =>
            s.name.toLowerCase() ===
            materialType.measurement_strategy.toLowerCase(),
        );
        const strategyDisplayName = strategy?.display_name || "";
        return (
          materialType.name?.toLowerCase().includes(query) ||
          materialType.description?.toLowerCase().includes(query) ||
          strategyDisplayName.toLowerCase().includes(query)
        );
      });
    }

    // Aplicar ordenamiento
    if (sortDescriptor.column) {
      result = [...result].sort((a, b) => {
        const column = sortDescriptor.column as keyof MaterialType;
        const aValue = a[column];
        const bValue = b[column];

        // Manejar valores null/undefined
        if (aValue == null && bValue == null) return 0;
        if (aValue == null)
          return sortDescriptor.direction === "ascending" ? 1 : -1;
        if (bValue == null)
          return sortDescriptor.direction === "ascending" ? -1 : 1;

        // Comparacion de strings
        const aStr = String(aValue).toLowerCase();
        const bStr = String(bValue).toLowerCase();

        if (aStr < bStr)
          return sortDescriptor.direction === "ascending" ? -1 : 1;
        if (aStr > bStr)
          return sortDescriptor.direction === "ascending" ? 1 : -1;
        return 0;
      });
    }

    return result;
  }, [materialTypes, searchQuery, sortDescriptor, measurementStrategies]);

  return (
    <div className="space-y-4">
      {error && (
        <div className="rounded-md border border-danger/30 bg-danger/20 p-3 text-sm text-danger">
          {error}
        </div>
      )}

      {deleteSuccess && (
        <div className="rounded-md bg-success/20 p-3 text-sm text-success border border-success/30">
          {deleteSuccess}
        </div>
      )}

      {editSuccess && (
        <div className="rounded-md bg-primary/20 p-3 text-sm text-primary border border-primary/30">
          {editSuccess}
        </div>
      )}

      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="w-full md:flex-1">
          <Input
            isClearable
            className="w-full max-w-md"
            placeholder="Search por nombre, description o estrategia..."
            startContent={<Search className="text-default-300" />}
            value={searchQuery}
            onValueChange={handleSearchChange}
            variant="bordered"
            size="sm"
          />
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center gap-3 w-full sm:w-auto sm:justify-end">
          <Chip size="sm" variant="flat" color="primary">
            Total: {total}
          </Chip>
          <Button
            color="primary"
            variant="solid"
            type="button"
            onPress={() => setShowCreateModal(true)}
            startContent={<Plus className="w-4 h-4" />}
            className="font-semibold"
            size="sm"
          >
            Create Tipo de Material
          </Button>
        </div>
      </div>

      <Table
        key={isMobile ? "mobile" : "desktop"}
        aria-label="Tabla de tipos de materials"
        isCompact={isMobile}
        isHeaderSticky
        isStriped
        removeWrapper
        shadow="sm"
        radius="md"
        selectionMode="single"
        onRowAction={(key: React.Key) => {
          const materialType = filteredMaterialTypes.find(
            (mt) => mt.id === key,
          );
          if (materialType) handleRowClick(materialType);
        }}
        classNames={{
          base: "max-h-[calc(100dvh-250px)] overflow-y-auto",
          row: "cursor-pointer hover:bg-table-row-hover transition-colors",
          wrapper: "max-h-[calc(100dvh-250px)]",
        }}
        bottomContent={
          totalPages > 1 ? (
            <div className="flex justify-center p-2">
              <Pagination
                page={page}
                total={totalPages}
                onChange={(p: number) => setPage(p)}
                showControls
              />
            </div>
          ) : null
        }
      >
        <TableHeader>
          {[
            <TableColumn
              key="name"
              allowsSorting
              sortDescriptor={sortDescriptor}
              onSortChange={setSortDescriptor}
            >
              Nombre
            </TableColumn>,
            !isMobile && (
              <TableColumn
                key="description"
                allowsSorting
                sortDescriptor={sortDescriptor}
                onSortChange={setSortDescriptor}
              >
                Description
              </TableColumn>
            ),
            !isMobile && (
              <TableColumn key="strategy">Estrategia de Medicion</TableColumn>
            ),
            <TableColumn key="actions" width={200}>
              Acciones
            </TableColumn>,
          ].filter(Boolean)}
        </TableHeader>
        <TableBody
          isLoading={isLoading}
          loadingContent={<Spinner />}
          emptyContent={
            searchQuery
              ? "No se encontraron tipos de materials con ese criterio"
              : "Sin tipos de materials"
          }
          items={filteredMaterialTypes}
        >
          {(item: MaterialType) => (
            <TableRow key={item.id}>
              {[
                <TableCell key="name">
                  <button
                    type="button"
                    className="text-left hover:text-primary transition-colors underline decoration-transparent hover:decoration-current"
                    onClick={() => handleRowClick(item)}
                  >
                    {item.name}
                  </button>
                </TableCell>,
                !isMobile && (
                  <TableCell key="description">
                    {item.description ? (
                      <Tooltip content={item.description}>
                        <span className="max-w-[200px] truncate block">
                          {item.description}
                        </span>
                      </Tooltip>
                    ) : (
                      <span className="text-default-400">-</span>
                    )}
                  </TableCell>
                ),
                !isMobile && (
                  <TableCell key="strategy">
                    {(() => {
                      const strategy = measurementStrategies.find(
                        (s) =>
                          s.name.toLowerCase() ===
                          item.measurement_strategy.toLowerCase(),
                      );
                      return strategy ? (
                        <Chip size="sm" color="primary" variant="flat">
                          {strategy.display_name}
                        </Chip>
                      ) : (
                        <span className="text-default-400">-</span>
                      );
                    })()}
                  </TableCell>
                ),
                <TableCell key="actions">
                  <div className="flex flex-col sm:flex-row gap-2">
                    <Button
                      size="sm"
                      color="default"
                      variant="flat"
                      type="button"
                      onPress={() => handleEditClick(item)}
                      isDisabled={editingMaterialType?.id === item.id}
                      className="text-primary hover:bg-primary/10"
                      startContent={
                        editingMaterialType?.id !== item.id ? (
                          <Pencil className="w-3 h-3" />
                        ) : undefined
                      }
                    >
                      {editingMaterialType?.id === item.id ? (
                        <Spinner size="sm" />
                      ) : (
                        "Edit"
                      )}
                    </Button>
                    <Button
                      size="sm"
                      color="danger"
                      variant="flat"
                      type="button"
                      onPress={() => handleDeleteClick(item)}
                      isDisabled={deletingMaterialType?.id === item.id}
                      startContent={
                        deletingMaterialType?.id !== item.id ? (
                          <Trash className="w-3 h-3" />
                        ) : undefined
                      }
                    >
                      {deletingMaterialType?.id === item.id ? (
                        <Spinner size="sm" />
                      ) : (
                        "Delete"
                      )}
                    </Button>
                  </div>
                </TableCell>,
              ].filter(Boolean)}
            </TableRow>
          )}
        </TableBody>
      </Table>

      <CreateMaterialTypeModal
        isOpen={showCreateModal}
        onOpenChange={setShowCreateModal}
        onSuccess={handleMaterialTypeCreated}
      />

      {/* Modal de Properties */}

      <CenteredModal
        isOpen={showPropertiesModal}
        onOpenChange={setShowPropertiesModal}
        size="lg"
        scrollBehavior="inside"
        backdrop="blur"
      >
        {(onClose) => (
          <>
            <ModalHeader className="flex flex-col gap-1 border-b border-divider">
              <div className="flex items-center gap-2">
                <Clipboard className="w-6 h-6 text-primary" />

                <div>
                  <h3 className="text-xl font-bold">
                    {selectedMaterialType?.name}
                  </h3>
                </div>
              </div>
            </ModalHeader>

            <ModalBody className="py-6">
              {selectedMaterialType && (
                <div className="space-y-4">
                  {selectedMaterialType.description && (
                    <div className="rounded-lg bg-default-50 p-4 border border-divider">
                      <h4 className="mb-2 font-semibold text-foreground">
                        Description
                      </h4>

                      <p className="text-default-600">
                        {selectedMaterialType.description}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </ModalBody>

            <ModalFooter className="border-t border-divider">
              <Button
                color="default"
                variant="flat"
                type="button"
                onPress={onClose}
              >
                Cerrar
              </Button>
            </ModalFooter>
          </>
        )}
      </CenteredModal>

      <CenteredModal
        isOpen={showEditModal}
        onOpenChange={setShowEditModal}
        onClose={() => setEditingMaterialType(null)}
        size="lg"
        scrollBehavior="inside"
        backdrop="blur"
      >
        {(onClose) => (
          <>
            <ModalHeader className="border-b border-divider">
              Edit Tipo de Material
            </ModalHeader>

            <ModalBody className="py-6">
              {editingMaterialType && (
                <EditMaterialType
                  materialType={editingMaterialType}
                  measurementStrategies={measurementStrategies}
                  onSuccess={handleEditSuccess}
                  onCancel={() => {
                    handleEditCancel();

                    onClose();
                  }}
                />
              )}
            </ModalBody>
          </>
        )}
      </CenteredModal>

      <CenteredModal
        isOpen={showDeleteConfirm}
        onOpenChange={setShowDeleteConfirm}
        onClose={() => setDeletingMaterialType(null)}
        size="md"
        backdrop="blur"
      >
        {(onClose) => (
          <>
            <ModalHeader className="border-b border-divider">
              Confirmar Eliminacion
            </ModalHeader>
            <ModalBody className="py-6">
              <div className="space-y-4">
                <p>
                  Estas seguro de que quieres delete el tipo de material{" "}
                  <strong>"{deletingMaterialType?.name}"</strong>?
                </p>
                <p className="text-sm text-default-500">
                  Esta accion no se puede deshacer.
                </p>
              </div>
            </ModalBody>
            <ModalFooter className="border-t border-divider">
              <Button
                color="default"
                variant="flat"
                type="button"
                onPress={() => {
                  handleDeleteCancel();
                  onClose();
                }}
              >
                Cancel
              </Button>
              <Button
                color="danger"
                variant="solid"
                type="button"
                onPress={() => {
                  handleDeleteConfirm();
                  onClose();
                }}
              >
                Delete
              </Button>
            </ModalFooter>
          </>
        )}
      </CenteredModal>

      <CenteredModal
        isOpen={showDetailModal}
        onOpenChange={setShowDetailModal}
        onClose={handleDetailModalClose}
        size="lg"
        scrollBehavior="inside"
        backdrop="blur"
      >
        {(onClose) => (
          <>
            <ModalHeader className="border-b border-divider">
              Detalles del Tipo de Material
            </ModalHeader>
            <ModalBody className="py-6">
              {selectedMaterialType && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">
                      Informacion General
                    </h3>
                    <div className="grid grid-cols-1 gap-4">
                      <div className="flex flex-col gap-1">
                        <span className="text-sm font-medium text-default-500">
                          Nombre
                        </span>
                        <p className="text-base font-medium">
                          {selectedMaterialType.name}
                        </p>
                      </div>
                      <div className="flex flex-col gap-1">
                        <span className="text-sm font-medium text-default-500">
                          Description
                        </span>
                        <p className="text-base">
                          {selectedMaterialType.description ||
                            "Sin description"}
                        </p>
                      </div>
                    </div>
                  </div>

                  <Divider />

                  <div>
                    <h3 className="text-lg font-semibold mb-2">
                      Especificaciones Tecnicas
                    </h3>
                    <div className="grid grid-cols-1 gap-4">
                      <div className="flex flex-col gap-1">
                        <span className="text-sm font-medium text-default-500">
                          Estrategia de Medicion
                        </span>
                        <p className="text-base flex items-center gap-2">
                          {(() => {
                            const strategy = measurementStrategies.find(
                              (s) =>
                                s.name.toLowerCase() ===
                                selectedMaterialType.measurement_strategy.toLowerCase(),
                            );
                            if (!strategy) return "No especificada";
                            return <>{strategy.display_name}</>;
                          })()}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </ModalBody>
            <ModalFooter className="border-t border-divider">
              <Button
                color="primary"
                variant="solid"
                type="button"
                onPress={() => handleEditClick(selectedMaterialType!)}
                className="font-semibold"
              >
                Edit Tipo de Material
              </Button>
              <Button
                color="default"
                variant="flat"
                type="button"
                onPress={() => {
                  handleDetailModalClose();
                  onClose();
                }}
              >
                Cerrar
              </Button>
            </ModalFooter>
          </>
        )}
      </CenteredModal>
    </div>
  );
};

type EditMaterialTypeProps = {
  materialType: MaterialType;
  measurementStrategies: MeasurementStrategy[];
  onSuccess: () => void;
  onCancel: () => void;
};

export const EditMaterialType: React.FC<EditMaterialTypeProps> = ({
  materialType,
  measurementStrategies,
  onSuccess,
  onCancel,
}) => {
  const { isAuthenticated, sessionReady } = useAuth();
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");

  // Form state initialized with material type data
  const [name, setName] = useState(materialType.name || "");
  const [description, setDescription] = useState(
    materialType.description || "",
  );
  const [measurementStrategy, setMeasurementStrategy] = useState(() => {
    const strategy = measurementStrategies.find(
      (s) =>
        s.name.toLowerCase() ===
        materialType.measurement_strategy.toLowerCase(),
    );
    return strategy ? strategy.name : materialType.measurement_strategy || "";
  });

  const selectedStrategyKeys = useMemo(() => {
    return (measurementStrategy || "").length > 0
      ? new Set([measurementStrategy])
      : new Set<string>();
  }, [measurementStrategy]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isAuthenticated && !sessionReady) return;

    setIsSaving(true);
    setError("");

    try {
      await apiClient.put(`/material-types/${materialType.id}`, {
        name,
        description,
        measurement_strategy: measurementStrategy,
      });

      onSuccess();
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      console.error("ERROR Error al actualizar tipo de material:", message);
      setError(message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="rounded-md bg-danger/20 p-3 text-sm text-danger border border-danger/30">
          {error}
        </div>
      )}

      <Input
        label="Nombre"
        placeholder="Ej: Acero"
        value={name}
        onValueChange={setName}
        isRequired
        description="Nombre unico del tipo de material"
      />

      <Textarea
        label="Description"
        placeholder="Ej: Material metalico utilizado en construccion"
        value={description}
        onValueChange={setDescription}
        description="Informacion adicional sobre el tipo de material (opcional)"
      />

      <Select
        label="Estrategia de Medicion"
        placeholder="Selecciona una estrategia de measurement"
        selectedKeys={selectedStrategyKeys}
        onSelectionChange={(keys: Set<React.Key> | "all") => {
          if (keys === "all") {
            return;
          }

          const selected = Array.from(keys)[0];
          setMeasurementStrategy(selected as string);
        }}
        description="Estrategia de measurement para este tipo de material"
      >
        {measurementStrategies.map((strategy) => (
          <SelectItem
            key={strategy.name}
            value={strategy.name}
            textValue={strategy.display_name}
          >
            <div className="flex flex-col gap-1">
              <span className="font-medium">{strategy.display_name}</span>
              <span className="text-xs text-default-500">
                {strategy.description}
              </span>
            </div>
          </SelectItem>
        ))}
      </Select>

      <Divider className="my-4" />

      <div className="flex justify-end gap-2">
        <Button color="default" variant="flat" type="button" onPress={onCancel}>
          Cancel
        </Button>
        <Button
          color="primary"
          variant="solid"
          type="submit"
          isLoading={isSaving}
          className="font-semibold"
          isDisabled={!name}
        >
          Actualizar Tipo de Material
        </Button>
      </div>
    </form>
  );
};
