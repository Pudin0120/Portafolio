import { Chip, Spinner, Tooltip } from "@heroui/react";

interface SyncBadgeProps {
  status: "pending" | "synced" | "error";
}

export function SyncBadge({ status }: SyncBadgeProps) {
  const config = {
    pending: { color: "warning" as const, label: "Pending" },
    synced: { color: "success" as const, label: "Sincronizado" },
    error: { color: "danger" as const, label: "Error" },
  }[status];

  return (
    <Tooltip content={config.label}>
      <Chip color={config.color} variant="flat" startContent={status === "pending" ? <Spinner size="sm" /> : null}>
        {config.label}
      </Chip>
    </Tooltip>
  );
}
