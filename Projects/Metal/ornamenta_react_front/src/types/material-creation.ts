/**
 * Types and interfaces for material creation
 * Este archivo define las estructuras de datos especificas para cada estrategia de measurement
 */

import { MaterialType, Composition } from "./products";

// ============================================================================
// INTERFACES GENERALES
// ============================================================================

/**
 * Properties base para cualquier material
 */
export interface BaseMaterialProperties {
  material_type_id: string;
  purchase_price_amount: number;
  sale_price_amount?: number;
  purchase_price_currency: string;
  sale_price_currency?: string;
  description?: string;
  barcode?: string;
  sku?: string;
  name?: string;
  image_url?: string; // URL de la imagen en Firebase Storage
}

/**
 * Properties para la estrategia SHEET (Laminas)
 */
export interface SheetMaterialProperties extends BaseMaterialProperties {
  composition_id?: string;
  measurement_strategy: "SHEET" | "sheet";
  properties: {
    thickness?: {
      gauge?: number;
      value?: number;
      unit?: string;
    };
    area?: {
      value: number;
      unit: string;
    };
    width?: {
      value: number;
      unit: string;
    };
    length?: {
      value: number;
      unit: string;
    };
    color?: string;
    brand?: string;
    model?: string;
    part_number?: string;
    [key: string]: any;
  };
}

/**
 * Properties para la estrategia LABOR (Mano de obra)
 */
export interface LaborMaterialProperties extends BaseMaterialProperties {
  measurement_strategy: "LABOR" | "labor";
  properties: {
    unit_type: "linear_meter" | "square_meter";
    length?: {
      value: number;
      unit: string;
    };
    area?: {
      value: number;
      unit: string;
    };
    width?: {
      value: number;
      unit: string;
    };
    height?: {
      value: number;
      unit: string;
    };
    color?: string;
    brand?: string;
    model?: string;
    part_number?: string;
  };
}

/**
 * Properties para la estrategia SOLID (Solidos)
 */
export interface SolidMaterialProperties extends BaseMaterialProperties {
  composition_id?: string;
  measurement_strategy: "SOLID" | "solid";
  properties: {
    mass?: {
      value: number;
      unit: string;
    };
    volume?: {
      value: number;
      unit: string;
    };
    color?: string;
    brand?: string;
    model?: string;
    part_number?: string;
  };
}

/**
 * Properties para la estrategia LIQUID (Liquidos)
 */
export interface LiquidMaterialProperties extends BaseMaterialProperties {
  composition_id?: string;
  measurement_strategy: "LIQUID" | "liquid";
  properties: {
    volume: {
      value: number;
      unit: string;
    };
    color?: string;
    brand?: string;
    model?: string;
    part_number?: string;
    [key: string]: any;
  };
}

/**
 * Properties para la estrategia UNIT (Unidades)
 */
export interface UnitMaterialProperties extends BaseMaterialProperties {
  composition_id?: string;
  measurement_strategy: "UNIT" | "unit";
  properties: {
    color?: string;
    brand?: string;
    model?: string;
    part_number?: string;
    [key: string]: any;
  };
}

/**
 * Properties para la estrategia PROFILE (Perfiles)
 */
export interface ProfileMaterialProperties extends BaseMaterialProperties {
  composition_id?: string;
  measurement_strategy: "PROFILE" | "profile";
  properties: {
    shape: "ROUND" | "RECTANGULAR" | "L_SHAPE" | "FLAT" | "U_SHAPE";
    thickness: {
      gauge?: number;
      value?: number;
      unit?: string;
    };
    diameter?: {
      value: number;
      unit: string;
    };
    width?: {
      value: number;
      unit: string;
    };
    height?: {
      value: number;
      unit: string;
    };
    length: {
      value: number;
      unit: string;
    };
    is_hollow?: boolean;
    color?: string;
    brand?: string;
    model?: string;
    part_number?: string;
    [key: string]: any;
  };
}

/**
 * Configuration de una propiedad en el formulario
 */
export interface PropertyConfig {
  name: string;
  display_name: string;
  type: string;
  required: boolean | "conditional";
  required_if?: string;
  description?: string;
  options?: any;
  unit_dimension?: string;
  preferred_units?: string[];
  default_value?: any;
  default_unit?: string;
  note?: string;
}

/**
 * Configuration de modo de entrada
 */
export interface InputMode {
  mode: string;
  display_name: string;
  description: string;
  recommended?: boolean;
}

/**
 * Configuration de estrategia de measurement
 */
export interface StrategyConfig {
  name: string;
  display_name: string;
  description?: string;
  icon: string;
  input_modes?: InputMode[];
  properties?: PropertyConfig[];
}

/**
 * Material creation form state
 */
export interface MaterialFormState {
  materialTypeId: string;
  compositionId: string;
  measurementStrategy: string;
  purchasePriceAmount: string;
  salePriceAmount: string;
  priceCurrency: string;
  description: string;
  barcode: string;
  sku: string;
  name: string;
  dynamicProperties: Record<string, any>;
  inputMode: string;
}

/**
 * Common props for all material creation components
 */
export interface BaseMaterialCreationProps {
  onSuccess: () => void;
  onCancel: () => void;
  materialTypes: MaterialType[];
  compositions: Composition[];
  availableStrategies: StrategyConfig[];
  isLoading?: boolean;
}

// ============================================================================
// TIPOS UNION
// ============================================================================

/**
 * Union of all possible material properties
 */
export type MaterialProperties =
  | SheetMaterialProperties
  | LaborMaterialProperties
  | SolidMaterialProperties
  | LiquidMaterialProperties
  | UnitMaterialProperties
  | ProfileMaterialProperties;

// ============================================================================
// INTERFACES DE COMPONENTES ESPECIFICOS
// ============================================================================

/**
 * Props para componentes de formulario de estrategias especificas
 */
export interface StrategyFormComponentProps {
  dynamicProperties: Record<string, any>;
  onPropertyChange: (key: string, value: any) => void;
  strategyConfig: StrategyConfig | undefined;
  inputMode: string;
  onInputModeChange: (mode: string) => void;
  shouldShowProperty: (prop: PropertyConfig) => boolean;

  // Coordinator props (optional to allow generic use)
  materialTypeObj?: any;
  compositions?: any[];
  compositionId?: string;
  setCompositionId?: (id: string) => void;
  setShowCreateCompositionModal?: (show: boolean) => void;
  setShowTypeSelector?: (show: boolean) => void;
  barcode?: string;
  setBarcode?: (val: string) => void;
  description?: string;
  setDescription?: (val: string) => void;
  purchasePrice?: string;
  setPurchasePrice?: (val: string) => void;
  salePrice?: string;
  setSalePrice?: (val: string) => void;
  showOptionalIdentity?: boolean;
  setShowOptionalIdentity?: (val: boolean) => void;
  showOptionalTechnicalDetails?: boolean;
  setShowOptionalTechnicalDetails?: (val: boolean) => void;
  name?: string;
  setName?: (val: string) => void;
}

/**
 * Props para el componente de creation de material especifico por estrategia
 */
export interface StrategyMaterialCreationProps {
  onSuccess: () => void;
  onCancel: () => void;
  materialType: MaterialType;
  compositions: Composition[];
  strategyConfig: StrategyConfig;
}

// ============================================================================
// TIPOS DE UTILIDAD
// ============================================================================

/**
 * API response when creating a material
 */
export interface CreateMaterialResponse {
  id: string;
  material_type_id: string;
  composition_id?: string;
  description?: string;
  measurement_strategy: string;
  price_amount: number;
  price_currency: string;
  properties: Record<string, any>;
  created_at: string;
  updated_at: string;
}

/**
 * Error del API
 */
export interface ApiError {
  detail: string | Record<string, any>;
  status?: number;
}

/**
 * Function que valida si las properties del formulario son valid
 */
export type PropertyValidator = (
  properties: Record<string, any>,
  strategyConfig: StrategyConfig,
) => { valid: boolean; errors: string[] };

/**
 * Function que construye el payload para el backend
 */
export type PayloadBuilder = (
  formState: MaterialFormState,
  strategyConfig: StrategyConfig,
) => MaterialProperties;
