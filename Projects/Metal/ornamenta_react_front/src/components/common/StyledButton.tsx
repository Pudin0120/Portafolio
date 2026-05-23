import React from "react";
import { Button } from "@heroui/react";

interface StyledButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?:
    | "solid"
    | "bordered"
    | "light"
    | "flat"
    | "faded"
    | "shadow"
    | "ghost";
  colorScheme?:
    | "primary"
    | "secondary"
    | "success"
    | "warning"
    | "danger"
    | "default";
  isLoading?: boolean;
  isDisabled?: boolean;
  size?: "sm" | "md" | "lg";
  startContent?: React.ReactNode;
  endContent?: React.ReactNode;
}

/**
 * Boton estandarizado que utiliza las clases semanticas de HeroUI
 * Las cuales estan mapeadas a las variables CSS dinamicas en ThemeContext.
 */
export const StyledButton: React.FC<any> = ({
  children,
  variant = "solid",
  colorScheme = "primary",
  className = "",
  ...props
}) => {
  // Mapeo directo a los colores semanticos de HeroUI que ya estan personalizados por el theme
  const herouiColor = colorScheme;

  return (
    <Button
      color={herouiColor as any}
      variant={variant}
      className={className}
      {...props}
    >
      {children}
    </Button>
  );
};

/**
 * Wrapper para mensajes de estado estandarizados
 * Utiliza variables de color del sistema (primary, success, danger, warning)
 */
export const StatusMessage: React.FC<{
  type: "success" | "error" | "warning" | "info";
  children: React.ReactNode;
  className?: string;
}> = ({ type, children, className = "" }) => {
  const styles = {
    success:
      "bg-success/10 border-success/20 text-success-700 dark:text-success-400",
    error: "bg-danger/10 border-danger/20 text-danger-700 dark:text-danger-400",
    warning:
      "bg-warning/10 border-warning/20 text-warning-700 dark:text-warning-400",
    info: "bg-primary/10 border-primary/20 text-primary-700 dark:text-primary-400",
  };

  return (
    <div
      className={`rounded-xl px-4 py-3 border backdrop-blur-sm ${styles[type]} ${className}`}
    >
      {children}
    </div>
  );
};

/**
 * Boton de accion principal (Dinamico)
 */
export const PrimaryButton: React.FC<any> = (props) => {
  return <StyledButton colorScheme="primary" {...props} />;
};

/**
 * Boton de accion secundaria (Dinamico)
 */
export const SecondaryButton: React.FC<any> = (props) => {
  return <StyledButton colorScheme="secondary" {...props} />;
};

/**
 * Boton de exito (Dinamico)
 */
export const SuccessButton: React.FC<any> = (props) => {
  return <StyledButton colorScheme="success" {...props} />;
};

/**
 * Boton de peligro/delete (Dinamico)
 */
export const DangerButton: React.FC<any> = (props) => {
  return <StyledButton colorScheme="danger" {...props} />;
};
