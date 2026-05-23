import React, { useState } from "react";
import {
  Alert,
  Button,
  Input,
  ModalBody,
  ModalFooter,
  ModalHeader,
  Select,
  SelectItem,
} from "@heroui/react";
import { CenteredModal } from "../common";
import type { IUserData } from "@shared/user";
import type { Role } from "@shared/role";
import { ApiError } from "../../services/apiClient";
import { UserService } from "../../services/userService";
import { translateError } from "../../utils/errorHandling";
import { auth } from "../../services/firebase";
import { fetchSignInMethodsForEmail } from "firebase/auth";
import { useEmployeeMetadata } from "../../hooks/useEmployeeMetadata";

interface CreateEmployeeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: unknown) => void;
  onError: (error: string) => void;
  initialData?: Partial<IUserData>;
  isEdit?: boolean;
}

const getInitialFormData = (initialData?: Partial<IUserData>): IUserData => ({
  identification_number: initialData?.identification_number ?? "",
  document_type: initialData?.document_type ?? "CC",
  first_name: initialData?.first_name ?? "",
  last_name: initialData?.last_name ?? "",
  email: initialData?.email ?? "",
  state: initialData?.state ?? "A",
  firebase_uid: initialData?.firebase_uid ?? "",
  phone: initialData?.phone ?? "",
  role: initialData?.role ?? "",
  password: "",
});

const getErrorMessage = (error: unknown): string => {
  if (error instanceof ApiError) {
    return translateError(error.message);
  }

  if (error instanceof Error) {
    return translateError(error.message);
  }

  return "Error al procesar la solicitud";
};

const getFirebaseErrorCode = (error: unknown): string | null => {
  if (typeof error !== "object" || error === null || !("code" in error)) {
    return null;
  }

  const code = (error as { code?: unknown }).code;
  return typeof code === "string" ? code : null;
};

export const CreateEmployeeModal: React.FC<CreateEmployeeModalProps> = ({
  isOpen,
  onClose,
  onSave,
  onError,
  initialData,
  isEdit = false,
}) => {
  const [formData, setFormData] = useState<IUserData>(
    getInitialFormData(initialData),
  );
  const [isLoading, setIsLoading] = useState(false);
  const [internalError, setInternalError] = useState<string | null>(null);

  const { roles, documentTypes } = useEmployeeMetadata();

  const handleInputChange = (field: keyof IUserData, value: string) => {
    let newValue = value;

    switch (field) {
      case "identification_number":
        if (formData.document_type === "NI") {
          newValue = newValue.replace(/[^a-zA-Z0-9-]/g, "").slice(0, 15);
        } else {
          newValue = newValue.replace(/\D/g, "").slice(0, 10);
        }
        break;

      case "phone":
        newValue = newValue.replace(/(?!^\+)\D/g, "").slice(0, 13);
        if (!/^\+?\d*$/.test(newValue)) {
          return;
        }
        break;

      case "first_name":
      case "last_name":
        newValue = newValue
          .replace(/[^a-zA-ZaeiouAEIOUnN\s]/g, "")
          .slice(0, 50);
        break;

      case "email":
        newValue = newValue.slice(0, 100);
        break;

      case "password":
        newValue = newValue.slice(0, 50);
        break;
    }

    setFormData((prev) => ({
      ...prev,
      [field]: newValue,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setInternalError(null);

    if (
      !formData.identification_number ||
      !formData.first_name ||
      !formData.last_name ||
      !formData.email ||
      (!isEdit && !formData.password)
    ) {
      const message = "Please completa todos los campos obligatorios.";
      setInternalError(message);
      onError(message);
      setIsLoading(false);
      return;
    }

    if (!isEdit && formData.password.length < 6) {
      const message = "La password debe tener al menos 6 caracteres.";
      setInternalError(message);
      onError(message);
      setIsLoading(false);
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      const message = "Please ingresa un email valid.";
      setInternalError(message);
      onError(message);
      setIsLoading(false);
      return;
    }

    try {
      if (!isEdit) {
        try {
          if (!auth) {
            throw new Error("Firebase no configurado");
          }

          const signInMethods = await fetchSignInMethodsForEmail(
            auth,
            formData.email,
          );

          if (signInMethods.length > 0) {
            const message =
              "Este email ya esta registrado en Firebase.";
            setInternalError(message);
            onError(message);
            setIsLoading(false);
            return;
          }
        } catch (firebaseError: unknown) {
          if (getFirebaseErrorCode(firebaseError) === "auth/email-already-in-use") {
            const message = "Este email ya esta registrado.";
            setInternalError(message);
            onError(message);
            setIsLoading(false);
            return;
          }
        }
      }

      const response = isEdit
        ? await UserService.updateUser(
            initialData?.identification_number ?? "",
            formData,
          )
        : await UserService.createUserWithFirebase(formData);

      onSave(response);
      setFormData(
        getInitialFormData({
          role: roles[0]?.id ?? "",
        }),
      );
      onClose();
    } catch (error: unknown) {
      const message = getErrorMessage(error);
      setInternalError(message);
      onError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <CenteredModal
      isOpen={isOpen}
      onOpenChange={(open: boolean) => !open && onClose()}
      size="lg"
      scrollBehavior="inside"
      backdrop="blur"
    >
      {() => (
        <form
          onSubmit={handleSubmit}
          className="flex h-full min-h-[60dvh] flex-col overflow-hidden"
        >
          <ModalHeader className="flex shrink-0 flex-col gap-1 pb-2">
            <h3 className="text-xl font-semibold">
              {isEdit ? "Edit empleado" : "Create empleado"}
            </h3>
            <p className="text-sm text-default-500">
              {isEdit
                ? "Modifica los datos del empleado."
                : "Completa los datos del nuevo empleado."}
            </p>
          </ModalHeader>

          <ModalBody className="gap-4 overflow-y-auto px-1 pb-4 sm:px-2">
            {internalError && (
              <Alert
                color="danger"
                variant="flat"
                title={internalError}
                onClose={() => setInternalError(null)}
              />
            )}

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Select
                label="Tipo de document"
                placeholder="Selecciona el tipo"
                selectedKeys={[formData.document_type]}
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                  handleInputChange("document_type", e.target.value)
                }
                required
                classNames={{
                  label: "font-medium text-foreground/80",
                  trigger:
                    "min-h-12 border border-divider bg-content1/90 text-foreground shadow-sm dark:bg-content2/80",
                  value: "text-foreground",
                  helperWrapper: "text-surface-muted",
                  description: "text-surface-muted",
                  selectorIcon: "text-surface-muted",
                }}
              >
                {documentTypes.map((doc) => (
                  <SelectItem key={doc.id} value={doc.id} textValue={doc.label}>
                    {doc.label}
                  </SelectItem>
                ))}
              </Select>

              <Input
                label="Number de document"
                placeholder="123456789"
                value={formData.identification_number}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  handleInputChange("identification_number", e.target.value)
                }
                required
              />
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Input
                label="Nombre"
                placeholder="Juan"
                value={formData.first_name}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  handleInputChange("first_name", e.target.value)
                }
                required
              />
              <Input
                label="Apellido"
                placeholder="Perez"
                value={formData.last_name}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  handleInputChange("last_name", e.target.value)
                }
                required
              />
            </div>

            <Input
              label="Email"
              type="email"
              placeholder="user@ejemplo.com"
              value={formData.email}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                handleInputChange("email", e.target.value)
              }
              required
            />

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Input
                label="Telefono"
                placeholder="3001234567"
                value={formData.phone || ""}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  handleInputChange("phone", e.target.value)
                }
              />
              <Select
                label="Rol"
                placeholder="Selecciona el rol"
                selectedKeys={formData.role ? [formData.role] : []}
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                  handleInputChange("role", e.target.value)
                }
                required
                classNames={{
                  label: "font-medium text-foreground/80",
                  trigger:
                    "min-h-12 border border-divider bg-content1/90 text-foreground shadow-sm dark:bg-content2/80",
                  value: "text-foreground",
                  helperWrapper: "text-surface-muted",
                  description: "text-surface-muted",
                  selectorIcon: "text-surface-muted",
                }}
              >
                {roles.map((role) => (
                  <SelectItem key={role.id} value={role.id} textValue={role.label}>
                    {role.label}
                  </SelectItem>
                ))}
              </Select>
            </div>

            {!isEdit && (
              <Input
                label="Password"
                type="password"
                placeholder="Minimo 6 caracteres"
                value={formData.password}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  handleInputChange("password", e.target.value)
                }
                required
                description="La password debe tener al menos 6 caracteres."
              />
            )}
          </ModalBody>

          <ModalFooter className="flex shrink-0 flex-col-reverse gap-2 border-t border-divider sm:flex-row">
            <Button
              color="default"
              variant="bordered"
              onPress={onClose}
              isDisabled={isLoading}
              className="w-full sm:w-auto"
            >
              Cancel
            </Button>
            <Button
              color="primary"
              variant="solid"
              type="submit"
              isLoading={isLoading}
              className="w-full font-semibold sm:w-auto"
            >
              {isLoading
                ? isEdit
                  ? "Actualizando..."
                  : "Creating..."
                : isEdit
                  ? "Actualizar empleado"
                  : "Create empleado"}
            </Button>
          </ModalFooter>
        </form>
      )}
    </CenteredModal>
  );
};
