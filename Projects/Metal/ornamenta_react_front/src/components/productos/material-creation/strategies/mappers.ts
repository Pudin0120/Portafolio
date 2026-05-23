import { Material } from "@/types/products";
import { StrategyConfig } from "@/types/material-creation";
import { denormalizeUnit } from "../utils";

/**
 * Mappers para transformar datos del material (backend) al estado del formulario (frontend)
 */

export const mapSheetToForm = (material: Material): Record<string, any> => {
  const props: Record<string, any> = {};
  const properties = material.properties || {};

  const thicknessData = properties["thickness"] as any;
  if (thicknessData) {
    if (thicknessData.gauge !== undefined) {
      props["thickness_type"] = "gauge";
      props["thickness_gauge"] = thicknessData.gauge;
      if (thicknessData.mm !== undefined) {
        props["thickness_mm_display"] = thicknessData.mm;
        props["thickness_mm"] = String(thicknessData.mm);
      }
    } else if (thicknessData.value !== undefined) {
      props["thickness_type"] = "measurement";
      props["thickness_mm"] = thicknessData.value;
      props["thickness_unit"] = denormalizeUnit(thicknessData.unit || "mm");
    }
  }

  ["area", "width", "length"].forEach((key) => {
    const data = properties[key] as any;
    if (data) {
      props[`${key}_value`] = data.value;
      props[`${key}_unit`] = denormalizeUnit(
        typeof data.unit === "string" ? data.unit : data.unit?.symbol,
      );
    }
  });

  // Si no hay width/length pero si area, intentamos mantener el modo area
  if (!props["width_value"] && !props["length_value"] && props["area_value"]) {
    props["_input_mode"] = "area_direct";
  } else {
    props["_input_mode"] = "dimensions";
  }

  // Global properties
  if (properties["color"]) props["color"] = properties["color"];
  if (properties["brand"]) props["brand"] = properties["brand"];
  if (properties["model"]) props["model"] = properties["model"];
  if (properties["part_number"])
    props["part_number"] = properties["part_number"];

  return props;
};

export const mapLiquidToForm = (material: Material): Record<string, any> => {
  const props: Record<string, any> = {};
  const properties = material.properties || {};

  const volumeData = properties["volume"] as any;
  if (volumeData) {
    props["volume_value"] = volumeData.value;
    props["volume_unit"] = denormalizeUnit(
      typeof volumeData.unit === "string"
        ? volumeData.unit
        : volumeData.unit?.symbol || "L",
    );
  }

  if (properties["color"]) props["color"] = properties["color"];
  if (properties["brand"]) props["brand"] = properties["brand"];
  if (properties["model"]) props["model"] = properties["model"];
  if (properties["part_number"])
    props["part_number"] = properties["part_number"];

  return props;
};

export const mapUnitToForm = (material: Material): Record<string, any> => {
  const props: Record<string, any> = {};
  const properties = material.properties || {};

  if (properties["color"]) props["color"] = properties["color"];
  if (properties["brand"]) props["brand"] = properties["brand"];
  if (properties["model"]) props["model"] = properties["model"];
  if (properties["part_number"])
    props["part_number"] = properties["part_number"];

  return props;
};

export const mapSolidToForm = (material: Material): Record<string, any> => {
  const props: Record<string, any> = {};
  const properties = material.properties || {};

  const massData = (properties["mass"] || properties["weight"]) as any;
  if (
    massData &&
    (massData.value !== undefined || massData.gauge !== undefined)
  ) {
    props["mass_value"] = massData.value;
    props["mass_unit"] = denormalizeUnit(
      typeof massData.unit === "string"
        ? massData.unit
        : massData.unit?.symbol || "kg",
    );
  }

  const volumeData = properties["volume"] as any;
  if (volumeData && volumeData.value !== undefined) {
    props["volume_value"] = volumeData.value;
    props["volume_unit"] = denormalizeUnit(
      typeof volumeData.unit === "string"
        ? volumeData.unit
        : volumeData.unit?.symbol || "L",
    );
  }

  if (properties["color"]) props["color"] = properties["color"];
  if (properties["brand"]) props["brand"] = properties["brand"];
  if (properties["model"]) props["model"] = properties["model"];
  if (properties["part_number"])
    props["part_number"] = properties["part_number"];

  return props;
};

export const mapLaborToForm = (material: Material): Record<string, any> => {
  const props: Record<string, any> = {};
  const properties = material.properties || {};

  props["unit_type"] = properties["unit_type"] || "linear_meter";

  const metrics = ["length", "area", "width", "height"];
  metrics.forEach((key) => {
    const data = properties[key] as any;
    if (data && data.value !== undefined) {
      props[`${key}_value`] = data.value;
      props[`${key}_unit`] = denormalizeUnit(
        typeof data.unit === "string" ? data.unit : data.unit?.symbol,
      );
    }
  });

  if (properties["color"]) props["color"] = properties["color"];
  if (properties["brand"]) props["brand"] = properties["brand"];
  if (properties["model"]) props["model"] = properties["model"];
  if (properties["part_number"])
    props["part_number"] = properties["part_number"];

  return props;
};

export const mapProfileToForm = (material: Material): Record<string, any> => {
  const props: Record<string, any> = {};
  const properties = material.properties || {};

  props["shape"] = properties["shape"] || "ROUND";
  props["is_hollow"] = properties["is_hollow"] ?? true;

  // thickness
  const thicknessData = properties["thickness"] as any;
  if (thicknessData) {
    if (thicknessData.gauge !== undefined) {
      props["thickness_type"] = "gauge";
      props["thickness_gauge"] = thicknessData.gauge;
    } else if (thicknessData.value !== undefined) {
      props["thickness_type"] = "measurement";
      props["thickness_value"] = thicknessData.value;
      props["thickness_unit"] = denormalizeUnit(thicknessData.unit || "mm");
    }
  }

  // Dimensiones dinamicas
  const dims = ["diameter", "width", "height", "length"];
  dims.forEach((dim) => {
    const data = properties[dim] as any;
    if (data) {
      props[`${dim}_value`] = data.value;
      props[`${dim}_unit`] = denormalizeUnit(
        typeof data.unit === "string" ? data.unit : data.unit?.symbol,
      );
    }
  });

  if (properties["color"]) props["color"] = properties["color"];
  if (properties["brand"]) props["brand"] = properties["brand"];
  if (properties["model"]) props["model"] = properties["model"];
  if (properties["part_number"])
    props["part_number"] = properties["part_number"];

  return props;
};

export const mapGenericToForm = (
  material: Material,
  strategyConfig: StrategyConfig | undefined,
): Record<string, any> => {
  const props: Record<string, any> = {};
  if (!strategyConfig?.properties) return props;

  strategyConfig.properties.forEach((prop) => {
    const propertyValue = material.properties![prop.name] as any;
    if (propertyValue === undefined || propertyValue === null) return;

    if (prop.type === "measurement") {
      if (propertyValue.value !== undefined) {
        props[`${prop.name}_value`] = propertyValue.value;
      }
      const unitValue =
        typeof propertyValue.unit === "string"
          ? propertyValue.unit
          : propertyValue.unit?.symbol || prop.default_unit;
      props[`${prop.name}_unit`] = denormalizeUnit(unitValue);
    } else if (prop.type === "gauge_or_measurement") {
      if (propertyValue.gauge !== undefined) {
        props[`${prop.name}_type`] = "gauge";
        props[`${prop.name}_gauge`] = propertyValue.gauge;
      } else {
        props[`${prop.name}_type`] = "measurement";
        props[`${prop.name}_mm`] = propertyValue.value;
        props[`${prop.name}_unit`] = denormalizeUnit(
          propertyValue.unit || "mm",
        );
      }
    } else {
      props[prop.name] = propertyValue;
    }
  });

  return props;
};
