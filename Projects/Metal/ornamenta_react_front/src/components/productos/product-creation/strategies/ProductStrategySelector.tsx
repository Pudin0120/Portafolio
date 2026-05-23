/**
 * Selector de estrategia que renderiza el formulario apropiado segun el material
 */

import React from "react";
import { ProductStrategyFormProps } from "@/types/product-creation";
import { getProductStrategy, getDefaultProductStrategy } from "./registry";

export const ProductStrategySelector: React.FC<ProductStrategyFormProps> = (
  props,
) => {
  const { material } = props;
  const strategy =
    getProductStrategy(material.measurement_strategy) ||
    getDefaultProductStrategy();
  const { FormComponent } = strategy;

  return <FormComponent {...props} />;
};
