/**
 * Componente de formulario para la estrategia SHEET (Laminas)
 */

import React from "react";
import {
  Input,
  Select,
  SelectItem,
  RadioGroup,
  Radio,
  Tabs,
  Tab,
} from "@heroui/react";
import { StrategyFormComponentProps } from "@/types/material-creation";
import { MeasurementField, PropertyLabel } from "../FormFields";
import { getDisplayUnitName } from "../utils";
import { Ruler, Maximize } from "lucide-react";

export const SheetPropertyForm: React.FC<StrategyFormComponentProps> = ({
  dynamicProperties,
  onPropertyChange,
  strategyConfig,
  inputMode,
  onInputModeChange,
  shouldShowProperty,
}) => {
  if (!strategyConfig) return null;

  return (
    <div className="space-y-6">
      {/* Selector de modo de entrada simplificado con Tabs */}
      {strategyConfig.input_modes && strategyConfig.input_modes.length > 1 && (
        <div className="flex flex-col gap-2">
          <label className="text-sm font-semibold text-default-700">
            Modo de Definicion
          </label>
          <Tabs
            selectedKey={inputMode}
            onSelectionChange={(key: React.Key) =>
              onInputModeChange(key as string)
            }
            variant="flat"
            color="primary"
            size="sm"
            classNames={{
              tabList: "w-full bg-default-100 p-1",
              cursor: "bg-white shadow-sm",
              tab: "h-8",
              tabContent: "group-data-[selected=true]:text-primary font-bold",
            }}
          >
            {strategyConfig.input_modes.map((mode) => {
              // Limpiar el nombre del modo por si viene con basura del backend
              const cleanName = mode.display_name
                .replace(/[\u1000-\uFFFF]|[^\w\sAEIOUaeiounN]/g, "")
                .trim();

              return (
                <Tab
                  key={mode.mode}
                  title={
                    <div className="flex items-center gap-2">
                      {mode.mode === "dimensions" ? (
                        <Ruler size={14} />
                      ) : (
                        <Maximize size={14} />
                      )}
                      <span className="whitespace-nowrap">{cleanName}</span>
                    </div>
                  }
                />
              );
            })}
          </Tabs>
        </div>
      )}

      {/* Properties dinamicas */}
      <div className="space-y-6 pt-2">
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

              {/* Propiedad gauge_or_measurement (Espesor) */}
              {prop.type === "gauge_or_measurement" && (
                <div className="space-y-2">
                  <RadioGroup
                    value={dynamicProperties[`${prop.name}_type`] || "gauge"}
                    onValueChange={(type: string) => {
                      onPropertyChange(`${prop.name}_type`, type);
                    }}
                    orientation="horizontal"
                  >
                    <Radio value="gauge">Calibre (AWG)</Radio>
                    <Radio value="measurement">Medida Directa</Radio>
                  </RadioGroup>

                  {dynamicProperties[`${prop.name}_type`] === "gauge" ||
                  !dynamicProperties[`${prop.name}_type`] ? (
                    <Input
                      type="number"
                      label="Number de calibre"
                      placeholder="Ej: 14"
                      value={dynamicProperties[`${prop.name}_gauge`] || ""}
                      onValueChange={(value: string) =>
                        onPropertyChange(
                          `${prop.name}_gauge`,
                          value ? parseInt(value) : undefined,
                        )
                      }
                      variant="bordered"
                      size="sm"
                    />
                  ) : (
                    <div className="flex gap-2">
                      <Input
                        type="number"
                        label="Valor (mm)"
                        step="0.01"
                        value={dynamicProperties[`${prop.name}_mm`] || ""}
                        onValueChange={(value: string) =>
                          onPropertyChange(
                            `${prop.name}_mm`,
                            value ? parseFloat(value) : undefined,
                          )
                        }
                        variant="bordered"
                        size="sm"
                      />
                      <Select
                        label="Unidad"
                        selectedKeys={
                          new Set([
                            dynamicProperties[`${prop.name}_unit`] || "mm",
                          ])
                        }
                        onSelectionChange={(keys: any) => {
                          const unit = Array.from(keys)[0] as string;
                          onPropertyChange(`${prop.name}_unit`, unit);
                        }}
                        className="w-24"
                      >
                        {prop.options?.measurement?.preferred_units?.map(
                          (unit: string) => (
                            <SelectItem
                              key={unit}
                              value={unit}
                              title={getDisplayUnitName(unit)}
                            >
                              {unit}
                            </SelectItem>
                          ),
                        )}
                      </Select>
                    </div>
                  )}
                </div>
              )}

              {/* Propiedad measurement (area, width, length) */}
              {prop.type === "measurement" && (
                <MeasurementField
                  propName={prop.name}
                  propUnit={dynamicProperties[`${prop.name}_unit`]}
                  prop={prop}
                  dynamicProperties={dynamicProperties}
                  onPropertyChange={onPropertyChange}
                  isRequired={prop.required === true}
                  autoSetUnit={false}
                />
              )}
            </div>
          ))}
      </div>
    </div>
  );
};
