import React, { useCallback } from "react";
import { Input } from "@heroui/react";
import { BarcodeScannerButton } from "./BarcodeScannerButton";

type BarcodeInputProps = Omit<
  React.ComponentProps<typeof Input>,
  "onValueChange"
> & {
  value: string;
  onValueChange: (value: string) => void;
};

export const BarcodeInput: React.FC<BarcodeInputProps> = ({
  value,
  onValueChange,
  endContent,
  ...props
}) => {
  const handleDetected = useCallback(
    (detectedValue: string) => onValueChange(detectedValue),
    [onValueChange],
  );

  return (
    <Input
      {...props}
      value={value}
      onValueChange={onValueChange}
      endContent={
        <div className="flex items-center gap-1">
          {endContent}
          <BarcodeScannerButton onDetected={handleDetected} />
        </div>
      }
    />
  );
};
