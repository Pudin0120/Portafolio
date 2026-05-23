import React, { type Key } from "react";
import {
  Input,
  Switch,
  Divider,
  Autocomplete,
  AutocompleteItem,
  Button,
  RadioGroup,
  Radio,
  Select,
  SelectItem,
} from "@heroui/react";
import {
  Plus,
  ChevronDown,
  ChevronUp,
  Ruler,
  Maximize,
  Box,
} from "lucide-react";
import type { StrategyFormComponentProps } from "@/types/material-creation";
import { PropertyLabel, MeasurementField } from "../FormFields";
import { FormSection, FormGrid, FormColumn, FormContainer } from "./FormLayout";
import { ImageUpload } from "@components/common/ImageUpload";
import { BarcodeInput } from "@components/common/BarcodeInput";
import { formatCurrency } from "@/utils";
import { IdentityHeader } from "../IdentityHeader";

/**
 * PROFILE Strategy Form - Built with Builder Pattern approach
 */
export const ProfileMaterialForm: React.FC<StrategyFormComponentProps> = ({
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

  const shape = dynamicProperties["shape"] || "";
  const isHollowShape = ["L_SHAPE", "U_SHAPE", "FLAT"].includes(shape);
  const isHollow = isHollowShape
    ? true
    : (dynamicProperties["is_hollow"] ?? true);

  const purchasePriceDisplay = purchasePrice
    ? formatCurrency(parseFloat(purchasePrice)).replace("$", "").trim()
    : "";

  const salePriceDisplay = salePrice
    ? formatCurrency(parseFloat(salePrice)).replace("$", "").trim()
    : "";

  const shapeOptions =
    strategyConfig?.properties?.find((p) => p.name === "shape")?.options || [];

  return (
    <FormContainer>
      {/* --- COLUMNA IZQUIERDA: Identidad y Costos --- */}
      <FormColumn>
        <FormSection title="Identidad del Material" sticky>
          <IdentityHeader
            name={name}
            setName={setName}
            strategyName="PROFILE"
            materialTypeName={materialTypeObj?.name}
          />

          <div className="space-y-4">
            {materialTypeObj?.requires_composition !== false && (
              <div className="space-y-1">
                <Autocomplete
                  label="Composicion"
                  placeholder="Ej: Acero, Aluminio..."
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
                  placeholder="Description del material"
                  size="sm"
                  variant="bordered"
                  value={description}
                  onValueChange={(val: string) => setDescription(val)}
                />
              </div>
            )}
          </div>
        </FormSection>

        <FormSection title="Costos y Precios" sticky>
          <FormGrid>
            <Input
              type="text"
              label="Price Compra"
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

      {/* --- COLUMNA DERECHA: Properties Tecnicas y Visual --- */}
      <FormColumn>
        <FormSection title="Visual y Marca">
          <ImageUpload
            value={dynamicProperties["image_url"]}
            onChange={(url: string) => onPropertyChange("image_url", url)}
          />
        </FormSection>

        <FormSection title="Properties Tecnicas" sticky>
          <div className="bg-default-50/50 rounded-xl p-4 border border-default-100 space-y-6">
            {/* 1. SECCION DE FORMA */}
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Box className="w-4 h-4 text-primary" />
                <span className="text-xs font-bold text-default-700 uppercase tracking-tight">
                  Geometria del Perfil
                </span>
              </div>

              <Select
                label="Forma de la seccion"
                placeholder="Selecciona una forma"
                selectedKeys={shape ? [shape] : []}
                onSelectionChange={(keys: any) => {
                  const selected = Array.from(keys)[0] as string;
                  onPropertyChange("shape", selected);
                }}
                size="sm"
                variant="bordered"
              >
                {(shapeOptions as any[]).map((option) => (
                  <SelectItem
                    key={option.value}
                    textValue={option.display_name}
                  >
                    {option.display_name}
                  </SelectItem>
                ))}
              </Select>

              {!isHollowShape && (
                <div className="flex items-center justify-between p-3 bg-content2 rounded-xl shadow-sm border border-default-100">
                  <div>
                    <p className="text-xs font-bold text-foreground">
                      Es Perfil Hueco?
                    </p>
                    <p className="text-[10px] text-default-500">
                      Marca si es tubular o macizo
                    </p>
                  </div>
                  <Switch
                    isSelected={isHollow}
                    onValueChange={(val: boolean) =>
                      onPropertyChange("is_hollow", val)
                    }
                    size="sm"
                    color="primary"
                  />
                </div>
              )}
            </div>

            {/* 2. ESPESOR (THICKNESS / GAUGE) - Solo si es hueco */}
            {isHollow && (
              <>
                <Divider />
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Ruler className="w-4 h-4 text-primary" />
                    <span className="text-xs font-bold text-default-700 uppercase tracking-tight">
                      Espesor / Calibre
                    </span>
                  </div>

                  <RadioGroup
                    value={dynamicProperties[`thickness_type`] || "measurement"}
                    onValueChange={(type: string) =>
                      onPropertyChange(`thickness_type`, type)
                    }
                    orientation="horizontal"
                    size="sm"
                    classNames={{ wrapper: "gap-4" }}
                  >
                    <Radio value="measurement">Medida (mm/in)</Radio>
                    <Radio value="gauge">Calibre (AWG)</Radio>
                  </RadioGroup>

                  {dynamicProperties[`thickness_type`] === "gauge" ? (
                    <Input
                      type="number"
                      label="Number de Calibre"
                      placeholder="Ej: 14"
                      value={String(dynamicProperties[`thickness_gauge`] || "")}
                      onValueChange={(value: string) =>
                        onPropertyChange(
                          `thickness_gauge`,
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
                        label="Espesor de Pared"
                        step="0.01"
                        placeholder="0.00"
                        value={String(
                          dynamicProperties[`thickness_value`] || "",
                        )}
                        onValueChange={(value: string) =>
                          onPropertyChange(
                            `thickness_value`,
                            value ? parseFloat(value) : undefined,
                          )
                        }
                        variant="bordered"
                        size="sm"
                        className="flex-1"
                      />
                      <Select
                        label="Unidad"
                        selectedKeys={
                          new Set([dynamicProperties[`thickness_unit`] || "mm"])
                        }
                        onSelectionChange={(keys: any) =>
                          onPropertyChange(
                            `thickness_unit`,
                            Array.from(keys)[0],
                          )
                        }
                        className="w-28"
                        size="sm"
                        variant="bordered"
                      >
                        <SelectItem key="mm" value="mm" title="Milimetros">
                          mm
                        </SelectItem>
                        <SelectItem key="in" value="in" title="Pulgadas">
                          in
                        </SelectItem>
                      </Select>
                    </div>
                  )}
                </div>
              </>
            )}

            <Divider />

            {/* 3. DIMENSIONES SEGUN FORMA */}
            <div className="space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">
              <div className="flex items-center gap-2">
                <Maximize className="w-4 h-4 text-primary" />
                <span className="text-xs font-bold text-default-700 uppercase tracking-tight">
                  Dimensiones de Seccion
                </span>
              </div>

              <div className="space-y-6">
                {/* Diametro (Solo para ROUND) */}
                {shape === "ROUND" && (
                  <div className="space-y-2">
                    <PropertyLabel displayName="Diametro Exterior" isRequired />
                    <MeasurementField
                      propName="diameter"
                      propUnit={dynamicProperties[`diameter_unit`] || "cm"}
                      prop={
                        {
                          ...(strategyConfig.properties?.find(
                            (p) => p.name === "diameter",
                          ) || {}),
                          name: "diameter",
                          type: "measurement",
                          default_unit: "cm",
                          preferred_units: ["mm", "cm", "in"],
                        } as any
                      }
                      dynamicProperties={dynamicProperties}
                      onPropertyChange={onPropertyChange}
                      isRequired
                    />
                  </div>
                )}

                {/* Ancho (Para todo lo que NO sea ROUND) */}
                {shape && shape !== "ROUND" && (
                  <div className="space-y-2">
                    <PropertyLabel displayName="Ancho / Base" isRequired />
                    <MeasurementField
                      propName="width"
                      propUnit={dynamicProperties[`width_unit`] || "cm"}
                      prop={
                        {
                          ...(strategyConfig.properties?.find(
                            (p) => p.name === "width",
                          ) || {}),
                          name: "width",
                          type: "measurement",
                          default_unit: "cm",
                          preferred_units: ["mm", "cm", "in"],
                        } as any
                      }
                      dynamicProperties={dynamicProperties}
                      onPropertyChange={onPropertyChange}
                      isRequired
                    />
                  </div>
                )}

                {/* Alto (Solo para RECTANGULAR, L_SHAPE, U_SHAPE) */}
                {["RECTANGULAR", "L_SHAPE", "U_SHAPE"].includes(shape) && (
                  <div className="space-y-2">
                    <PropertyLabel displayName="Altura / Ala" isRequired />
                    <MeasurementField
                      propName="height"
                      propUnit={dynamicProperties[`height_unit`] || "cm"}
                      prop={
                        {
                          ...(strategyConfig.properties?.find(
                            (p) => p.name === "height",
                          ) || {}),
                          name: "height",
                          type: "measurement",
                          default_unit: "cm",
                          preferred_units: ["mm", "cm", "in"],
                        } as any
                      }
                      dynamicProperties={dynamicProperties}
                      onPropertyChange={onPropertyChange}
                      isRequired
                    />
                  </div>
                )}

                <Divider />

                {/* Longitud Comercial (Comun para todos) */}
                <div className="space-y-2">
                  <PropertyLabel
                    displayName="Longitud Comercial"
                    isRequired
                    description="Largo estandar de la pieza (ej: 6m)"
                  />
                  <MeasurementField
                    propName="length"
                    propUnit={dynamicProperties[`length_unit`] || "m"}
                    prop={
                      {
                        ...(strategyConfig.properties?.find(
                          (p) => p.name === "length",
                        ) || {}),
                        name: "length",
                        type: "measurement",
                        default_unit: "m",
                        preferred_units: ["m", "cm", "in"],
                      } as any
                    }
                    dynamicProperties={dynamicProperties}
                    onPropertyChange={onPropertyChange}
                    isRequired
                  />
                </div>
              </div>
            </div>

            {/* --- SECCION DESPLEGABLE: Detalles Adicionales --- */}
            <div className="space-y-4 pt-4 border-t border-default-100">
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
                      placeholder="Ej: Rojo, RAL 9005"
                      size="sm"
                      variant="bordered"
                      value={dynamicProperties["color"] || ""}
                      onValueChange={(val: string) =>
                        onPropertyChange("color", val)
                      }
                    />
                    <Input
                      label="Marca"
                      placeholder="Ej: Aceros S.A."
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
                      placeholder="Ej: PN-12345"
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
