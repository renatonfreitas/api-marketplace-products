from datetime import datetime
from decimal import Decimal
import os
from uuid import UUID

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, field_validator
from supabase import Client, create_client

load_dotenv()

app = FastAPI()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

class ProductCreate(BaseModel):
    name: str
    sku: str
    description: str | None = None
    category_id: UUID | None = None
    quantity_per_unit: str | None = None
    unit_price: Decimal
    discount: Decimal = Decimal("0")

class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: UUID | None = None
    quantity_per_unit: str | None = None
    unit_price: Decimal | None = None
    discount: Decimal | None = None

class ProductResponse(BaseModel):
    product_id: UUID
    name: str
    sku: str
    description: str | None
    category_id: UUID | None
    quantity_per_unit: str | None
    unit_price: Decimal
    discount: Decimal
    created_at: datetime


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/v1/products")
async def get_products():
    data = supabase.table("products").select("*").execute().data
    return data

@app.get("/v1/products/{sku}")
async def get_product_by_sku(sku: str):
    data = supabase.table("products").select("*").eq("sku", sku).execute().data
    return data

@app.post("/v1/products", response_model=ProductResponse, status_code=201)
async def create_product(data: ProductCreate):
    payload = data.model_dump()
    if payload.get("category_id"):
        payload["category_id"] = str(payload["category_id"])
    payload["unit_price"] = float(payload["unit_price"])
    payload["discount"] = float(payload["discount"])

    result = supabase.table("products").insert(payload).execute()
    return result.data[0]

@app.put("/v1/products/{sku}",response_model=ProductResponse)
async def update_product(sku: str, data: ProductCreate):

    payload = data.model_dump()
    if payload.get("category_id"):
        payload["category_id"] = str(payload["category_id"])
    payload["unit_price"] = float(payload["unit_price"])
    payload["discount"] = float(payload["discount"])

    result = supabase.table("products").update(payload).eq("sku", sku).execute()
    return result.data[0]

@app.delete("/v1/products/{sku}")
async def delete_product(sku: str):
    supabase.table("products").delete().eq("sku", sku).execute()