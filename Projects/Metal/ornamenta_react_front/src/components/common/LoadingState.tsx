import React from "react";
import { Spinner } from "@heroui/react";

interface LoadingStateProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

/**
 * Estado de carga profesional con feedback visual
 * Cumple con heuristica #1: Visibility of system status
 */
export const LoadingState: React.FC<LoadingStateProps> = ({ 
  message = "Cargando...",
  size = "md",
  className = "",
}) => {
  return (
    <div className={`flex flex-col items-center justify-center py-12 ${className}`}>
      <Spinner 
        size={size}
        classNames={{
          circle1: "border-b-brand-orange-600",
          circle2: "border-b-brand-teal-600",
        }}
      />
      {message && (
        <p className="mt-4 text-sm text-gray-600 animate-pulse">{message}</p>
      )}
    </div>
  );
};
