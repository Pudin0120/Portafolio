import React, { useState, useEffect, useMemo } from "react";
import { Package, Circle, DollarSign, Plus } from "lucide-react";
import { useAuth } from "@hooks/useAuth";
import { formatPrice } from "@/utils";
import { useConnectivity } from "@/providers/ConnectivityProvider";
import { apiClient } from "@services/apiClient";
import {
  Input,
  Textarea,
  Button,
  Card,
  CardBody,
  CardHeader,
  Divider,
  Spinner,
  Chip,
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
} from "@heroui/react";
import { Product, Material, MaterialType, UnitMeasure } from "@/types/products";
import { useProducts } from "@context/ProductsContext";
import { CenteredModal } from "@components/common/CenteredModal";
import { ProductSelector } from "./ProductSelector";
import { ComponentsList, ComponentItem } from "./ComponentsList";
import { SimpleProductForm } from "./SimpleProductForm";
import { HelpTooltip, helpContent } from "@components/HelpTooltip";

type ProductsResponse = {
  products: Product[];
  total: number;
};

type MaterialsResponse = {
  materials: Material[];
  total: number;
};

type MaterialTypesResponse = {
  material_types: MaterialType[];
  total: number;
};

type UnitMeasuresResponse = {
  units: UnitMeasure[];
  total: number;
};

const getNumericPrice = (price: Product["price"]): number => {
  const parsed =
    typeof price === "number" ? price : Number.parseFloat(price ?? "");
  return Number.isFinite(parsed) ? parsed : 0;
};

type CompositeProductFormProps = {
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
};

export const CompositeProductForm: React.FC<CompositeProductFormProps> = ({
  onSuccess,
  onError,
}) => {
  const { isAuthenticated, sessionReady } = useAuth();
  const { fetchProducts } = useProducts();
  const { connectionEpoch } = useConnectivity();
  const [isSaving, setIsSaving] = useState(false);
  const [isLoadingProducts, setIsLoadingProducts] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [showCreateSimpleModal, setShowCreateSimpleModal] = useState(false);

  // Data para SimpleProductForm
  const [materials, setMaterials] = useState<Material[]>([]);
  const [materialTypes, setMaterialTypes] = useState<MaterialType[]>([]);
  const [unitMeasures, setUnitMeasures] = useState<UnitMeasure[]>([]);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [components, setComponents] = useState<ComponentItem[]>([]);
  const [selectedProductId, setSelectedProductId] = useState("");
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [quantity, setQuantity] = useState("1");
  const [simpleProductSuccess, setSimpleProductSuccess] = useState("");
  const [refreshProductsTrigger, setRefreshProductsTrigger] = useState(0);

  // Cargar datos iniciales
  useEffect(() => {
    const fetchData = async () => {
      if (!isAuthenticated && !sessionReady) return;
      setIsLoadingProducts(true);
      try {
        const [productsData, materialsData, materialTypesData, unitMeasuresData] = await Promise.all([
          apiClient.get<ProductsResponse>("/products/"),
          apiClient.get<MaterialsResponse>("/materials/"),
          apiClient.get<MaterialTypesResponse>("/material-types/"),
          apiClient.get<UnitMeasuresResponse>("/unit-measures/"),
        ]);

        if (productsData) {
          setProducts(productsData.products || []);
        }
        if (materialsData) {
          setMaterials(materialsData.materials || []);
        }
        if (materialTypesData) {
          setMaterialTypes(materialTypesData.material_types || []);
        }
        if (unitMeasuresData) {
          setUnitMeasures(unitMeasuresData.units || []);
        }
      } catch (err) {
        console.error("Error al cargar datos:", err);
      } finally {
        setIsLoadingProducts(false);
      }
    };

    fetchData();
  }, [isAuthenticated, sessionReady, connectionEpoch]);

  // Recargar products cuando se crea uno nuevo
  const refreshProducts = async () => {
    if (!isAuthenticated && !sessionReady) return;
    try {
      const data = await apiClient.get<ProductsResponse>("/products/");
      if (data) {
        setProducts(data.products || []);
      }
    } catch (err) {
      console.error("Error al recargar products:", err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isAuthenticated && !sessionReady) {
      console.error("No user logged in or session not ready");
      onError("Debes estar autenticado");
      return;
    }

    if (components.length === 0) {
      console.warn("No components added");
      onError("Debes agregar al menos un componente");
      return;
    }

    setIsSaving(true);
    onError("");

    try {
      const payload = {
        name,
        description,
        components,
      };

      console.log(
        " Creando Product Compuesto:",
        JSON.stringify(payload, null, 2),
      );

      await apiClient.post("/products/composite", payload);

      // Invalidar cache de products para que aparezca en la lista
      await fetchProducts();

      onSuccess("Product compuesto creado exitosamente!");

      // Reset form
      setName("");
      setDescription("");
      setComponents([]);
      setSelectedProductId("");
      setSelectedProduct(null);
      setQuantity("1");
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      console.error("Submit error:", message);
      onError(message);
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddComponent = () => {
    if (!selectedProductId) {
      onError("Please selecciona un product");
      return;
    }

    const qty = parseInt(quantity) || 1;
    if (qty <= 0) {
      onError("La quantity debe ser mayor a 0");
      return;
    }

    // Verificar si el product ya esta en los componentes
    const existingIndex = components.findIndex(
      (c) => c.product_id === selectedProductId,
    );

    if (existingIndex >= 0) {
      // Si ya existe, actualizar la quantity
      const updatedComponents = [...components];
      updatedComponents[existingIndex].quantity += qty;
      setComponents(updatedComponents);
    } else {
      // Si no existe, agregarlo
      setComponents([
        ...components,
        { product_id: selectedProductId, quantity: qty },
      ]);
    }

    // Reset selection
    setSelectedProductId("");
    setSelectedProduct(null);
    setQuantity("1");
    onError("");
  };

  const handleRemoveComponent = (index: number) => {
    setComponents(components.filter((_, i) => i !== index));
  };

  const handleSimpleProductSuccess = (message: string) => {
    setSimpleProductSuccess(message);
    setShowCreateSimpleModal(false);

    // Actualizar trigger para forzar recarga en ProductSelector
    setRefreshProductsTrigger((prev) => prev + 1);

    // Tambien recargar la lista local
    refreshProducts();

    // Limpiar mensaje despues de 5 segundos
    setTimeout(() => setSimpleProductSuccess(""), 5000);
  };

  const handleSimpleProductError = (message: string) => {
    onError(message);
  };

  // Excluir products que ya estan en componentes del selector
  const excludedProductIds = components.map((c) => c.product_id);

  // Calcular price estimado del product seleccionado
  const selectedProductEstimatedPrice = useMemo(() => {
    const price = getNumericPrice(selectedProduct?.price);
    if (!price) return null;
    const qty = parseInt(quantity) || 1;
    return price * qty;
  }, [selectedProduct, quantity]);

  // Calcular price total del product compuesto
  const totalCompositePrice = useMemo(() => {
    return components.reduce((sum, comp) => {
      const product = products.find((p) => p.id === comp.product_id);
      const price = getNumericPrice(product?.price);
      if (!price) return sum;
      return sum + price * comp.quantity;
    }, 0);
  }, [components, products]);

  if (isLoadingProducts) {
    return (
      <Card>
        <CardBody>
          <div className="flex justify-center p-8">
            <Spinner />
          </div>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-semibold">Nuevo Product Compuesto</h3>
          <HelpTooltip content={helpContent.compositeProduct} size="sm" />
        </div>
      </CardHeader>
      <CardBody>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Nombre"
            placeholder="Ej: Porton de Acero Galvanizado Estandar"
            value={name}
            onValueChange={setName}
            isRequired
          />

          <Textarea
            label="Description"
            placeholder="Ej: Porton completo con marco, lamina y pintura"
            value={description}
            onValueChange={setDescription}
            isRequired
          />

          <Divider />

          <div className="flex items-center justify-between">
            <h4 className="font-semibold text-foreground">Componentes</h4>
            <Button
              size="sm"
              color="primary"
              variant="solid"
              onPress={() => setShowCreateSimpleModal(true)}
              startContent={<Plus className="w-4 h-4" />}
              className="font-semibold"
            >
              Create Simple Product
            </Button>
          </div>

          {simpleProductSuccess && (
            <div className="rounded-md bg-success-50 p-3 text-sm text-success">
              {simpleProductSuccess}
            </div>
          )}

          <div className="space-y-3 rounded-lg border border-divider bg-default-50 p-4">
            <ProductSelector
              selectedProductId={selectedProductId}
              onProductChange={setSelectedProductId}
              onProductSelect={setSelectedProduct}
              excludeProductIds={excludedProductIds}
              label="Seleccionar Product"
              placeholder="Busca y selecciona un product"
              refreshTrigger={refreshProductsTrigger}
            />

            <div className="flex gap-2">
              <Input
                type="number"
                label="Quantity"
                placeholder="1"
                value={quantity}
                onValueChange={setQuantity}
                min="1"
                className="max-w-[150px]"
              />

              <Button
                color="primary"
                variant="solid"
                onPress={handleAddComponent}
                className="mt-auto font-semibold"
                isDisabled={!selectedProductId}
                startContent={<Plus className="w-4 h-4" />}
              >
                Agregar Componente
              </Button>
            </div>

            {selectedProduct && (
              <Card className="bg-default-100 border border-divider">
                <CardBody className="p-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 space-y-1">
                      <p className="font-semibold text-foreground">
                        {selectedProduct.name}
                      </p>
                      <div className="flex items-center gap-2 text-xs text-default-600">
                        <span className="flex items-center gap-1">
                          {selectedProduct.product_type === "simple" ? (
                            <Circle className="w-3 h-3" />
                          ) : (
                            <Package className="w-3 h-3" />
                          )}
                          {selectedProduct.product_type === "simple"
                            ? "Product Simple"
                            : "Product Compuesto"}
                        </span>
                        {selectedProduct.material_name && (
                          <>
                            <span></span>
                            <span className="flex items-center gap-1">
                              <Package className="w-3 h-3" />{" "}
                              {selectedProduct.material_name}
                            </span>
                          </>
                        )}
                      </div>
                      <p className="text-xs text-default-500">
                        {selectedProduct.description}
                      </p>
                    </div>
                    <div className="text-right space-y-1">
                      {getNumericPrice(selectedProduct.price) > 0 ? (
                        <>
                          <Chip color="success" variant="flat" size="sm">
                            $
                            {formatPrice(
                              getNumericPrice(selectedProduct.price),
                            )}{" "}
                            {selectedProduct.currency || "COP"}
                          </Chip>
                          {selectedProductEstimatedPrice &&
                            parseInt(quantity) > 1 && (
                              <p className="text-xs font-semibold text-success">
                                Total: $
                                {formatPrice(selectedProductEstimatedPrice)}{" "}
                                {selectedProduct.currency || "COP"}
                              </p>
                            )}
                        </>
                      ) : (
                        <Chip color="default" variant="flat" size="sm">
                          Sin price
                        </Chip>
                      )}
                    </div>
                  </div>
                </CardBody>
              </Card>
            )}
          </div>

          {components.length > 0 && (
            <>
              <Divider />

              <div className="space-y-3">
                <ComponentsList
                  components={components}
                  products={products}
                  onRemoveComponent={handleRemoveComponent}
                  showPrices={true}
                />
              </div>
            </>
          )}

          {components.length === 0 && (
            <Card className="bg-default-50">
              <CardBody className="p-4">
                <p className="text-center text-sm text-default-500">
                  No hay componentes agregados. Busca y agrega products para
                  construir tu product compuesto.
                </p>
              </CardBody>
            </Card>
          )}

          <Divider />

          <div className="flex justify-end">
            <Button
              color="primary"
              variant="solid"
              type="submit"
              isLoading={isSaving}
              isDisabled={components.length === 0}
              className="font-semibold"
            >
              Create Composite Product
            </Button>
          </div>
        </form>
      </CardBody>

      {/* Modal para create product simple */}
      <CenteredModal
        isOpen={showCreateSimpleModal}
        onOpenChange={setShowCreateSimpleModal}
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
                El product se agregara automaticamente a la lista y podras
                seleccionarlo despues.
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
    </Card>
  );
};
