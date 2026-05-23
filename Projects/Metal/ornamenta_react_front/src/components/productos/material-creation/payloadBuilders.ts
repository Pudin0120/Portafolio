/**
 * Constructores de payload para cada estrategia de measurement
 * Cada builder transforma las properties del formulario al formato esperado por el backend
 */

import {
  StrategyConfig,
  MaterialFormState,
  SheetMaterialProperties,
  LaborMaterialProperties,
  SolidMaterialProperties,
  LiquidMaterialProperties,
  UnitMaterialProperties,
  ProfileMaterialProperties,
  MaterialProperties,
} from "@/types/material-creation";
import { denormalizeUnit, isValidNumber } from "./utils";

/**
 * Construye el payload para la estrategia SHEET
 */
export const buildSheetPayload = (
  formState: MaterialFormState,
  strategyConfig: StrategyConfig,
): SheetMaterialProperties => {
  const { dynamicProperties } = formState;
  const properties: SheetMaterialProperties["properties"] = {};

  // Construir thickness anidado
  const thicknessType = dynamicProperties["thickness_type"] || "gauge";
  if (thicknessType === "gauge") {
    const gaugeValue = dynamicProperties["thickness_gauge"];
    if (isValidNumber(gaugeValue)) {
      properties.thickness = {
        gauge: parseInt(String(gaugeValue)),
      };
    }
  } else if (thicknessType === "measurement") {
    const value = dynamicProperties["thickness_value"];
    const unit = denormalizeUnit(dynamicProperties["thickness_unit"] || "mm");
    if (isValidNumber(value)) {
      properties.thickness = {
        value: parseFloat(String(value)),
        unit: unit,
      };
    }
  }

  // Manejo de dimensiones vs area segun el inputMode
  if (formState.inputMode === "dimensions") {
    const widthValue = dynamicProperties["width_value"];
    const widthUnit = denormalizeUnit(dynamicProperties["width_unit"] || "m");
    const lengthValue = dynamicProperties["length_value"];
    const lengthUnit = denormalizeUnit(dynamicProperties["length_unit"] || "m");

    if (isValidNumber(widthValue) && isValidNumber(lengthValue)) {
      properties.width = {
        value: parseFloat(String(widthValue)),
        unit: widthUnit,
      };
      properties.length = {
        value: parseFloat(String(lengthValue)),
        unit: lengthUnit,
      };
    }
  } else {
    // Modo area_direct o por defecto
    const areaValue = dynamicProperties["area_value"];
    const areaUnit = denormalizeUnit(dynamicProperties["area_unit"] || "m");
    if (isValidNumber(areaValue)) {
      properties.area = {
        value: parseFloat(String(areaValue)),
        unit: areaUnit,
      };
    }
  }

  return {
    material_type_id: formState.materialTypeId,
    composition_id: formState.compositionId || undefined,
    description: formState.description || undefined,
    name: formState.name || undefined,
    barcode: formState.barcode || undefined,
    measurement_strategy: "SHEET",
    purchase_price_amount: parseFloat(formState.purchasePriceAmount),
    purchase_price_currency: formState.priceCurrency,
    sale_price_amount: formState.salePriceAmount
      ? parseFloat(formState.salePriceAmount)
      : undefined,
    sale_price_currency: formState.priceCurrency,
    properties: {
      ...properties,
      color: dynamicProperties["color"] || undefined,
      brand: dynamicProperties["brand"] || undefined,
      model: dynamicProperties["model"] || undefined,
      part_number: dynamicProperties["part_number"] || undefined,
    },
    image_url: (dynamicProperties["image_url"] as string) || undefined,
  };
};

/**
 * Construye el payload para la estrategia LABOR
 */
export const buildLaborPayload = (
  formState: MaterialFormState,
  strategyConfig: StrategyConfig,
): LaborMaterialProperties => {
  const { dynamicProperties } = formState;
  const unitType = dynamicProperties["unit_type"] || "linear_meter";
  const properties: LaborMaterialProperties["properties"] = {
    unit_type: unitType,
    color: dynamicProperties["color"] || undefined,
    brand: dynamicProperties["brand"] || undefined,
    model: dynamicProperties["model"] || undefined,
    part_number: dynamicProperties["part_number"] || undefined,
  };

  // Manejo de medidas segun el tipo de unidad
  if (unitType === "square_meter") {
    // Si es por area, intentamos dimensiones o area directa
    if (formState.inputMode === "dimensions") {
      const widthValue = dynamicProperties["width_value"];
      const widthUnit = denormalizeUnit(dynamicProperties["width_unit"] || "m");
      const lengthValue = dynamicProperties["length_value"];
      const lengthUnit = denormalizeUnit(
        dynamicProperties["length_unit"] || "m",
      );

      if (isValidNumber(widthValue) && isValidNumber(lengthValue)) {
        properties.width = {
          value: parseFloat(String(widthValue)),
          unit: widthUnit,
        };
        properties.length = {
          value: parseFloat(String(lengthValue)),
          unit: lengthUnit,
        };
      }
    } else {
      const areaValue = dynamicProperties["area_value"];
      const areaUnit = denormalizeUnit(dynamicProperties["area_unit"] || "m");
      if (isValidNumber(areaValue)) {
        properties.area = {
          value: parseFloat(String(areaValue)),
          unit: areaUnit,
        };
      }
    }
  } else if (unitType === "linear_meter") {
    // Si es por metro lineal, intentamos el largo
    const lengthValue = dynamicProperties["length_value"];
    const lengthUnit = denormalizeUnit(dynamicProperties["length_unit"] || "m");
    if (isValidNumber(lengthValue)) {
      properties.length = {
        value: parseFloat(String(lengthValue)),
        unit: lengthUnit,
      };
    }
  }

  return {
    material_type_id: formState.materialTypeId,
    description: formState.description || undefined,
    name: formState.name || undefined,
    barcode: formState.barcode || undefined,
    purchase_price_amount: parseFloat(formState.purchasePriceAmount),
    purchase_price_currency: formState.priceCurrency,
    sale_price_amount: formState.salePriceAmount
      ? parseFloat(formState.salePriceAmount)
      : undefined,
    sale_price_currency: formState.priceCurrency,
    measurement_strategy: "LABOR",
    properties,
    image_url: (dynamicProperties["image_url"] as string) || undefined,
  };
};

/**
 * Construye el payload para la estrategia SOLID
 */
export const buildSolidPayload = (
  formState: MaterialFormState,
  strategyConfig: StrategyConfig,
): SolidMaterialProperties => {
  const { dynamicProperties } = formState;
  const properties: SolidMaterialProperties["properties"] = {
    color: dynamicProperties["color"] || undefined,
    brand: dynamicProperties["brand"] || undefined,
    model: dynamicProperties["model"] || undefined,
    part_number: dynamicProperties["part_number"] || undefined,
  };

  // Prioridad: weight (masa) primero, luego volume
  const massValue = dynamicProperties["mass_value"];
  const massUnit = denormalizeUnit(dynamicProperties["mass_unit"] || "kg");

  if (isValidNumber(massValue)) {
    properties.mass = {
      value: parseFloat(massValue),
      unit: massUnit,
    };
  } else {
    // Si no hay masa, intentar volumen
    const volumeValue = dynamicProperties["volume_value"];
    const volumeUnit = denormalizeUnit(dynamicProperties["volume_unit"] || "L");

    if (isValidNumber(volumeValue)) {
      properties.volume = {
        value: parseFloat(volumeValue),
        unit: volumeUnit,
      };
    }
  }

  return {
    material_type_id: formState.materialTypeId,
    composition_id: formState.compositionId || undefined,
    description: formState.description || undefined,
    name: formState.name || undefined,
    barcode: formState.barcode || undefined,
    measurement_strategy: "SOLID",
    purchase_price_amount: parseFloat(formState.purchasePriceAmount),
    purchase_price_currency: formState.priceCurrency,
    sale_price_amount: formState.salePriceAmount
      ? parseFloat(formState.salePriceAmount)
      : undefined,
    sale_price_currency: formState.priceCurrency,
    properties,
    image_url: (dynamicProperties["image_url"] as string) || undefined,
  };
};

/**
 * Construye el payload para la estrategia LIQUID
 */
export const buildLiquidPayload = (
  formState: MaterialFormState,
  strategyConfig: StrategyConfig,
): LiquidMaterialProperties => {
  const { dynamicProperties } = formState;

  const volumeValue = dynamicProperties["volume_value"];
  const volumeUnit = denormalizeUnit(dynamicProperties["volume_unit"] || "L");

  return {
    material_type_id: formState.materialTypeId,
    composition_id: formState.compositionId || undefined,
    description: formState.description || undefined,
    name: formState.name || undefined,
    barcode: formState.barcode || undefined,
    measurement_strategy: "LIQUID",
    purchase_price_amount: parseFloat(formState.purchasePriceAmount),
    purchase_price_currency: formState.priceCurrency,
    sale_price_amount: formState.salePriceAmount
      ? parseFloat(formState.salePriceAmount)
      : undefined,
    sale_price_currency: formState.priceCurrency,
    properties: {
      volume: {
        value: parseFloat(volumeValue),
        unit: volumeUnit,
      },
      color: dynamicProperties["color"] || undefined,
      brand: dynamicProperties["brand"] || undefined,
      model: dynamicProperties["model"] || undefined,
      part_number: dynamicProperties["part_number"] || undefined,
    },
    image_url: (dynamicProperties["image_url"] as string) || undefined,
  };
};

/**
 * Construye el payload para la estrategia UNIT
 */
export const buildUnitPayload = (
  formState: MaterialFormState,
  _strategyConfig: StrategyConfig,
): UnitMaterialProperties => {
  const { dynamicProperties } = formState;

  return {
    material_type_id: formState.materialTypeId,
    composition_id: formState.compositionId || undefined,
    description: formState.description || undefined,
    name: formState.name || undefined,
    barcode: formState.barcode || undefined,
    measurement_strategy: "UNIT",
    purchase_price_amount: parseFloat(formState.purchasePriceAmount),
    purchase_price_currency: formState.priceCurrency,
    sale_price_amount: formState.salePriceAmount
      ? parseFloat(formState.salePriceAmount)
      : undefined,
    sale_price_currency: formState.priceCurrency,
    properties: {
      color: dynamicProperties["color"] || undefined,
      brand: dynamicProperties["brand"] || undefined,
      model: dynamicProperties["model"] || undefined,
      part_number: dynamicProperties["part_number"] || undefined,
    },
    image_url: (dynamicProperties["image_url"] as string) || undefined,
  };
};

/**
 * Construye el payload generico para estrategias no especificas
 */
export const buildGenericPayload = (
  formState: MaterialFormState,
  strategyConfig: StrategyConfig,
): any => {
  const { dynamicProperties } = formState;
  const properties: Record<string, any> = {};

  if (!strategyConfig.properties) return properties;

  strategyConfig.properties.forEach((prop) => {
    const propKey = prop.name;

    if (prop.type === "gauge_or_measurement") {
      const type = dynamicProperties[`${propKey}_type`] || "gauge";

      if (type === "gauge") {
        const gaugeValue = dynamicProperties[`${propKey}_gauge`];
        if (isValidNumber(gaugeValue)) {
          properties[propKey] = {
            gauge: parseInt(gaugeValue),
          };
        }
      } else {
        const mmValue = dynamicProperties[`${propKey}_mm`];
        const unit = dynamicProperties[`${propKey}_unit`] || "mm";
        if (isValidNumber(mmValue)) {
          properties[propKey] = {
            value: parseFloat(mmValue),
            unit: unit,
          };
        }
      }
    } else if (prop.type === "measurement") {
      const value = dynamicProperties[`${propKey}_value`];
      const unit = denormalizeUnit(
        dynamicProperties[`${propKey}_unit`] || prop.default_unit,
      );

      if (isValidNumber(value)) {
        properties[propKey] = {
          value: parseFloat(value),
          unit: unit,
        };
      }
    } else if (prop.type === "number") {
      const value = dynamicProperties[propKey];
      if (isValidNumber(value)) {
        properties[propKey] = parseFloat(value);
      }
    } else if (prop.type === "text") {
      const value = dynamicProperties[propKey];
      if (value !== undefined && value !== null && value !== "") {
        properties[propKey] = value;
      }
    }
  });

  return {
    material_type_id: formState.materialTypeId,
    composition_id: formState.compositionId || undefined,
    description: formState.description || undefined,
    name: formState.name || undefined,
    barcode: formState.barcode || undefined,
    measurement_strategy: formState.measurementStrategy.toUpperCase(),
    purchase_price_amount: parseFloat(formState.purchasePriceAmount),
    purchase_price_currency: formState.priceCurrency,
    sale_price_amount: formState.salePriceAmount
      ? parseFloat(formState.salePriceAmount)
      : undefined,
    sale_price_currency: formState.priceCurrency,
    properties: {
      ...properties,
    },
    image_url: (dynamicProperties["image_url"] as string) || undefined,
  };
};

/**
 * Construye el payload para la estrategia PROFILE
 */
export const buildProfilePayload = (
  formState: MaterialFormState,
  _strategyConfig: StrategyConfig,
): ProfileMaterialProperties => {
  const { dynamicProperties } = formState;
  const properties: any = {
    shape: dynamicProperties["shape"],
    is_hollow: dynamicProperties["is_hollow"],
  };

  // thickness
  const thicknessType = dynamicProperties["thickness_type"] || "measurement";
  if (thicknessType === "gauge") {
    const gaugeValue = dynamicProperties["thickness_gauge"];
    if (isValidNumber(gaugeValue)) {
      properties.thickness = {
        gauge: parseInt(String(gaugeValue)),
      };
    }
  } else {
    const value = dynamicProperties["thickness_value"];
    const unit = denormalizeUnit(dynamicProperties["thickness_unit"] || "mm");
    if (isValidNumber(value)) {
      properties.thickness = {
        value: parseFloat(String(value)),
        unit: unit,
      };
    }
  }

  // diameter
  if (properties.shape === "ROUND") {
    const diamValue = dynamicProperties["diameter_value"];
    const diamUnit = denormalizeUnit(
      dynamicProperties["diameter_unit"] || "mm",
    );
    if (isValidNumber(diamValue)) {
      properties.diameter = {
        value: parseFloat(String(diamValue)),
        unit: diamUnit,
      };
    }
  }

  // width
  if (properties.shape !== "ROUND") {
    const widthValue = dynamicProperties["width_value"];
    const widthUnit = denormalizeUnit(dynamicProperties["width_unit"] || "mm");
    if (isValidNumber(widthValue)) {
      properties.width = {
        value: parseFloat(String(widthValue)),
        unit: widthUnit,
      };
    }
  }

  // height
  if (["RECTANGULAR", "L_SHAPE", "U_SHAPE"].includes(properties.shape)) {
    const heightValue = dynamicProperties["height_value"];
    const heightUnit = denormalizeUnit(
      dynamicProperties["height_unit"] || "mm",
    );
    if (isValidNumber(heightValue)) {
      properties.height = {
        value: parseFloat(String(heightValue)),
        unit: heightUnit,
      };
    }
  }

  // length
  const lengthValue = dynamicProperties["length_value"];
  const lengthUnit = denormalizeUnit(dynamicProperties["length_unit"] || "m");
  if (isValidNumber(lengthValue)) {
    properties.length = {
      value: parseFloat(String(lengthValue)),
      unit: lengthUnit,
    };
  }

  return {
    material_type_id: formState.materialTypeId,
    composition_id: formState.compositionId || undefined,
    description: formState.description || undefined,
    name: formState.name || undefined,
    barcode: formState.barcode || undefined,
    measurement_strategy: "PROFILE",
    purchase_price_amount: parseFloat(formState.purchasePriceAmount),
    purchase_price_currency: formState.priceCurrency,
    sale_price_amount: formState.salePriceAmount
      ? parseFloat(formState.salePriceAmount)
      : undefined,
    sale_price_currency: formState.priceCurrency,
    properties: {
      ...properties,
      color: dynamicProperties["color"] || undefined,
      brand: dynamicProperties["brand"] || undefined,
      model: dynamicProperties["model"] || undefined,
      part_number: dynamicProperties["part_number"] || undefined,
    },
    image_url: (dynamicProperties["image_url"] as string) || undefined,
  };
};

/**
 * Construye el payload apropiado segun la estrategia de measurement
 */
export const buildMaterialPayload = (
  formState: MaterialFormState,
  strategyConfig: StrategyConfig,
): MaterialProperties => {
  // Use a map or direct lookup instead of registry to avoid circular dependency
  const strategy = formState.measurementStrategy.toUpperCase();

  switch (strategy) {
    case "SHEET":
      return buildSheetPayload(formState, strategyConfig);
    case "PROFILE":
      return buildProfilePayload(formState, strategyConfig);
    case "LABOR":
      return buildLaborPayload(formState, strategyConfig);
    case "SOLID":
      return buildSolidPayload(formState, strategyConfig);
    case "LIQUID":
      return buildLiquidPayload(formState, strategyConfig);
    case "UNIT":
      return buildUnitPayload(formState, strategyConfig);
    default:
      return buildGenericPayload(formState, strategyConfig);
  }
};
