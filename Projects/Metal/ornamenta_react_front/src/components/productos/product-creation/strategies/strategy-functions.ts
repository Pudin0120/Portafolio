import { Material, MeasurementStrategy } from "@/types/products";
import { PropertyConfig } from "@/types/material-creation";

// ============================================================================
// ESTRATEGIA: SHEET
// ============================================================================

export const getRequiredPropertiesForSheet = (): PropertyConfig[] => [
  {
    name: "area",
    display_name: "Area",
    type: "measurement",
    required: false,
    description: "Area total de la lamina",
    note: "Opcional si especificas ancho y largo",
  },
  {
    name: "width",
    display_name: "Ancho",
    type: "measurement",
    required: false,
    description: "Ancho de la lamina",
  },
  {
    name: "length",
    display_name: "Largo",
    type: "measurement",
    required: false,
    description: "Largo de la lamina",
  },
];

export const getAvailableUnitsForSheet = () => ["m", "cm", "ft", "in"];

export const validateDimensionsSheet = (dimensions: Record<string, any>) => {
  const errors: string[] = [];
  const hasArea = dimensions.area && parseFloat(dimensions.area) > 0;
  const hasWidthHeight =
    dimensions.width &&
    parseFloat(dimensions.width) > 0 &&
    dimensions.height &&
    parseFloat(dimensions.height) > 0;

  if (!hasArea && !hasWidthHeight) {
    errors.push("Debe especificar area O ancho y alto");
  }
  return { valid: errors.length === 0, errors };
};

export const buildDimensionsPayloadSheet = (
  dimensions: Record<string, any>,
) => {
  const payload: Record<string, any> = {};
  const toDim = (val: any, unit: string) => {
    const num = parseFloat(String(val));
    return isNaN(num) ? undefined : { value: num, unit };
  };
  const getUnit = (key: string) => dimensions[`${key}_unit`] || dimensions.unit;

  if (dimensions.area) {
    payload.area = toDim(dimensions.area, getUnit("area"));
  } else if (dimensions.width && dimensions.height) {
    payload.width = toDim(dimensions.width, getUnit("width"));
    payload.height = toDim(dimensions.height, getUnit("height"));
  }
  return payload;
};

export const shouldShowPropertySheet = (
  prop: PropertyConfig,
  dimensions: Record<string, any>,
) => {
  if ((prop.name === "width" || prop.name === "length") && dimensions.area) {
    return true;
  }
  if (prop.name === "area" && (dimensions.width || dimensions.length)) {
    return true;
  }
  return true;
};

// ============================================================================
// ESTRATEGIA: LABOR
// ============================================================================

export const getRequiredPropertiesForLabor = (
  _strategy: MeasurementStrategy,
  material: Material,
): PropertyConfig[] => {
  const properties: PropertyConfig[] = [];
  const unitType = material.properties?.unit_type as string;

  if (unitType === "linear_meter") {
    properties.push({
      name: "length",
      display_name: "Longitud",
      type: "measurement",
      required: true,
      description: "Longitud del work",
    });
  } else if (unitType === "square_meter") {
    properties.push(
      {
        name: "width",
        display_name: "Ancho",
        type: "measurement",
        required: true,
        description: "Ancho del area de work",
      },
      {
        name: "height",
        display_name: "Alto",
        type: "measurement",
        required: true,
        description: "Alto del area de work",
      },
    );
  }
  return properties;
};

export const getAvailableUnitsForLabor = (material: Material) => {
  const unitType = material.properties?.unit_type as string;
  if (unitType === "linear_meter") return ["m", "cm", "ft", "mm"];
  if (unitType === "square_meter") return ["m", "cm", "ft"];
  return ["m", "cm", "mm"];
};

export const validateDimensionsLabor = (
  dimensions: Record<string, any>,
  _requiredProperties: PropertyConfig[],
  material: Material,
) => {
  const errors: string[] = [];
  const unitType = material.properties?.unit_type as string;

  if (unitType === "linear_meter") {
    if (!dimensions.length || parseFloat(dimensions.length) <= 0) {
      errors.push("Debe especificar la longitud");
    }
  } else if (unitType === "square_meter") {
    if (!dimensions.width || parseFloat(dimensions.width) <= 0) {
      errors.push("Debe especificar el ancho");
    }
    if (!dimensions.height || parseFloat(dimensions.height) <= 0) {
      errors.push("Debe especificar el alto");
    }
  }
  return { valid: errors.length === 0, errors };
};

export const buildDimensionsPayloadLabor = (
  dimensions: Record<string, any>,
  material: Material | null,
) => {
  const payload: Record<string, any> = {};
  const toDim = (val: any, unit: string) => {
    const num = parseFloat(String(val));
    return isNaN(num) ? undefined : { value: num, unit };
  };
  const getUnit = (key: string) => dimensions[`${key}_unit`] || dimensions.unit;

  const laborUnitType = material?.properties?.unit_type as string;
  payload.unit_type = laborUnitType;
  if (laborUnitType === "linear_meter") {
    payload.length = toDim(dimensions.length, getUnit("length"));
  } else {
    payload.width = toDim(dimensions.width, getUnit("width"));
    payload.height = toDim(dimensions.height, getUnit("height"));
  }
  return payload;
};

// ============================================================================
// ESTRATEGIA: SOLID
// ============================================================================

export const getRequiredPropertiesForSolid = (
  _strategy: MeasurementStrategy,
  material: Material,
): PropertyConfig[] => {
  const properties: PropertyConfig[] = [];
  const solidProps = material.properties || {};
  const hasDimensionsInMaterial = !!(
    solidProps["width"] ||
    solidProps["height"] ||
    solidProps["depth"]
  );

  if (hasDimensionsInMaterial) {
    properties.push(
      {
        name: "width",
        display_name: "Ancho",
        type: "measurement",
        required: true,
        description: "Ancho del solido",
      },
      {
        name: "height",
        display_name: "Alto",
        type: "measurement",
        required: true,
        description: "Alto del solido",
      },
      {
        name: "depth",
        display_name: "Profundidad",
        type: "measurement",
        required: true,
        description: "Profundidad del solido",
      },
    );
  } else {
    properties.push(
      {
        name: "weight",
        display_name: "Peso",
        type: "measurement",
        required: false,
        description: "Peso del material",
        note: "Especifica peso o volumen",
      },
      {
        name: "volume",
        display_name: "Volumen",
        type: "measurement",
        required: false,
        description: "Volumen del material",
        note: "Especifica peso o volumen",
      },
    );
  }
  return properties;
};

export const getAvailableUnitsForSolid = (material: Material) => {
  const properties = material.properties || {};
  const hasDimensions =
    properties["width"] || properties["height"] || properties["depth"];
  if (hasDimensions) return ["m", "cm", "mm", "in", "ft"];

  // Para solidos sin dimensiones (como granel), permitimos peso y volumen
  return ["kg", "g", "lb", "ton", "oz", "L", "ml", "m3", "cm3", "gal", "fl oz"];
};

export const validateDimensionsSolid = (
  dimensions: Record<string, any>,
  _requiredProperties: PropertyConfig[],
  material: Material,
) => {
  const errors: string[] = [];
  const materialProps = material.properties || {};
  const isMaterialWithDimensions = !!(
    materialProps["width"] ||
    materialProps["height"] ||
    materialProps["depth"]
  );

  if (isMaterialWithDimensions) {
    if (!dimensions.width || parseFloat(dimensions.width) <= 0) {
      errors.push("Ancho requerido");
    }
    if (!dimensions.height || parseFloat(dimensions.height) <= 0) {
      errors.push("Alto requerido");
    }
    if (!dimensions.depth || parseFloat(dimensions.depth) <= 0) {
      errors.push("Profundidad requerida");
    }
  } else {
    const hasWeight = dimensions.weight && parseFloat(dimensions.weight) > 0;
    const hasVolume = dimensions.volume && parseFloat(dimensions.volume) > 0;
    if (!hasWeight && !hasVolume) {
      errors.push("Debe especificar peso o volumen");
    }
  }
  return { valid: errors.length === 0, errors };
};

export const buildDimensionsPayloadSolid = (
  dimensions: Record<string, any>,
  material: Material | null,
) => {
  const payload: Record<string, any> = {};
  const toDim = (val: any, unit: string) => {
    const num = parseFloat(String(val));
    return isNaN(num) ? undefined : { value: num, unit };
  };
  const getUnit = (key: string) => dimensions[`${key}_unit`] || dimensions.unit;

  const materialProps = material?.properties || {};
  const isMaterialWithDimensions = !!(
    materialProps["width"] ||
    materialProps["height"] ||
    materialProps["depth"]
  );

  if (isMaterialWithDimensions) {
    payload.width = toDim(dimensions.width, getUnit("width"));
    payload.height = toDim(dimensions.height, getUnit("height"));
    payload.depth = toDim(dimensions.depth, getUnit("depth"));
  } else {
    if (dimensions.weight)
      payload.weight = toDim(dimensions.weight, getUnit("weight"));
    if (dimensions.volume)
      payload.volume = toDim(dimensions.volume, getUnit("volume"));
  }
  return payload;
};

export const shouldShowPropertySolid = (
  prop: PropertyConfig,
  dimensions: Record<string, any>,
) => {
  if (prop.name === "weight" && dimensions.volume) return false;
  if (prop.name === "volume" && dimensions.weight) return false;
  return true;
};

// ============================================================================
// ESTRATEGIA: LIQUID
// ============================================================================

export const getRequiredPropertiesForLiquid = (): PropertyConfig[] => [
  {
    name: "volume",
    display_name: "Volumen",
    type: "measurement",
    required: true,
    description: "Volumen del liquido",
  },
];

export const getAvailableUnitsForLiquid = () => [
  "L",
  "ml",
  "gal",
  "m3",
  "cm3",
  "fl oz",
];

export const validateDimensionsLiquid = (dimensions: Record<string, any>) => {
  const errors: string[] = [];
  if (!dimensions.volume || parseFloat(dimensions.volume) <= 0) {
    errors.push("Debe especificar el volumen");
  }
  return { valid: errors.length === 0, errors };
};

export const buildDimensionsPayloadLiquid = (
  dimensions: Record<string, any>,
) => {
  const payload: Record<string, any> = {};
  const toDim = (val: any, unit: string) => {
    const num = parseFloat(String(val));
    return isNaN(num) ? undefined : { value: num, unit };
  };
  const getUnit = (key: string) => dimensions[`${key}_unit`] || dimensions.unit;

  if (dimensions.volume) {
    payload.volume = toDim(dimensions.volume, getUnit("volume"));
  }
  return payload;
};

// ============================================================================
// ESTRATEGIA: PROFILE
// ============================================================================

export const getRequiredPropertiesForProfile = (): PropertyConfig[] => [
  {
    name: "length",
    display_name: "Longitud",
    type: "measurement",
    required: true,
    description: "Longitud de la pieza",
  },
];

export const getAvailableUnitsForProfile = () => ["m", "cm", "ft", "mm", "in"];

export const validateDimensionsProfile = (dimensions: Record<string, any>) => {
  const errors: string[] = [];
  if (!dimensions.length || parseFloat(dimensions.length) <= 0) {
    errors.push("Debe especificar la longitud");
  }
  return { valid: errors.length === 0, errors };
};

export const buildDimensionsPayloadProfile = (
  dimensions: Record<string, any>,
) => {
  const payload: Record<string, any> = {};
  const toDim = (val: any, unit: string) => {
    const num = parseFloat(String(val));
    return isNaN(num) ? undefined : { value: num, unit };
  };
  const getUnit = (key: string) => dimensions[`${key}_unit`] || dimensions.unit;

  if (dimensions.length) {
    payload.length = toDim(dimensions.length, getUnit("length"));
  }
  return payload;
};

// ============================================================================
// ESTRATEGIA: UNIT
// ============================================================================

export const getRequiredPropertiesForUnit = (): PropertyConfig[] => [];

export const getAvailableUnitsForUnit = () => ["un", "pza", "set"];

export const validateDimensionsUnit = () => ({ valid: true, errors: [] });

export const buildDimensionsPayloadUnit = () => ({});

// ============================================================================
// ESTRATEGIA: GENERIC / FALLBACK
// ============================================================================

export const getRequiredPropertiesGeneric = (
  strategy: MeasurementStrategy,
): PropertyConfig[] => {
  if (!strategy.properties) return [];
  return strategy.properties.map((prop) => ({
    name: prop.name,
    display_name: prop.display_name,
    type: prop.type,
    required:
      typeof prop.required === "boolean"
        ? prop.required
        : prop.required === "conditional"
          ? ("conditional" as const)
          : false,
    required_if: prop.required_if,
    description: prop.description,
    unit_dimension: prop.unit_dimension,
    preferred_units: prop.preferred_units,
    options: prop.options as any,
    default_value: prop.default_value,
    default_unit: prop.default_unit,
    note: prop.note,
  }));
};

export const getAvailableUnitsGeneric = () => ["m", "cm", "mm"];

export const validateDimensionsGeneric = (
  dimensions: Record<string, any>,
  requiredProperties: PropertyConfig[],
) => {
  const errors: string[] = [];
  requiredProperties.forEach((prop) => {
    if (prop.required === true) {
      if (!dimensions[prop.name] || dimensions[prop.name] === "") {
        errors.push(`${prop.display_name} es requerido`);
      }
    }
  });
  return { valid: errors.length === 0, errors };
};

export const buildDimensionsPayloadGeneric = (
  dimensions: Record<string, any>,
) => {
  const payload: Record<string, any> = {};
  const toDim = (val: any, unit: string) => {
    const num = parseFloat(String(val));
    return isNaN(num) ? undefined : { value: num, unit };
  };
  const getUnit = (key: string) => dimensions[`${key}_unit`] || dimensions.unit;

  Object.entries(dimensions).forEach(([key, value]) => {
    if (key !== "unit" && key !== "mode" && !key.endsWith("_unit")) {
      payload[key] = toDim(value, getUnit(key));
    }
  });
  return payload;
};

export const shouldShowPropertyGeneric = () => true;
