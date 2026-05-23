import React, { useState } from "react";
import { Client } from "@/types/clients";
import { Work } from "@/types/works";
import { ClientSearch, CreateClientModal } from "@components/common";
import { QuotationStep1 } from "@/components/quotations/QuotationStep1";
import { QuotationStep2 } from "@/components/quotations/QuotationStep2";
import { QuotationStep3 } from "@/components/quotations/QuotationStep3";
import { HelpTooltip, helpContent } from "@components/HelpTooltip";
import { Card, CardBody, Divider, Chip } from "@heroui/react";

interface CreateQuotationProps {
  onBack?: () => void;
}

export const CreateQuotation: React.FC<CreateQuotationProps> = () => {
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [createdWork, setCreatedWork] = useState<Work | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleClientSelected = (client: Client) => {
    setSelectedClient(client);
  };

  const handleClientCreated = (client: Client) => {
    setSelectedClient(client);
    setRefreshTrigger((prev) => prev + 1); // Trigger refresh of ClientSearch
  };

  return (
    <div className="mx-auto max-w-6xl p-4">
      <div className="mb-6">
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-semibold text-foreground">
            Create Quotation
          </h2>
          <Chip size="sm" variant="flat" color="primary" className="font-bold">
            Borrador
          </Chip>
          <HelpTooltip
            content={
              helpContent.quotations || {
                title: "Create Quotation",
                description:
                  "Crea una nueva quotation para tus clients. El estado es Borrador hasta que la finalices.",
                steps: [],
                tips: [],
              }
            }
          />
        </div>
      </div>

      {/* Seleccion de Client */}
      <Card className="border-none shadow-sm mb-6 bg-content1">
        <div className="bg-primary/5 px-6 py-4 border-b border-divider rounded-t-lg">
          <h3 className="text-lg font-semibold text-primary">
            Paso 1: Selecciona un Client
          </h3>
        </div>
        <CardBody className="gap-4 p-6">
          <CreateClientModal onClientCreated={handleClientCreated} />

          <ClientSearch
            onClientSelected={handleClientSelected}
            key={refreshTrigger}
          />
        </CardBody>
      </Card>

      {/* Proximos pasos */}
      {selectedClient && (
        <>
          <QuotationStep1
            selectedClient={selectedClient}
            onWorkCreated={setCreatedWork}
          />

          {createdWork && (
            <>
              <QuotationStep2
                work={createdWork}
                onProductsAdded={setCreatedWork}
              />

              <QuotationStep3
                work={createdWork}
                onProductsAdded={setCreatedWork}
              />
            </>
          )}
        </>
      )}
    </div>
  );
};
