type BarcodeDetectorFormat =
  | "aztec"
  | "code_128"
  | "code_39"
  | "code_93"
  | "codabar"
  | "data_matrix"
  | "ean_13"
  | "ean_8"
  | "itf"
  | "pdf417"
  | "qr_code"
  | "upc_a"
  | "upc_e";

interface DetectedBarcode {
  rawValue: string;
  format: BarcodeDetectorFormat;
  boundingBox: DOMRectReadOnly;
}

interface BarcodeDetector {
  detect(source: ImageBitmapSource): Promise<DetectedBarcode[]>;
}

interface BarcodeDetectorConstructor {
  new (options?: { formats?: BarcodeDetectorFormat[] }): BarcodeDetector;
  getSupportedFormats?: () => Promise<BarcodeDetectorFormat[]>;
}

interface Navigator {
  bluetooth?: unknown;
}

interface Window {
  BarcodeDetector?: BarcodeDetectorConstructor;
  AbsoluteOrientationSensor?: unknown;
  Accelerometer?: unknown;
  Gyroscope?: unknown;
  Magnetometer?: unknown;
}
