import React from "react";
import { Card, CardBody, CardHeader, Divider } from "@heroui/react";
import { Work } from "@/types/works";
import { Chip } from "@heroui/react";

interface QuotationStep2Props {
  work: Work;
  onProductsAdded?: (updatedWork: Work) => void;
}

export const QuotationStep2: React.FC<QuotationStep2Props> = ({ work }) => {
  const getStateLabel = (state: string) => {
    const stateMap: Record<string, string> = {
      DRAFT: "Borrador",
      QUOTED: "Cotizada",
      IN_PROGRESS: "En Progreso",
      DELIVERED: "Entregada",
    };
    return stateMap[state] || state;
  };

  return (
    <Card className="border-none shadow-sm bg-content1">
      <CardHeader className="flex flex-col items-start px-6 py-4 bg-secondary/5">
        <div className="flex justify-between w-full items-center">
          <h2 className="text-xl font-semibold text-secondary">
            Paso 3: Detalle del Work Creado
          </h2>
          <Chip color="success" variant="flat" size="sm" className="font-bold">
            {getStateLabel(work.state)}
          </Chip>
        </div>
        <p className="text-sm text-default-500 mt-1">
          Revisa la information basica antes de agregar products
        </p>
      </CardHeader>
      <Divider className="bg-divider" />
      <CardBody className="gap-6 p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-1">
            <p className="text-xs text-default-400 uppercase tracking-wider font-bold">
              Nombre del Work
            </p>
            <p className="text-lg font-medium text-foreground">
              {work.work_name}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-default-400 uppercase tracking-wider font-bold">
              Identificador
            </p>
            <p className="text-sm font-mono text-default-500">
              #{work.work_id.slice(-8).toUpperCase()}
            </p>
          </div>
        </div>

        <Divider className="opacity-50" />

        <div className="space-y-1">
          <p className="text-xs text-default-400 uppercase tracking-wider font-bold">
            Description
          </p>
          <p className="text-base text-foreground leading-relaxed">
            {work.description || "Sin description detallada"}
          </p>
        </div>
      </CardBody>
    </Card>
  );
};

export default QuotationStep2;
