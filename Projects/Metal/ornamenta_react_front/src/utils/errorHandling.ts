// Utilidades para manejo de errores

export const getErrorMessage = (error: unknown): string => {
  if (error instanceof Error) {
    return translateError(error.message);
  }
  return translateError(String(error));
};

export const translateError = (message: string): string => {
  const lowerMessage = message.toLowerCase();

  if (
    lowerMessage.includes("email-already-in-use") ||
    lowerMessage.includes("email address is already in use") ||
    lowerMessage.includes("email ya esta registrado") ||
    lowerMessage.includes("409")
  ) {
    return "Este email ya esta registrado. Please, usa uno diferente.";
  }

  if (lowerMessage.includes("invalid-email")) {
    return "El formato del email no es valid.";
  }

  if (lowerMessage.includes("weak-password")) {
    return "La password es muy debil. Debe tener al menos 6 caracteres.";
  }

  if (lowerMessage.includes("user-not-found")) {
    return "User not found.";
  }

  if (lowerMessage.includes("wrong-password")) {
    return "Password incorrecta.";
  }

  if (
    lowerMessage.includes("identification_number") &&
    lowerMessage.includes("already exists")
  ) {
    return "Ya existe un user con este number de identificacion.";
  }

  return message;
};

export const handleApiError = (
  status: number,
  customMessage?: string,
): string => {
  if (customMessage) return translateError(customMessage);

  switch (status) {
    case 400:
      return "Los datos ingresados no son valids. Please, verify la information.";
    case 409:
      return "Ya existe un registro con este email o number de document.";
    case 500:
      return "An internal server error occurred. Try again later.";
    default:
      return "Error al procesar la solicitud. Please, intente nuevamente.";
  }
};
