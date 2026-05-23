/**
 * Translations for task and work statuses
 * Centralizes all English labels to maintain consistency
 */

export const taskStateTranslations: Record<string, string> = {
  PENDING: 'Pending',
  ASSIGNED: 'Asignada',
  READY: 'Por Iniciar',
  IN_PROGRESS: 'En Proceso',
  COMPLETED: 'Completada',
  FINISHED: 'Finalizada',
};

export const workStateTranslations: Record<string, string> = {
  DRAFT: 'Borrador',
  QUOTED: 'Cotizado',
  IN_PROGRESS: 'En Progreso',
  DELIVERED: 'Entregado',
};

export const productStateTranslations: Record<string, string> = {
  PENDING: 'Pending',
  IN_PROGRESS: 'En Proceso',
  COMPLETED: 'Completed',
  DELIVERED: 'Entregado',
};

/**
 * Gets the label for a task status
 */
export const getTaskStateLabel = (state: string): string => {
  return taskStateTranslations[state] || state;
};

/**
 * Gets the label for a work status
 */
export const getWorkStateLabel = (state: string): string => {
  return workStateTranslations[state] || state;
};

/**
 * Gets the label for a product status
 */
export const getProductStateLabel = (state: string): string => {
  return productStateTranslations[state] || state;
};

/**
 * Gets the HeroUI color according to task status
 */
export const getTaskStateColor = (state: string): 'default' | 'warning' | 'success' | 'danger' | 'secondary' => {
  switch (state) {
    case 'PENDING':
      return 'default';
    case 'ASSIGNED':
      return 'secondary';
    case 'READY':
      return 'warning';
    case 'IN_PROGRESS':
      return 'warning';
    case 'COMPLETED':
      return 'success';
    case 'FINISHED':
      return 'success';
    default:
      return 'default';
  }
};

/**
 * Gets the HeroUI color according to work status
 */
export const getWorkStateColor = (state: string): 'default' | 'warning' | 'success' => {
  switch (state) {
    case 'DRAFT':
      return 'default';
    case 'QUOTED':
      return 'warning';
    case 'IN_PROGRESS':
      return 'warning';
    case 'DELIVERED':
      return 'success';
    default:
      return 'default';
  }
};

/**
 * Gets the HeroUI color according to product status
 */
export const getProductStateColor = (state: string): 'default' | 'warning' | 'success' => {
  switch (state) {
    case 'PENDING':
      return 'default';
    case 'IN_PROGRESS':
      return 'warning';
    case 'COMPLETED':
      return 'success';
    case 'DELIVERED':
      return 'success';
    default:
      return 'default';
  }
};
