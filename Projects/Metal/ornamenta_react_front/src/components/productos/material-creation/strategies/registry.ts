import { Table, Hammer, Box, Droplets, Ruler } from "lucide-react";
import type { MaterialStrategyRegistry } from "./types";
import { SheetMaterialForm } from "./SheetMaterialForm";
import { ProfileMaterialForm } from "./ProfileMaterialForm";
import { LaborMaterialForm } from "./LaborMaterialForm";
import { SolidMaterialForm } from "./SolidMaterialForm";
import { LiquidMaterialForm } from "./LiquidMaterialForm";
import { UnitMaterialForm } from "./UnitMaterialForm";
import { GenericStrategyForm } from "./GenericStrategyForm";
import {
  buildSheetPayload,
  buildLaborPayload,
  buildSolidPayload,
  buildLiquidPayload,
  buildUnitPayload,
  buildProfilePayload,
  buildGenericPayload,
} from "../payloadBuilders";
import {
  mapSheetToForm,
  mapLiquidToForm,
  mapProfileToForm,
  mapSolidToForm,
  mapLaborToForm,
  mapUnitToForm,
  mapGenericToForm,
} from "./mappers";

const REGISTRY: MaterialStrategyRegistry = {
  SHEET: {
    name: "SHEET",
    icon: Table,
    requiresGauge: true,
    FormComponent: SheetMaterialForm,
    payloadBuilder: buildSheetPayload,
    materialToFormMapper: mapSheetToForm,
  },
  PROFILE: {
    name: "PROFILE",
    icon: Hammer,
    requiresGauge: true,
    FormComponent: ProfileMaterialForm,
    payloadBuilder: buildProfilePayload,
    materialToFormMapper: mapProfileToForm,
  },
  LABOR: {
    name: "LABOR",
    icon: Hammer,
    requiresGauge: false,
    FormComponent: LaborMaterialForm,
    payloadBuilder: buildLaborPayload,
    materialToFormMapper: mapLaborToForm,
  },
  SOLID: {
    name: "SOLID",
    icon: Box,
    requiresGauge: false,
    FormComponent: SolidMaterialForm,
    payloadBuilder: buildSolidPayload,
    materialToFormMapper: mapSolidToForm,
  },
  LIQUID: {
    name: "LIQUID",
    icon: Droplets,
    requiresGauge: false,
    FormComponent: LiquidMaterialForm,
    payloadBuilder: buildLiquidPayload,
    materialToFormMapper: mapLiquidToForm,
  },
  LINEAR: {
    name: "LINEAR",
    icon: Ruler,
    requiresGauge: false,
    FormComponent: GenericStrategyForm,
    payloadBuilder: buildGenericPayload,
    materialToFormMapper: mapGenericToForm,
  },
  UNIT: {
    name: "UNIT",
    icon: Box,
    requiresGauge: false,
    isSimpleUnit: true,
    FormComponent: UnitMaterialForm,
    payloadBuilder: buildUnitPayload,
    materialToFormMapper: mapUnitToForm,
  },
};

export const MATERIAL_STRATEGY_REGISTRY = REGISTRY;

export const getMaterialStrategy = (name: string) => {
  return REGISTRY[name?.toUpperCase()] || null;
};

export const getDefaultMaterialStrategy = () => {
  return REGISTRY.UNIT;
};

export const isCompositionCompatible = (
  strategyName: string | undefined,
): boolean => {
  if (!strategyName) return true;

  const strategy = strategyName.toUpperCase();
  // Caso especial: LABOR no suele requerir composicion
  if (strategy === "LABOR") return true;

  return true;
};
