# Componentes Comunes Reutilizables

Esta carpeta contiene componentes que pueden ser reutilizados en toda la aplicaciAn.

## TableSearchBar

Componente de bAsqueda reutilizable para tablas que incluye:
- Campo de entrada con Acono de bAsqueda (Y")
- BotAn para limpiar la bAsqueda
- Etiqueta y descripciAn configurables
- IntegraciAn con HeroUI

### Uso

```tsx
import { TableSearchBar } from '@components/common/TableSearchBar';

function MiComponente() {
  const [searchQuery, setSearchQuery] = useState('');
  
  return (
    <TableSearchBar
      value={searchQuery}
      onValueChange={setSearchQuery}
      placeholder="Search por nombre, descripciAn..."
      label="Search"
      description="Buscando en X elementos"
    />
  );
}
```

### Props

| Prop | Tipo | Requerido | Default | DescripciAn |
|------|------|-----------|---------|-------------|
| `value` | `string` | a... | - | Valor actual de la bAsqueda |
| `onValueChange` | `(value: string) => void` | a... | - | Callback cuando cambia el valor |
| `placeholder` | `string` | a | `'Search...'` | Texto placeholder del input |
| `label` | `string` | a | `'BAsqueda'` | Etiqueta del campo |
| `description` | `string` | a | - | Texto descriptivo debajo del campo |
| `className` | `string` | a | `''` | Clases CSS adicionales |

### Ejemplo de ImplementaciAn Completa

```tsx
import { useMemo, useState } from 'react';
import { TableSearchBar } from '@components/common/TableSearchBar';

function ProductsList() {
  const [products, setProducts] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  // Filtrar products basados en la bAsqueda
  const filteredProducts = useMemo(() => {
    if (!searchQuery.trim()) return products;
    
    const query = searchQuery.toLowerCase();
    return products.filter((product) => {
      return (
        product.name?.toLowerCase().includes(query) ||
        product.description?.toLowerCase().includes(query) ||
        product.category?.toLowerCase().includes(query)
      );
    });
  }, [products, searchQuery]);

  return (
    <div>
      <TableSearchBar
        value={searchQuery}
        onValueChange={setSearchQuery}
        placeholder="Search products por nombre, descripciAn o categorAa..."
        label="Search products"
        description={`Buscando en ${products.length} product(s)`}
      />
      
      {/* Render filteredProducts en tu tabla */}
    </div>
  );
}
```

## Componentes Implementados

a... **TableSearchBar** - Barra de bAsqueda para tablas con filtrado en tiempo real

### Componentes Usados en:
- `ProductsList.tsx` - BAsqueda de products
- `MaterialsManager.tsx` - BAsqueda de materials
- `MaterialTypeManager.tsx` - BAsqueda de tipos de materials + Filtro por categorAa
- `CreateMaterial.tsx` - BAsqueda de tipos de materials al create un material

## Ejemplo Avanzado: Filtros Combinados

```tsx
import { useMemo, useState } from 'react';
import { TableSearchBar } from '@components/common/TableSearchBar';
import { Select, SelectItem, Button } from '@heroui/react';

function MaterialTypeManager() {
  const [materialTypes, setMaterialTypes] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Extraer categorAas Anicas
  const availableCategories = useMemo(() => {
    const categories = new Set(materialTypes.map(mt => mt.category));
    return Array.from(categories).sort();
  }, [materialTypes]);

  // Filtrado combinado: bAsqueda + categorAa
  const filteredItems = useMemo(() => {
    let filtered = materialTypes;
    
    // Filtrar por categorAa
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(mt => mt.category === selectedCategory);
    }
    
    // Filtrar por bAsqueda de texto
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter((item) => 
        item.name?.toLowerCase().includes(query) ||
        item.category?.toLowerCase().includes(query) ||
        item.description?.toLowerCase().includes(query)
      );
    }
    
    return filtered;
  }, [materialTypes, searchQuery, selectedCategory]);

  // Detectar si hay filtros activos
  const hasActiveFilters = searchQuery.trim() !== '' || selectedCategory !== 'all';

  const handleClearFilters = () => {
    setSearchQuery('');
    setSelectedCategory('all');
  };

  return (
    <div>
      <div className="flex gap-3">
        <TableSearchBar
          value={searchQuery}
          onValueChange={setSearchQuery}
          placeholder="Search..."
          className="flex-1"
        />
        
        <Select
          label="CategorAa"
          selectedKeys={new Set([selectedCategory])}
          onSelectionChange={(keys) => setSelectedCategory(Array.from(keys)[0])}
          className="w-60"
        >
          <SelectItem key="all">Todas</SelectItem>
          {availableCategories.map(cat => (
            <SelectItem key={cat}>{cat}</SelectItem>
          ))}
        </Select>
        
        {hasActiveFilters && (
          <Button onPress={handleClearFilters}>
            Limpiar filtros
          </Button>
        )}
      </div>
      
      {/* Render filteredItems */}
    </div>
  );
}
```

## Mejores PrActicas

1. **Filtrado del lado del client**: Usa `useMemo` para optimizar el filtrado
2. **BAsqueda en mAltiples campos**: Incluye todos los campos relevantes en la bAsqueda
3. **Feedback visual**: Muestra contador de resultados filtrados vs totales
4. **Case insensitive**: Siempre convierte a minAsculas para la comparaciAn
5. **Trim whitespace**: Limpia espacios en blanco antes de filtrar
6. **Filtros combinados**: Permite combinar bAsqueda de texto con filtros de categorAas
7. **BotAn de limpiar**: Agrega un botAn visible para resetear todos los filtros cuando estA(c)n activos


