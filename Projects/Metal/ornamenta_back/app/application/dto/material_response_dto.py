from pydantic import BaseModel, ConfigDict, Field
from typing import Dict


class MaterialDetailDTO(BaseModel):
    price: float = Field(..., description="The price of the material.")
    unit: str = Field(..., description="The unit of measure for the price.")


class MaterialResponseDTO(BaseModel):
    materials: Dict[str, MaterialDetailDTO] = Field(
        ..., description="A dictionary of materials and their details.")
