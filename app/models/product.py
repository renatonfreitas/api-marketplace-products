from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel


class Address(SQLModel, table=True):
    __tablename__ = "addresses"

    address_id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    supplier_id: UUID = Field(foreign_key="suppliers.supplier_id")
    street: str = Field(min_length=1, max_length=255)
    number: str | None = Field(default=None, max_length=10)
    complement: str | None = None
    neighborhood: str | None = Field(default=None, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=2, max_length=2)
    zip_code: str = Field(min_length=1, max_length=10)
    country: str = Field(default="Brasil", max_length=100)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))

    suppliers: "Supplier" = Relationship(back_populates="addresses")

class Category(SQLModel, table=True):
    __tablename__ = "categories"

    category_id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, unique=True, min_length=1, max_length=100)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))

    products: list["Product"] = Relationship(
        back_populates="categories",
        link_model="ProductCategory"
    )

class Supplier(SQLModel, table=True):
    __tablename__ = "suppliers"

    supplier_id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, unique=True, min_length=1, max_length=255)
    email: str | None = Field(default=None, index=True)
    phone: str | None = None
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))

    addresses: list[Address] = Relationship(back_populates="suppliers")
    products: list["Product"] = Relationship(
        back_populates="suppliers",
        link_model="ProductSupplier"
    )

class Product(SQLModel, table=True):
    __tablename__ = "products"

    product_id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, min_length=1, max_length=255)
    sku: str = Field(index=True, unique=True, min_length=1, max_length=50)
    description: str | None = None
    quantity_per_unit: str | None = None # mesma coisa que unit_quantity
    unit_quantity: str | None = None # mesma coisa que quantity_per_unit
    unit_price: Decimal = Field(gt=0, decimal_places=2, max_digits=10)
    discount: Decimal = Field(default=Decimal("0"), ge=0, le=100, decimal_places=2, max_digits=5)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))

    categories: list[Category] = Relationship(
        back_populates="products",
        link_model="ProductCategory"
    )
    suppliers: list[Supplier] = Relationship(
        back_populates="products",
        link_model="ProductSupplier"
    )

class ProductCategory(SQLModel, table=True):
    __tablename__ = "products_categories"

    product_id: UUID = Field(foreign_key="products.product_id", primary_key=True)
    category_id: UUID = Field(foreign_key="categories.category_id", primary_key=True)

class ProductSupplier(SQLModel, table=True):
    __tablename__ = "products_suppliers"

    product_id: UUID = Field(foreign_key="products.product_id", primary_key=True)
    supplier_id: UUID = Field(foreign_key="suppliers.supplier_id", primary_key=True)