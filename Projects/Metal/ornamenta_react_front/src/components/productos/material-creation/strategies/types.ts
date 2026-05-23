import React from "react";
import {
  MaterialFormState,
  StrategyConfig,
  MaterialProperties,
  StrategyFormComponentProps,
} from "@/types/material-creation";
import { Material } from "@/types/products";

export interface MaterialStrategy {
  name: string;
  icon: React.ElementType;
  requiresGauge: boolean;
  isSimpleUnit?: boolean;
  FormComponent: React.FC<StrategyFormComponentProps>;
  payloadBuilder: (
    formState: MaterialFormState,
    strategyConfig: StrategyConfig,
  ) => MaterialProperties;
  materialToFormMapper?: (
    material: Material,
    strategyConfig: StrategyConfig | undefined,
  ) => Record<string, any>;
}

export interface MaterialStrategyRegistry {
  [key: string]: MaterialStrategy;
}
