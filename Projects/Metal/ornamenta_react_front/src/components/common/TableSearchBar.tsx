import React from "react";
import { Search } from "lucide-react";
import { Input } from "@heroui/react";

export type TableSearchBarProps = {
  value: string;
  onValueChange: (value: string) => void;
  placeholder?: string;
  label?: string;
  description?: string;
  className?: string;
};

/**
 * Componente reutilizable de busqueda para tablas
 * Incluye un campo de entrada con icono de busqueda y boton para limpiar
 */
export const TableSearchBar: React.FC<TableSearchBarProps> = ({
  value,
  onValueChange,
  placeholder = "Search...",
  label = "Busqueda",
  description,
  className = "",
}) => {
  return (
    <div className="min-h-[80px]">
      <Input
        isClearable
        value={value}
        onValueChange={onValueChange}
        placeholder={placeholder}
        label={label}
        description={description}
        labelPlacement="outside"
        startContent={<Search className="text-default-400 w-5 h-5" />}
        onClear={() => onValueChange("")}
        className={className}
        aria-label={label}
      />
    </div>
  );
};
