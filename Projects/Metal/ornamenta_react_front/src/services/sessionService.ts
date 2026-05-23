let accessToken: string | null = null;

export const sessionService = {
  setAccessToken(token: string | null): void {
    accessToken = token;
  },
  clearAccessToken(): void {
    accessToken = null;
  },
  getAccessToken(): string | null {
    return accessToken;
  },
  isOfflineSafe(): boolean {
    return typeof navigator !== "undefined" && !navigator.onLine;
  },
};
