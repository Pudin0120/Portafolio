import { useState, useMemo, useEffect } from "react";
import { Material, MeasurementStrategy } from "@/types/products";
import { MaterialSelector } from "./MaterialSelector";
import {
  Button,
  Card,
  CardBody,
  Input,
  Image,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure,
} from "@heroui/react";
import {
  Trash2,
  Plus,
  Box,
  Hash,
  Calculator,
  Package,
} from "lucide-react";
import { ProductStrategySelector } from "./product-creation/strategies/ProductStrategySelector";
import {
  getRequiredPropertiesForProduct,
  getAvailableUnitsForMaterial,
  getDefaultUnitForMaterial,
  validateDimensions,
} from "./product-creation";
import { useAuth } from "@hooks/useAuth";
import { CenteredModal } from "@components/common/CenteredModal";

export interface MaterialRequirement {
  material: Material;
  quantity: number;
  dimensions?: MaterialDimensions;
  finalName?: string;
  calculatedPrices?: {
    purchase: string;
    sale: string;
    currency: string;
  };
}

type DimensionValue =
  | string
  | number
  | {
      value: string | number;
      unit?: string;
    };

type MaterialDimensions = Record<string, DimensionValue | undefined>;

interface MaterialRecipeEditorProps {
  materials: MaterialRequirement[];
  onMaterialsChange: (materials: MaterialRequirement[]) => void;
}

export const MaterialRecipeEditor = ({
  materials,
  onMaterialsChange,
}: MaterialRecipeEditorProps) => {
  const { user } = useAuth();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedMaterial, setSelectedMaterial] = useState<Material | null>(
    null,
  );
  const [selectedId, setSelectedId] = useState("");

  // Estado para dimensiones temporales en la modal
  const [tempDimensions, setTempDimensions] = useState<MaterialDimensions>({});
  const [tempUnit, setTempUnit] = useState("");
  const [measurementStrategies, setMeasurementStrategies] = useState<
    Record<string, MeasurementStrategy>
  >({});

  // Cargar estrategias
  useEffect(() => {
    const fetchStrategies = async () => {
      if (!user) return;
      try {
        const token = await user.getIdToken();
        const res = await fetch(
          `${import.meta.env.VITE_API_URL}/measurement-strategies/`,
          {
            headers: { Authorization: `Bearer ${token}` },
          },
        );
        if (res.ok) {
          const strategiesArray: MeasurementStrategy[] = await res.json();
          const strategiesMap: Record<string, MeasurementStrategy> = {};
          strategiesArray.forEach((s) => {
            strategiesMap[s.name.toUpperCase()] = s;
          });
          setMeasurementStrategies(strategiesMap);
        }
      } catch (err) {
        console.error("Error cargando estrategias:", err);
      }
    };
    fetchStrategies();
  }, [user]);

  const currentStrategy = useMemo(() => {
    if (!selectedMaterial) return null;
    return (
      measurementStrategies[
        selectedMaterial.measurement_strategy.toUpperCase()
      ] || null
    );
  }, [selectedMaterial, measurementStrategies]);

  const requiredProperties = useMemo(() => {
    if (!currentStrategy || !selectedMaterial) return [];
    return getRequiredPropertiesForProduct(currentStrategy, selectedMaterial);
  }, [currentStrategy, selectedMaterial]);

  const availableUnits = useMemo(() => {
    if (!selectedMaterial) return [];
    return getAvailableUnitsForMaterial(selectedMaterial);
  }, [selectedMaterial]);

  // Validacion de dimensiones en tiempo real
  const validation = useMemo(() => {
    if (!selectedMaterial) return { valid: true, errors: [] };
    return validateDimensions(
      { ...tempDimensions, unit: tempUnit },
      requiredProperties,
      selectedMaterial,
    );
  }, [selectedMaterial, tempDimensions, tempUnit, requiredProperties]);

  // Manejar cambio de dimensiones en la modal
  const handleDimensionChange = (key: string, value: DimensionValue) => {
    setTempDimensions((prev) => ({ ...prev, [key]: value }));
  };

  const openConfigModal = (mat: Material) => {
    const strategyName = mat.measurement_strategy.toUpperCase();
    const defaultUnit = getDefaultUnitForMaterial(mat) || "";

    // Si es una estrategia de unidad simple y no tiene properties requeridas, agregar directamente
    if (strategyName === "UNIT" || strategyName === "UNIDADES") {
      const newRequirement: MaterialRequirement = {
        material: mat,
        quantity: 1,
        dimensions: { unit: defaultUnit },
      };
      onMaterialsChange([...materials, newRequirement]);
      setSelectedId("");
      return;
    }

    setSelectedMaterial(mat);
    setTempUnit(defaultUnit);
    setTempDimensions({ unit: defaultUnit });
    onOpen();
  };

  const handleConfirmMaterial = () => {
    if (selectedMaterial && validation.valid) {
      const newRequirement: MaterialRequirement = {
        material: selectedMaterial,
        quantity: 1,
        dimensions: { ...tempDimensions, unit: tempUnit },
      };

      onMaterialsChange([...materials, newRequirement]);
      setSelectedMaterial(null);
      setSelectedId("");
      onClose();
    }
  };

  const removeMaterial = (index: number) => {
    const newMats = [...materials];
    newMats.splice(index, 1);
    onMaterialsChange(newMats);
  };

  const updateQuantity = (index: number, quantity: number) => {
    const newMats = [...materials];
    newMats[index] = { ...newMats[index], quantity: Math.max(0, quantity) };
    onMaterialsChange(newMats);
  };

  const getDimensionDisplayValue = (value: DimensionValue | undefined) => {
    if (value === undefined) {
      return "";
    }

    return typeof value === "object" ? value.value : value;
  };

  return (
    <div className="space-y-4">
      <div className="bg-content2/50 p-4 rounded-2xl border border-default-100 shadow-sm">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-[10px] font-bold text-default-400 uppercase tracking-wider flex items-center gap-2">
            <Box className="w-3.5 h-3.5" /> Seleccion de Materials
          </h4>
        </div>

        <div className="flex gap-2 items-start">
          <div className="flex-1">
            <MaterialSelector
              selectedMaterialId={selectedId}
              onMaterialChange={setSelectedId}
              onMaterialSelect={(mat) => {
                if (mat) openConfigModal(mat);
              }}
              label=""
              placeholder="Search material..."
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-2 max-h-[400px] overflow-y-auto pr-1 custom-scrollbar">
        {materials.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10 bg-default-50/50 rounded-2xl border-2 border-dashed border-default-200 opacity-60">
            <Box className="w-8 h-8 text-default-300 mb-2" />
            <p className="text-[10px] font-bold text-default-400 uppercase tracking-widest text-center">
              Sin materials configurados
            </p>
          </div>
        ) : (
          materials.map((req, idx) => (
            <Card
              key={`${req.material.id}-${idx}`}
              shadow="none"
              className="border border-default-200 bg-background/50 hover:bg-background transition-colors"
            >
              <CardBody className="p-3">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center overflow-hidden rounded-lg border border-surface-border bg-surface-elevated shadow-sm">
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
                      <Package className="w-5 h-5 text-default-300" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-bold truncate text-foreground">
                      {req.material.name}
                    </p>
                    <div className="flex gap-2 mt-1">
                      {req.dimensions &&
                        Object.entries(req.dimensions).map(([k, v]) => {
                          if (k === "mode" || k === "unit" || !v) return null;
                          return (
                            <span
                              key={k}
                              className="text-[9px] bg-primary/10 text-primary px-1.5 py-0.5 rounded font-bold uppercase"
                            >
                              {k}: {getDimensionDisplayValue(v)}
                            </span>
                          );
                        })}
                      <span className="text-[9px] bg-default-100 text-default-500 px-1.5 py-0.5 rounded font-bold uppercase">
                        {getDimensionDisplayValue(req.dimensions?.unit)}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Input
                      type="number"
                      size="sm"
                      variant="flat"
                      value={req.quantity.toString()}
                      onValueChange={(val: string) =>
                        updateQuantity(idx, parseFloat(val) || 0)
                      }
                      className="w-20"
                      classNames={{
                        input: "text-center font-bold",
                        inputWrapper: "h-8",
                      }}
                      startContent={
                        <Hash className="w-3 h-3 text-default-400" />
                      }
                    />
                    <Button
                      isIconOnly
                      color="danger"
                      variant="flat"
                      size="sm"
                      onPress={() => removeMaterial(idx)}
                      aria-label="Delete material"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </div>
              </CardBody>
            </Card>
          ))
        )}
      </div>

      {/* Modal de Configuration de Dimensiones */}
      <CenteredModal
        isOpen={isOpen}
        onOpenChange={onClose}
        size="2xl"
        backdrop="blur"
      >
        {(onCloseModal: () => void) => (
          <>
            <ModalHeader className="border-b border-divider py-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary/10 rounded-xl">
                  <Calculator className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h3 className="text-base font-bold">Medidas del Material</h3>
                  <p className="text-[10px] text-default-400 font-bold uppercase tracking-widest">
                    {selectedMaterial?.name}
                  </p>
                </div>
              </div>
            </ModalHeader>
            <ModalBody className="py-6 px-4 md:px-8">
              <div className="flex flex-col md:flex-row gap-8 items-start">
                {(selectedMaterial?.image_url ||
                  selectedMaterial?.properties?.image_url) && (
                  <div className="w-full md:w-40 flex-shrink-0 animate-in fade-in zoom-in duration-300">
                    <div className="aspect-square rounded-2xl bg-default-50 border border-default-200 p-2 shadow-inner overflow-hidden">
                      <Image
                        src={
                          selectedMaterial.image_url ||
                          selectedMaterial.properties?.image_url
                        }
                        alt={selectedMaterial.name}
                        className="w-full h-full object-contain"
                        radius="lg"
                      />
                    </div>
                  </div>
                )}
                <div className="flex-1 w-full min-w-0">
                  {selectedMaterial && currentStrategy && (
                    <ProductStrategySelector
                      material={selectedMaterial}
                      strategy={currentStrategy}
                      dimensions={tempDimensions}
                      onDimensionChange={handleDimensionChange}
                      requiredProperties={requiredProperties}
                      availableUnits={availableUnits}
                      selectedUnit={tempUnit}
                      onUnitChange={setTempUnit}
                      strategyConfig={undefined}
                    />
                  )}
                </div>
              </div>
            </ModalBody>
            <ModalFooter className="border-t border-divider flex items-center justify-between">
              <div className="flex-1">
                {validation.errors.length > 0 && (
                  <p className="text-[10px] font-bold text-danger uppercase tracking-tighter animate-in fade-in slide-in-from-left-2">
                     {validation.errors[0]}
                  </p>
                )}
              </div>
              <div className="flex gap-2">
                <Button
                  variant="flat"
                  color="default"
                  onPress={onCloseModal}
                  size="sm"
                  className="font-bold"
                >
                  Cancel
                </Button>
                <Button
                  color="primary"
                  onPress={handleConfirmMaterial}
                  size="sm"
                  className="font-bold px-8 shadow-lg shadow-primary/20"
                  startContent={<Plus className="w-4 h-4" />}
                  isDisabled={!validation.valid}
                >
                  Agregar a la Receta
                </Button>
              </div>
            </ModalFooter>
          </>
        )}
      </CenteredModal>
    </div>
  );
};
