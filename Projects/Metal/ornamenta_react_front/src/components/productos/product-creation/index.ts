/**
 * Exportaciones centralizadas para product-creation
 */

// Utilidades
export * from "./utils";

// Componentes de campos
export * from "./FormFields";

// Estrategias
export { ProductStrategySelector } from "./strategies/ProductStrategySelector";
export { SheetProductForm } from "./strategies/SheetProductForm";
export { LaborProductForm } from "./strategies/LaborProductForm";
export { SolidProductForm } from "./strategies/SolidProductForm";
export { GenericProductForm } from "./strategies/GenericProductForm";
