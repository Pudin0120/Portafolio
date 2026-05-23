import React, { useEffect, useState, useMemo } from "react";
import { Plus, Pencil, Trash } from "lucide-react";
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
  Pagination,
  Tooltip,
  Divider,
  Input,
} from "@heroui/react";
import { Composition, CompositionsResponse } from "@/types/products";
import { EditComposition } from "./CreateComposition";
import { CreateCompositionModal } from "./CreateCompositionModal";
import { CenteredModal } from "@components/common/CenteredModal";
import { Search } from "lucide-react";

type SortDescriptor = {
  column: string;
  direction: "ascending" | "descending";
};

type CompositionsManagerProps = Record<string, never>;

const PAGE_SIZE = 20;

export const CompositionsManager: React.FC<CompositionsManagerProps> = () => {
  const { isAuthenticated, sessionReady } = useAuth();
  const isMobile = useIsMobile();
  const { connectionEpoch } = useConnectivity();
  const [isLoading, setIsLoading] = useState(false);
  const [compositions, setCompositions] = useState<Composition[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [deletingComposition, setDeletingComposition] =
    useState<Composition | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteSuccess, setDeleteSuccess] = useState<string | null>(null);
  const [editingComposition, setEditingComposition] =
    useState<Composition | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editSuccess, setEditSuccess] = useState<string | null>(null);
  const [selectedComposition, setSelectedComposition] =
    useState<Composition | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [sortDescriptor, setSortDescriptor] = useState<SortDescriptor>({
    column: "name",
    direction: "ascending",
  });

  // Calcular total de paginas
  const totalPages = useMemo(() => {
    if (total === 0) return 1;
    return Math.max(1, Math.ceil(total / PAGE_SIZE));
  }, [total]);

  const handleSearchChange = (value: string) => {
    setSearchQuery(value);
    setPage(1);
  };

  const fetchCompositions = React.useCallback(async () => {
    if (!isAuthenticated && !sessionReady) return;
    setIsLoading(true);
    try {
      const searchParams = new URLSearchParams();
      searchParams.set("limit", String(PAGE_SIZE));
      searchParams.set("offset", String((page - 1) * PAGE_SIZE));

      const data = await apiClient.get<CompositionsResponse>(
        `/compositions/?${searchParams.toString()}`,
      );

      let compositionsArray: Composition[] = [];
      let totalCount: number = 0;

      if (Array.isArray(data)) {
        compositionsArray = data;
        totalCount = data.length;
      } else if (data) {
        compositionsArray = data.compositions || data.materials || [];
        totalCount = data.total || compositionsArray.length;
      }

      setCompositions(compositionsArray);
      setTotal(totalCount);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated, sessionReady, page]);

  useEffect(() => {
    fetchCompositions();
  }, [fetchCompositions, connectionEpoch]);

  const handleCompositionCreated = () => {
    setShowCreateModal(false);
    setPage(1);
    fetchCompositions();
  };

  const handleDeleteClick = (composition: Composition) => {
    setDeletingComposition(composition);
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deletingComposition || (!isAuthenticated && !sessionReady)) return;

    try {
      await apiClient.delete(`/compositions/${deletingComposition.id}`);
      setDeleteSuccess(
        `Composicion "${deletingComposition.name}" eliminada exitosamente`,
      );
      setTimeout(() => setDeleteSuccess(null), 3000);
      fetchCompositions();
    } catch (err) {
      console.error("ERROR Error al delete composicion:", err);
    } finally {
      setShowDeleteConfirm(false);
      setDeletingComposition(null);
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteConfirm(false);
    setDeletingComposition(null);
  };

  const handleEditClick = (composition: Composition) => {
    setEditingComposition(composition);
    setShowEditModal(true);
  };

  const handleEditSuccess = () => {
    setShowEditModal(false);
    setEditingComposition(null);
    setEditSuccess("Composicion actualizada exitosamente");
    setTimeout(() => setEditSuccess(null), 3000);
    fetchCompositions();
  };

  const handleEditCancel = () => {
    setShowEditModal(false);
    setEditingComposition(null);
  };

  const handleCompositionClick = (composition: Composition) => {
    setSelectedComposition(composition);
    setShowDetailModal(true);
  };

  const handleDetailModalClose = () => {
    setShowDetailModal(false);
    setSelectedComposition(null);
  };

  // Filtrar y ordenar composiciones
  const filteredCompositions = useMemo(() => {
    let result = compositions;

    // Aplicar busqueda
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = compositions.filter((composition) => {
        return (
          composition.name?.toLowerCase().includes(query) ||
          composition.description?.toLowerCase().includes(query)
        );
      });
    }

    // Aplicar ordenamiento
    if (sortDescriptor.column) {
      result = [...result].sort((a, b) => {
        const column = sortDescriptor.column as keyof Composition;
        const aValue = a[column];
        const bValue = b[column];

        if (aValue == null && bValue == null) return 0;
        if (aValue == null)
          return sortDescriptor.direction === "ascending" ? 1 : -1;
        if (bValue == null)
          return sortDescriptor.direction === "ascending" ? -1 : 1;

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
  }, [compositions, searchQuery, sortDescriptor]);

  return (
    <div className="space-y-4">
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
            placeholder="Search por nombre o description..."
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
            Create Composicion
          </Button>
        </div>
      </div>

      <Table
        key={isMobile ? "mobile" : "desktop"}
        aria-label="Tabla de composiciones"
        isCompact={isMobile}
        isHeaderSticky
        isStriped
        removeWrapper
        shadow="sm"
        radius="md"
        selectionMode="single"
        onRowAction={(key: React.Key) => {
          const composition = filteredCompositions.find((c) => c.id === key);
          if (composition) handleCompositionClick(composition);
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
            !isMobile && <TableColumn key="details">Detalles</TableColumn>,
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
              ? "No se encontraron composiciones con ese criterio"
              : "Sin composiciones"
          }
          items={filteredCompositions}
        >
          {(item: Composition) => (
            <TableRow key={item.id}>
              {[
                <TableCell key="name" className="font-semibold">
                  {item.name}
                </TableCell>,
                !isMobile && (
                  <TableCell key="details">
                    <div className="flex items-center gap-2">
                      {item.description ? (
                        <Tooltip content={item.description}>
                          <span className="text-default-400 text-xs italic truncate max-w-[250px]">
                            {item.description}
                          </span>
                        </Tooltip>
                      ) : (
                        <span className="text-default-300">-</span>
                      )}
                    </div>
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
                      isDisabled={editingComposition?.id === item.id}
                      className="text-primary hover:bg-primary/10"
                      startContent={
                        editingComposition?.id !== item.id ? (
                          <Pencil className="w-3 h-3" />
                        ) : undefined
                      }
                    >
                      {editingComposition?.id === item.id ? (
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
                      isDisabled={deletingComposition?.id === item.id}
                      startContent={
                        deletingComposition?.id !== item.id ? (
                          <Trash className="w-3 h-3" />
                        ) : undefined
                      }
                    >
                      {deletingComposition?.id === item.id ? (
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

      {/* Modal reutilizable para create composicion */}
      <CreateCompositionModal
        isOpen={showCreateModal}
        onOpenChange={setShowCreateModal}
        onSuccess={handleCompositionCreated}
      />

      {/* Modal de detalles */}
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
              Detalles de la Composicion
            </ModalHeader>
            <ModalBody className="py-6">
              {selectedComposition && (
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
                          {selectedComposition.name}
                        </p>
                      </div>
                      <div className="flex flex-col gap-1">
                        <span className="text-sm font-medium text-default-500">
                          Description
                        </span>
                        <p className="text-base">
                          {selectedComposition.description || "Sin description"}
                        </p>
                      </div>
                    </div>
                  </div>

                  <Divider />

                  <div>
                    <h3 className="text-lg font-semibold mb-2">
                      Especificaciones
                    </h3>
                    <div className="grid grid-cols-1 gap-4">
                      <div className="flex flex-col gap-1">
                        <span className="text-sm font-medium text-default-500">
                          ID
                        </span>
                        <p className="text-base">{selectedComposition.id}</p>
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
                onPress={() => handleEditClick(selectedComposition!)}
                className="font-semibold"
              >
                Edit Composicion
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

      {/* Modal de edicion */}
      <CenteredModal
        isOpen={showEditModal}
        onOpenChange={setShowEditModal}
        onClose={() => setEditingComposition(null)}
        size="2xl"
        scrollBehavior="inside"
        backdrop="blur"
      >
        {(onClose) => (
          <>
            <ModalHeader className="border-b border-divider">
              Edit Composicion
            </ModalHeader>
            <ModalBody className="py-6">
              {editingComposition && (
                <EditComposition
                  composition={editingComposition}
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

      {/* Modal de confirmacion de eliminacion */}
      <CenteredModal
        isOpen={showDeleteConfirm}
        onOpenChange={setShowDeleteConfirm}
        onClose={() => setDeletingComposition(null)}
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
                  Estas seguro de que quieres delete la composicion{" "}
                  <strong>"{deletingComposition?.name}"</strong>?
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
    </div>
  );
};
