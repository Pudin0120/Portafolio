/**
 * Formulario especifico para la estrategia PROFILE (Perfiles Estructurales)
 */

import React, { useEffect } from "react";
import { Select, SelectItem, Switch } from "@heroui/react";
import { StrategyFormComponentProps } from "@/types/material-creation";
import { MeasurementField, PropertyLabel } from "../FormFields";

export const ProfilePropertyForm: React.FC<StrategyFormComponentProps> = ({
  dynamicProperties,
  onPropertyChange,
  strategyConfig,
}) => {
  const shape = dynamicProperties["shape"] || "";

  // Set default values when strategy is selected
  useEffect(() => {
    if (dynamicProperties["is_hollow"] === undefined) {
      onPropertyChange("is_hollow", true);
    }
    if (!dynamicProperties["length_unit"]) {
      onPropertyChange("length_unit", "m");
    }
    if (!dynamicProperties["length_value"]) {
      onPropertyChange("length_value", "6");
    }
  }, []);

  const shapeOptions =
    strategyConfig?.properties?.find((p) => p.name === "shape")?.options || [];

  return (
    <div className="space-y-6">
      {/* Forma del Perfil */}
      <div className="space-y-2">
        <PropertyLabel
          displayName="Forma del Perfil"
          isRequired={true}
          description="Selecciona la geometria de la seccion transversal"
        />
        <Select
          placeholder="Selecciona una forma"
          selectedKeys={shape ? [shape] : []}
          onSelectionChange={(keys: any) => {
            const selected = Array.from(keys)[0] as string;
            onPropertyChange("shape", selected);

            // Logic to clear incompatible fields could go here
            if (selected === "ROUND") {
              onPropertyChange("width_value", "");
              onPropertyChange("height_value", "");
            } else {
              onPropertyChange("diameter_value", "");
            }
          }}
          size="sm"
          variant="bordered"
          className="max-w-xs"
        >
          {(shapeOptions as any[]).map((option) => (
            <SelectItem key={option.value} textValue={option.display_name}>
              {option.display_name}
            </SelectItem>
          ))}
        </Select>
      </div>

      {/* Espesor / Calibre (Comun para todas las formas) */}
      <div className="space-y-2">
        {strategyConfig?.properties
          ?.filter((p) => p.name === "thickness")
          .map((prop) => (
            <MeasurementField
              key={prop.name}
              propName={prop.name}
              propUnit={dynamicProperties[`${prop.name}_unit`]}
              prop={prop}
              dynamicProperties={dynamicProperties}
              onPropertyChange={onPropertyChange}
              isRequired={true}
            />
          ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
        {/* Diametro (Solo para ROUND) */}
        {shape === "ROUND" &&
          strategyConfig?.properties
            ?.filter((p) => p.name === "diameter")
            .map((prop) => (
              <MeasurementField
                key={prop.name}
                propName={prop.name}
                propUnit={dynamicProperties[`${prop.name}_unit`]}
                prop={prop}
                dynamicProperties={dynamicProperties}
                onPropertyChange={onPropertyChange}
                isRequired={true}
              />
            ))}

        {/* Ancho (Para todo lo que NO sea ROUND) */}
        {shape &&
          shape !== "ROUND" &&
          strategyConfig?.properties
            ?.filter((p) => p.name === "width")
            .map((prop) => (
              <MeasurementField
                key={prop.name}
                propName={prop.name}
                propUnit={dynamicProperties[`${prop.name}_unit`]}
                prop={prop}
                dynamicProperties={dynamicProperties}
                onPropertyChange={onPropertyChange}
                isRequired={true}
              />
            ))}

        {/* Alto (Solo para RECTANGULAR, L_SHAPE, U_SHAPE) */}
        {["RECTANGULAR", "L_SHAPE", "U_SHAPE"].includes(shape) &&
          strategyConfig?.properties
            ?.filter((p) => p.name === "height")
            .map((prop) => (
              <MeasurementField
                key={prop.name}
                propName={prop.name}
                propUnit={dynamicProperties[`${prop.name}_unit`]}
                prop={prop}
                dynamicProperties={dynamicProperties}
                onPropertyChange={onPropertyChange}
                isRequired={true}
              />
            ))}
      </div>

      {/* Longitud Comercial */}
      <div className="pt-2">
        {strategyConfig?.properties
          ?.filter((p) => p.name === "length")
          .map((prop) => (
            <MeasurementField
              key={prop.name}
              propName={prop.name}
              propUnit={dynamicProperties[`${prop.name}_unit`]}
              prop={prop}
              dynamicProperties={dynamicProperties}
              onPropertyChange={onPropertyChange}
              isRequired={true}
            />
          ))}
      </div>

      {/* Es Hueco? */}
      <div className="flex items-center gap-4 p-4 rounded-xl bg-default-100/50 border border-default-200">
        <div className="flex-1">
          <p className="text-sm font-bold text-foreground">Es Perfil Hueco?</p>
          <p className="text-tiny text-default-500">
            Marca si es un tubo o perfil con espesor de pared, o macizo.
          </p>
        </div>
        <Switch
          isSelected={dynamicProperties["is_hollow"]}
          onValueChange={(val: boolean) => onPropertyChange("is_hollow", val)}
          size="sm"
        />
      </div>
    </div>
  );
};
