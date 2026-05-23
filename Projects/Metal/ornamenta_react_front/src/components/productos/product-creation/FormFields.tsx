/**
 * Campos de formulario reutilizables para la creation de products
 */

import React from "react";
import { Input, Card, CardBody, Chip, Select, SelectItem } from "@heroui/react";
import { formatPrice } from "@/utils";
import { Material } from "@/types/products";
import { PropertyConfig } from "@/types/material-creation";

/**
 * Props para ProductMeasurementField
 */
interface ProductMeasurementFieldProps {
  propName: string;
  prop: PropertyConfig;
  value: string | number;
  onChange: (value: string | number) => void;
  unit: string;
  availableUnits?: string[];
  onUnitChange?: (unit: string) => void;
  isRequired?: boolean;
  description?: string;
  isSquared?: boolean;
}

/**
 * Campo de measurement para products con selector de unidad integrado
 */
export const ProductMeasurementField: React.FC<
  ProductMeasurementFieldProps
> = ({
  propName,
  prop,
  value,
  onChange,
  unit,
  availableUnits = [],
  onUnitChange,
  isRequired = false,
  description,
  isSquared = false,
}) => {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between px-1">
        <label className="text-xs font-bold text-default-600 uppercase tracking-tight">
          {prop.display_name}{" "}
          {isRequired && <span className="text-danger">*</span>}
        </label>
        {description && (
          <span className="text-[10px] text-default-400 font-medium">
            {description}
          </span>
        )}
      </div>

      <div className="flex gap-0">
        <Input
          type="number"
          placeholder="0"
          value={String(value || "")}
          onValueChange={(val: string) => onChange(val)}
          step="0.01"
          min="0"
          variant="bordered"
          classNames={{
            inputWrapper:
              "bg-default-50 border-default-200 hover:border-primary-300 focus-within:!border-primary-500 transition-all h-11 rounded-r-none border-r-0 shadow-sm",
            input: "font-semibold text-sm",
          }}
        />

        {availableUnits.length > 0 && onUnitChange ? (
          <Select
            selectedKeys={unit ? new Set([unit]) : new Set()}
            onSelectionChange={(keys: any) =>
              onUnitChange(String(Array.from(keys)[0]))
            }
            variant="bordered"
            disallowEmptySelection
            aria-label="Unidad"
            classNames={{
              trigger:
                "bg-default-100 border-default-200 hover:border-primary-300 focus-within:!border-primary-500 transition-all h-11 w-24 rounded-l-none border-l shadow-sm",
              value: "font-bold text-xs text-primary-600",
            }}
          >
            {availableUnits.map((u) => (
              <SelectItem key={u} textValue={u + (isSquared ? "" : "")}>
                {u}
                {isSquared ? "" : ""}
              </SelectItem>
            ))}
          </Select>
        ) : (
          <div className="bg-default-100 border border-default-200 h-11 px-4 flex items-center justify-center rounded-r-xl border-l-0 min-w-[60px]">
            <span className="text-xs font-bold text-primary-600">
              {unit}
              {isSquared ? "" : ""}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Props para MaterialInfoCard
 */
interface MaterialInfoCardProps {
  material: Material;
  strategyDisplayName: string;
}

/**
 * Tarjeta que muestra information del material seleccionado
 */
export const MaterialInfoCard: React.FC<MaterialInfoCardProps> = ({
  material,
  strategyDisplayName,
}) => {
  return (
    <Card className="bg-default-100 border border-divider shadow-sm">
      <CardBody className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            <p className="text-sm font-bold text-foreground">
              {material.name || material.description}
            </p>
            <p className="text-xs font-medium text-primary mt-0.5">
              {strategyDisplayName}
            </p>
            {material.description && (
              <p className="text-xs text-default-500 mt-2 leading-relaxed">
                {material.description}
              </p>
            )}
          </div>
          <div className="flex flex-col gap-1 items-end">
            <Chip
              color="primary"
              variant="flat"
              size="sm"
              className="font-bold"
            >
              $
              {formatPrice(
                parseFloat(
                  material.sale_price_amount ||
                    material.purchase_price_amount ||
                    material.price_amount,
                ),
              )}
            </Chip>
            <span className="text-[10px] font-bold text-default-400 uppercase tracking-tighter">
              {material.price_currency}
            </span>
          </div>
        </div>
      </CardBody>
    </Card>
  );
};

/**
 * Props para PropertyGroupLabel
 */
interface PropertyGroupLabelProps {
  title: string;
  description?: string;
}

/**
 * Etiqueta para agrupar properties relacionadas
 */
export const PropertyGroupLabel: React.FC<PropertyGroupLabelProps> = ({
  title,
  description,
}) => {
  return (
    <div className="space-y-1">
      <h4 className="text-sm font-semibold text-foreground">{title}</h4>
      {description && <p className="text-xs text-default-500">{description}</p>}
    </div>
  );
};
