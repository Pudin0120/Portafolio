/**
 * Componente selector que renderiza el formulario apropiado segun la estrategia de measurement
 */

import React from "react";
import { StrategyFormComponentProps } from "@/types/material-creation";
import { getMaterialStrategy, getDefaultMaterialStrategy } from "./registry";

interface StrategyPropertiesProps extends StrategyFormComponentProps {
  measurementStrategy: string;
}

/**
 * Selecciona y renderiza el componente de formulario apropiado segun la estrategia
 */
export const StrategyProperties: React.FC<StrategyPropertiesProps> = ({
  measurementStrategy,
  ...props
}) => {
  if (!props.strategyConfig) return null;

  const strategy =
    getMaterialStrategy(measurementStrategy) || getDefaultMaterialStrategy();
  const { FormComponent } = strategy;

  return <FormComponent {...props} />;
};
