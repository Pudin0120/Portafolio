import React, { useState } from "react";
import {
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  Input,
  Select,
  SelectItem,
  useDisclosure,
} from "@heroui/react";
import { Client, CreateClientRequest, DocumentType } from "@/types/clients";
import { clientService } from "@services/clientService";
import { CenteredModal } from "./CenteredModal";
import { PrimaryButton, StatusMessage } from "./StyledButton";

interface CreateClientModalProps {
  onClientCreated?: (client: Client) => void;
}

const DOCUMENT_TYPES: DocumentType[] = ["CC", "CE", "NIT"];

export const CreateClientModal: React.FC<CreateClientModalProps> = ({
  onClientCreated,
}) => {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState<CreateClientRequest>({
    identification_number: "",
    document_type: "CC",
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    address: "",
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    let newValue = value;

    if (name === "identification_number" && value.length > 10) {
      newValue = value.slice(0, 10);
    } else if (name === "phone" && value.length > 15) {
      newValue = value.slice(0, 15);
    }

    setFormData((prev) => ({
      ...prev,
      [name]: newValue,
    }));
  };

  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value as DocumentType,
    }));
  };

  const handleSubmit = async () => {
    setError(null);

    if (
      !formData.identification_number.trim() ||
      !formData.first_name.trim() ||
      !formData.last_name.trim() ||
      !formData.email.trim() ||
      !formData.phone.trim() ||
      !formData.address.trim()
    ) {
      setError("Todos los campos son obligatorios");
      return;
    }

    if (formData.identification_number.length > 10) {
      setError(
        "El numero de identificacion no puede tener mas de 10 caracteres",
      );
      return;
    }

    if (formData.phone.length > 15) {
      setError("El telefono no puede tener mas de 15 caracteres");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError("El email no es valido");
      return;
    }

    try {
      setIsLoading(true);
      const newClient = await clientService.createClient(formData);
      onClientCreated?.(newClient);

      setFormData({
        identification_number: "",
        document_type: "CC",
        first_name: "",
        last_name: "",
        email: "",
        phone: "",
        address: "",
      });

      onOpenChange();
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Error al create el client";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <PrimaryButton onPress={onOpen}>+ Create Nuevo Client</PrimaryButton>

      <CenteredModal
        isOpen={isOpen}
        onOpenChange={onOpenChange}
        size="2xl"
        backdrop="blur"
      >
        {(onClose: () => void) => (
          <>
            <ModalHeader className="flex flex-col gap-1 text-primary">
              Create Nuevo Client
            </ModalHeader>

            <ModalBody className="gap-4">
              {error && <StatusMessage type="error">{error}</StatusMessage>}

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <Input
                  label="Numero de Identificacion"
                  name="identification_number"
                  value={formData.identification_number}
                  onChange={handleInputChange}
                  placeholder="Ej: 123456789"
                  isDisabled={isLoading}
                  isRequired
                />

                <Select
                  label="Document Type"
                  name="document_type"
                  selectedKeys={[formData.document_type]}
                  onChange={handleSelectChange}
                  isDisabled={isLoading}
                  isRequired
                >
                  {DOCUMENT_TYPES.map((type) => (
                    <SelectItem key={type} value={type} textValue={type}>
                      {type}
                    </SelectItem>
                  ))}
                </Select>
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <Input
                  label="Nombre"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  placeholder="Juan"
                  isDisabled={isLoading}
                  isRequired
                />

                <Input
                  label="Apellido"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  placeholder="Perez"
                  isDisabled={isLoading}
                  isRequired
                />
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <Input
                  label="Email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="juan@example.com"
                  isDisabled={isLoading}
                  isRequired
                />

                <Input
                  label="Telefono"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  placeholder="3001234567"
                  isDisabled={isLoading}
                  isRequired
                />
              </div>

              <Input
                label="Direccion"
                name="address"
                value={formData.address}
                onChange={handleInputChange}
                placeholder="Calle 123 #45-67"
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
                Create Client
              </PrimaryButton>
            </ModalFooter>
          </>
        )}
      </CenteredModal>
    </>
  );
};

export default CreateClientModal;
