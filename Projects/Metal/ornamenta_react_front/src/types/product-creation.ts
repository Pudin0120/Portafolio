/**
 * Types and interfaces for creating products based on materials
 * Products inherit the measurement strategy from their base material
 * y permiten ajustar las dimensiones/medidas especificas
 */

import { Material, MeasurementStrategy } from "./products";
import { StrategyConfig, PropertyConfig } from "./material-creation";

// ============================================================================
// INTERFACES BASE
// ============================================================================

/**
 * Product creation form state
 */
export interface ProductFormState {
  name?: string; // Nombre personalizado (opcional)
  materialId: string;
  dimensions: Record<string, any>; // Dimensiones ajustables segun estrategia
}

/**
 * Configuration derived from the material to create a product
 */
export interface ProductFromMaterialConfig {
  material: Material;
  strategy: MeasurementStrategy;
  strategyConfig?: StrategyConfig;
  requiredProperties: PropertyConfig[];
  availableUnits: string[];
  defaultUnit?: string;
}

/**
 * Props for strategy-based product form components
 */
export interface ProductStrategyFormProps {
  material: Material;
  strategy: MeasurementStrategy;
  strategyConfig?: StrategyConfig;
  dimensions: Record<string, any>;
  onDimensionChange: (key: string, value: any) => void;
  requiredProperties: PropertyConfig[];
  availableUnits: string[];
  selectedUnit: string;
  onUnitChange: (unit: string) => void;
}

/**
 * Base props for product creation
 */
export interface BaseProductCreationProps {
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

// ============================================================================
// DIMENSIONES POR ESTRATEGIA
// ============================================================================

/**
 * Dimensiones estructuradas con valor y unidad
 */
export interface DimensionValue {
  value: number;
  unit: string;
}

/**
 * Dimensions for SHEET-based products
 */
export interface SheetProductDimensions {
  width?: DimensionValue;
  height?: DimensionValue;
  area?: DimensionValue;
}

/**
 * Dimensions for LABOR-based products
 */
export interface LaborProductDimensions {
  unit_type: "linear_meter" | "square_meter";
  length?: DimensionValue;
  width?: DimensionValue;
  height?: DimensionValue;
  area?: DimensionValue;
}

/**
 * Dimensions for SOLID-based products
 */
export interface SolidProductDimensions {
  weight?: DimensionValue;
  volume?: DimensionValue;
  width?: DimensionValue;
  height?: DimensionValue;
  depth?: DimensionValue;
}

/**
 * Dimensions for PROFILE-based products
 */
export interface ProfileProductDimensions {
  length: DimensionValue;
}

/**
 * Union de todas las dimensiones posibles
 */
export type ProductDimensions =
  | SheetProductDimensions
  | LaborProductDimensions
  | SolidProductDimensions
  | ProfileProductDimensions
  | Record<string, DimensionValue | string | number | any>;

/**
 * Material requirement for a simple product recipe
 */
export interface ProductMaterialRequirement {
  material_id: string;
  quantity: number;
  dimensions?: Record<string, any>;
}

/**
 * Payload to create a simple product
 */
export interface CreateSimpleProductPayload {
  name?: string;
  materials?: ProductMaterialRequirement[];
  dimensions?: Record<string, DimensionValue | any>;
  image_url?: string;
  properties?: Record<string, any>;
  purchase_price_override?: number;
  sale_price_override?: number;
}

/**
 * Simple product simulation response
 */
export interface SimulateSimpleProductResponse {
  name: string;
  description: string;
  purchase_price: string;
  sale_price: string;
  currency: string;
  materials: any[];
  dimensions_summary: any;
  properties: any;
}

/**
 * API response when creating a product
 */
export interface CreateProductResponse {
  id: string;
  name: string;
  description: string;
  product_type: string;
  material_id: string;
  material_name: string;
  dimensions: Record<string, any>;
  price?: number;
  currency?: string;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// VALIDADORES Y BUILDERS
// ============================================================================

/**
 * Function que valida las dimensiones segun la estrategia
 */
export type DimensionValidator = (
  dimensions: Record<string, any>,
  strategy: MeasurementStrategy,
  material: Material,
) => { valid: boolean; errors: string[] };

/**
 * Function que construye el payload de dimensiones para el backend
 */
export type DimensionPayloadBuilder = (
  dimensions: Record<string, any>,
  strategy: MeasurementStrategy,
  material: Material,
) => Record<string, any>;
