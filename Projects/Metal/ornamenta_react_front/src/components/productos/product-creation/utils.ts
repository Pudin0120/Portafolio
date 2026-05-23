import { Material, MeasurementStrategy } from "@/types/products";
import { PropertyConfig } from "@/types/material-creation";
import {
  getProductStrategy,
  getDefaultProductStrategy,
} from "./strategies/registry";

/**
 * Obtiene las properties requeridas para create un product segun la estrategia del material
 */
export const getRequiredPropertiesForProduct = (
  strategy: MeasurementStrategy,
  material: Material,
): PropertyConfig[] => {
  const s = getProductStrategy(strategy.name) || getDefaultProductStrategy();
  return s.getRequiredProperties(strategy, material);
};

/**
 * Obtiene las unidades disponibles para un material segun su estrategia
 */
export const getAvailableUnitsForMaterial = (material: Material): string[] => {
  const s =
    getProductStrategy(material.measurement_strategy) ||
    getDefaultProductStrategy();
  return s.getAvailableUnits(material);
};

/**
 * Obtiene la unidad por defecto para un material
 */
export const getDefaultUnitForMaterial = (
  material: Material,
): string | undefined => {
  const availableUnits = getAvailableUnitsForMaterial(material);
  return availableUnits[0];
};

/**
 * Valida que las dimensiones proporcionadas sean valid
 */
export const validateDimensions = (
  dimensions: Record<string, any>,
  requiredProperties: PropertyConfig[],
  material: Material,
): { valid: boolean; errors: string[] } => {
  const errors: string[] = [];

  if (!dimensions.unit) {
    errors.push("Debe seleccionar una unidad de medida");
  }

  const s =
    getProductStrategy(material.measurement_strategy) ||
    getDefaultProductStrategy();
  const validation = s.validateDimensions(
    dimensions,
    requiredProperties,
    material,
  );

  return {
    valid: errors.length === 0 && validation.valid,
    errors: [...errors, ...validation.errors],
  };
};

/**
 * Construye el payload de dimensiones para enviar al backend con el nuevo formato estructurado
 */
export const buildDimensionsPayload = (
  dimensions: Record<string, any>,
  material: Material | null,
): Record<string, any> => {
  if (!material) return dimensions;

  const s =
    getProductStrategy(material.measurement_strategy) ||
    getDefaultProductStrategy();
  return s.buildDimensionsPayload(dimensions, material);
};

/**
 * Determina si una propiedad debe mostrarse segun el contexto
 */
export const shouldShowPropertyForProduct = (
  prop: PropertyConfig,
  dimensions: Record<string, any>,
  material: Material,
): boolean => {
  const s =
    getProductStrategy(material.measurement_strategy) ||
    getDefaultProductStrategy();
  if (s.shouldShowProperty) {
    return s.shouldShowProperty(prop, dimensions, material);
  }
  return true;
};
