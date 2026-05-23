export type RouteAcceptanceKey =
	| "protected-view"
	| "dashboard-layout"
	| "dashboard-page"
	| "employee-dashboard"
	| "admin-dashboard"
	| "manager-dashboard"
	| "supervisor-dashboard"
	| "materials-manager"
	| "employees-manager"
	| "products-manager"
	| "quotations-manager"
	| "works-manager"
	| "tasks-manager"
	| "payroll-page";

export interface RouteAcceptanceSignal {
	label: string;
	description: string;
	selector?: string;
}

export interface RouteAcceptance {
	key: RouteAcceptanceKey;
	label: string;
	signals: RouteAcceptanceSignal[];
	notes?: string;
}

const ROUTE_ACCEPTANCE_REGISTRY: RouteAcceptance[] = [
	{
		key: "protected-view",
		label: "ProtectedView",
		signals: [
			{
				label: "Session gate cleared",
				description:
					"The global loading state has finished and the authenticated outlet may render.",
			},
			{
				label: "Authenticated outlet visible",
				description:
					"The protected route content is mounted instead of the login route.",
				selector: "#main-content",
			},
			{
				label: "Install prompt available",
				description:
					"The authenticated shell shows the install prompt when applicable.",
				selector: "text=Instalar App",
			},
		],
	},
	{
		key: "dashboard-layout",
		label: "DashboardLayout",
		signals: [
			{
				label: "Sidebar toggle visible",
				description:
					"The main shell exposes its menu toggle so the user can navigate.",
				selector: "button[aria-label='Cerrar menu']",
			},
			{
				label: "Breadcrumbs visible",
				description: "Route breadcrumbs are rendered in the header.",
				selector: "[aria-label='Ruta de navegacion']",
			},
			{
				label: "Network indicator visible",
				description: "Connectivity status is shown in the header.",
				selector: "text=En linea",
			},
		],
	},
	{
		key: "dashboard-page",
		label: "DashboardPage",
		signals: [
			{
				label: "Resolved role view",
				description:
					"A role-specific dashboard is visible instead of the loading gate.",
			},
			{
				label: "Resolved state branch",
				description: "Active or inactive session state has been resolved.",
				selector: "text=Cuenta Desactivada",
			},
			{
				label: "No loading gate",
				description: "The startup verification message is no longer visible.",
				selector: "text=Verificando sesion...",
			},
		],
	},
	{
		key: "employee-dashboard",
		label: "EmployeeDashboardPage",
		signals: [
			{
				label: "Profile section visible",
				description: "The employee profile content is rendered.",
				selector: "text=Mi Perfil",
			},
			{
				label: "Tabs are visible",
				description: "The employee route exposes its tab navigation.",
				selector: "[role='tablist']",
			},
			{
				label: "Breadcrumbs visible",
				description: "The employee dashboard breadcrumb trail is rendered.",
				selector: "[aria-label='Ruta de navegacion']",
			},
		],
	},
	{
		key: "admin-dashboard",
		label: "AdminDashboardPage",
		signals: [
			{
				label: "Manager creation section visible",
				description: "The admin entry route shows the manager management area.",
				selector: "text=Gestion de Gerentes",
			},
			{
				label: "Branding tab visible",
				description:
					"Theme personalization is accessible from the admin shell.",
				selector: "text=Branding & Tema",
			},
			{
				label: "Profile tab visible",
				description: "The admin dashboard exposes the profile section.",
				selector: "text=Mi Perfil",
			},
		],
	},
	{
		key: "manager-dashboard",
		label: "ManagerDashboardPage",
		signals: [
			{
				label: "Employees tab visible",
				description:
					"The manager shell exposes the employee management section.",
				selector: "text=Gestion de Empleados",
			},
			{
				label: "Products tab visible",
				description: "The manager shell exposes the product area.",
				selector: "text=Products",
			},
			{
				label: "Materials tab visible",
				description: "The manager shell exposes the materials area.",
				selector: "text=Materials",
			},
		],
	},
	{
		key: "supervisor-dashboard",
		label: "SupervisorDashboardPage",
		signals: [
			{
				label: "Works tab visible",
				description: "The supervisor shell exposes the works section.",
				selector: "text=Works",
			},
			{
				label: "Tasks tab visible",
				description: "The supervisor shell exposes the task section.",
				selector: "text=Tasks",
			},
			{
				label: "Profile tab visible",
				description: "The supervisor dashboard exposes the profile section.",
				selector: "text=Mi Perfil",
			},
		],
	},
	{
		key: "materials-manager",
		label: "MaterialsManager",
		signals: [
			{
				label: "Materials table visible",
				description: "The main materials table has rendered.",
				selector: "[aria-label='Materials table']",
			},
			{
				label: "Create material button visible",
				description: "The primary create action is present.",
				selector: "text=Create Material",
			},
			{
				label: "Search input visible",
				description: "The materials search control is ready for typing.",
				selector: "input[placeholder*='Search']",
			},
		],
	},
	{
		key: "employees-manager",
		label: "EmployeesManager",
		signals: [
			{
				label: "Employees table visible",
				description: "The main employee table has rendered.",
				selector: "[aria-label='Tabla de empleados']",
			},
			{
				label: "Create employee button visible",
				description: "The primary create action is present.",
				selector: "text=Create Employee",
			},
			{
				label: "State toggle actions visible",
				description: "Employee action controls are available in the table.",
				selector: "text=Edit",
			},
		],
	},
	{
		key: "products-manager",
		label: "ProductsManager",
		signals: [
			{
				label: "Products tab visible",
				description: "The products list tab is present.",
				selector: "text=Products",
			},
			{
				label: "Create simple tab visible",
				description: "The simple product form tab is available.",
				selector: "text=Create Simple",
			},
			{
				label: "Create composite tab visible",
				description: "The composite product form tab is available.",
				selector: "text=Create Composite",
			},
		],
	},
	{
		key: "quotations-manager",
		label: "QuotationsManager",
		signals: [
			{
				label: "Quotations list visible",
				description: "The quotations list tab is present.",
				selector: "text=Cotizaciones",
			},
			{
				label: "Create quotation tab visible",
				description: "The create quotation flow is available.",
				selector: "text=Create Quotation",
			},
			{
				label: "Tab navigation visible",
				description: "The route exposes interactive tabs.",
				selector: "[role='tablist']",
			},
		],
	},
	{
		key: "works-manager",
		label: "WorksManager",
		signals: [
			{
				label: "Works list visible",
				description: "The in-progress works list is present.",
				selector: "text=En Progreso",
			},
			{
				label: "Delivered tab visible",
				description: "The delivered works list is accessible.",
				selector: "text=Entregados",
			},
			{
				label: "Edit flow available",
				description: "The edit draft flow can be opened from the route.",
				selector: "text=Edit",
			},
		],
	},
	{
		key: "tasks-manager",
		label: "TasksManager",
		signals: [
			{
				label: "My tasks tab visible",
				description: "The personal tasks list tab is available.",
				selector: "text=Mis Tasks",
			},
			{
				label: "Role gated tab visible",
				description: "Managers and supervisors can see the all-tasks tab.",
				selector: "text=Todas las Tasks",
			},
			{
				label: "Task filters visible",
				description: "The route exposes its task filtering controls.",
				selector: "[aria-label='Task options']",
			},
		],
	},
	{
		key: "payroll-page",
		label: "PayrollPage",
		signals: [
			{
				label: "Payroll title visible",
				description: "The payroll route has rendered its page heading.",
				selector: "text=Payrolls",
			},
			{
				label: "Tab navigation visible",
				description: "The route exposes a tabbed payroll interface.",
				selector: "[role='tablist']",
			},
			{
				label: "Role-specific tab visible",
				description:
					"The manager or employee view is present depending on role.",
				selector: "text=My Payroll",
			},
		],
	},
];

export const listRouteAcceptanceKeys = (): RouteAcceptanceKey[] => {
	return ROUTE_ACCEPTANCE_REGISTRY.map((entry) => entry.key);
};

export const getRouteAcceptance = (
	key: RouteAcceptanceKey,
): RouteAcceptance | undefined => {
	return ROUTE_ACCEPTANCE_REGISTRY.find((entry) => entry.key === key);
};

export const getRouteReadySignals = (
	key: RouteAcceptanceKey,
): RouteAcceptanceSignal[] => {
	return getRouteAcceptance(key)?.signals ?? [];
};

export const assertRouteAcceptanceCount = (
	key: RouteAcceptanceKey,
	minSignals: number = 3,
): void => {
	const acceptance = getRouteAcceptance(key);
	if (!acceptance) {
		throw new Error(`Missing route acceptance definition for ${key}`);
	}

	if (acceptance.signals.length < minSignals) {
		throw new Error(
			`Route ${key} has ${acceptance.signals.length} readiness signals; expected at least ${minSignals}`,
		);
	}
};

export interface RouteWaitTarget {
	waitForSelector: (selector: string) => Promise<void>;
}

export const waitForRouteReady = async (
	target: RouteWaitTarget,
	key: RouteAcceptanceKey,
): Promise<void> => {
	const signals = getRouteReadySignals(key);
	for (const signal of signals) {
		if (signal.selector) {
			// Each selector is an observable readiness cue; the caller can decide
			// which one matters most for its assertion.
			// We wait sequentially so tests can reuse the same helper contract.
			// eslint-disable-next-line no-await-in-loop
			await target.waitForSelector(signal.selector);
		}
	}
};

export const routeAcceptanceSummary = (): RouteAcceptance[] => {
	return [...ROUTE_ACCEPTANCE_REGISTRY];
};
