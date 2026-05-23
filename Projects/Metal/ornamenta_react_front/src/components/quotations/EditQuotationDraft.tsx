import React, { useState, useEffect } from 'react';
import { Work } from '@/types/works';
import { workService } from '@/services/workService';
import { QuotationStep3 } from '@/components/quotations/QuotationStep3';
import { HelpTooltip, helpContent } from '@components/HelpTooltip';
import {
  Card,
  CardBody,
  CardHeader,
  Button,
  Divider,
  Spinner,
} from '@heroui/react';
import { ArrowLeft, Save } from 'lucide-react';

interface EditQuotationDraftProps {
  workId: string;
  onBack: () => void;
}

export const EditQuotationDraft: React.FC<EditQuotationDraftProps> = ({
  workId,
  onBack,
}) => {
  const [work, setWork] = useState<Work | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    loadQuotation();
  }, [workId]);

  const loadQuotation = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const loadedWork = await workService.getWorkById(workId);
      
      // Solo permitir edit borradores
      if (loadedWork.state !== 'DRAFT') {
        setError('Solo se pueden edit borradores. Este work ya ha sido cotizado.');
        return;
      }
      
      setWork(loadedWork);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar la quotation');
    } finally {
      setIsLoading(false);
    }
  };

  const handleProductsAdded = (updatedWork: Work) => {
    setWork(updatedWork);
  };

  const handleSaveAndQuote = async () => {
    if (!work) return;

    try {
      setIsSaving(true);
      setError(null);
      
      // Generar quotation
      const quotedWork = await workService.generateQuote(work.work_id);
      setWork(quotedWork);
      setSuccess('Quotation generada exitosamente!');
      setTimeout(() => {
        setSuccess(null);
        onBack();
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al generar quotation');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-96">
        <Spinner label="Cargando quotation..." />
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-1 border-red-200 bg-red-50 mx-auto max-w-6xl">
        <CardBody className="gap-4">
          <p className="text-red-600 font-semibold">{error}</p>
          <Button
            color="primary"
            startContent={<ArrowLeft className="w-4 h-4" />}
            onClick={onBack}
            className="w-fit"
          >
            Volver
          </Button>
        </CardBody>
      </Card>
    );
  }

  if (!work) {
    return (
      <Card className="border-1 border-gray-200 mx-auto max-w-6xl">
        <CardBody>
          <p className="text-gray-500">No se encontro la quotation</p>
          <Button
            color="primary"
            startContent={<ArrowLeft className="w-4 h-4" />}
            onClick={onBack}
            className="w-fit mt-4"
          >
            Volver
          </Button>
        </CardBody>
      </Card>
    );
  }

  return (
    <div className="mx-auto max-w-6xl p-4 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-semibold text-foreground">
            Edit Borrador de Quotation
          </h2>
          <HelpTooltip
            content={
              helpContent.products || {
                title: 'Edit Borrador',
                description: 'Modifica los products del borrador antes de cotizar',
                steps: [],
                tips: [],
              }
            }
          />
        </div>
        <Button
          isIconOnly
          variant="light"
          className="text-gray-600"
          onClick={onBack}
          title="Volver"
        >
          <ArrowLeft className="w-5 h-5" />
        </Button>
      </div>

      {/* Informacion del Work */}
      <Card className="border-1 border-gray-200">
        <CardHeader className="flex flex-col items-start px-4 py-4 bg-orange-50">
          <h3 className="text-lg font-semibold">Informacion de la Quotation</h3>
        </CardHeader>
        <Divider />
        <CardBody className="gap-4 p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-gray-500 uppercase font-semibold">Nombre</p>
              <p className="text-sm font-medium">{work.work_name}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase font-semibold">Client</p>
              <p className="text-sm font-medium">{work.client_identification}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase font-semibold">Estado</p>
              <span className="px-2 py-1 rounded-full text-xs font-medium inline-block"
                style={{
                  backgroundColor: '#fef3c7',
                  color: '#92400e',
                }}>
                Borrador
              </span>
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase font-semibold">Impuesto</p>
              <p className="text-sm font-medium">{(work.tax * 100).toFixed(1)}%</p>
            </div>
          </div>
          {work.description && (
            <div>
              <p className="text-xs text-gray-500 uppercase font-semibold mb-1">Description</p>
              <p className="text-sm text-gray-700">{work.description}</p>
            </div>
          )}
        </CardBody>
      </Card>

      {/* Gestion de Products */}
      <QuotationStep3 work={work} onProductsAdded={handleProductsAdded} />

      {/* Acciones */}
      <div className="flex justify-between gap-4">
        <Button
          color="default"
          variant="bordered"
          startContent={<ArrowLeft className="w-4 h-4" />}
          onClick={onBack}
        >
          Volver
        </Button>
        <Button
          color="primary"
          isLoading={isSaving}
          isDisabled={
            isSaving ||
            !work.products ||
            work.products.length === 0
          }
          startContent={<Save className="w-4 h-4" />}
          onClick={handleSaveAndQuote}
        >
          {isSaving ? 'Generando quotation...' : 'Generar Quotation'}
        </Button>
      </div>

      {/* Mensajes */}
      {success && (
        <Card className="border-1 border-green-200 bg-green-50">
          <CardBody>
            <p className="text-green-600 font-semibold">{success}</p>
          </CardBody>
        </Card>
      )}
    </div>
  );
};

export default EditQuotationDraft;
