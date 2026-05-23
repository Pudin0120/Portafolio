import React, { useState, useMemo } from "react";
import { Plus, ChevronDown, ChevronUp, CircleCheck, Eye } from "lucide-react";
import {
  Input,
  Button,
  Spinner,
  Autocomplete,
  AutocompleteItem,
  Divider,
  Card,
  CardBody,
} from "@heroui/react";
import { Search, X } from "lucide-react";
import { formatCurrency } from "@/utils";
import { CreateMaterialTypeModal } from "./CreateMaterialTypeModal";
import { CreateCompositionModal } from "./CreateCompositionModal";
import { CommonMaterialFields } from "./material-creation/CommonMaterialFields";
import {
  StrategyProperties,
  shouldShowProperty as shouldShowPropertyUtil,
  useMaterialForm,
} from "./material-creation";
import { StrategyIcon } from "./material-creation/StrategyIcon";
import {
  isCompositionCompatible,
  getMaterialStrategy,
} from "./material-creation/strategies/registry";

import { PropertyConfig } from "@/types/material-creation";
import { Material, MaterialType, Composition } from "@/types/products";
import { BarcodeInput } from "@components/common/BarcodeInput";
import { LocalMediaImage } from "@components/common/LocalMediaImage";
import { useConnectivity } from "@/providers/ConnectivityProvider";

type CreateMaterialProps = {
  onSuccess: () => void;
  onCancel: () => void;
  cloneFrom?: Material;
};

export const CreateMaterial: React.FC<CreateMaterialProps> = ({
  onSuccess,
  onCancel,
  cloneFrom,
}) => {
  // Modal states
  const [showCreateMaterialTypeModal, setShowCreateMaterialTypeModal] =
    useState(false);
  const [showCreateCompositionModal, setShowCreateCompositionModal] =
    useState(false);
  const [showOptionalIdentity, setShowOptionalIdentity] = useState(false);
  const { isOnline } = useConnectivity();
  const [showOptionalTechnicalDetails, setShowOptionalTechnicalDetails] =
    useState(false);

  // Unified Hook
  const {
    isLoading,
    isSaving,
    error,

    // Values
    materialTypeId,
    compositionId,
    measurementStrategy,
    purchasePriceAmount,
    salePriceAmount,
    description,
    barcode,
    dynamicProperties,
    inputMode,
    name,

    // Computed
    materialTypes,
    compositions,
    selectedStrategyConfig,

    // Handlers
    setMaterialTypeId,
    setCompositionId,
    setPurchasePriceAmount,
    setSalePriceAmount,
    setDescription,
    setBarcode,
    setName,
    handlePropertyChange,
    handleInputModeChange,
    handleSubmit,
    getPayload,
    refreshTypes,
    refreshCompositions,
    hasChanges,
  } = useMaterialForm({
    onSuccess,
    cloneFrom,
  });

  const selectedMaterialTypeObj = useMemo(
    () => materialTypes.find((t) => t.id === materialTypeId),
    [materialTypes, materialTypeId],
  );

  const SelectedStrategyForm = useMemo(() => {
    const strategy = getMaterialStrategy(measurementStrategy);
    return strategy?.FormComponent;
  }, [measurementStrategy]);

  const requiresComposition =
    selectedMaterialTypeObj?.requires_composition ??
    measurementStrategy?.toUpperCase() !== "LABOR";

  const [showSummary, setShowSummary] = useState(false);
  const [showTypeSelector, setShowTypeSelector] = useState(!cloneFrom);
  const [searchQuery, setSearchQuery] = useState("");

  const isCloneMode = !!cloneFrom;

  const filteredMaterialTypes = useMemo(() => {
    return materialTypes.filter(
      (type) =>
        type.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        type.measurement_strategy
          .toLowerCase()
          .includes(searchQuery.toLowerCase()),
    );
  }, [materialTypes, searchQuery]);

  const summaryData = useMemo(() => {
    if (!showSummary) return null;
    const payload = getPayload();
    if (!payload) return null;

    const typeName =
      materialTypes.find((t) => t.id === materialTypeId)?.name || "N/A";
    const selectedType = materialTypes.find((t) => t.id === materialTypeId);
    const requiresComp = selectedType?.requires_composition ?? true;

    const compName = requiresComp
      ? compositions.find((c) => c.id === compositionId)?.name || "N/A"
      : "No aplica";

    return {
      payload,
      typeName,
      compName,
      requiresComposition: requiresComp,
    };
  }, [
    showSummary,
    getPayload,
    materialTypes,
    materialTypeId,
    compositions,
    compositionId,
  ]);

  // ============================================================================
  // FILTERS & MEMOS (UI ONLY)
  // ============================================================================

  const filteredCompositions = useMemo(() => {
    return isCompositionCompatible(measurementStrategy) ? compositions : [];
  }, [compositions, measurementStrategy]);

  const shouldShowProperty = (prop: unknown): boolean => {
    return shouldShowPropertyUtil(
      prop as PropertyConfig,
      inputMode,
      dynamicProperties,
    );
  };

  // ============================================================================
  // CALLBACKS FOR MODALS
  // ============================================================================

  const handleMaterialTypeCreated = async (newType: MaterialType) => {
    await refreshTypes();
    setMaterialTypeId(newType.id);
    setShowCreateMaterialTypeModal(false);
  };

  const handleCompositionCreated = async (newComp: Composition) => {
    await refreshCompositions();
    setCompositionId(newComp.id);
    setShowCreateCompositionModal(false);
  };

  const renderTypeSelector = () => (
    <div className="flex min-h-[70dvh] max-h-[calc(100dvh-2rem)] flex-col animate-in fade-in slide-in-from-bottom-4 duration-500 md:h-[600px]">
      <div className="flex flex-1 flex-col items-center justify-start space-y-6 overflow-hidden p-3 sm:space-y-8 sm:p-4">
        <div className="text-center space-y-2">
          <h3 className="text-2xl font-black text-foreground tracking-tight">
            Que vas a create hoy?
          </h3>
          <p className="text-default-500 text-sm max-w-xs mx-auto">
            Selecciona el tipo de material para desbloquear las properties
            tecnicas especificas.
          </p>
        </div>

        <div className="w-full max-w-md animate-in fade-in slide-in-from-top-4 duration-700 delay-150">
          <Input
            placeholder="Search tipo de material..."
            value={searchQuery}
            onValueChange={setSearchQuery}
            variant="bordered"
            radius="full"
            size="lg"
            startContent={<Search className="text-default-400 w-5 h-5" />}
            endContent={
              searchQuery && (
                <Button
                  isIconOnly
                  variant="light"
                  radius="full"
                  size="sm"
                  onPress={() => setSearchQuery("")}
                >
                  <X className="w-4 h-4 text-default-400" />
                </Button>
              )
            }
            classNames={{
              inputWrapper:
                "bg-default-100/50 border-2 group-data-[focused=true]:border-primary transition-all duration-300",
            }}
          />
        </div>

        <div className="custom-scrollbar grid w-full max-w-2xl flex-1 grid-cols-1 gap-4 overflow-y-auto p-2 sm:grid-cols-2 lg:grid-cols-3">
          {filteredMaterialTypes.map((type) => {
            const strategy = type.measurement_strategy;
            return (
              <button
                key={type.id}
                type="button"
                onClick={() => {
                  setMaterialTypeId(type.id);
                  setShowTypeSelector(false);
                  setSearchQuery("");
                }}
                className="group relative flex flex-col items-center p-6 rounded-[2rem] bg-default-50 border-2 border-default-200 hover:border-primary hover:bg-primary/5 transition-all duration-300 hover:scale-[1.02] shadow-sm hover:shadow-md"
              >
                <div className="p-4 rounded-2xl bg-content1 shadow-sm group-hover:bg-primary/10 transition-colors duration-300 mb-3 border border-default-100">
                  <StrategyIcon strategyName={strategy} />
                </div>
                <span className="text-sm font-bold text-foreground group-hover:text-primary transition-colors text-center line-clamp-1">
                  {type.name}
                </span>
                <span className="text-[10px] uppercase tracking-widest text-default-400 font-black mt-1">
                  {strategy}
                </span>
              </button>
            );
          })}

          {filteredMaterialTypes.length === 0 && searchQuery && (
            <Button
              onPress={() => setShowCreateMaterialTypeModal(true)}
              className="col-span-full h-auto py-12 flex flex-col items-center justify-center space-y-4 rounded-[2rem] border-2 border-dashed border-default-200 hover:border-secondary hover:bg-secondary/5 transition-all duration-300 group bg-transparent"
            >
              <div className="p-4 rounded-2xl bg-default-100 group-hover:bg-secondary group-hover:text-white transition-colors duration-300">
                <Plus className="w-8 h-8" />
              </div>
              <div className="space-y-1">
                <p className="text-default-500 font-medium group-hover:text-secondary transition-colors">
                  No encontramos nada que coincida con "{searchQuery}"
                </p>
                <p className="text-xs text-default-400 font-black uppercase tracking-widest group-hover:text-secondary/70">
                  Hace click aca para create "{searchQuery}"
                </p>
              </div>
            </Button>
          )}

          {!searchQuery && (
            <button
              type="button"
              onClick={() => setShowCreateMaterialTypeModal(true)}
              className="flex flex-col items-center justify-center p-6 rounded-[2rem] border-2 border-dashed border-default-200 hover:border-secondary hover:bg-secondary/5 transition-all duration-300 group"
            >
              <div className="p-4 rounded-2xl bg-default-100 group-hover:bg-secondary group-hover:text-white transition-colors duration-300 mb-3">
                <Plus className="w-6 h-6" />
              </div>
              <span className="text-sm font-bold text-default-500 group-hover:text-secondary transition-colors">
                Nuevo Tipo
              </span>
            </button>
          )}
        </div>
      </div>

      <div className="flex flex-col-reverse justify-center gap-2 border-t border-default-100 pt-4 sm:flex-row sm:pt-6">
        <Button
          color="default"
          variant="light"
          onPress={onCancel}
          className="w-full font-bold sm:w-auto"
        >
          Cancel
        </Button>
        <Button
          color="primary"
          variant="solid"
          onPress={() => handleSubmit()}
          isLoading={isSaving}
          isDisabled={!isOnline}
          startContent={<CircleCheck className="w-4 h-4" />}
          className="w-full font-bold sm:w-auto"
          size="sm"
        >
          Confirmar y {isCloneMode ? "Clonar" : "Create"}
        </Button>
      </div>
    </div>
  );

  const renderSummary = () => (
    <div className="flex min-h-[70dvh] max-h-[calc(100dvh-2rem)] flex-col animate-in fade-in zoom-in-95 duration-300 md:h-[700px]">
      <div className="custom-scrollbar flex-1 overflow-y-auto p-3 sm:p-4">
        <div className="flex items-center gap-2 mb-2">
          <div className="p-2 bg-primary/10 rounded-full">
            <Eye className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-foreground">
              Resumen del Material
            </h3>
            <p className="text-xs text-default-500">
              Revisa que todo este correcto antes de confirmar
            </p>
          </div>
        </div>

        <Card className="border-none bg-default-50 shadow-sm">
          <CardBody className="p-6">
            <div className="flex flex-col gap-6 md:flex-row md:gap-8">
              {/* Visual Section */}
              <div className="w-full md:w-1/3 space-y-4">
                <div className="aspect-square rounded-2xl bg-content1 border border-default-200 overflow-hidden flex items-center justify-center shadow-inner">
                  {summaryData?.payload.image_url ? (
                    <LocalMediaImage
                      src={summaryData.payload.image_url}
                      alt="Preview"
                      className="w-full h-full object-contain p-2"
                    />
                  ) : (
                    <div className="flex flex-col items-center gap-2 text-default-300">
                      <Plus className="w-12 h-12 rotate-45" />
                      <span className="text-xs font-medium">Sin imagen</span>
                    </div>
                  )}
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between items-center px-1">
                    <span className="text-[10px] font-bold uppercase text-default-400">
                      Price Venta
                    </span>
                    <span className="text-lg font-bold text-success">
                      $
                      {formatCurrency(
                        summaryData?.payload.sale_price_amount || 0,
                      )
                        .replace("$", "")
                        .trim()}
                    </span>
                  </div>
                  <div className="flex justify-between items-center px-1">
                    <span className="text-[10px] font-bold uppercase text-default-400">
                      Price Compra
                    </span>
                    <span className="text-sm font-semibold text-warning-600">
                      $
                      {formatCurrency(
                        summaryData?.payload.purchase_price_amount || 0,
                      )
                        .replace("$", "")
                        .trim()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Info Section */}
              <div className="flex-1 space-y-6">
                <div className="grid grid-cols-1 gap-x-8 gap-y-4 sm:grid-cols-2">
                  <div className="col-span-2">
                    <p className="text-[10px] font-bold uppercase text-default-400 block mb-1">
                      Nombre / Tipo
                    </p>
                    <p className="text-xl font-bold text-foreground">
                      {summaryData?.payload.name || summaryData?.typeName}
                    </p>
                    {summaryData?.payload.name && (
                      <p className="text-xs text-default-400">
                        Tipo: {summaryData?.typeName}
                      </p>
                    )}
                  </div>

                  <div>
                    <p className="text-[10px] font-bold uppercase text-default-400 block mb-1">
                      Composicion
                    </p>
                    <p className="font-semibold text-foreground">
                      {summaryData?.compName}
                    </p>
                  </div>

                  <div>
                    <p className="text-[10px] font-bold uppercase text-default-400 block mb-1">
                      Estrategia
                    </p>
                    <div className="flex items-center gap-2 text-foreground">
                      <StrategyIcon
                        strategyName={
                          summaryData?.payload.measurement_strategy || ""
                        }
                      />
                      <span className="font-semibold text-sm">
                        {summaryData?.payload.measurement_strategy}
                      </span>
                    </div>
                  </div>

                  {summaryData?.payload.barcode && (
                    <div className="col-span-2">
                      <p className="text-[10px] font-bold uppercase text-default-400 block mb-1">
                        Codigo de Barras
                      </p>
                      <p className="font-mono text-sm bg-default-200/50 text-foreground px-2 py-1 rounded inline-block">
                        {summaryData.payload.barcode}
                      </p>
                    </div>
                  )}

                  {summaryData?.payload.description && (
                    <div className="col-span-2">
                      <p className="text-[10px] font-bold uppercase text-default-400 block mb-1">
                        Description
                      </p>
                      <p className="text-sm text-default-600 italic">
                        "{summaryData.payload.description}"
                      </p>
                    </div>
                  )}
                </div>

                {/* Dynamic Props Table */}
                <div className="pt-4 border-t border-divider">
                  <p className="text-[10px] font-bold uppercase text-default-400 block mb-3">
                    Properties Tecnicas
                  </p>
                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                    {Object.entries(summaryData?.payload.properties || {}).map(
                      ([key, val]) => {
                        if (val === undefined || val === null) return null;

                        if (typeof val === "object" && val !== null) {
                          const objVal = val as Record<string, string | number>;
                          return (
                            <div
                              key={key}
                              className="p-2 rounded-lg bg-content2 border border-default-100"
                            >
                              <span className="text-[9px] font-bold text-default-400 uppercase block">
                                {key === "thickness"
                                  ? "Espesor / Calibre"
                                  : key === "part_number"
                                    ? "Referencia"
                                    : key === "brand"
                                      ? "Marca"
                                      : key === "width"
                                        ? "Ancho"
                                        : key === "length"
                                          ? "Largo"
                                          : key === "area"
                                            ? "Area"
                                            : key === "color"
                                              ? "Color"
                                              : key.replace("_", " ")}
                              </span>
                              <span className="text-xs font-bold text-foreground">
                                {objVal.value ?? objVal.gauge ?? "-"}{" "}
                                <span className="text-[10px] text-primary">
                                  {(objVal.unit as string) ??
                                    (objVal.gauge ? "Ga" : "")}
                                </span>
                              </span>
                            </div>
                          );
                        }
                        return (
                          <div
                            key={key}
                            className="p-2 rounded-lg bg-content2 border border-default-100"
                          >
                            <span className="text-[9px] font-bold text-default-400 uppercase block">
                              {key.replace("_", " ")}
                            </span>
                            <span className="text-xs font-bold text-foreground">
                              {String(val)}
                            </span>
                          </div>
                        );
                      },
                    )}
                  </div>
                </div>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>

      <div className="mt-6 flex flex-col-reverse justify-end gap-3 border-t border-default-100 pt-6 sm:flex-row">
        <Button
          color="default"
          variant="flat"
          onPress={() => setShowSummary(false)}
          size="sm"
          className="w-full sm:w-auto"
        >
          Volver a Edit
        </Button>
        <Button
          color="primary"
          variant="solid"
          onPress={() => handleSubmit()}
          isLoading={isSaving}
          startContent={<CircleCheck className="w-4 h-4" />}
          className="w-full px-8 font-bold sm:w-auto"
          size="sm"
        >
          Confirmar y {isCloneMode ? "Clonar" : "Create"}
        </Button>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="flex justify-center p-8">
        <Spinner />
      </div>
    );
  }

  return (
    <>
      {showTypeSelector ? (
        renderTypeSelector()
      ) : showSummary && summaryData ? (
        renderSummary()
      ) : (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            setShowSummary(true);
          }}
          className="custom-scrollbar flex min-h-[70dvh] max-h-[calc(100dvh-2rem)] flex-col overflow-y-auto md:h-[700px] md:overflow-hidden"
        >
          {error && (
            <div className="rounded-md bg-danger-50 p-3 text-sm text-danger mb-4 mx-1">
              {error}
            </div>
          )}

          <div className="flex flex-1 min-h-0 flex-col items-start gap-6 p-2 sm:p-3 md:flex-row md:gap-8">
            {SelectedStrategyForm ? (
              <SelectedStrategyForm
                dynamicProperties={dynamicProperties}
                onPropertyChange={handlePropertyChange}
                strategyConfig={selectedStrategyConfig}
                inputMode={inputMode}
                onInputModeChange={handleInputModeChange}
                shouldShowProperty={shouldShowProperty}
                materialTypeObj={selectedMaterialTypeObj}
                compositions={compositions}
                compositionId={compositionId}
                setCompositionId={setCompositionId}
                setShowCreateCompositionModal={setShowCreateCompositionModal}
                setShowTypeSelector={setShowTypeSelector}
                barcode={barcode}
                setBarcode={setBarcode}
                description={description}
                setDescription={setDescription}
                purchasePrice={purchasePriceAmount}
                setPurchasePrice={setPurchasePriceAmount}
                salePrice={salePriceAmount}
                setSalePrice={setSalePriceAmount}
                showOptionalIdentity={showOptionalIdentity}
                setShowOptionalIdentity={setShowOptionalIdentity}
                showOptionalTechnicalDetails={showOptionalTechnicalDetails}
                setShowOptionalTechnicalDetails={
                  setShowOptionalTechnicalDetails
                }
                name={name}
                setName={setName}
              />
            ) : (
              <>
                {/* --- LEFT COLUMN: Identity & Cost --- */}
                <div className="w-full space-y-6 md:max-h-full md:flex-1 md:overflow-y-auto md:pr-4 md:custom-scrollbar">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between sticky top-0 bg-content1/95 backdrop-blur-md py-2 z-20 border-b border-divider mb-2">
                      <h3 className="text-[10px] font-bold uppercase tracking-wider text-default-400">
                        Identidad del Material
                      </h3>
                      <Button
                        size="sm"
                        variant="light"
                        color="primary"
                        className="h-6 text-[10px] font-bold"
                        onPress={() => setShowTypeSelector(true)}
                      >
                        Cambiar Tipo
                      </Button>
                    </div>
                    <div className="space-y-4">
                      <div className="p-4 rounded-2xl bg-primary/5 border border-primary/10 flex items-center gap-4 animate-in fade-in slide-in-from-left-2">
                        <div className="p-3 bg-content1 rounded-xl shadow-sm border border-default-100">
                          <StrategyIcon strategyName={measurementStrategy} />
                        </div>
                        <div>
                          <p className="text-[10px] uppercase font-black text-primary/50 leading-none mb-1">
                            Tipo seleccionado
                          </p>
                          <p className="text-lg font-black text-primary leading-none">
                            {selectedMaterialTypeObj?.name}
                          </p>
                        </div>
                      </div>

                      {requiresComposition && (
                        <div className="space-y-1">
                          <Autocomplete
                            label="Composicion"
                            placeholder="Ej: Acero, Aluminio..."
                            selectedKey={compositionId}
                            onSelectionChange={(key: React.Key | null) =>
                              setCompositionId(key as string)
                            }
                            isRequired
                            variant="flat"
                            size="sm"
                          >
                            {filteredCompositions.map((comp) => (
                              <AutocompleteItem
                                key={comp.id}
                                textValue={comp.name}
                              >
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
                        </div>
                      )}
                    </div>

                    <Divider className="my-2" />

                    <div className="space-y-4">
                      <button
                        type="button"
                        className="w-full flex items-center justify-between p-2 hover:bg-default-100 rounded-lg transition-colors text-left"
                        onClick={() =>
                          setShowOptionalIdentity(!showOptionalIdentity)
                        }
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
                          <span className="text-tiny font-medium text-primary">
                            {showOptionalIdentity ? "Ver menos" : "Completar"}
                          </span>
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
                            onValueChange={setBarcode}
                          />
                          <Input
                            label="Description"
                            placeholder="Description del material"
                            size="sm"
                            variant="bordered"
                            value={description}
                            onValueChange={setDescription}
                          />
                        </div>
                      )}
                    </div>
                  </div>

                  {/* --- PRICE --- */}
                  <div className="space-y-4">
                    <h3 className="text-[10px] font-bold uppercase tracking-wider text-default-400 sticky top-0 bg-content1/95 backdrop-blur-md py-2 z-20 border-b border-divider mb-2">
                      Costos y Precios
                    </h3>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      <Input
                        type="text"
                        label="Price Compra"
                        placeholder="0"
                        size="sm"
                        value={
                          purchasePriceAmount
                            ? formatCurrency(parseFloat(purchasePriceAmount))
                                .replace("$", "")
                                .trim()
                            : ""
                        }
                        onValueChange={(val: string) => {
                          const numericValue = val.replace(/\D/g, "");
                          setPurchasePriceAmount(numericValue);
                        }}
                        isRequired
                        startContent={
                          <div className="pointer-events-none flex items-center">
                            <span className="text-default-400 text-small font-bold">
                              $
                            </span>
                          </div>
                        }
                      />
                      <Input
                        type="text"
                        label="Price Venta"
                        placeholder="0"
                        size="sm"
                        value={
                          salePriceAmount
                            ? formatCurrency(parseFloat(salePriceAmount))
                                .replace("$", "")
                                .trim()
                            : ""
                        }
                        onValueChange={(val: string) => {
                          const numericValue = val.replace(/\D/g, "");
                          setSalePriceAmount(numericValue);
                        }}
                        startContent={
                          <div className="pointer-events-none flex items-center">
                            <span className="text-default-400 text-small font-bold">
                              $
                            </span>
                          </div>
                        }
                      />
                    </div>
                  </div>

                  {/* --- STRATEGY INFO (Visual only) --- */}
                  {selectedStrategyConfig && (
                    <div className="space-y-4 pt-2">
                      <h3 className="text-[10px] font-bold uppercase tracking-wider text-default-400 sticky top-0 bg-content1/95 backdrop-blur-md py-2 z-20 border-b border-divider mb-2">
                        Medicion
                      </h3>
                      <div className="flex items-center gap-3 p-3 rounded-lg bg-default-50 border border-default-200">
                        <StrategyIcon
                          strategyName={selectedStrategyConfig.name}
                        />
                        <div className="flex-1 overflow-hidden">
                          <p className="font-semibold text-foreground text-xs truncate">
                            {selectedStrategyConfig.display_name}
                          </p>
                          <p className="text-[10px] leading-tight text-default-500 line-clamp-1">
                            {selectedStrategyConfig.description}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* --- RIGHT COLUMN: Technical Properties & Details --- */}
                <div className="w-full space-y-6 md:max-h-full md:flex-1 md:overflow-y-auto md:pr-4 md:custom-scrollbar">
                  <CommonMaterialFields
                    name={name}
                    onNameChange={setName}
                    dynamicProperties={dynamicProperties}
                    onPropertyChange={handlePropertyChange}
                  />

                  {/* --- DYNAMIC PROPERTIES --- */}
                  {selectedStrategyConfig &&
                    selectedStrategyConfig.properties &&
                    selectedStrategyConfig.properties.length > 0 &&
                    measurementStrategy?.toUpperCase() !== "UNIT" && (
                      <div className="space-y-4">
                        <h3 className="text-[10px] font-bold uppercase tracking-wider text-default-400 sticky top-0 bg-content1/95 backdrop-blur-md py-2 z-20 border-b border-divider mb-2">
                          Properties Tecnicas
                        </h3>
                        <div className="bg-default-50/50 rounded-xl p-4 border border-default-100">
                          <StrategyProperties
                            measurementStrategy={measurementStrategy}
                            strategyConfig={selectedStrategyConfig}
                            dynamicProperties={dynamicProperties}
                            onPropertyChange={handlePropertyChange}
                            inputMode={inputMode}
                            onInputModeChange={handleInputModeChange}
                            shouldShowProperty={shouldShowProperty}
                          />
                        </div>
                      </div>
                    )}

                  {/* --- SIMPLE UNIT MESSAGE --- */}
                  {measurementStrategy?.toUpperCase() === "UNIT" && (
                    <div className="flex flex-col items-center justify-center h-full p-8 text-center space-y-4 bg-default-50/30 rounded-2xl border-2 border-dashed border-default-200">
                      <div className="p-4 bg-primary/10 rounded-full">
                        <StrategyIcon strategyName="UNIT" />
                      </div>
                      <div className="space-y-1">
                        <p className="text-sm font-bold text-foreground">
                          Material por Unidad
                        </p>
                        <p className="text-xs text-default-500 max-w-[200px]">
                          Este material no requiere properties tecnicas
                          adicionales. Solo define su costo unitario.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>

          {/* --- FOOTER --- */}
          <div className="mt-6 flex flex-col-reverse justify-end gap-3 border-t border-default-100 pt-6 sm:flex-row">
            <Button
              color="default"
              variant="flat"
              onPress={onCancel}
              size="sm"
              className="w-full sm:w-auto"
            >
              Cancel
            </Button>
            <Button
              color="primary"
              variant="solid"
              type="submit"
              isLoading={isSaving}
              isDisabled={
                !isOnline ||
                !materialTypeId ||
                !measurementStrategy ||
                !purchasePriceAmount ||
                (requiresComposition && !compositionId) ||
                (isCloneMode && !hasChanges)
              }
              className="w-full px-8 font-bold sm:w-auto"
              size="sm"
              startContent={<Eye className="w-4 h-4" />}
            >
              Revisar Resumen
            </Button>
          </div>
        </form>
      )}

      <CreateMaterialTypeModal
        isOpen={showCreateMaterialTypeModal}
        onOpenChange={setShowCreateMaterialTypeModal}
        onSuccess={handleMaterialTypeCreated}
        initialName={searchQuery}
      />

      <CreateCompositionModal
        isOpen={showCreateCompositionModal}
        onOpenChange={setShowCreateCompositionModal}
        onSuccess={handleCompositionCreated}
      />
    </>
  );
};
