"use client";

import { usePWAInstall } from "@hooks/usePWAInstall";
import { Download } from "lucide-react";
import { Button } from "@heroui/react";

export function InstallPrompt() {
  const { isInstallable, installPWA } = usePWAInstall();

  if (!isInstallable) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <Button
        color="primary"
        variant="shadow"
        endContent={<Download size={18} />}
        onPress={installPWA}
        className="shadow-lg hover:-translate-y-1 transition-transform"
      >
        Instalar App
      </Button>
    </div>
  );
}
