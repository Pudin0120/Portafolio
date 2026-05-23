import React, { useRef } from "react";
import { Button, Input } from "@heroui/react";
import { StrategyIcon } from "./StrategyIcon";
import { Edit2 } from "lucide-react";

interface IdentityHeaderProps {
  name: string;
  setName: (name: string) => void;
  strategyName: string;
  materialTypeName?: string;
}

/**
 * Common header for all Material Strategy Forms.
 * Provides a consistent way to view and edit the material name.
 */
export const IdentityHeader: React.FC<IdentityHeaderProps> = ({
  name,
  setName,
  strategyName,
  materialTypeName,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleEditClick = () => {
    inputRef.current?.focus();
    // Optional: select all text on focus
    inputRef.current?.select();
  };

  return (
    <div className="flex items-center justify-between mb-4">
      <div className="p-4 rounded-2xl bg-primary/5 border border-primary/10 flex items-center gap-4 w-full group transition-all hover:bg-primary/10">
        <div className="p-3 bg-content1 rounded-xl shadow-sm border border-default-100 group-hover:scale-105 transition-transform">
          <StrategyIcon strategyName={strategyName} />
        </div>
        <div className="flex-1">
          <p className="text-[10px] uppercase font-black text-primary/50 leading-none mb-1">
            Nombre del material
          </p>
          <Input
            ref={inputRef}
            variant="underlined"
            size="sm"
            value={name}
            onValueChange={setName}
            placeholder={materialTypeName || "Sin nombre"}
            classNames={{
              input: "text-lg font-black text-primary p-0 h-auto min-h-0",
              mainWrapper: "h-auto",
              inputWrapper: "h-auto border-none p-0 group-data-[focus=true]:after:scale-x-100",
            }}
            fullWidth
          />
        </div>
        <Button
          isIconOnly
          size="sm"
          variant="light"
          color="primary"
          className="rounded-full"
          onPress={handleEditClick}
        >
          <Edit2 className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
};
