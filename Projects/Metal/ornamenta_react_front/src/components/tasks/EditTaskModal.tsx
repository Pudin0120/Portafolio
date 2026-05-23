import React from 'react';
import {
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  Input,
  Select,
  SelectItem,
  Textarea,
  Divider,
  Spinner,
} from '@heroui/react';
import { Task, TaskState } from '@/types/tasks';
import { useAuth } from '@/hooks/useAuth';
import { CenteredModal } from '@components/common/CenteredModal';

interface EditTaskModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  task: Task | null;
  formData: Partial<Task>;
  onFormChange: (field: keyof Task, value: any) => void;
  onSave: () => Promise<void>;
  isSaving: boolean;
  stateOptions: Array<{ label: string; value: string }>;
}

export const EditTaskModal: React.FC<EditTaskModalProps> = ({
  isOpen,
  onOpenChange,
  task,
  formData,
  onFormChange,
  onSave,
  isSaving,
  stateOptions,
}) => {
  const { userRole } = useAuth();
  const isManager = userRole === 'MANAGER';

  if (!task) return null;

  return (
    <CenteredModal isOpen={isOpen} onOpenChange={onOpenChange} size="lg">
      {(onClose: () => void) => (
        <>
          <ModalHeader className="flex flex-col gap-1">
            <h2 className="text-xl font-semibold">Edit Task</h2>
          </ModalHeader>
          <Divider />
          <ModalBody className="space-y-4">
              {/* Nombre */}
              <Input
                label="Nombre de la task"
                placeholder="Ingresa el nombre"
                value={formData.task_name || ''}
                onValueChange={(value: string) => onFormChange('task_name', value)}
                isDisabled={isSaving}
              />

              {/* Description */}
              <Textarea
                label="Description"
                placeholder="Ingresa una description"
                value={formData.description || ''}
                onValueChange={(value: string) => onFormChange('description', value)}
                isDisabled={isSaving}
                minRows={3}
              />

              {/* Orden de ejecucion */}
              <Input
                type="number"
                label="Orden de ejecucion"
                placeholder="Ingresa el orden"
                value={String(formData.execution_order || '')}
                onValueChange={(value: string) => onFormChange('execution_order', parseInt(value) || 0)}
                isDisabled={isSaving}
              />

              {/* Estado - Solo consulta */}
              <Select
                label="Estado (Solo consulta)"
                selectedKeys={formData.state ? [formData.state] : []}
                isDisabled={true}
              >
                {stateOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </Select>

              {/* Mano de obra - Solo para Manager */}
              {isManager && (
                <Input
                  type="number"
                  label="Mano de obra"
                  placeholder="Ingresa el costo de mano de obra"
                  value={String(formData.labor || '')}
                  onValueChange={(value: string) => onFormChange('labor', parseFloat(value) || 0)}
                  isDisabled={isSaving}
                  step="0.01"
                  min="0"
                  startContent={<span className="text-gray-600">$</span>}
                />
              )}

              {/* Valor estimado - Solo para Manager */}
              {isManager && (
                <Input
                  type="number"
                  label="Valor estimado"
                  placeholder="Ingresa el valor estimado"
                  value={String(formData.estimated_value || '')}
                  onValueChange={(value: string) => onFormChange('estimated_value', parseFloat(value) || 0)}
                  isDisabled={isSaving}
                  step="0.01"
                  min="0"
                  startContent={<span className="text-gray-600">$</span>}
                />
              )}
            </ModalBody>
            <Divider />
            <ModalFooter>
              <Button
                color="default"
                variant="light"
                onPress={onClose}
                isDisabled={isSaving}
              >
                Cancel
              </Button>
              <Button
                color="warning"
                onPress={onSave}
                isDisabled={isSaving}
                className="bg-brand-orange-600 text-white"
              >
                {isSaving && <Spinner size="sm" color="current" className="mr-2" />}
                {isSaving ? 'Guardando...' : 'Save'}
              </Button>
            </ModalFooter>
          </>
        )}
      </CenteredModal>
  );
};
