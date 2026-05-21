from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class AddressBase(BaseModel):
    street: str = Field(..., min_length=1, max_length=255)
    number: str | None = Field(default=None, max_length=10)
    complement: str | None = None
    neighborhood: str | None = Field(default=None, max_length=100)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: str = Field(..., min_length=1, max_length=10)
    country: str | None = Field(default="Brasil", max_length=100)

class AddressRequest(AddressBase):
    supplier_id: UUID = Field(..., description="UUID do supplier")

class AddressResponse(AddressBase):
    address_id: UUID
    supplier_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)