import { Material, MeasurementStrategy } from "@/types/products";
import { PropertyConfig, StrategyConfig } from "@/types/material-creation";
import { ProductStrategyFormProps } from "@/types/product-creation";
import React from "react";

export interface ProductStrategy {
  name: string;
  FormComponent: React.FC<ProductStrategyFormProps>;
  getRequiredProperties: (
    strategy: MeasurementStrategy,
    material: Material,
  ) => PropertyConfig[];
  getAvailableUnits: (material: Material) => string[];
  validateDimensions: (
    dimensions: Record<string, any>,
    requiredProperties: PropertyConfig[],
    material: Material,
  ) => { valid: boolean; errors: string[] };
  buildDimensionsPayload: (
    dimensions: Record<string, any>,
    material: Material | null,
  ) => Record<string, any>;
  shouldShowProperty?: (
    prop: PropertyConfig,
    dimensions: Record<string, any>,
    material: Material,
  ) => boolean;
}

export interface ProductStrategyRegistry {
  [key: string]: ProductStrategy;
}
