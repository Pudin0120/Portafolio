import React, { useState, useEffect } from "react";
import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Input,
  Button,
  Pagination,
  Spinner,
  Card,
  CardBody,
  CardHeader,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure,
  Divider,
} from "@heroui/react";
import { Search, Trash2, Edit2, Eye, Play } from "lucide-react";
import { Work } from "@/types/works";
import { workService } from "@/services/workService";
import { EditQuotationDraft } from "./EditQuotationDraft";
import { ViewQuotation } from "./ViewQuotation";
import { ViewQuotationDetails } from "./ViewQuotationDetails";
import { useSidebar } from "@/context/SidebarContext";
import { CenteredModal } from "@components/common/CenteredModal";
import { useAuth } from "@/hooks/useAuth";

export const QuotationsList: React.FC = () => {
  const { userRole } = useAuth();
  const [quotations, setQuotations] = useState<Work[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchValue, setSearchValue] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedQuotation, setSelectedQuotation] = useState<Work | null>(null);
  const [viewMode, setViewMode] = useState<
    "list" | "edit" | "view" | "view-modal"
  >("list");
  const [workToDelete, setWorkToDelete] = useState<Work | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [workToStart, setWorkToStart] = useState<Work | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const {
    isOpen: isStartWorkOpen,
    onOpen: onStartWorkOpen,
    onOpenChange: onStartWorkOpenChange,
  } = useDisclosure();
  const { isOpen: sidebarOpen } = useSidebar();
  const itemsPerPage = 10;

  const loadQuotations = React.useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      // Cargar cotizaciones con estado DRAFT o QUOTED
      // Se realizan dos llamadas y se combinan los resultados
      const [draftResponse, quotedResponse] = await Promise.all([
        workService.getWorksByState("DRAFT"),
        workService.getWorksByState("QUOTED"),
      ]);

      const allWorks = [
        ...(draftResponse.works || []),
        ...(quotedResponse.works || []),
      ];

      setQuotations(allWorks);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Error al cargar las cotizaciones",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadQuotations();
  }, [loadQuotations]);

  const filteredQuotations = quotations.filter(
    (quotation) =>
      quotation.work_name?.toLowerCase().includes(searchValue.toLowerCase()) ||
      quotation.description?.toLowerCase().includes(searchValue.toLowerCase()),
  );

  const handleDeleteClick = (work: Work) => {
    setWorkToDelete(work);
    onOpen();
  };

  const handleViewClick = (work: Work) => {
    setSelectedQuotation(work);
    setViewMode("view-modal");
  };

  const handleConfirmDelete = async () => {
    if (!workToDelete) return;

    try {
      setIsDeleting(true);
      await workService.deleteWork(workToDelete.work_id);

      // Remover del estado local
      setQuotations((prev) =>
        prev.filter((q) => q.work_id !== workToDelete.work_id),
      );
      setWorkToDelete(null);
      onOpenChange();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Error al delete la quotation",
      );
    } finally {
      setIsDeleting(false);
    }
  };

  const handleStartWorkClick = (work: Work) => {
    setWorkToStart(work);
    onStartWorkOpen();
  };

  const handleConfirmStartWork = async () => {
    if (!workToStart) return;

    try {
      setIsStarting(true);
      await workService.startWork(workToStart.work_id);

      // Remover de la lista de cotizaciones ya que ya no es una quotation
      setQuotations((prev) =>
        prev.filter((q) => q.work_id !== workToStart.work_id),
      );
      setWorkToStart(null);
      onStartWorkOpenChange();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Error al iniciar el work",
      );
    } finally {
      setIsStarting(false);
    }
  };

  const pages = Math.ceil(filteredQuotations.length / itemsPerPage);
  const start = (currentPage - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  const items = filteredQuotations.slice(start, end);

  const getStateLabel = (state: string) => {
    const stateMap: Record<string, string> = {
      DRAFT: "Borrador",
      QUOTED: "Cotizada",
      IN_PROGRESS: "En Progreso",
      DELIVERED: "Entregada",
    };
    return stateMap[state] || state;
  };

  const getStateColor = (state: string) => {
    switch (state) {
      case "DRAFT":
        return { bg: "#fef3c7", color: "#92400e" };
      case "QUOTED":
        return { bg: "#dbeafe", color: "#1e40af" };
      case "IN_PROGRESS":
        return { bg: "#fef3c7", color: "#92400e" };
      case "DELIVERED":
        return { bg: "#d1fae5", color: "#065f46" };
      default:
        return { bg: "#f0fdf4", color: "#166534" };
    }
  };

  if (viewMode === "edit" && selectedQuotation) {
    return (
      <EditQuotationDraft
        workId={selectedQuotation.work_id}
        onBack={() => {
          setViewMode("list");
          setSelectedQuotation(null);
          loadQuotations();
        }}
      />
    );
  }

  if (viewMode === "view" && selectedQuotation) {
    return (
      <ViewQuotation
        workId={selectedQuotation.work_id}
        onBack={() => {
          setViewMode("list");
          setSelectedQuotation(null);
        }}
      />
    );
  }

  if (viewMode === "view-modal" && selectedQuotation) {
    return (
      <ViewQuotationDetails
        workId={selectedQuotation.work_id}
        onBack={() => {
          setViewMode("list");
          setSelectedQuotation(null);
        }}
      />
    );
  }

  return (
    <div className="space-y-4 mt-4">
      <Input
        isClearable
        className="w-full sm:max-w-xs"
        placeholder="Search quotation..."
        startContent={<Search className="w-4 h-4" />}
        value={searchValue}
        onValueChange={setSearchValue}
      />

      {items.length === 0 ? (
        <Card className="border-1 border-gray-200">
          <CardBody className="text-center py-10">
            <p className="text-gray-500">No hay cotizaciones registradas</p>
          </CardBody>
        </Card>
      ) : (
        <>
          <Table
            aria-label="Tabla de cotizaciones"
            bottomContent={
              pages > 1 ? (
                <div className="flex w-full justify-center">
                  <Pagination
                    isCompact
                    color="primary"
                    page={currentPage}
                    total={pages}
                    onChange={setCurrentPage}
                  />
                </div>
              ) : null
            }
          >
            <TableHeader>
              <TableColumn key="name" allowsSorting>
                Nombre
              </TableColumn>
              <TableColumn key="description">Description</TableColumn>
              <TableColumn key="client">Client</TableColumn>
              <TableColumn key="status">Estado</TableColumn>
              <TableColumn key="actions" align="center">
                Acciones
              </TableColumn>
            </TableHeader>
            <TableBody items={items} emptyContent={"No hay cotizaciones"}>
              {(item: Work) => (
                <TableRow key={item.work_id}>
                  <TableCell>{item.work_name}</TableCell>
                  <TableCell>{item.description}</TableCell>
                  <TableCell>{item.client_identification || "-"}</TableCell>
                  <TableCell>
                    <span
                      className="px-2 py-1 rounded-full text-xs font-medium"
                      style={{
                        backgroundColor: getStateColor(item.state).bg,
                        color: getStateColor(item.state).color,
                      }}
                    >
                      {getStateLabel(item.state)}
                    </span>
                  </TableCell>
                  <TableCell>
                    <div className="flex justify-center items-center gap-2">
                      <Button
                        isIconOnly
                        variant="light"
                        size="sm"
                        className="text-blue-600 hover:bg-blue-50"
                        title="Ver quotation"
                        onPress={() => handleViewClick(item)}
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      {item.state === "DRAFT" && (
                        <Button
                          isIconOnly
                          variant="light"
                          size="sm"
                          className="text-orange-600 hover:bg-orange-50"
                          title="Edit borrador"
                          onPress={() => {
                            setSelectedQuotation(item);
                            setViewMode("edit");
                          }}
                        >
                          <Edit2 className="w-4 h-4" />
                        </Button>
                      )}
                      {item.state === "QUOTED" && userRole === "MANAGER" && (
                        <Button
                          isIconOnly
                          variant="light"
                          size="sm"
                          className="text-green-600 hover:bg-green-50"
                          title="Iniciar work"
                          onPress={() => handleStartWorkClick(item)}
                        >
                          <Play className="w-4 h-4" />
                        </Button>
                      )}
                      <Button
                        isIconOnly
                        variant="light"
                        size="sm"
                        className="text-red-600 hover:bg-red-50"
                        title="Delete"
                        onPress={() => handleDeleteClick(item)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </>
      )}

      {/* Modal de confirmacion de eliminacion */}
      <CenteredModal
        isOpen={isOpen}
        onOpenChange={onOpenChange}
        backdrop="blur"
      >
        {(onClose: () => void) => (
          <>
            <ModalHeader className="flex flex-col gap-1 border-b border-divider">
               Delete Quotation
            </ModalHeader>
            <ModalBody className="py-6">
              <p>
                Estas seguro de que deseas delete la quotation{" "}
                <span className="font-semibold">{workToDelete?.work_name}</span>
                ?
              </p>
              <p className="text-sm text-default-500">
                Esta accion es irreversible y se perderan todos los datos
                asociados.
              </p>
              {(workToDelete?.state === "IN_PROGRESS" ||
                workToDelete?.state === "DELIVERED") && (
                <p className="text-danger font-semibold text-sm mt-2">
                  ERROR No se puede delete: Este work esta en estado{" "}
                  {workToDelete?.state === "IN_PROGRESS"
                    ? "En Progreso"
                    : "Entregado"}
                </p>
              )}
            </ModalBody>
            <ModalFooter className="border-t border-divider">
              <Button
                color="default"
                variant="flat"
                type="button"
                onPress={() => onOpenChange()}
                isDisabled={isDeleting}
              >
                Cancel
              </Button>
              <Button
                color="danger"
                variant="solid"
                type="button"
                isLoading={isDeleting}
                isDisabled={
                  isDeleting ||
                  workToDelete?.state === "IN_PROGRESS" ||
                  workToDelete?.state === "DELIVERED"
                }
                onPress={handleConfirmDelete}
              >
                Delete
              </Button>
            </ModalFooter>
          </>
        )}
      </CenteredModal>

      {/* Modal de confirmacion para iniciar work */}
      <CenteredModal
        isOpen={isStartWorkOpen}
        onOpenChange={onStartWorkOpenChange}
        backdrop="blur"
      >
        {(onClose: () => void) => (
          <>
            <ModalHeader className="flex flex-col gap-1 border-b border-divider">
               Iniciar Work
            </ModalHeader>
            <ModalBody className="py-6">
              <p>
                Deseas iniciar el work{" "}
                <span className="font-semibold">{workToStart?.work_name}</span>?
              </p>
              <p className="text-sm text-default-500">
                Se generaran todas las tasks automaticamente desde los
                products y el estado cambiara a "En Progreso".
              </p>
              <p className="text-sm text-warning-600 font-semibold mt-2">
                 Los products no podran ser modificados una vez iniciado el
                work.
              </p>
            </ModalBody>
            <ModalFooter className="border-t border-divider">
              <Button
                color="default"
                variant="flat"
                type="button"
                onPress={() => onStartWorkOpenChange()}
                isDisabled={isStarting}
              >
                Cancel
              </Button>
              <Button
                color="success"
                variant="solid"
                type="button"
                isLoading={isStarting}
                isDisabled={isStarting}
                onPress={handleConfirmStartWork}
              >
                Iniciar Work
              </Button>
            </ModalFooter>
          </>
        )}
      </CenteredModal>
    </div>
  );
};
