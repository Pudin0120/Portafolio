// Validation utilities

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validateIdentificationNumber = (identification: string): boolean => {
  return identification.length <= 12 && identification.length > 0;
};

export const validatePhone = (phone: string): boolean => {
  return phone.length <= 15 && phone.length > 0;
};

export const validateRequiredFields = (data: Record<string, any>, requiredFields: string[]): string | null => {
  for (const field of requiredFields) {
    if (!data[field] || data[field].toString().trim() === '') {
      return `El campo ${field} es obligatorio`;
    }
  }
  return null;
};

/**
 * Validates a document number according to backend rules
 * The backend accepts any alphanumeric document up to 12 characters
 * Aplica para CC, CE y NIT por igual
 */
export const validateDocumentNumber = (value: string): { valid: boolean; error?: string } => {
  const trimmed = value.trim();
  
  if (trimmed.length === 0) {
    return { valid: false, error: 'The document number cannot be empty.' };
  }
  
  // Validate maximum length according to the database (VARCHAR(12))
  if (trimmed.length > 12) {
    return { valid: false, error: 'The document number cannot exceed 12 characters.' };
  }
  
  return { valid: true };
};

/**
 * Validates a document according to its type
 * Nota: El backend ahora acepta documents alfanumericos de hasta 12 caracteres para todos los tipos
 */
export const validateDocumentByType = (
  documentType: string, 
  documentNumber: string
): { valid: boolean; error?: string } => {
  // Validar que el tipo de document sea valid
  if (!['CC', 'CE', 'NI'].includes(documentType)) {
    return { valid: false, error: 'Invalid document type.' };
  }
  
  // Validar el number de document (mismo criterio para todos los tipos)
  return validateDocumentNumber(documentNumber);
};
