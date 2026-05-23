// Product Types
export type ProductComponent = {
  product_id: string;
  product_name: string;
  product_type: string;
  quantity: number;
  order_index: number;
};

export type Product = {
  id: string;
  name: string;
  description: string;
  product_type: string;
  material_id: string;
  material_name: string;
  measurement_strategy?: string; // Estrategia de measurement del material (e.g., 'LIQUID', 'LINEAR', 'AREA', 'VOLUME')
  valid_dimensions?: string[]; // Lista de dimensiones valid para este material
  dimensions: Record<string, unknown> | null;
  components: ProductComponent[];
  image_url?: string | null;
  price?: number | string; // Calculated product price (optional, depends on the backend)
  purchase_price?: number | string;
  purchase_price_currency?: string;
  sale_price?: number | string;
  sale_price_currency?: string;
  currency?: string; // Price currency
  last_calculation_audit?: Record<string, unknown> | null;
};

export type ProductsResponse = {
  products: Product[];
  total: number;
};

// Material Types
export type Material = {
  id: string;
  material_type_id: string;
  material_type_name: string;
  material_type_unit_id?: string;
  material_type_unit_name?: string;
  material_type_unit_symbol?: string;
  name: string;
  description: string | null;
  measurement_strategy: string;
  price_amount: string; // Legacy field, keeping for compatibility
  price_currency: string;
  purchase_price_amount: string;
  purchase_price_currency: string;
  sale_price_amount: string;
  sale_price_currency: string;
  sku: string;
  barcode: string | null;
  image_url: string | null;
  properties: Record<string, any>;
  composition_id: string | null;
  composition_name: string | null;
  is_deleted?: boolean;
  deleted_at?: string | null;
  composition?: {
    id: string;
    name: string;
  };
};

export type MaterialsResponse = {
  materials: Material[];
  total: number;
};

// Tipos de Material
export type MaterialType = {
  id: string;
  name: string;
  description: string;
  measurement_strategy: string;
  requires_composition?: boolean;
};

export type MaterialTypesResponse = {
  material_types: MaterialType[];
  total: number;
};

// Unidades de Medida
export type UnitMeasure = {
  id: string;
  name: string;
  symbol: string;
  pint_unit_text: string;
  dimension: string;
};

export type UnitMeasuresResponse = {
  units: UnitMeasure[];
  total: number;
};

// Tipos de Composiciones
export type Composition = {
  id: string;
  name: string;
  description?: string;
};

export type CompositionsResponse =
  | Composition[]
  | {
      compositions?: Composition[];
      materials?: Composition[];
      total?: number;
    };

// Estrategias de Medicion
export type MeasurementStrategyProperty = {
  name: string;
  display_name: string;
  type: string;
  required: boolean | string;
  required_if?: string;
  description: string;
  unit_dimension?: string;
  preferred_units?: string[];
  options?: Record<string, unknown>;
  examples?: unknown[];
  default_value?: unknown;
  default_unit?: string;
  material_property?: boolean;
  note?: string;
};

export type MeasurementStrategyInputMode = {
  mode: string;
  display_name: string;
  description: string;
  recommended: boolean;
};

export type MeasurementStrategyExample = {
  description: string;
  mode?: string;
  properties: Record<string, unknown>;
};

export type MeasurementStrategy = {
  name: string;
  display_name: string;
  description: string;
  icon: string;
  input_modes?: MeasurementStrategyInputMode[];
  properties: MeasurementStrategyProperty[];
  calculation: {
    formula: string;
    result_unit: string;
    description: string;
  };
  examples: MeasurementStrategyExample[];
};

export type MeasurementStrategySummary = {
  name: string;
  display_name: string;
  description: string;
  icon: string;
};

export type MeasurementStrategiesResponse = MeasurementStrategy[];
export type MeasurementStrategiesSummaryResponse = MeasurementStrategySummary[];
