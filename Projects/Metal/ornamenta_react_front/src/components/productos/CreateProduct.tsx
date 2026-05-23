import React, { useState } from "react";
import { SimpleProductForm } from "./SimpleProductForm";
import { CompositeProductForm } from "./CompositeProductForm";

type ProductType = "simple" | "composite";

type CreateProductProps = {
  onBack: () => void;
};

export const CreateProduct: React.FC<CreateProductProps> = ({ onBack }) => {
  const [productType] = useState<ProductType>("simple");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSuccess = (message: string) => {
    setSuccess(message);
    setError("");
    // Limpiar mensaje de exito despues de 5 segundos
    setTimeout(() => setSuccess(""), 5000);
  };

  const handleError = (message: string) => {
    setError(message);
    setSuccess("");
  };

  return (
    <div className="mx-auto max-w-4xl p-4">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-foreground">
          Create Simple Product
        </h2>
      </div>

      {error && (
        <div className="mb-4 rounded-md bg-danger-50 p-3 text-sm text-danger">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-4 rounded-md bg-success-50 p-3 text-sm text-success">
          {success}
        </div>
      )}

      {productType === "simple" ? (
        <SimpleProductForm onSuccess={handleSuccess} onError={handleError} />
      ) : (
        <CompositeProductForm onSuccess={handleSuccess} onError={handleError} />
      )}
    </div>
  );
};
