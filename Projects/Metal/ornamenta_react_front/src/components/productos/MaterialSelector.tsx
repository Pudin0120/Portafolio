import React, { useEffect, useState, useMemo } from "react";
import { Package, Ruler, Plus } from "lucide-react";
import { useAuth } from "@hooks/useAuth";
import { apiClient } from "@services/apiClient";
import { formatPrice } from "@/utils";
import {
  Select,
  SelectItem,
  Spinner,
  Button,
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  Image,
} from "@heroui/react";
import { Material } from "@/types/products";
import { TableSearchBar } from "@components/common/TableSearchBar";
import { CenteredModal } from "@components/common/CenteredModal";
import { CreateMaterialModal } from "./CreateMaterialModal";
import { FileImage } from "lucide-react";

type MaterialsResponse = {
  materials: Material[];
  total: number;
};

type MaterialSelectorProps = {
  selectedMaterialId: string;
  onMaterialChange: (materialId: string) => void;
  onMaterialSelect: (material: Material | null) => void;
  label?: string;
  placeholder?: string;
  isRequired?: boolean;
};

export const MaterialSelector: React.FC<MaterialSelectorProps> = ({
  selectedMaterialId,
  onMaterialChange,
  onMaterialSelect,
  label = "Material",
  placeholder = "Selecciona un material",
  isRequired = false,
}) => {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [materials, setMaterials] = useState<Material[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);

  const selectedKeys = useMemo(() => {
    return selectedMaterialId
      ? new Set([selectedMaterialId])
      : new Set<string>();
  }, [selectedMaterialId]);

  const fetchMaterials = React.useCallback(async () => {
    if (!user) return;
    setIsLoading(true);
    try {
      const data: MaterialsResponse = await apiClient.get("/materials/");
      setMaterials(data.materials || []);
    } catch (err) {
      console.error("Error al cargar materials:", err);
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchMaterials();
  }, [fetchMaterials]);

  // Filtrar materials segun busqueda
  const filteredMaterials = useMemo(() => {
    if (!searchQuery.trim()) return materials;

    const query = searchQuery.toLowerCase();
    return materials.filter(
      (m) =>
        m.name?.toLowerCase().includes(query) ||
        m.description?.toLowerCase().includes(query) ||
        m.material_type_name?.toLowerCase().includes(query) ||
        m.measurement_strategy?.toLowerCase().includes(query),
    );
  }, [materials, searchQuery]);

  const handleSelectionChange = (keys: any) => {
    const selected = Array.from(keys)[0] as string;
    onMaterialChange(selected);

    const material = materials.find((m) => m.id === selected);
    onMaterialSelect(material || null);
  };

  const handleMaterialCreated = () => {
    setShowCreateModal(false);
    fetchMaterials(); // Recargar la lista de materials
  };

  if (isLoading) {
    return (
      <div className="flex items-center gap-2">
        <Spinner size="sm" />
        <span className="text-sm text-default-500">Cargando materials...</span>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-3">
        <div className="flex items-center justify-between gap-3">
          <div className="flex-1">
            <TableSearchBar
              value={searchQuery}
              onValueChange={setSearchQuery}
              placeholder="Search por nombre, description, tipo o estrategia..."
              label="Search materials"
            />
          </div>
          <Button
            color="primary"
            variant="solid"
            size="sm"
            onPress={() => setShowCreateModal(true)}
            className="shrink-0 font-semibold"
            startContent={<Plus className="w-4 h-4" />}
          >
            Nuevo Material
          </Button>
        </div>

        <Select
          label={label}
          placeholder={
            filteredMaterials.length === 0
              ? "No hay materials disponibles"
              : placeholder
          }
          selectedKeys={selectedKeys}
          onSelectionChange={handleSelectionChange}
          isRequired={isRequired}
          description={`${filteredMaterials.length} material(es) disponible(s)`}
        >
          {filteredMaterials.length > 0 ? (
            filteredMaterials.map((mat) => (
              <SelectItem
                key={mat.id}
                value={mat.id}
                textValue={`${mat.name} - ${mat.description}`}
              >
                <div className="flex items-center gap-3 py-1">
                  {/* Thumbnail */}
                  <div className="flex-shrink-0">
                    {mat.image_url || mat.properties?.image_url ? (
                      <Image
                        src={
                          (mat.image_url || mat.properties?.image_url) as string
                        }
                        alt={mat.name}
                        width={32}
                        height={32}
                        className="object-cover rounded shadow-sm"
                      />
                    ) : (
                      <div className="w-8 h-8 rounded bg-default-100 flex items-center justify-center text-default-400">
                        <FileImage className="w-4 h-4" />
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col flex-1">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-semibold">{mat.name}</span>
                      <span className="text-xs font-semibold text-primary">
                        $
                        {formatPrice(
                          parseFloat(
                            mat.sale_price_amount ||
                              mat.purchase_price_amount ||
                              mat.price_amount,
                          ),
                        )}{" "}
                        {mat.sale_price_currency ||
                          mat.purchase_price_currency ||
                          mat.price_currency}
                      </span>
                    </div>
                    <div className="text-xs text-default-500 flex items-center gap-2">
                      <span className="flex items-center gap-1">
                        <Package className="w-3 h-3" /> {mat.material_type_name}
                      </span>
                      <span></span>
                      <span className="flex items-center gap-1">
                        <Ruler className="w-3 h-3" /> {mat.measurement_strategy}
                      </span>
                    </div>
                  </div>
                </div>
              </SelectItem>
            ))
          ) : (
            <SelectItem key="empty" value="" textValue="No hay materials">
              No hay materials{" "}
              {searchQuery ? "que coincidan con la busqueda" : "disponibles"}
            </SelectItem>
          )}
        </Select>
      </div>

      <CreateMaterialModal
        isOpen={showCreateModal}
        onOpenChange={setShowCreateModal}
        onSuccess={handleMaterialCreated}
      />
    </>
  );
};
