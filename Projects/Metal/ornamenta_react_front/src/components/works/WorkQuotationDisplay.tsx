import React from 'react';
import { Work } from '@/types/works';
import { QuotationDisplay } from '@/components/common/QuotationDisplay';
import { Card } from '@heroui/react';

interface WorkQuotationDisplayProps {
  work: Work;
  clientName?: string;
  workAddress?: string;
  userName?: string;
  productDetails?: Record<string, { components?: Array<{ product_id: string; product_name: string; quantity: number; price?: number }> }>;
}

export const WorkQuotationDisplay: React.FC<WorkQuotationDisplayProps> = ({
  work,
  clientName = 'No disponible',
  workAddress = 'No disponible',
  userName = 'No disponible',
  productDetails = {},
}) => {
  return (
    <Card className="border-1 border-gray-200">
      <QuotationDisplay
        work={work}
        clientName={clientName}
        workAddress={workAddress}
        userName={userName}
        productDetails={productDetails}
        showBackButton={false}
        showHeader={false}
      />
    </Card >
  );
};

export default WorkQuotationDisplay;
