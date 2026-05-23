import React, { useState, useEffect, useCallback, useMemo } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  Users,
  Package,
  Wrench,
  DollarSign,
  Hammer,
  ClipboardList,
  User as UserIcon,
  FileText,
  Home,
  Palette,
} from "lucide-react";
import { useAuth } from "@hooks/useAuth";
import { UserService } from "@services/userService";
import { MaterialsManager } from "@components/products/MaterialsManager";
import { ProductsManager } from "@components/products/ProductsManager";
import { ProfilePage } from "@pages/ProfilePage";
import { PayrollPage } from "@pages/PayrollPage";
import { QuotationsPage } from "@pages/QuotationsPage";
import { WorksPage } from "@pages/WorksPage";
import { TasksPage } from "@pages/TasksPage";
import { HomePage } from "@pages/HomePage";
import { EmployeesManager } from "@components/employees/EmployeesManager";
import { InventoryManager } from "@components/inventory/InventoryManager";
import { DashboardLayout } from "@components/DashboardLayout";
import type { MenuItem } from "@components/SidebarMenu";
import type { BreadcrumbItem } from "@components/Breadcrumbs";
import { ColorSettings } from "@components/settings/ColorSettings";

type TabKey =
  | "home"
  | "empleados"
  | "products"
  | "materials"
  | "inventario"
  | "cotizaciones"
  | "branding"
  | "about";

const TAB_CONFIG: Record<
  TabKey,
  { path: string; label: string; icon: React.ReactNode; breadcrumb: string }
> = {
  home: {
    path: "/",
    label: "Inicio",
    icon: <Home className="w-5 h-5" />,
    breadcrumb: "Inicio",
  },
  empleados: {
    path: "/employees",
    label: "Gestion de Empleados",
    icon: <Users className="w-5 h-5" />,
    breadcrumb: "Gestion de Empleados",
  },
  inventario: {
    path: "/inventory",
    label: "Inventario",
    icon: <Package className="w-5 h-5" />,
    breadcrumb: "Inventario",
  },
  products: {
    path: "/products",
    label: "Products",
    icon: <Wrench className="w-5 h-5" />,
    breadcrumb: "Products",
  },
  materials: {
    path: "/materials",
    label: "Materials",
    icon: <Palette className="w-5 h-5" />,
    breadcrumb: "Materials",
  },
  cotizaciones: {
    path: "/quotations",
    label: "Cotizaciones",
    icon: <FileText className="w-5 h-5" />,
    breadcrumb: "Cotizaciones",
  },
  branding: {
    path: "/branding",
    label: "Personalizacion",
    icon: <Palette className="w-5 h-5" />,
    breadcrumb: "Personalizacion de Tema",
  },
  about: {
    path: "/about",
    label: "Mi Perfil",
    icon: <UserIcon className="w-5 h-5" />,
    breadcrumb: "Mi Perfil",
  },
};

export const ManagerDashboardPage: React.FC = () => {
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

  const [subTab, setSubTab] = useState<string>("");
  const [employeeSubTab, setEmployeeSubTab] = useState<string>("");
  const [userProfile, setUserProfile] = useState<{
    first_name: string;
    last_name: string;
    email: string;
  } | null>(null);

  const fetchUserProfile = useCallback(async () => {
    if (!user) return;
    try {
      const userData = await UserService.getUserProfile();
      setUserProfile({
        first_name: userData.first_name || "",
        last_name: userData.last_name || "",
        email: userData.email || user.email || "",
      });
    } catch {
      setUserProfile({
        first_name: "",
        last_name: "",
        email: user?.email || "",
      });
    }
  }, [user]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchUserProfile();
  }, [fetchUserProfile]);

  const handleTabChange = (tab: string) => {
    const key = tab as TabKey;
    if (TAB_CONFIG[key]) {
      navigate(TAB_CONFIG[key].path);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/login");
    } catch (error) {
      console.error(error);
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
    const breadcrumbs: BreadcrumbItem[] = [];

    if (activeTab === "home") {
      breadcrumbs.push({ label: "Inicio", key: "home", active: true });
    } else {
      breadcrumbs.push({ label: "Inicio", key: "home", active: false });

      breadcrumbs.push({
        label: TAB_CONFIG[activeTab].breadcrumb,
        key: activeTab,
        active: !subTab && !employeeSubTab,
      });

      if (activeTab === "empleados" && employeeSubTab) {
        breadcrumbs.push({
          label: employeeSubTab,
          key: "create-edit-empleado",
          active: true,
        });
      } else if (
        (activeTab === "products" || activeTab === "materials") &&
        subTab
      ) {
        const subTabLabels: Record<string, string> = {
          products: "Lista de Products",
          "create-simple": "Create Simple Product",
          "create-composite": "Create Composite Product",
          materials: "Lista de Materials",
          compositions: "Composiciones",
          types: "Material Types",
        };
        breadcrumbs.push({
          label: subTabLabels[subTab] || subTab,
          key: subTab,
          active: true,
        });
      }
    }

    return breadcrumbs;
  }, [activeTab, subTab, employeeSubTab]);

  const handleBreadcrumbClick = (key: string) => {
    if (activeTab === "products" || activeTab === "materials") return;
    handleTabChange(key);
  };

  const renderContent = () => {
    switch (activeTab) {
      case "home":
        return <HomePage />;
      case "empleados":
        return (
          <EmployeesManager
            onSubTabChange={setEmployeeSubTab}
            onModalOpen={() => {}}
          />
        );
      case "products":
        return (
          <ProductsManager
            onBack={() => navigate("/")}
            onSubTabChange={setSubTab}
          />
        );
      case "materials":
        return <MaterialsManager onSubTabChange={setSubTab} />;
      case "inventario":
        return <InventoryManager />;
      case "cotizaciones":
        return <QuotationsPage />;
      case "branding":
        return (
          <div className="p-6">
            <ColorSettings
              title="Tu Estilo"
              description="Personaliza los colores de tu panel"
            />
          </div>
        );
      case "about":
        return <ProfilePage />;
      default:
        return null;
    }
  };

  return (
    <DashboardLayout
      menuItems={menuItems}
      breadcrumbItems={breadcrumbItems}
      onMenuItemClick={handleTabChange}
      onBreadcrumbClick={handleBreadcrumbClick}
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
