import React, { useState, useEffect } from "react";
import { useAuth } from "@hooks/useAuth";
import { getErrorMessage } from "@utils/errorHandling";
import { sessionService } from "@services/sessionService";
import { resolveProfileAccessToken } from "@services/auth/authUiGuards";

interface UserProfile {
	identification_number: string;
	document_type: string;
	first_name: string;
	last_name: string;
	email: string;
	state: string;
	firebase_uid: string;
	phone: string;
	role: string;
}

export const ProfilePage: React.FC = () => {
	const { user, isAuthenticated, sessionReady } = useAuth();
	const [profile, setProfile] = useState<UserProfile | null>(null);
	const [isLoading, setIsLoading] = useState(true);
	const [error, setError] = useState("");

	useEffect(() => {
		const fetchProfile = async () => {
			if (!sessionReady) {
				return;
			}

			try {
				setIsLoading(true);
				setError("");

				const sessionToken = sessionService.getAccessToken();
				const firebaseToken = user ? await user.getIdToken() : null;
				const token = resolveProfileAccessToken(sessionToken, firebaseToken);

				if (!token) {
					setError(
						isAuthenticated
							? "No se pudo resolver la sesion autenticada"
							: "No hay user autenticado",
					);
					return;
				}

				const response = await fetch(
					`${import.meta.env.VITE_API_URL}/users/me`,
					{
						method: "GET",
						headers: {
							Authorization: `Bearer ${token}`,
							"Content-Type": "application/json",
						},
					},
				);

				if (!response.ok) {
					throw new Error(`Error ${response.status}: ${response.statusText}`);
				}

				const userData: UserProfile = await response.json();
				setProfile(userData);
			} catch (err) {
				const errorMessage = getErrorMessage(err);
				setError(`Error al cargar el perfil: ${errorMessage}`);
			} finally {
				setIsLoading(false);
			}
		};

		fetchProfile();
	}, [user, isAuthenticated, sessionReady]);

	const getDocumentTypeLabel = (type: string) => {
		switch (type) {
			case "CC":
				return "Cedula de Ciudadania";
			case "CE":
				return "Cedula de Extranjeria";
			case "NI":
				return "NIT";
			default:
				return type;
		}
	};

	const getStateLabel = (state: string) =>
		state === "A" ? "Active" : "Inactive";

	// Loading state
	if (isLoading) {
		return (
			<div className="flex flex-col items-center justify-center py-20 text-center">
				<h2 className="text-2xl font-semibold mb-3 text-foreground">
					Mi Perfil
				</h2>
				<p className="text-default-500">Cargando information del perfil...</p>
			</div>
		);
	}

	// Error state
	if (error) {
		return (
			<div className="max-w-3xl mx-auto p-6">
				<h2 className="text-2xl font-semibold mb-4 text-foreground">
					Mi Perfil
				</h2>
				<div className="p-4 bg-danger-50 border border-danger-200 rounded-lg text-danger-700 font-medium">
					{error}
				</div>
			</div>
		);
	}

	// No profile
	if (!profile) {
		return (
			<div className="flex flex-col items-center justify-center py-20 text-center">
				<h2 className="text-2xl font-semibold mb-3 text-foreground">
					Mi Perfil
				</h2>
				<p className="text-default-500">
					No se encontro information del perfil.
				</p>
			</div>
		);
	}

	// Perfil cargado
	return (
		<div className="max-w-3xl mx-auto p-6">
			<h2 className="text-3xl font-semibold mb-6 text-foreground border-b border-divider pb-2">
				Mi Perfil
			</h2>

			<div className="flex flex-col gap-6">
				{/* Informacion Personal */}
				<section className="rounded-xl border border-surface-border bg-surface-elevated p-5 shadow-sm">
					<h3 className="text-lg font-semibold mb-4 text-foreground/80">
						Informacion Personal
					</h3>
					<div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
						<div>
							<span className="block text-sm font-semibold text-default-600">
								Document Type:
							</span>
							<p className="text-foreground">
								{getDocumentTypeLabel(profile.document_type)}
							</p>
						</div>
						<div>
							<span className="block text-sm font-semibold text-default-600">
								Document Number:
							</span>
							<p className="text-foreground">{profile.identification_number}</p>
						</div>
						<div>
							<span className="block text-sm font-semibold text-default-600">
								Nombres:
							</span>
							<p className="text-foreground">{profile.first_name}</p>
						</div>
						<div>
							<span className="block text-sm font-semibold text-default-600">
								Apellidos:
							</span>
							<p className="text-foreground">{profile.last_name}</p>
						</div>
					</div>
				</section>

				{/* Informacion de Contacto */}
				<section className="rounded-xl border border-surface-border bg-surface-elevated p-5 shadow-sm">
					<h3 className="text-lg font-semibold mb-4 text-foreground/80">
						Informacion de Contacto
					</h3>
					<div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
						<div>
							<span className="block text-sm font-semibold text-default-600">
								Email:
							</span>
							<p className="text-foreground">{profile.email}</p>
						</div>
						<div>
							<span className="block text-sm font-semibold text-default-600">
								Telefono:
							</span>
							<p className="text-foreground">
								{profile.phone || "No especificado"}
							</p>
						</div>
					</div>
				</section>

				{/* Informacion Laboral */}
				<section className="rounded-xl border border-surface-border bg-surface-elevated p-5 shadow-sm">
					<h3 className="text-lg font-semibold mb-4 text-foreground/80">
						Informacion Laboral
					</h3>
					<div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
						<div>
							<span className="block text-sm font-semibold text-default-600">
								Rol:
							</span>
							<div className="mt-1">
								<span className="inline-block bg-primary text-primary-foreground text-sm px-3 py-1 rounded-md font-medium">
									{profile.role}
								</span>
							</div>
						</div>
						<div>
							<span className="block text-sm font-semibold text-default-600">
								Status:
							</span>
							<div className="mt-1">
								<span
									className={`inline-block text-sm px-3 py-1 rounded-md font-medium ${
										profile.state === "A"
											? "bg-success text-success-foreground"
											: "bg-danger text-danger-foreground"
									}`}
								>
									{getStateLabel(profile.state)}
								</span>
							</div>
						</div>
					</div>
				</section>
			</div>
		</div>
	);
};
