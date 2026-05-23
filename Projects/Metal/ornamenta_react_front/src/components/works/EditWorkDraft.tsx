import React, { useState, useEffect } from 'react';
import { Work } from '@/types/works';
import { workService } from '@/services/workService';
import { apiClient } from '@/services/apiClient';
import { clientService } from '@/services/clientService';
import { WorkTasksManager } from '@/components/works/WorkTasksManager';
import { WorkQuotationDisplay } from '@/components/works/WorkQuotationDisplay';
import {
  Card,
  CardBody,
  CardHeader,
  Button,
  Divider,
  Spinner,
} from '@heroui/react';
import { ArrowLeft, Save } from 'lucide-react';

interface EditWorkDraftProps {
  workId: string;
  onBack: () => void;
}

export const EditWorkDraft: React.FC<EditWorkDraftProps> = ({
  workId,
  onBack,
}) => {
  const [work, setWork] = useState<Work | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [productDetails, setProductDetails] = useState<Record<string, { components?: Array<{ product_id: string; product_name: string; quantity: number; price?: number }> }>>({});
  const [clientName, setClientName] = useState<string>('');
  const [workAddress, setWorkAddress] = useState<string>('');

  useEffect(() => {
    loadWork();
  }, [workId]);

  const getStateLabel = (state: string) => {
    const stateMap: Record<string, string> = {
      DRAFT: 'Borrador',
      QUOTED: 'Cotizada',
      IN_PROGRESS: 'En Progreso',
      DELIVERED: 'Entregada',
    };
    return stateMap[state] || state;
  };

  const getStateColor = (state: string) => {
    switch (state) {
      case 'DRAFT':
        return { bg: '#fef3c7', color: '#92400e' };
      case 'QUOTED':
        return { bg: '#d1fae5', color: '#065f46' };
      case 'IN_PROGRESS':
        return { bg: '#fef3c7', color: '#92400e' };
      case 'DELIVERED':
        return { bg: '#d1fae5', color: '#065f46' };
      default:
        return { bg: '#f0fdf4', color: '#166534' };
    }
  };

  const loadWork = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const loadedWork = await workService.getWorkById(workId);
      
      // Permitir edicion en DRAFT, QUOTED e IN_PROGRESS
      // Solo rechazar DELIVERED
      if (loadedWork.state === 'DELIVERED') {
        setError('No se pueden edit works entregados.');
        return;
      }
      
      setWork(loadedWork);

      // Cargar nombre del client y direccion
      try {
        const client = await clientService.getClientById(loadedWork.client_identification);
        const fullName = `${client.first_name} ${client.last_name}`.trim() || loadedWork.client_identification;
        setClientName(fullName);
        const address = client.address || loadedWork.description || 'No disponible';
        setWorkAddress(address);
      } catch {
        setClientName(loadedWork.client_identification);
        setWorkAddress('No disponible');
      }

      // Cargar detalles de products compuestos y sus componentes
      const compositeProducts = loadedWork.products.filter(p => p.product_type.toLowerCase() === 'composite');
      if (compositeProducts.length > 0) {
        const details: Record<string, { components?: Array<{ product_id: string; product_name: string; quantity: number; price?: number }> }> = {};
        await Promise.all(
          compositeProducts.map(async (product) => {
            try {
              const productData = await apiClient.get(`${import.meta.env.VITE_API_URL}/products/${product.product_id}`);
              
              // Cargar precios de cada componente
              if (productData.components && productData.components.length > 0) {
                const componentsWithPrices = await Promise.all(
                  productData.components.map(async (component: { product_id: string; product_name: string; quantity: number }) => {
                    try {
                      const componentData = await apiClient.get(`${import.meta.env.VITE_API_URL}/products/${component.product_id}`);
                      return {
                        ...component,
                        price: componentData.price
                      };
                    } catch (err) {
                      console.error(`Error loading component ${component.product_id}:`, err);
                      return component;
                    }
                  })
                );
                productData.components = componentsWithPrices;
              }
              
              details[product.product_id] = productData;
            } catch (err) {
              console.error(`Error loading product ${product.product_id}:`, err);
            }
          })
        );
        setProductDetails(details);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar el work');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTasksUpdated = (updatedWork: Work) => {
    setWork(updatedWork);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-96">
        <Spinner label="Cargando work..." />
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
          <p className="text-gray-500">No se encontro el work</p>
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
            Edit Work
          </h2>
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
          <h3 className="text-lg font-semibold">Informacion del Work</h3>
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
                  backgroundColor: getStateColor(work.state).bg,
                  color: getStateColor(work.state).color,
                }}>
                {getStateLabel(work.state)}
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

      {/* Gestion de Tasks */}
      <WorkTasksManager work={work} onTasksUpdated={handleTasksUpdated} />

      {/* Quotation del Work */}
      {work.products && work.products.length > 0 && (
        <WorkQuotationDisplay 
          work={work}
          productDetails={productDetails}
          userName="Gerente del Proyecto"
          clientName={clientName}
          workAddress={workAddress}
        />
      )}

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
        {work.state === 'DRAFT' && (
          <Button
            color="warning"
            startContent={<Save className="w-4 h-4" />}
            isLoading={isSaving}
            onClick={() => {
              setSuccess('Los cambios se han guardado automaticamente');
              setTimeout(() => setSuccess(null), 3000);
            }}
          >
            Save Cambios
          </Button>
        )}
      </div>

      {/* Mensajes */}
      {success && (
        <Card className="border-1 border-green-200 bg-green-50">
          <CardBody>
            <p className="text-green-600">{success}</p>
          </CardBody>
        </Card>
      )}
    </div>
  );
};

export default EditWorkDraft;
