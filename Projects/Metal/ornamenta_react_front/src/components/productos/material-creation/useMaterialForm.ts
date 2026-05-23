import { useState, useEffect, useMemo, useCallback } from "react";
import * as React from "react";
import { useAuth } from "@hooks/useAuth";
import {
	MaterialType,
	Composition,
	Material,
	CompositionsResponse,
} from "@/types/products";
import { StrategyConfig, MaterialFormState } from "@/types/material-creation";
import { materialToFormState, formStateToPayload } from "./mappers";
import { StorageService } from "@services/storageService";
import { apiClient } from "@services/apiClient";
import { sessionService } from "@services/sessionService";

type UseMaterialFormProps = {
	initialMaterialId?: string; // Si se provee, modo EDICION
	cloneFrom?: Material; // Si se provee, modo CLONACION
	onSuccess?: () => void;
};

export const useMaterialForm = ({
	initialMaterialId,
	cloneFrom,
	onSuccess,
}: UseMaterialFormProps = {}) => {
	const { user, isAuthenticated, sessionReady } = useAuth();

	// Estados de UI/Carga
	const [isLoading, setIsLoading] = useState(false);
	const [isSaving, setIsSaving] = useState(false);
	const [error, setError] = useState("");
	const [isDataReady, setIsDataReady] = useState(false);

	// Datos Maestros
	const [materialTypes, setMaterialTypes] = useState<MaterialType[]>([]);
	const [compositions, setCompositions] = useState<Composition[]>([]);
	const [availableStrategies, setAvailableStrategies] = useState<
		StrategyConfig[]
	>([]);

	// Estado del Formulario
	const [materialTypeId, setMaterialTypeId] = useState("");
	const [compositionId, setCompositionId] = useState("");
	const [measurementStrategy, setMeasurementStrategy] = useState("");
	const [inputMode, setInputMode] = useState("");
	const [purchasePriceAmount, setPurchasePriceAmount] = useState("");
	const [salePriceAmount, setSalePriceAmount] = useState("");
	const [priceCurrency] = useState("COP");
	const [description, setDescription] = useState("");
	const [barcode, setBarcode] = useState("");
	const [sku, setSku] = useState("");
	const [name, setName] = useState("");
	const [dynamicProperties, setDynamicProperties] = useState<
		Record<string, string | number | boolean | null | undefined>
	>({});

	// Estado original (para modo edicion)
	const [fullMaterial, setFullMaterial] = useState<Material | null>(null);

	// ============================================================================
	// SELECTORES / MEMOS
	// ============================================================================

	const selectedMaterialType = useMemo(
		() => materialTypes.find((mt) => mt.id === materialTypeId),
		[materialTypes, materialTypeId],
	);

	const selectedStrategyConfig = useMemo(() => {
		if (!measurementStrategy || availableStrategies.length === 0)
			return undefined;
		return availableStrategies.find(
			(s) => s.name.toLowerCase() === measurementStrategy.toLowerCase(),
		);
	}, [availableStrategies, measurementStrategy]);

	// ============================================================================
	// CARGA DE DATOS
	// ============================================================================

	const fetchData = useCallback(async () => {
		if (!isAuthenticated && !sessionReady) return;
		setIsLoading(true);
		setIsDataReady(false);
		setError("");

		try {
			// 1. Cargar Datos Maestros en paralelo usando apiClient
			const [typesData, compositionsData, strategiesDataRaw] = await Promise.all([
				apiClient.get<any>("/material-types/"),
				apiClient.get<any>("/compositions/"),
				apiClient.get<any>("/measurement-strategies/"),
			]);

			// Procesar Tipos
			const rawTypes = typesData?.material_types || typesData || [];
			const detailedTypes = await Promise.all(
				rawTypes.map(async (type: MaterialType) => {
					try {
						const detail = await apiClient.get<any>(`/material-types/${type.id}`);
						if (detail) return detail;
					} catch (e) {
						console.error(`Error fetching detail for type ${type.id}`, e);
					}
					return type;
				}),
			);
			setMaterialTypes(detailedTypes);

			// Procesar Composiciones
			let arr: Composition[] = [];
			if (Array.isArray(compositionsData)) {
				arr = compositionsData;
			} else if (compositionsData?.compositions) {
				arr = compositionsData.compositions;
			} else if (compositionsData?.materials) {
				arr = compositionsData.materials;
			}
			setCompositions(arr);

			// Procesar Estrategias
			let strategiesData: StrategyConfig[] = Array.isArray(strategiesDataRaw) ? strategiesDataRaw : [];
			strategiesData = strategiesData.filter((s) => s.properties);
			setAvailableStrategies(strategiesData);

			// 2. Si es modo EDICION o CLONACION, cargar el material
			const targetMaterialId = initialMaterialId || cloneFrom?.id;

			if (targetMaterialId) {
				const materialData = await apiClient.get<Material>(`/materials/${targetMaterialId}`);
				if (!materialData) throw new Error("Error al obtener el material");

				if (initialMaterialId) {
					setFullMaterial(materialData);
				}

				// Mapear datos al formulario
				const purchaseAmount =
					materialData.purchase_price_amount || materialData.price_amount;
				setPurchasePriceAmount(purchaseAmount || "");
				setSalePriceAmount(materialData.sale_price_amount || "");
				setDescription(materialData.description || "");
				setBarcode(materialData.barcode || "");
				setSku(initialMaterialId ? materialData.sku || "" : ""); // No clonamos el SKU por seguridad
				setName(materialData.name || "");

				setMaterialTypeId(materialData.material_type_id || "");
				setMeasurementStrategy(materialData.measurement_strategy || "");
				setCompositionId(materialData.composition_id || "");

				// Mapear properties dinamicas
				const strategyConfig = strategiesData.find(
					(s) => s.name === materialData.measurement_strategy,
				);
				if (strategyConfig) {
					const mappedProps = materialToFormState(materialData, strategyConfig);
					// Asegurarnos de que image_url este presente para el ImageUpload component
					mappedProps.image_url =
						materialData.image_url || materialData.properties?.image_url || "";

					// Extraer input mode si el mapper lo provee (o usar dimensiones por defecto para SHEET)
					if (mappedProps._input_mode) {
						setInputMode(mappedProps._input_mode as string);
						delete mappedProps._input_mode;
					} else if (strategyConfig.name.toUpperCase() === "SHEET") {
						setInputMode("dimensions");
					} else if (strategyConfig.input_modes?.length) {
						const defaultMode =
							strategyConfig.input_modes.find((m) => m.recommended) ||
							strategyConfig.input_modes[0];
						setInputMode(defaultMode.mode);
					}

					setDynamicProperties(mappedProps);
				}
			}

			setIsDataReady(true);
		} catch (err) {
			console.error("Error cargando datos:", err);
			setError("Error al cargar datos necesarios.");
		} finally {
			setIsLoading(false);
		}
	}, [user, initialMaterialId, cloneFrom]);

	useEffect(() => {
		if (!isAuthenticated && !sessionReady) return;

		const timeoutId = window.setTimeout(() => {
			void fetchData();
		}, 0);

		return () => window.clearTimeout(timeoutId);
	}, [fetchData, isAuthenticated, sessionReady]);

	// ============================================================================
	// EFECTOS DE LOGICA DE NEGOCIO
	// ============================================================================

	// Cambio automatico de estrategia al seleccionar tipo de material (SOLO CREACION/CLONACION)
	useEffect(() => {
		const timeoutId = window.setTimeout(() => {
			if (initialMaterialId) return; // En edicion no cambiamos estrategia automaticamente

			if (selectedMaterialType) {
				const newStrategy = selectedMaterialType.measurement_strategy;
				if (newStrategy !== measurementStrategy) {
					setMeasurementStrategy(newStrategy);
					setDynamicProperties({});
					setInputMode("");
				}
			}
		}, 0);

		return () => window.clearTimeout(timeoutId);
	}, [selectedMaterialType, initialMaterialId, measurementStrategy]);

	// Configurar input mode por defecto al cambiar estrategia (SOLO CREACION/CLONACION)
	useEffect(() => {
		const timeoutId = window.setTimeout(() => {
			if (initialMaterialId) return;

			if (selectedStrategyConfig?.input_modes?.length) {
				let defaultMode = selectedStrategyConfig.input_modes.find(
					(m) => m.recommended,
				);

				if (selectedStrategyConfig.name.toUpperCase() === "SHEET") {
					defaultMode = selectedStrategyConfig.input_modes.find(
						(m) => m.mode === "dimensions" || m.mode.includes("width"),
					);
				}

				if (!defaultMode) defaultMode = selectedStrategyConfig.input_modes[0];

				setInputMode(defaultMode?.mode || "dimensions");
			} else {
				setInputMode(
					selectedStrategyConfig?.name.toUpperCase() === "SHEET"
						? "dimensions"
						: "",
				);
			}
		}, 0);

		return () => window.clearTimeout(timeoutId);
	}, [selectedStrategyConfig, initialMaterialId]);

	// Detectar cambios (para habilitar boton en CLONACION o EDICION)
	const hasChanges = useMemo(() => {
		// Si no estamos clonando ni editando, no aplicamos esta logica de "bloqueo si no hay cambios"
		// (En creation pura, siempre "hay cambios" respecto a nada)
		if (!initialMaterialId && !cloneFrom) return true;

		// Si estamos editando o clonando, comparamos con cloneFrom (o fullMaterial en edicion)
		const base = fullMaterial || cloneFrom;
		if (!base) return false;

		// Comparacion simple de campos principales
		const purchaseAmount = base.purchase_price_amount || base.price_amount;
		if (purchasePriceAmount !== purchaseAmount) return true;
		if (salePriceAmount !== base.sale_price_amount) return true;
		if (name !== base.name) return true;
		if (description !== base.description) return true;
		if (barcode !== base.barcode) return true;
		if (materialTypeId !== base.material_type_id) return true;
		if (compositionId !== base.composition_id) return true;

		// Comparacion de properties dinamicas (superficial)
		const baseProps = materialToFormState(
			base,
			availableStrategies.find((s) => s.name === base.measurement_strategy) ||
				(null as unknown as StrategyConfig),
		);

		// Ignorar image_url para la comparacion de "cambios" si se desea,
		// o incluirla si es vital para un nuevo material
		const keys = Object.keys(dynamicProperties);
		for (const key of keys) {
			if (dynamicProperties[key] !== baseProps[key]) return true;
		}

		return false;
	}, [
		fullMaterial,
		cloneFrom,
		initialMaterialId,
		purchasePriceAmount,
		salePriceAmount,
		description,
		barcode,
		materialTypeId,
		compositionId,
		dynamicProperties,
		availableStrategies,
	]);

	// ============================================================================
	// HANDLERS
	// ============================================================================

	const handlePropertyChange = (
		key: string,
		value: string | number | boolean | null | undefined,
	) => {
		setDynamicProperties((prev) => ({ ...prev, [key]: value }));
	};

	const handleInputModeChange = (mode: string) => {
		setInputMode(mode);
		// En creation reseteamos para evitar conflictos, en edicion conservamos valores
		if (!initialMaterialId) {
			setDynamicProperties({});
		}
	};

	const handleSubmit = async (e?: React.FormEvent) => {
		if (e) e.preventDefault();
		if (!user || !selectedStrategyConfig) return;

		setIsSaving(true);
		setError("");

		try {
			const formState: MaterialFormState = {
				materialTypeId,
				compositionId,
				measurementStrategy,
				purchasePriceAmount,
				salePriceAmount,
				priceCurrency,
				description,
				barcode,
				sku,
				name,
				dynamicProperties,
				inputMode,
			};

			// Payload del Formulario
			const payload = formStateToPayload(formState, selectedStrategyConfig);

			if (initialMaterialId && fullMaterial) {
				// --- MODO EDICION (PATCH) ---
				const updateData: Partial<Material> & { image_url?: string | null } =
					{};

				if (materialTypeId !== fullMaterial.material_type_id) {
					updateData.material_type_id = materialTypeId;
				}

				if (name !== fullMaterial.name) updateData.name = name;
				if (description !== fullMaterial.description)
					updateData.description = description;
				if (barcode !== fullMaterial.barcode) updateData.barcode = barcode;
				if (sku !== fullMaterial.sku) updateData.sku = sku;

				const oldImageUrl =
					fullMaterial.image_url || fullMaterial.properties?.image_url;
				const newImageUrl = dynamicProperties["image_url"] as
					| string
					| undefined;

				if (newImageUrl !== oldImageUrl) {
					updateData.image_url = newImageUrl || null;
					if (oldImageUrl && typeof oldImageUrl === "string") {
						StorageService.deleteFileByUrl(oldImageUrl).catch(console.error);
					}
				}

				const currentPurchasePrice = parseFloat(
					fullMaterial.purchase_price_amount ||
						fullMaterial.price_amount ||
						"0",
				);
				const newPurchasePrice = parseFloat(purchasePriceAmount || "0");
				if (Math.abs(newPurchasePrice - currentPurchasePrice) > 0.01) {
					updateData.purchase_price_amount = String(newPurchasePrice);
				}

				const currentSalePrice = parseFloat(
					fullMaterial.sale_price_amount || "0",
				);
				const newSalePrice = parseFloat(salePriceAmount || "0");
				if (Math.abs(newSalePrice - currentSalePrice) > 0.01) {
					updateData.sale_price_amount = String(newSalePrice);
				}

				if (payload.properties) {
					const { image_url: _unused_img, ...otherProps } =
						payload.properties as Record<string, unknown>;
					if (Object.keys(otherProps).length > 0) {
						updateData.properties = otherProps;
					}
				}

				if (Object.keys(updateData).length > 0) {
					await apiClient.patch(`/materials/${initialMaterialId}`, updateData, {
						offlineOperation: {
							entity: "material",
							operation: "update",
							endpoint: `/materials/${initialMaterialId}`,
							method: "PATCH",
							body: updateData,
						},
					});
				}
			} else {
				// --- MODO CREACION (POST) ---
				await apiClient.post("/materials/", payload, {
					offlineOperation: {
						entity: "material",
						operation: "create",
						endpoint: "/materials/",
						method: "POST",
						body: payload,
					},
				});
			}

			if (onSuccess) onSuccess();
		} catch (err) {
			const msg = err instanceof Error ? err.message : String(err);
			console.error("Error submitting form:", msg);
			setError(msg);
		} finally {
			setIsSaving(false);
		}
	};

	// ============================================================================
	// EXPOSE
	// ============================================================================

	return {
		// Estado UI
		isLoading,
		isSaving,
		isDataReady,
		error,
		hasChanges,

		// Datos
		materialTypes,
		compositions,
		availableStrategies,
		fullMaterial, // Para referencia en UI si se necesita (nombre original, etc)

		// Form State Values
		materialTypeId,
		compositionId,
		measurementStrategy,
		purchasePriceAmount,
		salePriceAmount,
		priceCurrency,
		description,
		barcode,
		sku,
		name,
		dynamicProperties,
		inputMode,

		// Computed / Helpers
		selectedStrategyConfig,
		selectedMaterialType,

		// Setters (para inputs manuales si hacen falta)
		setMaterialTypeId,
		setCompositionId,
		setMeasurementStrategy,
		setPurchasePriceAmount,
		setSalePriceAmount,
		setDescription,
		setBarcode,
		setSku,
		setName,

		// Handlers Logicos
		handlePropertyChange,
		handleInputModeChange,
		handleSubmit,
		getPayload: () => {
			if (!selectedStrategyConfig) return null;
			return formStateToPayload(
				{
					materialTypeId,
					compositionId,
					measurementStrategy,
					purchasePriceAmount,
					salePriceAmount,
					priceCurrency,
					description,
					barcode,
					sku,
					name,
					dynamicProperties,
					inputMode,
				},
				selectedStrategyConfig,
			);
		},

		// Reload helpers
		refreshTypes: async () => {
			if (!isAuthenticated && !sessionReady) return;
			try {
				const data = await apiClient.get<any>("/material-types/");
				const rawTypes = data?.material_types || data || [];
				const detailedTypes = await Promise.all(
					rawTypes.map(async (type: MaterialType) => {
						try {
							const detail = await apiClient.get<any>(`/material-types/${type.id}`);
							if (detail) return detail;
						} catch (e) {
							console.error(`Error fetching detail for type ${type.id}`, e);
						}
						return type;
					}),
				);
				setMaterialTypes(detailedTypes);
			} catch (err) {
				console.error("Error refreshing types:", err);
			}
		},
		refreshCompositions: async () => {
			if (!isAuthenticated && !sessionReady) return;
			try {
				const compositionsData = await apiClient.get<any>("/compositions/");
				let arr: Composition[] = [];
				if (Array.isArray(compositionsData)) {
					arr = compositionsData;
				} else if (compositionsData?.compositions) {
					arr = compositionsData.compositions;
				} else if (compositionsData?.materials) {
					arr = compositionsData.materials;
				}
				setCompositions(arr);
			} catch (err) {
				console.error("Error refreshing compositions:", err);
			}
		},
	};
};
