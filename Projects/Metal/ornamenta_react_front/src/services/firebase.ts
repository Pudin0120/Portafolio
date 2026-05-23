import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getStorage } from "firebase/storage";

const isFirebaseConfigured = Boolean(import.meta.env.VITE_FIREBASE_API_KEY);

const firebaseConfig = {
  // Tus credenciales del proyecto de desarrollo de Firebase aqui
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

const app = isFirebaseConfigured ? initializeApp(firebaseConfig) : null;

export const auth = app ? getAuth(app) : null;
export const storage = app ? getStorage(app) : null;

if (import.meta.env.DEV) {
  (globalThis as Record<string, unknown>).auth = auth;
  (globalThis as Record<string, unknown>).getToken = async () => {
    if (!auth) {
      console.error("ERROR Firebase no esta configurado.");
      return;
    }

    const user = auth.currentUser;
    if (!user) {
      console.error("ERROR No hay ningun user logueado en Firebase.");
      return;
    }
    const token = await user.getIdToken();
    console.log(" Token para curl:");
    return token;
  };
}
