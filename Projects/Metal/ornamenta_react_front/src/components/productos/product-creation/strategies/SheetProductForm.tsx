/**
 * Formulario para products basados en la estrategia SHEET (Laminas)
 * Optimizado para reducir scroll y mejorar la UX con switch de modo de entrada.
 */

import React, { useState, useEffect } from "react";
import { Divider, Switch } from "@heroui/react";
import { ProductStrategyFormProps } from "@/types/product-creation";
import { ProductMeasurementField, PropertyGroupLabel } from "../FormFields";

export const SheetProductForm: React.FC<ProductStrategyFormProps> = ({
  dimensions,
  onDimensionChange,
  selectedUnit,
  availableUnits,
  onUnitChange,
}) => {
  // Por defecto falso: Modo Dimensiones (Ancho x Alto)
  const [isAreaMode, setIsAreaMode] = useState(!!dimensions.area);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4 bg-default-100/50 p-4 rounded-2xl border border-default-200 shadow-sm">
        <PropertyGroupLabel
          title="Modo de Entrada"
          description={
            isAreaMode
              ? "Ingresa la superficie total"
              : "Ingresa las medidas fisicas"
          }
        />
        <Switch
          isSelected={isAreaMode}
          onValueChange={setIsAreaMode}
          size="sm"
          color="primary"
          classNames={{
            label: "text-xs font-semibold text-default-600",
          }}
        >
          {isAreaMode ? "Area" : "Medidas"}
        </Switch>
      </div>

      <div className="min-h-[100px] flex flex-col justify-center gap-6 px-1">
        {isAreaMode ? (
          <div className="animate-in fade-in slide-in-from-top-1 duration-200">
            <ProductMeasurementField
              propName="area"
              prop={{
                name: "area",
                display_name: "Area Total",
                type: "measurement",
                required: true,
              }}
              value={dimensions.area || ""}
              onChange={(value) => onDimensionChange("area", value)}
              unit={dimensions.area_unit || selectedUnit}
              availableUnits={availableUnits}
              onUnitChange={(unit) => onDimensionChange("area_unit", unit)}
              description={`Superficie total`}
              isSquared
            />
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 animate-in fade-in slide-in-from-top-1 duration-200">
            <ProductMeasurementField
              propName="width"
              prop={{
                name: "width",
                display_name: "Ancho",
                type: "measurement",
                required: true,
              }}
              value={dimensions.width || ""}
              onChange={(value) => onDimensionChange("width", value)}
              unit={dimensions.width_unit || selectedUnit}
              availableUnits={availableUnits}
              onUnitChange={(unit) => onDimensionChange("width_unit", unit)}
            />
            <ProductMeasurementField
              propName="height"
              prop={{
                name: "height",
                display_name: "Alto",
                type: "measurement",
                required: true,
              }}
              value={dimensions.height || ""}
              onChange={(value) => onDimensionChange("height", value)}
              unit={dimensions.height_unit || selectedUnit}
              availableUnits={availableUnits}
              onUnitChange={(unit) => onDimensionChange("height_unit", unit)}
            />
          </div>
        )}
      </div>

      {!dimensions.area && (!dimensions.width || !dimensions.height) && (
        <div className="p-3 bg-warning-50 border border-warning-100 rounded-xl">
          <p className="text-[10px] font-bold text-warning-600 text-center uppercase tracking-tighter">
             Se requieren medidas para el calculo de price
          </p>
        </div>
      )}
    </div>
  );
};
