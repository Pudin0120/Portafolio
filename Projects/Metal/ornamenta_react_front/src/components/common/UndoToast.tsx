import React, { useEffect, useState } from "react";
import { Button, Card, CardBody, Progress } from "@heroui/react";
import { Undo2, X } from "lucide-react";

type UndoToastProps = {
  message: string;
  onUndo: () => void;
  onDismiss: () => void;
  duration?: number; // en milisegundos
};

export const UndoToast: React.FC<UndoToastProps> = ({
  message,
  onUndo,
  onDismiss,
  duration = 5000,
}) => {
  const [progress, setProgress] = useState(100);
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const interval = 50; // actualizar cada 50ms
    const decrement = (interval / duration) * 100;

    const timer = setInterval(() => {
      setProgress((prev) => {
        const next = prev - decrement;
        if (next <= 0) {
          clearInterval(timer);
          setIsVisible(false);
          setTimeout(onDismiss, 300); // delay para animacion
          return 0;
        }
        return next;
      });
    }, interval);

    return () => clearInterval(timer);
  }, [duration, onDismiss]);

  if (!isVisible) return null;

  return (
    <div className="fixed inset-x-3 bottom-3 z-50 animate-in slide-in-from-bottom-4 sm:inset-x-auto sm:right-6 sm:bottom-6">
      <Card className="w-full max-w-md border border-warning-200 bg-warning-50 shadow-lg">
        <CardBody className="gap-3">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1">
              <p className="text-sm font-medium text-warning-800">{message}</p>
            </div>
            <Button
              isIconOnly
              size="sm"
              variant="light"
              onPress={() => {
                setIsVisible(false);
                setTimeout(onDismiss, 300);
              }}
              className="text-warning-600"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>

          <div className="flex gap-2">
            <Button
              size="sm"
              color="warning"
              variant="solid"
              startContent={<Undo2 className="w-4 h-4" />}
              onPress={() => {
                setIsVisible(false);
                setTimeout(() => {
                  onUndo();
                  onDismiss();
                }, 100);
              }}
              className="font-semibold"
            >
              Deshacer
            </Button>
          </div>

          <Progress
            size="sm"
            value={progress}
            color="warning"
            className="mt-1"
            aria-label="Tiempo restante"
          />
        </CardBody>
      </Card>
    </div>
  );
};
