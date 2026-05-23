/**
 * Exportaciones centralizadas para los componentes de creation de materials
 */

// Componentes de formulario por estrategia
export { SheetMaterialForm } from "./strategies/SheetMaterialForm";
export { ProfileMaterialForm } from "./strategies/ProfileMaterialForm";
export { LaborMaterialForm } from "./strategies/LaborMaterialForm";
export { SolidMaterialForm } from "./strategies/SolidMaterialForm";
export { LiquidMaterialForm } from "./strategies/LiquidMaterialForm";
export { GenericStrategyForm } from "./strategies/GenericStrategyForm";
export { StrategyProperties } from "./strategies/StrategyProperties";

// Componentes de campos reutilizables
export { MeasurementField, PropertyLabel } from "./FormFields";

// Utilidades
export * from "./utils";
export * from "./payloadBuilders";
export * from "./mappers";
export * from "./useMaterialForm";
