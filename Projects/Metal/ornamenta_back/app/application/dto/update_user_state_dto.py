from pydantic import BaseModel, ConfigDict, Field


class UpdateUserStateDTO(BaseModel):
    state: str = Field(..., description="Nuevo estado (A para active, I para inactive)")
