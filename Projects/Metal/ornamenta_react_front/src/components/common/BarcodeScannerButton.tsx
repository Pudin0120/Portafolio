import React, { useEffect, useRef, useState } from "react";
import {
  Button,
  Modal,
  ModalBody,
  ModalContent,
  ModalFooter,
  ModalHeader,
  Tooltip,
} from "@heroui/react";
import {
  BrowserMultiFormatReader,
  type IScannerControls,
} from "@zxing/browser";
import { Camera, ScanBarcode, X } from "lucide-react";
import { usePeripheralCapabilities } from "@hooks/usePeripheralCapabilities";

type BarcodeScannerButtonProps = {
  onDetected: (value: string) => void;
  label?: string;
};

const BARCODE_FORMATS: BarcodeDetectorFormat[] = [
  "qr_code",
  "code_128",
  "code_39",
  "code_93",
  "ean_13",
  "ean_8",
  "upc_a",
  "upc_e",
  "itf",
  "data_matrix",
  "pdf417",
];

export const BarcodeScannerButton: React.FC<BarcodeScannerButtonProps> = ({
  onDetected,
  label = "Escanear codigo",
}) => {
  const { capabilities, refresh } = usePeripheralCapabilities();
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [isScanning, setIsScanning] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const zxingControlsRef = useRef<IScannerControls | null>(null);
  const frameRef = useRef<number | undefined>(undefined);

  const stopCamera = () => {
    if (frameRef.current) cancelAnimationFrame(frameRef.current);
    zxingControlsRef.current?.stop();
    zxingControlsRef.current = null;
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    setIsScanning(false);
  };

  useEffect(() => {
    if (!isOpen) {
      stopCamera();
      return;
    }

    let cancelled = false;

    const startScanner = async () => {
      setMessage("");
      await refresh();

      if (!navigator.mediaDevices?.getUserMedia) {
        setMessage("Este navegador no permite acceso a camara.");
        return;
      }

      try {
        const video = videoRef.current;
        if (!video) return;

        if (window.BarcodeDetector) {
          const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: { ideal: "environment" } },
            audio: false,
          });

          if (cancelled) {
            stream.getTracks().forEach((track) => track.stop());
            return;
          }

          streamRef.current = stream;
          video.srcObject = stream;
          await video.play();

          const detector = new window.BarcodeDetector({
            formats: BARCODE_FORMATS,
          });
          setIsScanning(true);

          const scan = async () => {
            if (cancelled || !videoRef.current) return;

            try {
              const codes = await detector.detect(videoRef.current);
              const value = codes[0]?.rawValue;

              if (value) {
                onDetected(value);
                setIsOpen(false);
                return;
              }
            } catch {
              setMessage(
                "No se pudo leer el codigo. Ajusta el enfoque e intenta de nuevo.",
              );
            }

            frameRef.current = requestAnimationFrame(scan);
          };

          frameRef.current = requestAnimationFrame(scan);
          return;
        }

        const reader = new BrowserMultiFormatReader();
        const controls = await reader.decodeFromConstraints(
          {
            video: { facingMode: { ideal: "environment" } },
            audio: false,
          },
          video,
          (result) => {
            const value = result?.getText();
            if (!value || cancelled) return;

            onDetected(value);
            setIsOpen(false);
          },
        );

        zxingControlsRef.current = controls;
        setIsScanning(true);
      } catch (error) {
        const isPermissionError =
          error instanceof DOMException &&
          ["NotAllowedError", "SecurityError"].includes(error.name);

        setMessage(
          isPermissionError
            ? "Permiso de camara denegado. Habilitalo en el navegador para escanear."
            : "No fue posible iniciar la camara.",
        );
      }
    };

    startScanner();

    return () => {
      cancelled = true;
      stopCamera();
    };
  }, [isOpen, onDetected, refresh]);

  const isDisabled = !capabilities.camera;
  const tooltip = !capabilities.camera
    ? "Camara no disponible"
    : capabilities.barcodeDetector
      ? label
      : "Escanear con compatibilidad ZXing";

  return (
    <>
      <Tooltip content={tooltip} delay={400}>
        <Button
          isIconOnly
          aria-label={label}
          size="sm"
          variant="light"
          color="primary"
          isDisabled={isDisabled}
          onPress={() => setIsOpen(true)}
        >
          <ScanBarcode className="h-4 w-4" />
        </Button>
      </Tooltip>

      <Modal
        isOpen={isOpen}
        onOpenChange={setIsOpen}
        placement="center"
        backdrop="blur"
        onClose={stopCamera}
      >
        <ModalContent>
          {(onClose: () => void) => (
            <>
              <ModalHeader className="flex items-center gap-2">
                <Camera className="h-5 w-5 text-primary" />
                Escanear codigo
              </ModalHeader>
              <ModalBody>
                <div className="overflow-hidden rounded-xl border border-default-200 bg-black">
                  <video
                    ref={videoRef}
                    className="aspect-video w-full object-cover"
                    muted
                    playsInline
                  />
                </div>
                <p className="text-xs text-default-500">
                  {message ||
                    (isScanning
                      ? "Apunta la camara al codigo de barras o QR."
                      : "Preparando camara...")}
                </p>
              </ModalBody>
              <ModalFooter>
                <Button
                  variant="flat"
                  color="default"
                  onPress={onClose}
                  startContent={<X className="h-4 w-4" />}
                >
                  Cerrar
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </>
  );
};
