import React, { useState, useMemo } from "react";
import { Tabs, Tab } from "@heroui/react";
import { ProductsList } from "./ProductsList";
import { CreateProduct } from "./CreateProduct";
import { CompositeProductForm } from "./composite-creation";
import { Breadcrumbs, BreadcrumbItem } from "../Breadcrumbs";
import { HelpTooltip, helpContent } from "@components/HelpTooltip";

type ProductsManagerProps = {
  onBack: () => void;
  onSubTabChange?: (tab: string) => void;
};

export const ProductsManager: React.FC<ProductsManagerProps> = ({
  onBack,
  onSubTabChange,
}) => {
  const [selectedTab, setSelectedTab] = useState("products");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSuccess = (message: string) => {
    setSuccess(message);
    setError("");
    // Limpiar mensaje de exito despues de 5 segundos
    setTimeout(() => setSuccess(""), 5000);
  };

  const handleError = (message: string) => {
    setError(message);
    setSuccess("");
  };

  // Notificar al padre cuando cambie la subpestana
  React.useEffect(() => {
    if (onSubTabChange) {
      onSubTabChange(selectedTab);
    }
  }, [selectedTab, onSubTabChange]);

  const breadcrumbItems: BreadcrumbItem[] = useMemo(() => {
    const tabLabels: Record<string, string> = {
      products: "Lista de Products",
      "create-simple": "Create Simple Product",
      "create-composite": "Create Composite Product",
    };

    return [
      { label: "Inicio", key: "home", active: false },
      { label: "Products", key: "products", active: false },
      {
        label: tabLabels[selectedTab] || "Gestion",
        key: selectedTab,
        active: true,
      },
    ];
  }, [selectedTab]);

  const handleBreadcrumbClick = (key: string) => {
    if (key === "products") {
      onBack();
    } else if (key.startsWith("create-")) {
      setSelectedTab(key);
    }
  };

  return (
    <div className="mx-auto max-w-6xl p-4">
      <div className="mb-4">
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-semibold text-foreground">
            Gestion de Products
          </h2>
          <HelpTooltip content={helpContent.products} />
        </div>
      </div>

      <Tabs
        selectedKey={selectedTab}
        onSelectionChange={(key: React.Key) => setSelectedTab(key as string)}
        className="mb-4"
      >
        <Tab key="products" title="Products">
          <ProductsList />
        </Tab>

        <Tab key="create-simple" title="Create Simple">
          <div className="mt-4">
            <CreateProduct onBack={onBack} />
          </div>
        </Tab>

        <Tab key="create-composite" title="Create Composite">
          <div className="mt-4">
            {error && (
              <div className="mb-4 rounded-md bg-danger-50 p-3 text-sm text-danger">
                {error}
              </div>
            )}

            {success && (
              <div className="mb-4 rounded-md bg-success-50 p-3 text-sm text-success">
                {success}
              </div>
            )}

            <CompositeProductForm
              onSuccess={handleSuccess}
              onError={handleError}
            />
          </div>
        </Tab>
      </Tabs>
    </div>
  );
};
