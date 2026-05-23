import React, { useMemo, useState } from "react";
import { ModalHeader, ModalBody, Button, Spinner } from "@heroui/react";
import { Material } from "@/types/products";
import { CenteredModal } from "@components/common/CenteredModal";
import {
  shouldShowProperty as shouldShowPropertyUtil,
  useMaterialForm,
} from "./material-creation";
import { getMaterialStrategy } from "./material-creation/strategies/registry";
import { useMaterials } from "@context/MaterialsContext";
import type { PropertyConfig } from "@/types/material-creation";

interface EditMaterialModalProps {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  material: Material;
  onSuccess: () => void;
}

export const EditMaterialModal: React.FC<EditMaterialModalProps> = ({
  isOpen,
  onOpenChange,
  material,
  onSuccess,
}) => {
  const { fetchMaterials } = useMaterials();
  const [showOptionalIdentity, setShowOptionalIdentity] = useState(false);
  const [showOptionalTechnicalDetails, setShowOptionalTechnicalDetails] =
    useState(false);

  // Hook unificado para manejo de estado
  const {
    isLoading,
    isSaving,
    isDataReady,
    error,

    // Values
    purchasePriceAmount,
    salePriceAmount,
    description,
    barcode,
    materialTypeId,
    dynamicProperties,
    inputMode,
    compositionId,
    name,

    // Computed
    materialTypes,
    fullMaterial,
    selectedStrategyConfig,
    compositions,

    // Handlers
    setPurchasePriceAmount,
    setSalePriceAmount,
    setDescription,
    setBarcode,
    setCompositionId,
    setName,
    handlePropertyChange,
    handleInputModeChange,
    handleSubmit,
  } = useMaterialForm({
    initialMaterialId: isOpen ? material.id : undefined,
    onSuccess: async () => {
      await fetchMaterials();
      onSuccess();
      onOpenChange(false); // Cerrar modal al save
    },
  });

  const shouldShowProperty = (prop: unknown): boolean => {
    return shouldShowPropertyUtil(
      prop as PropertyConfig,
      inputMode,
      dynamicProperties,
    );
  };

  const SelectedStrategyForm = useMemo(() => {
    if (!material.measurement_strategy) return null;
    const strategy = getMaterialStrategy(material.measurement_strategy);
    return strategy?.FormComponent;
  }, [material.measurement_strategy]);

  const selectedMaterialTypeObj = useMemo(
    () => materialTypes.find((mt) => mt.id === materialTypeId),
    [materialTypes, materialTypeId],
  );

  if (isLoading && isOpen) {
    return (
      <CenteredModal isOpen={isOpen} onOpenChange={onOpenChange} size="lg">
        {() => (
          <div className="flex justify-center items-center py-8">
            <Spinner />
          </div>
        )}
      </CenteredModal>
    );
  }

  return (
    <CenteredModal
      isOpen={isOpen}
      onOpenChange={onOpenChange}
      size="5xl"
      scrollBehavior="inside"
      backdrop="blur"
    >
      {() => (
        <>
          <ModalHeader className="border-b border-default-100 pb-4">
            Edit Material: {fullMaterial?.name || material.name}
          </ModalHeader>
          <ModalBody className="overflow-hidden p-0">
            <form
              onSubmit={handleSubmit}
              className="flex min-h-[70dvh] max-h-[calc(100dvh-2rem)] flex-col md:h-[750px]"
            >
              {error && (
                <div className="mx-6 mt-4 rounded-md bg-danger-50 p-3 text-sm text-danger">
                  {error}
                </div>
              )}

              <div className="min-h-0 flex-1 overflow-hidden p-2 sm:p-3">
                {SelectedStrategyForm && (
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
                    setShowCreateCompositionModal={() => {}} // Not needed in edit for now or can be added
                    setShowTypeSelector={() => {}} // Not allowed to change type in edit
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
                    name={name} // Use the dedicated name state from hook
                    setName={setName}
                  />
                )}
              </div>

              <div className="flex flex-col-reverse gap-3 border-t border-divider bg-content1 p-4 sm:flex-row sm:justify-end sm:p-6">
                <Button
                  color="default"
                  variant="flat"
                  type="button"
                  onPress={() => onOpenChange(false)}
                  size="sm"
                  className="w-full sm:w-auto"
                >
                  Cancel
                </Button>
                <Button
                  color="primary"
                  type="submit"
                  isLoading={isSaving}
                  isDisabled={!purchasePriceAmount || !isDataReady}
                  size="sm"
                  className="w-full px-8 font-bold sm:w-auto"
                >
                  {isSaving ? "Guardando..." : "Actualizar Material"}
                </Button>
              </div>
            </form>
          </ModalBody>
        </>
      )}
    </CenteredModal>
  );
};
