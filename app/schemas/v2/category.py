from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class CategoryRequest(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    category_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CategoryWithProductCount(CategoryResponse):
    product_count: int = 0