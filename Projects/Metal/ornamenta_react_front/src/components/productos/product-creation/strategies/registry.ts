import { ProductStrategyRegistry } from "./types";
import { SheetProductForm } from "./SheetProductForm";
import { LaborProductForm } from "./LaborProductForm";
import { SolidProductForm } from "./SolidProductForm";
import { GenericProductForm } from "./GenericProductForm";
import { ProfileProductForm } from "./ProfileProductForm";
import {
  getRequiredPropertiesForSheet,
  getRequiredPropertiesForLabor,
  getRequiredPropertiesForSolid,
  getRequiredPropertiesForLiquid,
  getRequiredPropertiesForProfile,
  getRequiredPropertiesForUnit,
  getRequiredPropertiesGeneric,
  getAvailableUnitsForSheet,
  getAvailableUnitsForLabor,
  getAvailableUnitsForSolid,
  getAvailableUnitsForLiquid,
  getAvailableUnitsForProfile,
  getAvailableUnitsForUnit,
  getAvailableUnitsGeneric,
  validateDimensionsSheet,
  validateDimensionsLabor,
  validateDimensionsSolid,
  validateDimensionsLiquid,
  validateDimensionsProfile,
  validateDimensionsUnit,
  validateDimensionsGeneric,
  buildDimensionsPayloadSheet,
  buildDimensionsPayloadLabor,
  buildDimensionsPayloadSolid,
  buildDimensionsPayloadProfile,
  buildDimensionsPayloadUnit,
  buildDimensionsPayloadGeneric,
  shouldShowPropertySheet,
  shouldShowPropertySolid,
  shouldShowPropertyGeneric,
} from "./strategy-functions";

export const PRODUCT_STRATEGY_REGISTRY: ProductStrategyRegistry = {
  SHEET: {
    name: "SHEET",
    FormComponent: SheetProductForm,
    getRequiredProperties: getRequiredPropertiesForSheet,
    getAvailableUnits: getAvailableUnitsForSheet,
    validateDimensions: validateDimensionsSheet,
    buildDimensionsPayload: buildDimensionsPayloadSheet,
    shouldShowProperty: shouldShowPropertySheet,
  },
  PROFILE: {
    name: "PROFILE",
    FormComponent: ProfileProductForm,
    getRequiredProperties: getRequiredPropertiesForProfile,
    getAvailableUnits: getAvailableUnitsForProfile,
    validateDimensions: validateDimensionsProfile,
    buildDimensionsPayload: buildDimensionsPayloadProfile,
  },
  LABOR: {
    name: "LABOR",
    FormComponent: LaborProductForm,
    getRequiredProperties: getRequiredPropertiesForLabor,
    getAvailableUnits: getAvailableUnitsForLabor,
    validateDimensions: validateDimensionsLabor,
    buildDimensionsPayload: buildDimensionsPayloadLabor,
  },
  SOLID: {
    name: "SOLID",
    FormComponent: SolidProductForm,
    getRequiredProperties: getRequiredPropertiesForSolid,
    getAvailableUnits: getAvailableUnitsForSolid,
    validateDimensions: validateDimensionsSolid,
    buildDimensionsPayload: buildDimensionsPayloadSolid,
    shouldShowProperty: shouldShowPropertySolid,
  },
  LIQUID: {
    name: "LIQUID",
    FormComponent: GenericProductForm,
    getRequiredProperties: getRequiredPropertiesForLiquid,
    getAvailableUnits: getAvailableUnitsForLiquid,
    validateDimensions: validateDimensionsLiquid,
    buildDimensionsPayload: buildDimensionsPayloadGeneric,
  },
  UNIT: {
    name: "UNIT",
    FormComponent: GenericProductForm,
    getRequiredProperties: getRequiredPropertiesForUnit,
    getAvailableUnits: getAvailableUnitsForUnit,
    validateDimensions: validateDimensionsUnit,
    buildDimensionsPayload: buildDimensionsPayloadUnit,
  },
  UNIDADES: {
    name: "UNIT",
    FormComponent: GenericProductForm,
    getRequiredProperties: getRequiredPropertiesForUnit,
    getAvailableUnits: getAvailableUnitsForUnit,
    validateDimensions: validateDimensionsUnit,
    buildDimensionsPayload: buildDimensionsPayloadUnit,
  },
};

export const getProductStrategy = (name: string) => {
  return PRODUCT_STRATEGY_REGISTRY[name.toUpperCase()] || null;
};

export const getDefaultProductStrategy = () => ({
  name: "GENERIC",
  FormComponent: GenericProductForm,
  getRequiredProperties: getRequiredPropertiesGeneric,
  getAvailableUnits: getAvailableUnitsGeneric,
  validateDimensions: validateDimensionsGeneric,
  buildDimensionsPayload: buildDimensionsPayloadGeneric,
  shouldShowProperty: shouldShowPropertyGeneric,
});
