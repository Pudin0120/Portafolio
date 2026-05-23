import { expect, test } from "@playwright/test";
import {
	assertRouteAcceptanceCount,
	getRouteAcceptance,
	listRouteAcceptanceKeys,
	routeAcceptanceSummary,
} from "../src/test-helpers/routeAcceptance";

test("covers all major routes with readiness signals", () => {
	const keys = listRouteAcceptanceKeys();

	expect(keys).toHaveLength(14);

	for (const key of keys) {
		const acceptance = getRouteAcceptance(key);
		expect(acceptance, `Missing acceptance for ${key}`).toBeTruthy();
		expect(acceptance?.signals).toHaveLength(3);
		assertRouteAcceptanceCount(key, 3);
	}
});

test("keeps route readiness metadata aligned and readable", () => {
	const summary = routeAcceptanceSummary();
	const labels = summary.map((entry) => entry.label);

	expect(labels).toContain("ProtectedView");
	expect(labels).toContain("DashboardLayout");
	expect(labels).toContain("MaterialsManager");
	expect(labels).toContain("TasksManager");
	expect(summary.every((entry) => entry.signals.length >= 3)).toBeTruthy();
});

test("documents observable selectors for ready states", () => {
	const materials = getRouteAcceptance("materials-manager");
	const tasks = getRouteAcceptance("tasks-manager");
	const payroll = getRouteAcceptance("payroll-page");

	expect(materials?.signals[0].selector).toContain("Materials table");
	expect(tasks?.signals[2].selector).toContain("Task options");
	expect(payroll?.signals[1].selector).toContain("tablist");
});
