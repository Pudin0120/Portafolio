/**
 * Utilidades comunes para la creation de materials
 */

import { PropertyConfig } from '@/types/material-creation';

/**
 * Mapea unidades a sus nombres en espanol para mostrar en la UI
 */
export const getDisplayUnitName = (unit: string | undefined): string => {
  if (!unit || typeof unit !== 'string') return unit || '';
  
  const unitMap: Record<string, string> = {
    // Longitud
    'mm': 'milimetros (mm)',
    'cm': 'centimetros (cm)',
    'm': 'metros (m)',
    'in': 'pulgadas (in)',
    'inch': 'pulgadas (in)',
    'ft': 'pies (ft)',
    'foot': 'pies (ft)',
    'feet': 'pies (ft)',
    
    // Area
    'm2': 'm (metros cuadrados)',
    'm': 'm (metros cuadrados)',
    'cm2': 'cm (centimetros cuadrados)',
    'cm': 'cm (centimetros cuadrados)',
    'ft2': 'ft (pies cuadrados)',
    'ft': 'ft (pies cuadrados)',
    'in2': 'in (pulgadas cuadradas)',
    'in': 'in (pulgadas cuadradas)',
    
    // Volumen
    'm3': 'm (metros cubicos)',
    'm': 'm (metros cubicos)',
    'cm3': 'cm (centimetros cubicos)',
    'cm': 'cm (centimetros cubicos)',
    'ft3': 'ft (pies cubicos)',
    'ft': 'ft (pies cubicos)',
    'l': 'litros (L)',
    'L': 'litros (L)',
    'ml': 'mililitros (ml)',
    'gal': 'galones (gal)',
    'fl oz': 'onzas liquidas (fl oz)',
    
    // Masa
    'g': 'gramos (g)',
    'kg': 'kilogramos (kg)',
    'lb': 'libras (lb)',
    'oz': 'onzas (oz)',
    
    // Densidad
    'kg/m3': 'kg/m',
    'kg/m': 'kg/m',
    'kg/l': 'kg/L',
    'g/cm3': 'g/cm',
    'g/cm': 'g/cm',
  };
  
  return unitMap[unit] || unit;
};

/**
 * Denormaliza las unidades para el backend (m  m2)
 */
export const denormalizeUnit = (unit: string | undefined): string => {
  if (!unit || typeof unit !== 'string') return '';
  let normalized = unit
    .replace(/m/g, 'm2')
    .replace(/cm/g, 'cm2')
    .replace(/ft/g, 'ft2')
    .replace(/in/g, 'in2')
    .replace(/m/g, 'm3')
    .replace(/cm/g, 'cm3')
    .replace(/ft/g, 'ft3');
  
  // Convertir nombres largos de unidades a abreviaturas estandar del backend
  normalized = normalized
    .replace(/inch(es)?/gi, 'in')
    .replace(/foot|feet/gi, 'ft')
    .replace(/meter(s)?/gi, 'm')
    .replace(/millimeter(s)?/gi, 'mm')
    .replace(/centimeter(s)?/gi, 'cm')
    .replace(/gallon(s)?/gi, 'gal')
    .replace(/liter(s)?/gi, 'l')
    .replace(/milliliter(s)?/gi, 'ml')
    .replace(/kilogram(s)?/gi, 'kg')
    .replace(/gram(s)?/gi, 'g')
    .replace(/pound(s)?/gi, 'lb')
    .replace(/ounce(s)?/gi, 'oz')
    .replace(/fluid\s*ounce(s)?/gi, 'fl oz');
  
  return normalized;
};

/**
 * Determina si una propiedad debe mostrarse segun el modo de entrada y condiciones
 */
export const shouldShowProperty = (
  prop: PropertyConfig,
  inputMode: string,
  dynamicProperties: Record<string, any>
): boolean => {
  // Si la propiedad es requerida siempre, mostrarla
  if (prop.required === true) return true;

  // Si no es condicional, mostrar por defecto
  if (prop.required !== 'conditional' || !prop.required_if) {
    return true;
  }

  // Formato SHEET/LIQUID: "mode == 'area_direct'"
  const modeMatch = prop.required_if.match(/mode == '([^']+)'/);
  if (modeMatch) {
    const requiredMode = modeMatch[1];
    return requiredMode === inputMode;
  }

  // Formato LABOR: "unit_type == 'linear_meter' AND sin width/height"
  const unitTypeMatch = prop.required_if.match(/unit_type == '([^']+)'/);
  if (unitTypeMatch) {
    const requiredUnitType = unitTypeMatch[1];
    const hasCorrectUnitType = dynamicProperties['unit_type'] === requiredUnitType;

    if (!hasCorrectUnitType) return false;

    // Verificar si contiene condicion de "sin"
    if (prop.required_if.includes(' sin ')) {
      const sinMatch = prop.required_if.match(/sin ([a-z]+\/[a-z]+)/);
      if (sinMatch) {
        const excludedFields = sinMatch[1].split('/');
        const hasExcludedValues = excludedFields.some(field => {
          const hasValue = dynamicProperties[`${field}_value`] !== undefined && 
                          dynamicProperties[`${field}_value`] !== null && 
                          dynamicProperties[`${field}_value`] !== '';
          return hasValue;
        });
        return !hasExcludedValues;
      }
    }
    return hasCorrectUnitType;
  }

  // Formato LABOR: "sin length/area" o "sin width/height"
  if (prop.required_if.includes('sin ')) {
    const sinMatch = prop.required_if.match(/sin ([a-z]+\/[a-z]+)/);
    if (sinMatch) {
      const excludedFields = sinMatch[1].split('/');
      const hasExcludedValues = excludedFields.some(field => {
        const hasValue = dynamicProperties[`${field}_value`] !== undefined && 
                        dynamicProperties[`${field}_value`] !== null && 
                        dynamicProperties[`${field}_value`] !== '';
        return hasValue;
      });
      return !hasExcludedValues;
    }
  }

  return false;
};

/**
 * Valida que un valor numerico sea valid
 */
export const isValidNumber = (value: any): boolean => {
  return value !== undefined && value !== null && value !== '' && !isNaN(parseFloat(value));
};

/**
 * Valida que una propiedad de measurement tenga valor y unidad
 */
export const isValidMeasurement = (
  properties: Record<string, any>,
  propertyName: string
): boolean => {
  const value = properties[`${propertyName}_value`];
  const unit = properties[`${propertyName}_unit`];
  return isValidNumber(value) && !!unit;
};

/**
 * Extrae el error del response del API
 */
export const extractApiError = async (response: Response): Promise<string> => {
  let errorMessage = 'Error al create material';
  try {
    const errorText = await response.text();
    try {
      const errorData = JSON.parse(errorText);
      errorMessage = errorData?.detail || errorText;
    } catch {
      errorMessage = errorText;
    }
  } catch {
    errorMessage = `Error ${response.status}: ${response.statusText}`;
  }
  return errorMessage;
};
