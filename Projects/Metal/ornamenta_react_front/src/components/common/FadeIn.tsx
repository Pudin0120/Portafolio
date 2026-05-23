import React from 'react';

interface FadeInProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
}

/**
 * Componente de animacion fade-in elegante con CSS
 * Mejora la percepcion de velocidad del sistema (heuristica #1 de Nielsen)
 */
export const FadeIn: React.FC<FadeInProps> = ({ 
  children, 
  delay = 0,
  duration = 0.3 
}) => {
  const style: React.CSSProperties = {
    animation: `fadeIn ${duration}s ease-out ${delay}s both`
  };

  return <div style={style}>{children}</div>;
};

/**
 * Animacion para lista de items
 */
export const FadeInList: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const style: React.CSSProperties = {
    animation: 'fadeIn 0.2s ease-out'
  };

  return <div style={style}>{children}</div>;
};

