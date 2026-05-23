const DB_NAME = "serviperfiles-local-media";
const DB_VERSION = 1;
const STORE_NAME = "media";
const LOCAL_MEDIA_PREFIX = "local-media://";

export type LocalMediaRecord = {
  id: string;
  folder: string;
  name: string;
  type: string;
  size: number;
  blob: Blob;
  createdAt: number;
  syncStatus: "pending" | "synced" | "error";
};

const openDatabase = (): Promise<IDBDatabase> => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: "id" });
        store.createIndex("folder", "folder", { unique: false });
        store.createIndex("syncStatus", "syncStatus", { unique: false });
      }
    };

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
};

const withStore = async <T>(
  mode: IDBTransactionMode,
  callback: (store: IDBObjectStore) => IDBRequest<T>,
): Promise<T> => {
  const db = await openDatabase();

  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, mode);
    const request = callback(tx.objectStore(STORE_NAME));

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
    tx.oncomplete = () => db.close();
    tx.onerror = () => {
      db.close();
      reject(tx.error);
    };
  });
};

export const isLocalMediaUrl = (url?: string | null): url is string =>
  Boolean(url?.startsWith(LOCAL_MEDIA_PREFIX));

export const getLocalMediaId = (url: string) =>
  url.replace(LOCAL_MEDIA_PREFIX, "");

export const createLocalMediaUrl = (id: string) => `${LOCAL_MEDIA_PREFIX}${id}`;

export const saveLocalImage = async (
  file: File,
  folder = "materials",
): Promise<LocalMediaRecord> => {
  const id = `${folder}-${Date.now()}-${crypto.randomUUID()}`;
  const record: LocalMediaRecord = {
    id,
    folder,
    name: file.name,
    type: file.type,
    size: file.size,
    blob: file,
    createdAt: Date.now(),
    syncStatus: "pending",
  };

  await withStore("readwrite", (store) => store.put(record));
  return record;
};

export const getLocalMedia = async (
  urlOrId: string,
): Promise<LocalMediaRecord | undefined> => {
  const id = isLocalMediaUrl(urlOrId) ? getLocalMediaId(urlOrId) : urlOrId;
  return withStore<LocalMediaRecord | undefined>("readonly", (store) =>
    store.get(id),
  );
};

export const deleteLocalMedia = async (urlOrId: string): Promise<void> => {
  const id = isLocalMediaUrl(urlOrId) ? getLocalMediaId(urlOrId) : urlOrId;
  await withStore("readwrite", (store) => store.delete(id));
};

export const markLocalMediaSynced = async (urlOrId: string): Promise<void> => {
  const record = await getLocalMedia(urlOrId);
  if (!record) return;

  await withStore("readwrite", (store) =>
    store.put({ ...record, syncStatus: "synced" }),
  );
};
