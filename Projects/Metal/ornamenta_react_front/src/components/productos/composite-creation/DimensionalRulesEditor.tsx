/**
 * Editor de reglas dimensionales para width, height, depth
 * Permite configurar si una dimension sigue al padre o es fija
 */

import React from "react";
import {
  Accordion,
  AccordionItem,
  RadioGroup,
  Radio,
  Input,
  Select,
  SelectItem,
} from "@heroui/react";
import { Ruler, Maximize2 } from "lucide-react";
import { DimensionalRule, CompositeDimensions } from "./types";

type DimensionalRulesEditorProps = {
  widthRule?: DimensionalRule;
  heightRule?: DimensionalRule;
  depthRule?: DimensionalRule;
  parentDimensions: CompositeDimensions;
  onChange: (
    width?: DimensionalRule,
    height?: DimensionalRule,
    depth?: DimensionalRule,
  ) => void;
};

export const DimensionalRulesEditor: React.FC<DimensionalRulesEditorProps> = ({
  widthRule,
  heightRule,
  depthRule,
  parentDimensions,
  onChange,
}) => {
  const updateRule = (
    dimension: "width" | "height" | "depth",
    rule?: DimensionalRule,
  ) => {
    const newWidth = dimension === "width" ? rule : widthRule;
    const newHeight = dimension === "height" ? rule : heightRule;
    const newDepth = dimension === "depth" ? rule : depthRule;
    onChange(newWidth, newHeight, newDepth);
  };

  const renderRuleEditor = (
    dimension: "width" | "height" | "depth",
    rule?: DimensionalRule,
    label: string = dimension,
  ) => {
    const ruleType = rule?.reference_type || "none";

    return (
      <div className="space-y-3">
        <RadioGroup
          value={ruleType}
          onValueChange={(value: string) => {
            if (value === "none") {
              updateRule(dimension, undefined);
            } else if (value === "parent") {
              updateRule(dimension, {
                reference_type: "parent",
                parent_dimension: dimension,
              });
            } else if (value === "fixed") {
              updateRule(dimension, {
                reference_type: "fixed",
                fixed_value: 0,
                unit: "mm",
              });
            }
          }}
          classNames={{
            wrapper: "gap-2",
          }}
        >
          <Radio value="none" size="sm">
            <span className="text-xs">Sin restriccion</span>
          </Radio>
          <Radio value="parent" size="sm">
            <span className="text-xs">Sigue dimension del padre</span>
          </Radio>
          <Radio value="fixed" size="sm">
            <span className="text-xs">Valor fijo</span>
          </Radio>
        </RadioGroup>

        {/* Campos condicionales */}
        {ruleType === "parent" && (
          <Select
            label="Dimension del padre"
            labelPlacement="outside"
            placeholder="Selecciona dimension"
            selectedKeys={rule?.parent_dimension ? [rule.parent_dimension] : []}
            onSelectionChange={(keys: unknown) => {
              const selected = Array.from(keys as Set<string>)[0] as
                | "width"
                | "height"
                | "depth";
              if (selected) {
                updateRule(dimension, {
                  reference_type: "parent",
                  parent_dimension: selected,
                });
              }
            }}
            size="sm"
            classNames={{
              label:
                "text-[10px] font-bold uppercase tracking-wider text-default-400",
            }}
          >
            <SelectItem key="width" value="width">
              Ancho del padre ({parentDimensions.width}mm)
            </SelectItem>
            <SelectItem key="height" value="height">
              Alto del padre ({parentDimensions.height}mm)
            </SelectItem>
            {parentDimensions.depth !== undefined && (
              <SelectItem key="depth" value="depth">
                Profundidad del padre ({parentDimensions.depth}mm)
              </SelectItem>
            )}
          </Select>
        )}

        {ruleType === "fixed" && (
          <Input
            type="number"
            label="Valor fijo (mm)"
            labelPlacement="outside"
            placeholder="0"
            value={rule?.fixed_value?.toString() || ""}
            onValueChange={(val: string) => {
              updateRule(dimension, {
                reference_type: "fixed",
                fixed_value: parseFloat(val) || 0,
                unit: "mm",
              });
            }}
            min="0"
            step="1"
            size="sm"
            classNames={{
              label:
                "text-[10px] font-bold uppercase tracking-wider text-default-400",
            }}
          />
        )}
      </div>
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Maximize2 className="w-4 h-4 text-primary" />
        <h4 className="text-sm font-bold text-foreground">
          Reglas Dimensionales (Opcional)
        </h4>
      </div>

      <p className="text-xs text-default-500 italic">
        Define como las dimensiones de este componente se relacionan con el
        product padre.
      </p>

      <Accordion variant="bordered" selectionMode="multiple">
        <AccordionItem
          key="width"
          aria-label="Regla de Ancho"
          title={
            <div className="flex items-center gap-2">
              <Ruler className="w-3.5 h-3.5" />
              <span className="text-sm font-semibold">Ancho (Width)</span>
              {widthRule && (
                <span className="text-[10px] text-primary bg-primary/10 px-2 py-0.5 rounded-full">
                  {widthRule.reference_type === "parent"
                    ? `Sigue ${widthRule.parent_dimension}`
                    : `Fijo ${widthRule.fixed_value}mm`}
                </span>
              )}
            </div>
          }
        >
          {renderRuleEditor("width", widthRule, "Ancho")}
        </AccordionItem>

        <AccordionItem
          key="height"
          aria-label="Regla de Alto"
          title={
            <div className="flex items-center gap-2">
              <Ruler className="w-3.5 h-3.5" />
              <span className="text-sm font-semibold">Alto (Height)</span>
              {heightRule && (
                <span className="text-[10px] text-primary bg-primary/10 px-2 py-0.5 rounded-full">
                  {heightRule.reference_type === "parent"
                    ? `Sigue ${heightRule.parent_dimension}`
                    : `Fijo ${heightRule.fixed_value}mm`}
                </span>
              )}
            </div>
          }
        >
          {renderRuleEditor("height", heightRule, "Alto")}
        </AccordionItem>

        <AccordionItem
          key="depth"
          aria-label="Regla de Profundidad"
          title={
            <div className="flex items-center gap-2">
              <Ruler className="w-3.5 h-3.5" />
              <span className="text-sm font-semibold">Profundidad (Depth)</span>
              {depthRule && (
                <span className="text-[10px] text-primary bg-primary/10 px-2 py-0.5 rounded-full">
                  {depthRule.reference_type === "parent"
                    ? `Sigue ${depthRule.parent_dimension}`
                    : `Fijo ${depthRule.fixed_value}mm`}
                </span>
              )}
            </div>
          }
        >
          {renderRuleEditor("depth", depthRule, "Profundidad")}
        </AccordionItem>
      </Accordion>
    </div>
  );
};
