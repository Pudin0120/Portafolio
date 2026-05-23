import React, { useState, useEffect, useCallback } from "react";
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
  useDisclosure,
  ModalHeader,
  ModalBody,
  ModalFooter,
} from "@heroui/react";
import { Search, Eye, Edit2, CheckCircle2 } from "lucide-react";
import { Work } from "@/types/works";
import { Client } from "@/types/clients";
import { workService } from "@/services/workService";
import { clientService } from "@/services/clientService";
import { WorkDetailModal } from "./WorkDetailModal";
import { useAuth } from "@/hooks/useAuth";
import { ApiError } from "@/services/apiClient";
import { CenteredModal } from "@components/common/CenteredModal";

interface WorksListProps {
  state: "IN_PROGRESS" | "DELIVERED";
  onEditWork?: (workId: string) => void;
}

export const WorksList: React.FC<WorksListProps> = ({ state, onEditWork }) => {
  const [works, setWorks] = useState<Work[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchValue, setSearchValue] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedWork, setSelectedWork] = useState<Work | null>(null);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [workToDeliver, setWorkToDeliver] = useState<Work | null>(null);
  const [isDelivering, setIsDelivering] = useState(false);
  const [deliveryError, setDeliveryError] = useState<string | null>(null);

  const {
    isOpen: isDetailOpen,
    onOpen: onOpenDetail,
    onOpenChange: onDetailOpenChange,
  } = useDisclosure();

  const {
    isOpen: isDeliverModalOpen,
    onOpen: onOpenDeliverModal,
    onOpenChange: onDeliverModalOpenChange,
  } = useDisclosure();

  const { userRole } = useAuth();
  const itemsPerPage = 10;

  const loadWorks = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await workService.getWorksByState(state);
      setWorks(response.works || []);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Error al cargar los works",
      );
    } finally {
      setIsLoading(false);
    }
  }, [state]);

  useEffect(() => {
    loadWorks();
  }, [loadWorks]);

  const getStateLabel = (stateStr: string) => {
    const stateMap: Record<string, string> = {
      DRAFT: "Borrador",
      QUOTED: "Cotizada",
      IN_PROGRESS: "En Progreso",
      DELIVERED: "Entregado",
    };
    return stateMap[stateStr] || stateStr;
  };

  const getStateColor = (stateStr: string) => {
    switch (stateStr) {
      case "IN_PROGRESS":
        return { bg: "#fef3c7", color: "#92400e" };
      case "DELIVERED":
        return { bg: "#d1fae5", color: "#065f46" };
      default:
        return { bg: "#f0fdf4", color: "#166534" };
    }
  };

  const handleViewWork = async (work: Work) => {
    try {
      const [fullWork, client] = await Promise.all([
        workService.getWorkById(work.work_id),
        clientService.getClientById(work.client_identification),
      ]);
      setSelectedWork(fullWork);
      setSelectedClient(client);
      onOpenDetail();
    } catch (err) {
      console.error("Error loading work details:", err);
    }
  };

  const handleDeliverClick = (work: Work) => {
    setWorkToDeliver(work);
    setDeliveryError(null);
    onOpenDeliverModal();
  };

  const handleConfirmDeliver = async () => {
    if (!workToDeliver) return;

    try {
      setIsDelivering(true);
      setDeliveryError(null);
      await workService.deliverWork(workToDeliver.work_id);

      // Recargar la lista de works despues de entregar
      await loadWorks();

      // Cerrar el modal
      onDeliverModalOpenChange();
      setWorkToDeliver(null);
    } catch (err) {
      // Manejar especificamente el error 400 (tasks pendientes)
      if (err instanceof ApiError && err.status === 400) {
        setDeliveryError(
          "No se puede entregar el work porque aun hay tasks pendientes. " +
            "Todas las tasks deben estar finalizadas para poder realizar la entrega.",
        );
      } else {
        const errorMessage =
          err instanceof Error ? err.message : "Error al entregar el work";
        setDeliveryError(errorMessage);
      }
    } finally {
      setIsDelivering(false);
    }
  };

  const isManager = userRole === "MANAGER";
  const filteredWorks = works.filter(
    (work) =>
      work.work_name?.toLowerCase().includes(searchValue.toLowerCase()) ||
      work.description?.toLowerCase().includes(searchValue.toLowerCase()) ||
      work.client_identification
        ?.toLowerCase()
        .includes(searchValue.toLowerCase()),
  );

  const pages = Math.ceil(filteredWorks.length / itemsPerPage);
  const start = (currentPage - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  const items = filteredWorks.slice(start, end);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-96">
        <Spinner label="Cargando works..." />
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-1 border-red-200 bg-red-50">
        <CardBody>
          <p className="text-red-600">{error}</p>
          <Button
            color="warning"
            className="mt-4 w-fit"
            type="button"
            onPress={loadWorks}
          >
            Reintentar
          </Button>
        </CardBody>
      </Card>
    );
  }

  return (
    <div className="space-y-4 mt-4">
      <Input
        isClearable
        className="w-full sm:max-w-xs"
        placeholder="Search work..."
        startContent={<Search className="w-4 h-4" />}
        value={searchValue}
        onValueChange={setSearchValue}
      />

      {items.length === 0 ? (
        <Card className="border-1 border-gray-200">
          <CardBody className="text-center py-10">
            <p className="text-gray-500">No hay works registrados</p>
          </CardBody>
        </Card>
      ) : (
        <>
          <Table
            aria-label="Tabla de works"
            bottomContent={
              pages > 1 ? (
                <div className="flex w-full justify-center">
                  <Pagination
                    isCompact
                    color="warning"
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
            <TableBody items={items} emptyContent={"No hay works"}>
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
                        title="Ver work"
                        type="button"
                        onPress={() => handleViewWork(item)}
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      {state === "IN_PROGRESS" && (
                        <Button
                          isIconOnly
                          variant="light"
                          size="sm"
                          className="text-orange-600 hover:bg-orange-50"
                          title="Edit"
                          type="button"
                          onPress={() => onEditWork?.(item.work_id)}
                        >
                          <Edit2 className="w-4 h-4" />
                        </Button>
                      )}
                      {state === "IN_PROGRESS" && isManager && (
                        <Button
                          isIconOnly
                          variant="light"
                          size="sm"
                          className="text-green-600 hover:bg-green-50"
                          title="Entregar work"
                          type="button"
                          onPress={() => handleDeliverClick(item)}
                        >
                          <CheckCircle2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </>
      )}

      <WorkDetailModal
        isOpen={isDetailOpen}
        onOpenChange={onDetailOpenChange}
        work={selectedWork}
        client={selectedClient}
      />

      <CenteredModal
        isOpen={isDeliverModalOpen}
        onOpenChange={onDeliverModalOpenChange}
        backdrop="blur"
      >
        {() => (
          <>
            <ModalHeader className="flex flex-col gap-1 border-b border-divider">
              Confirmar Entrega de Work
            </ModalHeader>
            <ModalBody className="py-6">
              {deliveryError && (
                <Card className="border-1 border-red-200 bg-red-50 mb-4">
                  <CardBody>
                    <p className="text-red-600 text-sm">{deliveryError}</p>
                  </CardBody>
                </Card>
              )}
              <div className="space-y-3">
                <p>
                  Estas seguro de que deseas marcar como entregado el work{" "}
                  <span className="font-semibold">
                    "{workToDeliver?.work_name}"
                  </span>
                  ?
                </p>
                <Card className="border-1 border-warning-200 bg-warning-50">
                  <CardBody className="py-3">
                    <p className="text-sm text-warning-800">
                       <strong>Importante:</strong> Todas las tasks deben
                      estar finalizadas para poder entregar el work. Si hay
                      tasks pendientes, la entrega sera rechazada.
                    </p>
                  </CardBody>
                </Card>
              </div>
            </ModalBody>
            <ModalFooter className="border-t border-divider">
              <Button
                variant="flat"
                type="button"
                onPress={() => onDeliverModalOpenChange()}
                isDisabled={isDelivering}
              >
                Cancel
              </Button>
              <Button
                color="success"
                type="button"
                onPress={handleConfirmDeliver}
                isLoading={isDelivering}
              >
                Confirmar Entrega
              </Button>
            </ModalFooter>
          </>
        )}
      </CenteredModal>
    </div>
  );
};
