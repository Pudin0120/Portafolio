import React, { useEffect, useState, useMemo } from 'react';
import { Package, Circle } from 'lucide-react';
import { useAuth } from '@hooks/useAuth';
import { apiClient } from '@services/apiClient';
import { formatPrice } from '@/utils';
import {
  Select,
  SelectItem,
  Input,
  Spinner,
} from '@heroui/react';
import { Product } from '@/types/products';
import { TableSearchBar } from '@components/common/TableSearchBar';

type ProductsResponse = {
  products: Product[];
  total: number;
};

type ProductSelectorProps = {
  selectedProductId: string;
  onProductChange: (productId: string) => void;
  onProductSelect: (product: Product | null) => void;
  excludeProductIds?: string[];
  label?: string;
  placeholder?: string;
  isRequired?: boolean;
  refreshTrigger?: number; // Nuevo: para forzar recarga
};

export const ProductSelector: React.FC<ProductSelectorProps> = ({
  selectedProductId,
  onProductChange,
  onProductSelect,
  excludeProductIds = [],
  label = 'Product',
  placeholder = 'Selecciona un product',
  isRequired = false,
  refreshTrigger = 0,
}) => {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [searchQuery, setSearchQuery] = useState('');

  const selectedKeys = useMemo(() => {
    return selectedProductId ? new Set([selectedProductId]) : new Set<string>();
  }, [selectedProductId]);

  useEffect(() => {
    const fetchProducts = async () => {
      if (!user) return;
      setIsLoading(true);
      try {
        const data: ProductsResponse = await apiClient.get('/products/');
        setProducts(data.products || []);
      } catch (err) {
        console.error('Error al cargar products:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchProducts();
  }, [user, refreshTrigger]); // Agregado refreshTrigger como dependencia

  // Filtrar products segun busqueda y exclusiones
  const filteredProducts = useMemo(() => {
    let filtered = products.filter(p => !excludeProductIds.includes(p.id));
    
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(p => 
        p.name?.toLowerCase().includes(query) ||
        p.description?.toLowerCase().includes(query) ||
        p.product_type?.toLowerCase().includes(query)
      );
    }
    
    return filtered;
  }, [products, searchQuery, excludeProductIds]);

  const handleSelectionChange = (keys: any) => {
    const selected = Array.from(keys)[0] as string;
    onProductChange(selected);
    
    const product = products.find(p => p.id === selected);
    onProductSelect(product || null);
  };

  if (isLoading) {
    return (
      <div className="flex items-center gap-2">
        <Spinner size="sm" />
        <span className="text-sm text-default-500">Cargando products...</span>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <TableSearchBar
        value={searchQuery}
        onValueChange={setSearchQuery}
        placeholder="Search por nombre, description o tipo..."
        label="Search products"
      />
      
      <Select
        label={label}
        placeholder={filteredProducts.length === 0 ? "No hay products disponibles" : placeholder}
        selectedKeys={selectedKeys}
        onSelectionChange={handleSelectionChange}
        isRequired={isRequired}
        description={`${filteredProducts.length} product(s) disponible(s)`}
      >
        {filteredProducts.length > 0 ? (
          filteredProducts.map((prod) => (
            <SelectItem 
              key={prod.id} 
              value={prod.id} 
              textValue={`${prod.name} - ${prod.product_type}`}
            >
              <div className="flex flex-col gap-1">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold">{prod.name}</span>
                  {/* TODO: Mostrar price cuando el backend lo provea */}
                  {/* <span className="text-xs font-semibold text-success">
                    ${formatPrice(prod.price || 0)} COP
                  </span> */}
                </div>
                <div className="flex items-center gap-1 text-xs text-default-500">
                  <span className="flex items-center gap-1">
                    {prod.product_type === 'simple' ? <Circle className="w-3 h-3" /> : <Package className="w-3 h-3" />}
                    {prod.product_type === 'simple' ? ' Simple' : ' Compuesto'}
                  </span>
                  {prod.material_name && (
                    <>
                      <span></span>
                      <span className="flex items-center gap-1"><Package className="w-3 h-3" /> {prod.material_name}</span>
                    </>
                  )}
                </div>
                <span className="text-xs text-default-400">{prod.description}</span>
              </div>
            </SelectItem>
          ))
        ) : (
          <SelectItem key="empty" value="" textValue="No hay products">
            No hay products {searchQuery ? 'que coincidan con la busqueda' : 'disponibles'}
          </SelectItem>
        )}
      </Select>
    </div>
  );
};
