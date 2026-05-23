/**
 * Modal para agregar o edit un componente del product compuesto
 * Incluye selector de product, quantity y reglas dimensionales
 */

import React, { useState, useMemo } from "react";
import {
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  Divider,
  Card,
  CardBody,
  Chip,
  useDisclosure,
} from "@heroui/react";
import { Package, Plus } from "lucide-react";
import { CenteredModal } from "@components/common/CenteredModal";
import { ProductSelector } from "../ProductSelector";
import { QuantityTypeSelector } from "./QuantityTypeSelector";
import { DimensionalRulesEditor } from "./DimensionalRulesEditor";
import { SimpleProductForm } from "../SimpleProductForm";
import {
  CompositeComponentForm,
  ComponentRelationship,
  CompositeDimensions,
} from "./types";
import { Product } from "@/types/products";
import { formatPrice } from "@/utils";

const getNumericPrice = (price: Product["price"]): number => {
  const parsed =
    typeof price === "number" ? price : Number.parseFloat(price ?? "");
  return Number.isFinite(parsed) ? parsed : 0;
};

type ComponentConfigModalProps = {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (component: CompositeComponentForm) => void;
  editingComponent?: CompositeComponentForm; // Para modo edicion
  parentDimensions: CompositeDimensions;
  excludeProductIds?: string[]; // No permitir agregar products ya agregados
};

export const ComponentConfigModal: React.FC<ComponentConfigModalProps> = ({
  isOpen,
  onOpenChange,
  onSave,
  editingComponent,
  parentDimensions,
  excludeProductIds = [],
}) => {
  const {
    isOpen: isCreateSimpleOpen,
    onOpen: onCreateSimpleOpen,
    onOpenChange: onCreateSimpleOpenChange,
    onClose: onCreateSimpleClose,
  } = useDisclosure();

  const [selectedProductId, setSelectedProductId] = useState(
    editingComponent?.product_id || "",
  );
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(
    editingComponent?.product || null,
  );
  const [baseQuantity, setBaseQuantity] = useState(
    editingComponent?.base_quantity || 1,
  );
  const [relationship, setRelationship] = useState<ComponentRelationship>(
    editingComponent?.relationship || {
      quantity_type: "fixed",
      base_quantity: 1,
      quantity_multiplier: 1,
    },
  );
  const [refreshProductsTrigger, setRefreshProductsTrigger] = useState(0);
  const [simpleProductSuccess, setSimpleProductSuccess] = useState("");

  // Preview calculado localmente (simple, sin precios reales)
  const calculatedQuantity = useMemo(() => {
    if (relationship.quantity_type === "fixed") {
      return (
        relationship.base_quantity * (relationship.quantity_multiplier || 1)
      );
    } else if (relationship.quantity_type === "perimeter") {
      const perimeter = (parentDimensions.width + parentDimensions.height) * 2;
      return perimeter * (relationship.quantity_multiplier || 1);
    } else if (relationship.quantity_type === "area") {
      const area = parentDimensions.width * parentDimensions.height;
      return area * (relationship.quantity_multiplier || 1);
    }
    return 0;
  }, [relationship, parentDimensions]);

  const handleSave = () => {
    if (!selectedProduct) {
      // TODO: Mostrar error con toast
      return;
    }

    const component: CompositeComponentForm = {
      product_id: selectedProduct.id,
      product: selectedProduct,
      base_quantity: baseQuantity,
      relationship,
    };

    onSave(component);
    onOpenChange(false);

    // Reset
    setSelectedProductId("");
    setSelectedProduct(null);
    setBaseQuantity(1);
    setRelationship({
      quantity_type: "fixed",
      base_quantity: 1,
      quantity_multiplier: 1,
    });
  };

  const handleCancel = () => {
    onOpenChange(false);
    // Reset
    setSelectedProductId("");
    setSelectedProduct(null);
    setBaseQuantity(1);
    setRelationship({
      quantity_type: "fixed",
      base_quantity: 1,
      quantity_multiplier: 1,
    });
  };

  const handleSimpleProductSuccess = (message: string) => {
    setSimpleProductSuccess(message);
    setRefreshProductsTrigger((prev) => prev + 1);
    onCreateSimpleClose();
    setTimeout(() => setSimpleProductSuccess(""), 5000);
  };

  const handleSimpleProductError = () => {
    // El manejo visual del error queda dentro de SimpleProductForm
    // para no duplicar feedback en este modal.
  };

  return (
    <CenteredModal
      isOpen={isOpen}
      onOpenChange={onOpenChange}
      size="5xl"
      backdrop="blur"
      scrollBehavior="inside"
    >
      {() => (
        <>
          <ModalHeader className="border-b border-divider py-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-xl">
                <Package className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h3 className="text-lg font-bold">
                  {editingComponent
                    ? "Edit Componente"
                    : "Agregar Componente"}
                </h3>
                <p className="text-xs text-default-500 font-normal">
                  Configura el product y sus reglas de calculo
                </p>
              </div>
            </div>
          </ModalHeader>

          <ModalBody className="py-6 space-y-6">
            {/* ProductSelector */}
            <div>
              <div className="mb-3 flex items-center justify-between">
                <p className="text-xs font-bold uppercase tracking-wider text-default-400">
                  Seleccion de componente
                </p>
                <Button
                  size="sm"
                  color="primary"
                  variant="flat"
                  startContent={<Plus className="w-4 h-4" />}
                  onPress={onCreateSimpleOpen}
                  className="font-semibold"
                >
                  Create Simple Product
                </Button>
              </div>

              {simpleProductSuccess && (
                <div className="mb-3 rounded-md bg-success-50 p-3 text-sm text-success">
                  {simpleProductSuccess}
                </div>
              )}

              <ProductSelector
                selectedProductId={selectedProductId}
                onProductChange={setSelectedProductId}
                onProductSelect={setSelectedProduct}
                excludeProductIds={excludeProductIds}
                label="Product Base"
                placeholder="Busca y selecciona un product"
                isRequired
                refreshTrigger={refreshProductsTrigger}
              />
            </div>

            <Divider />

            {/* QuantityTypeSelector */}
            <QuantityTypeSelector
              quantityType={relationship.quantity_type}
              baseQuantity={relationship.base_quantity}
              multiplier={relationship.quantity_multiplier || 1}
              onChange={(type, base, mult) => {
                setRelationship({
                  ...relationship,
                  quantity_type: type,
                  base_quantity: base,
                  quantity_multiplier: mult,
                });
              }}
            />

            <Divider />

            {/* DimensionalRulesEditor */}
            <DimensionalRulesEditor
              widthRule={relationship.width_rule}
              heightRule={relationship.height_rule}
              depthRule={relationship.depth_rule}
              parentDimensions={parentDimensions}
              onChange={(width, height, depth) => {
                setRelationship({
                  ...relationship,
                  width_rule: width,
                  height_rule: height,
                  depth_rule: depth,
                });
              }}
            />

            <Divider />

            {/* Preview Local */}
            {selectedProduct && (
              <Card className="border-2 border-primary/20 bg-primary/5">
                <CardBody className="p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <p className="text-[10px] font-bold uppercase tracking-widest text-primary mb-2">
                        Preview del Componente
                      </p>
                      <p className="text-sm font-bold text-foreground mb-1">
                        {selectedProduct.name}
                      </p>
                      <div className="flex items-center gap-2 text-xs text-default-500">
                        <Chip size="sm" color="primary" variant="flat">
                          {selectedProduct.product_type === "simple"
                            ? "Simple"
                            : "Compuesto"}
                        </Chip>
                        {selectedProduct.material_name && (
                          <span>Material: {selectedProduct.material_name}</span>
                        )}
                      </div>
                    </div>

                    <div className="text-right space-y-1">
                      <div>
                        <p className="text-[10px] font-bold uppercase text-default-400">
                          Quantity Calculada
                        </p>
                        <p className="text-lg font-black text-primary">
                          {calculatedQuantity.toFixed(2)}
                        </p>
                      </div>
                      {getNumericPrice(selectedProduct.price) > 0 && (
                        <div>
                          <p className="text-[10px] font-bold uppercase text-default-400">
                            Subtotal Estimado
                          </p>
                          <p className="text-sm font-bold text-success">
                            $
                            {formatPrice(
                              getNumericPrice(selectedProduct.price) *
                                calculatedQuantity,
                            )}{" "}
                            {selectedProduct.currency || "COP"}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Info de reglas aplicadas */}
                  <div className="mt-3 pt-3 border-t border-primary/10 space-y-1">
                    <p className="text-[9px] font-bold uppercase text-default-400">
                      Reglas Aplicadas:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {relationship.width_rule && (
                        <Chip size="sm" variant="flat" color="secondary">
                          Ancho:{" "}
                          {relationship.width_rule.reference_type === "parent"
                            ? `Sigue ${relationship.width_rule.parent_dimension}`
                            : `${relationship.width_rule.fixed_value}mm`}
                        </Chip>
                      )}
                      {relationship.height_rule && (
                        <Chip size="sm" variant="flat" color="secondary">
                          Alto:{" "}
                          {relationship.height_rule.reference_type === "parent"
                            ? `Sigue ${relationship.height_rule.parent_dimension}`
                            : `${relationship.height_rule.fixed_value}mm`}
                        </Chip>
                      )}
                      {relationship.depth_rule && (
                        <Chip size="sm" variant="flat" color="secondary">
                          Profundidad:{" "}
                          {relationship.depth_rule.reference_type === "parent"
                            ? `Sigue ${relationship.depth_rule.parent_dimension}`
                            : `${relationship.depth_rule.fixed_value}mm`}
                        </Chip>
                      )}
                    </div>
                  </div>
                </CardBody>
              </Card>
            )}
          </ModalBody>

          <ModalFooter className="border-t border-divider py-4">
            <Button
              color="default"
              variant="flat"
              onPress={handleCancel}
              size="md"
              className="font-bold"
            >
              Cancel
            </Button>
            <Button
              color="primary"
              variant="solid"
              onPress={handleSave}
              isDisabled={!selectedProduct}
              className="font-bold px-10 h-11 shadow-lg shadow-primary/20"
              size="md"
            >
              {editingComponent ? "Save Cambios" : "Agregar Componente"}
            </Button>
          </ModalFooter>

          <CenteredModal
            isOpen={isCreateSimpleOpen}
            onOpenChange={onCreateSimpleOpenChange}
            size="5xl"
            backdrop="blur"
            scrollBehavior="inside"
          >
            {() => (
              <>
                <ModalHeader className="flex flex-col gap-1 border-b border-divider">
                  <h3 className="text-xl font-bold text-primary">
                    Create Simple Product
                  </h3>
                  <p className="text-sm font-normal text-default-500">
                    Se agregara automaticamente al selector al finalizar.
                  </p>
                </ModalHeader>
                <ModalBody className="py-6">
                  <SimpleProductForm
                    onSuccess={handleSimpleProductSuccess}
                    onError={handleSimpleProductError}
                  />
                </ModalBody>
              </>
            )}
          </CenteredModal>
        </>
      )}
    </CenteredModal>
  );
};
