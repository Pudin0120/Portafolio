import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { LogOut, User as UserIcon } from "lucide-react";
import { Button } from "@heroui/react";
import { useAuth } from "@hooks/useAuth";
import { apiClient } from "@services/apiClient";

interface UserProfileMenuProps {
  isOpen: boolean;
  onToggle: () => void;
  onLogout: () => void;
  userProfile?: {
    first_name: string;
    last_name: string;
    email: string;
  } | null;
  userEmail?: string | null;
}

export const UserProfileMenu: React.FC<UserProfileMenuProps> = ({
  isOpen,
  onToggle,
  onLogout,
  userProfile,
  userEmail,
}) => {
  const { userRole } = useAuth();
  const [roleDisplayName, setRoleDisplayName] =
    React.useState<string>("User");

  const fullName =
    userProfile?.first_name && userProfile?.last_name
      ? `${userProfile.first_name} ${userProfile.last_name}`.trim()
      : userEmail || "User";

  const email = userProfile?.email || userEmail || "user@ejemplo.com";

  // Obtener display_name del rol del endpoint /roles
  React.useEffect(() => {
    const fetchRoleDisplayName = async () => {
      try {
        const data = await apiClient.get("/roles");
        const roleInfo = data.roles?.find(
          (r: { value: string }) => r.value === userRole?.toUpperCase(),
        );
        if (roleInfo) {
          setRoleDisplayName(roleInfo.display_name);
        }
      } catch (error) {
        console.error("Error al obtener role_display_name:", error);
      }
    };

    if (userRole) {
      fetchRoleDisplayName();
    }
  }, [userRole]);

  return (
    <div className="relative flex items-center gap-3" data-profile-menu>
      {/* Informacion del user */}
      <div className="hidden sm:flex items-center gap-2 text-right">
        <div className="flex flex-col">
          <span className="text-sm font-semibold text-foreground">
            {fullName}
          </span>
          <span className="text-xs text-default-500">{roleDisplayName}</span>
        </div>
      </div>

      {/* Boton de perfil */}
      <Button
        isIconOnly
        radius="full"
        color="primary"
        variant="solid"
        onClick={onToggle}
        className="w-10 h-10 flex items-center justify-center shadow-md hover:shadow-lg transition-all duration-200"
      >
        <UserIcon className="w-5 h-5 text-primary-foreground" />
      </Button>

      {/* Menu desplegable */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -5 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -5 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 top-full z-50 mt-2 w-56 overflow-hidden rounded-lg border border-surface-border bg-surface-elevated shadow-lg"
            style={{ originY: 0 }}
          >
            {/* Informacion del user */}
            <div className="border-b border-surface-border px-4 py-3">
              <p className="text-sm font-semibold text-foreground">
                {fullName}
              </p>
              <p className="text-xs text-primary font-medium mt-0.5">
                {roleDisplayName}
              </p>
              <p className="text-xs text-default-500 truncate mt-1">{email}</p>
            </div>

            {/* Boton de cerrar sesion */}
            <button
              type="button"
              onClick={onLogout}
              className="w-full flex items-center gap-2 px-4 py-3 text-sm text-danger font-medium hover:bg-danger/10 transition-colors duration-150"
            >
              <LogOut className="w-4 h-4" />
              Cerrar sesion
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
