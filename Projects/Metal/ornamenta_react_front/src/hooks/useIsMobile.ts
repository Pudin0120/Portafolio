import { useEffect, useState } from "react";

/**
 * Hook para detectar si la pantalla es movil
 * Retorna true si el ancho de la pantalla es menor a 768px (breakpoint md de Tailwind)
 */
export const useIsMobile = (): boolean => {
  const [isMobile, setIsMobile] = useState<boolean>(() => {
    // Inicializar basado en el tamano actual de la ventana
    return typeof window !== "undefined" ? window.innerWidth < 768 : false;
  });

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return isMobile;
};
