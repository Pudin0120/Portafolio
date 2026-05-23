import React, { useEffect, useState, useMemo } from "react";
import { useAuth } from "@hooks/useAuth";
import { CenteredModal } from "@components/common/CenteredModal";
import { apiClient } from "@services/apiClient";
import {
  ModalHeader,
  ModalBody,
  Button,
  Input,
  Textarea,
  Select,
  SelectItem,
  Spinner,
  Divider,
  Switch,
} from "@heroui/react";
import { Composition } from "@/types/products";

type CreateCompositionModalProps = {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  onSuccess?: (newComposition: any) => void;
};

export const CreateCompositionModal: React.FC<CreateCompositionModalProps> = ({
  isOpen,
  onOpenChange,
  onSuccess,
}) => {
  const { user } = useAuth();
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");

  // Form state
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [showDescription, setShowDescription] = useState(false);

  const resetForm = () => {
    setName("");
    setDescription("");
    setError("");
  };

  const handleOpenChange = (newIsOpen: boolean) => {
    if (!newIsOpen) {
      resetForm();
    }
    onOpenChange(newIsOpen);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    setIsSaving(true);
    setError("");

    try {
      const payload = {
        name,
        description: description || undefined,
      };

      const createdComposition = await apiClient.post<any>("/compositions/", payload);

      resetForm();
      onOpenChange(false);
      onSuccess?.(createdComposition);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      console.error("ERROR Error al create composicion:", message);
      setError(message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <CenteredModal
      isOpen={isOpen}
      onOpenChange={handleOpenChange}
      size="lg"
      backdrop="blur"
    >
      {(onClose) => (
        <>
          <ModalHeader className="flex flex-col gap-1 border-b border-divider pb-4">
            <h2 className="text-xl font-bold text-foreground">
              Nueva Composicion
            </h2>
            <p className="text-xs text-default-500 font-normal">
              Define las caracteristicas quimicas o de marca del material.
            </p>
          </ModalHeader>
          <ModalBody>
            <form onSubmit={handleSubmit} className="space-y-4 pb-4">
              {error && (
                <div className="rounded-md bg-danger/20 p-3 text-sm text-danger border border-danger/30">
                  {error}
                </div>
              )}

              <Input
                label="Nombre"
                placeholder="Ej: Acero Galvanizado"
                value={name}
                onValueChange={setName}
                isRequired
                variant="bordered"
              />

              <div className="flex items-center justify-between p-2 rounded-lg bg-default-50 border border-default-200">
                <span className="text-sm font-medium">Agregar description</span>
                <Switch
                  isSelected={showDescription}
                  onValueChange={(val: boolean) => {
                    setShowDescription(val);
                    if (!val) setDescription("");
                  }}
                  size="sm"
                  color="primary"
                />
              </div>

              {showDescription && (
                <Textarea
                  label="Description"
                  placeholder="Detalles sobre aleaciones, grado, etc."
                  value={description}
                  onValueChange={setDescription}
                  variant="bordered"
                  minRows={2}
                  className="animate-in fade-in slide-in-from-top-1 duration-200"
                />
              )}

              <div className="flex justify-end gap-2 pt-4 mt-2 border-t border-divider">
                <Button
                  color="default"
                  variant="flat"
                  onPress={() => handleOpenChange(false)}
                  isDisabled={isSaving}
                  size="sm"
                >
                  Cancel
                </Button>
                <Button
                  color="primary"
                  variant="solid"
                  type="submit"
                  isLoading={isSaving}
                  isDisabled={!name}
                  className="font-semibold"
                  size="sm"
                >
                  Create Composicion
                </Button>
              </div>
            </form>
          </ModalBody>
        </>
      )}
    </CenteredModal>
  );
};
