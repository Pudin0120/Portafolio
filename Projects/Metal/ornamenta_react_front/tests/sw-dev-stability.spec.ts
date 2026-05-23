import { expect, test } from "@playwright/test";
import {
	shouldCleanupDevServiceWorkers,
	shouldReplayQueueOnReconnect,
	shouldShowUpdatePrompt,
	shouldUsePromptBasedUpdates,
} from "../src/services/pwa/pwaLifecycle";

test("enables dev cleanup only on localhost dev hosts", () => {
	expect(shouldCleanupDevServiceWorkers(true, "localhost")).toBeTruthy();
	expect(shouldCleanupDevServiceWorkers(true, "127.0.0.1")).toBeTruthy();
	expect(shouldCleanupDevServiceWorkers(true, "example.com")).toBeFalsy();
	expect(shouldCleanupDevServiceWorkers(false, "localhost")).toBeFalsy();
});

test("uses prompt-based updates for the PWA lifecycle", () => {
	expect(shouldUsePromptBasedUpdates()).toBeTruthy();
	expect(shouldShowUpdatePrompt(true)).toBeTruthy();
	expect(shouldShowUpdatePrompt(false)).toBeFalsy();
});

test("replays sync work once per reconnect epoch", () => {
	expect(shouldReplayQueueOnReconnect(1, 0)).toBeTruthy();
	expect(shouldReplayQueueOnReconnect(1, 1)).toBeFalsy();
	expect(shouldReplayQueueOnReconnect(2, 1)).toBeTruthy();
	expect(shouldReplayQueueOnReconnect(0, 0)).toBeFalsy();
});
