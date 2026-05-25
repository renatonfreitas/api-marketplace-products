from fastapi import HTTPException, status
from app.api.v2.repositories.product_repository import ProductRepository
from app.api.v2.repositories.supplier_repository import SupplierRepository
from app.core.exceptions import ProductNotFoundError
from app.core.exceptions import EmptyListResponse, ProductNotFoundError
from app.schemas.v2.product import PaginatedProductResponse, ProductFilterParams, ProductListResponse, ProductRequest, ProductResponse, ProductUpdate
from decimal import Decimal
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class ProductService:

    @staticmethod
    async def list_products(params: ProductFilterParams) -> PaginatedProductResponse:
        """Lista produtos com filtros e paginação"""
        try:
            products, total = await ProductRepository.get_all_products(
                page=params.page,
                limit=params.limit,
                sort=params.sort,
                order=params.order,
                category=params.category,
                supplier_id=params.supplier_id,
                min_price=params.min_price,
                max_price=params.max_price,
                search=params.search,
                only_active=params.only_active
            )

            data = []
            for prod in products:
                category_count = len(prod.get("categories", []))
                supplier_count = len(prod.get("suppliers", []))
                
                data.append(ProductListResponse(
                    product_id=UUID(prod["product_id"]),
                    name=prod["name"],
                    sku=prod["sku"],
                    unit_price=Decimal(str(prod["unit_price"])),
                    discount=Decimal(str(prod["discount"])),
                    is_active=prod.get("is_active", True),
                    created_at=prod["created_at"],
                    category_count=category_count,
                    supplier_count=supplier_count
                ))
            
            pages = (total + params.limit - 1) // params.limit if total > 0 else 1
                
            return PaginatedProductResponse(
                data=data,
                total=total,
                page=params.page,
                limit=params.limit,
                pages=pages
            )
        except EmptyListResponse:
            raise
        except Exception as e:
            logger.error(f"Erro ao listar produtos: {str(e)}")
            raise Exception(f"Erro ao listar produtos: {str(e)}")
        
    @staticmethod
    async def get_product(sku: str) -> ProductResponse:
        """Busca produto por SKU"""
        try:
            product = await ProductRepository.get_by_sku(sku)
            if not product:
                raise ProductNotFoundError(sku)
            
            categories = []
            if product.get("categories"):
                for cat_rel in product["categories"]:
                    if cat_rel.get("categories"):
                        categories.append({
                            "category_id": UUID(cat_rel["categories"]["category_id"]),
                            "name": cat_rel["categories"]["name"],
                            "is_active": cat_rel["categories"].get("is_active", True),
                            "created_at": cat_rel["categories"]["created_at"],
                            "updated_at": cat_rel["categories"]["updated_at"]
                        })
            
            suppliers = []
            if product.get("suppliers"):
                for sup_rel in product["suppliers"]:
                    if sup_rel.get("suppliers"):
                        suppliers.append({
                            "supplier_id": UUID(sup_rel["suppliers"]["supplier_id"]),
                            "name": sup_rel["suppliers"]["name"],
                            "email": sup_rel["suppliers"].get("email"),
                            "phone": sup_rel["suppliers"].get("phone"),
                            "is_active": sup_rel["suppliers"].get("is_active", True),
                            "created_at": sup_rel["suppliers"]["created_at"],
                            "updated_at": sup_rel["suppliers"]["updated_at"]
                        })
            
            return ProductResponse(
                product_id=UUID(product["product_id"]),
                sku=product["sku"],
                name=product["name"],
                unit_price=Decimal(str(product["unit_price"])),
                discount=Decimal(str(product["discount"])),
                description=product.get("description"),
                unit_quantity=product.get("unit_quantity"),
                categories=categories,
                suppliers=suppliers,
                is_active=product.get("is_active", True),
                created_at=product["created_at"],
                updated_at=product["updated_at"]
            )
        except ProductNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Erro ao buscar produto: {str(e)}")
            raise Exception(f"Erro ao buscar produto: {str(e)}")
        
    @staticmethod
    async def create_product(
        sku: str,
        name: str,
        unit_price: Decimal,
        discount: Decimal = Decimal("0"),
        description: str | None = None,
        unit_quantity: str | None = None,
        category_ids: list[UUID] | None = None,
        supplier_ids: list[UUID] | None = None
    ) -> ProductResponse:
        try:
            # Validar se SKU já existe
            if await ProductRepository.check_sku_exists(sku):
                raise ValueError(f"Produto com SKU '{sku}' já existe")
            
            # Validar categorias
            if category_ids:
                if not await ProductRepository.validate_categories_exist(category_ids):
                    raise ValueError("Uma ou mais categorias não existem")
            
            # Validar suppliers
            if supplier_ids:
                if not await ProductRepository.validate_suppliers_exist(supplier_ids):
                    raise ValueError("Um ou mais suppliers não existem")
            
            # Criar produto
            product_data = {
                "sku": sku.strip(),
                "name": name.strip(),
                "unit_price": float(unit_price),
                "discount": float(discount),
                "description": description,
                "unit_quantity": unit_quantity,
                "is_active": True
            }
            
            product = await ProductRepository.create(
                product_data,
                category_ids=category_ids,
                supplier_ids=supplier_ids
            )
            
            return await ProductService.get_product(sku)
        except Exception as e:
            logger.error(f"Erro ao criar produto: {str(e)}")
            raise

    @staticmethod
    async def update_product(
        sku: str,
        new_sku: str | None = None,
        name: str | None = None,
        unit_price: Decimal | None = None,
        discount: Decimal | None = None,
        description: str | None = None,
        unit_quantity: str | None = None,
        is_active: bool | None = None,
        category_ids: list[UUID] | None = None,
        supplier_ids: list[UUID] | None = None
    ) -> ProductResponse:
        try:
            # Buscar produto atual
            current_product = await ProductRepository.get_by_sku(sku)
            if not current_product:
                raise ValueError(f"Produto com SKU '{sku}' não encontrado")
            
            product_id = UUID(current_product["product_id"])
            
            # Validar novo SKU se for diferente
            if new_sku and new_sku != sku:
                if await ProductRepository.check_sku_exists(new_sku, exclude_id=product_id):
                    raise ValueError(f"Produto com SKU '{new_sku}' já existe")
            
            # Validar categorias
            if category_ids is not None:
                if category_ids and not await ProductRepository.validate_categories_exist(category_ids):
                    raise ValueError("Uma ou mais categorias não existem")
            
            # Validar suppliers
            if supplier_ids is not None:
                if supplier_ids and not await ProductRepository.validate_suppliers_exist(supplier_ids):
                    raise ValueError("Um ou mais suppliers não existem")
            
            # Preparar dados
            update_data = {}
            if new_sku:
                update_data["sku"] = new_sku.strip()
            if name:
                update_data["name"] = name.strip()
            if unit_price:
                update_data["unit_price"] = float(unit_price)
            if discount is not None:
                update_data["discount"] = float(discount)
            if description:
                update_data["description"] = description
            if unit_quantity:
                update_data["unit_quantity"] = unit_quantity
            if is_active is not None:
                update_data["is_active"] = is_active
            
            # Atualizar
            product = await ProductRepository.update(
                product_id,
                update_data,
                category_ids=category_ids,
                supplier_ids=supplier_ids
            )
            
            final_sku = new_sku if new_sku else sku
            return await ProductService.get_product(final_sku)
        except Exception as e:
            logger.error(f"Erro ao atualizar produto: {str(e)}")
            raise

    @staticmethod
    async def delete_product(sku: str) -> dict:
        try:
            product = await ProductRepository.get_by_sku(sku)
            if not product:
                raise ValueError(f"Produto com SKU '{sku}' não encontrado")
            
            product_id = UUID(product["product_id"])
            await ProductRepository.delete(product_id)
            
            return {"message": f"Produto '{sku}' deletado com sucesso"}
        except Exception as e:
            logger.error(f"Erro ao deletar produto: {str(e)}")
            raise
    
