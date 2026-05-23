import React from "react";
import { X } from "lucide-react";
import Logo from "../assets/Logo.png";

export interface MenuItem {
  key: string;
  label: string;
  icon: React.ReactNode;
  active?: boolean;
}

interface SidebarMenuProps {
  isOpen: boolean;
  onClose: () => void;
  menuItems: MenuItem[];
  onItemClick: (key: string) => void;
  title?: string;
  className?: string;
  isMobile?: boolean;
}

export const SidebarMenu: React.FC<SidebarMenuProps> = ({
  isOpen,
  onClose,
  menuItems,
  onItemClick,
  title = "Serviperfiles A & C",
  className = "",
  isMobile = false,
}) => {
  return (
    <div
      className={`fixed left-0 top-0 z-[999] flex h-dvh max-h-dvh w-[min(260px,calc(100vw-1rem))] flex-col overflow-hidden shadow-xl transition-all duration-300 ease-in-out sm:w-[260px]
        border-r border-sidebar-border bg-sidebar text-sidebar-foreground
        ${isMobile ? (isOpen ? "translate-x-0" : "-translate-x-[110%]") : isOpen ? "translate-x-0" : "-translate-x-full"}
        ${className}`}
    >
      <div className="flex items-center justify-between gap-3 border-b border-sidebar-border p-4 sm:p-6">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-background p-1 shadow-md">
            <img src={Logo} alt="Logo" className="h-auto w-full" />
          </div>
          <h2 className="truncate text-xs font-bold leading-tight text-primary sm:text-sm">
            {title}
          </h2>
        </div>

        <button
          type="button"
          onClick={onClose}
          className={`rounded-full p-2 text-sidebar-muted transition-colors hover:bg-sidebar-hover hover:text-sidebar-foreground ${
            isMobile ? "" : "hidden"
          }`}
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <div className="custom-scrollbar flex-1 overflow-y-auto py-3 sm:py-4">
        {menuItems.map((item) => (
          <button
            key={item.key}
            type="button"
            onClick={() => onItemClick(item.key)}
            className={`group mx-3 my-1 flex w-[calc(100%-24px)] items-center gap-3 rounded-xl px-4 py-3 text-left transition-all duration-200
              ${
                item.active
                  ? "bg-primary font-bold text-primary-foreground shadow-lg shadow-primary/20"
                  : "font-medium text-sidebar-muted hover:bg-sidebar-hover hover:text-sidebar-foreground"
              }`}
          >
            <span
              className={`transition-transform duration-200 ${
                item.active ? "scale-110" : "group-hover:scale-110"
              }`}
            >
              {item.icon}
            </span>
            <span className="text-[15px]">{item.label}</span>
          </button>
        ))}
      </div>

      <div className="border-t border-sidebar-border p-4 text-center sm:p-6">
        <p className="text-xs font-medium text-sidebar-muted/70">
          A(c) 2026 Serviperfiles
        </p>
      </div>
    </div>
  );
};
