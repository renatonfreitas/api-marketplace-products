from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.v2.address import AddressResponse


class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: str | None = None
    phone: str | None = Field(default=None, max_length=20)

class SupplierRequest(SupplierBase):
    pass

class SupplierResponse(SupplierBase):
    supplier_id: UUID
    addresses: list[AddressResponse] = []
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SupplierWithProductCount(SupplierResponse):
    product_count: int = 0

class SupplierUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: str | None = None
    phone: str | None = Field(default=None, max_length=20)
    is_active: bool | None = None