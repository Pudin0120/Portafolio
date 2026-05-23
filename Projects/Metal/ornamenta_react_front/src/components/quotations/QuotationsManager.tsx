import React, { useState, useMemo } from 'react';
import { Tabs, Tab } from '@heroui/react';
import { QuotationsList } from './QuotationsList';
import { CreateQuotation } from './CreateQuotation';
import { HelpTooltip, helpContent } from '@/components/HelpTooltip';

type QuotationsManagerProps = {
  onBack: () => void;
  onSubTabChange?: (tab: string) => void;
};

export const QuotationsManager: React.FC<QuotationsManagerProps> = ({ onBack, onSubTabChange }) => {
  const [selectedTab, setSelectedTab] = useState('quotations');

  // Notificar al padre cuando cambie la subpestana
  React.useEffect(() => {
    if (onSubTabChange) {
      onSubTabChange(selectedTab);
    }
  }, [selectedTab, onSubTabChange]);

  useMemo(() => {
    const tabLabels: Record<string, string> = {
      'quotations': 'Lista de Cotizaciones',
      'create': 'Create Quotation',
    };
    
    return [
      { label: 'Inicio', key: 'home', active: false },
      { label: 'Cotizaciones', key: 'quotations', active: false },
      { label: tabLabels[selectedTab] || 'Gestion', key: selectedTab, active: true }
    ];
  }, [selectedTab]);

  return (
    <div className="mx-auto max-w-6xl p-4">

      <div className="mb-4">
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-semibold text-foreground">Gestion de Cotizaciones</h2>
          <HelpTooltip content={helpContent.quotations || { title: 'Gestion de Cotizaciones', description: 'Gestiona y crea cotizaciones para tus clients', steps: [], tips: [] }} />
        </div>
      </div>

      <Tabs
        selectedKey={selectedTab}
        onSelectionChange={(key: React.Key) => setSelectedTab(key as string)}
        className="mb-4"
      >
        <Tab key="quotations" title="Cotizaciones">
          <QuotationsList />
        </Tab>

        <Tab key="create" title="Create Quotation">
          <div className="mt-4">
            <CreateQuotation onBack={onBack} />
          </div>
        </Tab>
      </Tabs>
    </div>
  );
};
