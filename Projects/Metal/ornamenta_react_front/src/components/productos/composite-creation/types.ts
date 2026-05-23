/**
 * Types para creation de products compuestos con relaciones dimensionales
 */

import { Product } from "@/types/products";

// Regla dimensional para un eje (width, height, depth)
export type DimensionalRule = {
  reference_type: "parent" | "fixed";
  parent_dimension?: "width" | "height" | "depth";
  fixed_value?: number;
  unit?: string; // 'mm' por defecto
};

// Configuration de relacion dimensional completa
export type ComponentRelationship = {
  width_rule?: DimensionalRule;
  height_rule?: DimensionalRule;
  depth_rule?: DimensionalRule;
  quantity_type: "fixed" | "perimeter" | "area";
  base_quantity: number;
  quantity_multiplier?: number; // Default 1
};

// Componente en el formulario (con info completa del product)
export type CompositeComponentForm = {
  product_id: string;
  product: Product; // Product completo (para preview)
  base_quantity: number;
  relationship: ComponentRelationship;
};

// Dimensiones del product compuesto
export type CompositeDimensions = {
  width: number; // mm
  height: number; // mm
  depth?: number; // mm (opcional)
};

// Estado del formulario completo
export type CompositeFormState = {
  name: string;
  description: string;
  dimensions: CompositeDimensions;
  components: CompositeComponentForm[];
  image_url?: string;
  properties?: Record<string, string>; // Key-value pairs
};

// Componente calculado (response del backend)
export type CalculatedComponent = {
  product_id: string;
  product_name: string;
  base_quantity: number;
  calculated_quantity: number;
  calculated_dimensions: Record<string, number>;
  is_snapshot: boolean;
  purchase_price: string;
  sale_price: string;
  // Para compuestos anidados:
  components?: CalculatedComponent[]; // Recursivo
};

// Response de simulacion (desde backend)
export type SimulateCompositeResponse = {
  id?: string;
  name: string;
  description: string;
  dimensions: CompositeDimensions;
  is_composite: true;
  components: CalculatedComponent[];
  total_purchase_price: string;
  total_sale_price: string;
  created_at?: string;
  updated_at?: string;
};

// Payload para creation (lo que enviamos al POST)
export type CreateCompositeProductPayload = {
  name: string;
  description: string;
  dimensions: CompositeDimensions;
  components: Array<{
    product_id: string;
    base_quantity: number;
    relationship: ComponentRelationship;
  }>;
  image_url?: string;
  properties?: Record<string, string>;
};
