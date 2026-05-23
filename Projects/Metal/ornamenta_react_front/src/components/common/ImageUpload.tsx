import React, { useState, useRef } from "react";
import { Button, Chip, Progress } from "@heroui/react";
import { X, ImageIcon, HardDriveDownload } from "lucide-react";
import { ref, uploadBytesResumable, getDownloadURL } from "firebase/storage";
import { getIdTokenResult } from "firebase/auth";
import { storage } from "@/services/firebase";
import { useAuth } from "@hooks/useAuth";
import {
  createLocalMediaUrl,
  deleteLocalMedia,
  isLocalMediaUrl,
  markLocalMediaSynced,
  saveLocalImage,
} from "@services/localMediaStore";
import { LocalMediaImage } from "./LocalMediaImage";

interface ImageUploadProps {
  value?: string;
  onChange: (url: string) => void;
  folder?: string;
  label?: string;
}

export const ImageUpload: React.FC<ImageUploadProps> = ({
  value,
  onChange,
  folder = "materials",
  label = "Imagen del Material",
}) => {
  const { user } = useAuth();
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      alert("Please, subi un archivo de imagen valido.");
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      alert("La imagen es muy pesada. El maximo permitido es 5MB.");
      return;
    }

    setIsUploading(true);
    setProgress(0);
    let localUrl = "";

    try {
      const localRecord = await saveLocalImage(file, folder);
      localUrl = createLocalMediaUrl(localRecord.id);
      onChange(localUrl);

      if (!navigator.onLine || !user) {
        setIsUploading(false);
        return;
      }

      if (!storage) {
        throw new Error("Firebase Storage no esta configurado.");
      }

      // 1. Obtener el tenant_id de los custom claims del token
      // Forzamos el refresco del token para asegurarnos de tener los ultimos claims
      const tokenResult = await getIdTokenResult(user, true);
      const tenantId = tokenResult.claims.tenant_id as string;

      if (!tenantId) {
        throw new Error(
          "No se encontro un ID de organizacion (tenant_id) asociado a tu cuenta. Contacta al administrador.",
        );
      }

      const fileName = `${Date.now()}_${file.name.replace(/\s/g, "_")}`;
      const storagePath = `tenants/${tenantId}/${folder}/${fileName}`;
      const storageRef = ref(storage, storagePath);

      const uploadTask = uploadBytesResumable(storageRef, file);

      uploadTask.on(
        "state_changed",
        (snapshot) => {
          const p = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
          setProgress(p);
        },
        (error) => {
          console.error("Error al subir a Firebase:", error);
          setIsUploading(false);
        },
        async () => {
          const downloadURL = await getDownloadURL(uploadTask.snapshot.ref);
          onChange(downloadURL);
          markLocalMediaSynced(localUrl).catch(console.error);
          setIsUploading(false);
        },
      );
    } catch (err) {
      console.error("Error en el proceso de imagen:", err);
      if (!localUrl) {
        alert((err as Error).message);
      }
      setIsUploading(false);
    }
  };

  const removeImage = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (isLocalMediaUrl(value)) {
      deleteLocalMedia(value).catch(console.error);
    }
    onChange("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " ") {
      fileInputRef.current?.click();
    }
  };

  return (
    <div className="space-y-2">
      <span className="text-sm font-semibold text-default-700">{label}</span>

      <div
        className="relative group border-2 border-dashed border-default-200 rounded-xl p-4 flex flex-col items-center justify-center bg-default-50 hover:bg-default-100 transition-colors cursor-pointer min-h-[160px]"
        onClick={() => fileInputRef.current?.click()}
        onKeyDown={handleKeyPress}
        tabIndex={0}
        role="button"
        aria-label={label}
      >
        {value ? (
          <div className="relative w-full flex justify-center">
            <LocalMediaImage
              src={value}
              alt="Preview"
              className="max-h-[140px] object-contain rounded-lg"
            />
            {isLocalMediaUrl(value) && (
              <Chip
                size="sm"
                variant="flat"
                color="warning"
                className="absolute left-2 top-2 z-10"
                startContent={<HardDriveDownload className="h-3 w-3" />}
              >
                Local
              </Chip>
            )}
            <Button
              isIconOnly
              color="danger"
              variant="flat"
              size="sm"
              className="absolute -top-2 -right-2 z-10 rounded-full shadow-lg"
              onPress={(e: React.MouseEvent<HTMLButtonElement>) => removeImage(e)}
            >
              <X size={16} />
            </Button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2 w-full h-full py-4">
            <div className="p-3 bg-default-200 rounded-full text-default-500">
              <ImageIcon size={24} />
            </div>
            <div className="text-center">
              <p className="text-xs font-bold text-default-600">Subir imagen</p>
              <p className="text-[10px] text-default-400">JPG, PNG o WEBP</p>
            </div>
          </div>
        )}

        {isUploading && (
          <div className="absolute inset-0 bg-default-50/80 backdrop-blur-sm flex flex-col items-center justify-center p-4 rounded-xl z-20">
            <Progress
              size="sm"
              value={progress}
              color="primary"
              showValueLabel={true}
              className="max-w-md"
              label={navigator.onLine && user ? "Subiendo..." : "Guardando..."}
            />
          </div>
        )}
      </div>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleUpload}
        accept="image/*"
        className="hidden"
      />
    </div>
  );
};
