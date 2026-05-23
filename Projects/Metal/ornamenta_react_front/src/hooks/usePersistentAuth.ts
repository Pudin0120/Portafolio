import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { User as FirebaseUser } from "firebase/auth";
import {
	onAuthStateChanged,
	signInWithEmailAndPassword,
	signOut,
	sendPasswordResetEmail,
} from "firebase/auth";
import { auth } from "@services/firebase";
import { sessionService } from "@services/sessionService";
import {
	authSessionStorage,
	buildAuthSessionSnapshot,
} from "@services/auth/sessionStorage";
import type { AuthContextType, AuthSessionSnapshot } from "@shared/auth";
import type { Role } from "@shared/user";
import { useConnectivity } from "@/providers/ConnectivityProvider";
import {
	executePendingOperation,
	syncPendingOperations,
} from "@services/sync/syncManager";
import { shouldReplayQueueOnReconnect } from "@services/pwa/pwaLifecycle";

const API_BASE_URL: string = import.meta.env.VITE_API_URL;

export function usePersistentAuth(): AuthContextType {
	const { isOnline, setSyncing, connectionEpoch } = useConnectivity();
	const [user, setUser] = useState<FirebaseUser | null>(null);
	const [snapshot, setSnapshot] = useState<AuthSessionSnapshot | null>(() =>
		authSessionStorage.get(),
	);
	const [userRole, setUserRole] = useState<Role>(() => snapshot?.role || null);
	const [userState, setUserState] = useState<string | null>(
		() => snapshot?.state || null,
	);
	const [loading, setLoading] = useState<boolean>(true);
	const snapshotRef = useRef<AuthSessionSnapshot | null>(snapshot);
	const hydratedRef = useRef(false);
	const lastSyncedConnectionEpochRef = useRef(0);
	const [authReady, setAuthReady] = useState<boolean>(() => !auth);

	useEffect(() => {
		snapshotRef.current = snapshot;
	}, [snapshot]);

	const isAuthenticated = Boolean(user || snapshot);

	const persistSnapshot = useCallback(
		async (
			currentUser: FirebaseUser,
			nextRole: Role = userRole,
			nextState: string | null = userState,
		): Promise<void> => {
			const accessToken = await currentUser.getIdToken();
			const snapshotData = buildAuthSessionSnapshot(
				{
					uid: currentUser.uid,
					email: currentUser.email,
					displayName: currentUser.displayName,
				},
				nextRole,
				nextState,
				accessToken,
			);

			sessionService.setAccessToken(accessToken);
			authSessionStorage.set(snapshotData);
			setSnapshot(snapshotData);
		},
		[userRole, userState],
	);

	const syncUserProfile = useCallback(
		async (currentUser?: FirebaseUser | null): Promise<void> => {
			if (!isOnline) return;

			const accessToken = currentUser
				? await currentUser.getIdToken()
				: snapshotRef.current?.accessToken;

			if (!accessToken) return;

			try {
				const response = await fetch(`${API_BASE_URL}/users/me`, {
					method: "GET",
					headers: { Authorization: `Bearer ${accessToken}` },
				});

				if (!response.ok) {
					// Treat 401/403 as authentication failures rather than generic offline errors
					if (response.status === 401 || response.status === 403) {
						try {
							sessionService.clearAccessToken();
							authSessionStorage.clear();
							setSnapshot(null);
							setUser(null);
							setUserRole(null);
							setUserState(null);
						} catch {
							// best-effort cleanup
						}
						return;
					}
					return;
				}

				const userData = (await response.json()) as {
					role?: string;
					state?: string;
				};
				const determinedRole =
					userData.role && typeof userData.role === "string"
						? userData.role
						: null;
				const determinedState = userData.state ?? null;

				setUserRole(determinedRole);
				setUserState(determinedState);
				sessionService.setAccessToken(accessToken);

				if (currentUser) {
					await persistSnapshot(currentUser, determinedRole, determinedState);
				} else if (snapshotRef.current) {
					const updatedSnapshot = buildAuthSessionSnapshot(
						{
							uid: snapshotRef.current.uid,
							email: snapshotRef.current.email,
							displayName: snapshotRef.current.displayName,
						},
						determinedRole,
						determinedState,
						accessToken,
					);
					authSessionStorage.set(updatedSnapshot);
					setSnapshot(updatedSnapshot);
				}
			} catch {
				// Mantener sesion local si la revalidacion falla
			}
		},
		[isOnline, persistSnapshot],
	);

	const revalidateSession = useCallback(async (): Promise<void> => {
		const currentUser = auth?.currentUser;
		if (!currentUser || !isOnline) return;
		await syncUserProfile(currentUser);
	}, [isOnline, syncUserProfile]);

	useEffect(() => {
		if (!snapshotRef.current?.accessToken) return;
		if (!isOnline) return;
		if (
			!shouldReplayQueueOnReconnect(
				connectionEpoch,
				lastSyncedConnectionEpochRef.current,
			)
		) {
			return;
		}

		lastSyncedConnectionEpochRef.current = connectionEpoch;
		hydratedRef.current = false;
		void (async () => {
			setSyncing(true);
			try {
				await revalidateSession();
				await syncPendingOperations(executePendingOperation);
			} finally {
				setSyncing(false);
			}
		})();
	}, [connectionEpoch, isOnline, revalidateSession, setSyncing]);

	useEffect(() => {
		const applySnapshot = (currentSnapshot: AuthSessionSnapshot): void => {
			setUser(null);
			setUserRole(currentSnapshot.role);
			setUserState(currentSnapshot.state);
			sessionService.setAccessToken(currentSnapshot.accessToken);
		};

		if (!auth) {
			void Promise.resolve().then(() => {
				if (snapshotRef.current) {
					applySnapshot(snapshotRef.current);
				}
				setAuthReady(true);
				setLoading(false);
			});
			return;
		}

		const unsubscribe = onAuthStateChanged(
			auth,
			async (currentUser) => {
				if (currentUser) {
					setUser(currentUser);
					if (snapshotRef.current) {
						applySnapshot(snapshotRef.current);
					}
					if (isOnline && !hydratedRef.current) {
						hydratedRef.current = true;
						await syncUserProfile(currentUser);
					}
					setAuthReady(true);
					setLoading(false);
					return;
				}

				if (snapshotRef.current) {
					applySnapshot(snapshotRef.current);
					if (isOnline && !hydratedRef.current) {
						hydratedRef.current = true;
						await syncUserProfile(null);
					}
					setAuthReady(true);
					setLoading(false);
					return;
				}

				setUser(null);
				setUserRole(null);
				setUserState(null);
				sessionService.clearAccessToken();
				authSessionStorage.clear();
				setSnapshot(null);
				setAuthReady(true);
				setLoading(false);
			},
			() => {
				if (snapshotRef.current) {
					applySnapshot(snapshotRef.current);
				} else {
					setUser(null);
					setUserRole(null);
					setUserState(null);
					sessionService.clearAccessToken();
				}
				setAuthReady(true);
				setLoading(false);
			},
		);

		return () => unsubscribe();
	}, [isOnline, syncUserProfile]);

	useEffect(() => {
		if (snapshot && !isOnline) {
			sessionService.setAccessToken(snapshot.accessToken);
		}
	}, [isOnline, snapshot]);

	const login = useCallback((email: string, password: string) => {
		if (!auth) return Promise.reject(new Error("Firebase no configurado"));
		return signInWithEmailAndPassword(auth, email, password);
	}, []);

	const logout = useCallback(async () => {
		if (!isOnline) {
			throw new Error("No se puede cerrar sesion sin conexion");
		}
		setSnapshot(null);
		authSessionStorage.clear();
		sessionService.clearAccessToken();
		setUserRole(null);
		setUserState(null);
		await signOut(auth as NonNullable<typeof auth>);
	}, [isOnline]);

	const resetPassword = useCallback((email: string) => {
		if (!auth) return Promise.reject(new Error("Firebase no configurado"));
		return sendPasswordResetEmail(auth, email);
	}, []);

	const value = useMemo<AuthContextType>(
		() => ({
			user,
			userRole,
			userState,
			loading: loading || !authReady,
			sessionReady: authReady,
			isAuthenticated,
			isOffline: !isOnline,
			revalidateSession,
			login,
			logout,
			resetPassword,
		}),
		[
			user,
			userRole,
			userState,
			loading,
			authReady,
			isAuthenticated,
			isOnline,
			revalidateSession,
			login,
			logout,
			resetPassword,
		],
	);

	return value;
}
