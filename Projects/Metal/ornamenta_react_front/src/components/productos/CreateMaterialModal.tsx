import React from "react";
import { ModalHeader, ModalBody } from "@heroui/react";
import { CenteredModal } from "@components/common/CenteredModal";
import { CreateMaterial } from "./CreateMaterial";
import { useMaterials } from "@context/MaterialsContext";

import { Material } from "@/types/products";

interface CreateMaterialModalProps {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  onSuccess?: () => void;
  cloneFrom?: Material;
}

export const CreateMaterialModal: React.FC<CreateMaterialModalProps> = ({
  isOpen,
  onOpenChange,
  onSuccess,
  cloneFrom,
}) => {
  const { fetchMaterials } = useMaterials();

  const handleSuccess = async () => {
    await fetchMaterials();
    if (onSuccess) onSuccess();
    onOpenChange(false);
  };

  return (
    <CenteredModal
      isOpen={isOpen}
      onOpenChange={onOpenChange}
      size="4xl"
      scrollBehavior="inside"
      backdrop="blur"
    >
      {(onClose) => (
        <>
          <ModalHeader className="border-b border-default-100 pb-3">
            <div className="flex flex-col">
              <span className="text-xl font-bold text-primary">
                {cloneFrom
                  ? `Clonar Material: ${cloneFrom.name}`
                  : "Create Nuevo Material"}
              </span>
              <span className="text-xs text-default-500 font-normal">
                {cloneFrom
                  ? "Modifica los valores para create una nueva version de este material"
                  : "Configura la identidad y properties tecnicas del material"}
              </span>
            </div>
          </ModalHeader>
          <ModalBody className="py-6">
            <CreateMaterial
              onSuccess={handleSuccess}
              onCancel={onClose}
              cloneFrom={cloneFrom}
            />
          </ModalBody>
        </>
      )}
    </CenteredModal>
  );
};
