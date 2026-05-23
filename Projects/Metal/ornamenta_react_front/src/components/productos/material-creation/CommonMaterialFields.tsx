/**
 * Componente que agrupa los campos comunes para todas las estrategias:
 * - Imagen
 * - Color
 * - Marca y Referencia (seccion opcional)
 */

import React, { useState } from "react";
import { Input, Divider } from "@heroui/react";
import { ImageUpload } from "@components/common/ImageUpload";
import { PropertyLabel } from "./FormFields";
import { ChevronDown, ChevronUp } from "lucide-react";

interface CommonMaterialFieldsProps {
  name?: string;
  onNameChange?: (val: string) => void;
  dynamicProperties: Record<string, any>;
  onPropertyChange: (key: string, value: any) => void;
}

export const CommonMaterialFields: React.FC<CommonMaterialFieldsProps> = ({
  name,
  onNameChange,
  dynamicProperties,
  onPropertyChange,
}) => {
  const [showOptional, setShowOptional] = useState(false);

  return (
    <div className="space-y-6">
      <ImageUpload
        value={dynamicProperties["image_url"]}
        onChange={(url) => onPropertyChange("image_url", url)}
      />

      {/* Color - Ahora disponible para todas las estrategias */}
      <div className="space-y-2">
        <PropertyLabel
          displayName="Color"
          isRequired={false}
          description="Color del material (ej: Rojo, RAL 9005)"
        />
        <Input
          placeholder="Ej: Rojo, RAL 9005, Galvanizado"
          value={dynamicProperties["color"] || ""}
          onValueChange={(value: string) => onPropertyChange("color", value)}
          variant="bordered"
          size="sm"
        />
      </div>

      <Divider className="my-2" />

      {/* --- SECCION OPCIONAL CON TOGGLE --- */}
      <div className="space-y-4">
        <div
          className="flex items-center justify-between cursor-pointer p-2 hover:bg-default-100 rounded-lg transition-colors"
          onClick={() => setShowOptional(!showOptional)}
        >
          <div className="flex flex-col">
            <span className="text-sm font-bold text-default-600">
              Informacion Adicional
            </span>
            <span className="text-tiny text-default-400">
              Marca, Modelo y Referencia
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-tiny font-medium text-primary">
              {showOptional ? "Ver menos" : "Completar"}
            </span>
            {showOptional ? (
              <ChevronUp className="w-4 h-4 text-primary" />
            ) : (
              <ChevronDown className="w-4 h-4 text-primary" />
            )}
          </div>
        </div>

        {showOptional && (
          <div className="space-y-4 px-1 pb-2 animate-in fade-in slide-in-from-top-2 duration-300">
            {/* Marca */}
            <div className="space-y-2">
              <PropertyLabel
                displayName="Marca"
                isRequired={false}
                description="Fabricante del product"
              />
              <Input
                placeholder="Ej: Pintuco, Hettich"
                value={dynamicProperties["brand"] || ""}
                onValueChange={(value: string) =>
                  onPropertyChange("brand", value)
                }
                variant="bordered"
                size="sm"
              />
            </div>

            {/* Modelo */}
            <div className="space-y-2">
              <PropertyLabel
                displayName="Modelo"
                isRequired={false}
                description="Modelo especifico del product"
              />
              <Input
                placeholder="Ej: Premium, Serie X"
                value={dynamicProperties["model"] || ""}
                onValueChange={(value: string) =>
                  onPropertyChange("model", value)
                }
                variant="bordered"
                size="sm"
              />
            </div>

            {/* Referencia */}
            <div className="space-y-2">
              <PropertyLabel
                displayName="Referencia / Parte"
                isRequired={false}
                description="Codigo de referencia de fabrica"
              />
              <Input
                placeholder="Ej: REF-12345"
                value={dynamicProperties["part_number"] || ""}
                onValueChange={(value: string) =>
                  onPropertyChange("part_number", value)
                }
                variant="bordered"
                size="sm"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
