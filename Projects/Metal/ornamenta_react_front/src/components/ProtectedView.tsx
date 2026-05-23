import React from "react";
import { useAuth } from "@hooks/useAuth";
import { Card, Button } from "@heroui/react";
import { AlertCircle } from "lucide-react";

interface ProtectedViewProps {
  children: React.ReactNode;
  allowedStates?: string[]; // Por defecto solo "A" (Active)
}

export const ProtectedView: React.FC<ProtectedViewProps> = ({
  children,
  allowedStates = ["A"], // Solo activos por defecto
}) => {
  const { userState } = useAuth();

  const isAllowed = userState && allowedStates.includes(userState);

  if (!isAllowed) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 p-4">
        <Card className="w-full max-w-md p-6 border-danger-200 bg-danger-50">
          <div className="flex flex-col items-center text-center">
            <AlertCircle className="w-12 h-12 text-danger mb-4" />
            <h2 className="text-xl font-semibold text-danger mb-2">
              Acceso Restringido
            </h2>
            <p className="text-danger-700 mb-4">
              Tu cuenta ha sido desactivada. Solo puedes ver tu perfil.
            </p>
            <p className="text-sm text-danger-600">
              Status: {userState === "I" ? "Inactive" : "Desconocido"}
            </p>
          </div>
        </Card>
      </div>
    );
  }

  return <>{children}</>;
};
