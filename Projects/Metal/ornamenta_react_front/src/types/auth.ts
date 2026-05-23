import type { User as FirebaseUser, UserCredential } from "firebase/auth";
import type { Role } from "./user";

export interface AuthSessionSnapshot {
	uid: string;
	email: string;
	displayName: string;
	role: Role;
	state: string | null;
	accessToken: string;
	lastValidLoginAt: number;
}

// Tipos relacionados con autenticacion
export interface AuthContextType {
	user: FirebaseUser | null;
	userRole: Role;
	userState: string | null; // "A" = Active, "I" = Inactive
	loading: boolean;
	sessionReady: boolean;
	isAuthenticated: boolean;
	isOffline: boolean;
	revalidateSession: () => Promise<void>;
	login: (email: string, password: string) => Promise<UserCredential>;
	logout: () => Promise<void>;
	resetPassword: (email: string) => Promise<void>;
}
