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
import { Plus, ChevronDown, ChevronUp, Ruler, Maximize } from "lucide-react";
import type { StrategyFormComponentProps } from "@/types/material-creation";
import { PropertyLabel, MeasurementField } from "../FormFields";
import { FormSection, FormGrid, FormColumn, FormContainer } from "./FormLayout";
import { ImageUpload } from "@components/common/ImageUpload";
import { BarcodeInput } from "@components/common/BarcodeInput";
import { formatCurrency } from "@/utils";
import { IdentityHeader } from "../IdentityHeader";

/**
 * SHEET Strategy Form - Built with Builder Pattern approach

 * Handles Sheet-specific logic: Area vs Dimensions toggle, Gauge handling, and redundancy cleanup.
 */
export const SheetMaterialForm: React.FC<StrategyFormComponentProps> = ({
  dynamicProperties,
  onPropertyChange,
  strategyConfig,
  inputMode,
  onInputModeChange,
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

  const isDimensionsMode = inputMode !== "area_direct";

  const handleToggleMode = (isSelected: boolean) => {
    onInputModeChange(isSelected ? "dimensions" : "area_direct");
  };

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
        <FormSection title="Identidad del Material" sticky>
          <IdentityHeader
            name={name}
            setName={setName}
            strategyName="SHEET"
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
          <div className="bg-default-50/50 rounded-xl p-4 border border-default-100 space-y-8">
            {/* 1. SECCION DE ESPESOR (THICKNESS / GAUGE) */}
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Ruler className="w-4 h-4 text-primary" />
                <span className="text-xs font-bold text-default-700 uppercase tracking-tight">
                  Espesor / Calibre
                </span>
              </div>

              <RadioGroup
                value={dynamicProperties[`thickness_type`] || "gauge"}
                onValueChange={(type: string) =>
                  onPropertyChange(`thickness_type`, type)
                }
                orientation="horizontal"
                size="sm"
                classNames={{ wrapper: "gap-4" }}
              >
                <Radio value="gauge">Calibre (AWG)</Radio>
                <Radio value="measurement">Medida (mm/in)</Radio>
              </RadioGroup>

              {dynamicProperties[`thickness_type`] === "gauge" ||
              !dynamicProperties[`thickness_type`] ? (
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
                    label="Espesor"
                    step="0.01"
                    placeholder="0.00"
                    value={String(dynamicProperties[`thickness_value`] || "")}
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
                      onPropertyChange(`thickness_unit`, Array.from(keys)[0])
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

            <Divider />

            {/* 2. MODO DE ENTRADA: SWITCH PARA AREA vs DIMENSIONES */}
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-content2 rounded-xl shadow-sm border border-default-100">
                <div className="flex items-center gap-3">
                  <div
                    className={`p-2 rounded-lg ${isDimensionsMode ? "bg-primary/10 text-primary" : "bg-secondary/10 text-secondary"}`}
                  >
                    {isDimensionsMode ? (
                      <Maximize size={18} />
                    ) : (
                      <Ruler size={18} />
                    )}
                  </div>
                  <div>
                    <p className="text-xs font-bold text-foreground">
                      {isDimensionsMode
                        ? "Dimensiones (Ancho x Largo)"
                        : "Area Directa"}
                    </p>
                    <p className="text-[10px] text-default-500">
                      {isDimensionsMode
                        ? "Calculo automatico de area"
                        : "Ingreso manual del area total"}
                    </p>
                  </div>
                </div>
                <Switch
                  isSelected={isDimensionsMode}
                  onValueChange={handleToggleMode}
                  color="primary"
                  size="sm"
                />
              </div>

              {/* 3. CAMPOS DINAMICOS SEGUN EL MODO SELECCIONADO */}
              <div className="space-y-6 animate-in fade-in slide-in-from-top-2 duration-300">
                {strategyConfig.properties
                  ?.filter((prop) => shouldShowProperty(prop))
                  // Filtramos los que ya manejamos manualmente arriba para no duplicar
                  .filter(
                    (prop) =>
                      ![
                        "color",
                        "brand",
                        "part_number",
                        "thickness",
                        "thickness_type",
                        "thickness_gauge",
                        "area",
                        "width",
                        "length",
                      ].includes(prop.name),
                  )
                  .map((prop) => (
                    <div key={prop.name} className="space-y-2">
                      <PropertyLabel
                        displayName={prop.display_name}
                        isRequired={prop.required === true}
                        description={prop.description}
                        note={prop.note}
                      />
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

                {/* 4. CAMPOS MANUALES SEGUN EL MODO (AREA O DIMENSIONES) */}
                {!isDimensionsMode ? (
                  <div className="space-y-2 animate-in fade-in slide-in-from-top-2 duration-300">
                    <PropertyLabel
                      displayName="Area Total"
                      isRequired
                      description="Ingresa el area total de la lamina"
                    />
                    <MeasurementField
                      propName="area"
                      propUnit={dynamicProperties[`area_unit`] || "m2"}
                      prop={
                        {
                          name: "area",
                          type: "measurement",
                          default_unit: "m2",
                          preferred_units: ["m2", "cm2", "in2"],
                        } as any
                      }
                      dynamicProperties={dynamicProperties}
                      onPropertyChange={onPropertyChange}
                      isRequired
                    />
                  </div>
                ) : (
                  <div className="space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">
                    <div className="space-y-2">
                      <PropertyLabel displayName="Ancho" isRequired />
                      <MeasurementField
                        propName="width"
                        propUnit={dynamicProperties[`width_unit`] || "m"}
                        prop={
                          {
                            name: "width",
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
                    <div className="space-y-2">
                      <PropertyLabel displayName="Largo" isRequired />
                      <MeasurementField
                        propName="length"
                        propUnit={dynamicProperties[`length_unit`] || "m"}
                        prop={
                          {
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
                )}
              </div>

              {/* 5. SECCION DESPLEGABLE: Detalles Adicionales */}
              <div className="space-y-4 pt-4 border-t border-default-100">
                <button
                  type="button"
                  className="w-full flex items-center justify-between p-2 hover:bg-default-100 rounded-lg transition-colors text-left"
                  onClick={() =>
                    setShowOptionalTechnicalDetails(
                      !showOptionalTechnicalDetails,
                    )
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
          </div>
        </FormSection>
      </FormColumn>
    </FormContainer>
  );
};
