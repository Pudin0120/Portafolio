import type { AuthSessionSnapshot } from "@/types/auth";

const STORAGE_KEY = "serviperfiles.auth.session";

interface AuthSnapshotSource {
	uid: string;
	email?: string | null;
	displayName?: string | null;
}

export function buildAuthSessionSnapshot(
	source: AuthSnapshotSource,
	role: AuthSessionSnapshot["role"],
	state: AuthSessionSnapshot["state"],
	accessToken: string,
	lastValidLoginAt: number = Date.now(),
): AuthSessionSnapshot {
	return {
		uid: source.uid,
		email: source.email ?? "",
		displayName: source.displayName ?? "",
		role,
		state,
		accessToken,
		lastValidLoginAt,
	};
}

export const authSessionStorage = {
	get(): AuthSessionSnapshot | null {
		if (typeof window === "undefined") return null;

		try {
			const raw = localStorage.getItem(STORAGE_KEY);
			if (!raw) return null;
			return JSON.parse(raw) as AuthSessionSnapshot;
		} catch {
			return null;
		}
	},

	set(snapshot: AuthSessionSnapshot): void {
		if (typeof window === "undefined") return;
		localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
	},

	clear(): void {
		if (typeof window === "undefined") return;
		localStorage.removeItem(STORAGE_KEY);
	},
};
