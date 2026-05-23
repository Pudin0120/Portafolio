import React, { useState } from 'react';
import { Tabs, Tab } from '@heroui/react';
import { WorksList } from './WorksList';
import { EditWorkDraft } from './EditWorkDraft';
import { HelpTooltip } from '@/components/HelpTooltip';

type WorksManagerProps = {
  onBack?: () => void;
};

export const WorksManager: React.FC<WorksManagerProps> = ({ onBack }) => {
  const [selectedTab, setSelectedTab] = useState('in-progress');
  const [editingWorkId, setEditingWorkId] = useState<string | null>(null);

  const worksHelpContent = {
    title: 'Gestion de Works',
    description: 'Visualiza y gestiona tus works en progreso y entregados',
    steps: [
      {
        step: 'En Progreso',
        description: 'Visualiza todos los works que estan siendo realizados'
      },
      {
        step: 'Entregados',
        description: 'Visualiza todos los works que han sido completados y entregados'
      }
    ],
    tips: [
      'Puedes search works por nombre, description o client',
      'Usa las pestanas para filtrar por estado',
      'Haz clic en el icono de ojo para ver los detalles del work'
    ]
  };

  if (editingWorkId) {
    return (
      <EditWorkDraft
        workId={editingWorkId}
        onBack={() => setEditingWorkId(null)}
      />
    );
  }

  return (
    <div className="mx-auto max-w-6xl p-4">
      <div className="mb-4">
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-semibold text-foreground">Gestion de Works</h2>
          <HelpTooltip content={worksHelpContent} />
        </div>
      </div>

      <Tabs
        selectedKey={selectedTab}
        onSelectionChange={(key: React.Key) => setSelectedTab(key as string)}
        className="mb-4"
      >
        <Tab key="in-progress" title="En Progreso">
          <WorksList state="IN_PROGRESS" onEditWork={setEditingWorkId} />
        </Tab>

        <Tab key="delivered" title="Entregados">
          <WorksList state="DELIVERED" onEditWork={setEditingWorkId} />
        </Tab>
      </Tabs>
    </div>
  );
};
