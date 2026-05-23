import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { AuthProvider } from "@context/AuthContext";
import { SidebarProvider } from "@context/SidebarContext";
import { MaterialsProvider } from "@context/MaterialsContext";
import { ProductsProvider } from "@context/ProductsContext";
import { BrowserRouter } from "react-router-dom";
import { HeroUIProvider } from "@heroui/react";
import "./index.css";

import { ThemeProvider } from "./context/ThemeContext";
import { ConnectivityProvider } from "@/providers/ConnectivityProvider";
import { cleanupDevServiceWorkers } from "@services/pwa/devServiceWorkerCleanup";

async function bootstrap(): Promise<void> {
  const rootElement = document.getElementById("root") as HTMLElement | null;
  if (!rootElement) throw new Error("Root element not found");

  await cleanupDevServiceWorkers();

  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <ThemeProvider>
        <HeroUIProvider>
          <ConnectivityProvider>
            <AuthProvider>
              <SidebarProvider>
                <MaterialsProvider>
                  <ProductsProvider>
                    <BrowserRouter
                      future={{
                        v7_startTransition: true,
                        v7_relativeSplatPath: true,
                      }}
                    >
                      <App />
                    </BrowserRouter>
                  </ProductsProvider>
                </MaterialsProvider>
              </SidebarProvider>
            </AuthProvider>
          </ConnectivityProvider>
        </HeroUIProvider>
      </ThemeProvider>
    </React.StrictMode>,
  );
}

void bootstrap();
