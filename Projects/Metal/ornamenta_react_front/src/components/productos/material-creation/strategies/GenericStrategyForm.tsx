/**
 * Componente de formulario generico para estrategias de measurement
 * Usado para LIQUID y otras estrategias no especializadas
 */

import React from "react";
import { Button, Input } from "@heroui/react";
import { StrategyFormComponentProps } from "@/types/material-creation";
import { MeasurementField, PropertyLabel } from "../FormFields";

import { IdentityHeader } from "../IdentityHeader";

export const GenericStrategyForm: React.FC<StrategyFormComponentProps> = ({
  dynamicProperties,
  onPropertyChange,
  strategyConfig,
  shouldShowProperty,
  materialTypeObj,
  name = "",
  setName = () => {},
}) => {
  if (!strategyConfig) return null;

  return (
    <div className="space-y-6">
      <IdentityHeader
        name={name}
        setName={setName}
        strategyName={strategyConfig.name}
        materialTypeName={materialTypeObj?.name || strategyConfig.display_name}
      />

      {strategyConfig.properties
        ?.filter((prop) => shouldShowProperty(prop))
        .map((prop) => (
          <div key={prop.name} className="space-y-2">
            <PropertyLabel
              displayName={prop.display_name}
              isRequired={prop.required === true}
              description={prop.description}
              note={prop.note}
            />

            {/* Campo de measurement (con valor y unidad) */}
            {prop.type === "measurement" && (
              <MeasurementField
                propName={prop.name}
                propUnit={dynamicProperties[`${prop.name}_unit`]}
                prop={prop}
                dynamicProperties={dynamicProperties}
                onPropertyChange={onPropertyChange}
                isRequired={prop.required === true}
                autoSetUnit={true}
              />
            )}

            {/* Campo numerico simple */}
            {prop.type === "number" && (
              <Input
                type="number"
                step="0.01"
                placeholder={prop.default_value?.toString() || "0.0"}
                value={dynamicProperties[`${prop.name}_value`] || ""}
                onValueChange={(value: string) =>
                  onPropertyChange(
                    `${prop.name}_value`,
                    value ? parseFloat(value) : undefined,
                  )
                }
                isRequired={prop.required === true}
                variant="bordered"
              />
            )}
          </div>
        ))}
    </div>
  );
};
