from decimal import Decimal
import logging
from uuid import UUID
from fastapi import HTTPException, status
from app.api.v1.repositories.product_repository import ProductRepository
from app.core.exceptions import (CannotDeleteProductError, EmptyListResponse, InvalidParametersError, ProductNotFoundError, DuplicateSkuError, CategoryNotFoundError)
from app.schemas.v1.product import (PaginatedProductResponse, ProductFilterParams, ProductListResponse, ProductResponse, ProductRequest, ProductUpdate)

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
                min_price=params.min_price,
                max_price=params.max_price,
                search=params.search
            )

            if not products:
                raise EmptyListResponse()
                # return PaginatedProductResponse(data=[], total=0)
            
            # Converter para response
            product_list = []
            for p in products:
                category_count = len(p.get("categories", [])) if p.get("categories") else 0
                product_list.append(ProductListResponse(
                    product_id=UUID(p["product_id"]),
                    name=p["name"],
                    sku=p["sku"],
                    description=p["description"],
                    quantity_per_unit=p["quantity_per_unit"],
                    unit_price=Decimal(str(p["unit_price"])),
                    discount=Decimal(str(p["discount"])),
                    category_count=category_count,
                    created_at=p["created_at"]
                ))

            pages = (total + params.limit - 1) // params.limit

            return PaginatedProductResponse(
                data=product_list,
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
    async def get_product_by_sku(sku: str) -> ProductResponse:
        """Busca produto por SKU"""
        try:
            product = await ProductRepository.get_by_sku(sku)
            if not product:
                raise ProductNotFoundError(sku)

            # Processar categorias
            categories = []
            if product.get("categories"):
                for cat_data in product["categories"]:
                    if isinstance(cat_data, dict) and "categories" in cat_data:
                        categories.append(cat_data["categories"])

            product_response = ProductResponse(
                product_id=UUID(product["product_id"]),
                name=product["name"],
                sku=product["sku"],
                description=product["description"],
                quantity_per_unit=product["quantity_per_unit"],
                unit_price=Decimal(str(product["unit_price"])),
                discount=Decimal(str(product["discount"])),
                categories=categories,
                created_at=product["created_at"],
                updated_at=product["updated_at"]
            )

            return product_response
        
        except ProductNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Erro ao buscar produto: {str(e)}")
            raise Exception(f"Erro ao buscar produto: {str(e)}")


    @staticmethod
    async def create_product(request: ProductRequest) -> ProductResponse:
        """Cria novo produto"""
        try:
            # Validar SKU duplicado
            if await ProductRepository.check_sku_exists(request.sku):
                raise DuplicateSkuError(request.sku)
            
            # Validar categorias
            if request.category_ids:
                if not await ProductRepository.validate_categories_exist(request.category_ids):
                    raise InvalidParametersError("Uma ou mais categorias não existem")
            
            # Preparar dados
            product_data = {
                "sku": request.sku,
                "name": request.name,
                "description": request.description,
                "quantity_per_unit": request.quantity_per_unit,
                "unit_price": float(request.unit_price),
                "discount": float(request.discount)
            }
            
            # Criar produto
            product = await ProductRepository.create(product_data, request.category_ids)
            
            # Processar categorias
            categories = []
            if product.get("categories"):
                for cat_data in product["categories"]:
                    if isinstance(cat_data, dict) and "categories" in cat_data:
                        categories.append(cat_data["categories"])
            
            return ProductResponse(
                product_id=UUID(product["product_id"]),
                name=product["name"],
                sku=product["sku"],
                description=product["description"],
                quantity_per_unit=product["quantity_per_unit"],
                unit_price=Decimal(str(product["unit_price"])),
                discount=Decimal(str(product["discount"])),
                categories=categories,
                created_at=product["created_at"],
                updated_at=product["updated_at"]
            )
            
        except (DuplicateSkuError, InvalidParametersError):
            raise
        except Exception as e:
            logger.error(f"Erro ao criar produto: {str(e)}")
            raise Exception(f"Erro ao criar produto: {str(e)}")

    @staticmethod
    async def update_product(sku: str, request: ProductUpdate) -> ProductResponse:
        """Atualiza produto"""
        try:
            # Buscar produto existente
            product = await ProductRepository.get_by_sku(sku)
            if not product:
                raise ProductNotFoundError(sku)
            
            product_id = UUID(product["product_id"])
            
            # Validar novo SKU se mudou
            if request.sku and request.sku != sku:
                if await ProductRepository.check_sku_exists(request.sku, exclude_id=product_id):
                    raise DuplicateSkuError(request.sku)
            
            # Validar categorias
            if request.category_ids is not None:
                if request.category_ids and not await ProductRepository.validate_categories_exist(request.category_ids):
                    raise InvalidParametersError("Uma ou mais categorias não existem")
            
            # Preparar dados de atualização (apenas campos não-None)
            update_data = {}
            if request.sku is not None:
                update_data["sku"] = request.sku
            if request.name is not None:
                update_data["name"] = request.name
            if request.description is not None:
                update_data["description"] = request.description
            if request.quantity_per_unit is not None:
                update_data["quantity_per_unit"] = request.quantity_per_unit
            if request.unit_price is not None:
                update_data["unit_price"] = float(request.unit_price)
            if request.discount is not None:
                update_data["discount"] = float(request.discount)
            
            if not update_data and request.category_ids is None:
                # Se nada para atualizar, retornar produto atual
                product = await ProductRepository.get_by_id(product_id)
            else:
                product = await ProductRepository.update(product_id, update_data, request.category_ids)
            
            # Processar categorias
            categories = []
            if product.get("categories"):
                for cat_data in product["categories"]:
                    if isinstance(cat_data, dict) and "categories" in cat_data:
                        categories.append(cat_data["categories"])
            
            return ProductResponse(
                product_id=UUID(product["product_id"]),
                name=product["name"],
                sku=product["sku"],
                description=product["description"],
                quantity_per_unit=product["quantity_per_unit"],
                unit_price=Decimal(str(product["unit_price"])),
                discount=Decimal(str(product["discount"])),
                categories=categories,
                created_at=product["created_at"],
                updated_at=product["updated_at"]
            )
            
        except (ProductNotFoundError, DuplicateSkuError, InvalidParametersError):
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar produto: {str(e)}")
            raise Exception(f"Erro ao atualizar produto: {str(e)}")

    @staticmethod
    async def delete_product(sku: str) -> dict:
        """Deleta produto"""
        try:
            # Buscar produto
            product = await ProductRepository.get_by_sku(sku)
            if not product:
                raise ProductNotFoundError(sku)
            
            product_id = UUID(product["product_id"])
            
            # Aqui pode adicionar lógica de negócio
            # Ex: verificar se o produto está em pedidos ativos
            # if await OrderRepository.has_active_orders(product_id):
            #     raise CannotDeleteProductError(sku, "Produto possui pedidos ativos")
            
            # Deletar
            await ProductRepository.delete(product_id)
            
            return {"message": f"Produto '{sku}' deletado com sucesso"}
            
        except (ProductNotFoundError, CannotDeleteProductError):
            raise
        except Exception as e:
            logger.error(f"Erro ao deletar produto: {str(e)}")
            raise Exception(f"Erro ao deletar produto: {str(e)}")
