import React from 'react';
import { useNavigate } from 'react-router-dom';
import { QuotationsManager } from '@/components/quotations/QuotationsManager';

export const QuotationsPage: React.FC = () => {
  const navigate = useNavigate();

  const handleBackToMenu = () => {
    navigate('/quotations');
  };

  return <QuotationsManager onBack={handleBackToMenu} />;
};

export default QuotationsPage;
