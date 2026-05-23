import React, { useState, useMemo } from 'react';
import { Tabs, Tab } from '@heroui/react';
import { useAuth } from '@hooks/useAuth';
import { PayrollManagement } from '@components/payroll/PayrollManagement';
import { MyPayroll } from '@components/payroll/MyPayroll';
import { HelpTooltip, helpContent } from '@components/HelpTooltip';

export const PayrollPage: React.FC = () => {
  const { userRole } = useAuth();
  const [selectedTab, setSelectedTab] = useState('my-payroll');
  
  // Determinar si el user es gerente
  const isManager = userRole?.toLowerCase() === 'manager';

  // Configurar las pestanas disponibles segun el rol
  const availableTabs = useMemo(() => {
    const tabs = [];

    // Solo el gerente puede ver la gestion de payrolls
    if (isManager) {
      tabs.push({
        key: 'management',
        title: 'Gestion de Payrolls',
        component: <PayrollManagement />
      });
    } else {
      // Solo los empleados y supervisores pueden ver "My Payroll"
      tabs.push({ 
        key: 'my-payroll', 
        title: 'My Payroll', 
        component: <MyPayroll /> 
      });
    }

    return tabs;
  }, [isManager]);

  // Si el user es gerente, mostrar por defecto la gestion
  // Si no es gerente, mostrar "My Payroll"
  React.useEffect(() => {
    if (isManager) {
      setSelectedTab('management');
    } else {
      setSelectedTab('my-payroll');
    }
  }, [isManager]);

  return (
    <div className="mx-auto max-w-7xl p-4">
      <div className="mb-4">
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-semibold text-foreground">Payrolls</h2>
          <HelpTooltip content={helpContent.payroll} />
        </div>
      </div>

      <Tabs
        selectedKey={selectedTab}
        onSelectionChange={(key: React.Key) => setSelectedTab(key as string)}
        className="mb-4"
        classNames={{
          tabList: "border border-surface-border bg-surface-2",
          cursor: "bg-primary",
          tab: "data-[selected=true]:text-white",
          tabContent: "group-data-[selected=true]:text-white"
        }}
      >
        {availableTabs.map(tab => (
          <Tab key={tab.key} title={tab.title}>
            <div className="mt-4">
              {tab.component}
            </div>
          </Tab>
        ))}
      </Tabs>
    </div>
  );
};
