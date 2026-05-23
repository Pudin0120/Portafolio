import React, { useState } from "react";
import { useAuth } from "@hooks/useAuth";
import { Input, Textarea, Button, Divider } from "@heroui/react";
import { Composition } from "@/types/products";
import { apiClient } from "@services/apiClient";

type CreateCompositionProps = {
  onSuccess: () => void;
  onCancel: () => void;
};

type EditCompositionProps = {
  composition: Composition;
  onSuccess: () => void;
  onCancel: () => void;
};

export const CreateComposition: React.FC<CreateCompositionProps> = ({
  onSuccess,
  onCancel,
}) => {
  const { user } = useAuth();
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");

  // Form state
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    setIsSaving(true);
    setError("");

    try {
      const payload = {
        name,
        description: description || undefined,
      };

      await apiClient.post("/compositions/", payload);

      onSuccess();
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      console.error("ERROR Error al create composicion:", message);
      setError(message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="rounded-md bg-danger/20 p-3 text-sm text-danger border border-danger/30">
          {error}
        </div>
      )}

      <Input
        label="Nombre"
        placeholder="Ej: Acero galvanizado"
        value={name}
        onValueChange={setName}
        isRequired
        description="Nombre unico de la composicion"
      />

      <Textarea
        label="Description"
        placeholder="Ej: Acero con recubrimiento de zinc grado G90 para proteccion contra corrosion"
        value={description}
        onValueChange={setDescription}
        description="Informacion adicional sobre la composicion (opcional)"
      />

      <Divider className="my-4" />

      <div className="flex justify-end gap-2">
        <Button color="default" variant="bordered" onPress={onCancel}>
          Cancel
        </Button>
        <Button
          color="primary"
          variant="solid"
          type="submit"
          isLoading={isSaving}
          isDisabled={!name}
          className="font-semibold"
        >
          Create Composicion
        </Button>
      </div>
    </form>
  );
};

export const EditComposition: React.FC<EditCompositionProps> = ({
  composition,
  onSuccess,
  onCancel,
}) => {
  const { user } = useAuth();
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");

  // Form state initialized with composition data
  const [name, setName] = useState(composition.name || "");
  const [description, setDescription] = useState(composition.description || "");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    setIsSaving(true);
    setError("");

    try {
      const payload = {
        name,
        description: description || undefined,
      };

      await apiClient.put(`/compositions/${composition.id}`, payload);

      onSuccess();
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      console.error("ERROR Error al actualizar composicion:", message);
      setError(message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="rounded-md bg-danger/20 p-3 text-sm text-danger border border-danger/30">
          {error}
        </div>
      )}

      <Input
        label="Nombre"
        placeholder="Ej: Acero galvanizado"
        value={name}
        onValueChange={setName}
        isRequired
        description="Nombre unico de la composicion"
      />

      <Textarea
        label="Description"
        placeholder="Ej: Acero con recubrimiento de zinc grado G90 para proteccion contra corrosion"
        value={description}
        onValueChange={setDescription}
        description="Informacion adicional sobre la composicion (opcional)"
      />

      <Divider className="my-4" />

      <div className="flex justify-end gap-2">
        <Button color="default" variant="flat" onPress={onCancel}>
          Cancel
        </Button>
        <Button
          color="primary"
          type="submit"
          isLoading={isSaving}
          isDisabled={!name}
        >
          Actualizar Composicion
        </Button>
      </div>
    </form>
  );
};
