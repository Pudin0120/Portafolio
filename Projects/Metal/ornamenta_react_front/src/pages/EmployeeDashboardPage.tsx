import React, { useState, useEffect, useCallback, useMemo } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  ClipboardList,
  DollarSign,
  FileText,
  Home,
  Palette,
  User as UserIcon,
} from "lucide-react";
import { useAuth } from "@hooks/useAuth";
import { useConnectivity } from "@/providers/ConnectivityProvider";
import { DashboardLayout } from "@components/DashboardLayout";
import { ProfilePage } from "@pages/ProfilePage";
import { QuotationsPage } from "@pages/QuotationsPage";
import { TasksPage } from "@pages/TasksPage";
import type { MenuItem } from "@components/SidebarMenu";
import type { BreadcrumbItem } from "@components/Breadcrumbs";
import { EmployeeHomePage } from "./EmployeeHomePage";
import { PayrollPage } from "@pages/PayrollPage";
import { UserService, type UserProfile } from "@services/userService";
import { ColorSettings } from "@components/settings/ColorSettings";

type TabKey =
  | "home"
  | "tasks"
  | "cotizaciones"
  | "payroll"
  | "branding"
  | "about";

const TAB_CONFIG: Record<
  TabKey,
  { path: string; label: string; icon: React.ReactNode }
> = {
  home: { path: "/", label: "Inicio", icon: <Home className="w-5 h-5" /> },
  tasks: {
    path: "/tasks",
    label: "Tasks",
    icon: <ClipboardList className="w-5 h-5" />,
  },
  cotizaciones: {
    path: "/quotations",
    label: "Cotizaciones",
    icon: <FileText className="w-5 h-5" />,
  },
  payroll: {
    path: "/payrolls",
    label: "Payrolls",
    icon: <DollarSign className="w-5 h-5" />,
  },
  branding: {
    path: "/branding",
    label: "Personalizacion",
    icon: <Palette className="w-5 h-5" />,
  },
  about: {
    path: "/about",
    label: "Mi Perfil",
    icon: <UserIcon className="w-5 h-5" />,
  },
};

export const EmployeeDashboardPage: React.FC = () => {
  const { user, logout } = useAuth();
  const { isOnline } = useConnectivity();
  const navigate = useNavigate();
  const location = useLocation();

  const activeTab = useMemo<TabKey>(() => {
    return (
      (Object.entries(TAB_CONFIG).find(
        ([_, config]) =>
          location.pathname.includes(config.path) && config.path !== "/",
      )?.[0] as TabKey) || "home"
    );
  }, [location.pathname]);

  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);

  // --- Cargar perfil del user ---
  const fetchUserProfile = useCallback(async () => {
    if (!user) return;

    try {
      const userData = await UserService.getUserProfile();
      setUserProfile(userData);
    } catch {
      setUserProfile({
        first_name: "",
        last_name: "",
        email: user.email || "",
        identification_number: "",
        document_type: "",
        state: "",
        phone: "",
        role: "employee",
      });
    }
  }, [user]);

  useEffect(() => {
    if (!isOnline) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchUserProfile();
  }, [fetchUserProfile, isOnline]);

  // --- Navegacion entre pestanas ---
  const handleTabChange = (tab: string) => {
    const tabValue = tab as TabKey;
    navigate(TAB_CONFIG[tabValue].path);
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/login");
    } catch (error) {
      console.error(error);
    }
  };

  // --- Elementos del menu lateral ---
  const menuItems = useMemo(
    (): MenuItem[] =>
      Object.entries(TAB_CONFIG).map(([key, config]) => ({
        key,
        label: config.label,
        icon: config.icon,
        active: activeTab === key,
      })),
    [activeTab],
  );

  // --- Migas de pan ---
  const breadcrumbItems = useMemo((): BreadcrumbItem[] => {
    const breadcrumbs: BreadcrumbItem[] = [];

    if (activeTab === "home") {
      breadcrumbs.push({ label: "Inicio", key: "home", active: true });
    } else {
      breadcrumbs.push({ label: "Inicio", key: "home", active: false });
      breadcrumbs.push({
        label:
          activeTab === "tasks"
            ? "Gestion de Tasks"
            : TAB_CONFIG[activeTab].label,
        key: activeTab,
        active: true,
      });
    }
    return breadcrumbs;
  }, [activeTab]);

  // --- Renderizado de contenido segun la pestana ---
  const renderContent = () => {
    const contentMap: Record<TabKey, React.ReactNode> = {
      home: <EmployeeHomePage />,
      tasks: <TasksPage />,
      cotizaciones: <QuotationsPage />,
      payroll: <PayrollPage />,
        branding: (
          <div className="rounded-2xl border border-surface-border bg-surface-1 p-4 shadow-sm md:p-6">
            <ColorSettings
              title="Tu Estilo"
              description="Personaliza los colores de tu panel"
            />
          </div>
      ),
      about: <ProfilePage />,
    };
    return contentMap[activeTab] || null;
  };

  return (
    <DashboardLayout
      menuItems={menuItems}
      breadcrumbItems={breadcrumbItems}
      onMenuItemClick={handleTabChange}
      onBreadcrumbClick={handleTabChange}
      onLogout={handleLogout}
      userProfile={userProfile}
      userEmail={user?.email || null}
      onMenuToggle={() => {}}
      onMenuStateChange={() => {}}
    >
      {renderContent()}
    </DashboardLayout>
  );
};
