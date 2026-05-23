import React, { useCallback, useEffect, useState } from 'react';
import {
  Card,
  CardBody,
  CardHeader,
  Button,
  Divider,
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
} from '@heroui/react';
import { ArrowUp, ArrowDown, ChevronDown, ChevronRight, Package, Trash2 } from 'lucide-react';
import { Work, WorkProduct } from '@/types/works';
import { workService } from '@/services/workService';
import { apiClient } from '@/services/apiClient';
import { useAuth } from '@/hooks/useAuth';

interface ProductGroup {
  parentProductId: string;
  isComposite: boolean;
  productName: string;
  products: WorkProduct[];
  productType: string;
  startOrder: number;
  endOrder: number;
}

interface WorkProductsManagerProps {
  work: Work;
  onProductsUpdated?: (updatedWork: Work) => void;
}

export const WorkProductsManager: React.FC<WorkProductsManagerProps> = ({
  work,
  onProductsUpdated,
}) => {
  const { userRole } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());
  const [productGroups, setProductGroups] = useState<ProductGroup[]>([]);

  const isManagerOrSupervisor = userRole === 'MANAGER' || userRole === 'SUPERVISOR';
  const canEdit = (work.state === 'DRAFT' || work.state === 'QUOTED') && isManagerOrSupervisor;

  const loadProductGroups = useCallback(async () => {
    try {
      // Identificar products compuestos
      const compositeProducts = new Map<string, WorkProduct>();
      const compositeChildrenMap = new Map<string, string[]>(); // composite_id -> child_product_ids

      // Cargar detalles de products compuestos
      for (const product of work.products) {
        if (product.product_type.toLowerCase() === 'composite' || product.snapshot?.composition) {
          compositeProducts.set(product.product_id, product);

          // Obtener componentes del composite
          try {
            const productData = await apiClient.get(`${import.meta.env.VITE_API_URL}/products/${product.product_id}`);
            if (productData.components && Array.isArray(productData.components)) {
              const childIds = (productData.components as Array<{ product_id: string }>).map(
                (component) => component.product_id,
              );
              compositeChildrenMap.set(product.product_id, childIds);
            }
          } catch (err) {
            console.error(`Error loading composite product ${product.product_id}:`, err);
          }
        }
      }

      // Create mapa de hijo -> padre
      const childToParentMap = new Map<string, string>();
      compositeChildrenMap.forEach((children, parentId) => {
        children.forEach(childId => {
          childToParentMap.set(childId, parentId);
        });
      });

      // Agrupar products
      const groups: ProductGroup[] = [];
      const processedProducts = new Set<string>();

      // Ordenar products por execution_order
      const sortedProducts = [...work.products].sort((a, b) => a.execution_order - b.execution_order);

      for (const product of sortedProducts) {
        if (processedProducts.has(product.product_id)) continue;

        // Si es un product compuesto
        if (compositeProducts.has(product.product_id)) {
          const children = compositeChildrenMap.get(product.product_id) || [];
          const childProducts = sortedProducts.filter(p => children.includes(p.product_id));

          processedProducts.add(product.product_id);
          childProducts.forEach(c => processedProducts.add(c.product_id));

          const allProducts = [product, ...childProducts];
          const orders = allProducts.map(p => p.execution_order);
          
          groups.push({
            parentProductId: product.product_id,
            isComposite: true,
            productName: product.product_name,
            products: allProducts,
            productType: product.product_type,
            startOrder: Math.min(...orders),
            endOrder: Math.max(...orders),
          });
        }
        // Si es un hijo de un compuesto, ya fue procesado
        else if (childToParentMap.has(product.product_id)) {
          continue;
        }
        // Product simple independiente
        else {
          processedProducts.add(product.product_id);
          groups.push({
            parentProductId: product.product_id,
            isComposite: false,
            productName: product.product_name,
            products: [product],
            productType: product.product_type,
            startOrder: product.execution_order,
            endOrder: product.execution_order,
          });
        }
      }

      setProductGroups(groups);

      // Expandir todos por defecto
      const allGroupIds = groups.map(g => g.parentProductId);
      setExpandedGroups(new Set(allGroupIds));
    } catch (err) {
      console.error('Error al cargar grupos de products:', err);
      setProductGroups([]);
    }
  }, [work.products]);

  useEffect(() => {
    loadProductGroups();
  }, [loadProductGroups]);

  const toggleGroupExpansion = (groupId: string) => {
    const newExpanded = new Set(expandedGroups);
    if (newExpanded.has(groupId)) {
      newExpanded.delete(groupId);
    } else {
      newExpanded.add(groupId);
    }
    setExpandedGroups(newExpanded);
  };

  const handleMoveGroup = async (groupIndex: number, direction: 'up' | 'down') => {
    const newIndex = direction === 'up' ? groupIndex - 1 : groupIndex + 1;

    if (newIndex < 0 || newIndex >= productGroups.length) return;

    try {
      setIsLoading(true);
      setError(null);

      const group1 = productGroups[groupIndex];
      const group2 = productGroups[newIndex];

      // Obtener products ordenados de ambos grupos
      const group1Products = [...group1.products].sort((a, b) => a.execution_order - b.execution_order);
      const group2Products = [...group2.products].sort((a, b) => a.execution_order - b.execution_order);

      const minOrder1 = Math.min(...group1Products.map(p => p.execution_order));
      const minOrder2 = Math.min(...group2Products.map(p => p.execution_order));

      const offset = minOrder2 - minOrder1;

      // Reordenar todos los products del grupo 1
      const updates1 = group1Products.map(product => {
        const newOrder = product.execution_order + offset;
        return workService.reorderProduct(work.work_id, product.product_id, newOrder);
      });

      // Reordenar todos los products del grupo 2
      const updates2 = group2Products.map(product => {
        const newOrder = product.execution_order - offset;
        return workService.reorderProduct(work.work_id, product.product_id, newOrder);
      });

      await Promise.all([...updates1, ...updates2]);

      setSuccess('Orden de products actualizado exitosamente');

      // Recargar work
      const updatedWork = await workService.getWorkById(work.work_id);
      onProductsUpdated?.(updatedWork);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al reordenar product');
    } finally {
      setIsLoading(false);
      setTimeout(() => {
        setSuccess(null);
        setError(null);
      }, 3000);
    }
  };

  const handleMoveProductWithinGroup = async (groupIndex: number, productIndex: number, direction: 'up' | 'down') => {
    const group = productGroups[groupIndex];
    if (!group.isComposite) return;

    const sortedProducts = [...group.products].sort((a, b) => a.execution_order - b.execution_order);
    
    // Saltar el product compuesto padre (primero en la lista)
    const childProducts = sortedProducts.slice(1);
    const newProductIndex = direction === 'up' ? productIndex - 1 : productIndex + 1;

    if (newProductIndex < 0 || newProductIndex >= childProducts.length) return;

    try {
      setIsLoading(true);
      setError(null);

      const product1 = childProducts[productIndex];
      const product2 = childProducts[newProductIndex];

      // Intercambiar execution_order
      const newOrder1 = product2.execution_order;
      const newOrder2 = product1.execution_order;

      await Promise.all([
        workService.reorderProduct(work.work_id, product1.product_id, newOrder1),
        workService.reorderProduct(work.work_id, product2.product_id, newOrder2),
      ]);

      setSuccess('Orden de products actualizado exitosamente');

      // Recargar work
      const updatedWork = await workService.getWorkById(work.work_id);
      onProductsUpdated?.(updatedWork);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al reordenar product');
    } finally {
      setIsLoading(false);
      setTimeout(() => {
        setSuccess(null);
        setError(null);
      }, 3000);
    }
  };

  const handleRemoveProduct = async (productId: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      await workService.removeProductFromWork(work.work_id, productId);
      setSuccess('Product removido exitosamente');

      // Recargar work completo
      const updatedWork = await workService.getWorkById(work.work_id);
      onProductsUpdated?.(updatedWork);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al remover product');
    } finally {
      setIsLoading(false);
      setTimeout(() => {
        setSuccess(null);
        setError(null);
      }, 3000);
    }
  };

  // Ordenar products por execution_order
  const _sortedProducts = [...(work.products || [])].sort((a, b) => 
    (a.execution_order || 0) - (b.execution_order || 0)
  );

  const _getProductPrice = (
    product: WorkProduct & {
      snapshot?: { price_amount?: string | number; price_currency?: string };
      current_price?: { amount?: string | number; currency?: string };
    },
  ) => {
    let priceAmount = 0;
    let priceCurrency = 'COP';
    
    // En QUOTED: usar snapshot (precios congelados)
    // En DRAFT: usar current_price (precios dinamicos)
    if (work.state === 'QUOTED' && product.snapshot?.price_amount) {
      const price = product.snapshot.price_amount;
      priceAmount = typeof price === 'string' ? parseFloat(price) : Number(price);
      priceAmount = isNaN(priceAmount) ? 0 : priceAmount;
      priceCurrency = product.snapshot?.price_currency || 'COP';
    } else if (product.current_price?.amount) {
      const price = product.current_price.amount;
      priceAmount = typeof price === 'string' ? parseFloat(price) : Number(price);
      priceAmount = isNaN(priceAmount) ? 0 : priceAmount;
      priceCurrency = product.current_price?.currency || 'COP';
    }
    
    return { amount: priceAmount, currency: priceCurrency };
  };

  const formatCurrency = (amount: string | number) => {
    const num = typeof amount === 'string' ? parseFloat(amount) : amount;
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
    }).format(num);
  };

  const renderTableRows = () => {
    const rows: React.ReactElement[] = [];

    productGroups.forEach((group, groupIndex) => {
      const isExpanded = expandedGroups.has(group.parentProductId);
      const sortedProducts = [...group.products].sort((a, b) => a.execution_order - b.execution_order);
      
      const badgeColor = group.isComposite
        ? { bg: 'bg-orange-100', border: 'border-orange-300', text: 'text-orange-700' }
        : {
            bg: "bg-surface-3",
            border: "border-surface-border",
            text: "text-surface-foreground",
          };

      // Fila del grupo (product padre o simple)
      const parentProduct = sortedProducts[0];
      const childProducts = sortedProducts.slice(1);

      rows.push(
        <TableRow key={`group-${group.parentProductId}`} className={`${group.isComposite ? 'bg-orange-50' : 'bg-surface-1'}`}>
          <TableCell>
            <div className="flex items-center gap-3">
              {group.isComposite && childProducts.length > 0 && (
                <button
                  onClick={() => toggleGroupExpansion(group.parentProductId)}
                  className="flex-shrink-0 rounded p-1 hover:bg-table-row-hover"
                  title={isExpanded ? 'Contraer' : 'Expandir'}
                >
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4" />
                  ) : (
                    <ChevronRight className="w-4 h-4" />
                  )}
                </button>
              )}
              <div className="flex-shrink-0">
                <Package className={`w-4 h-4 ${group.isComposite ? 'text-orange-600' : 'text-secondary'}`} />
              </div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-foreground">{group.productName}</span>
                <span
                  className={`px-2 py-0.5 text-xs font-medium rounded-full border ${badgeColor.bg} ${badgeColor.border} ${badgeColor.text}`}
                >
                  {group.isComposite ? 'Compuesto' : 'Simple'}
                </span>
                {group.isComposite && childProducts.length > 0 && (
                  <span className="text-xs text-surface-muted">({childProducts.length} componentes)</span>
                )}
              </div>
            </div>
          </TableCell>
          <TableCell>
            <span className="text-sm">{parentProduct.quantity}</span>
          </TableCell>
          <TableCell>
            <span className="text-sm font-medium">
              {parentProduct.current_price 
                ? formatCurrency(parentProduct.current_price.amount)
                : '-'}
            </span>
          </TableCell>
          <TableCell>
            <span className="text-sm font-medium">
              {parentProduct.line_total_amount 
                ? formatCurrency(parentProduct.line_total_amount)
                : '-'}
            </span>
          </TableCell>
          <TableCell>
            <div className="flex items-center justify-center gap-2">
              {canEdit && (
                <>
                  <Button
                    size="sm"
                    isIconOnly
                    variant="light"
                    onPress={() => handleMoveGroup(groupIndex, 'up')}
                    isDisabled={groupIndex === 0 || isLoading}
                    title="Mover product arriba"
                  >
                    <ArrowUp className="w-4 h-4" />
                  </Button>
                  <Button
                    size="sm"
                    isIconOnly
                    variant="light"
                    onPress={() => handleMoveGroup(groupIndex, 'down')}
                    isDisabled={groupIndex === productGroups.length - 1 || isLoading}
                    title="Mover product abajo"
                  >
                    <ArrowDown className="w-4 h-4" />
                  </Button>
                  <Button
                    size="sm"
                    isIconOnly
                    variant="light"
                    color="danger"
                    onPress={() => handleRemoveProduct(parentProduct.product_id)}
                    title="Remover product"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </>
              )}
            </div>
          </TableCell>
        </TableRow>
      );

      // Filas de componentes (si esta expandido y es compuesto)
      if (isExpanded && group.isComposite && childProducts.length > 0) {
        childProducts.forEach((product, productIndex) => {
          rows.push(
            <TableRow key={`product-${product.product_id}`} className="bg-surface-2">
              <TableCell>
                <div className="flex items-center gap-3 pl-12">
                  <span className="text-sm">{product.product_name}</span>
                </div>
              </TableCell>
              <TableCell>
                <span className="text-sm">{product.quantity}</span>
              </TableCell>
              <TableCell>
                <span className="text-sm">
                  {product.current_price 
                    ? formatCurrency(product.current_price.amount)
                    : '-'}
                </span>
              </TableCell>
              <TableCell>
                <span className="text-sm">
                  {product.line_total_amount 
                    ? formatCurrency(product.line_total_amount)
                    : '-'}
                </span>
              </TableCell>
              <TableCell>
                <div className="flex items-center justify-center gap-2">
                  {canEdit && (
                    <>
                      <Button
                        size="sm"
                        isIconOnly
                        variant="light"
                        onPress={() => handleMoveProductWithinGroup(groupIndex, productIndex, 'up')}
                        isDisabled={productIndex === 0 || isLoading}
                        title="Mover componente arriba"
                      >
                        <ArrowUp className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        isIconOnly
                        variant="light"
                        onPress={() => handleMoveProductWithinGroup(groupIndex, productIndex, 'down')}
                        isDisabled={productIndex === childProducts.length - 1 || isLoading}
                        title="Mover componente abajo"
                      >
                        <ArrowDown className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        isIconOnly
                        variant="light"
                        color="danger"
                        onPress={() => handleRemoveProduct(product.product_id)}
                        title="Remover componente"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </>
                  )}
                </div>
              </TableCell>
            </TableRow>
          );
        });
      }
    });

    return rows;
  };

  return (
    <Card className="border border-surface-border">
      <CardHeader className="flex flex-col items-start px-4 py-4 bg-orange-50">
        <div className="flex items-center gap-2 w-full">
          <h2 className="text-xl font-semibold">Gestionar Products</h2>
          {work.state === 'QUOTED' && (
            <span className="text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded font-semibold" title="Precios congelados">
               Precios Congelados
            </span>
          )}
        </div>
        <p className="mt-1 text-sm text-surface-muted">
          {canEdit
            ? 'Reordena los products y cambia su orden de ejecucion'
            : 'Visualiza los products del work y su orden de ejecucion'}
        </p>
      </CardHeader>
      <Divider />
      <CardBody className="gap-4 p-6">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-green-600 text-sm">{success}</p>
          </div>
        )}

        {productGroups && productGroups.length > 0 ? (
          <>
            <div className="flex items-center justify-between">
              <p className="font-semibold text-lg">Products</p>
              <span className="text-sm text-gray-500">
                {productGroups.length} product{productGroups.length !== 1 ? 's' : ''}
              </span>
            </div>

            {/* Leyenda */}
            <div className="flex items-center gap-4 rounded-lg bg-surface-2 p-3 text-xs text-surface-muted">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-orange-100 border border-orange-300 rounded"></div>
                <span>Product Compuesto</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded border border-surface-border bg-surface-3"></div>
                <span>Product Simple</span>
              </div>
            </div>

            <div className="overflow-x-auto">
              <Table aria-label="Tabla jerarquica de products">
                <TableHeader>
                  <TableColumn>PRODUCTO</TableColumn>
                  <TableColumn>CANTIDAD</TableColumn>
                  <TableColumn>PRECIO UNITARIO</TableColumn>
                  <TableColumn>TOTAL</TableColumn>
                  <TableColumn className="text-center">ACCIONES</TableColumn>
                </TableHeader>
                <TableBody>
                  {renderTableRows()}
                </TableBody>
              </Table>
            </div>

            {/* Resumen */}
            <div className="mt-6 bg-gradient-to-r from-orange-50 to-orange-100 p-4 rounded-lg border border-orange-200">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-orange-700 font-medium mb-1">Total de Products</p>
                  <p className="text-2xl font-bold text-orange-900">{productGroups.length}</p>
                </div>
                <div>
                  <p className="text-xs text-orange-700 font-medium mb-1">Products Compuestos</p>
                  <p className="text-2xl font-bold text-orange-900">
                    {productGroups.filter(g => g.isComposite).length}
                  </p>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">No hay products en este work</p>
            <p className="text-sm text-gray-400">Agrega products para comenzar</p>
          </div>
        )}
      </CardBody>
    </Card>
  );
};

export default WorkProductsManager;
