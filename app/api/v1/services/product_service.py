from decimal import Decimal
import logging
from uuid import UUID

from fastapi import HTTPException, status
logger = logging.getLogger(_name_)
from app.api.v1.repositories.product_repository import ProductRepository
from app.core.exceptions import (
    EmptyListResponse,
    ProductNotFoundError,
    DuplicateSkuError,
    CategoryNotFoundError
)

from app.schemas.v1.product import (
    PaginatedProductResponse,
    ProductFilterParams,
    ProductListResponse,
    ProductResponse,
    ProductRequest
)

from app.api.v1.repositories.product_repository import ProductRepository

from app.core.exceptions import (
    EmptyListResponse,
    ProductNotFoundError,
    DuplicateSkuError
)

from app.schemas.v1.product import (
    PaginatedProductResponse,
    ProductFilterParams,
    ProductListResponse,
    ProductResponse,
    ProductRequest
)
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

    # TODO
    # @staticmethod
    # async def create_product(request: ProductRequest) -> ProductResponse:
    #     """Cria novo produto"""
@staticmethod
async def create_product(request: ProductRequest) -> ProductResponse:
    """Cria novo produto"""

    try:

        # Verifica se SKU já existe
        sku_exists = await ProductRepository.check_sku_exists(request.sku)

        if sku_exists:
            raise DuplicateSkuError(request.sku)

        # Valida categorias
        if request.category_ids:

            categories_valid = await ProductRepository.validate_categories_exist(
                request.category_ids
            )

            if not categories_valid:
                raise CategoryNotFoundError(request.category_ids[0])

        # Dados produto
        product_data = {
            "name": request.name,
            "sku": request.sku,
            "description": request.description,
            "quantity_per_unit": request.quantity_per_unit,
            "unit_price": float(request.unit_price),
            "discount": float(request.discount)
        }

        # Cria produto
        created_product = await ProductRepository.create(
            product_data=product_data,
            category_ids=request.category_ids
        )

        return ProductResponse(
            product_id=UUID(created_product["product_id"]),
            name=created_product["name"],
            sku=created_product["sku"],
            description=created_product["description"],
            quantity_per_unit=created_product["quantity_per_unit"],
            unit_price=Decimal(str(created_product["unit_price"])),
            discount=Decimal(str(created_product["discount"])),
            categories=[],
            created_at=created_product["created_at"],
            updated_at=created_product["updated_at"]
        )

    except (
        DuplicateSkuError,
        CategoryNotFoundError
    ):
        raise

    except Exception as e:

        logger.error(f"Erro ao criar produto: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar produto"
        )
    # TODO
    # @staticmethod
    # async def update_product(sku: str, request: ProductRequest) -> ProductResponse:
    #     """Atualiza produto"""

    # TODO
    # @staticmethod
    # async def delete_product(sku: str) -> dict:
    #     """Deleta produto"""
