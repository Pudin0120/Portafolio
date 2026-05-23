export const shouldCleanupDevServiceWorkers = (
	isDev: boolean,
	hostname: string,
): boolean => {
	return isDev && (hostname === "localhost" || hostname === "127.0.0.1");
};

export const shouldUsePromptBasedUpdates = (): boolean => true;

export const shouldShowUpdatePrompt = (needRefresh: boolean): boolean => {
	return needRefresh;
};

export const shouldReplayQueueOnReconnect = (
	connectionEpoch: number,
	lastHandledEpoch: number,
): boolean => {
	return connectionEpoch > 0 && connectionEpoch !== lastHandledEpoch;
};
