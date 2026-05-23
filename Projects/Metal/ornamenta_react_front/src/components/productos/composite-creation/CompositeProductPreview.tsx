/**
 * Preview del product compuesto con simulacion en tiempo real
 * Muestra arbol jerarquico, precios calculados y resumen
 */

import React from "react";
import { Card, CardBody, Chip, Spinner, Divider } from "@heroui/react";
import {
  Calculator,
  DollarSign,
  ShoppingCart,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";
import { ComponentsHierarchyTree } from "./ComponentsHierarchyTree";
import { SimulateCompositeResponse, CompositeComponentForm } from "./types";
import { formatPrice } from "@/utils";

type CompositeProductPreviewProps = {
  simulation: SimulateCompositeResponse | null;
  isSimulating: boolean;
  components: CompositeComponentForm[];
};

export const CompositeProductPreview: React.FC<
  CompositeProductPreviewProps
> = ({ simulation, isSimulating, components }) => {
  if (isSimulating) {
    return (
      <Card className="bg-default-50">
        <CardBody className="p-8">
          <div className="flex flex-col items-center justify-center gap-4">
            <Spinner size="lg" color="primary" />
            <div className="text-center">
              <p className="text-sm font-bold text-primary">
                Calculando product compuesto...
              </p>
              <p className="text-xs text-default-500 mt-1">
                Estamos procesando las reglas dimensionales y calculando precios
              </p>
            </div>
          </div>
        </CardBody>
      </Card>
    );
  }

  if (!simulation || components.length === 0) {
    return (
      <Card className="bg-default-50 border-2 border-dashed border-default-200">
        <CardBody className="p-8">
          <div className="flex flex-col items-center justify-center gap-3 text-center">
            <AlertCircle className="w-12 h-12 text-default-300" />
            <div>
              <p className="text-sm font-bold text-default-500">
                Sin componentes
              </p>
              <p className="text-xs text-default-400 mt-1">
                Agrega componentes para ver el preview del product compuesto
              </p>
            </div>
          </div>
        </CardBody>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header con info del product */}
      <Card className="border-t-4 border-primary bg-primary/5">
        <CardBody className="p-6">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle2 className="w-5 h-5 text-success" />
                <p className="text-[10px] font-bold uppercase tracking-widest text-primary">
                  Product Compuesto Calculado
                </p>
              </div>
              <h3 className="text-2xl font-black text-foreground mb-2">
                {simulation.name}
              </h3>
              <p className="text-sm text-default-600">
                {simulation.description}
              </p>

              {/* Dimensiones */}
              <div className="flex items-center gap-3 mt-4">
                <div className="rounded-xl border border-surface-border bg-surface-elevated px-3 py-2">
                  <p className="text-[9px] font-bold uppercase text-default-400">
                    Ancho
                  </p>
                  <p className="text-sm font-black text-foreground">
                    {simulation.dimensions.width}mm
                  </p>
                </div>
                <div className="rounded-xl border border-surface-border bg-surface-elevated px-3 py-2">
                  <p className="text-[9px] font-bold uppercase text-default-400">
                    Alto
                  </p>
                  <p className="text-sm font-black text-foreground">
                    {simulation.dimensions.height}mm
                  </p>
                </div>
                {simulation.dimensions.depth !== undefined && (
                  <div className="rounded-xl border border-surface-border bg-surface-elevated px-3 py-2">
                    <p className="text-[9px] font-bold uppercase text-default-400">
                      Profundidad
                    </p>
                    <p className="text-sm font-black text-foreground">
                      {simulation.dimensions.depth}mm
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Precios Totales */}
            <div className="flex flex-col gap-3">
              <Card className="bg-warning-50 border border-warning-200">
                <CardBody className="p-4 text-center">
                  <div className="flex items-center gap-2 mb-1">
                    <ShoppingCart className="w-4 h-4 text-warning-600" />
                    <p className="text-[9px] font-bold uppercase text-warning-600">
                      Costo Total
                    </p>
                  </div>
                  <p className="text-2xl font-black text-warning-700">
                    ${formatPrice(parseFloat(simulation.total_purchase_price))}
                  </p>
                  <p className="text-[9px] text-warning-600 mt-1">COP</p>
                </CardBody>
              </Card>

              <Card className="bg-success-50 border border-success-200">
                <CardBody className="p-4 text-center">
                  <div className="flex items-center gap-2 mb-1">
                    <DollarSign className="w-4 h-4 text-success-600" />
                    <p className="text-[9px] font-bold uppercase text-success-600">
                      Price Venta
                    </p>
                  </div>
                  <p className="text-2xl font-black text-success-700">
                    ${formatPrice(parseFloat(simulation.total_sale_price))}
                  </p>
                  <p className="text-[9px] text-success-600 mt-1">COP</p>
                </CardBody>
              </Card>

              {/* Margen de ganancia */}
              {parseFloat(simulation.total_purchase_price) > 0 && (
                <Chip color="primary" variant="flat" size="sm">
                  Margen:{" "}
                  {(
                    ((parseFloat(simulation.total_sale_price) -
                      parseFloat(simulation.total_purchase_price)) /
                      parseFloat(simulation.total_purchase_price)) *
                    100
                  ).toFixed(1)}
                  %
                </Chip>
              )}
            </div>
          </div>
        </CardBody>
      </Card>

      <Divider />

      {/* Arbol de componentes */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Calculator className="w-5 h-5 text-primary" />
          <h4 className="text-lg font-bold text-foreground">
            Estructura del Product
          </h4>
          <Chip size="sm" color="primary" variant="flat">
            {simulation.components.length} componente(s)
          </Chip>
        </div>

        <ComponentsHierarchyTree
          components={components}
          calculatedComponents={simulation.components}
          showActions={false}
          showPrices={true}
        />
      </div>

      {/* Info adicional */}
      <Card className="bg-default-100/50 border border-default-200">
        <CardBody className="p-4">
          <div className="flex gap-2 text-default-600">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <div className="text-xs space-y-1">
              <p className="font-bold">Importante:</p>
              <ul className="list-disc list-inside space-y-0.5 text-default-500">
                <li>
                  Los precios mostrados son calculados automaticamente segun las
                  reglas configuradas.
                </li>
                <li>
                  Las dimensiones de los componentes se ajustaran segun las
                  reglas establecidas.
                </li>
                <li>
                  Los componentes compuestos anidados muestran su estructura
                  interna.
                </li>
              </ul>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  );
};
