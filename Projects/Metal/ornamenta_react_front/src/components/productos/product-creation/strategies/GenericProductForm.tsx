/**
 * Formulario generico para products basados en estrategias LIQUID y otras no especializadas
 */

import React from "react";
import { ProductStrategyFormProps } from "@/types/product-creation";
import { ProductMeasurementField, PropertyGroupLabel } from "../FormFields";

export const GenericProductForm: React.FC<ProductStrategyFormProps> = ({
  material,
  strategy,
  dimensions,
  onDimensionChange,
  requiredProperties,
  selectedUnit,
  availableUnits,
  onUnitChange,
}) => {
  return (
    <div className="space-y-4">
      <div className="bg-default-50 p-4 rounded-2xl border border-default-100 shadow-sm">
        <PropertyGroupLabel
          title="Medidas Requeridas"
          description={
            strategy.description || "Especifica las dimensiones necesarias"
          }
        />
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 px-1">
        {requiredProperties.map((prop) => (
          <ProductMeasurementField
            key={prop.name}
            propName={prop.name}
            prop={prop}
            value={dimensions[prop.name] || ""}
            onChange={(value) => onDimensionChange(prop.name, value)}
            unit={dimensions[`${prop.name}_unit`] || selectedUnit}
            availableUnits={availableUnits}
            onUnitChange={(unit) => onUnitChange(unit)}
            isRequired={prop.required === true}
          />
        ))}
      </div>
    </div>
  );
};
