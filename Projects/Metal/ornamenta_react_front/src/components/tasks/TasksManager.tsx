import React, { useState } from 'react';
import { Tabs, Tab } from '@heroui/react';
import { TasksList } from './TasksList';
import { MyTasksList } from './MyTasksList';
import { HelpTooltip } from '@/components/HelpTooltip';
import { useAuth } from '@/hooks/useAuth';

type TasksManagerProps = {
  onBack?: () => void;
};

export const TasksManager: React.FC<TasksManagerProps> = ({ onBack }) => {
  const { userRole } = useAuth();
  const [selectedTab, setSelectedTab] = useState('my-tasks');

  const isManagerOrSupervisor = userRole === 'MANAGER' || userRole === 'SUPERVISOR';

  const tasksHelpContent = {
    title: 'Gestion de Tasks',
    description: 'Visualiza y gestiona tus tasks',
    steps: [
      {
        step: 'Mis Tasks',
        description: 'Ve todas las tasks que te han sido asignadas'
      },
      {
        step: 'Todas las Tasks',
        description: 'Gestiona todas las tasks del sistema (solo Gerente/Supervisor)'
      },
      {
        step: 'Filtrar por Estado',
        description: 'Usa el selector de estado para filtrar tasks'
      },
      {
        step: 'Filtrar por Work',
        description: 'Filtra las tasks segun el work asociado'
      },
      {
        step: 'Filtrar por Fechas',
        description: 'Usa el rango de fechas para ver tasks actualizadas en un periodo especifico'
      },
      {
        step: 'Search Tasks',
        description: 'Busca por nombre o description de la task'
      }
    ],
    tips: [
      'Puedes search tasks por nombre o description',
      'Usa el filtro de estado para ver tasks especificas',
      'Filtra por work para ver solo las tasks de un proyecto especifico',
      'El rango de fechas te permite ver tasks actualizadas en un periodo',
      'Las tasks se ordenan por fecha de actualizacion mas reciente',
      'El orden de ejecucion te indica la secuencia de las tasks',
      'Haz clic en el icono de ojo para ver los detalles de la task'
    ]
  };

  return (
    <div className="mx-auto max-w-6xl p-4">
      <div className="mb-4">
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-semibold text-foreground">Gestion de Tasks</h2>
          <HelpTooltip content={tasksHelpContent} />
        </div>
      </div>

      <Tabs
        selectedKey={selectedTab}
        onSelectionChange={(key: React.Key) => setSelectedTab(key as string)}
        aria-label="Task options"
        color="warning"
        variant="underlined"
        classNames={{
          tabList: "gap-6 w-full relative rounded-none p-0 border-b border-divider",
          cursor: "w-full bg-brand-orange-500",
          tab: "max-w-fit px-4 h-12",
          tabContent: "group-data-[selected=true]:text-brand-orange-600"
        }}
      >
        <Tab key="my-tasks" title="Mis Tasks">
          <MyTasksList />
        </Tab>
        
        {isManagerOrSupervisor && (
          <Tab key="all-tasks" title="Todas las Tasks">
            <TasksList />
          </Tab>
        )}
      </Tabs>
    </div>
  );
};
