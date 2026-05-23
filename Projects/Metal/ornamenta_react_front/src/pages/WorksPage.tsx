import React from 'react';
import { useNavigate } from 'react-router-dom';
import { WorksManager } from '@/components/works/WorksManager';

export const WorksPage: React.FC = () => {
  const navigate = useNavigate();

  const handleBackToMenu = () => {
    navigate('/works');
  };

  return <WorksManager onBack={handleBackToMenu} />;
};

export default WorksPage;
