/**
 * Formulario para products basados en la estrategia LABOR (Mano de obra)
 */

import React from "react";
import { ProductStrategyFormProps } from "@/types/product-creation";
import { ProductMeasurementField, PropertyGroupLabel } from "../FormFields";

export const LaborProductForm: React.FC<ProductStrategyFormProps> = ({
  material,
  dimensions,
  onDimensionChange,
  selectedUnit,
  availableUnits,
  onUnitChange,
}) => {
  const unitType = material.properties?.unit_type as string;

  return (
    <div className="space-y-6">
      <div className="bg-default-50 p-4 rounded-2xl border border-default-100 shadow-sm">
        <PropertyGroupLabel
          title={
            unitType === "linear_meter"
              ? "Work por Longitud"
              : "Work por Superficie"
          }
          description={
            unitType === "linear_meter"
              ? "Especifica el largo total"
              : "Especifica el area de work"
          }
        />
      </div>

      <div className="space-y-6 px-1">
        {unitType === "linear_meter" ? (
          <ProductMeasurementField
            propName="length"
            prop={{
              name: "length",
              display_name: "Longitud",
              type: "measurement",
              required: true,
            }}
            value={dimensions.length || ""}
            onChange={(value) => onDimensionChange("length", value)}
            unit={dimensions.length_unit || selectedUnit}
            availableUnits={availableUnits}
            onUnitChange={(unit) => onDimensionChange("length_unit", unit)}
            isRequired
          />
        ) : (
          <div className="grid grid-cols-1 gap-6">
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
              isRequired
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
              isRequired
            />
          </div>
        )}
      </div>
    </div>
  );
};
