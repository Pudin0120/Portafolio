import React from 'react';

type ProductsMenuProps = {
  onNavigate: (view: 'products-manager' | 'manage-materials') => void;
};

export const ProductsMenu: React.FC<ProductsMenuProps> = ({ onNavigate }) => {
  // Este componente ya no se usa, pero se mantiene por compatibilidad
  // La navegacion ahora va directamente desde el menu lateral
  return null;
};

