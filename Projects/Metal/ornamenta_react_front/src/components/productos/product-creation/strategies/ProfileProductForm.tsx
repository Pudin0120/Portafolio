/**
 * Formulario especifico para products basados en Perfiles (PROFILE)
 *
 * Los perfiles heredan forma, diametro, espesor, ancho y alto del material base.
 * El user solo especifica la longitud de la pieza que necesita.
 */

import React from "react";
import { ProductStrategyFormProps } from "@/types/product-creation";
import { ProductMeasurementField, PropertyGroupLabel } from "../FormFields";

export const ProfileProductForm: React.FC<ProductStrategyFormProps> = ({
  material,
  dimensions,
  onDimensionChange,
  selectedUnit,
  availableUnits,
}) => {
  const materialProps = material.properties as any;
  const shape = materialProps?.shape;

  // Helper to format shape display name
  const getShapeDisplayName = (s: string) => {
    const shapes: Record<string, string> = {
      ROUND: "Redondo (Tubo/Barra)",
      RECTANGULAR: "Rectangular / Cuadrado",
      L_SHAPE: "Angulo (L)",
      FLAT: "Platina / Solera",
      U_SHAPE: "Canal (U)",
    };
    return shapes[s] || s;
  };

  return (
    <div className="space-y-6">
      {/* Informacion del material base - Mas compacta */}
      {(shape ||
        materialProps?.thickness ||
        materialProps?.diameter ||
        materialProps?.width ||
        materialProps?.height) && (
        <div className="bg-default-50 p-4 rounded-2xl border border-default-100">
          <p className="text-[10px] font-bold text-default-400 uppercase tracking-widest mb-3">
            Especificaciones Tecnicas
          </p>
          <div className="grid grid-cols-2 gap-x-4 gap-y-3">
            {shape && (
              <div className="flex flex-col">
                <span className="text-[9px] uppercase text-default-400 font-bold tracking-tight">
                  Forma
                </span>
                <span className="text-xs font-bold text-foreground truncate">
                  {getShapeDisplayName(shape)}
                </span>
              </div>
            )}
            {materialProps?.thickness && (
              <div className="flex flex-col">
                <span className="text-[9px] uppercase text-default-400 font-bold tracking-tight">
                  Espesor
                </span>
                <span className="text-xs font-bold text-foreground">
                  {materialProps.thickness.gauge
                    ? `Cal. ${materialProps.thickness.gauge}`
                    : `${materialProps.thickness.value} ${materialProps.thickness.unit}`}
                </span>
              </div>
            )}
            {materialProps?.diameter && (
              <div className="flex flex-col">
                <span className="text-[9px] uppercase text-default-400 font-bold tracking-tight">
                  Diametro
                </span>
                <span className="text-xs font-bold text-foreground">
                  {materialProps.diameter.value} {materialProps.diameter.unit}
                </span>
              </div>
            )}
            {materialProps?.width && (
              <div className="flex flex-col">
                <span className="text-[9px] uppercase text-default-400 font-bold tracking-tight">
                  Ancho
                </span>
                <span className="text-xs font-bold text-foreground">
                  {materialProps.width.value} {materialProps.width.unit}
                </span>
              </div>
            )}
            {materialProps?.height && (
              <div className="flex flex-col">
                <span className="text-[9px] uppercase text-default-400 font-bold tracking-tight">
                  Alto
                </span>
                <span className="text-xs font-bold text-foreground">
                  {materialProps.height.value} {materialProps.height.unit}
                </span>
              </div>
            )}
            <div className="flex flex-col">
              <span className="text-[9px] uppercase text-default-400 font-bold tracking-tight">
                Tipo
              </span>
              <span className="text-xs font-bold text-foreground">
                {materialProps?.is_hollow ? "Hueco" : "Macizo"}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Campo de longitud */}
      <div className="space-y-4 pt-2 px-1">
        <PropertyGroupLabel
          title="Medida Requerida"
          description="Largo de la pieza para el product"
        />

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
          isRequired={true}
        />
      </div>

      {!dimensions.length && (
        <div className="p-3 bg-warning-50 border border-warning-100 rounded-xl">
          <p className="text-[10px] font-bold text-warning-600 text-center uppercase tracking-tighter">
             Se requiere longitud para el calculo de price
          </p>
        </div>
      )}
    </div>
  );
};
