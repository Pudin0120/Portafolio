import React from "react";
import {
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  Divider,
  Card,
  CardBody,
  Chip,
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
} from "@heroui/react";
import { Work } from "@/types/works";
import { Client } from "@/types/clients";
import {
  getTaskStateLabel,
  getTaskStateColor,
  getProductStateLabel,
  getProductStateColor,
} from "@/utils/translations";
import { CenteredModal } from "@components/common/CenteredModal";

interface WorkDetailModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  work: Work | null;
  client: Client | null;
}

export const WorkDetailModal: React.FC<WorkDetailModalProps> = ({
  isOpen,
  onOpenChange,
  work,
  client,
}) => {
  if (!work) return null;

  const getStatusColor = (status: string) => {
    switch (status) {
      case "IN_PROGRESS":
        return "warning";
      case "DELIVERED":
        return "success";
      default:
        return "default";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "IN_PROGRESS":
        return "En Progreso";
      case "DELIVERED":
        return "Entregado";
      default:
        return status;
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return "-";

    try {
      return new Date(dateString).toLocaleDateString("es-ES", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    } catch {
      return dateString;
    }
  };

  return (
    <CenteredModal
      isOpen={isOpen}
      onOpenChange={onOpenChange}
      size="2xl"
      scrollBehavior="inside"
      classNames={{
        base: "bg-surface-elevated",
        backdrop: "bg-black/50",
        closeButton: "text-brand-orange-600 hover:bg-brand-orange-50",
      }}
    >
      {(onClose: () => void) => (
        <>
          <ModalHeader className="flex flex-col gap-1 border-b border-divider">
            <div className="flex w-full flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <h2 className="text-xl font-bold text-default-800">
                {work.work_name}
              </h2>
              <Chip
                color={getStatusColor(work.state)}
                variant="flat"
                size="sm"
                className="font-medium"
              >
                {getStatusLabel(work.state)}
              </Chip>
            </div>
          </ModalHeader>

          <ModalBody className="py-4 sm:py-6">
            <div className="space-y-4">
              <div>
                <span className="mb-2 block text-sm font-semibold text-default-600">
                  Client
                </span>
                <div className="space-y-1">
                  <p className="font-medium text-default-900">
                    {client
                      ? `${client.first_name} ${client.last_name}`
                      : work.client_identification}
                  </p>
                  {client?.address && (
                    <p className="text-sm text-default-600">{client.address}</p>
                  )}
                  {client?.email && (
                    <p className="text-sm text-default-600">{client.email}</p>
                  )}
                  {client?.phone && (
                    <p className="text-sm text-default-600">{client.phone}</p>
                  )}
                </div>
              </div>

              <div>
                <span className="mb-2 block text-sm font-semibold text-default-600">
                  Description
                </span>
                <p className="text-default-700">
                  {work.description || "Sin description"}
                </p>
              </div>

              <Divider />

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <Card className="border-1 border-default-200 bg-default-100">
                  <CardBody className="py-3">
                    <span className="mb-1 block text-xs font-medium text-default-600">
                      Fecha de inicio
                    </span>
                    <p className="text-sm font-semibold text-default-900">
                      {formatDate(work.start_date)}
                    </p>
                  </CardBody>
                </Card>

                <Card className="border-1 border-default-200 bg-default-100">
                  <CardBody className="py-3">
                    <span className="mb-1 block text-xs font-medium text-default-600">
                      Entrega aprox.
                    </span>
                    <p className="text-sm font-semibold text-default-900">
                      {formatDate(work.end_aprox_delivery_date)}
                    </p>
                  </CardBody>
                </Card>

                {work.end_delivery_date && (
                  <Card className="border-1 border-success-200 bg-success-100">
                    <CardBody className="py-3">
                      <span className="mb-1 block text-xs font-medium text-default-600">
                        Entrega real
                      </span>
                      <p className="text-sm font-semibold text-default-900">
                        {formatDate(work.end_delivery_date)}
                      </p>
                    </CardBody>
                  </Card>
                )}
              </div>

              <Divider />

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <Card className="border-1 border-default-200 bg-default-100">
                  <CardBody className="py-3">
                    <span className="mb-1 block text-xs font-medium text-default-600">
                      Deposito
                    </span>
                    <p className="text-sm font-semibold text-default-900">
                      {work.deposit_amount} {work.deposit_currency}
                    </p>
                  </CardBody>
                </Card>

                <Card className="border-1 border-default-200 bg-default-100">
                  <CardBody className="py-3">
                    <span className="mb-1 block text-xs font-medium text-default-600">
                      Valor products
                    </span>
                    <p className="text-sm font-semibold text-default-900">
                      {work.products_value}
                    </p>
                  </CardBody>
                </Card>

                <Card className="border-1 border-default-200 bg-default-100">
                  <CardBody className="py-3">
                    <span className="mb-1 block text-xs font-medium text-default-600">
                      Valor total
                    </span>
                    <p className="text-sm font-semibold text-default-900">
                      {work.work_value}
                    </p>
                  </CardBody>
                </Card>

                <Card className="border-1 border-warning-200 bg-warning-100">
                  <CardBody className="py-3">
                    <span className="mb-1 block text-xs font-medium text-default-600">
                      Impuesto
                    </span>
                    <p className="text-sm font-semibold text-default-900">
                      {work.tax * 100}%
                    </p>
                  </CardBody>
                </Card>
              </div>

              <Card className="border-1 border-warning-200 bg-warning-50">
                <CardBody className="py-4">
                  <div className="mb-2 flex items-center justify-between gap-3">
                    <span className="block text-sm font-semibold text-default-700">
                      Progreso del work
                    </span>
                    <p className="text-sm font-bold text-warning-600">
                      {work.completion_percentage}%
                    </p>
                  </div>
                  <div className="h-2 w-full rounded-full bg-default-200">
                    <div
                      className="h-2 rounded-full bg-warning-600 transition-all duration-300"
                      style={{ width: `${work.completion_percentage}%` }}
                    />
                  </div>
                </CardBody>
              </Card>

              <Divider />

              {work.products && work.products.length > 0 && (
                <div>
                  <span className="mb-3 block text-sm font-semibold text-default-700">
                    Products ({work.products.length})
                  </span>
                  <div className="overflow-x-auto">
                    <Table
                      aria-label="Tabla de products del work"
                      className="min-w-[560px] bg-surface-elevated"
                      classNames={{
                        table: "bg-surface-elevated",
                        tr: "border-b border-surface-border",
                        td: "py-3",
                      }}
                    >
                      <TableHeader>
                        <TableColumn className="bg-warning-100">
                          Product
                        </TableColumn>
                        <TableColumn className="bg-warning-100">
                          Quantity
                        </TableColumn>
                        <TableColumn className="bg-warning-100">
                          Estado
                        </TableColumn>
                      </TableHeader>
                      <TableBody>
                        {work.products.map((product) => (
                          <TableRow key={product.product_id}>
                            <TableCell>
                              <div className="flex flex-col">
                                <p className="font-medium text-default-900">
                                  {product.product_name}
                                </p>
                                <p className="text-xs text-default-500">
                                  {product.product_type}
                                </p>
                              </div>
                            </TableCell>
                            <TableCell>
                              <p className="font-medium text-default-900">
                                {product.quantity}
                              </p>
                            </TableCell>
                            <TableCell>
                              <Chip
                                size="sm"
                                variant="flat"
                                className="font-medium"
                                color={getProductStateColor(product.state)}
                              >
                                {getProductStateLabel(product.state)}
                              </Chip>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </div>
              )}

              {work.tasks && work.tasks.length > 0 && (
                <div>
                  <Divider className="my-4" />
                  <span className="mb-3 block text-sm font-semibold text-default-700">
                    Tasks ({work.tasks.length})
                  </span>
                  <div className="overflow-x-auto">
                    <Table
                      aria-label="Tabla de tasks del work"
                      className="min-w-[560px] bg-surface-elevated"
                      classNames={{
                        table: "bg-surface-elevated",
                        tr: "border-b border-surface-border",
                        td: "py-3",
                      }}
                    >
                      <TableHeader>
                        <TableColumn className="bg-warning-100">
                          Task
                        </TableColumn>
                        <TableColumn className="bg-warning-100">
                          Valor
                        </TableColumn>
                        <TableColumn className="bg-warning-100">
                          Estado
                        </TableColumn>
                      </TableHeader>
                      <TableBody>
                        {work.tasks.map((task) => (
                          <TableRow key={task.task_id}>
                            <TableCell>
                              <div className="flex flex-col">
                                <p className="font-medium text-default-900">
                                  {task.task_name}
                                </p>
                                <p className="text-xs text-default-500">
                                  {task.description}
                                </p>
                              </div>
                            </TableCell>
                            <TableCell>
                              <p className="font-medium text-default-900">
                                {task.estimated_value_formatted}
                              </p>
                            </TableCell>
                            <TableCell>
                              <Chip
                                size="sm"
                                variant="flat"
                                className="font-medium"
                                color={getTaskStateColor(task.state)}
                              >
                                {getTaskStateLabel(task.state)}
                              </Chip>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </div>
              )}
            </div>
          </ModalBody>

          <ModalFooter className="border-t border-divider">
            <Button
              color="default"
              variant="flat"
              onPress={onClose}
              className="font-medium"
              type="button"
            >
              Cerrar
            </Button>
          </ModalFooter>
        </>
      )}
    </CenteredModal>
  );
};
