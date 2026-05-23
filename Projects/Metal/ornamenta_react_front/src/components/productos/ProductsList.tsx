import React, { useMemo, useState, useEffect } from "react";
import { useAuth } from "@hooks/useAuth";
import { formatPrice } from "@/utils";
import { apiClient } from "@/services/apiClient";
import { Pencil, Trash, AlertCircle } from "lucide-react";
import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Pagination,
  Spinner,
  Chip,
  Button,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Tooltip,
  Divider,
  Input,
  Textarea,
  Select,
  SelectItem,
  Alert,
} from "@heroui/react";
import { Product, ProductComponent } from "@/types/products";
import { TableSearchBar } from "@components/common/TableSearchBar";
import { CenteredModal } from "@components/common/CenteredModal";
import { useProducts } from "@context/ProductsContext";
import { UndoToast } from "@components/common/UndoToast";
import { useConnectivity } from "@/providers/ConnectivityProvider";

type ProductsListProps = Record<string, never>;

type SortableProductColumn =
  | "name"
  | "description"
  | "product_type"
  | "price"
  | "components_count";

interface ProductsSortDescriptor {
  column: SortableProductColumn;
  direction: "ascending" | "descending";
}

type ProductDimensionsState = Record<string, string | number | undefined>;
type SelectionKeys = Set<React.Key> | "all";

const SORTABLE_COLUMNS: SortableProductColumn[] = [
  "name",
  "description",
  "product_type",
  "price",
  "components_count",
];

const isSortableColumn = (column: string): column is SortableProductColumn =>
  SORTABLE_COLUMNS.includes(column as SortableProductColumn);

const getProductTypeLabel = (productType: string): string =>
  productType === "simple" ? "Simple" : "Compuesto";

const getNumericPrice = (price: Product["price"]): number | undefined => {
  const parsed =
    typeof price === "number" ? price : Number.parseFloat(price ?? "");
  return Number.isFinite(parsed) ? parsed : undefined;
};

const getProductPriceDisplay = (product: Product): string =>
  getNumericPrice(product.price) && getNumericPrice(product.price)! > 0
    ? `$${formatPrice(getNumericPrice(product.price)!)} ${product.currency || "COP"}`
    : "Price no disponible";

const normalizeDimensions = (
  dimensions: Product["dimensions"],
): ProductDimensionsState => {
  if (!dimensions) return {};

  return Object.entries(dimensions).reduce<ProductDimensionsState>(
    (acc, [key, value]) => {
      if (typeof value === "string" || typeof value === "number") {
        acc[key] = value;
      }
      return acc;
    },
    {},
  );
};

const getSortableValue = (
  product: Product,
  column: SortableProductColumn,
): string | number => {
  switch (column) {
    case "name":
      return product.name ?? "";
    case "description":
      return product.description ?? "";
    case "product_type":
      return product.product_type ?? "";
    case "price":
      return getNumericPrice(product.price) ?? 0;
    case "components_count":
      return Array.isArray(product.components) ? product.components.length : 0;
    default:
      return "";
  }
};

interface ProductDetailApiComponent {
  product_id?: string;
  product_name?: string;
  product_type?: string;
  quantity?: number;
  order_index?: number;
}

interface ProductDetailApiResponse {
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
  recipe?: Array<{
    dimensions?: Record<string, unknown> | null;
  }>;
  components?: ProductDetailApiComponent[];
  image_url?: string | null;
  price?: number | string;
  price_amount?: number | string;
  purchase_price?: number | string;
  purchase_price_amount?: number | string;
  sale_price?: number | string;
  sale_price_amount?: number | string;
  currency?: string;
  price_currency?: string;
  purchase_price_currency?: string;
  sale_price_currency?: string;
  last_calculation_audit?: Record<string, unknown> | null;
}

export const ProductsList: React.FC<ProductsListProps> = () => {
  const { user } = useAuth();
  const { isOnline } = useConnectivity();
  const {
    state: {
      products,
      isLoading,
      error,
      searchQuery,
      pagination,
      deletedProduct,
    },
    setSearchQuery,
    setPage,
    deleteProduct,
    undoDelete,
    clearError,
  } = useProducts();

  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [deletingProduct, setDeletingProduct] = useState<Product | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isLoadingProductDetail, setIsLoadingProductDetail] = useState(false);
  const [productDetailError, setProductDetailError] = useState<string | null>(
    null,
  );

  const parsePrice = (value: number | string | null | undefined) => {
    if (typeof value === "number" && Number.isFinite(value)) return value;
    if (typeof value === "string") {
      const parsed = Number.parseFloat(value);
      if (Number.isFinite(parsed)) return parsed;
    }
    return undefined;
  };

  const getDisplayPrices = (product: Product) => {
    const salePrice = parsePrice(product.sale_price);
    const purchasePrice = parsePrice(product.purchase_price);
    const genericPrice = parsePrice(product.price);

    return {
      salePrice: salePrice ?? genericPrice,
      purchasePrice,
      saleCurrency: product.sale_price_currency || product.currency || "COP",
      purchaseCurrency:
        product.purchase_price_currency || product.currency || "COP",
    };
  };

  const formatDimensionValue = (value: unknown) => {
    if (value === null || value === undefined) return "-";
    if (typeof value === "object") {
      const dimensionObj = value as { value?: unknown; unit?: unknown };
      if (
        typeof dimensionObj.value === "number" ||
        typeof dimensionObj.value === "string"
      ) {
        return `${dimensionObj.value}${dimensionObj.unit ? ` ${String(dimensionObj.unit)}` : ""}`;
      }
      return JSON.stringify(value);
    }
    return String(value);
  };

  const isNullDimensionValue = (value: unknown) => {
    if (value === null || value === undefined) return true;
    if (typeof value !== "object") return false;

    const dimensionObj = value as { value?: unknown; unit?: unknown };
    const hasValue =
      dimensionObj.value !== null && dimensionObj.value !== undefined;
    const hasUnit =
      dimensionObj.unit !== null && dimensionObj.unit !== undefined;

    return !hasValue && !hasUnit;
  };

  const normalizeDimensionObject = (value: unknown) => {
    if (!value || typeof value !== "object") return null;
    const dimensionObj = value as { value?: unknown; unit?: unknown };
    const normalizedValue =
      typeof dimensionObj.value === "number" ||
      typeof dimensionObj.value === "string"
        ? dimensionObj.value
        : null;
    const normalizedUnit =
      typeof dimensionObj.unit === "string" ? dimensionObj.unit : null;

    if (normalizedValue === null && !normalizedUnit) return null;

    return {
      value: normalizedValue,
      unit: normalizedUnit,
    };
  };

  const mergeDimensionsWithRecipeFallback = (
    apiDimensions: Record<string, unknown> | null | undefined,
    recipeDimensions: Record<string, unknown> | null | undefined,
  ): Record<string, unknown> | null => {
    if (!apiDimensions && !recipeDimensions) return null;

    const keys = new Set<string>([
      ...Object.keys(apiDimensions || {}),
      ...Object.keys(recipeDimensions || {}),
    ]);

    const merged: Record<string, unknown> = {};

    keys.forEach((key) => {
      const apiValue = apiDimensions?.[key];
      const recipeValue = recipeDimensions?.[key];

      const apiDim = normalizeDimensionObject(apiValue);
      const recipeDim = normalizeDimensionObject(recipeValue);

      if (apiDim) {
        const apiNumeric =
          typeof apiDim.value === "number" ? apiDim.value : undefined;
        const shouldFallbackToRecipe =
          apiNumeric === 0 &&
          typeof recipeDim?.value === "number" &&
          recipeDim.value > 0;

        merged[key] = shouldFallbackToRecipe ? recipeDim : apiDim;
        return;
      }

      merged[key] = recipeDim || apiValue || recipeValue || null;
    });

    return merged;
  };

  const handleSearchChange = (value: string) => {
    setSearchQuery(value);
  };

  const normalizeProductDetail = (
    raw: ProductDetailApiResponse,
    fallback: Product,
  ): Product => {
    const salePrice =
      parsePrice(raw.sale_price) ?? parsePrice(raw.sale_price_amount);
    const purchasePrice =
      parsePrice(raw.purchase_price) ?? parsePrice(raw.purchase_price_amount);
    const genericPrice = parsePrice(raw.price) ?? parsePrice(raw.price_amount);
    const firstRecipeDimensions =
      Array.isArray(raw.recipe) && raw.recipe.length > 0
        ? raw.recipe[0]?.dimensions
        : undefined;
    const mergedDimensions = mergeDimensionsWithRecipeFallback(
      raw.dimensions,
      firstRecipeDimensions,
    );
    const currency =
      raw.sale_price_currency ||
      raw.currency ||
      raw.price_currency ||
      raw.purchase_price_currency ||
      fallback.currency ||
      "COP";

    return {
      ...fallback,
      id: raw.id || raw.product_id || fallback.id,
      name: raw.name || fallback.name,
      description: raw.description ?? fallback.description,
      product_type: raw.product_type || fallback.product_type,
      material_id: raw.material_id || fallback.material_id,
      material_name: raw.material_name || fallback.material_name,
      measurement_strategy:
        raw.measurement_strategy || fallback.measurement_strategy,
      valid_dimensions: raw.valid_dimensions || fallback.valid_dimensions,
      dimensions: mergedDimensions || fallback.dimensions,
      image_url: raw.image_url ?? fallback.image_url ?? null,
      price: salePrice ?? genericPrice ?? fallback.price,
      purchase_price: purchasePrice ?? fallback.purchase_price,
      sale_price: salePrice ?? fallback.sale_price,
      purchase_price_currency:
        raw.purchase_price_currency ||
        fallback.purchase_price_currency ||
        currency,
      sale_price_currency:
        raw.sale_price_currency || fallback.sale_price_currency || currency,
      currency,
      last_calculation_audit:
        raw.last_calculation_audit ?? fallback.last_calculation_audit ?? null,
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
        : fallback.components,
    };
  };

  const handleRowClick = async (product: Product) => {
    setSelectedProduct(product);
    setShowDetailModal(true);
    setIsLoadingProductDetail(true);
    setProductDetailError(null);

    try {
      const detail = await apiClient.get<ProductDetailApiResponse>(
        `/products/${product.id}`,
      );
      setSelectedProduct(normalizeProductDetail(detail, product));
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "No se pudo cargar el detalle del product";
      setProductDetailError(message);
    } finally {
      setIsLoadingProductDetail(false);
    }
  };

  const handleEditClick = (product: Product) => {
    setEditingProduct(product);
    setShowEditModal(true);
  };

  const handleEditSuccess = () => {
    setShowEditModal(false);
    setEditingProduct(null);
    setSuccessMessage("Product actualizado exitosamente");
    setTimeout(() => setSuccessMessage(null), 3000);
  };

  const handleEditCancel = () => {
    setShowEditModal(false);
    setEditingProduct(null);
  };

  const handleDeleteClick = (product: Product) => {
    setDeletingProduct(product);
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deletingProduct || !user) return;
    await deleteProduct(deletingProduct.id);
    setShowDeleteConfirm(false);
    setDeletingProduct(null);
  };

  const handleDeleteCancel = () => {
    setShowDeleteConfirm(false);
    setDeletingProduct(null);
  };

  const handleSortChange = (descriptor: {
    column: React.Key;
    direction: "ascending" | "descending";
  }) => {
    const column = String(descriptor.column);
    if (!isSortableColumn(column)) return;

    setSortDescriptor({
      column,
      direction: descriptor.direction,
    });
  };

  const renderActionButtons = (product: Product) => (
    <div className="flex flex-wrap gap-2">
      <Button
        size="sm"
        color="default"
        variant="flat"
        onPress={() => handleEditClick(product)}
        isDisabled={editingProduct?.id === product.id || !isOnline}
        className="text-primary hover:bg-primary/10"
        startContent={
          editingProduct?.id !== product.id ? (
            <Pencil className="w-3 h-3" />
          ) : undefined
        }
      >
        {editingProduct?.id === product.id ? <Spinner size="sm" /> : "Edit"}
      </Button>
      <Button
        size="sm"
        color="danger"
        variant="flat"
        onPress={() => handleDeleteClick(product)}
        isDisabled={deletingProduct?.id === product.id || !isOnline}
        startContent={
          deletingProduct?.id !== product.id ? (
            <Trash className="w-3 h-3" />
          ) : undefined
        }
      >
        {deletingProduct?.id === product.id ? (
          <Spinner size="sm" />
        ) : (
          "Delete"
        )}
      </Button>
    </div>
  );

  const [sortDescriptor, setSortDescriptor] = useState<ProductsSortDescriptor>({
    column: "name",
    direction: "ascending",
  });

  const sortedItems = useMemo(() => {
    const items = [...products];
    const { column, direction } = sortDescriptor;
    const dir = direction === "descending" ? -1 : 1;

    items.sort((a, b) => {
      const av = getSortableValue(a, column);
      const bv = getSortableValue(b, column);

      if (typeof av === "string" && typeof bv === "string") {
        return av.localeCompare(bv) * dir;
      }

      if (typeof av === "number" && typeof bv === "number") {
        return av === bv ? 0 : av > bv ? dir : -dir;
      }

      return 0;
    });

    return items;
  }, [products, sortDescriptor]);

  return (
    <div className="mx-auto max-w-6xl p-4">
      {successMessage && (
        <Alert
          color="success"
          variant="flat"
          className="mb-4"
          onClose={() => setSuccessMessage(null)}
        >
          {successMessage}
        </Alert>
      )}

      {error && (
        <Alert
          color="danger"
          variant="flat"
          className="mb-4"
          startContent={<AlertCircle className="w-5 h-5" />}
          onClose={clearError}
        >
          {error}
        </Alert>
      )}

      {deletedProduct && (
        <UndoToast
          message={`Product "${deletedProduct.product.name}" eliminado`}
          onUndo={undoDelete}
          onDismiss={() => {}}
        />
      )}

      <div className="mb-4">
        <h2 className="text-2xl font-semibold text-foreground">
          Lista de Products
        </h2>
      </div>

      <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <TableSearchBar
          value={searchQuery}
          onValueChange={handleSearchChange}
          placeholder="Search por nombre, description, material o tipo..."
          label="Search products"
          description={`Mostrando ${products.length} de ${pagination.totalItems} product(s)`}
          className="w-full md:flex-1"
        />
        <Chip color="primary" variant="flat" className="w-fit">
          Mostrando: {products.length} / {pagination.totalItems}
        </Chip>
      </div>

      <div className="space-y-3 md:hidden">
        {isLoading ? (
          <div className="flex items-center justify-center rounded-2xl border border-divider bg-content1 p-8">
            <Spinner />
          </div>
        ) : sortedItems.length === 0 ? (
          <div className="rounded-2xl border border-divider bg-content1 p-6 text-center text-sm text-default-500">
            {error ? `Error: ${error}` : "Sin products para mostrar"}
          </div>
        ) : (
          sortedItems.map((item) => (
            <article
              key={item.id}
              className="rounded-2xl border border-divider bg-content1 p-4 shadow-sm"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <button
                    type="button"
                    className="min-w-0 text-left text-base font-semibold text-foreground transition-colors hover:text-primary"
                    onClick={() => handleRowClick(item)}
                  >
                    <span className="block truncate">{item.name}</span>
                  </button>
                  <Chip
                    size="sm"
                    variant="flat"
                    color={
                      item.product_type === "simple" ? "primary" : "secondary"
                    }
                  >
                    {getProductTypeLabel(item.product_type)}
                  </Chip>
                </div>

                <p className="line-clamp-2 text-sm text-default-500">
                  {item.description || "Sin description"}
                </p>

                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  <div className="rounded-xl bg-default-50 p-3">
                    <p className="text-xs font-semibold uppercase tracking-wide text-default-400">
                      Price
                    </p>
                    <p className="mt-1 text-sm font-semibold text-success-600">
                      {getProductPriceDisplay(item)}
                    </p>
                  </div>
                  <div className="rounded-xl bg-default-50 p-3">
                    <p className="text-xs font-semibold uppercase tracking-wide text-default-400">
                      Material
                    </p>
                    <p className="mt-1 text-sm font-medium text-foreground">
                      {item.material_name || "No especificado"}
                    </p>
                  </div>
                </div>

                <div className="flex flex-col gap-2 sm:flex-row">
                  <Button
                    color="default"
                    variant="bordered"
                    onPress={() => handleRowClick(item)}
                    className="w-full sm:w-auto"
                  >
                    Ver detalle
                  </Button>
                  {renderActionButtons(item)}
                </div>
              </div>
            </article>
          ))
        )}

        {pagination.totalPages > 1 && (
          <div className="flex justify-center p-2">
            <Pagination
              page={pagination.currentPage}
              total={pagination.totalPages}
              onChange={(p: number) => setPage(p)}
              showControls
            />
          </div>
        )}
      </div>

      <div className="hidden md:block">
        <div className="overflow-x-auto rounded-2xl border border-divider bg-content1 shadow-sm">
          <Table
            aria-label="Tabla de products"
            isStriped
            removeWrapper
            selectionMode="single"
            onRowAction={(key: React.Key) => {
              const product = products.find((p) => p.id === key);
              if (product) handleRowClick(product);
            }}
            classNames={{
              row: "cursor-pointer hover:bg-table-row-hover transition-colors",
            }}
            sortDescriptor={sortDescriptor}
            onSortChange={handleSortChange}
            bottomContent={
              pagination.totalPages > 1 ? (
                <div className="flex justify-center p-2">
                  <Pagination
                    page={pagination.currentPage}
                    total={pagination.totalPages}
                    onChange={(p: number) => setPage(p)}
                    showControls
                  />
                </div>
              ) : null
            }
          >
            <TableHeader>
              <TableColumn key="name" allowsSorting>
                Nombre
              </TableColumn>
              <TableColumn key="description" allowsSorting>
                Description
              </TableColumn>
              <TableColumn key="product_type" allowsSorting>
                Tipo
              </TableColumn>
              <TableColumn key="price" allowsSorting>
                Price
              </TableColumn>
              <TableColumn key="actions" width={200}>
                Acciones
              </TableColumn>
            </TableHeader>
            <TableBody
              isLoading={isLoading}
              loadingContent={<Spinner className="my-4" />}
              emptyContent={
                error ? `Error: ${error}` : "Sin products para mostrar"
              }
              items={sortedItems}
            >
              {(item: Product) => (
                <TableRow key={item.id}>
                  <TableCell>
                    <button
                      type="button"
                      className="text-left hover:text-primary transition-colors underline decoration-transparent hover:decoration-current"
                      onClick={() => handleRowClick(item)}
                    >
                      {item.name}
                    </button>
                  </TableCell>
                  <TableCell>
                    <Tooltip content={item.description}>
                      <span className="block max-w-[240px] truncate">
                        {item.description}
                      </span>
                    </Tooltip>
                  </TableCell>
                  <TableCell>
                    <Chip
                      size="sm"
                      variant="flat"
                      color={
                        item.product_type === "simple" ? "primary" : "secondary"
                      }
                    >
                      {item.product_type === "simple"
                        ? " Simple"
                        : " Compuesto"}
                    </Chip>
                  </TableCell>
                  <TableCell className="font-semibold">
                    {(() => {
                      const { salePrice, saleCurrency } =
                        getDisplayPrices(item);
                      return salePrice && salePrice > 0 ? (
                        <Chip color="success" variant="flat" size="sm">
                          ${formatPrice(salePrice)} {saleCurrency}
                        </Chip>
                      ) : (
                        <span className="text-xs text-default-400">
                          Price no disponible
                        </span>
                      );
                    })()}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        color="default"
                        variant="flat"
                        onPress={() => handleEditClick(item)}
                        isDisabled={editingProduct?.id === item.id}
                        className="text-primary hover:bg-primary/10"
                        startContent={
                          editingProduct?.id !== item.id ? (
                            <Pencil className="w-3 h-3" />
                          ) : undefined
                        }
                      >
                        {editingProduct?.id === item.id ? (
                          <Spinner size="sm" />
                        ) : (
                          "Edit"
                        )}
                      </Button>
                      <Button
                        size="sm"
                        color="danger"
                        variant="flat"
                        onPress={() => handleDeleteClick(item)}
                        isDisabled={deletingProduct?.id === item.id}
                        startContent={
                          deletingProduct?.id !== item.id ? (
                            <Trash className="w-3 h-3" />
                          ) : undefined
                        }
                      >
                        {deletingProduct?.id === item.id ? (
                          <Spinner size="sm" />
                        ) : (
                          "Delete"
                        )}
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </div>

      <CenteredModal
        isOpen={showDetailModal}
        onOpenChange={(isOpen: boolean) => {
          setShowDetailModal(isOpen);
        }}
        onClose={() => {
          setShowDetailModal(false);
          setSelectedProduct(null);
          setProductDetailError(null);
        }}
        size="lg"
        scrollBehavior="inside"
        backdrop="blur"
      >
        {(onClose: () => void) => (
          <>
            <ModalHeader className="border-b border-divider">
              Detalles del Product
            </ModalHeader>
            <ModalBody className="py-5 sm:py-6">
              {isLoadingProductDetail && (
                <div className="py-8 flex justify-center">
                  <Spinner />
                </div>
              )}
              {productDetailError && !isLoadingProductDetail && (
                <Alert color="warning" variant="flat" className="mb-4">
                  {productDetailError}
                </Alert>
              )}
              {selectedProduct && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">
                      Informacion General
                    </h3>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      <div className="flex flex-col gap-1 sm:col-span-2">
                        <span className="text-sm font-medium text-default-500">
                          Nombre
                        </span>
                        <p className="text-base font-medium">
                          {selectedProduct.name}
                        </p>
                      </div>
                      <div className="flex flex-col gap-1">
                        <span className="text-sm font-medium text-default-500">
                          Description
                        </span>
                        <p className="text-base">
                          {selectedProduct.description || "Sin description"}
                        </p>
                      </div>
                      <div className="flex flex-col gap-1">
                        <span className="text-sm font-medium text-default-500">
                          Tipo
                        </span>
                        <p className="text-base">
                          {selectedProduct.product_type === "simple"
                            ? " Simple"
                            : " Compuesto"}
                        </p>
                      </div>
                      <div className="flex flex-col gap-1">
                        <span className="text-sm font-medium text-default-500">
                          Material
                        </span>
                        <p className="text-base">
                          {selectedProduct.material_name || "No especificado"}
                        </p>
                      </div>
                      {selectedProduct.image_url && (
                        <div className="flex flex-col gap-2">
                          <span className="text-sm font-medium text-default-500">
                            Imagen
                          </span>
                          <img
                            src={selectedProduct.image_url}
                            alt={`Imagen de ${selectedProduct.name}`}
                            className="w-full max-w-xs h-44 object-cover rounded-lg border border-divider"
                            loading="lazy"
                          />
                        </div>
                      )}
                      <div className="flex flex-col gap-1">
                        <span className="text-sm font-medium text-default-500">
                          Price de venta
                        </span>
                        <p className="text-base font-medium text-success-600">
                          {(() => {
                            const { salePrice, saleCurrency } =
                              getDisplayPrices(selectedProduct);
                            return salePrice && salePrice > 0
                              ? `$${formatPrice(salePrice)} ${saleCurrency}`
                              : "Price no disponible";
                          })()}
                        </p>
                      </div>
                      <div className="flex flex-col gap-1">
                        <span className="text-sm font-medium text-default-500">
                          Price de compra
                        </span>
                        <p className="text-base font-medium text-warning-700">
                          {(() => {
                            const { purchasePrice, purchaseCurrency } =
                              getDisplayPrices(selectedProduct);
                            return purchasePrice && purchasePrice > 0
                              ? `$${formatPrice(purchasePrice)} ${purchaseCurrency}`
                              : "Price no disponible";
                          })()}
                        </p>
                      </div>
                    </div>
                  </div>

                  {(() => {
                    if (!selectedProduct.dimensions) return null;

                    const visibleDimensions = Object.entries(
                      selectedProduct.dimensions,
                    ).filter(([, value]) => !isNullDimensionValue(value));

                    if (visibleDimensions.length === 0) return null;

                    return (
                      <>
                        <Divider />
                        <div>
                          <h3 className="text-lg font-semibold mb-2">
                            Dimensiones
                          </h3>
                          <div className="grid grid-cols-2 gap-4">
                            {visibleDimensions.map(([key, value]) => (
                              <div key={key} className="flex flex-col gap-1">
                                <span className="text-sm font-medium text-default-500 capitalize">
                                  {key}
                                </span>
                                <p className="text-base">
                                  {formatDimensionValue(value)}
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>
                      </>
                    );
                  })()}

                  {selectedProduct.components &&
                    selectedProduct.components.length > 0 && (
                      <>
                        <Divider />
                        <div>
                          <h3 className="text-lg font-semibold mb-2">
                            Componentes ({selectedProduct.components.length})
                          </h3>
                          <div className="space-y-3">
                            {selectedProduct.components.map((component) => (
                              <div
                                key={`${component.product_id}-${component.order_index}`}
                                className="flex items-center gap-3 p-3 bg-default-50 rounded-lg border border-divider"
                              >
                                <Chip size="sm" color="primary" variant="flat">
                                  x{component.quantity}
                                </Chip>
                                <div className="flex-1">
                                  <p className="font-medium">
                                    {component.product_name}
                                  </p>
                                  <p className="text-sm text-default-500">
                                    {component.product_type === "simple"
                                      ? " Simple"
                                      : " Compuesto"}
                                  </p>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </>
                    )}
                </div>
              )}
            </ModalBody>
            <ModalFooter className="flex flex-col-reverse gap-2 border-t border-divider sm:flex-row">
              <Button
                color="primary"
                variant="solid"
                type="button"
                onPress={() => {
                  if (!selectedProduct) return;
                  setShowDetailModal(false);
                  handleEditClick(selectedProduct);
                }}
                className="w-full font-semibold sm:w-auto"
              >
                Edit Product
              </Button>
              <Button
                color="default"
                variant="flat"
                type="button"
                onPress={onClose}
                className="w-full sm:w-auto"
              >
                Cerrar
              </Button>
            </ModalFooter>
          </>
        )}
      </CenteredModal>

      <CenteredModal
        isOpen={showDeleteConfirm}
        onOpenChange={(isOpen: boolean) => {
          setShowDeleteConfirm(isOpen);
        }}
        onClose={() => {
          setShowDeleteConfirm(false);
          setDeletingProduct(null);
        }}
        size="md"
        backdrop="blur"
      >
        {(onClose: () => void) => (
          <>
            <ModalHeader className="border-b border-divider">
              Confirmar Eliminacion
            </ModalHeader>
            <ModalBody className="py-6">
              <div className="space-y-4">
                <p>
                  Estas seguro de que quieres delete el product{" "}
                  <strong>"{deletingProduct?.name}"</strong>?
                </p>
                <p className="text-sm text-default-500">
                  Podras deshacer esta accion en los proximos 5 segundos. Ten en
                  cuenta que esto puede afectar otros products que referencian
                  este product.
                </p>
              </div>
            </ModalBody>
            <ModalFooter className="flex flex-col-reverse gap-2 border-t border-divider sm:flex-row">
              <Button
                color="default"
                variant="flat"
                type="button"
                onPress={() => {
                  handleDeleteCancel();
                  onClose();
                }}
                className="w-full sm:w-auto"
              >
                Cancel
              </Button>
              <Button
                color="danger"
                variant="solid"
                type="button"
                onPress={() => {
                  void handleDeleteConfirm();
                  onClose();
                }}
                className="w-full sm:w-auto"
              >
                Delete
              </Button>
            </ModalFooter>
          </>
        )}
      </CenteredModal>

      <CenteredModal
        isOpen={showEditModal}
        onOpenChange={(isOpen: boolean) => {
          setShowEditModal(isOpen);
        }}
        onClose={() => {
          setShowEditModal(false);
          setEditingProduct(null);
        }}
        size="lg"
        scrollBehavior="inside"
        backdrop="blur"
      >
        {(onClose: () => void) => (
          <>
            <ModalHeader className="border-b border-divider">
              Edit Product
            </ModalHeader>
            <ModalBody className="py-6">
              {editingProduct && (
                <EditProduct
                  product={editingProduct}
                  onSuccess={handleEditSuccess}
                  onCancel={() => {
                    handleEditCancel();
                    onClose();
                  }}
                />
              )}
            </ModalBody>
          </>
        )}
      </CenteredModal>
    </div>
  );
};

type EditProductProps = {
  product: Product;
  onSuccess: () => void;
  onCancel: () => void;
};

export const EditProduct: React.FC<EditProductProps> = ({
  product,
  onSuccess,
  onCancel,
}) => {
  const { user } = useAuth();
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");

  // Form states
  const [name, setName] = useState(product.name || "");
  const [description, setDescription] = useState(product.description || "");
  const [dimensions, setDimensions] = useState<ProductDimensionsState>(
    normalizeDimensions(product.dimensions),
  );
  const [components, setComponents] = useState<ProductComponent[]>(
    product.components || [],
  );

  // Sincronizar estado cuando cambia el product
  useEffect(() => {
    setName(product.name || "");
    setDescription(product.description || "");
    setDimensions(normalizeDimensions(product.dimensions));
    setComponents(product.components || []);
  }, [product]);

  // Generar nombre automaticamente basado en dimensiones
  useEffect(() => {
    const generateName = () => {
      const validDimensions = product.valid_dimensions || [];
      const dimensionValues = validDimensions
        .filter((dim) => dimensions[dim])
        .map((dim) => `${dimensions[dim]}`)
        .join("x");

      if (dimensionValues && dimensions.unit) {
        const generatedName = `${product.material_name} ${dimensionValues}${dimensions.unit}`;
        setName(generatedName);
      }
    };

    generateName();
  }, [dimensions, product.material_name, product.valid_dimensions]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    setIsSaving(true);
    setError("");

    try {
      const token = await user.getIdToken();

      const updateData: Record<string, unknown> = {
        description,
      };

      // El nombre se genera automaticamente en el backend, no lo enviamos
      // Add dimensions for simple products
      if (
        product.product_type === "simple" &&
        Object.keys(dimensions).length > 0
      ) {
        updateData.dimensions = dimensions;
      }

      // Add components for composite products
      if (product.product_type === "composite" && components.length > 0) {
        updateData.components = components;
      }

      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/products/${product.id}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(updateData),
        },
      );

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(errorData || "Error al actualizar el product");
      }

      onSuccess();
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Error al actualizar el product";
      setError(message);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDimensionChange = (key: string, value: string) => {
    setDimensions((prev) => {
      const updated = {
        ...prev,
        [key]: value,
      };
      return updated;
    });
  };

  const renderSimpleProductForm = () => {
    // Get valid dimensions from the product's valid_dimensions array
    const validDimensions = product.valid_dimensions || [];
    const isLiquid = product.measurement_strategy?.toUpperCase() === "LIQUID";

    const dimensionConfig: Record<
      string,
      { label: string; placeholder: string }
    > = {
      volume: { label: "Volumen", placeholder: "Ej: 500" },
      width: { label: "Ancho", placeholder: "Ej: 2.5" },
      height: { label: "Alto", placeholder: "Ej: 3.5" },
      depth: { label: "Profundidad", placeholder: "Ej: 1.0" },
      diameter: { label: "Diametro", placeholder: "Ej: 0.5" },
      length: { label: "Largo", placeholder: "Ej: 5.0" },
      mass: { label: "Masa (kg)", placeholder: "Ej: 10" },
      area: { label: "Area", placeholder: "Ej: 4.5" },
    };

    // Opciones de unidades
    const volumeUnits = [
      { label: "Mililitros (ml)", value: "ml" },
      { label: "Litros (L)", value: "L" },
      { label: "Galones (gal)", value: "gal" },
    ];

    const linearUnits = [
      { label: "Milimetros (mm)", value: "mm" },
      { label: "Centimetros (cm)", value: "cm" },
      { label: "Metros (m)", value: "m" },
      { label: "Pulgadas (in)", value: "in" },
      { label: "Pies (ft)", value: "ft" },
    ];

    const unitOptions = isLiquid ? volumeUnits : linearUnits;

    return (
      <div className="space-y-4">
        <h4 className="text-lg font-semibold">Dimensiones del Product</h4>
        <p className="text-sm text-default-500">
          Material: <span className="font-medium">{product.material_name}</span>
          <br />
          Estrategia:{" "}
          <span className="font-medium">{product.measurement_strategy}</span>
        </p>

        {validDimensions.length > 0 ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {validDimensions.map((dimKey: string) => (
              <Input
                key={dimKey}
                label={dimensionConfig[dimKey]?.label || dimKey}
                type="number"
                step="0.01"
                value={dimensions[dimKey] ? String(dimensions[dimKey]) : ""}
                onValueChange={(value: string) =>
                  handleDimensionChange(dimKey, value)
                }
                placeholder={dimensionConfig[dimKey]?.placeholder || `Ej: 1.0`}
              />
            ))}
            {/* Select para unidades */}
            <Select
              label={isLiquid ? "Unidad de Volumen" : "Unidad de Medida"}
              selectedKeys={
                dimensions.unit ? new Set([String(dimensions.unit)]) : new Set()
              }
              onSelectionChange={(keys: SelectionKeys) => {
                if (keys === "all") {
                  return;
                }

                const selected = Array.from(keys)[0];
                if (selected) {
                  handleDimensionChange("unit", String(selected));
                }
              }}
              placeholder="Selecciona una unidad"
            >
              {unitOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </Select>
          </div>
        ) : (
          <div className="p-4 bg-default-50 rounded-lg">
            <p className="text-sm text-default-500">
              No hay dimensiones configuradas para este material.
            </p>
          </div>
        )}
      </div>
    );
  };

  const renderCompositeProductForm = () => (
    <div className="space-y-4">
      <h4 className="text-lg font-semibold">
        Componentes del Product Compuesto
      </h4>
      <p className="text-sm text-default-500">
        Los componentes definen que products y en que cantidades conforman este
        product compuesto.
      </p>

      {/* Components would need a more complex interface - for now just show current components */}
      <div className="space-y-2">
        <h5 className="text-sm font-medium">Componentes actuales:</h5>
        {components.length > 0 ? (
          components.map((component) => (
            <div
              key={`${component.product_id}-${component.order_index}`}
              className="p-3 bg-default-50 rounded-lg"
            >
              <div className="flex items-center gap-3">
                <Chip size="sm" color="primary" variant="flat">
                  x{component.quantity}
                </Chip>
                <div className="flex-1">
                  <p className="font-medium">{component.product_name}</p>
                  <p className="text-sm text-default-500">
                    {component.product_type === "simple"
                      ? " Simple"
                      : " Compuesto"}
                  </p>
                </div>
              </div>
            </div>
          ))
        ) : (
          <p className="text-sm text-default-400">Sin componentes definidos</p>
        )}
      </div>

      <div className="p-4 bg-warning-50 border border-warning-200 rounded-lg">
        <p className="text-sm text-warning-700">
           La edicion de componentes requiere una interfaz mas compleja que
          permita seleccionar products y cantidades. Esta funcionalidad esta
          pending de implementar.
        </p>
      </div>
    </div>
  );

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="rounded-md bg-danger-50 p-3 text-sm text-danger">
          {error}
        </div>
      )}

      <Input
        label="Nombre"
        placeholder="Ej: Product Ejemplo"
        value={name}
        isDisabled
        description="Se genera automaticamente basado en el material y dimensiones"
      />

      <Textarea
        label="Description"
        placeholder="Description del product"
        value={description}
        onValueChange={setDescription}
        description="Informacion adicional sobre el product (opcional)"
      />

      <Divider className="my-4" />

      {product.product_type === "simple"
        ? renderSimpleProductForm()
        : renderCompositeProductForm()}

      <Divider className="my-4" />

      <div className="flex flex-col-reverse justify-end gap-2 sm:flex-row">
        <Button
          color="default"
          variant="flat"
          type="button"
          onPress={onCancel}
          className="w-full sm:w-auto"
        >
          Cancel
        </Button>
        <Button
          color="primary"
          variant="solid"
          type="submit"
          isLoading={isSaving}
          className="w-full font-semibold sm:w-auto"
          isDisabled={!description.trim()}
        >
          {isSaving ? "Guardando..." : "Actualizar Product"}
        </Button>
      </div>
    </form>
  );
};
