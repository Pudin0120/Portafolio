import React, {
	createContext,
	useContext,
	useReducer,
	useCallback,
	useEffect,
	useRef,
} from "react";
import { Material } from "@/types/products";
import { useAuth } from "@hooks/useAuth";
import { useDebounce } from "@hooks/useDebounce";
import { StorageService } from "@services/storageService";
import { useConnectivity } from "@/providers/ConnectivityProvider";
import { sessionService } from "@services/sessionService";
import { apiClient } from "@services/apiClient";

// ============================================================================
// TYPES
// ============================================================================

type PaginationMeta = {
	currentPage: number;
	pageSize: number;
	totalItems: number;
	totalPages: number;
};

type MaterialsState = {
	materials: Material[];
	isLoading: boolean;
	error: string | null;
	searchQuery: string;
	pagination: PaginationMeta;
	// Undo action state
	deletedMaterial: { material: Material; timestamp: number } | null;
};

type MaterialsAction =
	| { type: "FETCH_START" }
	| {
			type: "FETCH_SUCCESS";
			payload: { materials: Material[]; total: number };
	  }
	| { type: "FETCH_ERROR"; payload: string }
	| { type: "SET_SEARCH_QUERY"; payload: string }
	| { type: "SET_PAGE"; payload: number }
	| { type: "ADD_MATERIAL"; payload: Material }
	| { type: "UPDATE_MATERIAL"; payload: Material }
	| { type: "DELETE_MATERIAL_OPTIMISTIC"; payload: string }
	| { type: "PREPARE_UNDO_DELETE"; payload: Material }
	| { type: "CONFIRM_DELETE_UI" }
	| { type: "UNDO_DELETE" }
	| { type: "CLEAR_ERROR" };

type MaterialsContextType = {
	state: MaterialsState;
	fetchMaterials: () => Promise<void>;
	setSearchQuery: (query: string) => void;
	setPage: (page: number) => void;
	addMaterial: (material: Material) => void;
	updateMaterial: (material: Material) => void;
	deleteMaterial: (materialId: string) => Promise<void>;
	undoDelete: () => void;
	clearError: () => void;
};

// ============================================================================
// CONSTANTS
// ============================================================================

const PAGE_SIZE = 20;
const UNDO_TIMEOUT_MS = 5000;

// ============================================================================
// REDUCER
// ============================================================================

const initialState: MaterialsState = {
	materials: [],
	isLoading: false,
	error: null,
	searchQuery: "",
	pagination: {
		currentPage: 1,
		pageSize: PAGE_SIZE,
		totalItems: 0,
		totalPages: 0,
	},
	deletedMaterial: null,
};

function materialsReducer(
	state: MaterialsState,
	action: MaterialsAction,
): MaterialsState {
	switch (action.type) {
		case "FETCH_START":
			return {
				...state,
				isLoading: true,
				error: null,
			};

		case "FETCH_SUCCESS": {
			const { materials, total } = action.payload;
			return {
				...state,
				materials,
				isLoading: false,
				pagination: {
					...state.pagination,
					totalItems: total,
					totalPages: Math.max(1, Math.ceil(total / PAGE_SIZE)),
				},
			};
		}

		case "FETCH_ERROR":
			return {
				...state,
				isLoading: false,
				error: action.payload,
			};

		case "SET_SEARCH_QUERY":
			return {
				...state,
				searchQuery: action.payload,
				pagination: { ...state.pagination, currentPage: 1 },
			};

		case "SET_PAGE":
			return {
				...state,
				pagination: { ...state.pagination, currentPage: action.payload },
			};

		case "ADD_MATERIAL":
			return {
				...state,
				materials: [action.payload, ...state.materials].slice(0, PAGE_SIZE),
				pagination: {
					...state.pagination,
					totalItems: state.pagination.totalItems + 1,
					totalPages: Math.max(
						1,
						Math.ceil((state.pagination.totalItems + 1) / PAGE_SIZE),
					),
				},
			};

		case "UPDATE_MATERIAL":
			return {
				...state,
				materials: state.materials.map((m) =>
					m.id === action.payload.id ? action.payload : m,
				),
			};

		case "DELETE_MATERIAL_OPTIMISTIC":
			return {
				...state,
				materials: state.materials.filter((m) => m.id !== action.payload),
				pagination: {
					...state.pagination,
					totalItems: Math.max(0, state.pagination.totalItems - 1),
					totalPages: Math.max(
						1,
						Math.ceil(Math.max(0, state.pagination.totalItems - 1) / PAGE_SIZE),
					),
				},
			};

		case "PREPARE_UNDO_DELETE":
			return {
				...state,
				deletedMaterial: {
					material: action.payload,
					timestamp: Date.now(),
				},
			};

		case "CONFIRM_DELETE_UI":
			return {
				...state,
				deletedMaterial: null,
			};

		case "UNDO_DELETE":
			if (!state.deletedMaterial) return state;
			return {
				...state,
				materials: [state.deletedMaterial.material, ...state.materials].slice(
					0,
					PAGE_SIZE,
				),
				pagination: {
					...state.pagination,
					totalItems: state.pagination.totalItems + 1,
					totalPages: Math.max(
						1,
						Math.ceil((state.pagination.totalItems + 1) / PAGE_SIZE),
					),
				},
				deletedMaterial: null,
			};

		case "CLEAR_ERROR":
			return {
				...state,
				error: null,
			};

		default:
			return state;
	}
}

// ============================================================================
// CONTEXT
// ============================================================================

const MaterialsContext = createContext<MaterialsContextType | undefined>(
	undefined,
);

// ============================================================================
// PROVIDER
// ============================================================================

export const MaterialsProvider: React.FC<{ children: React.ReactNode }> = ({
	children,
}) => {
	const [state, dispatch] = useReducer(materialsReducer, initialState);
	const { user, isAuthenticated, sessionReady } = useAuth();
	const { isOnline, connectionEpoch } = useConnectivity();
	const debouncedSearchQuery = useDebounce(state.searchQuery, 500);

	// Referencias para el timeout del delete real
	const deleteTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
	const materialPendingRef = useRef<Material | null>(null);

	// Limpieza al desmontar
	useEffect(() => {
		return () => {
			if (deleteTimeoutRef.current) {
				clearTimeout(deleteTimeoutRef.current);
			}
		};
	}, []);

	const fetchMaterials = useCallback(async () => {
		// We allow fetching if either we have a Firebase user OR the session is ready with a snapshot
		if (!isAuthenticated && !sessionReady) return;

		dispatch({ type: "FETCH_START" });
		try {
			const searchParams = new URLSearchParams();
			searchParams.set("limit", String(PAGE_SIZE));
			searchParams.set(
				"offset",
				String((state.pagination.currentPage - 1) * PAGE_SIZE),
			);
			if (debouncedSearchQuery.trim()) {
				searchParams.set("search", debouncedSearchQuery.trim());
			}

			const data = await apiClient.get<{ materials: Material[]; total: number }>(
				`/materials/?${searchParams.toString()}`,
			);
			dispatch({
				type: "FETCH_SUCCESS",
				payload: { materials: data?.materials || [], total: data?.total || 0 },
			});
		} catch (err) {
			dispatch({
				type: "FETCH_ERROR",
				payload:
					err instanceof Error ? err.message : "Error al cargar materials",
			});
		}
	}, [state.pagination.currentPage, debouncedSearchQuery, isAuthenticated, sessionReady]);

	useEffect(() => {
		if (!isOnline || (!user && !sessionReady)) return;
		void fetchMaterials();
	}, [fetchMaterials, isOnline, connectionEpoch, user, sessionReady]);

	const setSearchQuery = useCallback((query: string) => {
		dispatch({ type: "SET_SEARCH_QUERY", payload: query });
	}, []);

	const setPage = useCallback((page: number) => {
		dispatch({ type: "SET_PAGE", payload: page });
	}, []);

	const addMaterial = useCallback((material: Material) => {
		dispatch({ type: "ADD_MATERIAL", payload: material });
	}, []);

	const updateMaterial = useCallback((material: Material) => {
		dispatch({ type: "UPDATE_MATERIAL", payload: material });
	}, []);

	const executeRealDelete = useCallback(
		async (material: Material) => {
			if (!user) return;
			try {
				await apiClient.delete(`/materials/${material.id}`);

				// Si la eliminacion en el backend fue exitosa, borramos la imagen de Storage si existe
				const imageUrl = material.image_url || material.properties?.image_url;
				if (imageUrl && typeof imageUrl === "string") {
					StorageService.deleteFileByUrl(imageUrl).catch((err) =>
						console.error(
							" No se pudo borrar la imagen de Storage tras delete el material:",
							err,
						),
					);
				}

				dispatch({ type: "CONFIRM_DELETE_UI" });
			} catch (err) {
				console.error("ERROR Error real delete material:", err);
				dispatch({
					type: "FETCH_ERROR",
					payload:
						err instanceof Error
							? err.message
							: "Error al delete el material",
				});
				// Rollback: devolvemos el material a la lista
				dispatch({ type: "ADD_MATERIAL", payload: material });
			}
		},
		[user],
	);

	const deleteMaterial = useCallback(
		async (materialId: string) => {
			const material = state.materials.find((m) => m.id === materialId);
			if (!material) return;

			// Si habia otro borrado pending, lo ejecutamos inmediatamente para no perderlo
			if (deleteTimeoutRef.current && materialPendingRef.current) {
				clearTimeout(deleteTimeoutRef.current);
				executeRealDelete(materialPendingRef.current);
			}

			// 1. Borrado optimista en la UI
			dispatch({ type: "DELETE_MATERIAL_OPTIMISTIC", payload: materialId });
			dispatch({ type: "PREPARE_UNDO_DELETE", payload: material });

			// 2. Agendar el borrado real
			materialPendingRef.current = material;
			deleteTimeoutRef.current = setTimeout(() => {
				executeRealDelete(material);
				materialPendingRef.current = null;
				deleteTimeoutRef.current = null;
			}, UNDO_TIMEOUT_MS);
		},
		[state.materials, executeRealDelete],
	);

	const undoDelete = useCallback(() => {
		if (deleteTimeoutRef.current) {
			clearTimeout(deleteTimeoutRef.current);
			deleteTimeoutRef.current = null;
			materialPendingRef.current = null;
			dispatch({ type: "UNDO_DELETE" });
		}
	}, []);

	const clearError = useCallback(() => {
		dispatch({ type: "CLEAR_ERROR" });
	}, []);

	const value: MaterialsContextType = {
		state,
		fetchMaterials,
		setSearchQuery,
		setPage,
		addMaterial,
		updateMaterial,
		deleteMaterial,
		undoDelete,
		clearError,
	};

	return (
		<MaterialsContext.Provider value={value}>
			{children}
		</MaterialsContext.Provider>
	);
};

export const useMaterials = (): MaterialsContextType => {
	const context = useContext(MaterialsContext);
	if (!context)
		throw new Error("useMaterials must be used within MaterialsProvider");
	return context;
};
