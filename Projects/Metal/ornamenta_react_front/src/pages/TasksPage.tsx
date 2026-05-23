import React from 'react';
import { useNavigate } from 'react-router-dom';
import { TasksManager } from '@/components/tasks/TasksManager';

export const TasksPage: React.FC = () => {
  const navigate = useNavigate();

  const handleBackToMenu = () => {
    navigate('/tasks');
  };

  return <TasksManager onBack={handleBackToMenu} />;
};

export default TasksPage;
