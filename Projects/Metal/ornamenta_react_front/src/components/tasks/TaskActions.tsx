import React from 'react';
import { Button } from '@heroui/react';
import { Eye } from 'lucide-react';
import { Task } from '@/types/tasks';

interface TaskActionsProps {
  task: Task;
  onView: (task: Task) => void;
}

export const TaskActions: React.FC<TaskActionsProps> = ({ task, onView }) => {
  return (
    <div className="flex justify-center items-center gap-2">
      <Button
        isIconOnly
        variant="light"
        size="sm"
        className="text-brand-orange-600 hover:bg-brand-orange-50"
        title="Ver task"
        onPress={() => onView(task)}
      >
        <Eye className="w-4 h-4" />
      </Button>
    </div>
  );
};
