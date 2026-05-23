import React, { useState, useEffect, useMemo, useCallback } from "react";
import { apiClient } from "@services/apiClient";
import {
  Input,
  Button,
  Card,
  CardBody,
  Divider,
  Switch,
  Image,
  Tabs,
  Tab,
  useDisclosure,
  ModalHeader,
  ModalBody,
  ModalFooter,
} from "@heroui/react";
import {
  Eye,
  Package,
  Settings2,
  Image as ImageIcon,
  Calculator,
  CheckCircle2,
  AlertCircle,
  Undo2,
} from "lucide-react";
import {
  BaseProductCreationProps,
  CreateSimpleProductPayload,
  SimulateSimpleProductResponse,
} from "@/types/product-creation";
import {
  MaterialRecipeEditor,
  MaterialRequirement,
} from "./MaterialRecipeEditor";
import { ImageUpload } from "@components/common/ImageUpload";
import { BarcodeInput } from "@components/common/BarcodeInput";
import { LocalMediaImage } from "@components/common/LocalMediaImage";
import { useProducts } from "@context/ProductsContext";
import { buildDimensionsPayload } from "./product-creation";
import { CenteredModal } from "@components/common/CenteredModal";

export const SimpleProductForm: React.FC<BaseProductCreationProps> = ({
  onSuccess,
  onError,
}) => {
  const { fetchProducts } = useProducts();
  const { isOpen, onOpen, onOpenChange, onClose } = useDisclosure();

  const [isSaving, setIsSaving] = useState(false);
  // --- Estado del formulario ---
  const [name, setName] = useState("");
  const [recipeMaterials, setRecipeMaterials] = useState<MaterialRequirement[]>(
    [],
  );
  const [imageUrl, setImageUrl] = useState("");
  const [barcode, setBarcode] = useState("");
  const [purchasePriceOverride, setPurchasePriceOverride] =
    useState<string>("");
  const [salePriceOverride, setSalePriceOverride] = useState<string>("");
  const [isService, setIsService] = useState(false);
  const [simulation, setSimulation] =
    useState<SimulateSimpleProductResponse | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  // --- Callbacks estables ---
  const handleRecipeChange = useCallback((materials: MaterialRequirement[]) => {
    setRecipeMaterials(materials);
    if (materials.length > 0) {
      setIsService(false);
    }
  }, []);

  // --- Efectos ---

  // Simulacion en tiempo real
  useEffect(() => {
    const simulate = async () => {
      // Solo simular si hay materials
      if (recipeMaterials.length === 0 || isService) {
        setSimulation(null);
        return;
      }

      setIsSimulating(true);
      try {
        const payload = {
          name: name.trim() || undefined,
          materials: recipeMaterials.map((m) => ({
            material_id: m.material.id,
            quantity: m.quantity,
            dimensions: m.dimensions
              ? buildDimensionsPayload(m.dimensions, m.material)
              : undefined,
          })),
        };

        const res = await apiClient.post<SimulateSimpleProductResponse>(
          "/products/simple/simulate",
          payload,
        );
        setSimulation(res);
      } catch {
        setSimulation(null);
      } finally {
        setIsSimulating(false);
      }
    };

    const timer = setTimeout(simulate, 500); // Debounce
    return () => clearTimeout(timer);
  }, [recipeMaterials, name, isService]);

  const [activeTab, setActiveTab] = useState("definition");

  const handleSubmit = async () => {
    if (!isService && recipeMaterials.length === 0) {
      onError("Debe agregar al menos un material");
      return;
    }

    if (isService && (!purchasePriceOverride || !salePriceOverride || !name)) {
      onError("Para servicios, el nombre y los precios son obligatorios");
      return;
    }

    setIsSaving(true);
    try {
      const productData: CreateSimpleProductPayload = {
        name: name.trim() || undefined,
        materials: recipeMaterials.map((m) => ({
          material_id: m.material.id,
          quantity: m.quantity,
          dimensions: m.dimensions
            ? buildDimensionsPayload(m.dimensions, m.material)
            : undefined,
        })),
        image_url: imageUrl || undefined,
        properties: barcode ? { barcode } : undefined,
        purchase_price_override: isService
          ? parseFloat(purchasePriceOverride)
          : undefined,
        sale_price_override: isService
          ? parseFloat(salePriceOverride)
          : undefined,
      };

      await apiClient.post("/products/simple", productData);
      await fetchProducts();
      onSuccess("Product creado exitosamente");

      // Reset
      setName("");
      setRecipeMaterials([]);
      setImageUrl("");
      setBarcode("");
      setPurchasePriceOverride("");
      setSalePriceOverride("");
      setIsService(false);
      onClose();
      setActiveTab("definition");
    } catch (err: unknown) {
      const message =
        typeof err === "object" &&
        err !== null &&
        "response" in err &&
        typeof (err as { response?: unknown }).response === "object"
          ? (((err as { response?: { data?: { detail?: unknown } } }).response
              ?.data?.detail as string | undefined) ??
            (err instanceof Error ? err.message : undefined))
          : err instanceof Error
            ? err.message
            : undefined;

      onError(message || "Error al create product");
    } finally {
      setIsSaving(false);
    }
  };

  const finalProductName = useMemo(() => {
    return (
      name ||
      (recipeMaterials.length > 0
        ? `Product de ${recipeMaterials[0].material.name}`
        : "Sin nombre")
    );
  }, [name, recipeMaterials]);

  const getDimensionDisplayValue = (
    value:
      | string
      | number
      | {
          value: string | number;
          unit?: string;
        }
      | undefined,
  ) => {
    if (value === undefined) {
      return "";
    }

    return typeof value === "object" ? value.value : value;
  };

  return (
    <div className="flex flex-col h-full animate-in fade-in duration-500">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          onOpen();
        }}
        className="flex flex-col h-full overflow-hidden"
      >
        <div className="flex flex-col flex-1 min-h-0 overflow-hidden pb-4">
          <Tabs
            selectedKey={activeTab}
            onSelectionChange={(key: React.Key) => setActiveTab(key.toString())}
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
            <Tab
              key="definition"
              title={
                <div className="flex items-center space-x-2">
                  <Package className="w-4 h-4" />
                  <span>1. Identificacion</span>
                </div>
              }
            >
              <div className="custom-scrollbar min-h-[45dvh] max-h-[calc(100dvh-260px)] overflow-y-auto pt-6 pr-2">
                <div className="space-y-6 max-w-4xl mx-auto w-full pb-20">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-6">
                      <div className="flex items-center justify-between bg-content2/50 p-4 rounded-2xl border border-default-100 shadow-sm">
                        <div className="flex flex-col">
                          <span className="text-xs font-bold text-foreground">
                            Product de Servicio?
                          </span>
                          <span className="text-[10px] text-default-500">
                            Sin materials fisicos, solo intangibles
                          </span>
                        </div>
                        <Switch
                          isSelected={isService}
                          onValueChange={(val: boolean) => {
                            setIsService(val);
                            if (val) setRecipeMaterials([]);
                          }}
                          size="md"
                          aria-label="Product de Servicio?"
                        />
                      </div>

                      <Input
                        label="Nombre del Product"
                        labelPlacement="outside"
                        placeholder={
                          isService
                            ? "Nombre del servicio..."
                            : "Opcional: Nombre personalizado"
                        }
                        value={name}
                        onValueChange={setName}
                        variant="bordered"
                        size="md"
                        isRequired={isService}
                        classNames={{
                          label:
                            "text-[10px] font-bold uppercase tracking-wider text-default-400",
                          inputWrapper: "rounded-xl",
                        }}
                      />

                      <BarcodeInput
                        label="Codigo de Barras / QR"
                        labelPlacement="outside"
                        placeholder="Opcional"
                        value={barcode}
                        onValueChange={setBarcode}
                        variant="bordered"
                        size="md"
                        classNames={{
                          label:
                            "text-[10px] font-bold uppercase tracking-wider text-default-400",
                          inputWrapper: "rounded-xl",
                        }}
                      />

                      {isService && (
                        <div className="grid grid-cols-1 gap-4 rounded-2xl border border-warning-100 bg-warning-50/30 p-4 animate-in slide-in-from-top-2 sm:grid-cols-2">
                          <Input
                            type="number"
                            label="Price Compra"
                            placeholder="0.00"
                            value={purchasePriceOverride}
                            onValueChange={setPurchasePriceOverride}
                            startContent={
                              <span className="text-default-400">$</span>
                            }
                            variant="flat"
                            size="sm"
                          />
                          <Input
                            type="number"
                            label="Price Venta"
                            placeholder="0.00"
                            value={salePriceOverride}
                            onValueChange={setSalePriceOverride}
                            startContent={
                              <span className="text-default-400">$</span>
                            }
                            variant="flat"
                            size="sm"
                          />
                        </div>
                      )}
                    </div>

                    <div className="space-y-3">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-default-400 flex items-center gap-2">
                        <ImageIcon className="w-3.5 h-3.5" /> Imagen
                      </span>
                      <ImageUpload
                        value={imageUrl}
                        onChange={setImageUrl}
                        label=""
                        folder="products"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </Tab>

            <Tab
              key="recipe"
              title={
                <div className="flex items-center space-x-2">
                  <Calculator className="w-4 h-4" />
                  <span>2. Receta & Simulacion</span>
                </div>
              }
              isDisabled={isService}
            >
              <div className="custom-scrollbar min-h-[45dvh] max-h-[calc(100dvh-260px)] overflow-y-auto pt-6 pr-2">
                <div className="space-y-6 max-w-4xl mx-auto w-full pb-20">
                  <div className="bg-default-50/50 p-1 rounded-3xl border border-default-100">
                    <MaterialRecipeEditor
                      materials={recipeMaterials}
                      onMaterialsChange={handleRecipeChange}
                    />
                  </div>

                  {/* Panel de Simulacion Integrado */}
                  {simulation && (
                    <Card className="border-none bg-primary/5 shadow-none border-t-4 border-primary animate-in fade-in slide-in-from-bottom-4">
                      <CardBody className="p-4">
                        <div className="flex flex-wrap items-center justify-between gap-4">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-primary/10 rounded-xl">
                              <Calculator className="w-5 h-5 text-primary" />
                            </div>
                            <div>
                              <p className="text-[10px] font-bold text-primary uppercase tracking-widest">
                                Calculo del Product Final
                              </p>
                              <p className="text-sm font-bold text-foreground">
                                {simulation.name}
                              </p>
                            </div>
                          </div>

                          <div className="flex gap-6">
                            <div>
                              <p className="text-[9px] font-bold text-default-400 uppercase">
                                Costo Total
                              </p>
                              <p className="text-lg font-black text-warning-600">
                                {simulation.purchase_price}
                              </p>
                            </div>
                            <div>
                              <p className="text-[9px] font-bold text-default-400 uppercase">
                                Price Venta
                              </p>
                              <p className="text-lg font-black text-success-600">
                                {simulation.sale_price}
                              </p>
                            </div>
                          </div>
                        </div>
                        <div className="mt-2 pt-2 border-t border-primary/10">
                          <p className="text-[10px] text-default-500 italic">
                            {simulation.description}
                          </p>
                        </div>
                      </CardBody>
                    </Card>
                  )}

                  {isSimulating && (
                    <div className="flex items-center justify-center gap-2 py-4 text-primary animate-pulse">
                      <Calculator className="w-4 h-4" />
                      <span className="text-xs font-bold uppercase tracking-widest">
                        Calculando product final...
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </Tab>
          </Tabs>
        </div>

        {/* Footer Reducido */}
        <div className="sticky bottom-0 z-30 flex flex-col gap-3 border-t border-divider bg-background/80 px-4 py-3 backdrop-blur-sm sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div className="text-[9px] font-bold uppercase tracking-widest text-default-400">
            {isService
              ? "Servicio"
              : `Paso ${activeTab === "definition" ? "1" : "2"} de 2`}
          </div>
          <div className="flex flex-col gap-2 sm:flex-row">
            {activeTab === "recipe" && (
              <Button
                variant="flat"
                size="sm"
                onPress={() => setActiveTab("definition")}
                className="w-full font-bold sm:w-auto"
              >
                Anterior
              </Button>
            )}
            {activeTab === "definition" && !isService && (
              <Button
                color="primary"
                size="sm"
                onPress={() => setActiveTab("recipe")}
                className="w-full font-bold sm:w-auto"
                isDisabled={recipeMaterials.length === 0}
              >
                Siguiente
              </Button>
            )}
            {(isService || activeTab === "recipe") && (
              <Button
                color="primary"
                variant="solid"
                type="submit"
                isLoading={isSaving}
                isDisabled={
                  (recipeMaterials.length === 0 && !isService) ||
                  (isService && (!name || !purchasePriceOverride))
                }
                className="w-full px-6 font-bold shadow-lg shadow-primary/20 sm:w-auto"
                size="sm"
                startContent={<Eye className="w-4 h-4" />}
              >
                Confirmar
              </Button>
            )}
          </div>
        </div>
      </form>

      {/* Modal de Resumen y Confirmacion Final */}
      <CenteredModal
        isOpen={isOpen}
        onOpenChange={onOpenChange}
        size="4xl"
        backdrop="blur"
        scrollBehavior="inside"
      >
        {(onCloseModal) => (
          <>
            <ModalHeader className="border-b border-divider py-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary/10 rounded-xl">
                  <CheckCircle2 className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h3 className="text-lg font-bold">Resumen del Product</h3>
                  <p className="text-xs text-default-500 font-normal">
                    Verifica que todo este correcto antes de create
                  </p>
                </div>
              </div>
            </ModalHeader>
            <ModalBody className="py-6 space-y-8">
              <div className="flex flex-col md:flex-row gap-8">
                {/* Visual Section */}
                <div className="w-full md:w-1/3 space-y-4">
                  <div className="aspect-square rounded-3xl bg-default-50 border-2 border-dashed border-default-200 overflow-hidden flex items-center justify-center shadow-inner group transition-all hover:border-primary/30">
                    {imageUrl ? (
                      <LocalMediaImage
                        src={imageUrl}
                        alt="Preview"
                        className="w-full h-full object-contain p-4 transition-transform group-hover:scale-105"
                      />
                    ) : (
                      <div className="flex flex-col items-center gap-3 text-default-300">
                        <ImageIcon className="w-16 h-16 opacity-20" />
                        <span className="text-[10px] font-bold uppercase tracking-widest">
                          Sin imagen
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="p-4 rounded-2xl bg-primary/5 border border-primary/10">
                    <p className="text-[10px] font-bold text-primary uppercase tracking-widest mb-3">
                      Impacto en Precios
                    </p>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-default-500 font-medium">
                          Costo Estimado
                        </span>
                        <span className="text-sm font-bold text-warning-600">
                          {isService
                            ? `$${purchasePriceOverride}`
                            : simulation?.purchase_price || "---"}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-default-500 font-medium">
                          Price de Venta
                        </span>
                        <span className="text-sm font-bold text-success-600">
                          {isService
                            ? `$${salePriceOverride}`
                            : simulation?.sale_price || "---"}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex-1 space-y-8">
                  <section>
                    <p className="text-[10px] font-bold uppercase text-default-400 tracking-widest mb-2">
                      Nombre Comercial
                    </p>
                    <p className="text-2xl font-black text-foreground leading-tight tracking-tight">
                      {simulation?.name || finalProductName}
                    </p>
                    {isService && (
                      <div className="mt-2 inline-flex items-center gap-1.5 px-2 py-0.5 bg-warning-100 text-warning-700 rounded-full text-[10px] font-bold uppercase tracking-wider">
                        <Settings2 className="w-3 h-3" /> Servicio
                      </div>
                    )}
                    {barcode && (
                      <p className="mt-3 inline-block rounded-lg bg-default-100 px-2 py-1 font-mono text-xs text-default-600">
                        {barcode}
                      </p>
                    )}
                  </section>

                  {!isService && recipeMaterials.length > 0 && (
                    <section>
                      <p className="text-[10px] font-bold uppercase text-default-400 tracking-widest mb-4">
                        Estructura del Product (Receta)
                      </p>
                      <div className="grid grid-cols-1 gap-3">
                        {recipeMaterials.map((req, idx) => (
                          <div
                            key={`${req.material.id}-${idx}`}
                            className="p-4 rounded-2xl bg-default-50 border border-default-200 hover:border-primary/20 transition-all shadow-sm group"
                          >
                            <div className="flex justify-between items-start mb-3">
                              <div className="flex items-center gap-2">
                                <div className="flex h-8 w-8 items-center justify-center overflow-hidden rounded-lg border border-surface-border bg-surface-elevated shadow-sm">
                                  {req.material.image_url ||
                                  req.material.properties?.image_url ? (
                                    <Image
                                      src={
                                        req.material.image_url ||
                                        req.material.properties?.image_url
                                      }
                                      alt={req.material.name}
                                      className="w-full h-full object-contain p-0.5"
                                    />
                                  ) : (
                                    <Package className="w-4 h-4 text-default-400 group-hover:text-primary transition-colors" />
                                  )}
                                </div>
                                <span className="text-sm font-bold text-foreground">
                                  {req.material.name}
                                </span>
                              </div>
                              <div className="flex flex-col items-end">
                                <span className="text-[10px] font-black text-primary bg-primary/10 px-2 py-1 rounded-lg uppercase tracking-wider">
                                  Cant: {req.quantity}
                                </span>
                              </div>
                            </div>

                            <div className="flex flex-wrap gap-2">
                              {req.dimensions &&
                                Object.entries(req.dimensions).map(
                                  ([key, val]) => {
                                    if (
                                      key === "mode" ||
                                      key === "unit" ||
                                      !val
                                    )
                                      return null;
                                    return (
                                      <div
                                        key={key}
                                        className="flex min-w-[60px] flex-col rounded-xl border border-surface-border bg-surface-elevated px-2.5 py-1.5 shadow-sm"
                                      >
                                        <span className="text-[8px] font-black text-default-400 uppercase tracking-tighter mb-0.5">
                                          {key.replace("_", " ")}
                                        </span>
                                        <span className="text-xs font-bold text-foreground flex items-baseline gap-1">
                                          {getDimensionDisplayValue(val)}
                                          <span className="text-[9px] text-primary/60 font-black">
                                            {getDimensionDisplayValue(
                                              req.dimensions?.unit,
                                            )}
                                          </span>
                                        </span>
                                      </div>
                                    );
                                  },
                                )}
                              {(!req.dimensions ||
                                Object.keys(req.dimensions).filter(
                                  (k) =>
                                    k !== "unit" &&
                                    k !== "mode" &&
                                    req.dimensions?.[k],
                                ).length === 0) && (
                                <span className="text-[10px] italic text-default-400 px-1">
                                  Sin dimensiones especificas (Venta por unidad)
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </section>
                  )}

                  {simulation?.description && !isService && (
                    <section className="p-4 rounded-2xl bg-default-100/50 border border-default-200">
                      <div className="flex gap-2 text-default-600">
                        <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                        <p className="text-xs leading-relaxed italic">
                          {simulation.description}
                        </p>
                      </div>
                    </section>
                  )}
                </div>
              </div>
            </ModalBody>
            <ModalFooter className="flex flex-col-reverse gap-2 border-t border-divider py-4 sm:flex-row">
              <Button
                color="default"
                variant="flat"
                onPress={onCloseModal}
                size="md"
                className="w-full font-bold sm:w-auto"
                startContent={<Undo2 className="w-4 h-4" />}
              >
                Volver a Edit
              </Button>
              <Button
                color="primary"
                variant="solid"
                onPress={handleSubmit}
                isLoading={isSaving}
                className="h-11 w-full px-10 text-sm font-bold shadow-lg shadow-primary/20 sm:w-auto"
                size="md"
                startContent={<CheckCircle2 className="w-5 h-5" />}
              >
                Confirmar y Create
              </Button>
            </ModalFooter>
          </>
        )}
      </CenteredModal>
    </div>
  );
};
