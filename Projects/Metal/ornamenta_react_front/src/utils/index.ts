// Archivo de barril para exportar todas las utilidades
export * from "./validation";
export * from "./errorHandling";

/**
 * Formats a number as a price with thousands separators
 * @param price - El price a formatear
 * @param locale - The locale to use (default 'en-US')
 * @returns El price formateado (ej: 10,000.00)
 */
export const formatPrice = (
  price: number,
  locale: string = "es-CO",
): string => {
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(price);
};

/**
 * Formats a number as COP currency
 * @param value - El valor a formatear
 * @returns El valor formateado como moneda (ej: $ 10.000)
 */
export const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};
