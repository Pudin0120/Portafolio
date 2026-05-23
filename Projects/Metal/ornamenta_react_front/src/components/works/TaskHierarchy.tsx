import React from 'react';
import { CompositeGroup } from '@/types/works';
import { Work } from '@/types/works';

export interface TaskGroup {
  parentProductId: string;
  isComposite: boolean;
  productName: string;
  tasks: any[];
  productType?: string;
  startOrder: number;
  endOrder: number;
}

/**
 * Convierte la respuesta de jerarquia del backend a TaskGroups para el UI.
 * 
 * Estructura esperada del backend:
 * - composite_groups con composite_id !== null: Products compuestos con sus tasks internas
 * - composite_groups con composite_id === null: Products simples independientes
 * 
 * Cada task tiene parent_composite_id que indica si pertenece a un compuesto.
 */
export const convertHierarchyToGroups = (
  compositeGroups: CompositeGroup[],
  work?: Work
): TaskGroup[] => {
  const result: TaskGroup[] = [];

  compositeGroups.forEach((group) => {
    if (group.composite_id !== null) {
      // Caso 1: Product compuesto (con composite_id definido)
      result.push({
        parentProductId: group.composite_id,
        isComposite: true,
        productName: group.composite_name || 'Product Compuesto',
        tasks: group.tasks,
        productType: 'COMPOSITE',
        startOrder: group.start_execution_order,
        endOrder: group.end_execution_order,
      });
    } else {
      // Caso 2: Products simples independientes (composite_id === null)
      // Agrupar cada task independiente como un product simple
      group.tasks.forEach((task) => {
        const productId = task.product_id || 'unknown';
        
        // Encontrar el nombre del product desde work.products
        let productName = 'Task Independiente';
        let productType = 'SIMPLE';

        if (work) {
          const product = work.products.find((p) => p.product_id === productId);
          if (product) {
            productName = product.product_name || product.product_id;
            productType = product.product_type || 'SIMPLE';
          }
        }

        result.push({
          parentProductId: productId,
          isComposite: false,
          productName,
          tasks: [task], // Un solo task en products simples
          productType,
          startOrder: task.execution_order || 0,
          endOrder: task.execution_order || 0,
        });
      });
    }
  });

  return result;
};

/**
 * Determina si una task puede ser movida fuera de su grupo
 */
export const canMoveTaskOutOfGroup = (taskGroup: TaskGroup): boolean => {
  return !taskGroup.isComposite;
};

/**
 * Obtiene el indice de un grupo en la lista ordenada
 */
export const getGroupIndex = (
  groupId: string,
  groups: TaskGroup[]
): number => {
  return groups.findIndex((g) => g.parentProductId === groupId);
};
