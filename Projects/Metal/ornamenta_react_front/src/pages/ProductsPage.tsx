import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ProductsMenu } from '@components/products/ProductsMenu';
import { ProductsManager } from '@components/products/ProductsManager';
import { MaterialsManager } from '@components/products/MaterialsManager';

type ViewMode = 'menu' | 'products-manager' | 'manage-materials';

export const ProductsPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [viewMode, setViewMode] = useState<ViewMode>('menu');

  // Sincronizar la URL con el viewMode
  useEffect(() => {
    const pathname = location.pathname;

    if (pathname.includes('/products') && !pathname.includes('/materials')) {
      setViewMode('products-manager');
    } else if (pathname.includes('/materials') || pathname.includes('/products/materials')) {
      setViewMode('manage-materials');
    } else {
      setViewMode('menu');
    }
  }, [location.pathname]);

  const handleNavigate = (view: ViewMode) => {
    switch (view) {
      case 'products-manager':
        navigate('/products');
        break;
      case 'manage-materials':
        navigate('/materials');
        break;
      case 'menu':
      default:
        navigate('/products');
        break;
    }
  };

  const handleBackToMenu = () => {
    navigate('/products');
  };

  switch (viewMode) {
    case 'menu':
      return <ProductsMenu onNavigate={handleNavigate} />;

    case 'products-manager':
      return <ProductsManager onBack={handleBackToMenu} />;

    case 'manage-materials':
      return <MaterialsManager onBack={handleBackToMenu} context="products" />;

    default:
      return <ProductsMenu onNavigate={handleNavigate} />;
  }
};
