import React, {
	createContext,
	useContext,
	useReducer,
	useCallback,
	useEffect,
	useRef,
} from "react";
import { Product } from "@/types/products";
import { useAuth } from "@hooks/useAuth";
import { useDebounce } from "@hooks/useDebounce";
import { useConnectivity } from "@/providers/ConnectivityProvider";
import { sessionService } from "@services/sessionService";

type ApiProductPriceLike = number | string | null | undefined;

interface ApiProduct {
	id?: string;
	product_id?: string;
	name?: string;
	description?: string;
	product_type?: string;
	material_id?: string;
	material_name?: string;
	measurement_strategy?: string;
	valid_dimensions?: string[];
	dimensions?: Record<string, unknown> | null;
	components?: ApiProductComponent[];
	image_url?: string | null;
	price?: ApiProductPriceLike;
	purchase_price?: ApiProductPriceLike;
	sale_price?: ApiProductPriceLike;
	purchase_price_amount?: ApiProductPriceLike;
	sale_price_amount?: ApiProductPriceLike;
	price_amount?: ApiProductPriceLike;
	currency?: string;
	purchase_price_currency?: string;
	sale_price_currency?: string;
	price_currency?: string;
	last_calculation_audit?: Record<string, unknown> | null;
}

interface ApiProductComponent {
	product_id?: string;
	product_name?: string;
	product_type?: string;
	quantity?: number;
	order_index?: number;
}

interface ApiProductsResponse {
	products?: ApiProduct[];
	items?: ApiProduct[];
	total?: number;
	count?: number;
}

const parseNumericPrice = (value: ApiProductPriceLike): number | undefined => {
	if (typeof value === "number" && Number.isFinite(value)) return value;
	if (typeof value === "string") {
		const parsed = Number.parseFloat(value);
		if (Number.isFinite(parsed)) return parsed;
	}
	return undefined;
};

const normalizeProduct = (raw: ApiProduct): Product => {
	const salePrice =
		parseNumericPrice(raw.sale_price) ??
		parseNumericPrice(raw.sale_price_amount);
	const purchasePrice =
		parseNumericPrice(raw.purchase_price) ??
		parseNumericPrice(raw.purchase_price_amount);
	const genericPrice =
		parseNumericPrice(raw.price) ?? parseNumericPrice(raw.price_amount);

	const effectivePrice = salePrice ?? genericPrice ?? purchasePrice;
	const currency =
		raw.sale_price_currency ||
		raw.currency ||
		raw.price_currency ||
		raw.purchase_price_currency ||
		"COP";

	return {
		id: raw.id || raw.product_id || "",
		name: raw.name || "Unnamed product",
		description: raw.description || "",
		product_type: raw.product_type || "simple",
		material_id: raw.material_id || "",
		material_name: raw.material_name || "",
		measurement_strategy: raw.measurement_strategy,
		valid_dimensions: raw.valid_dimensions,
		dimensions: raw.dimensions || null,
		components: Array.isArray(raw.components)
			? raw.components.map((component) => ({
					product_id: component.product_id || "",
					product_name: component.product_name || "",
					product_type: component.product_type || "simple",
					quantity:
						typeof component.quantity === "number" &&
						Number.isFinite(component.quantity)
							? component.quantity
							: 0,
					order_index:
						typeof component.order_index === "number" &&
						Number.isFinite(component.order_index)
							? component.order_index
							: 0,
				}))
			: [],
		image_url: raw.image_url || null,
		price: effectivePrice,
		purchase_price: purchasePrice,
		sale_price: salePrice,
		purchase_price_currency: raw.purchase_price_currency || currency,
		sale_price_currency: raw.sale_price_currency || currency,
		currency,
		last_calculation_audit: raw.last_calculation_audit || null,
	};
};

// ============================================================================
// TYPES
// ============================================================================

type PaginationMeta = {
	currentPage: number;
	pageSize: number;
	totalItems: number;
	totalPages: number;
};

type ProductsState = {
	products: Product[];
	isLoading: boolean;
	error: string | null;
	searchQuery: string;
	pagination: PaginationMeta;
	// Undo action state
	deletedProduct: { product: Product; timestamp: number } | null;
};

type ProductsAction =
	| { type: "FETCH_START" }
	| {
			type: "FETCH_SUCCESS";
			payload: { products: Product[]; total: number };
	  }
	| { type: "FETCH_ERROR"; payload: string }
	| { type: "SET_SEARCH_QUERY"; payload: string }
	| { type: "SET_PAGE"; payload: number }
	| { type: "ADD_PRODUCT"; payload: Product }
	| { type: "UPDATE_PRODUCT"; payload: Product }
	| { type: "DELETE_PRODUCT_OPTIMISTIC"; payload: string }
	| { type: "PREPARE_UNDO_DELETE"; payload: Product }
	| { type: "CONFIRM_DELETE_UI" }
	| { type: "UNDO_DELETE" }
	| { type: "CLEAR_ERROR" };

type ProductsContextType = {
	state: ProductsState;
	fetchProducts: () => Promise<void>;
	setSearchQuery: (query: string) => void;
	setPage: (page: number) => void;
	addProduct: (product: Product) => void;
	updateProduct: (product: Product) => void;
	deleteProduct: (productId: string) => Promise<void>;
	undoDelete: () => void;
	clearError: () => void;
};

// ============================================================================
// CONSTANTS
// ============================================================================

const PAGE_SIZE = 10;
const UNDO_TIMEOUT_MS = 5000;

// ============================================================================
// REDUCER
// ============================================================================

const initialState: ProductsState = {
	products: [],
	isLoading: false,
	error: null,
	searchQuery: "",
	pagination: {
		currentPage: 1,
		pageSize: PAGE_SIZE,
		totalItems: 0,
		totalPages: 0,
	},
	deletedProduct: null,
};

function productsReducer(
	state: ProductsState,
	action: ProductsAction,
): ProductsState {
	switch (action.type) {
		case "FETCH_START":
			return {
				...state,
				isLoading: true,
				error: null,
			};

		case "FETCH_SUCCESS": {
			const { products, total } = action.payload;
			return {
				...state,
				products,
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

		case "ADD_PRODUCT":
			return {
				...state,
				products: [action.payload, ...state.products].slice(0, PAGE_SIZE),
				pagination: {
					...state.pagination,
					totalItems: state.pagination.totalItems + 1,
					totalPages: Math.max(
						1,
						Math.ceil((state.pagination.totalItems + 1) / PAGE_SIZE),
					),
				},
			};

		case "UPDATE_PRODUCT":
			return {
				...state,
				products: state.products.map((p) =>
					p.id === action.payload.id ? action.payload : p,
				),
			};

		case "DELETE_PRODUCT_OPTIMISTIC":
			return {
				...state,
				products: state.products.filter((p) => p.id !== action.payload),
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
				deletedProduct: {
					product: action.payload,
					timestamp: Date.now(),
				},
			};

		case "CONFIRM_DELETE_UI":
			return {
				...state,
				deletedProduct: null,
			};

		case "UNDO_DELETE":
			if (!state.deletedProduct) return state;
			return {
				...state,
				products: [state.deletedProduct.product, ...state.products].slice(
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
				deletedProduct: null,
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

const ProductsContext = createContext<ProductsContextType | undefined>(
	undefined,
);

// ============================================================================
// PROVIDER
// ============================================================================

export const ProductsProvider: React.FC<{ children: React.ReactNode }> = ({
	children,
}) => {
	const [state, dispatch] = useReducer(productsReducer, initialState);
	const { user, isAuthenticated, sessionReady } = useAuth();
	const { isOnline } = useConnectivity();
	const debouncedSearchQuery = useDebounce(state.searchQuery, 500);

	const deleteTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
	const productIdToDeleteRef = useRef<string | null>(null);

	// Limpieza al desmontar
	useEffect(() => {
		return () => {
			if (deleteTimeoutRef.current) {
				clearTimeout(deleteTimeoutRef.current);
			}
		};
	}, []);

	const fetchProducts = useCallback(async () => {
		if (!isAuthenticated && !sessionReady) return;
		dispatch({ type: "FETCH_START" });
		try {
			const token = sessionService.getAccessToken();
			const effectiveToken = token || (await user?.getIdToken());

			if (!effectiveToken) throw new Error("User not authenticated");

			const url = new URL(`${import.meta.env.VITE_API_URL}/products/`);
			url.searchParams.set("limit", String(PAGE_SIZE));
			url.searchParams.set(
				"offset",
				String((state.pagination.currentPage - 1) * PAGE_SIZE),
			);
			if (debouncedSearchQuery.trim()) {
				url.searchParams.set("search", debouncedSearchQuery.trim());
			}
			const res = await fetch(url.toString(), {
				headers: { Authorization: `Bearer ${token}` },
			});
			if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`);
			const data: ApiProductsResponse = await res.json();
			const sourceProducts = data.products || data.items || [];
			const normalizedProducts = sourceProducts.map(normalizeProduct);
			const total = data.total ?? data.count ?? normalizedProducts.length;
			dispatch({
				type: "FETCH_SUCCESS",
				payload: { products: normalizedProducts, total },
			});
		} catch (err) {
			dispatch({
				type: "FETCH_ERROR",
				payload:
					err instanceof Error ? err.message : "Error al cargar products",
			});
		}
	}, [user, state.pagination.currentPage, debouncedSearchQuery]);

	useEffect(() => {
		if (!isOnline || (!user && !sessionReady)) return;
		void fetchProducts();
	}, [fetchProducts, isOnline, user, sessionReady]);

	const setSearchQuery = useCallback((query: string) => {
		dispatch({ type: "SET_SEARCH_QUERY", payload: query });
	}, []);

	const setPage = useCallback((page: number) => {
		dispatch({ type: "SET_PAGE", payload: page });
	}, []);

	const addProduct = useCallback((product: Product) => {
		dispatch({ type: "ADD_PRODUCT", payload: product });
	}, []);

	const updateProduct = useCallback((product: Product) => {
		dispatch({ type: "UPDATE_PRODUCT", payload: product });
	}, []);

	const executeRealDelete = useCallback(
		async (productId: string) => {
			if (!user) return;
			try {
				const token = await user.getIdToken();
				const res = await fetch(
					`${import.meta.env.VITE_API_URL}/products/${productId}`,
					{
						method: "DELETE",
						headers: { Authorization: `Bearer ${token}` },
					},
				);
				if (!res.ok) throw new Error("Error al delete product en servidor");
				dispatch({ type: "CONFIRM_DELETE_UI" });
			} catch (err) {
				console.error("ERROR Error real delete product:", err);
			}
		},
		[user],
	);

	const deleteProduct = useCallback(
		async (productId: string) => {
			const product = state.products.find((p) => p.id === productId);
			if (!product) return;

			if (deleteTimeoutRef.current && productIdToDeleteRef.current) {
				clearTimeout(deleteTimeoutRef.current);
				executeRealDelete(productIdToDeleteRef.current);
			}

			dispatch({ type: "DELETE_PRODUCT_OPTIMISTIC", payload: productId });
			dispatch({ type: "PREPARE_UNDO_DELETE", payload: product });

			productIdToDeleteRef.current = productId;
			deleteTimeoutRef.current = setTimeout(() => {
				executeRealDelete(productId);
				productIdToDeleteRef.current = null;
				deleteTimeoutRef.current = null;
			}, UNDO_TIMEOUT_MS);
		},
		[state.products, executeRealDelete],
	);

	const undoDelete = useCallback(() => {
		if (deleteTimeoutRef.current) {
			clearTimeout(deleteTimeoutRef.current);
			deleteTimeoutRef.current = null;
			productIdToDeleteRef.current = null;
			dispatch({ type: "UNDO_DELETE" });
		}
	}, []);

	const clearError = useCallback(() => {
		dispatch({ type: "CLEAR_ERROR" });
	}, []);

	const value: ProductsContextType = {
		state,
		fetchProducts,
		setSearchQuery,
		setPage,
		addProduct,
		updateProduct,
		deleteProduct,
		undoDelete,
		clearError,
	};

	return (
		<ProductsContext.Provider value={value}>
			{children}
		</ProductsContext.Provider>
	);
};

export const useProducts = (): ProductsContextType => {
	const context = useContext(ProductsContext);
	if (!context)
		throw new Error("useProducts must be used within ProductsProvider");
	return context;
};
