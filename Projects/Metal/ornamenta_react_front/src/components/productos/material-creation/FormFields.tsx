/**
 * Componentes reutilizables para campos de formulario de materials
 */

import React, { useEffect } from "react";
import { Input, Select, SelectItem } from "@heroui/react";
import { PropertyConfig } from "@/types/material-creation";
import { getDisplayUnitName } from "./utils";

interface MeasurementFieldProps {
  propName: string;
  propUnit: string | undefined;
  prop: PropertyConfig;
  dynamicProperties: Record<string, any>;
  onPropertyChange: (key: string, value: any) => void;
  isRequired?: boolean;
  autoSetUnit?: boolean;
}

/**
 * Campo de measurement (valor + unidad)
 */
export const MeasurementField: React.FC<MeasurementFieldProps> = ({
  propName,
  propUnit,
  prop,
  dynamicProperties,
  onPropertyChange,
  isRequired = false,
  autoSetUnit = true,
}) => {
  // Asegurar que la unidad este presente en el estado si no lo esta
  useEffect(() => {
    if (!propUnit && (prop.default_unit || prop.preferred_units?.[0])) {
      onPropertyChange(
        `${propName}_unit`,
        prop.default_unit || prop.preferred_units?.[0],
      );
    }
  }, [
    propName,
    propUnit,
    prop.default_unit,
    prop.preferred_units,
    onPropertyChange,
  ]);

  const currentUnit =
    propUnit || prop.default_unit || prop.preferred_units?.[0] || "L";

  return (
    <div className="flex gap-2">
      <Input
        type="number"
        label="Valor"
        step="0.01"
        placeholder={prop.default_value?.toString() || "0.0"}
        value={dynamicProperties[`${propName}_value`] || ""}
        onValueChange={(value: string) => {
          onPropertyChange(
            `${propName}_value`,
            value ? parseFloat(value) : undefined,
          );
          // Si autoSetUnit es true, forzamos la unidad si no existe (aunque el useEffect ya lo hace)
          if (
            autoSetUnit &&
            !propUnit &&
            (prop.default_unit || prop.preferred_units?.[0])
          ) {
            onPropertyChange(
              `${propName}_unit`,
              prop.default_unit || prop.preferred_units?.[0],
            );
          }
        }}
        isRequired={isRequired}
        variant="bordered"
      />
      <Select
        label="Unidad"
        selectedKeys={new Set([currentUnit])}
        onSelectionChange={(keys: any) => {
          const unit = Array.from(keys)[0] as string;
          onPropertyChange(`${propName}_unit`, unit);
        }}
        className="w-32"
        isRequired={isRequired}
        variant="bordered"
      >
        {(prop.preferred_units || []).map((unit: string) => (
          <SelectItem key={unit} value={unit} title={getDisplayUnitName(unit)}>
            {unit}
          </SelectItem>
        ))}
      </Select>
    </div>
  );
};

interface PropertyLabelProps {
  displayName: string;
  isRequired?: boolean;
  description?: string;
  note?: string;
}

/**
 * Etiqueta de propiedad con description y nota opcional
 */
export const PropertyLabel: React.FC<PropertyLabelProps> = ({
  displayName,
  isRequired = false,
  description,
  note,
}) => (
  <div className="space-y-1">
    <label className="text-sm font-semibold">
      {displayName}
      {isRequired && <span className="text-danger ml-1">*</span>}
    </label>
    {description && <p className="text-xs text-default-500">{description}</p>}
    {note && (
      <p className="text-xs text-secondary-600 font-medium"> {note}</p>
    )}
  </div>
);
