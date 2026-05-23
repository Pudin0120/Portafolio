import type { Role } from "@shared/user";

export const shouldBlockAuthenticatedRoutes = (
	loading: boolean,
	sessionReady: boolean,
): boolean => {
	return loading || !sessionReady;
};

export const canShowNoRoleFallback = (
	sessionReady: boolean,
	userRole: Role,
): boolean => {
	return sessionReady && userRole === null;
};

export const resolveProfileAccessToken = (
	sessionToken: string | null,
	firebaseToken: string | null,
): string | null => {
	return sessionToken ?? firebaseToken;
};
