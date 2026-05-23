import { Chip, Tooltip } from "@heroui/react";
import { useConnectivity } from "@/providers/ConnectivityProvider";

interface NetworkStatusIndicatorProps {
  showLabel?: boolean;
  className?: string;
}

export function NetworkStatusIndicator({
  showLabel = false,
  className = '',
}: NetworkStatusIndicatorProps) {
  const { isOnline, syncing } = useConnectivity();
  const label = syncing ? "Sincronizando" : isOnline ? "En linea" : "Sin conexion";
  const color = syncing ? "warning" : isOnline ? "success" : "danger";

  return (
    <Tooltip content={label}>
      <Chip className={className} color={color} variant="flat">
        {showLabel ? label : ""}
      </Chip>
    </Tooltip>
  );
}
