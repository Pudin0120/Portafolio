import React from "react";
import { useAuth } from "@hooks/useAuth";
import { roleViewsConfig } from "@config/roleViews";
import { Card, Button } from "@heroui/react";
import { AlertCircle } from "lucide-react";
import { ProfilePage } from "@pages/ProfilePage";
import { LoadingState } from "@components/common/LoadingState";
import { canShowNoRoleFallback } from "@services/auth/authUiGuards";

export const DashboardPage: React.FC = () => {
	const { userRole, userState, logout, sessionReady } = useAuth();

	const handleLogout = async () => {
		try {
			await logout();
			// La redireccion se maneja automaticamente en App
		} catch (error) {
			console.error("Error al cerrar sesion", error);
		}
	};

	// Si el user esta inactive, mostrar solo su perfil
	if (!sessionReady) {
		return (
			<div className="flex min-h-screen items-center justify-center bg-background p-4">
				<LoadingState message="Verificando sesion..." />
			</div>
		);
	}

	if (userState === "I") {
		return (
			<div className="flex flex-col items-center justify-center min-h-screen bg-background p-4">
				<Card className="w-full max-w-2xl p-6 border-danger-200 bg-danger-50 mb-6">
					<div className="flex items-start gap-4">
						<AlertCircle className="w-8 h-8 text-danger flex-shrink-0 mt-1" />
						<div>
							<h2 className="text-xl font-semibold text-danger mb-2">
								Cuenta Desactivada
							</h2>
							<p className="text-danger-700">
								Tu cuenta ha sido desactivada. Solo puedes ver tu perfil.
								Contacta al administrador si crees que esto es un error.
							</p>
						</div>
					</div>
				</Card>

				<div className="w-full max-w-2xl">
					<h3 className="text-lg font-semibold mb-4 text-foreground">
						Mi Perfil
					</h3>
					<ProfilePage />
				</div>

				<div className="mt-6">
					<Button color="danger" variant="flat" onPress={handleLogout}>
						Cerrar sesion
					</Button>
				</div>
			</div>
		);
	}

	// Obtener el componente de vista correspondiente al rol del user
	const RoleView = userRole
		? (roleViewsConfig[userRole.toLowerCase()] ?? null)
		: null;
	const showNoRoleFallback = canShowNoRoleFallback(sessionReady, userRole);

	return (
		<div className="min-h-screen bg-background">
			<div>
				{RoleView ? (
					<RoleView />
				) : userRole ? (
					<div className="p-10 text-center">
						<h2 className="text-2xl font-bold text-foreground">
							Vista no disponible
						</h2>
						<p className="text-default-500 mt-2">
							No hay una vista configurada para el rol:{" "}
							<strong>{userRole}</strong>
						</p>
						<p className="text-default-400">
							Please, contacta al administrador del sistema.
						</p>
					</div>
				) : showNoRoleFallback ? (
					<div className="p-10 text-center">
						<h2 className="text-2xl font-bold text-foreground">
							Sin rol asignado
						</h2>
						<p className="text-default-500 mt-2">
							Tu cuenta no tiene un rol asignado. Please, contacta al
							administrador del sistema.
						</p>
						<button
							type="button"
							onClick={handleLogout}
							className="mt-4 px-4 py-2 bg-danger text-danger-foreground rounded-xl hover:opacity-90 transition-opacity font-semibold"
						>
							Cerrar sesion
						</button>
					</div>
				) : null}
			</div>
		</div>
	);
};

export default DashboardPage;
