import React, { useState } from "react";
import {
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  Input,
  useDisclosure,
} from "@heroui/react";
import { Client, UpdateClientRequest } from "@/types/clients";
import { clientService } from "@services/clientService";
import { CenteredModal } from "./CenteredModal";
import { SecondaryButton, StatusMessage, PrimaryButton } from "./StyledButton";

interface EditClientModalProps {
  client: Client;
  onClientUpdated?: (client: Client) => void;
}

export const EditClientModal: React.FC<EditClientModalProps> = ({
  client,
  onClientUpdated,
}) => {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState<UpdateClientRequest>({
    first_name: client.first_name,
    last_name: client.last_name,
    email: client.email,
    phone: client.phone,
    address: client.address,
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev: UpdateClientRequest) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async () => {
    setError(null);

    if (
      !formData.first_name?.trim() ||
      !formData.last_name?.trim() ||
      !formData.email?.trim() ||
      !formData.phone?.trim() ||
      !formData.address?.trim()
    ) {
      setError("Todos los campos son obligatorios");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError("El email no es valido");
      return;
    }

    try {
      setIsLoading(true);
      const updatedClient = await clientService.updateClient(
        client.identification_number,
        formData,
      );
      onClientUpdated?.(updatedClient);
      onOpenChange();
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Error al actualizar el client";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <SecondaryButton onPress={onOpen} size="sm" className="min-w-fit">
        Edit Client
      </SecondaryButton>

      <CenteredModal
        isOpen={isOpen}
        onOpenChange={onOpenChange}
        size="2xl"
        backdrop="blur"
      >
        {(onClose: () => void) => (
          <>
            <ModalHeader className="flex flex-col gap-1 text-secondary">
              Edit Client
            </ModalHeader>

            <ModalBody className="gap-4">
              {error && <StatusMessage type="error">{error}</StatusMessage>}

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <Input
                  label="Nombre"
                  name="first_name"
                  value={formData.first_name || ""}
                  onChange={handleInputChange}
                  isDisabled={isLoading}
                  isRequired
                />

                <Input
                  label="Apellido"
                  name="last_name"
                  value={formData.last_name || ""}
                  onChange={handleInputChange}
                  isDisabled={isLoading}
                  isRequired
                />
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <Input
                  label="Email"
                  name="email"
                  type="email"
                  value={formData.email || ""}
                  onChange={handleInputChange}
                  isDisabled={isLoading}
                  isRequired
                />

                <Input
                  label="Telefono"
                  name="phone"
                  value={formData.phone || ""}
                  onChange={handleInputChange}
                  isDisabled={isLoading}
                  isRequired
                />
              </div>

              <Input
                label="Direccion"
                name="address"
                value={formData.address || ""}
                onChange={handleInputChange}
                isDisabled={isLoading}
                isRequired
                fullWidth
              />
            </ModalBody>

            <ModalFooter className="flex flex-col-reverse gap-2 sm:flex-row">
              <Button
                color="danger"
                variant="light"
                onPress={onClose}
                isDisabled={isLoading}
                className="w-full font-bold sm:w-auto"
              >
                Cancel
              </Button>
              <PrimaryButton
                onPress={handleSubmit}
                isLoading={isLoading}
                className="w-full sm:w-auto"
              >
                Actualizar Client
              </PrimaryButton>
            </ModalFooter>
          </>
        )}
      </CenteredModal>
    </>
  );
};

export default EditClientModal;
