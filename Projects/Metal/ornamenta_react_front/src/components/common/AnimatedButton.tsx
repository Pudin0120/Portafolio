import React from "react";
import { Button } from "@heroui/react";

/**
 * Boton con estilos mejorados que respetan el tema dinamico del sistema.
 * Utiliza variables CSS (--primary-500, --secondary-500, etc.) calculadas en ThemeContext.
 */
export const AnimatedButton: React.FC<any> = ({
  children,
  variant = "primary",
  className = "",
  ...props
}) => {
  const baseClasses =
    "transition-all duration-200 hover:scale-105 active:scale-95 font-bold shadow-sm";

  const variantClasses: Record<string, string> = {
    // Usamos las variables del theme dinamico en lugar de brand-orange hardcodeado
    primary: "bg-primary text-primary-foreground hover:opacity-90",
    secondary: "bg-secondary text-secondary-foreground hover:opacity-90",
    danger: "bg-danger text-danger-foreground hover:opacity-90",
  };

  return (
    <Button
      className={`${baseClasses} ${variantClasses[variant] || ""} ${className}`}
      {...props}
    >
      {children}
    </Button>
  );
};

/**
 * Boton de accion principal (Dinamico)
 */
export const PrimaryButton: React.FC<any> = (props) => (
  <AnimatedButton variant="primary" {...props} />
);

/**
 * Boton de accion secundaria (Dinamico)
 */
export const SecondaryButton: React.FC<any> = (props) => (
  <AnimatedButton variant="secondary" {...props} />
);

/**
 * Boton de accion peligrosa (Dinamico)
 */
export const DangerButton: React.FC<any> = (props) => (
  <AnimatedButton variant="danger" {...props} />
);
