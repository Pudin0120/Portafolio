/**
 * Componente de formulario completo para la estrategia SOLID (Solidos)
 */

import React, { type Key } from "react";
import {
  Input,
  Divider,
  Autocomplete,
  AutocompleteItem,
  Button,
} from "@heroui/react";
import { Plus, ChevronDown, ChevronUp, Scale, Box, X } from "lucide-react";
import type {
  PropertyConfig,
  StrategyFormComponentProps,
} from "@/types/material-creation";
import { PropertyLabel, MeasurementField } from "../FormFields";
import { FormSection, FormGrid, FormColumn, FormContainer } from "./FormLayout";
import { ImageUpload } from "@components/common/ImageUpload";
import { BarcodeInput } from "@components/common/BarcodeInput";
import { formatCurrency } from "@/utils";
import { IdentityHeader } from "../IdentityHeader";

/**
 * SOLID Strategy Form - Full Layout
 */
export const SolidMaterialForm: React.FC<StrategyFormComponentProps> = ({
  dynamicProperties,
  onPropertyChange,
  strategyConfig,
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

  const hasMassValue =
    dynamicProperties["mass_value"] !== undefined &&
    dynamicProperties["mass_value"] !== null &&
    dynamicProperties["mass_value"] !== "";

  const hasVolumeValue =
    dynamicProperties["volume_value"] !== undefined &&
    dynamicProperties["volume_value"] !== null &&
    dynamicProperties["volume_value"] !== "";

  const selectedMode = hasMassValue ? "mass" : hasVolumeValue ? "volume" : null;

  const handleMassSelect = () => {
    onPropertyChange("mass_value", 1);
    onPropertyChange("mass_unit", "kg");
    onPropertyChange("volume_value", undefined);
    onPropertyChange("volume_unit", undefined);
  };

  const handleVolumeSelect = () => {
    onPropertyChange("volume_value", 1);
    onPropertyChange("volume_unit", "L");
    onPropertyChange("mass_value", undefined);
    onPropertyChange("mass_unit", undefined);
  };

  const handleClearMode = () => {
    onPropertyChange("mass_value", undefined);
    onPropertyChange("mass_unit", undefined);
    onPropertyChange("volume_value", undefined);
    onPropertyChange("volume_unit", undefined);
  };

  const selectedMeasurementProp: PropertyConfig = {
    display_name: selectedMode === "mass" ? "Masa" : "Volumen",
    name: selectedMode === "mass" ? "mass" : "volume",
    type: "measurement",
    required: true,
    description:
      selectedMode === "mass"
        ? "Peso neto del material"
        : "Capacidad o espacio que ocupa",
    default_unit: selectedMode === "mass" ? "kg" : "L",
    preferred_units:
      selectedMode === "mass" ? ["kg", "lb", "g"] : ["L", "m3", "mL"],
    ...(strategyConfig.properties?.find(
      (property) =>
        property.name === (selectedMode === "mass" ? "mass" : "volume"),
    ) ?? {}),
  };

  return (
    <FormContainer>
      {/* --- COLUMNA IZQUIERDA: Identidad y Costos --- */}
      <FormColumn>
        <FormSection title="Identidad del Material" sticky>
          <IdentityHeader
            name={name}
            setName={setName}
            strategyName="SOLID"
            materialTypeName={materialTypeObj?.name}
          />

          <div className="space-y-4">
            {materialTypeObj?.requires_composition !== false && (
              <div className="space-y-1">
                <Autocomplete
                  label="Composicion"
                  placeholder="Ej: Acero, Madera..."
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
            {!selectedMode ? (
              <div className="space-y-4">
                <p className="text-xs font-bold text-default-500 uppercase">
                  Como se cuantifica este material?
                </p>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  <Button
                    color="primary"
                    variant="bordered"
                    className="h-20 border-2"
                    onPress={handleMassSelect}
                  >
                    <div className="flex flex-col items-center gap-1">
                      <Scale className="w-5 h-5" />
                      <span className="text-sm font-bold">Por Masa</span>
                      <span className="text-[10px] opacity-60">
                        (kg, lb, g)
                      </span>
                    </div>
                  </Button>
                  <Button
                    color="primary"
                    variant="bordered"
                    className="h-20 border-2"
                    onPress={handleVolumeSelect}
                  >
                    <div className="flex flex-col items-center gap-1">
                      <Box className="w-5 h-5" />
                      <span className="text-sm font-bold">Por Volumen</span>
                      <span className="text-[10px] opacity-60">(L, m)</span>
                    </div>
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-6 animate-in fade-in duration-300">
                <div className="flex items-center justify-between pb-2 border-b border-default-100">
                  <div className="flex items-center gap-2">
                    {selectedMode === "mass" ? (
                      <Scale className="w-4 h-4 text-primary" />
                    ) : (
                      <Box className="w-4 h-4 text-primary" />
                    )}
                    <span className="text-xs font-bold text-default-700 uppercase tracking-tight">
                      {selectedMode === "mass"
                        ? "Masa del Material"
                        : "Volumen del Material"}
                    </span>
                  </div>
                  <Button
                    isIconOnly
                    variant="light"
                    size="sm"
                    color="danger"
                    onPress={handleClearMode}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>

                <div className="space-y-2">
                  <PropertyLabel
                    displayName={selectedMode === "mass" ? "Masa" : "Volumen"}
                    isRequired
                    description={
                      selectedMode === "mass"
                        ? "Peso neto del material"
                        : "Capacidad o espacio que ocupa"
                    }
                  />
                  <MeasurementField
                    propName={selectedMode === "mass" ? "mass" : "volume"}
                    propUnit={dynamicProperties[`${selectedMode}_unit`]}
                    prop={selectedMeasurementProp}
                    dynamicProperties={dynamicProperties}
                    onPropertyChange={onPropertyChange}
                    isRequired
                  />
                </div>

                <Button
                  variant="flat"
                  size="sm"
                  className="w-full text-tiny font-bold"
                  onPress={handleClearMode}
                >
                  Cambiar a {selectedMode === "mass" ? "Volumen" : "Masa"}
                </Button>
              </div>
            )}

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
                      placeholder="Ej: Gris, Negro..."
                      size="sm"
                      variant="bordered"
                      value={dynamicProperties["color"] || ""}
                      onValueChange={(val: string) =>
                        onPropertyChange("color", val)
                      }
                    />
                    <Input
                      label="Marca"
                      placeholder="Ej: Generic"
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
                      placeholder="Ej: S-100"
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
