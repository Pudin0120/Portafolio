import React, { useState, useEffect } from "react";
import {
  Input,
  Button,
  Card,
  CardBody,
  Chip,
  Divider,
  Select,
  SelectItem,
  Spinner,
} from "@heroui/react";
import { Client } from "@/types/clients";
import { clientService } from "@services/clientService";
import { EditClientModal } from "./EditClientModal";
import { PrimaryButton, StatusMessage } from "./StyledButton";

interface ClientSearchProps {
  onClientSelected?: (client: Client) => void;
}

export const ClientSearch: React.FC<ClientSearchProps> = ({
  onClientSelected,
}) => {
  const [searchValue, setSearchValue] = useState("");
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [allClients, setAllClients] = useState<Client[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingClients, setIsLoadingClients] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [updateSuccess, setUpdateSuccess] = useState<string | null>(null);
  const [selectedClientId, setSelectedClientId] = useState<string>("");

  // Cargar lista de clients al montar el componente
  useEffect(() => {
    const loadClients = async () => {
      try {
        setIsLoadingClients(true);
        const response = await clientService.getClients();
        setAllClients(response.clients);
      } catch (err) {
        console.error("Error cargando clients:", err);
      } finally {
        setIsLoadingClients(false);
      }
    };

    loadClients();
  }, []);

  const handleSearch = async () => {
    if (!searchValue.trim()) {
      setError("Please ingrese un number de identificacion");
      return;
    }

    setIsLoading(true);
    setError(null);
    setNotFound(false);
    setSelectedClient(null);
    setSelectedClientId("");

    try {
      const client = await clientService.getClientById(searchValue.trim());
      setSelectedClient(client);
      onClientSelected?.(client);
      setNotFound(false);
    } catch (err) {
      setSelectedClient(null);
      const errorMessage =
        err instanceof Error ? err.message : "Error al search client";

      // Si es un error 404, el client no fue encontrado
      if (errorMessage.includes("404") || errorMessage.includes("not found")) {
        setNotFound(true);
        setError("Client no encontrado");
      } else {
        setError(errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectClient = (clientId: string) => {
    setSelectedClientId(clientId);
    const client = allClients.find((c) => c.identification_number === clientId);
    if (client) {
      setSelectedClient(client);
      onClientSelected?.(client);
      setError(null);
      setNotFound(false);
      setSearchValue("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  const handleClientUpdated = (updatedClient: Client) => {
    setSelectedClient(updatedClient);
    setUpdateSuccess("Client actualizado exitosamente");
    setTimeout(() => setUpdateSuccess(null), 3000);
  };

  return (
    <div className="space-y-4">
      {/* Desplegable de clients disponibles */}
      <div className="space-y-2">
        <p className="text-sm font-semibold">
          Selecciona un client de la lista
        </p>
        {isLoadingClients ? (
          <div className="flex justify-center py-4">
            <Spinner size="sm" />
          </div>
        ) : (
          <Select
            label="Clients Disponibles"
            placeholder="Search y seleccionar client..."
            value={selectedClientId}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
              handleSelectClient(e.target.value)
            }
            className="w-full"
          >
            {allClients.map((client) => (
              <SelectItem
                key={client.identification_number}
                value={client.identification_number}
                textValue={`${client.first_name} ${client.last_name} - ${client.identification_number}`}
              >
                {client.first_name} {client.last_name} -{" "}
                {client.identification_number}
              </SelectItem>
            ))}
          </Select>
        )}
      </div>

      <Divider />

      {/* Busqueda por number de identificacion */}
      <div className="space-y-2">
        <p className="text-sm font-semibold">
          O busca por number de identificacion
        </p>
        <div className="flex gap-2">
          <Input
            placeholder="Ingrese number de identificacion del client"
            variant="bordered"
            value={searchValue}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setSearchValue(e.target.value)
            }
            onKeyPress={handleKeyPress}
            isDisabled={isLoading}
            className="flex-1"
          />
          <PrimaryButton
            onPress={handleSearch}
            isLoading={isLoading}
            isDisabled={isLoading || !searchValue.trim()}
          >
            Search
          </PrimaryButton>
        </div>
      </div>

      {error && (
        <StatusMessage type={notFound ? "warning" : "error"}>
          {error}
        </StatusMessage>
      )}

      {updateSuccess && (
        <StatusMessage type="success">{updateSuccess}</StatusMessage>
      )}

      {selectedClient && (
        <Card className="border-primary/20 border-2 bg-primary/5 shadow-none">
          <CardBody className="gap-4">
            <div className="flex justify-between items-center">
              <div className="flex-1">
                <h3 className="text-lg font-bold text-primary">
                  {selectedClient.first_name} {selectedClient.last_name}
                </h3>
                <p className="text-sm text-default-500 font-medium">
                  {selectedClient.document_type} -{" "}
                  {selectedClient.identification_number}
                </p>
              </div>
              <div className="flex gap-2 items-center">
                <Chip color="primary" variant="flat" className="font-bold">
                  Seleccionado
                </Chip>
                <EditClientModal
                  client={selectedClient}
                  onClientUpdated={handleClientUpdated}
                />
              </div>
            </div>
          </CardBody>
        </Card>
      )}

      {updateSuccess && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
          {updateSuccess}
        </div>
      )}

      {selectedClient && (
        <Card className="border-primary border-2">
          <CardBody className="gap-4">
            <div className="flex justify-between items-center">
              <div className="flex-1">
                <h3 className="text-lg font-semibold">
                  {selectedClient.first_name} {selectedClient.last_name}
                </h3>
                <p className="text-sm text-gray-600">
                  {selectedClient.document_type} -{" "}
                  {selectedClient.identification_number}
                </p>
              </div>
              <div className="flex gap-2 items-center">
                <Chip color="success" variant="flat">
                  Seleccionado
                </Chip>
                <EditClientModal
                  client={selectedClient}
                  onClientUpdated={handleClientUpdated}
                />
              </div>
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  );
};

export default ClientSearch;
