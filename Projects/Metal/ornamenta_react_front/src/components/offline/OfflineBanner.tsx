import { Button, Card, CardBody, Chip } from "@heroui/react";
import { useConnectivity } from "@/providers/ConnectivityProvider";
import { useSyncQueue } from "@/hooks/useSyncQueue";

interface OfflineBannerProps {
  onOpenSyncQueue: () => void;
}

export function OfflineBanner({ onOpenSyncQueue }: OfflineBannerProps) {
  const { isOnline } = useConnectivity();
  const { pendingCount, errorCount } = useSyncQueue();

  if (isOnline) return null;

  return (
    <div className="px-3 pt-3">
      <Card className="border-warning-200 bg-warning-50">
        <CardBody className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap items-center gap-2">
            <Chip color="warning" variant="flat">Sin conexion</Chip>
            <span className="text-sm text-warning-800">Hay {pendingCount} operaciones pendientes y {errorCount} con error.</span>
          </div>
          <Button color="warning" variant="flat" onPress={onOpenSyncQueue}>
            Ver cola
          </Button>
        </CardBody>
      </Card>
    </div>
  );
}
