import type { IUserData } from "@shared/user";
import type { Role, RoleResponse } from "@shared/role";
import { apiClient } from "./apiClient";

export interface UserProfile {
	identification_number: string;
	document_type: string;
	first_name: string;
	last_name: string;
	email: string;
	state: string;
	phone: string;
	role: string;
}

export class UserService {
	static async createUser(userData: IUserData): Promise<unknown> {
		return apiClient.post("/admin/users", userData, {
			offlineOperation: {
				entity: "employee",
				operation: "create",
				endpoint: "/admin/users",
				method: "POST",
				body: userData,
			},
		});
	}

	static async createUserWithFirebase(userData: IUserData): Promise<unknown> {
		return this.createUser(userData);
	}

	static async updateUser(
		identificationNumber: string,
		userData: Partial<IUserData>,
	): Promise<unknown> {
		return apiClient.put(`/admin/users/${identificationNumber}`, userData, {
			offlineOperation: {
				entity: "employee",
				operation: "update",
				endpoint: `/admin/users/${identificationNumber}`,
				method: "PUT",
				body: userData,
			},
		});
	}

	static async getCurrentUser(): Promise<UserProfile> {
		return apiClient.get("/users/me");
	}

	static async getRoles(): Promise<Role[]> {
		const data: RoleResponse = await apiClient.get("/roles");

		if (!data.roles || !Array.isArray(data.roles)) {
			throw new Error("Formato de respuesta invalid");
		}

		return data.roles;
	}

	static async getUserProfile(): Promise<UserProfile> {
		return this.getCurrentUser();
	}
}
