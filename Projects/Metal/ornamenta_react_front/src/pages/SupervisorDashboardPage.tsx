import React, { useState, useEffect, useCallback, useMemo } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  Hammer,
  ClipboardList,
  Home,
  User as UserIcon,
  FileText,
  DollarSign,
  Palette,
} from "lucide-react";
import { useAuth } from "@hooks/useAuth";
import { DashboardLayout } from "@components/DashboardLayout";
import { ProfilePage } from "@pages/ProfilePage";
import { QuotationsPage } from "@pages/QuotationsPage";
import { WorksPage } from "@pages/WorksPage";
import { TasksPage } from "@pages/TasksPage";
import { PayrollPage } from "@pages/PayrollPage";
import { UserService, type UserProfile } from "@services/userService";
import type { MenuItem } from "@components/SidebarMenu";
import type { BreadcrumbItem } from "@components/Breadcrumbs";
import { HomePage } from "./HomePage";
import { ColorSettings } from "@components/settings/ColorSettings";

type TabKey =
  | "home"
  | "works"
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
  works: {
    path: "/works",
    label: "Works",
    icon: <Hammer className="w-5 h-5" />,
  },
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

export const SupervisorDashboardPage: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const activeTab = useMemo<TabKey>(() => {
    const pathname = location.pathname;
    return (
      (Object.entries(TAB_CONFIG).find(
        ([_, config]) => pathname.includes(config.path) && config.path !== "/",
      )?.[0] as TabKey) || "home"
    );
  }, [location.pathname]);

  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);

  const fetchUserProfile = useCallback(async () => {
    if (!user) return;
    try {
      const userData = await UserService.getUserProfile();
      setUserProfile(userData);
    } catch (error) {
      console.error("Error al cargar el perfil del user:", error);
      setUserProfile({
        first_name: "",
        last_name: "",
        email: user.email || "",
        identification_number: "",
        document_type: "",
        state: "",
        phone: "",
        role: "supervisor",
      });
    }
  }, [user]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchUserProfile();
  }, [fetchUserProfile]);

  const handleTabChange = (key: string) => {
    const tabKey = key as TabKey;
    if (TAB_CONFIG[tabKey]) {
      navigate(TAB_CONFIG[tabKey].path);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/login");
    } catch (error) {
      console.error("Error al cerrar sesion:", error);
    }
  };

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

  const breadcrumbItems = useMemo((): BreadcrumbItem[] => {
    const base: BreadcrumbItem[] = [
      { label: "Inicio", key: "home", active: activeTab === "home" },
    ];

    if (activeTab !== "home") {
      base.push({
        label: TAB_CONFIG[activeTab].label,
        key: activeTab,
        active: true,
      });
    }

    return base;
  }, [activeTab]);

  const renderContent = () => {
    const contentMap: Record<TabKey, React.ReactNode> = {
      home: <HomePage />,
      works: <WorksPage />,
      tasks: <TasksPage />,
      cotizaciones: <QuotationsPage />,
      payroll: <PayrollPage />,
      branding: (
        <div className="p-6">
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
