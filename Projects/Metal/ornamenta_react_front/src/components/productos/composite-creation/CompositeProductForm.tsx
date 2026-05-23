/**
 * Formulario principal para creation de products compuestos
 * Multi-step con dimensiones dinamicas y relaciones calculadas
 */

import React, { useState, useEffect, useCallback } from "react";
import {
  Card,
  CardBody,
  CardHeader,
  Input,
  Textarea,
  Button,
  Tabs,
  Tab,
  Divider,
  useDisclosure,
} from "@heroui/react";
import {
  Package,
  Ruler,
  Settings,
  Eye,
  Plus,
  Image as ImageIcon,
} from "lucide-react";
import { useAuth } from "@hooks/useAuth";
import { apiClient } from "@services/apiClient";
import { useProducts } from "@context/ProductsContext";
import { ImageUpload } from "@components/common/ImageUpload";
import { ComponentConfigModal } from "./ComponentConfigModal";
import { ComponentsHierarchyTree } from "./ComponentsHierarchyTree";
import { CompositeProductPreview } from "./CompositeProductPreview";
import {
  CompositeFormState,
  CreateCompositeProductPayload,
  SimulateCompositeResponse,
  CompositeComponentForm,
} from "./types";
import { BaseProductCreationProps } from "@/types/product-creation";

export const CompositeProductForm: React.FC<BaseProductCreationProps> = ({
  onSuccess,
  onError,
}) => {
  const { user } = useAuth();
  const { fetchProducts } = useProducts();
  const { isOpen, onOpen, onOpenChange } = useDisclosure();

  const [activeTab, setActiveTab] = useState<
    "basic" | "dimensions" | "components" | "preview"
  >("basic");
  const [isSaving, setIsSaving] = useState(false);

  // Estado del formulario
  const [formState, setFormState] = useState<CompositeFormState>({
    name: "",
    description: "",
    dimensions: { width: 1000, height: 2000 }, // Defaults
    components: [],
    image_url: "",
    properties: {},
  });

  // Simulacion en tiempo real
  const [simulation, setSimulation] =
    useState<SimulateCompositeResponse | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  // Modal de componente
  const [editingComponentIndex, setEditingComponentIndex] = useState<
    number | null
  >(null);

  // Simular product compuesto (debounced)
  useEffect(() => {
    const simulate = async () => {
      if (formState.components.length === 0) {
        setSimulation(null);
        return;
      }

      setIsSimulating(true);
      try {
        const payload: CreateCompositeProductPayload = {
          name: formState.name || "Unnamed product",
          description: formState.description,
          dimensions: formState.dimensions,
          components: formState.components.map((c) => ({
            product_id: c.product_id,
            base_quantity: c.base_quantity,
            relationship: c.relationship,
          })),
          image_url: formState.image_url,
          properties: formState.properties,
        };

        const res = await apiClient.post<SimulateCompositeResponse>(
          "/products/composite/simulate",
          payload,
        );
        setSimulation(res);
      } catch (err) {
        console.error("Error en simulacion:", err);
        setSimulation(null);
      } finally {
        setIsSimulating(false);
      }
    };

    const timer = setTimeout(simulate, 500); // Debounce 500ms
    return () => clearTimeout(timer);
  }, [formState]);

  // Submit final
  const handleSubmit = async () => {
    if (!formState.name.trim()) {
      onError("El nombre del product es obligatorio");
      return;
    }

    if (formState.components.length === 0) {
      onError("Debe agregar al menos un componente");
      return;
    }

    setIsSaving(true);
    try {
      const payload: CreateCompositeProductPayload = {
        name: formState.name,
        description: formState.description,
        dimensions: formState.dimensions,
        components: formState.components.map((c) => ({
          product_id: c.product_id,
          base_quantity: c.base_quantity,
          relationship: c.relationship,
        })),
        image_url: formState.image_url,
        properties: formState.properties,
      };

      await apiClient.post("/products/composite", payload);
      await fetchProducts(); // Invalidar cache
      onSuccess("Product compuesto creado exitosamente");

      // Reset
      setFormState({
        name: "",
        description: "",
        dimensions: { width: 1000, height: 2000 },
        components: [],
        image_url: "",
        properties: {},
      });
      setActiveTab("basic");
      setSimulation(null);
    } catch (err: unknown) {
      const error = err as {
        response?: { data?: { detail?: string } };
        message?: string;
      };
      onError(
        error.response?.data?.detail ||
          error.message ||
          "Error al create product compuesto",
      );
    } finally {
      setIsSaving(false);
    }
  };

  // Agregar componente
  const handleAddComponent = useCallback(
    (component: CompositeComponentForm) => {
      if (editingComponentIndex !== null) {
        // Modo edicion
        const updated = [...formState.components];
        updated[editingComponentIndex] = component;
        setFormState({ ...formState, components: updated });
        setEditingComponentIndex(null);
      } else {
        // Modo agregar
        setFormState({
          ...formState,
          components: [...formState.components, component],
        });
      }
    },
    [formState, editingComponentIndex],
  );

  // Remover componente
  const handleRemoveComponent = useCallback(
    (index: number) => {
      setFormState({
        ...formState,
        components: formState.components.filter((_, i) => i !== index),
      });
    },
    [formState],
  );

  // Edit componente
  const handleEditComponent = useCallback(
    (index: number) => {
      setEditingComponentIndex(index);
      onOpen();
    },
    [onOpen],
  );

  // Products excluidos (ya agregados)
  const excludedProductIds = formState.components.map((c) => c.product_id);

  return (
    <div className="flex flex-col h-full animate-in fade-in duration-500">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold">Create Composite Product</h3>
          </div>
        </CardHeader>
        <CardBody>
          <Tabs
            selectedKey={activeTab}
            onSelectionChange={(key: React.Key) =>
              setActiveTab(
                key as "basic" | "dimensions" | "components" | "preview",
              )
            }
            variant="underlined"
            color="primary"
            classNames={{
              tabList:
                "gap-6 w-full relative rounded-none border-b border-divider p-0",
              cursor: "w-full bg-primary",
              tab: "max-w-fit px-0 h-12",
              tabContent:
                "group-data-[selected=true]:text-primary font-bold text-xs uppercase tracking-widest",
            }}
          >
            {/* Tab 1: Identificacion */}
            <Tab
              key="basic"
              title={
                <div className="flex items-center space-x-2">
                  <Package className="w-4 h-4" />
                  <span>1. Identificacion</span>
                </div>
              }
            >
              <div className="pt-6 space-y-6 max-w-4xl mx-auto">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <Input
                      label="Nombre del Product"
                      labelPlacement="outside"
                      placeholder="Ej: Puerta Principal 2m x 1m"
                      value={formState.name}
                      onValueChange={(val: string) =>
                        setFormState({ ...formState, name: val })
                      }
                      variant="bordered"
                      isRequired
                      classNames={{
                        label:
                          "text-[10px] font-bold uppercase tracking-wider text-default-400",
                        inputWrapper: "rounded-xl",
                      }}
                    />

                    <Textarea
                      label="Description"
                      labelPlacement="outside"
                      placeholder="Ej: Puerta metalica con marco, perfiles y cerradura"
                      value={formState.description}
                      onValueChange={(val: string) =>
                        setFormState({ ...formState, description: val })
                      }
                      variant="bordered"
                      isRequired
                      classNames={{
                        label:
                          "text-[10px] font-bold uppercase tracking-wider text-default-400",
                        inputWrapper: "rounded-xl",
                      }}
                    />
                  </div>

                  <div className="space-y-3">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-default-400 flex items-center gap-2">
                      <ImageIcon className="w-3.5 h-3.5" /> Imagen
                    </span>
                    <ImageUpload
                      value={formState.image_url || ""}
                      onChange={(url: string) =>
                        setFormState({ ...formState, image_url: url })
                      }
                      label=""
                      folder="products"
                    />
                  </div>
                </div>
              </div>
            </Tab>

            {/* Tab 2: Dimensiones */}
            <Tab
              key="dimensions"
              title={
                <div className="flex items-center space-x-2">
                  <Ruler className="w-4 h-4" />
                  <span>2. Dimensiones</span>
                </div>
              }
            >
              <div className="pt-6 space-y-6 max-w-4xl mx-auto">
                <div className="p-6 rounded-2xl bg-default-50 border border-default-200">
                  <h4 className="text-sm font-bold text-foreground mb-4">
                    Dimensiones del Product Compuesto
                  </h4>
                  <p className="text-xs text-default-500 mb-6">
                    Estas dimensiones se usaran como referencia para calcular
                    los componentes que dependen del tamano del product padre.
                  </p>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Input
                      type="number"
                      label="Ancho (mm)"
                      labelPlacement="outside"
                      placeholder="1000"
                      value={formState.dimensions.width.toString()}
                      onValueChange={(val: string) =>
                        setFormState({
                          ...formState,
                          dimensions: {
                            ...formState.dimensions,
                            width: parseFloat(val) || 0,
                          },
                        })
                      }
                      min="0"
                      step="1"
                      isRequired
                      variant="bordered"
                      classNames={{
                        label:
                          "text-[10px] font-bold uppercase tracking-wider text-default-400",
                        inputWrapper: "rounded-xl",
                      }}
                    />

                    <Input
                      type="number"
                      label="Alto (mm)"
                      labelPlacement="outside"
                      placeholder="2000"
                      value={formState.dimensions.height.toString()}
                      onValueChange={(val: string) =>
                        setFormState({
                          ...formState,
                          dimensions: {
                            ...formState.dimensions,
                            height: parseFloat(val) || 0,
                          },
                        })
                      }
                      min="0"
                      step="1"
                      isRequired
                      variant="bordered"
                      classNames={{
                        label:
                          "text-[10px] font-bold uppercase tracking-wider text-default-400",
                        inputWrapper: "rounded-xl",
                      }}
                    />

                    <Input
                      type="number"
                      label="Profundidad (mm) - Opcional"
                      labelPlacement="outside"
                      placeholder="50"
                      value={formState.dimensions.depth?.toString() || ""}
                      onValueChange={(val: string) =>
                        setFormState({
                          ...formState,
                          dimensions: {
                            ...formState.dimensions,
                            depth: val ? parseFloat(val) : undefined,
                          },
                        })
                      }
                      min="0"
                      step="1"
                      variant="bordered"
                      classNames={{
                        label:
                          "text-[10px] font-bold uppercase tracking-wider text-default-400",
                        inputWrapper: "rounded-xl",
                      }}
                    />
                  </div>
                </div>
              </div>
            </Tab>

            {/* Tab 3: Componentes */}
            <Tab
              key="components"
              title={
                <div className="flex items-center space-x-2">
                  <Settings className="w-4 h-4" />
                  <span>3. Componentes</span>
                </div>
              }
            >
              <div className="pt-6 space-y-6">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-bold text-foreground">
                    Constructor de Componentes
                  </h4>
                  <Button
                    color="primary"
                    variant="solid"
                    onPress={() => {
                      setEditingComponentIndex(null);
                      onOpen();
                    }}
                    startContent={<Plus className="w-4 h-4" />}
                    className="font-bold"
                  >
                    Agregar Componente
                  </Button>
                </div>

                <ComponentsHierarchyTree
                  components={formState.components}
                  calculatedComponents={simulation?.components}
                  onRemoveComponent={handleRemoveComponent}
                  onEditComponent={handleEditComponent}
                  showActions={true}
                  showPrices={true}
                />
              </div>
            </Tab>

            {/* Tab 4: Preview */}
            <Tab
              key="preview"
              title={
                <div className="flex items-center space-x-2">
                  <Eye className="w-4 h-4" />
                  <span>4. Preview</span>
                </div>
              }
              isDisabled={formState.components.length === 0}
            >
              <div className="pt-6">
                <CompositeProductPreview
                  simulation={simulation}
                  isSimulating={isSimulating}
                  components={formState.components}
                />
              </div>
            </Tab>
          </Tabs>

          <Divider className="my-6" />

          {/* Footer con navegacion */}
          <div className="flex justify-between items-center">
            <div className="text-[9px] text-default-400 font-bold uppercase tracking-widest">
              Paso{" "}
              {activeTab === "basic"
                ? "1"
                : activeTab === "dimensions"
                  ? "2"
                  : activeTab === "components"
                    ? "3"
                    : "4"}{" "}
              de 4
            </div>
            <div className="flex gap-2">
              {activeTab !== "basic" && (
                <Button
                  variant="flat"
                  size="sm"
                  onPress={() => {
                    const tabs: Array<
                      "basic" | "dimensions" | "components" | "preview"
                    > = ["basic", "dimensions", "components", "preview"];
                    const currentIndex = tabs.indexOf(activeTab);
                    if (currentIndex > 0) {
                      setActiveTab(tabs[currentIndex - 1]);
                    }
                  }}
                  className="font-bold"
                >
                  Anterior
                </Button>
              )}
              {activeTab !== "preview" && (
                <Button
                  color="primary"
                  size="sm"
                  onPress={() => {
                    const tabs: Array<
                      "basic" | "dimensions" | "components" | "preview"
                    > = ["basic", "dimensions", "components", "preview"];
                    const currentIndex = tabs.indexOf(activeTab);
                    if (currentIndex < tabs.length - 1) {
                      setActiveTab(tabs[currentIndex + 1]);
                    }
                  }}
                  className="font-bold"
                  isDisabled={
                    (activeTab === "basic" && !formState.name) ||
                    (activeTab === "components" &&
                      formState.components.length === 0)
                  }
                >
                  Siguiente
                </Button>
              )}
              {activeTab === "preview" && (
                <Button
                  color="primary"
                  variant="solid"
                  onPress={handleSubmit}
                  isLoading={isSaving}
                  isDisabled={
                    formState.components.length === 0 || !formState.name
                  }
                  className="font-bold px-6 shadow-lg shadow-primary/20"
                  size="sm"
                  startContent={<Package className="w-4 h-4" />}
                >
                  Create Composite Product
                </Button>
              )}
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Modal de Componente */}
      <ComponentConfigModal
        isOpen={isOpen}
        onOpenChange={onOpenChange}
        onSave={handleAddComponent}
        editingComponent={
          editingComponentIndex !== null
            ? formState.components[editingComponentIndex]
            : undefined
        }
        parentDimensions={formState.dimensions}
        excludeProductIds={excludedProductIds}
      />
    </div>
  );
};
