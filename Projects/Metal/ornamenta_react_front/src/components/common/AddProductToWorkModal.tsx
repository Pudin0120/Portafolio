import React, { useState, useEffect, useCallback } from "react";
import { Plus } from "lucide-react";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  Input,
  Select,
  SelectItem,
  useDisclosure,
} from "@heroui/react";
import { CenteredModal } from "@components/common/CenteredModal";
import { workService, AddProductToWorkRequest } from "@/services/workService";
import { Product } from "@/types/products";
import { apiClient } from "@/services/apiClient";
import { SimpleProductForm } from "@/components/products/SimpleProductForm";

interface AddProductToWorkModalProps {
  workId: string;
  workStatus: string;
  onProductAdded?: () => void;
  onModalStateChange?: (isOpen: boolean) => void;
}

export const AddProductToWorkModal: React.FC<AddProductToWorkModalProps> = ({
  workId,
  workStatus,
  onProductAdded,
  onModalStateChange,
}) => {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const {
    isOpen: isCreateProductOpen,
    onOpen: onCreateProductOpen,
    onOpenChange: onCreateProductOpenChange,
  } = useDisclosure();

  const [portalTarget, setPortalTarget] = useState<HTMLElement | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [searchValue, setSearchValue] = useState("");
  const [formData, setFormData] = useState({
    product_id: "",
    quantity: "" as string | number,
    execution_order: null as number | null,
  });

  const loadProducts = useCallback(async () => {
    try {
      const response = await apiClient.get("/products/?limit=1000");
      const data = response.data || response;
      setProducts(
        Array.isArray(data.products)
          ? data.products
          : Array.isArray(data)
            ? data
            : [],
      );
      setError(null);
    } catch (err) {
      console.error("Error loading products:", err);
      setError("Error al cargar products");
    }
  }, []);

  // Esperar a que exista el contenedor #main-content antes de asignar portalContainer
  useEffect(() => {
    const el = document.getElementById("main-content");
    if (el) setPortalTarget(el);
  }, []);

  useEffect(() => {
    if (isOpen) {
      loadProducts();
    }
  }, [isOpen, loadProducts]);

  useEffect(() => {
    if (onModalStateChange) {
      onModalStateChange(isOpen || isCreateProductOpen);
    }
  }, [isOpen, isCreateProductOpen, onModalStateChange]);

  const isActionAllowed = () => {
    return workStatus === "DRAFT" || workStatus === "QUOTED";
  };

  const handleProductCreatedSuccess = (message: string) => {
    setSuccess(message);
    loadProducts();
    onCreateProductOpenChange();
  };

  const handleProductCreatedError = (message: string) => {
    setError(message);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    if (name === "quantity") {
      const numValue = value === "" ? "" : Math.max(1, parseInt(value) || 1);
      setFormData((prev) => ({
        ...prev,
        quantity: numValue,
      }));
    } else if (name === "execution_order") {
      setFormData((prev) => ({
        ...prev,
        execution_order: value ? parseInt(value) : null,
      }));
    }
  };

  const handleSelectChange = (keys: any) => {
    let selectedId = "";

    if (keys) {
      if (typeof keys === "string") {
        selectedId = keys;
      } else if (keys instanceof Set) {
        const firstValue = Array.from(keys as Set<string>)[0];
        selectedId = firstValue || "";
      } else if (typeof keys[Symbol.iterator] === "function") {
        const firstValue = Array.from(keys as any)[0];
        selectedId = String(firstValue || "");
      } else if (typeof keys === "object" && keys.target) {
        selectedId = keys.target.value || "";
      }
    }

    setFormData((prev) => ({
      ...prev,
      product_id: selectedId,
    }));
  };

  const filteredProducts = products.filter((product) => {
    if (formData.product_id === product.id) return true;
    return (
      product.name?.toLowerCase().includes(searchValue.toLowerCase()) ||
      product.description?.toLowerCase().includes(searchValue.toLowerCase())
    );
  });

  const handleSubmit = async () => {
    setError(null);

    if (!formData.product_id) {
      setError("Debe seleccionar un product");
      return;
    }

    const finalQuantity =
      formData.quantity === "" ? 1 : parseInt(String(formData.quantity));

    if (finalQuantity < 1) {
      setError("La quantity debe ser mayor a 0");
      return;
    }

    try {
      setIsLoading(true);

      const payload: AddProductToWorkRequest = {
        product_id: formData.product_id,
        quantity: finalQuantity,
      };

      if (formData.execution_order !== null) {
        payload.execution_order = formData.execution_order;
      }

      await workService.addProductToWork(workId, payload);
      await workService.getWorkById(workId);

      setSuccess("Product agregado exitosamente!");
      onProductAdded?.();

      setFormData({
        product_id: "",
        quantity: "",
        execution_order: null,
      });

      setTimeout(() => {
        setError(null);
        setSuccess(null);
        onOpenChange();
      }, 1500);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Error al agregar product";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Button
        onPress={onOpen}
        color="primary"
        size="sm"
        isDisabled={!isActionAllowed()}
        title={
          !isActionAllowed() ? `No se permite en estado ${workStatus}` : ""
        }
      >
        + Agregar Product
      </Button>

      {/* Modal principal */}
      {portalTarget && (
        <CenteredModal
          isOpen={isOpen}
          onOpenChange={onOpenChange}
          size="2xl"
          backdrop="blur"
          portalContainer={portalTarget}
        >
          {(onClose: () => void) => (
            <>
              <ModalHeader className="flex flex-col gap-1">
                Agregar Product a Quotation
              </ModalHeader>

              <ModalBody className="gap-4">
                {error && (
                  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    {error}
                  </div>
                )}

                {success && (
                  <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
                    {success}
                  </div>
                )}

                <Input
                  label="Search product"
                  placeholder="Escribe el nombre o description..."
                  value={searchValue}
                  onValueChange={setSearchValue}
                  isDisabled={isLoading}
                  isClearable
                  onClear={() => setSearchValue("")}
                />

                <div className="flex gap-2 items-end">
                  <div className="flex-1">
                    <Select
                      label="Product"
                      selectedKeys={
                        formData.product_id
                          ? new Set([formData.product_id])
                          : new Set()
                      }
                      onChange={handleSelectChange}
                      isDisabled={isLoading || filteredProducts.length === 0}
                      placeholder="Selecciona un product"
                      className="w-full"
                    >
                      {filteredProducts.map((product) => (
                        <SelectItem key={product.id} textValue={product.name}>
                          {product.name} - ${product.price || 0}
                        </SelectItem>
                      ))}
                    </Select>
                  </div>
                  <Button
                    isIconOnly
                    color="warning"
                    variant="solid"
                    size="lg"
                    onPress={onCreateProductOpen}
                    isDisabled={isLoading}
                    title="Create nuevo product"
                  >
                    <Plus className="w-5 h-5" />
                  </Button>
                </div>

                <Input
                  label="Quantity"
                  name="quantity"
                  type="number"
                  value={formData.quantity.toString()}
                  onChange={handleInputChange}
                  placeholder="1"
                  min="1"
                  isDisabled={isLoading}
                  isRequired
                />

                {formData.product_id && (
                  <div className="bg-warning-50 border border-warning-200 p-3 rounded-lg">
                    {(() => {
                      const product = products.find(
                        (p) => p.id === formData.product_id,
                      );
                      const unitPrice = Number(product?.price ?? 0) || 0;
                      const quantity =
                        formData.quantity === ""
                          ? 1
                          : parseInt(String(formData.quantity));
                      const totalPrice = unitPrice * quantity;
                      return (
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-700">
                              Price unitario:
                            </span>
                            <span className="font-semibold">
                              $
                              {unitPrice.toLocaleString("es-ES", {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2,
                              })}
                            </span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-700">Quantity:</span>
                            <span className="font-semibold">{quantity}</span>
                          </div>
                          <div className="border-t border-warning-200 pt-2 flex justify-between">
                            <span className="font-semibold text-gray-800">
                              Total:
                            </span>
                            <span className="font-bold text-lg text-warning-600">
                              $
                              {totalPrice.toLocaleString("es-ES", {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2,
                              })}
                            </span>
                          </div>
                        </div>
                      );
                    })()}
                  </div>
                )}

                <Input
                  label="Orden de Ejecucion (Opcional)"
                  name="execution_order"
                  type="number"
                  placeholder="Dejar vacio para agregar al final"
                  isDisabled={isLoading}
                />

                {workStatus === "QUOTED" && (
                  <div className="bg-warning-100 border border-warning-400 text-warning-700 px-4 py-3 rounded">
                     El price se congelara inmediatamente al agregar este
                    product
                  </div>
                )}
              </ModalBody>

              <ModalFooter>
                <Button
                  color="danger"
                  variant="light"
                  onPress={onClose}
                  isDisabled={isLoading}
                >
                  Cancel
                </Button>
                <Button
                  color="primary"
                  onPress={handleSubmit}
                  isLoading={isLoading}
                >
                  Agregar Product
                </Button>
              </ModalFooter>
            </>
          )}
        </CenteredModal>
      )}

      {/* Modal de creation de product */}
      {portalTarget && (
        <CenteredModal
          isOpen={isCreateProductOpen}
          onOpenChange={onCreateProductOpenChange}
          size="lg"
          scrollBehavior="inside"
          backdrop="blur"
          portalContainer={portalTarget}
          classNames={{
            wrapper: "z-[2000] flex items-center justify-center",
            base: "max-w-3xl",
            backdrop: "z-[1999] bg-black/40 backdrop-blur-md",
          }}
        >
          {(onClose: () => void) => (
            <>
              <ModalHeader className="flex flex-col gap-1">
                <h3 className="text-xl font-bold">Create Nuevo Product</h3>
                <p className="text-sm font-normal text-default-500">
                  El product se agregara automaticamente a la lista de
                  disponibles.
                </p>
              </ModalHeader>
              <ModalBody>
                <SimpleProductForm
                  onSuccess={handleProductCreatedSuccess}
                  onError={handleProductCreatedError}
                />
              </ModalBody>
            </>
          )}
        </CenteredModal>
      )}
    </>
  );
};

export default AddProductToWorkModal;
