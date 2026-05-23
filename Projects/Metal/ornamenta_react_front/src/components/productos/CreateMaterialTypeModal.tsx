import React, { useEffect, useState, useMemo } from "react";
import {
  Hammer,
  Table,
  Droplets,
  Package,
  Square,
  Grid3x3,
  Ruler,
} from "lucide-react";
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
  Switch,
} from "@heroui/react";
import {
  MeasurementStrategy,
  MeasurementStrategiesResponse,
} from "@/types/products";

// Helper function to get strategy icon
const getStrategyIcon = (strategyName: string) => {
  switch (strategyName?.toUpperCase()) {
    case "LABOR":
      return <Hammer className="w-5 h-5 text-primary" />;
    case "SHEET":
      return <Table className="w-5 h-5 text-secondary" />;
    case "LIQUID":
      return <Droplets className="w-5 h-5 text-warning" />;
    case "VOLUME":
      return <Package className="w-5 h-5 text-secondary" />;
    case "LENGTH":
      return <Ruler className="w-5 h-5 text-success" />;
    case "AREA":
      return <Square className="w-5 h-5 text-warning" />;
    default:
      return <Ruler className="w-5 h-5 text-default-400" />;
  }
};

type CreateMaterialTypeModalProps = {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  onSuccess?: (newType: any) => void;
  initialName?: string;
};

export const CreateMaterialTypeModal: React.FC<
  CreateMaterialTypeModalProps
> = ({ isOpen, onOpenChange, onSuccess, initialName = "" }) => {
  const { user } = useAuth();
  const [isSaving, setIsSaving] = useState(false);
  const [isLoadingStrategies, setIsLoadingStrategies] = useState(false);
  const [error, setError] = useState("");
  const [measurementStrategies, setMeasurementStrategies] = useState<
    MeasurementStrategy[]
  >([]);

  // Form state
  const [name, setName] = useState(initialName);
  const [description, setDescription] = useState("");
  const [showDescription, setShowDescription] = useState(false);
  const [measurementStrategy, setMeasurementStrategy] = useState("");

  // Update name when initialName changes or modal opens
  useEffect(() => {
    if (isOpen && initialName) {
      setName(initialName);
    }
  }, [isOpen, initialName]);

  const selectedStrategyKeys = useMemo(() => {
    return measurementStrategy
      ? new Set([measurementStrategy])
      : new Set<string>();
  }, [measurementStrategy]);

  // Cargar estrategias de measurement
  useEffect(() => {
    const fetchStrategies = async () => {
      if (!user || !isOpen) return;
      setIsLoadingStrategies(true);
      try {
        const strategiesData = await apiClient.get<MeasurementStrategiesResponse>(
          "/measurement-strategies/",
        );
        if (strategiesData) {
          setMeasurementStrategies(strategiesData || []);
        }
      } catch (err) {
        console.error("Error al cargar estrategias de measurement:", err);
      } finally {
        setIsLoadingStrategies(false);
      }
    };

    fetchStrategies();
  }, [user, isOpen]);

  const resetForm = () => {
    setName("");
    setDescription("");
    setMeasurementStrategy("");
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
      const newMaterialType = await apiClient.post<any>(
        "/material-types/",
        {
          name,
          description,
          measurement_strategy: measurementStrategy,
        },
      );

      resetForm();
      onOpenChange(false);

      // OK MEJORADO: Pasar el nuevo tipo de material al callback
      // Esto permite al padre seleccionar automaticamente el nuevo tipo
      if (onSuccess) {
        onSuccess(newMaterialType);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      console.error("ERROR Error al create tipo de material:", message);
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
              Nuevo Tipo de Material
            </h2>
            <p className="text-xs text-default-500 font-normal">
              Define la categoria y como se medira este material.
            </p>
          </ModalHeader>
          <ModalBody>
            <form onSubmit={handleSubmit} className="space-y-4 pb-4">
              {error && (
                <div className="rounded-md bg-danger/20 p-3 text-sm text-danger border border-danger/30">
                  {error}
                </div>
              )}

              <div className="grid grid-cols-1 gap-4">
                <Input
                  label="Nombre"
                  placeholder="Ej: Lamina Metalica"
                  value={name}
                  onValueChange={setName}
                  isRequired
                  variant="bordered"
                />

                <Select
                  label="Estrategia de Medicion"
                  placeholder={
                    isLoadingStrategies
                      ? "Cargando..."
                      : "Selecciona como se mide"
                  }
                  selectedKeys={selectedStrategyKeys}
                  onSelectionChange={(keys: any) => {
                    const selected = Array.from(keys)[0];
                    setMeasurementStrategy(selected as string);
                  }}
                  isRequired
                  variant="bordered"
                  isDisabled={isLoadingStrategies}
                >
                  {measurementStrategies.map((strategy) => (
                    <SelectItem
                      key={strategy.name}
                      value={strategy.name}
                      textValue={strategy.display_name}
                      startContent={getStrategyIcon(strategy.name)}
                    >
                      <div className="flex flex-col">
                        <span className="text-sm font-medium">
                          {strategy.display_name}
                        </span>
                        <span className="text-tiny text-default-400">
                          {strategy.description}
                        </span>
                      </div>
                    </SelectItem>
                  ))}
                </Select>
              </div>

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
                  placeholder="Para que sirve este tipo de material..."
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
                  type="button"
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
                  isDisabled={!name || !measurementStrategy}
                  className="font-semibold"
                  size="sm"
                >
                  Create Tipo
                </Button>
              </div>
            </form>
          </ModalBody>
        </>
      )}
    </CenteredModal>
  );
};
