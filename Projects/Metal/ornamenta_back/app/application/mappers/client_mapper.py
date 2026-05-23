"""
Mapper para Client (dominio  DTO).
"""
from typing import List

from app.domain.models.client import Client
from app.domain.value_objects.document_number import DocumentNumber, DocumentEnum
from app.domain.value_objects.email import Email
from app.application.dto.client_dto import ClientDTO, ClientCreateDTO, ClientListDTO


class ClientMapper:
    """Mapper para convertir entre Client de dominio y DTOs."""

    @staticmethod
    def to_dto(client: Client) -> ClientDTO:
        """
        Convierte un Client de dominio a ClientDTO.
        
        Args:
            client: Entidad de dominio Client
            
        Returns:
            ClientDTO para respuesta
        """
        return ClientDTO(
            identification_number=client.identification_number.value,
            document_type=client.identification_number.doc_type.value,
            first_name=client.first_name,
            last_name=client.last_name,
            email=client.email.value,
            phone=client.phone,
            address=client.address
        )

    @staticmethod
    def to_domain(dto: ClientCreateDTO) -> Client:
        """
        Convierte un ClientCreateDTO a Client de dominio.
        
        Args:
            dto: DTO de creation de client
            
        Returns:
            Entidad de dominio Client
        """
        # Map document type
        doc_type_map = {
            'CC': DocumentEnum.CC,
            'CE': DocumentEnum.CE,
            'NIT': DocumentEnum.NIT,
        }
        doc_type = doc_type_map.get(dto.document_type, DocumentEnum.CC)
        
        return Client(
            identification_number=DocumentNumber(value=dto.identification_number, doc_type=doc_type),
            first_name=dto.first_name,
            last_name=dto.last_name,
            email=Email(value=dto.email),
            phone=dto.phone,
            address=dto.address,
            tenant_id=None
        )

    @staticmethod
    def to_dto_list(clients: List[Client]) -> ClientListDTO:
        """
        Convierte una lista de Clients a ClientListDTO.
        
        Args:
            clients: Lista de entidades de dominio Client
            
        Returns:
            ClientListDTO con lista de clients y total
        """
        return ClientListDTO(
            clients=[ClientMapper.to_dto(client) for client in clients],
            total=len(clients)
        )
