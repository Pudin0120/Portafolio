import { useCallback, useEffect, useState } from "react";

type PermissionSupport = PermissionState | "unsupported" | "unknown";

type PeripheralCapabilities = {
  camera: boolean;
  barcodeDetector: boolean;
  gallery: boolean;
  geolocation: boolean;
  sensors: boolean;
  bluetooth: boolean;
  permissions: {
    camera: PermissionSupport;
    geolocation: PermissionSupport;
  };
};

const defaultCapabilities: PeripheralCapabilities = {
  camera: false,
  barcodeDetector: false,
  gallery: false,
  geolocation: false,
  sensors: false,
  bluetooth: false,
  permissions: {
    camera: "unknown",
    geolocation: "unknown",
  },
};

const queryPermission = async (
  name: PermissionName,
): Promise<PermissionSupport> => {
  if (!navigator.permissions?.query) return "unsupported";

  try {
    const status = await navigator.permissions.query({ name });
    return status.state;
  } catch {
    return "unsupported";
  }
};

export const usePeripheralCapabilities = () => {
  const [capabilities, setCapabilities] =
    useState<PeripheralCapabilities>(defaultCapabilities);

  const refresh = useCallback(async () => {
    const camera = Boolean(navigator.mediaDevices?.getUserMedia);
    const barcodeDetector = Boolean(window.BarcodeDetector);
    const gallery = typeof document !== "undefined";
    const geolocation = "geolocation" in navigator;
    const sensors = Boolean(
      window.AbsoluteOrientationSensor ||
      window.Accelerometer ||
      window.Gyroscope ||
      window.Magnetometer ||
      "DeviceMotionEvent" in window,
    );
    const bluetooth = Boolean(navigator.bluetooth);

    const [cameraPermission, geolocationPermission] = await Promise.all([
      queryPermission("camera" as PermissionName),
      queryPermission("geolocation"),
    ]);

    setCapabilities({
      camera,
      barcodeDetector,
      gallery,
      geolocation,
      sensors,
      bluetooth,
      permissions: {
        camera: cameraPermission,
        geolocation: geolocationPermission,
      },
    });
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { capabilities, refresh };
};
