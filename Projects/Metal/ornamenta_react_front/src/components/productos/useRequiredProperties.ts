import { useMemo } from 'react';
import { Material, MeasurementStrategy } from '@/types/products';

export const useRequiredProperties = (
  currentStrategy: MeasurementStrategy | null, 
  selectedMaterial: Material | null
) => {
  return useMemo(() => {
    if (!currentStrategy || !selectedMaterial?.properties) return [];
    
    const unitType = selectedMaterial.properties['unit_type'] as string;
    if (!unitType) return currentStrategy.properties.filter(prop => prop.required === true);
    
    // Para LABOR: mostrar solo width y height segun unit_type
    // No mostrar area ni length como opciones directas
    return currentStrategy.properties.filter(prop => {
      if (prop.name === 'unit_type') return false;
      
      // Siempre requeridos
      if (prop.required === true) return true;
      
      // Para LABOR: solo mostrar width y height
      if (selectedMaterial.measurement_strategy === 'LABOR') {
        if (unitType === 'linear_meter') {
          // Solo width y height (para calcular perimetro)
          return prop.name === 'width' || prop.name === 'height';
        } else if (unitType === 'square_meter') {
          // Solo width y height (para calcular area)
          return prop.name === 'width' || prop.name === 'height';
        }
      }
      
      // Para otras estrategias: evaluar condicionales normalmente
      if (prop.required === 'conditional' && prop.required_if) {
        const unitTypeMatch = prop.required_if.match(/unit_type == '([^']+)'/);
        if (unitTypeMatch) {
          const requiredUnitType = unitTypeMatch[1];
          return unitType === requiredUnitType;
        }
      }
      
      return false;
    });
  }, [currentStrategy, selectedMaterial]);
};

