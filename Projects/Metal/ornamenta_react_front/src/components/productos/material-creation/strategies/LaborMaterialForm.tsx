/**
 * Componente de formulario completo para la estrategia LABOR (Mano de obra)
 */

import React, { type Key } from "react";
import {
  Input,
  Divider,
  Autocomplete,
  AutocompleteItem,
  Button,
  Select,
  SelectItem,
} from "@heroui/react";
import { Plus, ChevronDown, ChevronUp, Hammer } from "lucide-react";
import type { StrategyFormComponentProps } from "@/types/material-creation";
import { PropertyLabel, MeasurementField } from "../FormFields";
import { FormSection, FormGrid, FormColumn, FormContainer } from "./FormLayout";
import { ImageUpload } from "@components/common/ImageUpload";
import { BarcodeInput } from "@components/common/BarcodeInput";
import { formatCurrency } from "@/utils";
import { IdentityHeader } from "../IdentityHeader";

/**
 * LABOR Strategy Form - Full Layout
 */
export const LaborMaterialForm: React.FC<StrategyFormComponentProps> = ({
  dynamicProperties,
  onPropertyChange,
  strategyConfig,
  shouldShowProperty,
  materialTypeObj,
  compositions = [],
  compositionId = "",
  setCompositionId = () => {},
  setShowCreateCompositionModal = () => {},
  setShowTypeSelector = () => {},
  barcode = "",
  setBarcode = () => {},
  description = "",
  setDescription = () => {},
  purchasePrice = "",
  setPurchasePrice = () => {},
  salePrice = "",
  setSalePrice = () => {},
  showOptionalIdentity = false,
  setShowOptionalIdentity = () => {},
  showOptionalTechnicalDetails = false,
  setShowOptionalTechnicalDetails = () => {},
  name = "",
  setName = () => {},
}) => {
  if (!strategyConfig) return null;

  const purchasePriceDisplay = purchasePrice
    ? formatCurrency(parseFloat(purchasePrice)).replace("$", "").trim()
    : "";

  const salePriceDisplay = salePrice
    ? formatCurrency(parseFloat(salePrice)).replace("$", "").trim()
    : "";

  return (
    <FormContainer>
      {/* --- COLUMNA IZQUIERDA: Identidad y Costos --- */}
      <FormColumn>
        <FormSection title="Identidad de la Mano de Obra" sticky>
          <IdentityHeader
            name={name}
            setName={setName}
            strategyName="LABOR"
            materialTypeName={materialTypeObj?.name}
          />

          <div className="bg-default-50/50 rounded-xl p-4 border border-default-100 space-y-6">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Hammer className="w-4 h-4 text-primary" />
                <span className="text-xs font-bold text-default-700 uppercase tracking-tight">
                  Calculo de Quantity
                </span>
              </div>

              <div className="space-y-2">
                <PropertyLabel
                  displayName="Tipo de Unidad"
                  isRequired
                  description="Define como se cobrara el servicio"
                />
                <Select
                  placeholder="Selecciona tipo de unidad"
                  selectedKeys={new Set([dynamicProperties["unit_type"] || ""])}
                  onSelectionChange={(keys: any) => {
                    const selected = Array.from(keys)[0] as string;
                    onPropertyChange("unit_type", selected);
                    // Resetear properties relacionadas
                    onPropertyChange("length_value", undefined);
                    onPropertyChange("area_value", undefined);
                    onPropertyChange("width_value", undefined);
                    onPropertyChange("height_value", undefined);
                  }}
                  variant="flat"
                  size="sm"
                  isRequired
                >
                  <SelectItem key="linear_meter" value="linear_meter">
                    Metro Lineal (Perimetro)
                  </SelectItem>
                  <SelectItem key="square_meter" value="square_meter">
                    Metro Cuadrado (Area)
                  </SelectItem>
                </Select>
              </div>
            </div>

            {/* Properties condicionales segun unit_type */}
            <div className="space-y-6 pt-4 border-t border-default-100">
              {strategyConfig.properties
                ?.filter(
                  (prop) =>
                    shouldShowProperty(prop) && prop.name !== "unit_type",
                )
                .map((prop) => (
                  <div key={prop.name} className="space-y-2">
                    <PropertyLabel
                      displayName={prop.display_name}
                      isRequired={
                        prop.required === true ||
                        (prop.required === "conditional" &&
                          shouldShowProperty(prop))
                      }
                      description={prop.description}
                    />

                    {prop.type === "measurement" && (
                      <MeasurementField
                        propName={prop.name}
                        propUnit={dynamicProperties[`${prop.name}_unit`]}
                        prop={prop}
                        dynamicProperties={dynamicProperties}
                        onPropertyChange={onPropertyChange}
                        isRequired={
                          prop.required === true ||
                          (prop.required === "conditional" &&
                            shouldShowProperty(prop))
                        }
                        autoSetUnit={true}
                      />
                    )}
                  </div>
                ))}
            </div>
          </div>

          <div className="space-y-4">
            {materialTypeObj?.requires_composition !== false && (
              <div className="space-y-1">
                <Autocomplete
                  label="Composicion"
                  placeholder="Ej: Instalacion, Pintura..."
                  selectedKey={compositionId}
                  onSelectionChange={(key: Key | null) =>
                    setCompositionId(key as string)
                  }
                  isRequired
                  variant="flat"
                  size="sm"
                >
                  {compositions.map((comp) => (
                    <AutocompleteItem key={comp.id} textValue={comp.name}>
                      {comp.name}
                    </AutocompleteItem>
                  ))}
                </Autocomplete>
                <Button
                  color="secondary"
                  variant="light"
                  size="sm"
                  className="px-0 h-auto min-w-0 text-tiny"
                  onPress={() => setShowCreateCompositionModal(true)}
                  startContent={<Plus className="w-3 h-3" />}
                >
                  Nueva Composicion
                </Button>
                <Divider className="my-2" />
              </div>
            )}

            <button
              type="button"
              className="w-full flex items-center justify-between p-2 hover:bg-default-100 rounded-lg transition-colors text-left"
              onClick={() => setShowOptionalIdentity(!showOptionalIdentity)}
            >
              <div className="flex flex-col">
                <span className="text-sm font-bold text-default-600">
                  Detalles de Identidad
                </span>
                <span className="text-tiny text-default-400">
                  Codigo de barras y description
                </span>
              </div>
              <div className="flex items-center gap-2">
                {showOptionalIdentity ? (
                  <ChevronUp className="w-4 h-4 text-primary" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-primary" />
                )}
              </div>
            </button>

            {showOptionalIdentity && (
              <div className="space-y-4 px-1 pb-2 animate-in fade-in slide-in-from-top-2 duration-300">
                <BarcodeInput
                  label="Codigo de Barras"
                  placeholder="Opcional"
                  size="sm"
                  variant="bordered"
                  value={barcode}
                  onValueChange={(val: string) => setBarcode(val)}
                />
                <Input
                  label="Description"
                  placeholder="Description de la task"
                  size="sm"
                  variant="bordered"
                  value={description}
                  onValueChange={(val: string) => setDescription(val)}
                />
              </div>
            )}
          </div>
        </FormSection>

        <FormSection title="Tarifas y Costos" sticky>
          <FormGrid>
            <Input
              type="text"
              label="Costo por Unidad"
              size="sm"
              value={purchasePriceDisplay}
              onValueChange={(val: string) =>
                setPurchasePrice(val.replace(/\D/g, ""))
              }
              isRequired
              startContent={
                <span className="text-default-400 text-small font-bold">$</span>
              }
            />
            <Input
              type="text"
              label="Price Venta"
              size="sm"
              value={salePriceDisplay}
              onValueChange={(val: string) =>
                setSalePrice(val.replace(/\D/g, ""))
              }
              startContent={
                <span className="text-default-400 text-small font-bold">$</span>
              }
            />
          </FormGrid>
        </FormSection>
      </FormColumn>

      {/* --- COLUMNA DERECHA: Visual y Otros Detalles --- */}
      <FormColumn>
        <FormSection title="Visual y Referencia">
          <ImageUpload
            value={dynamicProperties["image_url"]}
            onChange={(url: string) => onPropertyChange("image_url", url)}
          />
        </FormSection>

        <FormSection title="Detalles Tecnicos">
          <div className="bg-default-50/50 rounded-xl p-4 border border-default-100">
            {/* --- SECCION DESPLEGABLE: Detalles Adicionales --- */}
            <div className="space-y-4">
              <button
                type="button"
                className="w-full flex items-center justify-between p-2 hover:bg-default-100 rounded-lg transition-colors text-left"
                onClick={() =>
                  setShowOptionalTechnicalDetails(!showOptionalTechnicalDetails)
                }
              >
                <div className="flex flex-col">
                  <span className="text-sm font-bold text-default-600">
                    Detalles Adicionales
                  </span>
                  <span className="text-tiny text-default-400">Opcional</span>
                </div>
                <div className="flex items-center gap-2">
                  {showOptionalTechnicalDetails ? (
                    <ChevronUp className="w-4 h-4 text-primary" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-primary" />
                  )}
                </div>
              </button>

              {showOptionalTechnicalDetails && (
                <div className="space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">
                  <FormGrid>
                    <Input
                      label="Color"
                      placeholder="Ej: Blanco, RAL 9003"
                      size="sm"
                      variant="bordered"
                      value={dynamicProperties["color"] || ""}
                      onValueChange={(val: string) =>
                        onPropertyChange("color", val)
                      }
                    />
                    <Input
                      label="Marca"
                      placeholder="Ej: Pintuco"
                      size="sm"
                      variant="bordered"
                      value={dynamicProperties["brand"] || ""}
                      onValueChange={(val: string) =>
                        onPropertyChange("brand", val)
                      }
                    />
                    <Input
                      label="Modelo"
                      placeholder="Ej: Premium, Serie X"
                      size="sm"
                      variant="bordered"
                      value={dynamicProperties["model"] || ""}
                      onValueChange={(val: string) =>
                        onPropertyChange("model", val)
                      }
                    />
                    <Input
                      label="Referencia / Parte"
                      placeholder="Ej: B-123"
                      size="sm"
                      variant="bordered"
                      value={dynamicProperties["part_number"] || ""}
                      onValueChange={(val: string) =>
                        onPropertyChange("part_number", val)
                      }
                    />
                  </FormGrid>
                </div>
              )}
            </div>
          </div>
        </FormSection>
      </FormColumn>
    </FormContainer>
  );
};
