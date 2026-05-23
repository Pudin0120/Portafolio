/**
 * Selector de tipo de quantity para componentes
 * - Fixed: Quantity fija
 * - Perimeter: Depende del perimetro
 * - Area: Depende del area
 */

import React from "react";
import { RadioGroup, Radio, Input } from "@heroui/react";
import { Calculator, Ruler, Square } from "lucide-react";

type QuantityTypeSelectorProps = {
  quantityType: "fixed" | "perimeter" | "area";
  baseQuantity: number;
  multiplier: number;
  onChange: (
    type: "fixed" | "perimeter" | "area",
    baseQuantity: number,
    multiplier: number,
  ) => void;
};

export const QuantityTypeSelector: React.FC<QuantityTypeSelectorProps> = ({
  quantityType,
  baseQuantity,
  multiplier,
  onChange,
}) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Calculator className="w-4 h-4 text-primary" />
        <h4 className="text-sm font-bold text-foreground">
          Configuration de Quantity
        </h4>
      </div>

      <RadioGroup
        value={quantityType}
        onValueChange={(value: string) =>
          onChange(
            value as "fixed" | "perimeter" | "area",
            baseQuantity,
            multiplier,
          )
        }
        classNames={{
          wrapper: "gap-3",
        }}
      >
        <Radio
          value="fixed"
          description="Quantity fija, no depende de las dimensiones"
        >
          <div className="flex items-center gap-2">
            <Calculator className="w-4 h-4" />
            <span className="font-semibold">Quantity Fija</span>
          </div>
        </Radio>

        <Radio
          value="perimeter"
          description="La quantity se calcula segun el perimetro del product"
        >
          <div className="flex items-center gap-2">
            <Ruler className="w-4 h-4" />
            <span className="font-semibold">Depende del Perimetro</span>
          </div>
        </Radio>

        <Radio
          value="area"
          description="La quantity se calcula segun el area del product"
        >
          <div className="flex items-center gap-2">
            <Square className="w-4 h-4" />
            <span className="font-semibold">Depende del Area</span>
          </div>
        </Radio>
      </RadioGroup>

      {/* Inputs condicionales */}
      <div className="grid grid-cols-2 gap-4 p-4 rounded-xl bg-default-50 border border-default-200">
        <Input
          type="number"
          label="Quantity Base"
          placeholder="1"
          value={baseQuantity.toString()}
          onValueChange={(val: string) =>
            onChange(quantityType, parseFloat(val) || 1, multiplier)
          }
          min="0"
          step="0.01"
          isRequired
          labelPlacement="outside"
          classNames={{
            label:
              "text-[10px] font-bold uppercase tracking-wider text-default-400",
          }}
        />

        {(quantityType === "perimeter" || quantityType === "area") && (
          <Input
            type="number"
            label="Multiplicador"
            placeholder="1"
            value={multiplier.toString()}
            onValueChange={(val: string) =>
              onChange(quantityType, baseQuantity, parseFloat(val) || 1)
            }
            min="0"
            step="0.01"
            labelPlacement="outside"
            classNames={{
              label:
                "text-[10px] font-bold uppercase tracking-wider text-default-400",
            }}
            description={
              quantityType === "perimeter"
                ? "Unidades por mm de perimetro"
                : "Unidades por mm de area"
            }
          />
        )}
      </div>

      {/* Helper text */}
      <div className="text-xs text-default-500 italic">
        {quantityType === "fixed" && (
          <p>
             La quantity sera exactamente <strong>{baseQuantity}</strong>{" "}
            unidad(es), sin importar las dimensiones del product.
          </p>
        )}
        {quantityType === "perimeter" && (
          <p>
             La quantity se calculara como: <strong>perimetro</strong> {" "}
            <strong>{multiplier}</strong>
          </p>
        )}
        {quantityType === "area" && (
          <p>
             La quantity se calculara como: <strong>area</strong> {" "}
            <strong>{multiplier}</strong>
          </p>
        )}
      </div>
    </div>
  );
};
