import { ref, deleteObject } from "firebase/storage";
import { storage } from "./firebase";

/**
 * Servicio para manejar operaciones comunes de Firebase Storage
 */
export const StorageService = {
  /**
   * Borra un archivo dado su URL de descarga
   * @param url URL completa de Firebase Storage
   */
  async deleteFileByUrl(url: string | null | undefined): Promise<void> {
    if (!url || !url.includes("firebasestorage.googleapis.com")) return;
    if (!storage) return;

    try {
      // Extraer el path del objeto desde la URL de Firebase
      // Las URLs son tipo: .../o/tenants%2F...%2Fimage.jpg?alt=media...
      const decodedUrl = decodeURIComponent(url);
      const startIndex = decodedUrl.indexOf("/o/") + 3;
      const endIndex = decodedUrl.indexOf("?");
      const filePath = decodedUrl.substring(
        startIndex,
        endIndex !== -1 ? endIndex : undefined,
      );

      const fileRef = ref(storage, filePath);
      await deleteObject(fileRef);
      console.log(`OK Archivo borrado de Storage: ${filePath}`);
    } catch (error) {
      // Si el archivo no existe, no nos volvemos locos, pero lo logueamos
      console.error("ERROR Error al borrar archivo de Storage:", error);
    }
  },
};
