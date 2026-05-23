import type { Key } from "react";

/**
 * Componente de formulario para la estrategia UNIT (Unidades)
 */

import {
  Input,
  Divider,
  Autocomplete,
  AutocompleteItem,
  Button,
} from "@heroui/react";
import { Plus, ChevronDown, ChevronUp, Package } from "lucide-react";
import type { StrategyFormComponentProps } from "@/types/material-creation";
import { FormSection, FormGrid, FormColumn, FormContainer } from "./FormLayout";
import { ImageUpload } from "@components/common/ImageUpload";
import { BarcodeInput } from "@components/common/BarcodeInput";
import { formatCurrency } from "@/utils";
import { IdentityHeader } from "../IdentityHeader";

/**
 * UNIT Strategy Form - Built with Builder Pattern approach
 */
export const UnitMaterialForm: React.FC<StrategyFormComponentProps> = ({
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

  return (
    <FormContainer>
      {/* --- COLUMNA IZQUIERDA: Identidad y Costos --- */}
      <FormColumn>
        <FormSection title="Identidad del Material" sticky>
          <IdentityHeader
            name={name}
            setName={setName}
            strategyName="UNIT"
            materialTypeName={materialTypeObj?.name}
          />

          <div className="space-y-4">
            {materialTypeObj?.requires_composition !== false && (
              <div className="space-y-1">
                <Autocomplete
                  label="Composicion"
                  placeholder="Ej: Acero, Plastico..."
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
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Package className="w-4 h-4 text-primary" />
                <span className="text-xs font-bold text-default-700 uppercase tracking-tight">
                  Atributos de Unidad
                </span>
              </div>

              <FormGrid>
                <Input
                  label="Marca"
                  placeholder="Ej: Hettich"
                  size="sm"
                  variant="bordered"
                  value={dynamicProperties["brand"] || ""}
                  onValueChange={(val: string) =>
                    onPropertyChange("brand", val)
                  }
                />
                <Input
                  label="Referencia / Parte"
                  placeholder="Ej: 123-ABC"
                  size="sm"
                  variant="bordered"
                  value={dynamicProperties["part_number"] || ""}
                  onValueChange={(val: string) =>
                    onPropertyChange("part_number", val)
                  }
                />
              </FormGrid>
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
                      placeholder="Ej: Cromado, Negro"
                      size="sm"
                      variant="bordered"
                      value={dynamicProperties["color"] || ""}
                      onValueChange={(val: string) =>
                        onPropertyChange("color", val)
                      }
                    />
                    <Input
                      label="Modelo"
                      placeholder="Ej: Serie Pro"
                      size="sm"
                      variant="bordered"
                      value={dynamicProperties["model"] || ""}
                      onValueChange={(val: string) =>
                        onPropertyChange("model", val)
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
