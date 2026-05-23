import React, { useState, useEffect, useCallback } from 'react';
import { Work } from '@/types/works';
import { workService } from '@/services/workService';
import { clientService } from '@/services/clientService';
import { apiClient } from '@/services/apiClient';
import { useAuth } from '@/hooks/useAuth';
import { QuotationDisplay } from '@/components/common/QuotationDisplay';
import {
  Card,
  CardBody,
  Spinner,
} from '@heroui/react';

interface ViewQuotationDetailsProps {
  workId: string;
  onBack: () => void;
}

export const ViewQuotationDetails: React.FC<ViewQuotationDetailsProps> = ({
  workId,
  onBack,
}) => {
  const { user } = useAuth();
  const [work, setWork] = useState<Work | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [clientName, setClientName] = useState<string>('');
  const [workAddress, setWorkAddress] = useState<string>('');
  const [userName, setUserName] = useState<string>('');
  const [productDetails, setProductDetails] = useState<Record<string, { components?: Array<{ product_id: string; product_name: string; quantity: number; price?: number }> }>>({});

  const loadQuotation = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const loadedWork = await workService.getWorkById(workId);
      setWork(loadedWork);
      
      // Cargar nombre del client y direccion
      try {
        const client = await clientService.getClientById(loadedWork.client_identification);
        const fullName = `${client.first_name} ${client.last_name}`.trim() || loadedWork.client_identification;
        setClientName(fullName);
        
        // Obtener la direccion del client o del work si esta disponible
        const address = client.address || loadedWork.description || 'No disponible';
        setWorkAddress(address);
      } catch {
        setClientName(loadedWork.client_identification);
        setWorkAddress('No disponible');
      }

      // Cargar nombre del user del sistema
      if (user) {
        try {
          const token = await user.getIdToken();
          const response = await fetch(`${import.meta.env.VITE_API_URL}/users/me`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });
          
          if (response.ok) {
            const userData = await response.json();
            const userFullName = `${userData.first_name || ''} ${userData.last_name || ''}`.trim() || 'No disponible';
            setUserName(userFullName);
          } else {
            setUserName('No disponible');
          }
        } catch (err) {
          console.error('Error cargando datos del user:', err);
          setUserName('No disponible');
        }
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
                      console.error(`ERROR Error loading component ${component.product_id}:`, err);
                      return component;
                    }
                  })
                );
                productData.components = componentsWithPrices;
              }
              
              details[product.product_id] = productData;
            } catch (err) {
              console.error(`ERROR Error loading product ${product.product_id}:`, err);
            }
          })
        );
        setProductDetails(details);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar la quotation');
    } finally {
      setIsLoading(false);
    }
  }, [workId, user]);

  useEffect(() => {
    loadQuotation();
  }, [workId, loadQuotation]);

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
        </CardBody>
      </Card>
    );
  }

  if (!work) {
    return (
      <Card className="border-1 border-gray-200 mx-auto max-w-6xl">
        <CardBody>
          <p className="text-gray-500">No se encontro la quotation</p>
        </CardBody>
      </Card>
    );
  }

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
        </CardBody>
      </Card>
    );
  }

  if (!work) {
    return (
      <Card className="border-1 border-gray-200 mx-auto max-w-6xl">
        <CardBody>
          <p className="text-gray-500">No se encontro la quotation</p>
        </CardBody>
      </Card>
    );
  }

  return (
    <QuotationDisplay
      work={work}
      onBack={onBack}
      clientName={clientName}
      workAddress={workAddress}
      userName={userName}
      productDetails={productDetails}
      showBackButton={true}
      showHeader={true}
    />
  );
};

