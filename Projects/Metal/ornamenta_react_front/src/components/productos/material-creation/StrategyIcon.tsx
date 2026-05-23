/**
 * Componentes de iconos para estrategias de measurement
 */

import React from "react";
import { STRATEGY_ICONS, DEFAULT_ICON } from "./strategies/icons";

interface StrategyIconProps {
  strategyName: string;
  className?: string;
}

/**
 * Obtiene el icono apropiado para una estrategia de measurement
 */
export const StrategyIcon: React.FC<StrategyIconProps> = ({
  strategyName,
  className = "w-8 h-8 text-primary",
}) => {
  const IconComponent =
    STRATEGY_ICONS[strategyName?.toUpperCase()] || DEFAULT_ICON;
  return <IconComponent className={className} />;
};
