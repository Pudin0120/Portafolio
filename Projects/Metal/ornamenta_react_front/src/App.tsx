import { Navigate, Outlet, Route, Routes } from "react-router-dom";
import { useAuth } from "@hooks/useAuth";
import { LoginPage } from "@pages/LoginPage";
import DashboardPage from "@pages/DashboardPage";

import { LoadingState } from "@components/common/LoadingState";
import { InstallPrompt } from "@components/common/InstallPrompt";
import { UpdateAvailableBanner } from "@components/common/UpdateAvailableBanner";
import { shouldBlockAuthenticatedRoutes } from "@services/auth/authUiGuards";

interface ProtectedRouteProps {
	isAuthenticated: boolean;
}

function ProtectedRoute({ isAuthenticated }: ProtectedRouteProps) {
	if (!isAuthenticated) {
		return <Navigate to="/login" />;
	}

	return (
		<>
			<InstallPrompt />
			<Outlet />
		</>
	);
}

function App() {
	const { isAuthenticated, loading, sessionReady } = useAuth();

	const shouldBlockRoutes = shouldBlockAuthenticatedRoutes(loading, sessionReady);

	return (
		<>
			<UpdateAvailableBanner />
			{shouldBlockRoutes ? (
				<div className="flex h-screen w-screen items-center justify-center">
					<LoadingState message="Verificando sesion..." />
				</div>
			) : (
				<Routes>
					<Route
						path="/login"
						element={
							isAuthenticated ? (
								<Navigate to="/" />
							) : (
								<>
									<InstallPrompt />
									<LoginPage />
								</>
							)
						}
					/>
					<Route element={<ProtectedRoute isAuthenticated={isAuthenticated} />}>
						<Route path="/" element={<DashboardPage />} />
						{/* Rutas para products y materials */}
						<Route path="/products/*" element={<DashboardPage />} />
						<Route path="/materials/*" element={<DashboardPage />} />
						<Route path="/payrolls/*" element={<DashboardPage />} />
						<Route path="/quotations/*" element={<DashboardPage />} />
						<Route path="/tasks/*" element={<DashboardPage />} />
						<Route path="/works/*" element={<DashboardPage />} />
						<Route path="/employees/*" element={<DashboardPage />} />
						<Route path="/inventory/*" element={<DashboardPage />} />
						<Route path="/about/*" element={<DashboardPage />} />
						<Route path="/branding/*" element={<DashboardPage />} />
					</Route>
					<Route path="/*" element={<Navigate to="/" />} />
				</Routes>
			)}
		</>
	);
}

export default App;
