import React, { useMemo } from 'react';
import { Select, SelectItem } from '@heroui/react';
import { MeasurementStrategyInputMode } from '@/types/products';

type InputModeSelectorProps = {
  inputModes: MeasurementStrategyInputMode[];
  selectedMode: string;
  onModeChange: (mode: string) => void;
  label?: string;
  placeholder?: string;
};

export const InputModeSelector: React.FC<InputModeSelectorProps> = ({
  inputModes,
  selectedMode,
  onModeChange,
  label = 'Metodo de entrada',
  placeholder = 'Selecciona un metodo',
}) => {
  const selectedKeys = useMemo(() => {
    return selectedMode ? new Set([selectedMode]) : new Set<string>();
  }, [selectedMode]);

  const handleSelectionChange = (keys: any) => {
    const selected = Array.from(keys)[0] as string;
    onModeChange(selected);
  };

  if (!inputModes || inputModes.length === 0) {
    return null;
  }

  // Solo mostrar si hay mas de un modo
  if (inputModes.length === 1) {
    return null;
  }

  return (
    <Select
      label={label}
      placeholder={placeholder}
      selectedKeys={selectedKeys}
      onSelectionChange={handleSelectionChange}
      description="Como ingresar las dimensiones"
    >
      {inputModes.map((mode) => (
        <SelectItem 
          key={mode.mode} 
          value={mode.mode}
          textValue={mode.display_name}
          description={mode.description}
        >
          <div className="flex flex-col gap-1">
            <span className="font-semibold">{mode.display_name}</span>
            <span className="text-xs text-default-500">{mode.description}</span>
            {mode.recommended && (
              <span className="text-xs text-success font-semibold"> Recomendado</span>
            )}
          </div>
        </SelectItem>
      ))}
    </Select>
  );
};
