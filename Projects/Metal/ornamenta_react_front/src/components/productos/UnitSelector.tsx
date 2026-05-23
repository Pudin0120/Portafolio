import React, { useMemo } from 'react';
import { Select, SelectItem } from '@heroui/react';

type UnitSelectorProps = {
  availableUnits: string[];
  selectedUnit: string;
  onUnitChange: (unit: string) => void;
  label?: string;
  placeholder?: string;
  isRequired?: boolean;
  description?: string;
};

export const UnitSelector: React.FC<UnitSelectorProps> = ({
  availableUnits,
  selectedUnit,
  onUnitChange,
  label = 'Unidad de Medida',
  placeholder = 'Selecciona una unidad',
  isRequired = false,
  description,
}) => {
  const selectedKeys = useMemo(() => {
    return selectedUnit ? new Set([selectedUnit]) : new Set<string>();
  }, [selectedUnit]);

  const handleSelectionChange = (keys: any) => {
    const selected = Array.from(keys)[0] as string;
    onUnitChange(selected);
  };

  return (
    <Select
      label={label}
      placeholder={availableUnits.length === 0 ? 'No hay unidades disponibles' : placeholder}
      selectedKeys={selectedKeys}
      onSelectionChange={handleSelectionChange}
      isRequired={isRequired}
      description={description || `${availableUnits.length} unidad(es) disponible(s)`}
    >
      {availableUnits.length > 0 ? (
        availableUnits.map((unit) => (
          <SelectItem 
            key={unit} 
            value={unit}
            textValue={unit}
          >
            {unit}
          </SelectItem>
        ))
      ) : (
        <SelectItem key="empty" value="" textValue="Sin unidades">
          No hay unidades disponibles
        </SelectItem>
      )}
    </Select>
  );
};
