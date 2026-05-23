/**
 * Formulario para products basados en la estrategia SOLID (Solidos)
 *
 * SOLID puede ser de dos tipos:
 * 1. Con dimensiones: width, height, depth + unit (unidades de longitud)
 * 2. Con masa: mass + unit (unidades de peso)
 */

import React, { useMemo, useEffect, useState } from "react";
import { Switch, Card, CardBody } from "@heroui/react";
import { ProductStrategyFormProps } from "@/types/product-creation";
import { ProductMeasurementField, PropertyGroupLabel } from "../FormFields";

export const SolidProductForm: React.FC<ProductStrategyFormProps> = ({
  material,
  dimensions,
  onDimensionChange,
  selectedUnit,
  availableUnits,
  onUnitChange,
}) => {
  // Estado para el switch de Peso vs Volumen
  const [isVolumeMode, setIsVolumeMode] = useState(
    !!(dimensions.volume && parseFloat(dimensions.volume) > 0),
  );

  // Detectar si este SOLID es de dimensiones o de masa
  const isMaterialWithDimensions = useMemo(() => {
    const props = material.properties || {};
    return !!(props["width"] || props["height"] || props["depth"]);
  }, [material]);

  // Filtrar unidades segun el modo para evitar confusion
  const filteredUnits = useMemo(() => {
    if (isMaterialWithDimensions) return availableUnits;

    const weightUnits = ["kg", "g", "lb", "ton", "oz"];
    const volumeUnits = ["L", "ml", "m3", "cm3", "gal", "fl oz"];

    if (isVolumeMode) {
      return availableUnits.filter((u) => volumeUnits.includes(u));
    }
    return availableUnits.filter((u) => weightUnits.includes(u));
  }, [availableUnits, isVolumeMode, isMaterialWithDimensions]);

  if (isMaterialWithDimensions) {
    return (
      <div className="space-y-6">
        <div className="bg-default-50 p-4 rounded-2xl border border-default-100 shadow-sm">
          <PropertyGroupLabel
            title="Medidas de la Pieza"
            description="Especifica las dimensiones fisicas"
          />
        </div>

        <div className="grid grid-cols-1 gap-6 px-1">
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
            isRequired={true}
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
            isRequired={true}
          />

          <ProductMeasurementField
            propName="depth"
            prop={{
              name: "depth",
              display_name: "Profundidad",
              type: "measurement",
              required: true,
            }}
            value={dimensions.depth || ""}
            onChange={(value) => onDimensionChange("depth", value)}
            unit={dimensions.depth_unit || selectedUnit}
            availableUnits={availableUnits}
            onUnitChange={(unit) => onDimensionChange("depth_unit", unit)}
            isRequired={true}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4 bg-default-50 p-4 rounded-2xl border border-default-100 shadow-sm">
        <PropertyGroupLabel
          title="Modo de Medicion"
          description={
            isVolumeMode ? "Entrada por volumen" : "Entrada por peso"
          }
        />
        <Switch
          isSelected={isVolumeMode}
          onValueChange={setIsVolumeMode}
          size="sm"
          color="primary"
          classNames={{
            label: "text-xs font-semibold text-default-600",
          }}
        >
          {isVolumeMode ? "Volumen" : "Peso"}
        </Switch>
      </div>

      <div className="min-h-[100px] flex flex-col justify-center px-1">
        {!isVolumeMode ? (
          <div className="animate-in fade-in slide-in-from-top-1 duration-200">
            <ProductMeasurementField
              propName="weight"
              prop={{
                name: "weight",
                display_name: "Peso Total",
                type: "measurement",
                required: true,
              }}
              value={dimensions.weight || ""}
              onChange={(value) => onDimensionChange("weight", value)}
              unit={dimensions.weight_unit || selectedUnit}
              availableUnits={filteredUnits}
              onUnitChange={(unit) => onDimensionChange("weight_unit", unit)}
              isRequired
            />
          </div>
        ) : (
          <div className="animate-in fade-in slide-in-from-top-1 duration-200">
            <ProductMeasurementField
              propName="volume"
              prop={{
                name: "volume",
                display_name: "Volumen Total",
                type: "measurement",
                required: true,
              }}
              value={dimensions.volume || ""}
              onChange={(value) => onDimensionChange("volume", value)}
              unit={dimensions.volume_unit || selectedUnit}
              availableUnits={filteredUnits}
              onUnitChange={(unit) => onDimensionChange("volume_unit", unit)}
              isRequired
            />
          </div>
        )}
      </div>
    </div>
  );
};
