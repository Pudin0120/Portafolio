import React, { useState } from "react";
import {
  Card,
  CardBody,
  CardHeader,
  Input,
  Textarea,
  Button,
  Divider,
  Spinner,
} from "@heroui/react";
import { Client } from "@/types/clients";
import { Work, CreateWorkRequest } from "@/types/works";
import { workService } from "@services/workService";
import { PrimaryButton, StatusMessage } from "@components/common";

interface QuotationStep1Props {
  selectedClient: Client;
  onWorkCreated?: (work: Work) => void;
  isLoading?: boolean;
}

export const QuotationStep1: React.FC<QuotationStep1Props> = ({
  selectedClient,
  onWorkCreated,
  isLoading = false,
}) => {
  const [formData, setFormData] = useState<CreateWorkRequest>({
    client_identification: selectedClient.identification_number,
    work_name: "",
    description: "",
    tax: 0.15,
    end_aprox_delivery_date: "",
    deposit_amount: 0,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = e.target;

    if (name === "tax") {
      // El user ingresa 15 para 15%, guardamos 0.15 para el back
      const numericValue = parseFloat(value) || 0;
      setFormData((prev) => ({
        ...prev,
        [name]: numericValue / 100,
      }));
    } else if (name === "deposit_amount") {
      setFormData((prev) => ({
        ...prev,
        [name]: value ? parseFloat(value) : 0,
      }));
    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    }
  };

  const handleSubmit = async () => {
    setError(null);
    setSuccess(null);

    // Validacion basica
    if (!formData.work_name?.trim()) {
      setError("El nombre del work es obligatorio");
      return;
    }

    if (formData.work_name.length < 3) {
      setError("El nombre del work debe tener al menos 3 caracteres");
      return;
    }

    if ((formData.tax ?? 0) < 0 || (formData.tax ?? 0) > 1) {
      setError("El porcentaje de ganancia debe estar entre 0% y 100%");
      return;
    }

    try {
      setIsSubmitting(true);
      const newWork = await workService.createWork(formData);
      setSuccess("Quotation created exitosamente");
      onWorkCreated?.(newWork);

      // Reset form
      setFormData({
        client_identification: selectedClient.identification_number,
        work_name: "",
        description: "",
        tax: 0.15,
        end_aprox_delivery_date: "",
        deposit_amount: 0,
      });
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Error al create la quotation";
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const taxPercentage = Math.round((formData.tax ?? 0) * 100);

  return (
    <Card className="border-none shadow-sm bg-content1">
      <CardHeader className="flex flex-col items-start px-6 py-4 bg-primary/5">
        <h2 className="text-xl font-semibold text-primary">
          Paso 2: Informacion de la Quotation
        </h2>
        <p className="text-sm text-default-500 mt-1">
          Completa los datos basicos de la quotation
        </p>
      </CardHeader>
      <Divider className="bg-divider" />
      <CardBody className="gap-6 p-6">
        {error && <StatusMessage type="error">{error}</StatusMessage>}

        {success && <StatusMessage type="success">{success}</StatusMessage>}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-default-400 uppercase tracking-wider font-bold mb-1">
              Client
            </p>
            <p className="text-lg font-semibold text-foreground">
              {selectedClient.first_name} {selectedClient.last_name}
            </p>
          </div>
          <div>
            <p className="text-xs text-default-400 uppercase tracking-wider font-bold mb-1">
              Document
            </p>
            <p className="text-lg font-semibold text-foreground">
              {selectedClient.document_type} -{" "}
              {selectedClient.identification_number}
            </p>
          </div>
        </div>

        <Divider />

        <div className="space-y-6">
          <Input
            label="Nombre del Work"
            name="work_name"
            placeholder="Ej: Ornamentacion para casa de Don Alexander Hernandez"
            variant="bordered"
            value={formData.work_name}
            onChange={handleInputChange}
            isDisabled={isSubmitting}
            isRequired
            minLength={3}
            maxLength={255}
            classNames={{
              label: "font-semibold",
            }}
          />

          <Textarea
            label="Description"
            name="description"
            placeholder="Describe en detalle el work a realizar"
            variant="bordered"
            value={formData.description || ""}
            onChange={handleInputChange}
            isDisabled={isSubmitting}
            maxLength={2000}
            minRows={3}
            maxRows={6}
            classNames={{
              label: "font-semibold",
            }}
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Porcentaje de Ganancia (%)"
              name="tax"
              type="number"
              variant="bordered"
              value={Math.round((formData.tax ?? 0) * 100).toString()}
              onChange={handleInputChange}
              isDisabled={isSubmitting}
              min={0}
              max={100}
              step={1}
              description="Porcentaje de rentabilidad sobre el costo total"
              classNames={{
                label: "font-semibold",
              }}
            />

            <Input
              label="Deposito inicial (opcional)"
              name="deposit_amount"
              type="number"
              variant="bordered"
              placeholder="0"
              value={formData.deposit_amount?.toString() || "0"}
              onChange={handleInputChange}
              isDisabled={isSubmitting}
              min={0}
              startContent={
                <div className="pointer-events-none flex items-center">
                  <span className="text-default-400 text-small">$</span>
                </div>
              }
              classNames={{
                label: "font-semibold",
              }}
            />
          </div>

          <div className="w-full">
            <Input
              label="Fecha Estimada de Entrega (opcional)"
              name="end_aprox_delivery_date"
              type="datetime-local"
              variant="bordered"
              placeholder="dd/mm/aaaa"
              value={formData.end_aprox_delivery_date || ""}
              onChange={handleInputChange}
              isDisabled={isSubmitting}
              className="cursor-pointer"
              classNames={{
                label: "font-semibold",
              }}
            />
          </div>
        </div>

        <Divider />

        <PrimaryButton
          onPress={handleSubmit}
          size="lg"
          isLoading={isSubmitting || isLoading}
          isDisabled={isSubmitting || isLoading || !formData.work_name.trim()}
          className="w-full shadow-md font-bold"
        >
          {isSubmitting ? "CREANDO COTIZACION..." : "CREAR COTIZACION"}
        </PrimaryButton>
      </CardBody>
    </Card>
  );
};

export default QuotationStep1;
