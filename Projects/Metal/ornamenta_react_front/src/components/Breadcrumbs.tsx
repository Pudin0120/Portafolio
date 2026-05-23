import React from "react";
import { Home, ChevronRight } from "lucide-react";

export interface BreadcrumbItem {
  label: string;
  key: string;
  active: boolean;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
  onItemClick: (key: string) => void;
  showHome?: boolean;
}

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({
  items,
  onItemClick,
  showHome = true,
}) => {
  // Mostrar todos los items (no solo los activos) para mostrar la ruta completa
  const displayItems = items;

  const handleHomeClick = () => {
    if (displayItems.length > 0) {
      onItemClick(displayItems[0].key);
    }
  };

  if (displayItems.length === 0) {
    return null;
  }

  return (
    <nav
      className="flex items-center gap-1 text-sm"
      aria-label="Ruta de navegacion"
    >
      {/* Icono Home */}
      {showHome && (
        <button
          type="button"
          onClick={handleHomeClick}
          className="text-primary hover:text-primary-700 p-1.5 rounded-md hover:bg-primary/10 transition-colors duration-150"
          aria-label="Ir al inicio"
          title="Inicio"
        >
          <Home className="w-4 h-4" />
        </button>
      )}

      {/* Items de breadcrumb */}
      {displayItems.map((item, index) => (
        <div key={item.key} className="flex items-center gap-1">
          {/* Separador con chevron */}
          {index > 0 && (
            <ChevronRight
              className="w-4 h-4 text-default-400"
              aria-hidden="true"
            />
          )}

          {/* Boton de breadcrumb */}
          <button
            type="button"
            onClick={() => onItemClick(item.key)}
            className={`px-2.5 py-1 rounded-md transition-all duration-150 ${
              item.active || index === displayItems.length - 1
                ? "cursor-default bg-surface-3 font-semibold text-foreground"
                : "text-primary hover:text-primary-700 hover:bg-primary/10 font-medium"
            }`}
            aria-current={item.active ? "page" : undefined}
          >
            {item.label}
          </button>
        </div>
      ))}
    </nav>
  );
};
