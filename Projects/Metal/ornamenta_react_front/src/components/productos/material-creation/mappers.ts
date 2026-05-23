import { Material } from "@/types/products";
import { StrategyConfig, MaterialFormState } from "@/types/material-creation";
import { denormalizeUnit } from "./utils";
import { buildMaterialPayload } from "./payloadBuilders";

/**
 * Mappers para transformar datos de materials entre formato backend y formato frontend
 */

import { getMaterialStrategy } from "./strategies/registry";

/**
 * Transforma un objeto Material del backend al formato plano dynamicProperties
 * que usan los formularios de React.
 */
export const materialToFormState = (
  material: Material,
  strategyConfig: StrategyConfig | undefined,
): Record<string, any> => {
  if (!material || !material.properties) return {};

  const props: Record<string, any> = {};
  const strategyName = material.measurement_strategy || "";
  const strategy = getMaterialStrategy(strategyName);

  // Mapear campos base
  // No incluimos 'name' en props para evitar colisiones con el estado independiente
  props["description"] = material.description || "";
  props["sku"] = material.sku || "";
  props["barcode"] = material.barcode || "";

  // Mapear image_url desde el atributo de primer nivel o legacy properties
  props["image_url"] =
    (material as any).image_url || material.properties?.image_url || "";

  // Manejar precios legacy vs nuevos
  const purchaseAmount =
    material.purchase_price_amount || material.price_amount;
  const purchaseCurrency =
    material.purchase_price_currency || material.price_currency;

  props["purchase_price_amount"] = purchaseAmount || "";
  props["sale_price_amount"] = material.sale_price_amount || "";
  props["price_currency"] = purchaseCurrency || "COP";

  // Usar el mapper de la estrategia si existe
  if (strategy?.materialToFormMapper) {
    const strategyProps = strategy.materialToFormMapper(
      material,
      strategyConfig,
    );
    Object.assign(props, strategyProps);
    return props;
  }

  // Fallback: Caso generico para otras estrategias si no tienen mapper especifico
  if (strategyConfig?.properties) {
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
      } else {
        props[prop.name] = propertyValue;
      }
    });
  }

  // Asegurarnos de capturar properties extra que no esten en el config pero si en el material
  // por si el backend mando cosas como 'brand', 'color', 'calibre', etc.
  const knownKeys = new Set([
    "description",
    "sku",
    "barcode",
    "image_url",
    "purchase_price_amount",
    "sale_price_amount",
    "price_currency",
    ...(strategyConfig?.properties?.map((p) => p.name) || []),
    ...(strategyConfig?.properties?.map((p) => `${p.name}_value`) || []),
    ...(strategyConfig?.properties?.map((p) => `${p.name}_unit`) || []),
  ]);

  Object.keys(material.properties).forEach((key) => {
    if (!knownKeys.has(key) && !knownKeys.has(`${key}_value`)) {
      props[key] = material.properties[key];
    }
  });

  return props;
};

/**
 * Genera el payload para enviar al backend, reutilizando la logica de creation.
 * Calcula el diff con el estado original si es necesario (o se envia todo y el backend decide).
 */
export const formStateToPayload = (
  formState: MaterialFormState,
  strategyConfig: StrategyConfig,
): any => {
  // Reutilizamos el builder existente que ya encapsula toda la logica de negocio compleja
  // para transformar dynamicProperties -> estructura anidada del backend
  const payload = buildMaterialPayload(formState, strategyConfig);

  // Extraemos las properties que es lo que realmente nos interesa para el PATCH
  // Nota: buildMaterialPayload devuelve un objeto completo tipo MaterialProperties
  // pero nosotros para el PATCH necesitamos un objeto parcial.
  // Sin embargo, podemos extraer 'properties' de ahi.

  return payload;
};
