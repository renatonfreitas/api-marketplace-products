from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.schemas.v1.category import CategoryResponse


class ProductBase(BaseModel):
    """Base com campos comuns"""
    name: str = Field(
        min_length=1, 
        max_length=255
    )
    sku: str = Field(
        min_length=1, 
        max_length=50, 
        pattern="^[A-Z0-9-]+$" # apenas maiúsculas, números e hífen
    )
    description: str | None = None
    quantity_per_unit: str
    unit_price: Decimal = Field(
        gt=0, 
        decimal_places=2, 
        max_digits=10
    )
    discount: Decimal = Field(
        default=Decimal("0"), 
        ge=0, 
        le=100, 
        decimal_places=2
    )

    @field_validator('unit_price', 'discount', mode='before')
    @classmethod
    def convert_to_decimal(cls, v):
        "Converte strings em Decimal"
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return Decimal(v)
            except:
                raise ValueError("Valor deve ser um número válido")
        return Decimal(str(v))
    
    @field_validator('sku')
    @classmethod
    def sku_format(cls, v):
        """Valida formato do SKU"""
        if not v or len(v) < 1:
            raise ValueError("SKU não pode estar vazio")
        if len(v) > 50:
            raise ValueError("SKU não pode ter mais de 50 caracteres")
        return v.upper().strip()

class ProductRequest(ProductBase):
    """POST/PUT - o que o cliente envia"""
    category_ids: list[UUID] | None = Field(default=None)

class ProductResponse(ProductBase):
    """GET - o que a API retorna"""
    product_id: UUID
    categories: list[CategoryResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProductUpdate(BaseModel):
    """PUT/PATCH - aceita campos opcionais"""
    name: str | None = Field(
        default=None,
        min_length=1, 
        max_length=255
    )
    sku: str | None = Field(
        default=None, 
        min_length=1, 
        max_length=50, 
        pattern="^[A-Z0-9-]+$"
    )
    description: str | None = None
    quantity_per_unit: str | None = None
    unit_price: Decimal | None = Field(
        default=None, 
        gt=0, 
        decimal_places=2, 
        max_digits=10
    )
    discount: Decimal | None = Field(
        default=None, 
        ge=0, 
        le=100, 
        decimal_places=2
    )
    category_ids: list[UUID] | None = None

class ProductFilterParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Página > 0")
    limit: int = Field(default=10, ge=1, le=100, description="1-100")
    sort: str = Field(
        default="name",
        pattern="^(name|unit_price|discount|created_at)$",
        description="Campo válido para ordenação",
    )
    order: str = Field(
        default="asc",
        pattern="^(asc|desc)$"
    )
    category: str | None = None
    min_price: Decimal | None = Field(default=None, ge=0)
    max_price: Decimal | None = Field(default=None, ge=0)
    search: str | None = Field(default=None, min_length=1, max_length=255)

    @field_validator('limit')
    @classmethod
    def limit_not_exceed_max(cls, v):
        if v > 100:
            raise ValueError("Limite máximo é 100 itens por página")
        return v
    
class ProductListResponse(ProductBase):
    """Resposta simplificada para listagens"""
    product_id: UUID
    category_count: int = 0
    created_at: datetime
    
    model_config = {"from_attributes": True}

class PaginatedProductResponse(BaseModel):
    """Resposta paginada genérica"""
    data: list[ProductListResponse]
    total: int
    page: int
    limit: int
    pages: int