import React, { useState } from "react";
import {
  Card,
  CardBody,
  CardHeader,
  Button,
  Divider,
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Chip,
} from "@heroui/react";
import { ArrowUp, ArrowDown, Trash2 } from "lucide-react";
import { Work } from "@/types/works";
import { workService } from "@services/workService";
import { AddProductToWorkModal } from "@components/common/AddProductToWorkModal";
import { StatusMessage, PrimaryButton } from "@components/common";

interface QuotationStep3Props {
  work: Work;
  onProductsAdded?: (updatedWork: Work) => void;
}

export const QuotationStep3: React.FC<QuotationStep3Props> = ({
  work,
  onProductsAdded,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleRemoveProduct = async (productId: string) => {
    try {
      await workService.removeProductFromWork(work.work_id, productId);
      setSuccess("Product removido");

      // Recargar work completo
      const updatedWork = await workService.getWorkById(work.work_id);
      onProductsAdded?.(updatedWork);
    } catch {
      setError("Error al remover product");
    }
  };

  const handleMoveProduct = async (
    currentIndex: number,
    direction: "up" | "down",
  ) => {
    if (!work.products) return;

    const newIndex = direction === "up" ? currentIndex - 1 : currentIndex + 1;

    if (newIndex < 0 || newIndex >= work.products.length) return;

    try {
      setIsLoading(true);
      const product1 = work.products[currentIndex];
      const product2 = work.products[newIndex];

      // Intercambiar los ordenes de ejecucion
      const temp = product1.execution_order;
      product1.execution_order = product2.execution_order;
      product2.execution_order = temp;

      // Llamar al servicio para actualizar los ordenes
      await Promise.all([
        workService.updateProductOrder(
          work.work_id,
          product1.product_id,
          product1.execution_order,
        ),
        workService.updateProductOrder(
          work.work_id,
          product2.product_id,
          product2.execution_order,
        ),
      ]);

      setSuccess("Orden actualizado exitosamente");

      // Recargar work completo
      const updatedWork = await workService.getWorkById(work.work_id);
      onProductsAdded?.(updatedWork);
    } catch {
      setError("Error al reordenar product");
    } finally {
      setIsLoading(false);
    }
  };

  // Ordenar products por execution_order
  const sortedProducts = [...(work.products || [])].sort(
    (a, b) => (a.execution_order || 0) - (b.execution_order || 0),
  );

  return (
    <>
      <div
        className={`transition-all duration-300 ${isModalOpen ? "blur-sm brightness-75" : ""}`}
      >
        <Card className="border-none shadow-sm bg-content1">
          <CardHeader className="flex flex-col items-start px-6 py-4 bg-primary/5">
            <div className="flex items-center gap-2 w-full">
              <h2 className="text-xl font-semibold text-primary">
                Paso 4: Gestionar Products
              </h2>
              {work.state === "QUOTED" && (
                <Chip
                  size="sm"
                  variant="flat"
                  color="warning"
                  startContent={<span></span>}
                  className="font-bold"
                >
                  Precios Congelados
                </Chip>
              )}
            </div>
            <p className="text-sm text-default-500 mt-1">
              Selecciona products para la quotation y ordena su ejecucion
            </p>
          </CardHeader>
          <Divider className="bg-divider" />
          <CardBody className="gap-4 p-6">
            {sortedProducts && sortedProducts.length > 0 ? (
              <>
                <div className="flex items-center justify-between mb-2">
                  <p className="font-semibold text-lg text-foreground">
                    Products Agregados
                  </p>
                  <Chip size="sm" variant="dot" color="primary">
                    {sortedProducts.length}{" "}
                    {sortedProducts.length !== 1 ? "products" : "product"}
                  </Chip>
                </div>
                <Table
                  aria-label="Tabla de products de la quotation"
                  removeWrapper
                  className="border-1 border-divider rounded-xl overflow-hidden"
                >
                  <TableHeader>
                    <TableColumn className="bg-default-100 text-default-600 font-bold">
                      ORDEN
                    </TableColumn>
                    <TableColumn className="bg-default-100 text-default-600 font-bold">
                      PRODUCTO
                    </TableColumn>
                    <TableColumn className="bg-default-100 text-default-600 font-bold text-center">
                      TIPO
                    </TableColumn>
                    <TableColumn className="bg-default-100 text-default-600 font-bold text-center">
                      CANTIDAD
                    </TableColumn>
                    <TableColumn className="bg-default-100 text-default-600 font-bold text-right">
                      PRECIO UNIT.
                    </TableColumn>
                    <TableColumn className="bg-default-100 text-default-600 font-bold text-right">
                      TOTAL
                    </TableColumn>
                    <TableColumn className="bg-default-100 text-default-600 font-bold text-center">
                      ACCIONES
                    </TableColumn>
                  </TableHeader>
                  <TableBody>
                    {sortedProducts.map((product, index) => {
                      let priceAmount = 0;
                      let priceCurrency = "COP";
                      let isSnapshotFrozen = false;

                      if (
                        work.state === "QUOTED" &&
                        (product.snapshot?.sale_price_amount ||
                          product.snapshot?.price_amount)
                      ) {
                        const price =
                          product.snapshot.sale_price_amount ||
                          product.snapshot.price_amount;
                        priceAmount =
                          typeof price === "string"
                            ? parseFloat(price)
                            : Number(price);
                        priceAmount = isNaN(priceAmount) ? 0 : priceAmount;
                        priceCurrency =
                          product.snapshot?.sale_price_currency ||
                          product.snapshot?.price_currency ||
                          "COP";
                        isSnapshotFrozen = true;
                      } else if (
                        product.current_price?.sale_price_amount ||
                        product.current_price?.amount
                      ) {
                        const price =
                          product.current_price.sale_price_amount ||
                          product.current_price.amount;
                        priceAmount =
                          typeof price === "string"
                            ? parseFloat(price)
                            : Number(price);
                        priceAmount = isNaN(priceAmount) ? 0 : priceAmount;
                        priceCurrency =
                          product.current_price?.sale_price_currency ||
                          product.current_price?.currency ||
                          "COP";
                        isSnapshotFrozen = false;
                      }

                      const totalPrice = priceAmount * product.quantity;
                      const rowKey = `${product.product_id}-${product.execution_order}`;

                      return (
                        <TableRow
                          key={rowKey}
                          className="border-b border-divider last:border-0 hover:bg-default-50 transition-colors"
                        >
                          <TableCell className="text-center">
                            <span className="font-bold text-primary bg-primary/10 w-8 h-8 flex items-center justify-center rounded-full mx-auto">
                              {index + 1}
                            </span>
                          </TableCell>
                          <TableCell>
                            <div>
                              <p className="font-semibold text-foreground">
                                {product.product_name}
                              </p>
                              <p className="text-[10px] font-mono text-default-400 uppercase">
                                {product.product_id.slice(-12)}
                              </p>
                            </div>
                          </TableCell>
                          <TableCell className="text-center">
                            <Chip
                              size="sm"
                              variant="flat"
                              className="capitalize text-[10px] font-bold"
                            >
                              {product.product_type}
                            </Chip>
                          </TableCell>
                          <TableCell className="text-center font-medium">
                            {product.quantity}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex flex-col items-end">
                              <span className="text-sm font-medium">
                                $
                                {priceAmount.toLocaleString("es-ES", {
                                  minimumFractionDigits: 2,
                                  maximumFractionDigits: 2,
                                })}
                              </span>
                              {isSnapshotFrozen && (
                                <span className="text-[9px] text-warning font-bold flex items-center gap-1">
                                  <span> CONGELADO</span>
                                </span>
                              )}
                            </div>
                          </TableCell>
                          <TableCell className="text-right font-bold text-foreground">
                            $
                            {totalPrice.toLocaleString("es-ES", {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            })}
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center justify-center gap-1">
                              <Button
                                isIconOnly
                                size="sm"
                                variant="light"
                                isDisabled={index === 0 || isLoading}
                                onPress={() => handleMoveProduct(index, "up")}
                              >
                                <ArrowUp className="w-4 h-4" />
                              </Button>
                              <Button
                                isIconOnly
                                size="sm"
                                variant="light"
                                isDisabled={
                                  index === sortedProducts.length - 1 ||
                                  isLoading
                                }
                                onPress={() => handleMoveProduct(index, "down")}
                              >
                                <ArrowDown className="w-4 h-4" />
                              </Button>
                              <Button
                                isIconOnly
                                size="sm"
                                color="danger"
                                variant="flat"
                                isLoading={isLoading}
                                onPress={() =>
                                  handleRemoveProduct(product.product_id)
                                }
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>

                {/* Mensajes de exito y error */}
                <div className="mt-4">
                  {success && (
                    <StatusMessage type="success">{success}</StatusMessage>
                  )}
                  {error && <StatusMessage type="error">{error}</StatusMessage>}
                </div>

                {/* Resumen de totales */}
                <div className="mt-6 bg-default-50 p-6 rounded-2xl border border-divider shadow-inner">
                  <div className="flex justify-between items-center mb-3">
                    <span className="text-default-500 font-medium">
                      Subtotal products:
                    </span>
                    <span className="font-semibold text-lg text-foreground">
                      $
                      {parseFloat(work.products_value || "0").toLocaleString(
                        "es-ES",
                        { minimumFractionDigits: 2, maximumFractionDigits: 2 },
                      )}
                    </span>
                  </div>
                  {work.tax > 0 && (
                    <>
                      <div className="flex justify-between items-center mb-4">
                        <span className="text-default-500 font-medium">
                          Ganancia Taller ({(work.tax * 100).toFixed(0)}%):
                        </span>
                        <span className="font-semibold text-lg text-foreground">
                          $
                          {(
                            parseFloat(work.products_value || "0") * work.tax
                          ).toLocaleString("es-ES", {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                          })}
                        </span>
                      </div>
                      <Divider className="my-4 opacity-50" />
                      <div className="flex justify-between items-center">
                        <span className="font-bold text-foreground text-lg uppercase tracking-wider">
                          Total Quotation:
                        </span>
                        <span className="font-bold text-2xl text-primary drop-shadow-sm">
                          $
                          {parseFloat(work.work_value || "0").toLocaleString(
                            "es-ES",
                            {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            },
                          )}
                        </span>
                      </div>
                    </>
                  )}
                </div>
              </>
            ) : (
              <div className="text-center py-12 bg-default-50 rounded-2xl border-2 border-dashed border-divider">
                <p className="text-default-400 font-medium">
                  No hay products agregados aun
                </p>
                <p className="text-xs text-default-300 mt-1">
                  Hace clic en "Agregar Product" para comenzar
                </p>
              </div>
            )}

            <Divider className="my-2 opacity-0" />

            <div className="flex flex-col sm:flex-row items-center gap-3">
              <AddProductToWorkModal
                workId={work.work_id}
                workStatus={work.state}
                onProductAdded={() => {
                  workService.getWorkById(work.work_id).then((updatedWork) => {
                    onProductsAdded?.(updatedWork);
                    setSuccess("Product agregado exitosamente");
                    setTimeout(() => setSuccess(null), 3000);
                  });
                }}
                onModalStateChange={setIsModalOpen}
              />

              {work.state === "DRAFT" && sortedProducts.length > 0 && (
                <PrimaryButton
                  isLoading={isLoading}
                  onPress={async () => {
                    try {
                      setIsLoading(true);
                      setError(null);
                      const quotedWork = await workService.generateQuote(
                        work.work_id,
                      );
                      onProductsAdded?.(quotedWork);
                      setSuccess("Quotation generada exitosamente!");
                      setTimeout(() => setSuccess(null), 3000);
                    } catch (err) {
                      setError("Error al generar la quotation");
                      console.error(err);
                    } finally {
                      setIsLoading(false);
                    }
                  }}
                  className="w-full sm:w-auto font-bold"
                >
                   GENERAR COTIZACION
                </PrimaryButton>
              )}
            </div>
          </CardBody>
        </Card>
      </div>
    </>
  );
};

export default QuotationStep3;
