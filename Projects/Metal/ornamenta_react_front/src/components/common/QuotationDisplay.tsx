import React, { useCallback, useMemo, useState } from "react";
import { Button, Divider } from "@heroui/react";
import { ArrowLeft, Download, Eye, EyeOff, Printer } from "lucide-react";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import { Work } from "@/types/works";

interface ProductDetailComponent {
  product_id: string;
  product_name: string;
  quantity: number;
  price?: number;
}

interface QuotationDisplayProps {
  work: Work;
  onBack?: () => void;
  clientName?: string;
  workAddress?: string;
  userName?: string;
  productDetails?: Record<
    string,
    {
      components?: ProductDetailComponent[];
    }
  >;
  showBackButton?: boolean;
  showHeader?: boolean;
  className?: string;
}

const PRIMARY_RGB: [number, number, number] = [230, 126, 34];

export const QuotationDisplay: React.FC<QuotationDisplayProps> = ({
  work,
  onBack,
  clientName = "No disponible",
  workAddress = "No disponible",
  userName = "No disponible",
  productDetails = {},
  showBackButton = true,
  showHeader = true,
  className = "",
}) => {
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  const [isClientView, setIsClientView] = useState(true);
  const [pdfError, setPdfError] = useState<string | null>(null);

  const formatCurrency = (amount: number): string =>
    new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: "COP",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);

  const getStateLabel = useCallback((state: string) => {
    const stateMap: Record<
      string,
      {
        label: string;
        color:
          | "default"
          | "primary"
          | "secondary"
          | "success"
          | "warning"
          | "danger";
      }
    > = {
      DRAFT: { label: "Borrador", color: "warning" },
      QUOTED: { label: "Cotizada", color: "primary" },
      IN_PROGRESS: { label: "En progreso", color: "secondary" },
      DELIVERED: { label: "Entregada", color: "success" },
    };

    return stateMap[state] ?? { label: state, color: "default" };
  }, []);

  const stateInfo = useMemo(
    () => getStateLabel(work.state),
    [getStateLabel, work.state],
  );

  const generatePDF = async (download: boolean = true) => {
    try {
      setIsGeneratingPDF(true);
      setPdfError(null);

      const doc = new jsPDF({
        orientation: "portrait",
        unit: "mm",
        format: "a4",
      });

      let yPosition = 12;
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const margin = 12;
      const contentWidth = pageWidth - 2 * margin;

      doc.setFillColor(PRIMARY_RGB[0], PRIMARY_RGB[1], PRIMARY_RGB[2]);
      doc.rect(0, 0, pageWidth, 28, "F");

      doc.setFont("Helvetica", "bold");
      doc.setFontSize(32);
      doc.setTextColor(255, 255, 255);
      doc.text("COTIZACION", margin, 22);

      doc.setFont("Helvetica", "normal");
      doc.setFontSize(7);
      doc.text("ID:", pageWidth - margin - 50, 16);
      doc.setFont("Helvetica", "bold");
      doc.setFontSize(8);
      doc.text(work.work_id, pageWidth - margin - 50, 23);

      yPosition = 35;

      const col1X = margin;
      const col2X = pageWidth / 2 + 6;
      const colWidth = (pageWidth - 2 * margin) / 2 - 2;

      doc.setFont("Helvetica", "bold");
      doc.setFontSize(9);
      doc.setTextColor(PRIMARY_RGB[0], PRIMARY_RGB[1], PRIMARY_RGB[2]);
      doc.text("CLIENTE", col1X, yPosition);
      doc.setFont("Helvetica", "normal");
      doc.setFontSize(10);
      doc.setTextColor(31, 41, 55);
      doc.text(doc.splitTextToSize(clientName, colWidth - 2), col1X, yPosition + 6);

      doc.setFont("Helvetica", "bold");
      doc.setFontSize(9);
      doc.setTextColor(PRIMARY_RGB[0], PRIMARY_RGB[1], PRIMARY_RGB[2]);
      doc.text("FECHA", col2X, yPosition);
      doc.setFont("Helvetica", "normal");
      doc.setFontSize(10);
      doc.setTextColor(31, 41, 55);
      doc.text(
        new Date().toLocaleDateString("es-CO", {
          year: "numeric",
          month: "long",
          day: "numeric",
        }),
        col2X,
        yPosition + 6,
      );

      yPosition += 18;

      doc.setFont("Helvetica", "bold");
      doc.setFontSize(9);
      doc.setTextColor(PRIMARY_RGB[0], PRIMARY_RGB[1], PRIMARY_RGB[2]);
      doc.text("TRABAJO", col1X, yPosition);
      doc.setFont("Helvetica", "normal");
      doc.setFontSize(10);
      doc.setTextColor(31, 41, 55);
      doc.text(doc.splitTextToSize(work.work_name, colWidth - 2), col1X, yPosition + 6);

      doc.setFont("Helvetica", "bold");
      doc.setFontSize(9);
      doc.setTextColor(PRIMARY_RGB[0], PRIMARY_RGB[1], PRIMARY_RGB[2]);
      doc.text("DIRECCION", col2X, yPosition);
      doc.setFont("Helvetica", "normal");
      doc.setFontSize(9);
      doc.setTextColor(31, 41, 55);
      doc.text(doc.splitTextToSize(workAddress, colWidth - 2), col2X, yPosition + 6);

      yPosition += 20;

      if (work.description) {
        doc.setFont("Helvetica", "bold");
        doc.setFontSize(9);
        doc.setTextColor(PRIMARY_RGB[0], PRIMARY_RGB[1], PRIMARY_RGB[2]);
        doc.text("DESCRIPTION", margin, yPosition);
        doc.setFont("Helvetica", "normal");
        doc.setFontSize(9);
        doc.setTextColor(55, 65, 81);
        const descriptionLines = doc.splitTextToSize(work.description, contentWidth);
        doc.text(descriptionLines, margin, yPosition + 6);
        yPosition += descriptionLines.length * 4 + 8;
      }

      doc.setDrawColor(156, 163, 175);
      doc.setLineWidth(0.5);
      doc.line(margin, yPosition, pageWidth - margin, yPosition);
      yPosition += 6;

      if (work.products && work.products.length > 0) {
        const tableData = work.products.map((product) => {
          const priceAmount = parseFloat(
            product.snapshot?.sale_price_amount ||
              product.snapshot?.price_amount ||
              product.current_price?.sale_price_amount ||
              product.current_price?.amount ||
              "0",
          );
          const displayPrice = isClientView
            ? priceAmount * (1 + work.tax)
            : priceAmount;
          const productTotal = displayPrice * product.quantity;

          return [
            product.product_name,
            product.quantity.toString(),
            formatCurrency(displayPrice),
            formatCurrency(productTotal),
          ];
        });

        autoTable(doc, {
          head: [["Product", "Quantity", "Price unitario", "Subtotal"]],
          body: tableData,
          startY: yPosition,
          margin: { left: margin, right: margin },
          styles: {
            fontSize: 9,
            cellPadding: 4,
            textColor: [31, 41, 55],
            lineColor: [229, 231, 235],
            lineWidth: 0.3,
          },
          headStyles: {
            fillColor: [PRIMARY_RGB[0], PRIMARY_RGB[1], PRIMARY_RGB[2]],
            textColor: [255, 255, 255],
            fontStyle: "bold",
            halign: "center",
            valign: "middle",
            lineColor: [PRIMARY_RGB[0], PRIMARY_RGB[1], PRIMARY_RGB[2]],
            lineWidth: 0.3,
          },
          bodyStyles: {
            fillColor: [255, 255, 255],
          },
          alternateRowStyles: {
            fillColor: [245, 245, 245],
          },
          columnStyles: {
            0: { halign: "left" },
            1: { halign: "center" },
            2: { halign: "right" },
            3: { halign: "right", fontStyle: "bold" },
          },
        });

        const autoTableDoc = doc as jsPDF & {
          lastAutoTable?: { finalY: number };
        };
        yPosition = (autoTableDoc.lastAutoTable?.finalY ?? yPosition) + 8;
      }

      const summaryX = pageWidth - margin - 80;
      const summaryValueX = pageWidth - margin;

      if (!isClientView) {
        doc.setFont("Helvetica", "normal");
        doc.setFontSize(9);
        doc.setTextColor(107, 114, 128);
        doc.text("Subtotal:", summaryX, yPosition);
        doc.setTextColor(31, 41, 55);
        doc.text(
          formatCurrency(parseFloat(work.products_value)),
          summaryValueX,
          yPosition,
          { align: "right" },
        );

        yPosition += 6;

        doc.setTextColor(107, 114, 128);
        doc.text(
          `% Ganancia (${(work.tax * 100).toFixed(1)}%):`,
          summaryX,
          yPosition,
        );
        doc.setTextColor(31, 41, 55);
        doc.text(
          formatCurrency(parseFloat(work.products_value) * work.tax),
          summaryValueX,
          yPosition,
          { align: "right" },
        );

        yPosition += 8;
      } else {
        yPosition += 4;
      }

      doc.setDrawColor(PRIMARY_RGB[0], PRIMARY_RGB[1], PRIMARY_RGB[2]);
      doc.setLineWidth(0.5);
      doc.line(summaryX - 5, yPosition - 2, pageWidth - margin, yPosition - 2);

      doc.setFont("Helvetica", "bold");
      doc.setFontSize(11);
      doc.setTextColor(75, 85, 99);
      doc.text("TOTAL:", summaryX, yPosition + 4);

      doc.setTextColor(PRIMARY_RGB[0], PRIMARY_RGB[1], PRIMARY_RGB[2]);
      doc.setFontSize(13);
      doc.text(
        formatCurrency(parseFloat(work.work_value)),
        summaryValueX,
        yPosition + 4,
        { align: "right" },
      );

      const footerY = pageHeight - 38;
      doc.setDrawColor(156, 163, 175);
      doc.setLineWidth(0.5);
      doc.line(margin, footerY, pageWidth - margin, footerY);

      const footerStartY = footerY + 6;
      const footerColWidth = (pageWidth - 2 * margin) / 3;

      doc.setFont("Helvetica", "bold");
      doc.setFontSize(9);
      doc.setTextColor(PRIMARY_RGB[0], PRIMARY_RGB[1], PRIMARY_RGB[2]);
      doc.text("Serviperfiles A&C", margin, footerStartY);
      doc.setFont("Helvetica", "normal");
      doc.setFontSize(8);
      doc.setTextColor(107, 114, 128);
      doc.text("Cl. 2 #7-72, Samaca, Boyaca", margin, footerStartY + 5);

      doc.setFont("Helvetica", "bold");
      doc.setFontSize(9);
      doc.setTextColor(PRIMARY_RGB[0], PRIMARY_RGB[1], PRIMARY_RGB[2]);
      doc.text("+57 3213735486", margin + footerColWidth, footerStartY);
      doc.setFont("Helvetica", "normal");
      doc.setFontSize(8);
      doc.setTextColor(107, 114, 128);
      doc.textWithLink(
        "serviperfilesayc.com",
        margin + footerColWidth,
        footerStartY + 5,
        {
          url: "https://serviperfilesayc.com",
        },
      );

      doc.setFont("Helvetica", "normal");
      doc.setFontSize(8);
      doc.setTextColor(107, 114, 128);
      doc.text("Cotizado por:", margin + footerColWidth * 2, footerStartY);
      doc.setFont("Helvetica", "bold");
      doc.setFontSize(8);
      doc.setTextColor(31, 41, 55);
      doc.text(userName, margin + footerColWidth * 2, footerStartY + 5);

      const validityY = footerStartY + 14;
      doc.setDrawColor(PRIMARY_RGB[0], PRIMARY_RGB[1], PRIMARY_RGB[2]);
      doc.setLineWidth(0.3);
      doc.rect(margin, validityY - 4, contentWidth, 14, "S");

      doc.setFont("Helvetica", "normal");
      doc.setFontSize(9);
      doc.setTextColor(PRIMARY_RGB[0], PRIMARY_RGB[1], PRIMARY_RGB[2]);
      const validityText =
        "Esta quotation es valida por 15 dias. Despues debera cotizarse nuevamente.";
      doc.text(doc.splitTextToSize(validityText, contentWidth - 4), margin + 2, validityY + 2);

      doc.setFont("Helvetica", "normal");
      doc.setFontSize(7);
      doc.setTextColor(156, 163, 175);
      doc.text("Pagina 1 de 1", pageWidth / 2, pageHeight - 5, {
        align: "center",
      });

      if (download) {
        doc.save(`${work.work_name}.pdf`);
      } else {
        window.open(doc.output("bloburi"), "_blank");
      }
    } catch {
      setPdfError("No se pudo generar el PDF. Intenta nuevamente.");
    } finally {
      setIsGeneratingPDF(false);
    }
  };

  return (
    <div className={`mx-auto max-w-6xl space-y-6 p-4 md:p-6 ${className}`}>
      {pdfError && (
        <div className="rounded-2xl border border-danger-200 bg-danger-50 px-4 py-3 text-sm text-danger-700">
          {pdfError}
        </div>
      )}

      {showHeader && (
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="text-2xl font-semibold text-foreground">
            Ver quotation
          </h2>
          {onBack && showBackButton && (
            <Button
              isIconOnly
              variant="light"
              className="text-default-600"
              onClick={onBack}
              title="Volver"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
          )}
        </div>
      )}

      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
          {onBack && showBackButton && (
            <Button
              color="default"
              variant="bordered"
              startContent={<ArrowLeft className="h-4 w-4" />}
              onClick={onBack}
              className="w-full sm:w-auto"
            >
              Volver
            </Button>
          )}

          {isClientView && (
            <>
              <Button
                color="primary"
                startContent={<Download className="h-4 w-4" />}
                onClick={() => generatePDF(true)}
                isLoading={isGeneratingPDF}
                isDisabled={isGeneratingPDF}
                className="w-full sm:w-auto"
              >
                Descargar PDF
              </Button>
              <Button
                color="primary"
                variant="bordered"
                startContent={<Printer className="h-4 w-4" />}
                onClick={() => generatePDF(false)}
                isLoading={isGeneratingPDF}
                isDisabled={isGeneratingPDF}
                className="w-full sm:w-auto"
              >
                Imprimir
              </Button>
            </>
          )}
        </div>

        <Button
          color={isClientView ? "success" : "warning"}
          variant="flat"
          startContent={
            isClientView ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />
          }
          onClick={() => setIsClientView((value) => !value)}
          className="w-full lg:w-auto"
        >
          {isClientView ? "Vista client" : "Vista interna"}
        </Button>
      </div>

      <div className="space-y-6 pb-12 pt-6">
        <div className="mb-6 border-b-2 border-primary-200 pb-4">
          <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <h1 className="text-3xl font-bold text-primary-600">COTIZACION</h1>
            <div className="text-left sm:text-right">
              <p className="text-xs font-semibold uppercase text-gray-500">
                ID quotation:
              </p>
              <p className="text-sm font-medium text-gray-800">{work.work_id}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 text-sm sm:grid-cols-2">
            <div>
              <p className="mb-1 text-xs font-semibold uppercase text-gray-500">
                Fecha:
              </p>
              <p className="font-medium text-gray-800">
                {new Date().toLocaleDateString("es-CO", {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </p>
            </div>
            <div className="text-left sm:text-right">
              <p className="mb-1 text-xs font-semibold uppercase text-gray-500">
                Direccion:
              </p>
              <p className="text-sm text-gray-800">{workAddress}</p>
            </div>
          </div>
        </div>

        <div className="space-y-2 text-sm">
          <div>
            <p className="font-semibold uppercase text-gray-500">Client</p>
            <p className="font-medium text-gray-800">{clientName}</p>
          </div>
          <div>
            <p className="font-semibold uppercase text-gray-500">Work</p>
            <p className="font-medium text-gray-800">{work.work_name}</p>
          </div>
          {work.description && (
            <div>
              <p className="font-semibold uppercase text-gray-500">Description</p>
              <p className="text-gray-700">{work.description}</p>
            </div>
          )}

          {!isClientView && (
            <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <p className="mb-2 font-semibold uppercase text-gray-500">
                  Estado
                </p>
                <Button
                  size="sm"
                  variant="flat"
                  color={stateInfo.color}
                  className="font-medium"
                >
                  {stateInfo.label}
                </Button>
              </div>
              <div>
                <p className="mb-2 font-semibold uppercase text-gray-500">
                  % Ganancia
                </p>
                <p className="font-medium text-gray-800">
                  {(work.tax * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          )}
        </div>

        {work.products && work.products.length > 0 && (
          <div>
            <h3 className="mb-4 text-lg font-semibold text-primary-600">
              Products
            </h3>
            <div className="overflow-x-auto rounded-lg border border-gray-300">
              <table className="min-w-[640px] w-full text-sm">
                <thead className="border-b border-gray-300 bg-primary-50">
                  <tr>
                    <th className="px-4 py-2 text-left font-semibold">Product</th>
                    <th className="px-4 py-2 text-center font-semibold">Cant.</th>
                    <th className="px-4 py-2 text-right font-semibold">
                      Unitario
                    </th>
                    <th className="px-4 py-2 text-right font-semibold">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {work.products.map((product) => {
                    const priceAmount = parseFloat(
                      product.snapshot?.sale_price_amount ||
                        product.snapshot?.price_amount ||
                        product.current_price?.sale_price_amount ||
                        product.current_price?.amount ||
                        "0",
                    );
                    const displayPrice = isClientView
                      ? priceAmount * (1 + work.tax)
                      : priceAmount;
                    const productTotal = displayPrice * product.quantity;
                    const components =
                      productDetails[product.product_id]?.components ?? [];

                    return (
                      <React.Fragment key={product.product_id}>
                        <tr className="border-b border-divider hover:bg-table-row-hover">
                          <td className="px-4 py-3">
                            <p className="font-medium">{product.product_name}</p>
                            {!isClientView && (
                            <p className="text-xs text-surface-muted">
                                {product.product_type}
                              </p>
                            )}
                          </td>
                          <td className="px-4 py-3 text-center">
                            {product.quantity}
                          </td>
                          <td className="px-4 py-3 text-right">
                            {formatCurrency(displayPrice)}
                          </td>
                          <td className="px-4 py-3 text-right font-semibold">
                            {formatCurrency(productTotal)}
                          </td>
                        </tr>

                        {!isClientView &&
                          product.product_type.toLowerCase() === "composite" &&
                          components.length > 0 && (
                            <tr className="bg-table-row-hover">
                              <td colSpan={4} className="px-4 py-2">
                                <div className="ml-4 text-xs text-surface-muted sm:ml-6">
                                    <p className="mb-1 font-semibold text-primary">
                                    Componentes:
                                  </p>
                                  <ul className="list-inside list-disc space-y-1">
                                    {components.map((component) => {
                                      const componentPrice = parseFloat(
                                        component.price?.toString() ?? "0",
                                      );
                                      const componentTotal =
                                        componentPrice * component.quantity;

                                      return (
                                        <li key={component.product_id}>
                                          <span className="font-medium">
                                            {component.product_name}
                                          </span>{" "}
                                          - {component.quantity} {" "}
                                          {formatCurrency(componentPrice)} ={" "}
                                          <span className="font-semibold">
                                            {formatCurrency(componentTotal)}
                                          </span>
                                        </li>
                                      );
                                    })}
                                  </ul>
                                </div>
                              </td>
                            </tr>
                          )}
                      </React.Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <div className="mb-12 mt-6 flex justify-end">
              <div className="w-full max-w-sm space-y-2">
                {!isClientView && (
                  <>
                    <div className="flex justify-between text-sm">
                      <p className="text-surface-muted">Subtotal:</p>
                      <p className="font-medium">
                        {formatCurrency(parseFloat(work.products_value))}
                      </p>
                    </div>
                    <div className="flex justify-between text-sm">
                      <p className="text-surface-muted">Ganancia:</p>
                      <p className="font-medium">
                        {formatCurrency(
                          parseFloat(work.products_value) * work.tax,
                        )}
                      </p>
                    </div>
                    <Divider className="my-2" />
                  </>
                )}
                <div className="flex justify-between border-t-2 border-primary-600 pt-4">
                  <p className="text-lg font-bold">TOTAL:</p>
                  <p className="text-lg font-bold text-primary-600">
                    {formatCurrency(parseFloat(work.work_value))}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="mt-8 border-t-2 border-primary-200 pt-6">
          <div className="grid grid-cols-1 gap-6 text-sm sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <p className="mb-1 font-semibold uppercase text-surface-muted">Empresa</p>
              <p className="font-bold text-foreground">Serviperfiles A&C</p>
              <p className="mt-2 text-surface-muted">Cotizado por:</p>
              <p className="text-foreground">{userName}</p>
            </div>
            <div>
              <p className="mb-1 font-semibold uppercase text-surface-muted">
                Direccion
              </p>
              <p className="text-foreground">Cl. 2 #7-72, Samaca, Boyaca</p>
            </div>
            <div>
              <p className="mb-1 font-semibold uppercase text-surface-muted">
                Contacto
              </p>
              <p className="text-foreground">+57 3213735486</p>
            </div>
            <div>
              <p className="mb-1 font-semibold uppercase text-surface-muted">Web</p>
              <a
                href="https://serviperfilesayc.com"
                className="text-primary hover:underline"
              >
                serviperfilesayc.com
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuotationDisplay;
